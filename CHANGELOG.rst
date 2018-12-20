=========
Changelog
=========

unreleased
- replaced alias_verb by extending register_verb(name=...) to register_verb(names=[...], ...)
- support for pandas 0.22.0 which apperantly had the DataFrameGroupBy at a slightly
  different location

Version 0.15
============
- X is now 'stacked' - dp(...).pd now replaces the X with the one just before the last dp(..) call.
    

Version 0.1
===========

- initial release
