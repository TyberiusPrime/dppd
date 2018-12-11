concat to dataframes on their row-axis
==================================================

R::

  mtcars %>% rbind(mtcars)

pandas::
  pd.concat([mtcars, mtcars])


plydata::

 ?

dpylython::

 ?


dfply::

  mtcars >> bind_rows(mtcars)


dppd::

  dp(mtcars).concat([mtcars]).pd


