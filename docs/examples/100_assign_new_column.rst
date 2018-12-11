assign a column transformed by a function (vectorised)
=======================================================

R::

  stringlength = function(x) {nchar(x)} # trivial example
  mtcars %>% mutate(x = stringlength(rowname))


pandas::

  def stringlength(series):
    return series.astype(str).str.len()
  mtcars.assign(x = stringlength(mtcars['name']))


dpython:
  
  TODO

dply::

  mtcars >> dp.mutate(x = dp.make_symbolic(stringlength)(X.name))


dppd::

  dp(mtcars).mutate(x = stringlength(X.name)).pd



