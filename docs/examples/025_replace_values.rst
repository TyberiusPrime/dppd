Replace values
==================================================

R::

  mtcars %>% mutate(cyl = replace(cyl, 4, 400))


pandas::

 mtcars.assign(cyl=mtcars.cyl.replace(4, 400))


plydata::

 mtcars >> dp.define(cyl='cyl.replace(4,400)') (mutate ok)


dpylython::

 dp.DplyFrame(mtcars) >> dp.mutate(cyl=X.cyl.replace(4, 400))


dfply::

 mtcars >>dp.mutate(cyl = X.cyl.replace(4, 400))


dppd::

  dp(mtcars).mutate(cyl = X.cyl.replace(4 ,400))

