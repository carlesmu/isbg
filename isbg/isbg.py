#!/usr/bin/env python2
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
    --dryrun             Do not actually make any changes
    --delete             The spams will be marked for deletion from your inbox
    --deletehigherthan # Delete any spam with a score higher than #
    --exitcodes          Use exitcodes to detail  what happened
    --expunge            Cause marked for deletion messages to also be deleted
                         (only useful if --delete is specified)
    --flag               The spams will be flagged in your inbox
    --gmail              Delete by copying to '[Gmail]/Trash' folder
    --help               Show the help screen
    --ignorelockfile     Don't stop if lock file is present
    --imaphost hostname  IMAP server name
    --imaplist           List imap directories
    --imappasswd passwd  IMAP account password
    --imapport port      Use a custom port
    --imapuser username  Who you login as
    --imapinbox mbox     Name of your inbox folder
    --learnspambox mbox  Name of your learn spam folder
    --learnhambox mbox   Name of your learn ham folder
    --learnthendestroy   Mark learnt messages for deletion
    --learnthenflag      Flag learnt messages
    --learnunflagged     Only learn if unflagged (for --learnthenflag)
    --learnflagged       Only learn flagged
    --lockfilegrace #    Set the lifetime of the lock file to # (in minutes)
    --lockfilename file  Override the lock file name
    --maxsize numbytes   Messages larger than this will be ignored as they are
                         unlikely to be spam
    --movehamto mbox     Move ham to folder
    --noninteractive     Prevent interactive requests
    --noreport           Don't include the SpamAssassin report in the message
                         copied to your spam folder
    --nostats            Don't print stats
    --partialrun num     Stop operation after scanning 'num' unseen emails
    --passwdfilename fn  Use a file to supply the password
    --savepw             Store the password to be used in future runs
    --spamc              Use spamc instead of standalone SpamAssassin binary
    --spaminbox mbox     Name of your spam folder
    --nossl              Don't use SSL to connect to the IMAP server
    --teachonly          Don't search spam, just learn from folders
    --trackfile file     Override the trackfile name
    --verbose            Show IMAP stuff happening
    --verbose-mails      Show mail bodies (extra-verbose)
    --version            Show the version information

    (Your inbox will remain untouched unless you specify --flag or --delete)

