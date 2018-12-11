TidyR verbs
=============


Dppd also supports tidyr verbs where they are 
'easier' to use than the pandas equivalents



gather
------
:func:`pandas.melt` with :func:`column specifications <dppd.single_verbs.parse_column_specification
See :func:`gather <dppd.single_verbs.gather>`


spread
------
:func:`spread <dppd.single_verbs.spread>` spreads a key/value column pair into it's components.
Inverse of :func:`gather <dppd.single_verbs.gather>`



unite
------
:func:`unite <dppd.single_verbs.unite>` joins the values of each row as strings


seperate
---------
:func:`seperate <dppd.single_verbs.seperate>` splits strings on a seperator


