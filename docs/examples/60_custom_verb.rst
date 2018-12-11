Writing your own non-parametrized 'verb'
==================================================

R::

  rc = function(df) ( df[rev(colnames(df)])
  mtcars %>% rc()

Any function taking a df as first parameter is a verb.

The python example is slightly more 'practical' in that it's
not an entirely trivial function.

prelude::

  def ints_to_floats(df):
    return df.assign(**{x[0]: x[1] for x in df.select_dtypes(int).astype(float).items()})


pandas::
  ints_to_floats(mtcars)


plydata::

  no documentation on custom verbs

dplython::

  @dp.ApplyToDataframe
  def ints_to_floats():
    return lambda df: df.assign(**{x[0]: x[1] for x in df.select_dtypes(int).astype(float).items()})

  dp.DplyFrame(mtcars) >> ints_to_floats()

Undocumented. Note that custom verbs (and many dplython verbs, but not all of them) need
to start with a dp.DplyFrame object, not a pd.DataFrame. Mutate is one exception

dfply::

  @dp.dfpipe
  def ints_to_floats(df):
    return df.assign(**{x[0]: x[1] for x in df.select_dtypes(int).astype(float).items()})
  mtcars >> ints_to_floats()

dfpipe decorator is well documented

dppd::

  #one more import
  from dppd register_verb
  dp, X = dppd()()

  @register_verb()
  def ints_to_floats(df):
    return df.assign(**{x[0]: x[1] for x in df.select_dtypes(int).astype(float).items()})
  dp(mtcars).ints_to_floats().pd
  



