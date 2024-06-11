=========
Changelog
=========


unreleased
==========

0.27
====

fixed norm_0_to_1()

0.26
====
- added .dir_dppd() to list just dppd registered verb, not those wrapping the object itself.
- dp(DataFrame).insert() now returns self and is therefore chainable.

0.25
====

- added .debug to print head&tail inline

0.24
===== 
- allow dp(collections.Counter).to_frame(key_name='x', count_name='y').pd

0.23 
====

- pca() on dataframe
- 'natsorted' for categoricals
- select_and_rename (select no longer renames!)
- level selection in column specifications
  (by passing in a list of regexps, might be shorter than the number of levels)

0.22
=====
- added binarize
- added dp({}).to_frame()
- minor bugfixes and polishing
- improved docs a bit

0.21
=====
- Fleshed out reset_columns

0.20
====
- added rename_columns/reset_columns

0.19
==========

- support for itertuples on groupBy objects
- column specs now support types (and forward the query to select_dtypes)
- column spec now accepts [True] as 'same columns, but sorted alphabetically'
- ends() for DataFrames
- categorize now by default keeps order as seen in the Series. Pass None to restore old
  behaviour


0.17
==========

=======
- a column spec of None now means 'all columns' (useful for e.g. distinct)
- added categorize verb for DataFrames

0.16
=======
- replaced alias_verb by extending register_verb(name=...) to register_verb(names=[...], ...)
- support for pandas 0.22.0 

0.15
============
- X is now 'stacked' - dp(...).pd now replaces the X with the one just before the last dp(..) call.
    

0.1
===========

- initial release
