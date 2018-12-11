10: if_else column assignment
=============================================

This is one where there are multiple good ways to do it.

R::
  
  TODO

pandas::

  mtcars.assign(high_powered = (mtcars.hp > 100).replace({True: 'yes', False: 'no'}))

  mtcars.assign(high_powered = np.where(mtcars.hp > 100, 'yes', 'no'))


plydata::

 mtcars >> dp.define(high_powered = dp.if_else('hp > 100', '"yes"','"no"'))

 mtcars >> dp.define(high_powered = "(hp > 100).replace({True: 'yes', False: 'no'})")

 mtcars >> dp.define(high_powered = "np.where(hp > 100, 'yes', 'no')")


dpylython::

 dp.DplyFrame(mtcars) >> dp.mutate(high_powered=(X.hp > 100).replace({True: 'yes', False: 'no'}))

No support for np.where (out of the box)

dfply::

  mtcars >> dp.mutate(high_powered=(X.hp > 100).replace({True: 'yes', False: 'no'}))
  mtcars >> dp.mutate(high_powered=dp.make_symbolic(np.where)(X.hp > 100, 'yes','no'))

np_where has to be wrapped in make_symbolic


dppd::

  dp(mtcars).mutate(high_powered = (X.hp > 100).replace({True: 'yes', False: 'no'})).pd

  dp(mtcars).mutate(high_powered=np.where(X.hp > 100, 'yes','no')).pd


