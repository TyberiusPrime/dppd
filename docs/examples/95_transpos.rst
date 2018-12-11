transpose
==================================================

R::

  mtcars %>% t() %>% as.tibble

Base R function t()'s result must be converted back into a tibble


pandas::

  mtcars.transpose()


plydata::

  mtcars >> dp.call('transpose')


dpylython::
  dp.DplyFrame(mtcars) >> X._.transpose()

It is undocumented when and when not you can use `mtcars >>` and when
you have to use DplyFrame

dfply::

  @dp.dfpipe
  def call(df, method, *args, **kwargs):
    return getattr(df, method)(*args, **kwargs)
  mtcars >> call('transpose')

dfply has no fall back to pandas methods - this introduces such a fallback instead of
wrapping transpose.

dfpyl version 2::

  mtcars >> dp.dfpipe(pd.DataFrame.transpose)

We could also wrap the classes method in a pipe instead

dppd::

  dp(mtcars).transpose().pd


