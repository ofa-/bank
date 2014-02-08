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
in turn exposed using a python-based web-server.

Bank operations are presented in a synthetic month x categories table,
with monthly and yearly totals, monthly per-category totals, and details
shown on hover.  Detailed sub-categories table view is also available.

Bank operations can be edited (description), categorized, and split
into multiple lines using the GUI.  Other modifications e.g. changing
dates, deleting, or merging lines require manual editing of text files.


Configuration
-------------

Configuration of accounts names, operations categories, auto-categorization
and cleanup sed script is done editing text files in directory ``./etc/``.

Configuration of online bank account credentials is done using boobank
or editing boobank config files in directory ``~/.config/weboob/backends``.

Configuration of current account balance is done editing account data file
in directory ``./server/``.
