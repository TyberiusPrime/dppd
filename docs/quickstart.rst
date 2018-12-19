Quickstart
==========


Style 1: Context managers
-------------------------


.. highlight:: python

::

  >>> import pandas as pd
  >>> from dppd import dppd
  >>> from plotnine.data import mtcars
  >>> with dppd(mtcars) as (dp, X):  # note parentheses!
  ...   dp.select(['name', 'hp', 'cyl'])
  ...   dp.filter_by(X.hp > 100).head(1)

  >>> print(X.head())
	  name   hp  cyl
  0  Mazda RX4  110    6
  >>> print(isinstance(X, pd.DataFrame))
  True
  >>> type(X)
  <class 'dppd.base.DPPDAwareProxy'>
  >>> print(len(X))
  1
  >>>m2 = X.pd
  >>>type(m2)
  <class 'pandas.core.frame.DataFrame'>


Within the context manager, dp is always the latest Dppd object and X is always the latest
intermediate DataFrame.  Once the context manager has ended, both variables (dp and
X here) point to a proxy of the final DataFrame object.

That proxy should, thanks to `wrapt <https://wrapt.readthedocs.io/en/latest/>`_ , behave
just like DataFrames, except that they have a property '.pd' that returns the real
DataFrame object.



Style 2: dp.....pd 
------------------

::

  >>>import pandas as pd
  >>>from dppd import dppd
  >>>from plotnine.data import mtcars
  >>>dp, X = dppd()

  >>> mt2 = (dp(mtcars)
    .select(['name', 'hp', 'cyl'])
    .filter_by(X.hp > 100)
    .head()
    .pd
  )
  >>> print(mt2.head())
		  name   hp  cyl
  0          Mazda RX4  110    6
  1      Mazda RX4 Wag  110    6
  3     Hornet 4 Drive  110    6
  4  Hornet Sportabout  175    8
  5            Valiant  105    6
  >>> print(type(mt2))
  <class 'pandas.core.frame.DataFrame'>


The inline-style is more casual, but requires the final call .pd
to retrieve the DataFrame object, otherwise you have a :class:`dppd.Dppd`.



How does it work
----------------
dppd follows the old adage that there's only one problem not solvable
by another layer of indirection, and achives it's pipeline-style method chaining
by having a proxy object X that always points to the latest DataFrame created in the
pipeline.

This allows for example the following:

::

  >>> with dppd(mtcars) as (dp, X):
  ...   high_kwh  = dp(mtcars).mutate(kwh = X.hp * 0.74).filter_by(X.kwh > 80).iloc[:2].pd
  ... 
  >>> high_kwh  
		  name   mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear  carb    kwh
  0          Mazda RX4  21.0    6  160.0  110  3.90  2.620  16.46   0   1     4     4   81.4
  1      Mazda RX4 Wag  21.0    6  160.0  110  3.90  2.875  17.02   0   1     4     4   81.4

.. note::

  Note that at this point ``(X == high_khw).all()`` and ``(dp == high_khw).all()``.

This approach is different to dplyr and other python implementations of the 
'grammar of data manipulation' - see `comparisons <comparisons.html>`_.

Dppd also contains a single-dispatch mechanism to avoid monkey patching.
See the section on `extending dppd <extending.html>`_


What's next?
------------
To learn more please refer to the sections on `Dpplyr verbs <verbs_dplyr.html>`_,
`dppd verbs <verbs_dppd.html>`_ and `grouping <grouping.html>`_.

