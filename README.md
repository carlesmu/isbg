| Stable:
[![Documentation Status](https://readthedocs.org/projects/isbg/badge/?version=stable)](http://isbg.readthedocs.io/en/stable/?badge=stable)
| Default:
[![Build Status](https://travis-ci.org/carlesmu/isbg.svg?branch=v2.0-dev)](https://travis-ci.org/carlesmu/isbg)
[![Codeclimate Maintainability](https://api.codeclimate.com/v1/badges/c487d0d5ee45186aded1/maintainability)](https://codeclimate.com/github/carlesmu/isbg/maintainability)
[![Codeclimate Coverage](https://api.codeclimate.com/v1/badges/c487d0d5ee45186aded1/test_coverage)](https://codeclimate.com/github/carlesmu/isbg/test_coverage)
[![codecov](https://codecov.io/gh/carlesmu/isbg/branch/v2.0-dev/graph/badge.svg)](https://codecov.io/gh/carlesmu/isbg)
| Master:
[![Documentation Status](https://readthedocs.org/projects/isbg/badge/?version=latest)](http://isbg.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e639e80142824c34bed0b13440136a01?branch=master)](https://www.codacy.com/app/carlesmu/isbg?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=carlesmu/isbg&amp;utm_campaign=Badge_Grade)
[![Codacy coverage Badge](https://api.codacy.com/project/badge/Coverage/e639e80142824c34bed0b13440136a01?branch=master)](https://www.codacy.com/app/carlesmu/isbg?utm_source=github.com&utm_medium=referral&utm_content=carlesmu/isbg&utm_campaign=Badge_Coverage)
| v2.0-dev:
[![Documentation Status](https://readthedocs.org/projects/isbg/badge/?version=v2.0-dev)](http://isbg.readthedocs.io/en/v2.0-dev/?badge=v2.0-dev)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e639e80142824c34bed0b13440136a01?branch=v2.0-dev)](https://www.codacy.com/app/carlesmu/isbg?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=carlesmu/isbg&amp;utm_campaign=Badge_Grade)
[![Codacy coverage Badge](https://api.codacy.com/project/badge/Coverage/e639e80142824c34bed0b13440136a01?branch=v2.0-dev)](https://www.codacy.com/app/carlesmu/isbg?utm_source=github.com&utm_medium=referral&utm_content=carlesmu/isbg&utm_campaign=Badge_Coverage)


# IMAP Spam Begone

isbg is a script and a python module that makes it easy to scan an IMAP inbox
for spam using SpamAssassin and get your spam moved to another folder.

Unlike the normal mode of deployments for SpamAssassin, isbg does
not need to be involved in mail delivery, and can run on completely
different machines to where your mailbox actually is. So this is the
perfect tool to take good care of your ISP mailbox without having to
leave it.

* [Features](#features)
* [Installation](#installation)
  * [Install from source](#install-from-source)
  * [Pip install](#pip-install)
* [Usage](#usage)
  * [SpamAssassin](#spamassassin)
    * [Configure your spamassassin](#configure-your-spamassassin)
      * [Allow-tell](#allow-tell)
  * [CLI Options](#cli-options)
  * [Do your first run](#do-your-first-run)
    * [Running it](#running-it)
  * [Your folder names](#your-folder-names)
  * [How does it work?](#how-does-it-work)
  * [Multiple accounts](#multiple-accounts)
  * [Saving your password](#saving-your-password)
  * [SSL](#ssl)
  * [Exit Codes](#exit-codes)
  * [Read and Seen flags](#read-and-seen-flags)
  * [Gmail Integration](#gmail-integration)
  * [Ignored emails](#ignored-emails)
  * [Partial runs](#partial-runs)
* [Contact and about](#contact-and-about)
* [License](#license)

## Features

* Works with all common IMAP servers
* Works on Linux, MacOS X and Windows (even smartphones!)
* Can do IMAP over SSL
* Can remember your password
* Will work painlessly against multiple IMAP accounts and servers
* Is not involved in the mail delivery process, and so can run on any machine 
  that can contact your IMAP server
* Highly configurable
* Sensible defaults so you don't have to do any configuring :-)
* Compatibility with Python 2.7, 3.5, 3.6
* Possibility to skip spam detection to stick only to the teach feature
* Don't fail when meeting horrible and bad formed mail
* Lock file to prevent multiple instance to run at the same time (for cron 
  jobs)

## Installation

Isbg install a python package module and also a script to use it `isbg`, it
also install another script to unwrap messages: `sa_unwrap`.

### Dependencies

Isbg is written in the Python language. Python is installed by default on most
Linux systems. You can can find out more about Python at 
[www.python.org](http://www.python.org/)

Make sure you have SpamAssassin installed. All the necessary information
can be found on the
[SpamAssassin wiki](https://wiki.apache.org/spamassassin/FrontPage).
SpamAssassin should be on your `$PATH` (it installs in `/usr/bin/` by default)

To run, `isbg` also depend on some python modules.
* [chardet](https://pypi.python.org/pypi/chardet) for encoding detection.
* [docopt](https://pypi.python.org/pypi/docopt) for command line options.
* [xdg](https://pypi.python.org/pypi/docopt) to found the `.cache` directory.
  `xdg` is not required, if it's not installed, isbg will try to found 
  `.cache`.


### Install from source

from the main directory where you have download isbg, run:

    $ python setup.py install --record installed_files.txt

It will install under `/usr/local/`. Supposing that you are using Python 2.7,
the package module should be in `/usr/local/lib/python2.7/dist-packages/` and
the main script will be `/usr/local/bin/isbg`.

In `installed_files.txt` there should be the list of files installed. To
uninstall them, use:

    $ tr '\n' '\0' < installed_files.txt | xargs -0 rm -vf --

In windows systems, you can build a windows installer using:

    python setup.py bdist_wininst

### install with PyPi

You also can install it from [Pypi](https://pypi.python.org/pypi/isbg), use:

    $ pip install isbg

To see the files installed you can use: 

    $ pip show isbg --files

And to uninstall it:

    $ pip uninstall isbg

## Usage

### SpamAssassin

If you have never used SpamAssassin before, you'll probably be quite
nervous about it being too good and taking out legitimate email, or not
taking out enough spam. It has an easily adustable threshold to change
how aggressive it is. Run the following command to create your
preferences file.

    $ spamassassin  &lt;/dev/null &gt;/dev/null
    Created user preferences file: /home/rogerb/.spamassassin/user_prefs

You can then edit `$HOME/.spamassassin/user_prefs` and change the thresholds.

You can also edit the system-wide settings in `/etc/spamassassin/locals.cf`.

If you want to use the `--learnspambox` or `--learnhambox`, you'll have
 to configure your spamassassin.

#### Configure your spamassassin

If you want to use `--learnspambox` or `--learnhambox` features,
you have to add this configuration:

##### Allow Tell

You have to start `spamd` with the `--allow-tell` option.

On Debian systems (Debian and Ubuntu), you have to edit
`/etc/default/spamassassin` and replace:

    OPTIONS="-D --create-prefs --max-children 5 --helper-home-dir"

by:

    OPTIONS="-D --allow-tell --create-prefs --max-children 5 --helper-home-dir"

Don't forget to restart your spamd server after that
 (`sudo service spamassassin restart` on Debian).


### CLI Options

The default behavior of isbg is to not make any changes your Inbox
unless you specify specific command line options. Consequently you can
experiment without worry at the beginning.

Your first step is to create a new folder to receive suspected spam.
 I use one named 'spam'.

Run isbg with the `--help` option to see what options are available:

    --imaphost hostname    IMAP server name.
    --imapuser username    Who you login as.
    --dryrun               Do not actually make any changes.
    --delete               The spams will be marked for deletion from 
                           your inbox.
    --deletehigherthan #   Delete any spam with a score higher than #.
    --exitcodes            Use exitcodes to detail  what happened.
    --expunge              Cause marked for deletion messages to also be
                           deleted (only useful if --delete is 
                           specified).
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
    --learnunflagged       Only learn if unflagged
                           (for  --learnthenflag).
    --learnflagged         Only learn flagged.
    --lockfilegrace=min    Set the lifetime of the lock file
                           [default: 240.0].
    --lockfilename file    Override the lock file name.
    --maxsize numbytes     Messages larger than this will be ignored as
                           they are unlikely to be spam.
    --movehamto mbox       Move ham to folder.
    --noninteractive       Prevent interactive requests.
    --noreport             Don't include the SpamAssassin report in the
                           message copied to your spam folder.
    --nostats              Don't print stats.
    --partialrun num       Stop operation after scanning 'num' unseen
                           emails. Use 0 to run without partial run
                           [default: 50].
    --passwdfilename fn    Use a file to supply the password.
    --savepw               Store the password to be used in future runs.
    --spamc                Use spamc instead of standalone SpamAssassin
                           binary.
    --spaminbox mbox       Name of your spam folder
                           [Default: INBOX.spam].
    --nossl                Don't use SSL to connect to the IMAP server.
    --teachonly            Don't search spam, just learn from folders.
    --trackfile file       Override the trackfile name.
    --verbose              Show IMAP stuff happening.
    --verbose-mails        Show mail bodies (extra-verbose).
    --version              Show the version information.
    
    (Your inbox will remain untouched unless you specify --flag or 
    --delete)

You can specify your imap password using `--imappasswd`.
This however is a really bad idea since any user on the system can run `ps` and
see the command line arguments. If you really must do it non-interactively
then set the password here.


### Do your first run

<pre>
$ isbg.py --imaphost mail.example.com  --savepw
IMAP password for rogerb@mail.example.com:
</pre>

The amount of time it takes will be proportional to the size of your
 inbox. You can specify `--verbose` if you want to see the gory details of
 what is going on.

You can now examine your spam folder and will see what spam was
detected. You can change the SpamAssassin threshold in your `user_prefs`
file it created earlier.

isbg remembers which messages it has already seen, so that it
doesn't process them again every time it is run. If you are testing and
do want it to run again, then remove the trackfile (default
`$HOME/.cache/isbg/track*`).

If you specified `--savepw` then isbg will remember your password the
next time you run against the same server with the same username. You
should not specify `--savepw` in future runs unless you want to change the
 saved password.

#### Running it

You'll probably want something to actually be done with the original
 spams in your inbox. By default nothing happens to them, but you have
two options available. If you specify `--flag` then spams will be flagged.

You can get the messages marked for deletion by specifying `--delete`.
 If you never want to see them in your inbox, also specify the `--expunge`
 option after `--delete` and they will be removed when isbg logs out of
the IMAP server.

### Your folder names

Each IMAP implementation names their folders differently, and most
IMAP clients manage to hide most of this from you. If your IMAP server
is Courier, then your folders are all below INBOX, and use dots to
seperate the components.

The UWash server typically has the folders below Mail and uses
slash (`/`) to seperate components.

If you don't know how your IMAP folders are implemented, you can always use
the `--imaplist` option to find out.

### How does it work?

IMAP assigns each message in a folder a unique id. isbg scans the
folder for messages it hasn't seen before, and for each one, downloads
the message and feeds it to SpamAssassin. If SpamAssassin says the
message is spam, then the SpamAssassin report is uploaded into your spam
 folder. Unless you specify the `--noreport` option, in which case the
message is copied from your Inbox to the Spam folder (the copy happens on
 the IMAP server itself so this option is good if you are on a low
bandwidth connection).

### Multiple accounts

By default isbg saves the list of seen IMAP message unique IDs in a
file in your home directory. It is named `.isbg-trackXXXX` where XXXX is a
 16 byte identifier based on the IMAP host, username and port number.
Consequently you can just run isbg against different servers/accounts
and it will automatically keep the tracked UIDs seperate. You can
override the filename with `--trackfile`.

To run isbg for multiple accounts one after another, it is possible to use
bash scripts like the ones in the folder "bash_scripts". Since these scripts
contain passwords and are thus sensitive data, make sure the file permissions
are very restrictive.

### Saving your password

If you don't want isbg to prompt you for your password each time,
you can specify the `--savepw` option. This will save the password in a
file in your home directory. The file is named `$HOME/.cache/isbg/.isbg-XXXX`
where XXXX is a 16 byte identifier based on the IMAP host, username and port
number (the same as for the multiple accounts description above). You can
override the filename with `--passwdfilename`.

The password is obfuscated, so anyone just looking at the contents
won't be able to see what it is. However, if they study the code to isbg
then they will be able to figure out how to de-obfuscate it, and
recover the original password. (isbg needs the original password each
time it is run as well).

Consequently you should regard this as providing minimal protection if
someone can read the file.

### SSL

isbg can do IMAP over SSL if your version of Python has been
compiled with SSL support. Since Python 2.6, SSL comes built in with Python.

However you should be aware that the SSL support does NOT check the
certificate name nor validate the issuer. If an attacker can intercept
the connection and modify all the packets flowing by, then they will be
able to pose as the IMAP server. Other than that, the connection will
have the usual security features of SSL.

### Exit Codes

When ISBG exits, it uses the exit code to tell you what happened. In
 general it is zero if all went well, and non-zero if there was a
problem. You can turn on additional reporting by using the `--exitcodes`
command line option.

    ==== ============ ================================================
        `--exitcodes` 
    code     needed?  description
    ==== ============ ================================================
      0      no       All went well
      1     yes       There was at least one new message, and none of
                      them were spam
      2     yes       There was at least one new message, and all them
                      were spam
      3     yes       There were new messages, with at least one spam
                      and one non-spam
     10      no       There were errors in the command line arguments
     11      no       The IMAP server reported an error
     12      no       There was an error of communication between
                      spamc and spamd
     20      no       The program was not launched in an interactive
                      terminal
     30      no       There is another instance of `isbg` running
     -1      no       Other errors
    ==== ============ ===================================================
    
### Read and Seen flags

There are two flags IMAP uses to mark messages, `Recent` and `Seen`.
`Recent` is sent to the first IMAP client that connects after a new
message is received. Other clients or subsequent connections won't see
that flag. The `Seen` flag is used to mark a message as read. IMAP clients
explicitly set `Seen` when a message is being read.

Pine and some other mailers use the `Recent` flag to mark new mail.
Unfortunately this means that if isbg or any other IMAP client has even
looked at the Inbox, the messages won't be shown as new. It really
should be using `Seen`.

The IMAP specification does not permit clients to change the `Recent` flag.

### Gmail Integration

Gmail has a few unique ways that they interact with a mail client. isbg must
be considered to be a client due to interacting with the Gmail servers over
IMAP, and thus, should conform to these special requirements for propper
integration.

There are two types of deletion on a Gmail server.

**Type 1: Move a message to '[Gmail]/Trash' folder.**

This "removes all labels" from the message. It will no longer appear in any
folders and there will be a single copy located in the trash folder.
Gmail will "empty the trash" after the received email message is 30 days old.

You can also do a "Normal IMAP delete" on the message in the trash folder to
cause it to be removed permanently without waiting 30 days.

**Type 2: Normal IMAP delete flag applied to a message.**

This will "remove a single label" from a message. It will no longer appear
in the folder it was removed from but will remain in other folders and also
in the "All Mail" folder.

Enable Gmail integration mode by passing `--gmail` in conjunction with
`--delete` on the command line when invoking isbg. These are the features
which are tweaked:

- The `--delete` command line switch will be modified so that it will result in
  a Type 1 delete.

- The `--deletehigherthan` command line switch will be modified so that it will
  results in a Type 1 delete.

- If `--learnspambox` is used along with the `--learnthendestroy` option, then a
  Type 1 delete occurs leaving only a copy of the spam in the Trash.

- If `--learnhambox` is used along with the `--learnthendestroy` option, then a
  Type 2 delete occurs, only removing the single label.

Reference information was taken from
[here](https://support.google.com/mail/answer/78755?hl=en)

### Ignored emails

By default, isbg ignores emails that are bigger than 120000 bytes since spam
are not often that big. If you ever get emails with score of 0 on 5 (0.0/5.0),
 it is likely that SpamAssassin is skipping it due to size.

Defaut maximum size can be changed with the use of the `--maxsize` option.

### Partial runs

By default, isbg scans 50 emails for operation: spam learn, ham learn and 
spam detection. If you want to change the default, you can use the 
`--partialrun` option specifying the number. Isbg tries to read first the new 
messages and tracks the before seen to not reprocess them.

This is useful when your inbox has a lot of emails, since deletion and mail
tracking are only performed at the end of the run and full scans can take too
long.

If you want that isbg does track all the emails you can disable the 
`partialrun` with `--partialrun=0`.

## Contact and about

Please join our [developpement mailing list](
https://mail.python.org/mm3/mailman3/lists/isbg.python.org/)
if you use ISBG or contribute to it! The mailing list will be used to announce
project news and to discuss the further developpement of ISBG.

You can also hang out with us on IRC, at `#isbg` on Freenode.

This software was written by Roger Binns
<[rogerb@rogerbinns.com](mailto:rogerb@rogerbinns.com)>
and is maintained by Thomas Lecavelier
<[thomas@lecavelier.name](mailto:thomas@lecavelier.name)>
since november 2009 with the great help of Anders Jenbo since v0.99,
and maintained by Carles Muñoz Gorriz <[carlesmu@internautas.org](
mailto:carlesmu@internautas.org)> since march 2018.

## License

This program is licensed under the [GNU General Public License version 3](
https://www.gnu.org/licenses/gpl-3.0.txt).
