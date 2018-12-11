Drop NaNs 
==========

R::
  TODO

pandas::

 mtcars[~pd.isnull(mtcars.cyl)]


pandas::

 mtcars.dropna(subset=['cyl'])


plydata::

  mtcars >> dp.call('.dropna', subset=['cyl'])


dpylython::

 dp.DplyFrame(mtcars) >> dp.sift(~X.cyl.isnull())


dfply::

 mtcars >>dp.filter_by(~X.cyl.isnull())  

but beware the `inversion bug <https://github.com/kieferk/dfply/issues/60>`_


dppd::

  dp(mtcars).filter_by(~X.cyl.isnull()).pd
  or
  dp(mtcars).dropna(subset=['cyl']).pd


