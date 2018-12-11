Select rows by iloc
==================================================

R::

  mtcars %>% slice(6:10)


pandas::

 mtcars.iloc[5:10]

plydata::

 (mtcars >>dp.call('.iloc'))[5:10]

plydata's call allows easy, if verbose fallbock on the DataFrames methods

dpylython::

 dp.DplyFrame(mtcars) >> X._.iloc[5:10]

dplython offers the original DataFrame's method via a '._' forward.

dfply::

  mtcars >> dp.row_slice(np.arange(5,10))

row_slice does not support the full iloc[] interface, but only single ints or lists of such.

dppd::

  dp(mtcars).iloc[5:10].pd()


