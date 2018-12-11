Distinct by multiple columns
==================================================

R::

  mtcars %>% distinct(mpg, am)

This drops all other columns. Pass .keep_all=T to distinct to keep them.

pandas::

  mtcars[~mtcars[['mpg','am']].duplicated()]


plydata::

 mtcars >> dp.distinct(['mpg', 'am'], 'first')

Must specify keep

dpylthon::

  dp.DplyFrame(mtcars) >> dp.sift(~X[['mpg', 'am']].duplicated())


dfply::

  mtcars >> dp.filter_by(~X[['mpg', 'am']].duplicated())


dppd::

  dp(mtcars).filter_by(~X[['mpg', 'am']].duplicated()).pd

