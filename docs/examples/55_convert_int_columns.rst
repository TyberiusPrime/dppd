convert all int columns to float:
==================================================

pandas::

  mtcars.assign(**{x[0]: x[1] for x in mtcars.select_dtypes(int).astype(float).items()})


plydata::

  mtcars >> dp.mutate(*[(x[0], list(x[1])) for x in mtcars.select_dtypes(int).astype(float).items()])

The conversion to a list is necessary (bug?)

dplython::

  mtcars >> dp.mutate(**{x[0]: x[1] for x in mtcars.select_dtypes(int).astype(float).items()})


dfply::

  mtcars >> dp.mutate(**{x[0]: x[1] for x in mtcars.select_dtypes(int).astype(float).items()})


dppd::

  dp(mtcars).mutate(**{x[0]: x[1] for x in mtcars.select_dtypes(int).astype(float).items()}).pd

