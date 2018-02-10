#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
isbg scans an IMAP Inbox and runs every entry against SpamAssassin.

For any entries that match, the message is copied to another folder,
and the original marked or deleted.

This software was mainly written Roger Binns <rogerb@rogerbinns.com>
and maintained by Thomas Lecavelier <thomas@lecavelier.name> since
novembre 2009. You may use isbg under any OSI approved open source
license such as those listed at http://opensource.org/licenses/alphabetical

Usage:
    isbg.py [options]
    isbg.py (-h | --help)
    isbg.py --version

Options:
    --imaphost hostname    IMAP server name.
    --imapuser username    Who you login as.
    --dryrun               Do not actually make any changes.
    --delete               The spams will be marked for deletion from your
                           inbox.
    --deletehigherthan #   Delete any spam with a score higher than #.
    --exitcodes            Use exitcodes to detail  what happened.
    --expunge              Cause marked for deletion messages to also be
                           deleted (only useful if --delete is specified).
    --flag                 The spams will be flagged in your inbox.
    --gmail                Delete by copying to '[Gmail]/Trash' folder.
    --help                 Show the help screen.
    --ignorelockfile       Don't stop if lock file is present.
    --imaplist             List imap directories.
    --imappasswd passwd    IMAP account password.
    --imapport port        Use a custom port.
    --imapinbox mbox       Name of your inbox folder [Default: INBOX].
    --learnspambox mbox    Name of your learn spam folder.
    --learnhambox mbox     Name of your learn ham folder.
    --learnthendestroy     Mark learnt messages for deletion.
    --learnthenflag        Flag learnt messages.
    --learnunflagged       Only learn if unflagged (for --learnthenflag).
    --learnflagged         Only learn flagged.
    --lockfilegrace=<min>  Set the lifetime of the lock file [default: 240.0].
    --lockfilename file    Override the lock file name.
    --maxsize numbytes     Messages larger than this will be ignored as they
                           are unlikely to be spam.
    --movehamto mbox       Move ham to folder.
    --noninteractive       Prevent interactive requests.
    --noreport             Don't include the SpamAssassin report in the
                           message copied to your spam folder.
    --nostats              Don't print stats.
    --partialrun num       Stop operation after scanning 'num' unseen emails.
    --passwdfilename fn    Use a file to supply the password.
    --savepw               Store the password to be used in future runs.
    --spamc                Use spamc instead of standalone SpamAssassin binary.
    --spaminbox mbox       Name of your spam folder [Default: INBOX.spam].
    --nossl                Don't use SSL to connect to the IMAP server.
    --teachonly            Don't search spam, just learn from folders.
    --trackfile file       Override the trackfile name.
    --verbose              Show IMAP stuff happening.
    --verbose-mails        Show mail bodies (extra-verbose).
    --version              Show the version information.

    (Your inbox will remain untouched unless you specify --flag or --delete)

