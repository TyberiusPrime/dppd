Filter by substring
==================================================

R::

  mtcars %>% filter(grepl('RX', rowname))

Actually a regexps-match.

pandas::
  mtcars[mtcars.name.str.contains('RX')]


plydata::

  mtcars >> dp.query("name.str.contains('RX')")


dplython::

  dp.DplyFrame(mtcars) >> dp.sift(X.name.str.contains('RX'))


dfply::

  mtcars >>dp.filter_by(X.name.str.contains('RX'))


dppd::

  dp(mtcars).filter_by(X.name.str.contains('RX')).pd
