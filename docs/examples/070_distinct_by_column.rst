Distinct by column
==================================================

R::

  mtcars %>% distinct(mpg)

This drops all other columns. Pass .keep_all=T to distinct to keep them.

pandas::

  mtcars[~mtcars.mpg.duplicated()]


plydata::

 mtcars >> dp.distinct('mpg', 'first')

Must specify keep

dpylthon::

  dp.DplyFrame(mtcars) >> dp.sift(~X.mpg.duplicated())


dfply::

  mtcars >> dp.filter_by(~X.mpg.duplicated())


dppd::

  dp(mtcars).filter_by(~X.mpg.duplicated()).pd


