Advanced selecting
==================================================

R::

  mtcars %>% select(starts_with("c"))

starts_with only works within a dplyr construct

pandas::

  #by boolean vector
  mtcars.loc[:, mtcars.columns.str.startswith('c')]
  #by list comprehension
  mtcars[[x for x in mtcars.columns if x.startswith('c')]]
  #by regexps, using bool vector interface
  mtcars.loc[:, mtcars.columns.str.contains('^c')] # search in python re module
  #by regexps using list comprehension
  mtcars[[x for x in mtcars.columns if re.match('c', x)]]  # very universal


plydata::

  #by select parameter
  mtcars >> dp.select(startswith='c')
  # Note that dplyr used starts_with
  #by select parameter - regexps
  mtcars >> dp.select(matches="^c")

select(matches=...) is actuall re.match, ie. only searchs at the start
This differs from the dplyr behaviour (but is consistent with python
re module) and is less general.

dpylython::

  # bool vectors don't work. -> Exception: "None not in index"
  dp.DplyFrame(mtcars) >> dp.select(X.columns.str.startswith('c'))
  # list comprehensions never return.
  dp.DplyFrame(mtcars) >> dp.select([x for x in X.columns if x.startswith('c')])

In summary: not supported

dfply::

  # by select parameter
  mtcars >> dp.select(dp.starts_with('c'))
  # by select regexps
  mtcars >> dp.select(dp.matches('c')) # 'search' in python re module
  # by bool vector
  mtcars >> dp.select(X.columns.str.startswith('c'))
  # by bool vector gegexps
  mtcars >> dp.select(X.columns.str.contains('^c'))

Faithful reproduction of dplyr but also works with the pandas-way
dp.matches is actuall re.search - arguably the more useful variant,
since it can be tuned to perfaorm 're.match' using '^' at the start of the
regexps.

dppd::

  # by boolean vector
  dp(mtcars).select(X.columns.str.startswith('c')).pd
  # by list comprehension
  dp(mtcars).select([c for c in X.columns if c.startswith('c')]).pd
  # by function callback
  dp(mtcars).select(lambda c: c.startswith('c')).pd
  # by regexps
  dp(mtcars).select(('^c',)).pd

