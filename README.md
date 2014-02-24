OFA's Bank
==========

This project provides a simple banking application, featuring:

* simple web-based gui
* automatic online bank account data download (using bookank)
* semi-automatic operations categorization (using sed)
* simple text-based configuration (not web-based)


Web-GUI
-------

Web GUI provides buttons for downloading, viewing, searching and
editing bank accounts data.  Clicking the download button causes
online bank account data to be downloaded (using boobank),
processed for cleanup and categorization (using sed),
and stored locally on disk in simple text files, which are
in turn exposed using a (python based) web-server.

Bank operations are presented in a synthetic month x categories table,
with monthly and yearly totals, monthly per-category totals, and details
shown on hover.  Detailed sub-categories table view is also available.

Bank operations can be edited (description), categorized, and split
into multiple lines using the GUI.  Other modifications e.g. changing dates,
adding, deleting, or merging lines require manual editing of text files.


Configuration
-------------

Configuration of accounts names, operations categories, auto-categorization
and cleanup sed script is done editing text files in directory ``./etc/``.

Configuration of online bank account credentials is done using boobank
or editing boobank config files in directory ``~/.config/weboob/backends``.

Configuration of current account balance is done editing account data file
in directory ``./server/``.


Installation
------------

You can try out the application right away using the provided sample data
and configuration.  Make sure you have ``python`` installed, checkout the
project, copy sample files in place with ``tar c -C sample . | tar x``,
then run ``./bin/bank --start``.

To download online-bank accounts data you, will need ``boobank`` installed
and configured.  In addition, auto-categorization requires various basics
such as ``sed``, ``awk``, ``grep`` and ``bash``, all of which are probably
already installed in your distribution.

To install ``boobank``, try ``sudo apt-get install weboob``.  Be sure to
read the note below, and checkout http://weboob.org/applications/boobank

Enjoy.


Note: project ``boobank`` is still moving fast, and provides regular updates,
both internal and online-banks backends fixes.  While this takes care of the
woes of online-banks "improvements" for you, it can break your install.  You
may wish to git clone the project and setup a "User install" as recommended.
