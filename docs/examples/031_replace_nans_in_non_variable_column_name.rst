NaN and non python-variable column name
==================================================

Prelude::

  mtcars = mtcars.assign(**{'da cyl': mtcars.cyl})


R::

  mtcars = mtcars %>% mutate(`da cyl` = cyl)
  mtcars %>% filter(!is.nan(cyl))


pandas::

 mtcars[mtcars['da cyl'].isnull()]


plydata::

  query supports no Q ('variable escape function') (bug?)

dpylython::

 dp.DplyFrame(mtcars) >> dp.sift(~X['da cyl'].isnull())


dfply::

 mtcars >> dp.filter_by(~X['da cyl'].isnull())


dppd::

  dp(mtcars).filter_by(~X['da cyl'].isnull()).pd


