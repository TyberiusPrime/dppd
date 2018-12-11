Select/Drop columns
==================================================
Select/Drop columns by name

.. highlight:: R

R::

  mtcars >> select(hp) # select only hp
  mtcars >> select(-hp) # drop hp

.. highlight:: python

pandas::

  mtcars[['hp', 'name',]] # select only hp and name
  mtcars.drop(['hp', 'name'], axis=1) # drop hp


plydata::

  mtcars >> dp.select('hp', 'name')
  mtcars >> dp.select('hp', 'name', drop=True)
  # no list passing


dplython::

  dp.DplyFrame(mtcars) >> dp.select(X.hp, X.name)


| Neither strings nor lists may be passed to select.
| No dropping of columns


dfply::

  mtcars >> dp.select('hp', 'name')
  mtcars >> dp.select(['hp', 'name'])
  mtcars >> dp.select(X.hp, X.name) # either works
  mtcars >> dp.select([X.hp, 'name']) even mixing
  mtcars >> dp.drop('hp')
  mtcars >> dp.drop(X.hp)


dppd::

  dp(mtcars).select(['hp', 'name']).pd # must be a list
  dp(mtcars).unselect(['hp']).pd # we like symetry
  dp(mtcars).drop('hp', axis=1).pd # fallback to pandas method