"""

import sys     # Because sys.stderr.write() is called bellow

# FIXME: This is necessary to allow using isbg both straight from the repo and
# installed / as an import.  We should probably decide to not care about
# running isbg as top-level script straight from the repo.
try:
    from .sa_unwrap import unwrap  # Imported the isbg module
except (ValueError, ImportError):
    try:
        from sa_unwrap import unwrap  # when excuted the script
    except ImportError:
        sys.stderr.write(
            'Cannot load sa_unwrap, please install isbg package properly!\n')

        # Create No-Op dummy function
        def unwrap(msg):
            """No-op dummy function."""
            return None

try:
    import imaputils            # as script: py2 and py3, as module: py3
    import utils
    from utils import __
except (ValueError, ImportError):
    from isbg import imaputils  # as module: py3
    from isbg import utils
    from isbg.utils import __

try:
    from docopt import docopt  # Creating command-line interface
except ImportError:
    sys.stderr.write("Missing dependency: docopt\n")
    raise

from subprocess import Popen, PIPE

import email      # To eassily encapsulated emails messages
import re
import os
import getpass
import time
import atexit
import json
import logging

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

# xdg base dir specification (only xdg_cache_home is used)
try:
    from xdg.BaseDirectory import xdg_cache_home
except ImportError:
    xdg_cache_home = ""    # pylint: disable=invalid-name
if xdg_cache_home == "":
    # pylint: disable=invalid-name
    xdg_cache_home = os.path.expanduser("~" + os.sep + ".cache")

__version__ = "2.0-dev"

# Exit codes to use in the command line
__exitcodes__ = {
    'ok': 0,          # all went well
    'newmsgs': 1,     # there were new messages - none of them spam
    'newspam': 2,     # they were all spam
    'newmsgspam': 3,  # there were new messages and new spam
    'flags': 10,      # there were errors in the command line arguments
    'imap': 11,       # there was an IMAP level error
    'spamc': 12,      # error of communication between spamc and spamd
    'tty': 20,        # error because of non interative terminal
    'locked': 30,     # there's certainly another isbg running
    'error': -1       # other errors
}


class ISBGError(Exception):
    """Class for the ISBG exceptions."""

    def __init__(self, exitcode=0, message=""):
        """Initialize the a ISBGError object."""
        self.exitcode = exitcode
        self.message = message
        Exception.__init__(self, message)
        assert exitcode in __exitcodes__.values()


def errorexit(msg, exitcode):
    """Raise an ISBGError.

    If its runed as a commandline also show a help message and exits.
    """
    if __name__ == '__main__':
        sys.stderr.write(msg)
        sys.stderr.write("\nUse --help to see valid options and arguments\n")
        if exitcode == -1:
            raise ISBGError(exitcode, msg)
        sys.exit(exitcode)
    else:
        raise ISBGError(exitcode, msg)


def score_from_mail(mail):
    r"""
    Search the spam score from a mail as a string.

    The returning format is 'd.d/d.d\n'.
    """
    res = re.search(r"score=(-?\d+(?:\.\d+)?) required=(\d+(?:\.\d+)?)", mail)
    score = res.group(1) + "/" + res.group(2) + "\n"
    return score


class ISBG(object):
    """Main ISBG class."""

    def __init__(self):
        """Initialize a ISBG object."""
        self.imapsets = imaputils.ImapSettings()
        self.imap = None

        # FIXME: This could be used when non runed interactivaly, may be with
        # the --noninteractive argument (instead of the addHandler:
        # logging.basicConfig(
        #    format=('%(asctime)s %(levelname)-8s [%(filename)s'
        #            + '%(lineno)d] %(message)s'),
        #    datefmt='%Y%m%d %H:%M:%S %Z')
        # see https://docs.python.org/2/howto/logging-cookbook.html
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.set_loglevel(logging.INFO)

        # We create the dir for store cached information (if needed)
        if not os.path.isdir(os.path.join(xdg_cache_home, "isbg")):
            os.makedirs(os.path.join(xdg_cache_home, "isbg"))

        # Reporting options:
        self.imaplist, self.nostats, self.noreport = (None, False, False)
        self.exitcodes, self.verbose, self.verbose_mails = (True, False, False)
        self.set_loglevel(logging.INFO)
        # Processing options:
        self.dryrun, self.maxsize, self.teachonly = (False, 120000, False)
        self.spamc, self.gmail = (False, False)
        # Lockfile options:
        self.ignorelockfile = False
        self.lockfilename = os.path.join(xdg_cache_home, "isbg", "lock")
        self.lockfilegrace = 240.0
        # Password options:
        self.passwdfilename, self.savepw = (None, False)
        # Trackfile oprions:
        self.pastuidsfile, self.partialrun = (None, False)
        # spamassassin options:
        self.movehamto, self.delete = (None, False)
        self.deletehigherthan, self.flag, self.expunge = (None, False, False)
        # Learning options:
        self.learnflagged, self.learnunflagged = (False, False)
        self.learnthendestroy, self.learnthenflag = (False, False)

        self.interactive = sys.stdin.isatty()
        self.alreadylearnt = "Message was already un/learned"
        # satest is the command that is used to test if the message is spam
        self.satest = ["spamassassin", "--exit-code"]
        # sasave is the one that dumps out a munged message including report
        self.sasave = ["spamassassin"]
        # what we use to set flags on the original spam in imapbox
        self.spamflagscmd = "+FLAGS.SILENT"
        # and the flags we set them to (none by default)
        self.spamflags = []

        # IMAP implementation detail
        # Courier IMAP ignores uid fetches where more than a certain number
        # are listed so we break them down into smaller groups of this size
        self.uidfetchbatchsize = 25
        # password saving stuff. A vague level of obfuscation
        self.passwdfilename = None
        self.passwordhash = None
        self.passwordhashlen = 256  # should be a multiple of 16

    def popen(self, cmd):
        """Call Popen, helper method."""
        if os.name == 'nt':
            return Popen(cmd, stdin=PIPE, stdout=PIPE)
        else:
            return Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)

    def set_loglevel(self, level):
        """Set the log level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def removelock(self):
        """Remove the lockfile."""
        if os.path.exists(self.lockfilename):
            os.remove(self.lockfilename)

    # Password stuff
    def getpw(self, data, shash):
        """Deobfuscate IMAP password."""
        res = ""
        for i in range(0, self.passwordhashlen):
            j = ord(data[i]) ^ ord(shash[i])
            if j == 0:
                break
            res = res + chr(j)
        return res

    def setpw(self, passwd, shash):
        """Obfuscate password."""
        if len(passwd) > self.passwordhashlen:
            raise ValueError(__(
                ("Password of length %d is too long to store " +
                 "(max accepted is %d)").format(len(passwd),
                                                self.passwordhashlen)))
        res = list(shash)
        for i in range(0, len(passwd)):
            res[i] = chr(ord(res[i]) ^ ord(passwd[i]))
        return ''.join(res)

    def assertok(self, res, *args):
        """Check that the return code is OK.

        It also prints out what happened (which would end
        up /dev/null'ed in non-verbose mode)
        """
        if 'fetch' in args[0] and not self.verbose_mails:
            res = utils.shorten(res, 140)
        self.logger.debug("{} = {}".format(args, res))
        if res[0] != "OK":
            self.logger.error(
                __("{} returned {} - aborting".format(args, res)))
            errorexit("\n%s returned %s - aborting\n"
                      % (repr(args), res),
                      __exitcodes__['imap'] if self.exitcodes else -1)

    def parse_args(self):
        """Argument processing."""
        try:
            opts = docopt(__doc__, version="isbg version " + __version__ +
                          ", from " + os.path.abspath(__file__))
            opts = dict([(k, v) for k, v in opts.items()
                         if v is not None])
        except Exception as exc:  # pylint: disable=broad-except
            errorexit("Option processing failed - " + str(exc),
                      __exitcodes__['flags'])

        # Check for required options:
        if not opts.get("--help") and not opts.get("--version"):
            if opts.get('--imaphost') is None:
                errorexit("Missed required option: --imaphost",
                          __exitcodes__['flags'])
            if opts.get('--imapuser') is None:
                errorexit("Missed required option: --imapuser",
                          __exitcodes__['flags'])

        if opts.get("--deletehigherthan") is not None:
            try:
                self.deletehigherthan = float(opts["--deletehigherthan"])
            except Exception:  # pylint: disable=broad-except
                errorexit("Unrecognized score - "
                          + opts["--deletehigherthan"],
                          __exitcodes__['flags'])
            if self.deletehigherthan < 1:
                errorexit("Score " + repr(self.deletehigherthan)
                          + " is too small", __exitcodes__['flags'])
        else:
            self.deletehigherthan = None

        if opts["--flag"] is True:
            self.spamflags.append("\\Flagged")

        self.imapsets.host = opts.get('--imaphost', self.imapsets.host)
        self.imapsets.passwd = opts.get('--imappasswd',
                                        self.imapsets.passwd)
        self.imapsets.port = opts.get('--imapport', self.imapsets.port)
        self.imapsets.user = opts.get('--imapuser', self.imapsets.user)
        self.imapsets.inbox = opts.get('--imapinbox', self.imapsets.inbox)
        self.imapsets.spaminbox = opts.get('--spaminbox',
                                           self.imapsets.spaminbox)
        self.imapsets.learnspambox = opts.get('--learnspambox')
        self.imapsets.learnhambox = opts.get('--learnhambox')
        self.imapsets.nossl = opts.get('--nossl', False)

        self.lockfilegrace = float(opts.get('--lockfilegrace',
                                            self.lockfilegrace))

        self.nostats = opts.get('--nostats', False)
        self.dryrun = opts.get('--dryrun', False)
        self.delete = opts.get('--delete', False)
        self.gmail = opts.get('--gmail', False)

        if opts.get("--maxsize") is not None:
            try:
                self.maxsize = int(opts["--maxsize"])
            except (TypeError, ValueError):
                errorexit("Unrecognised size - " + opts["--maxsize"],
                          __exitcodes__['flags'])
            if self.maxsize < 1:
                errorexit("Size " + repr(self.maxsize) + " is too small",
                          __exitcodes__['flags'])

        self.movehamto = opts.get('--movehamto')

        if opts["--noninteractive"] is True:
            self.interactive = 0

        self.noreport = opts.get('--noreport', self.noreport)

        self.lockfilename = opts.get('--lockfilename', self.lockfilename)

        self.pastuidsfile = opts.get('--trackfile', self.pastuidsfile)

        if opts.get("--partialrun") is not None:
            self.partialrun = int(opts["--partialrun"])
            if self.partialrun < 1:
                errorexit("Partial run number must be equal to 1 or higher",
                          __exitcodes__['flags'])

        self.verbose = opts.get('--verbose', False)
        if self.verbose:
            self.set_loglevel(logging.DEBUG)
        else:
            self.set_loglevel(logging.INFO)

        self.verbose_mails = opts.get('--verbose-mails', False)
        self.ignorelockfile = opts.get("--ignorelockfile", False)
        self.savepw = opts.get('--savepw', False)
        self.passwdfilename = opts.get('--passwdfilename',
                                       self.passwdfilename)

        self.imaplist = opts.get('--imaplist', False)

        self.learnunflagged = opts.get('--learnunflagged', False)
        self.learnflagged = opts.get('--learnflagged', False)
        self.learnthendestroy = opts.get('--learnthendestroy', False)
        self.learnthenflag = opts.get('--learnthendestroy', False)
        self.expunge = opts.get('--expunge', False)

        self.teachonly = opts.get('--teachonly', False)
        self.spamc = opts.get('--spamc', False)

        self.exitcodes = opts.get('--exitcodes', False)

        # fixup any arguments

        if opts.get("--imapport") is None:
            if opts["--nossl"] is True:
                self.imapsets.port = 143
            else:
                self.imapsets.port = 993

    def get_uidvalidity(self, mailbox):
        """Validate a mailbox."""
        uidvalidity = 0
        mbstatus = self.imap.status(mailbox, '(UIDVALIDITY)')
        if mbstatus[0] == 'OK':
            body = mbstatus[1][0].decode()
            uidval = re.search('UIDVALIDITY ([0-9]+)', body)
            if uidval is not None:
                uidvalidity = int(uidval.groups()[0])
        return uidvalidity

    def pastuid_read(self, uidvalidity, folder='inbox'):
        """Read the uids stored in a file for  a folder.

        pastuids_read keeps track of which uids we have already seen, so
        that we don't analyze them multiple times. We store its
        contents between sessions by saving into a file as Python
        code (makes loading it here real easy since we just source
        the file)
        """
        pastuids = []
        try:
            with open(self.pastuidsfile + folder, 'r') as rfile:
                struct = json.load(rfile)
                if struct['uidvalidity'] == uidvalidity:
                    pastuids = struct['uids']
        except Exception:  # pylint: disable=broad-except
            pass
        return pastuids

    def pastuid_write(self, uidvalidity, origpastuids, newpastuids,
                      folder='inbox'):
        """Write the uids in a file for the folder."""
        wfile = open(self.pastuidsfile + folder, "w+")
        try:
            os.chmod(self.pastuidsfile + folder, 0o600)
        except Exception:  # pylint: disable=broad-except
            pass
        self.logger.debug(__(('Writing pastuids, {} origpastuids, '
                              + 'newpastuids: {}'
                              ).format(len(origpastuids), newpastuids)))
        struct = {
            'uidvalidity': uidvalidity,
            'uids': list(set(newpastuids + origpastuids))
        }
        json.dump(struct, wfile)
        wfile.close()

    def spamassassin(self):
        """Run spamassassin in the imbox mails."""
        uids = []

        # check spaminbox exists by examining it
        res = self.imap.select(self.imapsets.spaminbox, 1)
        self.assertok(res, 'select', self.imapsets.spaminbox, 1)

        # select inbox
        res = self.imap.select(self.imapsets.inbox, 1)
        self.assertok(res, 'select', self.imapsets.inbox, 1)

        uidvalidity = self.get_uidvalidity(self.imapsets.inbox)

        # get the uids of all mails with a size less then the maxsize
        typ, inboxuids = self.imap.uid("SEARCH", None, "SMALLER",
                                       str(self.maxsize))
        inboxuids = sorted(inboxuids[0].split(), key=int, reverse=True)
        inboxuids = [x.decode() for x in inboxuids]

        # remember what pastuids looked like so that we can compare at the end
        # and remove the uids not found.
        origpastuids = self.pastuid_read(uidvalidity)
        origpastuids = [u for u in origpastuids if str(u) in inboxuids]

        newpastuids = []

        # filter away uids that was previously scanned
        uids = [u for u in inboxuids if int(u) not in origpastuids]

        # Take only X elements if partialrun is enabled
        if self.partialrun:
            uids = uids[:int(self.partialrun)]

        self.logger.debug(__('Got {} mails to check'.format(len(uids))))

        # Keep track of new spam uids
        spamlist = []

        # Keep track of spam that is to be deleted
        spamdeletelist = []

        if self.dryrun:
            processednum = 0
            fakespammax = 1
            processmax = 5

        # Main loop that iterates over each new uid we haven't seen before
        for uid in uids:
            # Retrieve the entire message
            mail = imaputils.get_message(self.imap, uid, newpastuids,
                                         logger=self.logger,
                                         assertok=self.assertok)
            # Unwrap spamassassin reports
            unwrapped = unwrap(mail)
            if unwrapped is not None and unwrapped:  # len(unwrapped) > 0
                mail = unwrapped[0]

            # Feed it to SpamAssassin in test mode
            if self.dryrun:
                if processednum > processmax:
                    break
                if processednum < fakespammax:
                    self.logger.info("Faking spam mail")
                    score = "10/10"
                    code = 1
                else:
                    self.logger.info("Faking ham mail")
                    score = "0/10"
                    code = 0
                processednum = processednum + 1
            else:
                proc = self.popen(self.satest)
                try:
                    score = proc.communicate(imaputils.mail_content(mail)
                                             )[0].decode(errors='ignore')
                    if not self.spamc:
                        score = score_from_mail(score)
                    code = proc.returncode
                except Exception:  # pylint: disable=broad-except
                    self.logger.exception(__(
                        'Error communicating with {}!'.format(self.satest)))
                    uids.remove(uid)
                    continue
                proc.stdin.close()
            if score == "0/0\n":
                errorexit("spamc -> spamd error - aborting",
                          __exitcodes__['spamc'])

            self.logger.debug(__(
                "Score for uid {}: {}".format(uid, score.strip())))

            if code == 0:
                # Message is below threshold
                pass
            else:
                # Message is spam, delete it or move it to spaminbox
                # (optionally with report)
                self.logger.debug(__("{} is spam".format(uid)))

                if (self.deletehigherthan is not None and
                        float(score.split('/')[0]) > self.deletehigherthan):
                    spamdeletelist.append(uid)
                    continue

                # do we want to include the spam report
                if self.noreport is False:
                    if self.dryrun:
                        self.logger.info("Skipping report because of --dryrun")
                    else:
                        proc = self.popen(self.sasave)
                        try:
                            mail = email.message_from_string(proc.communicate(
                                imaputils.mail_content(mail))[0])
                        except Exception:  # pylint: disable=broad-except
                            self.logger.exception(__(
                                'Error communicating with {}!'.format(
                                    self.sasave)))
                            continue
                        proc.stdin.close()
                        res = self.imap.append(self.imapsets.spaminbox, None,
                                               None,
                                               imaputils.mail_content(mail))
                        # The above will fail on some IMAP servers for various
                        # reasons. We print out what happened and continue
                        # processing
                        if res[0] != 'OK':
                            self.logger.error(__(
                                ("{} failed for uid {}: {}. Leaving original"
                                 + "message alone.").format(
                                     repr(["append", self.imapsets.spaminbox,
                                           "{email}"]),
                                     repr(uid), repr(res))))
                            continue
                else:
                    if self.dryrun:
                        self.logger.info("Skipping copy to spambox because"
                                         + " of --dryrun")
                    else:
                        # just copy it as is
                        res = self.imap.uid("COPY", uid,
                                            self.imapsets.spaminbox)
                        self.assertok(res, "uid copy", uid,
                                      self.imapsets.spaminbox)

                spamlist.append(uid)

        self.pastuid_write(uidvalidity, origpastuids, newpastuids)

        nummsg = len(uids)
        spamdeleted = len(spamdeletelist)
        numspam = len(spamlist) + spamdeleted

        # If we found any spams, now go and mark the original messages
        if numspam or spamdeleted:
            if self.dryrun:
                self.logger.info('Skipping labelling/expunging of mails '
                                 + ' because of --dryrun')
            else:
                res = self.imap.select(self.imapsets.inbox)
                self.assertok(res, 'select', self.imapsets.inbox)
                # Only set message flags if there are any
                if self.spamflags:  # len(self.smpamflgs) > 0
                    for uid in spamlist:
                        res = self.imap.uid("STORE", uid, self.spamflagscmd,
                                            imaputils.imapflags(self.spamflags)
                                            )
                        self.assertok(res, "uid store", uid, self.spamflagscmd,
                                      imaputils.imapflags(self.spamflags))
                        newpastuids.append(uid)
                # If its gmail, and --delete was passed, we actually copy!
                if self.delete and self.gmail:
                    for uid in spamlist:
                        res = self.imap.uid("COPY", uid, "[Gmail]/Trash")
                        self.assertok(res, "uid copy", uid, "[Gmail]/Trash")
                # Set deleted flag for spam with high score
                for uid in spamdeletelist:
                    if self.gmail is True:
                        res = self.imap.uid("COPY", uid, "[Gmail]/Trash")
                        self.assertok(res, "uid copy", uid, "[Gmail]/Trash")
                    else:
                        res = self.imap.uid("STORE", uid, self.spamflagscmd,
                                            "(\\Deleted)")
                        self.assertok(res, "uid store", uid, self.spamflagscmd,
                                      "(\\Deleted)")
                if self.expunge:
                    self.imap.expunge()

        return (numspam, nummsg, spamdeleted)

    def spamlearn(self):
        """Learn the spams (and if requested deleted or move them)."""
        learns = [
            {
                'inbox': self.imapsets.learnspambox,
                'learntype': 'spam',
                'moveto': None
            },
            {
                'inbox': self.imapsets.learnhambox,
                'learntype': 'ham',
                'moveto': self.movehamto
            },
        ]

        result = []

        for learntype in learns:
            n_learnt = 0
            n_tolearn = 0
            if learntype['inbox']:
                self.logger.debug(__("Teach {} to SA from: {}".format(
                    learntype['learntype'], learntype['inbox'])))
                uidvalidity = self.get_uidvalidity(learntype['inbox'])
                origpastuids = self.pastuid_read(uidvalidity,
                                                 folder=learntype['learntype'])
                newpastuids = []
                res = self.imap.select(learntype['inbox'])
                self.assertok(res, 'select', learntype['inbox'])
                if self.learnunflagged:
                    typ, uids = self.imap.uid("SEARCH", None, "UNFLAGGED")
                elif self.learnflagged:
                    typ, uids = self.imap.uid("SEARCH", None, "(FLAGGED)")
                else:
                    typ, uids = self.imap.uid("SEARCH", None, "ALL")
                uids = sorted(uids[0].split(), key=int, reverse=True)
                origpastuids = [u for u in origpastuids if str(u) in uids]
                uids = [u for u in uids if int(u) not in origpastuids]
                # Take only X elements if partialrun is enabled
                if self.partialrun:
                    uids = uids[:int(self.partialrun)]

                n_tolearn = len(uids)

                for uid in uids:
                    mail = imaputils.get_message(self.imap, uid,
                                                 logger=self.logger,
                                                 assertok=self.assertok)

                    # Unwrap spamassassin reports
                    unwrapped = unwrap(mail)
                    if unwrapped is not None:
                        self.logger.debug(__(
                            "{} Unwrapped: {}".format(uid, utils.shorten(
                                imaputils.mail_content(unwrapped[0]), 140))))

                    if unwrapped is not None and unwrapped:  # len(unwrapped)>0
                        mail = unwrapped[0]
                    if self.dryrun:
                        out = self.alreadylearnt
                        code = 0
                    else:
                        proc = self.popen(["spamc", "--learntype="
                                           + learntype['learntype']])
                        try:
                            out = proc.communicate(imaputils.mail_content(mail)
                                                   )[0]
                        except Exception:  # pylint: disable=broad-except
                            self.logger.exception(__(
                                'spamc error for mail {}'.format(uid)))
                            self.logger.debug(repr(
                                imaputils.mail_content(mail)))
                            continue
                        code = proc.returncode
                        proc.stdin.close()
                    if code == 69 or code == 74:
                        errorexit("spamd is misconfigured (use --allow-tell)",
                                  __exitcodes__['flags'])
                    if out.strip() == self.alreadylearnt or code == 6:
                        self.logger.debug(__(
                            ("Already learnt {} (spamc return"
                             + " code {})").format(uid, code)))
                    else:
                        n_learnt += 1
                        self.logger.debug(__(
                            "Learnt {} (spamc return code {})".format(uid,
                                                                      code)))
                    newpastuids.append(int(uid))
                    if not self.dryrun:
                        if self.learnthendestroy:
                            if self.gmail:
                                res = self.imap.uid("COPY", uid,
                                                    "[Gmail]/Trash")
                                self.assertok(res, "uid copy", uid,
                                              "[Gmail]/Trash")
                            else:
                                res = self.imap.uid("STORE", uid,
                                                    self.spamflagscmd,
                                                    "(\\Deleted)")
                                self.assertok(res, "uid store", uid,
                                              self.spamflagscmd, "(\\Deleted)")
                        elif learntype['moveto'] is not None:
                            res = self.imap.uid("COPY", uid,
                                                learntype['moveto'])
                            self.assertok(res, "uid copy", uid,
                                          learntype['moveto'])
                        elif self.learnthenflag:
                            res = self.imap.uid("STORE", uid,
                                                self.spamflagscmd,
                                                "(\\Flagged)")
                            self.assertok(res, "uid store", uid,
                                          self.spamflagscmd, "(\\Flagged)")
                self.pastuid_write(uidvalidity, origpastuids, newpastuids,
                                   folder=learntype['learntype'])
            result.append((n_tolearn, n_learnt))

        return result

    def do_isbg(self):
        """Execute the main isbg process.

        It should be called to process the IMAP account. It returns a
        exitcode if its called from the command line and have the --exitcodes
        param.
        """
        if self.spamc:
            self.satest = ["spamc", "-c"]
            self.sasave = ["spamc"]

        if self.delete and not self.gmail:
            self.spamflags.append("\\Deleted")

        if self.pastuidsfile is None:
            self.pastuidsfile = os.path.join(xdg_cache_home, "isbg", "track")
            newhash = md5()
            newhash.update(self.imapsets.host.encode())
            newhash.update(self.imapsets.user.encode())
            newhash.update(repr(self.imapsets.port).encode())
            res = newhash.hexdigest()
            self.pastuidsfile = self.pastuidsfile + res

        if self.passwdfilename is None:
            newhash = md5()
            newhash.update(self.imapsets.host.encode())
            newhash.update(self.imapsets.user.encode())
            newhash.update(repr(self.imapsets.port).encode())
            self.passwdfilename = os.path.join(xdg_cache_home, "isbg",
                                               ".isbg-" + newhash.hexdigest())

        if self.passwordhash is None:
            # We make hash that the password is xor'ed against
            mdh = md5()
            mdh.update(self.imapsets.host.encode())
            mdh.update(newhash.digest())
            mdh.update(self.imapsets.user.encode())
            mdh.update(newhash.digest())
            mdh.update(repr(self.imapsets.port).encode())
            mdh.update(newhash.digest())
            self.passwordhash = newhash.digest()
            while len(self.passwordhash) < self.passwordhashlen:
                newhash.update(self.passwordhash)
                self.passwordhash = self.passwordhash + newhash.digest()

        self.logger.debug(__("Lock file is {}".format(self.lockfilename)))
        self.logger.debug(__("Trackfile is {}".format(self.pastuidsfile)))
        self.logger.debug(__("SpamFlags are {}".format(self.spamflags)))
        self.logger.debug(__(
            "Password file is {}".format(self.passwdfilename)))

        # Acquire lockfilename or exit
        if self.ignorelockfile:
            self.logger.debug("Lock file is ignored. Continue.")
        else:
            if (os.path.exists(self.lockfilename) and
                    (os.path.getmtime(self.lockfilename) +
                     (self.lockfilegrace * 60) > time.time())):
                errorexit("Lock file is present. Guessing isbg is already "
                          + "running. Exit.", __exitcodes__['locked'])
            else:
                lockfile = open(self.lockfilename, 'w')
                lockfile.write(repr(os.getpid()))
                lockfile.close()
                # Make sure to delete lock file
                atexit.register(self.removelock)

        # Figure out the password
        if self.imapsets.passwd is None:
            if (self.savepw is False and
                    os.path.exists(self.passwdfilename) is True):
                try:
                    self.imapsets.passwd = self.getpw(utils.dehexof(open(
                        self.passwdfilename,
                        "rb").read().decode()),
                        self.passwordhash)
                    self.logger.debug("Successfully read password file")
                except Exception:  # pylint: disable=broad-except
                    self.logger.exception('Error reading pw!')

            # do we have to prompt?
            if self.imapsets.passwd is None:
                if not self.interactive:
                    errorexit("You need to specify your imap password and "
                              + "save it with the --savepw switch",
                              __exitcodes__['ok'])
                self.imapsets.passwd = getpass.getpass(
                    "IMAP password for %s@%s: " % (
                        self.imapsets.user, self.imapsets.host))

        # Should we save it?
        if self.savepw:
            wfile = open(self.passwdfilename, "wb+")
            try:
                os.chmod(self.passwdfilename, 0o600)
            except Exception:  # pylint: disable=broad-except
                self.logger.exception('Error saving pw!')
            wfile.write(utils.hexof(self.setpw(self.imapsets.passwd,
                                               self.passwordhash)).encode())
            wfile.close()

        # Main code starts here

        # Connection with the imaplib server
        self.imap = imaputils.login_imap(self.imapsets,
                                         logger=self.logger,
                                         assertok=self.assertok)

        # List imap directories
        if self.imaplist:
            imap_list = self.imap.list()
            self.assertok(imap_list, "list")
            dirlist = str([x.decode() for x in imap_list[1]])
            # string formatting
            dirlist = re.sub(r'\(.*?\)| \".\" \"|\"\', \'', " ", dirlist)
            self.logger.info(dirlist)

        # Spamassassin training
        s_tolearn, s_learnt, h_tolearn, h_learnt = (0, 0, 0, 0)
        if not self.imaplist:
            learned = self.spamlearn()
            s_tolearn, s_learnt = learned[0]
            h_tolearn, h_learnt = learned[1]

        # Spamassassin processing
        numspam, nummsg, spamdeleted = (0, 0, 0)
        if not self.imaplist:
            if not self.teachonly:
                numspam, nummsg, spamdeleted = self.spamassassin()

        # sign off
        self.imap.logout()
        del self.imap

        if self.nostats is False:
            if self.imapsets.learnspambox is not None:
                self.logger.info(__(
                    "{}/{} spams learnt".format(s_learnt, s_tolearn)))
            if self.imapsets.learnhambox:
                self.logger.info(__(
                    "{}/{} hams learnt".format(h_learnt, h_tolearn)))
            if not self.teachonly:
                self.logger.info(__(
                    "{} spams found in {} messages".format(numspam, nummsg)))
                self.logger.info(__("{}/{} was automatically deleted".format(
                    spamdeleted, numspam)))

        if self.exitcodes and __name__ == '__main__':
            if not self.teachonly:
                res = 0
                if numspam == 0:
                    return __exitcodes__['newmsgs']
                if numspam == nummsg:
                    return __exitcodes__['newspam']
                return __exitcodes__['newmsgspam']

            return __exitcodes__['ok']


def isbg_run():
    """Run when this module is called from the command line."""
    sbg = ISBG()
    sbg.parse_args()
    return sbg.do_isbg()  # return the exit code.


if __name__ == '__main__':
    isbgret = isbg_run()  # pylint: disable=invalid-name
    if isbgret is not None:
        sys.exit(isbgret)