"""

__version__ = "2.0-dev"

import socket  # to catch the socket.error exception
import sys     # Because sys.stderr.write() is called bellow
from io import BytesIO

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
    from docopt import docopt  # Creating command-line interface
except ImportError:
    sys.stderr.write("Missing dependency: docopt\n")
    raise

from subprocess import Popen, PIPE

import email      # To eassily encapsulated emails messages
import imaplib
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


class ISBGError(Exception):
    """Class for the ISBG exceptions."""

    pass


def errorexit(msg, exitcode):
    """Raise an ISBGError.

    If its runed as a commandline also show a help message and exits.
    """
    if __name__ == '__main__':
        sys.stderr.write(msg)
        sys.stderr.write("\nUse --help to see valid options and arguments\n")
        if exitcode == -1:
            raise ISBGError((exitcode, msg))
        sys.exit(exitcode)
    else:
        raise ISBGError((exitcode, msg))


def hexof(string):
    """Translate a string to a string with its hexadecimal value."""
    res = ""
    for i in string:
        res = res + ("%02x" % ord(i))
    return res


def hexdigit(char):
    """Tanslate a hexadecimal character his decimal (int) value."""
    if char >= '0' and char <= '9':
        return ord(char) - ord('0')
    if char >= 'a' and char <= 'f':
        return 10 + ord(char) - ord('a')
    if char >= 'A' and char <= 'F':
        return 10 + ord(char) - ord('A')
    raise ValueError(repr(char) + " is not a valid hexadecimal digit")


def dehexof(string):
    """Tanslate a hexadecimal string to his string value."""
    res = ""
    while len(string):
        res = res + chr(16 * hexdigit(string[0]) + hexdigit(string[1]))
        string = string[2:]
    return res


def truncate(inp, length):
    """Truncate a string to  a maximus length."""
    if len(inp) > length:
        return repr(inp)[:length - 3] + '...'
    return inp


def shorten(inp, length):
    """Short a dict or a list or other object to a maximus length."""
    if isinstance(inp, dict):
        return dict([(k, shorten(v, length)) for k, v in inp.items()])
    elif isinstance(inp, list) or isinstance(inp, tuple):
        return [shorten(x, length) for x in inp]
    return truncate(inp, length)


def imapflags(flaglist):
    """Transform a list to a string as expected for the IMAP4 standard."""
    return '(' + ','.join(flaglist) + ')'


class ImapSettings(object):
    """Class used to store the IMAP settigs."""

    def __init__(self):
        """Set Imap settings."""
        self.host = 'localhost'
        self.port = 143
        self.user = ''
        self.passwd = None
        self.nossl = False
        # Set mailboxes.
        self.inbox = 'INBOX'
        self.spaminbox = 'INBOX.spam'
        self.learnspambox = None
        self.learnhambox = None


class ISBG(object):
    """Main ISBG class."""

    exitcodeok = 0          # all went well
    exitcodenewmsgs = 1     # there were new messages - none of them spam
    exitcodenewspam = 2     # they were all spam
    exitcodenewmsgspam = 3  # there were new messages and new spam
    exitcodeflags = 10      # there were errors in the command line arguments
    exitcodeimap = 11       # there was an IMAP level error
    exitcodespamc = 12      # error of communication between spamc and spamd
    exitcodetty = 20        # error because of non interative terminal
    exitcodelocked = 30     # there's certainly another isbg running

    def __init__(self):
        """Initialize a ISBG object."""
        self.imapsets = ImapSettings()

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

        # Initializes variables
        if __name__ is not '__main__':
            self.set_reporting_opts()
            self.set_processing_opts()
            self.set_lockfile_opts()
            self.set_password_opts()
            self.set_trackfile_opts()
            self.set_sa_opts()
            self.set_learning_opts()

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
        """Helper to call Popen."""
        if os.name == 'nt':
            return Popen(cmd, stdin=PIPE, stdout=PIPE)
        else:
            return Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)

    def set_reporting_opts(self, imaplist=False, nostats=False, noreport=False,
                           exitcodes=True, verbose=False, verbose_mails=False):
        """Set reporting options."""
        self.imaplist = imaplist
        self.nostats = nostats
        self.noreport = noreport
        self.exitcodes = exitcodes
        self.verbose = verbose
        if self.verbose:
            self.set_loglevel(logging.DEBUG)
        else:
            self.set_loglevel(logging.INFO)
        self.verbose_mails = verbose_mails

    def set_processing_opts(self, dryrun=False, maxsize=120000,
                            teachonly=False, spamc=False, gmail=False):
        """Set processing options."""
        self.dryrun = dryrun
        self.maxsize = maxsize
        self.teachonly = teachonly
        self.spamc = spamc
        self.gmail = gmail

    def set_lockfile_opts(self, ignorelockfile=False,
                          lockfilename=os.path.join(xdg_cache_home,
                                                    "isbg", "lock"),
                          lockfilegrace=240):
        """Set lockfile options."""
        self.ignorelockfile = ignorelockfile
        self.lockfilename = lockfilename
        self.lockfilegrace = lockfilegrace

    def set_password_opts(self, passwdfilename=None, savepw=False):
        """Set password options."""
        self.passwdfilename = passwdfilename
        self.savepw = savepw

    def set_trackfile_opts(self, trackfile=None, partialrun=False):
        """Set trackfile options."""
        self.pastuidsfile = trackfile
        self.partialrun = partialrun

    def set_sa_opts(self, movehamto=None, delete=False, deletehigherthan=None,
                    flag=False, expunge=False):
        """Set spamassassin options."""
        self.movehamto = movehamto
        self.delete = delete
        self.deletehigherthan = deletehigherthan
        self.flag = flag
        self.expunge = expunge

    def set_learning_opts(self, learnflagged=False, learnunflagged=False,
                          learnthendestroy=False, learnthenflag=False):
        """Set learning options."""
        if learnflagged and learnunflagged:
            raise ValueError(
                'Cannot pass learnflagged and learnunflagged at same time')
        self.learnflagged = learnflagged
        self.learnunflagged = learnunflagged
        self.learnthendestroy = learnthendestroy
        self.learnthenflag = learnthenflag

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
    def getpw(self, data, hash):
        """Deobfuscate IMAP password."""
        res = ""
        for i in range(0, self.passwordhashlen):
            j = ord(data[i]) ^ ord(hash[i])
            if j == 0:
                break
            res = res + chr(j)
        return res

    def setpw(self, passwd, hash):
        """Obfuscate password."""
        if len(passwd) > self.passwordhashlen:
            raise ValueError(("Password of length %d is too long to "
                              + "store (max accepted is %d)"
                              ) % (len(passwd), self.passwordhashlen))
        res = list(hash)
        for i in range(0, len(passwd)):
            res[i] = chr(ord(res[i]) ^ ord(passwd[i]))
        return ''.join(res)

    def login_imap(self):
        """Login to the imap server."""
        max_retry = 10
        retry_time = 0.60   # seconds
        for retry in range(1, max_retry + 1):
            try:
                if self.imapsets.nossl:
                    self.imap = imaplib.IMAP4(self.imapsets.host,
                                              self.imapsets.port)
                else:
                    self.imap = imaplib.IMAP4_SSL(self.imapsets.host,
                                                  self.imapsets.port)
                break   # ok, exit for loop
            except socket.error as exc:
                self.logger.warning(('Error in IMAP connection: {} ... retry '
                                     + '{} of {}').format(exc, retry,
                                                          max_retry))
                if retry >= max_retry:
                    raise Exception(exc)
                else:
                    time.sleep(retry_time)
        self.logger.debug(
            'Server capabilities: {}'.format(self.imap.capability()))
        # Authenticate (only simple supported)
        res = self.imap.login(self.imapsets.user, self.imapsets.passwd)
        self.assertok(res, "login", self.imapsets.user, 'xxxxxxxx')

    def getmessage(self, uid, append_to=None):
        """Get a message by uid and optionaly append its uid to a list."""
        res = self.imap.uid("FETCH", uid, "(BODY.PEEK[])")
        self.assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
        mail = email.message.Message()
        if res[0] != "OK":
            self.assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
            try:
                body = res[1][0][1]
                mail = email.message_from_string(body)
            except Exception:  # pylint: disable=broad-except
                self.logger.warning(("Confused - rfc822 fetch gave {} - The "
                                     + "message was probably deleted while we "
                                     + "were running").format(res))
        else:
            body = res[1][0][1]
            mail = email.message_from_string(body)
        if append_to is not None:
            append_to.append(int(uid))
        return mail

    def assertok(self, res, *args):
        """Check that the return code is OK.

        It also prints out what happened (which would end
        up /dev/null'ed in non-verbose mode)
        """
        if 'fetch' in args[0] and not self.verbose_mails:
            res = shorten(res, 140)
        self.logger.debug("{} = {}".format(args, res))
        if res[0] != "OK":
            self.logger.error("{} returned {} - aborting")
            errorexit("\n%s returned %s - aborting\n"
                      % (repr(args), res),
                      self.exitcodeimap if self.exitcodes else -1)

    def parse_args(self):
        """Argument processing."""
        try:
            self.opts = docopt(__doc__, version="isbg version " + __version__)
            self.opts = dict([(k, v) for k, v in self.opts.items()
                              if v is not None])
        except Exception as exc:  # pylint: disable=broad-except
            errorexit("Option processing failed - " + str(exc),
                      self.exitcodeflags)

        if self.opts.get("--deletehigherthan") is not None:
            try:
                self.deletehigherthan = float(self.opts["--deletehigherthan"])
            except Exception:  # pylint: disable=broad-except
                errorexit("Unrecognized score - "
                          + self.opts["--deletehigherthan"],
                          self.exitcodeflags)
            if self.deletehigherthan < 1:
                errorexit("Score " + repr(self.deletehigherthan)
                          + " is too small", self.exitcodeflags)
        else:
            self.deletehigherthan = None

        if self.opts["--flag"] is True:
            self.spamflags.append("\\Flagged")

        self.imapsets.host = self.opts.get('--imaphost', self.imapsets.host)
        self.imapsets.passwd = self.opts.get('--imappasswd',
                                             self.imapsets.passwd)
        self.imapsets.port = self.opts.get('--imapport', self.imapsets.port)
        self.imapsets.user = self.opts.get('--imapuser', self.imapsets.user)
        self.imapsets.inbox = self.opts.get('--imapinbox', self.imapsets.inbox)
        self.imapsets.spaminbox = self.opts.get('--spaminbox',
                                                self.imapsets.spaminbox)
        self.imapsets.learnspambox = self.opts.get('--learnspambox')
        self.imapsets.learnhambox = self.opts.get('--learnhambox')
        self.imapsets.nossl = self.opts.get('--nossl', False)

        self.lockfilegrace = self.opts.get('--lockfilegrace',
                                           self.lockfilegrace)
        self.nostats = self.opts.get('--nostats', False)
        self.dryrun = self.opts.get('--dryrun', False)
        self.delete = self.opts.get('--delete', False)
        self.gmail = self.opts.get('--gmail', False)

        if self.opts.get("--maxsize") is not None:
            try:
                self.maxsize = int(self.opts["--maxsize"])
            except (TypeError, ValueError):
                errorexit("Unrecognised size - " + self.opts["--maxsize"],
                          self.exitcodeflags)
            if self.maxsize < 1:
                errorexit("Size " + repr(self.maxsize) + " is too small",
                          self.exitcodeflags)

        self.movehamto = self.opts.get('--movehamto')

        if self.opts["--noninteractive"] is True:
            self.interactive = 0

        self.noreport = self.opts.get('--noreport', self.noreport)

        self.lockfilename = self.opts.get('--lockfilename', self.lockfilename)

        self.pastuidsfile = self.opts.get('--trackfile', self.pastuidsfile)

        if self.opts.get("--partialrun") is not None:
            self.partialrun = int(self.opts["--partialrun"])
            if self.partialrun < 1:
                errorexit("Partial run number must be equal to 1 or higher",
                          self.exitcodeflags)

        self.verbose = self.opts.get('--verbose', False)
        if self.verbose:
            self.set_loglevel(logging.DEBUG)
        else:
            self.set_loglevel(logging.INFO)

        self.verbose_mails = self.opts.get('--verbose-mails', False)
        self.ignorelockfile = self.opts.get("--ignorelockfile", False)
        self.savepw = self.opts.get('--savepw', False)
        self.passwdfilename = self.opts.get('--passwdfilename',
                                            self.passwdfilename)

        self.imaplist = self.opts.get('--imaplist', False)

        self.learnunflagged = self.opts.get('--learnunflagged', False)
        self.learnflagged = self.opts.get('--learnflagged', False)
        self.learnthendestroy = self.opts.get('--learnthendestroy', False)
        self.learnthenflag = self.opts.get('--learnthendestroy', False)
        self.expunge = self.opts.get('--expunge', False)

        self.teachonly = self.opts.get('--teachonly', False)
        self.spamc = self.opts.get('--spamc', False)

        self.exitcodes = self.opts.get('--exitcodes', False)

        # fixup any arguments

        if self.opts.get("--imapport") is None:
            if self.opts["--nossl"] is True:
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
        self.logger.debug(('Writing pastuids, {} origpastuids, '
                           + 'newpastuids: {}'
                           ).format(len(origpastuids), newpastuids))
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

        self.logger.debug('Got {} mails to check'.format(len(uids)))

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
            mail = self.getmessage(uid, newpastuids)
            # Unwrap spamassassin reports
            unwrapped = unwrap(BytesIO(mail.as_string()))
            if unwrapped is not None and len(unwrapped) > 0:
                mail = email.message_from_string(unwrapped[0])

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
                    score = proc.communicate(mail.as_string()
                                             )[0].decode(errors='ignore')
                    if not self.spamc:
                        res = re.search(
                            "score=(-?\d+(?:\.\d+)?) required=(\d+(?:\.\d+)?)",
                            score)
                        score = res.group(1) + "/" + res.group(2) + "\n"
                    code = proc.returncode
                except Exception:  # pylint: disable=broad-except
                    self.logger.exception(
                        'Error communicating with {}!'.format(self.satest))
                    uids.remove(uid)
                    continue
                proc.stdin.close()
            if score == "0/0\n":
                errorexit("spamc -> spamd error - aborting",
                          self.exitcodespamc)

            self.logger.debug("Score for uid {}: {}".format(uid,
                                                            score.strip()))

            if code == 0:
                # Message is below threshold
                pass
            else:
                # Message is spam, delete it or move it to spaminbox
                # (optionally with report)
                self.logger.debug("{} is spam".format(uid))

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
                                mail.as_string())[0])
                        except Exception:  # pylint: disable=broad-except
                            self.logger.exception(
                                'Error communicating with {}!'.format(
                                    self.sasave))
                            continue
                        proc.stdin.close()
                        res = self.imap.append(self.imapsets.spaminbox, None,
                                               None, mail.as_string())
                        # The above will fail on some IMAP servers for various
                        # reasons. We print out what happened and continue
                        # processing
                        if res[0] != 'OK':
                            self.logger.error(
                                ("{} failed for uid {}: {}. Leaving original"
                                 + "message alone.").format(
                                    repr(["append",
                                          self.imapsets.spaminbox, "{email}"]),
                                    repr(uid), repr(res)))
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
                if len(self.spamflags) > 0:
                    for uid in spamlist:
                        res = self.imap.uid("STORE", uid, self.spamflagscmd,
                                            imapflags(self.spamflags))
                        self.assertok(res, "uid store", uid, self.spamflagscmd,
                                      imapflags(self.spamflags))
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
                self.logger.debug("Teach {} to SA from: {}".format(
                    learntype['learntype'], learntype['inbox']))
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
                    mail = self.getmessage(uid)
                    # Unwrap spamassassin reports
                    unwrapped = unwrap(BytesIO(mail.as_string()))
                    if unwrapped is not None:
                        self.logger.debug(
                            "{} Unwrapped: {}".format(uid, shorten(unwrapped,
                                                                   140)))
                    if unwrapped is not None and len(unwrapped) > 0:
                        mail = email.message_from_string(unwrapped[0])
                    if self.dryrun:
                        out = self.alreadylearnt
                        code = 0
                    else:
                        proc = self.popen(["spamc", "--learntype="
                                           + learntype['learntype']])
                        try:
                            out = proc.communicate(mail.as_string())[0]
                        except Exception:  # pylint: disable=broad-except
                            self.logger.exception(
                                'spamc error for mail {}'.format(uid))
                            self.logger.debug(repr(mail.as_string()))
                            continue
                        code = proc.returncode
                        proc.stdin.close()
                    if code == 69 or code == 74:
                        errorexit("spamd is misconfigured (use --allow-tell)",
                                  self.exitcodeflags)
                    if out.strip() == self.alreadylearnt or code == 6:
                        self.logger.debug(("Already learnt {} (spamc return"
                                           + " code {})").format(uid, code))
                    else:
                        n_learnt += 1
                        self.logger.debug(
                            "Learnt {} (spamc return code {})".format(uid,
                                                                      code))
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
        """Main isbg process.

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

        self.logger.debug("Lock file is {}".format(self.lockfilename))
        self.logger.debug("Trackfile is {}".format(self.pastuidsfile))
        self.logger.debug("SpamFlags are {}".format(self.spamflags))
        self.logger.debug("Password file is {}".format(self.passwdfilename))

        # Acquire lockfilename or exit
        if self.ignorelockfile:
            self.logger.debug("Lock file is ignored. Continue.")
        else:
            if (os.path.exists(self.lockfilename) and
                    (os.path.getmtime(self.lockfilename) +
                     (self.lockfilegrace * 60) > time.time())):
                errorexit("Lock file is present. Guessing isbg is already "
                          + "running. Exit.", self.exitcodelocked)
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
                    self.imapsets.passwd = self.getpw(dehexof(open(
                        self.passwdfilename,
                        "rb").read().decode()),
                        self.passwordhash)
                    self.logger.debug("Successfully read password file")
                except Exception:  # pylint: disable=broad-except
                    self.logger.exception('Error reading pw!')
                    pass

            # do we have to prompt?
            if self.imapsets.passwd is None:
                if not self.interactive:
                    errorexit("You need to specify your imap password and "
                              + "save it with the --savepw switch",
                              self.exitcodeok)
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
                pass
            wfile.write(hexof(self.setpw(self.imapsets.passwd,
                                         self.passwordhash)).encode())
            wfile.close()

        # Main code starts here

        # Connection with the imaplib server
        self.login_imap()

        # List imap directories
        if self.imaplist:
            imap_list = self.imap.list()
            self.assertok(imap_list, "list")
            dirlist = str([x.decode() for x in imap_list[1]])
            # string formatting
            dirlist = re.sub('\(.*?\)| \".\" \"|\"\', \'', " ", dirlist)
            self.logger.info(dirlist)

        # Spamassassin training
        learned = self.spamlearn()
        s_tolearn, s_learnt = learned[0]
        h_tolearn, h_learnt = learned[1]

        # Spamassassin processing
        if not self.teachonly:
            numspam, nummsg, spamdeleted = self.spamassassin()

        # sign off
        self.imap.logout()
        del self.imap

        if self.nostats is False:
            if self.imapsets.learnspambox is not None:
                self.logger.info("{}/{} spams learnt".format(s_learnt,
                                                             s_tolearn))
            if self.imapsets.learnhambox:
                self.logger.info("{}/{} hams learnt".format(h_learnt,
                                                            h_tolearn))
            if not self.teachonly:
                self.logger.info("{} spams found in {} messages".format(
                    numspam, nummsg))
                self.logger.info("{}/{} was automatically deleted".format(
                    spamdeleted, numspam))

        if self.exitcodes and __name__ == '__main__':
            if not self.teachonly:
                res = 0
                if numspam == 0:
                    return self.exitcodenewmsgs
                if numspam == nummsg:
                    return self.exitcodenewspam
                return self.exitcodenewmsgspam

            return self.exitcodeok


def isbg_run():
    """Run when this module is called from the command line."""
    isbg = ISBG()
    isbg.parse_args()
    return isbg.do_isbg()  # return the exit code.


if __name__ == '__main__':
    isbgret = isbg_run()  # pylint: disable=invalid-name
    if isbgret is not None:
        sys.exit(isbgret)
