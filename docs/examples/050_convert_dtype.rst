convert a column's type
==================================================

pandas::

  mtcars.assign(hp = mtcars.hp.astype(float))


plydata::

  mtcars >> dp.define(hp = 'hp.astype(float)')


dpylython::

  mtcars >> dp.mutate(hp = X.hp.astype(float))


dfply::

  mtcars >> dp.mutate(hp = X.hp.astype(float))


dppd::

  dp(mtcars).mutate(hp = X.hp.astype(float)).pd

