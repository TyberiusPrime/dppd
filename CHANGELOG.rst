=========
Changelog
=========


unreleased
- a column spec of None now means 'all columns' (useful for e.g. distinct)
- added categorize verb for DataFrames

0.16
- replaced alias_verb by extending register_verb(name=...) to register_verb(names=[...], ...)
- support for pandas 0.22.0 

Version 0.15
============
- X is now 'stacked' - dp(...).pd now replaces the X with the one just before the last dp(..) call.
    

Version 0.1
===========

- initial release
