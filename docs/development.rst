Development
===========

**isbg** uses `github flow`_ and, from v2.1.0 we use `git-hub`_ to deal
with pulls and issues.

.. _github flow: https://guides.github.com/introduction/flow/
.. _git-hub: https://github.com/sociomantic/git-hub


Development schema
------------------
We should work in a ``feature/*`` branch or ``bugfix/*`` branch and it
should be attached to an **issue**. We can use ``git hub issue`` to do
it, e.g.:

    $ git hub issue new --assign USER   # It creates the issue number 2
    $ git branch feature/DESCRIPTION    # Creates branch
    $ git checkout feature/DESCRIPTION  # Move to the new branch
    $                                   # Do changes in the branch
    $ git commit                        # Commit the changes
    $ git hub


Versioning schema
-----------------
We tag the new releases as:

  ``{major_release_number}.{minor_release_number}.{patch_release_number}``

The current version number of **isbg** is stored in ``isbg/isbg.py``
