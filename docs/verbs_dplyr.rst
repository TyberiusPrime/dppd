Dplyr verbs
============

All dplyr verbs stay 'in pipeline' - you can chain them 
together on a :class:Dppd.


Mutate
------

Adds new columns.

mutate() takes keyword arguments that are turned into
columns on the DataFrame.

Excluding `grouping <grouping.html>`_, this is a straigt forward
wrapper around :meth:`pandas.DataFrame.assign`.

Example::
  
  >> dp(mtcars).mutate(lower_case_name = X.name.str.lower()).head(1).pd
          name   mpg  cyl   disp   hp  drat    wt   qsec  vs  am  gear  carb lower_case_name
  0  Mazda RX4  21.0    6  160.0  110   3.9  2.62  16.46   0   1     4     4       mazda rx4


Select
------

Pick columns, with optional rename.

Example::

  >>>dp(mtcars).select('name').head(1).pd
	  name
  0  Mazda RX4

  >>> dp(mtcars).select([X.name, 'hp']).columns.pd
  Index(['name', 'hp'], dtype='object')

  >>> dp(mtcars).select(X.columns.str.startswith('c')).columns.pd
  Index(['cyl', 'carb'], dtype='object')
  

  >>> dp(mtcars).select(['-hp','-cyl','-am']).columns.pd
  Index(['name', 'mpg', 'disp', 'drat', 'wt', 'qsec', 'vs', 'gear', 'carb'], dtype='object')

  #renaming
  >>> dp(mtcars).select({'model': "name"}).columns.pd
  Index(['model'], dtype='object')

See :func:`select <dppd.single_verbs.select>` and :func:`column_specification
<dppd.single_verbs.parse_column_specification>` for full details.

.. note::

  This verb shadows :meth:`pandas.DataFrame.select`, which is deprecated.


filter_by
----------

Filter a DataFrame's rows.

Examples::

  # by a comparison / boolean vector
  >>> dp(mtcars).filter_by(X.hp > 100).head(2).pd
	      name   mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear  carb
  0      Mazda RX4  21.0    6  160.0  110   3.9  2.620  16.46   0   1     4     4
  1  Mazda RX4 Wag  21.0    6  160.0  110   3.9  2.875  17.02   0   1     4     4

  # by an existing columns
  >>> dp(mtcars).filter_by(X.am).head(2).pd
	      name   mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear  carb
  1  Mazda RX4 Wag  21.0    6  160.0  110   3.9  2.875  17.02   0   1     4     4
  1  Mazda RX4 Wag  21.0    6  160.0  110   3.9  2.875  17.02   0   1     4     4

  # by a callback
  >>> dp(mtcars).filter_by(lambda X: np.random.rand(len(X)) < 0.5).head(2).pd
	  name   mpg  cyl   disp   hp  drat    wt   qsec  vs  am  gear  carb
  6  Duster 360  14.3    8  360.0  245  3.21  3.57  15.84   0   0     3     4
  7   Merc 240D  24.4    4  146.7   62  3.69  3.19  20.00   1   0     4     2
  

See :func:`filter_by <dppd.single_verbs.filter_by>` for full details.

.. note::

  This function is not called filter as not to shadow :meth:`pandas.DataFrame.filter`



arrange
-------

Sort a DataFrame by a :func:`column_specification
<dppd.single_verbs.parse_column_specification>`

>>> dp(mtcars).arrange([X.hp, X.qsec], ascending=[False, True]).select(['name','hp','qsec']).head(5).pd
                 name   hp   qsec
30      Maserati Bora  335  14.60
28     Ford Pantera L  264  14.50
23         Camaro Z28  245  15.41
6          Duster 360  245  15.84
16  Chrysler Imperial  230  17.42


summarize
---------

Summarize the columns in a DataFrame with callbacks.


Example:

  >>> dp(mtcars).summarize(
  ...     ('hp', np.min),
  ...     ('hp', np.max),
  ...     ('hp', np.mean),
  ...     ('hp', np.std),
  ...     ).pd
    hp_amin  hp_amax   hp_mean     hp_std
  0       52      335  146.6875  67.483071

  >>> dp(mtcars).summarize(
  ...   ('hp', np.min, 'min(hp)'),
  ...   ('hp', np.max, 'max(hp)'),
  ...   ('hp', np.mean, 'mean(hp)'),
  ...   ('hp', np.std, 'stddev(hp)'),
  ...   ).pd
    min(hp)  max(hp)  mean(hp)  stddev(hp)
  0       52      335  146.6875   67.483071


Summarize is most useful with `grouped DataFrames <grouping.html>`_.


do
---
Map a grouped DataFrame into a concated other DataFrame.
Easier shown than explained::

  >>> dp(mtcars).groupby('cyl').add_count().ungroup().sort_index().head(5).select(['name','cyl','count']).pd
		  name  cyl  count
  0          Mazda RX4    6      7
  1      Mazda RX4 Wag    6      7
  2         Datsun 710    4     11
  3     Hornet 4 Drive    6      7
  4  Hornet Sportabout    8     14





