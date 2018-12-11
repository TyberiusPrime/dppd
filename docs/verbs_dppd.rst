Dppd verbs
============

Pandas DataFrame methods
------------------------

Within a dp(), **all** :class:`pandas.DataFrame` methods and accessors work
as you'd expect them to [#f1]_.

Example::

  >>> dp(mtcars).rank().pd.head(5)  
    name   mpg   cyl  disp    hp  drat    wt  qsec    vs    am  gear  carb
  0  18.0  19.5  15.0  13.5  13.0  21.5   9.0   6.0   9.5  26.0  21.5  25.5
  1  19.0  19.5  15.0  13.5  13.0  21.5  12.0  10.5   9.5  26.0  21.5  25.5
  2   5.0  24.5   6.0   6.0   7.0  20.0   7.0  23.0  25.5  26.0  21.5   4.0
  3  13.0  21.5  15.0  18.0  13.0   8.5  16.0  26.0  25.5  10.0   8.0   4.0
  4  14.0  15.0  25.5  27.5  21.0  10.5  19.0  10.5   9.5  10.0   8.0  12.5

You can even continue working with Series within the dp and convert them back to
a DataFrame later on::


  >>> dp(mtcars).set_index('name').sum().loc[X > 15].to_frame().pd
	      0
  mpg    642.900
  cyl    198.000
  disp  7383.100
  hp    4694.000
  drat   115.090
  wt     102.952
  qsec   571.160
  gear   118.000
  carb    90.000
    


concat
-------

:func:`concat <dppd.single_verbs.concat>` combines this DataFrame and another one.

Example::
  
  >>> len(mtcars)
  32
  >>> len(dp(mtcars).concat(mtcars).pd)
  64


unselect
---------
:func:`unselect <dppd.single_verbs.unselect>` drops by :func:`column specification <dppd.single_verbs.parse_column_specification>` [#f2]_.

Example:

  >>> dp(mtcars).unselect(lambda x: len(x) <= 3).pd.head(1)
	  name   disp  drat   qsec  gear  carb
  0  Mazda RX4  160.0   3.9  16.46     4     4
  



distinct
--------
:func:`distinct <dppd.single_verbs.distinct_dataframe>` selects unique rows, possibly
only considering a :func:`column specification <dppd.single_verbs.parse_column_specification>`.


Example::

  >>> dp(mtcars).distinct('cyl').pd
		  name   mpg  cyl   disp   hp  drat    wt   qsec  vs  am  gear  carb
  0          Mazda RX4  21.0    6  160.0  110  3.90  2.62  16.46   0   1     4     4
  2         Datsun 710  22.8    4  108.0   93  3.85  2.32  18.61   1   1     4     1
  4  Hornet Sportabout  18.7    8  360.0  175  3.15  3.44  17.02   0   0     3     2



transassign
-----------
:func:`transassign <dppd.single_verbs.transassign>` creates a new DataFrame based on
this one.

Example::

  >>> dp(mtcars).head(5).set_index('name').transassign(kwh = X.hp * 0.74).pd
			kwh
  name                     
  Mazda RX4           81.40
  Mazda RX4 Wag       81.40
  Datsun 710          68.82
  Hornet 4 Drive      81.40
  Hornet Sportabout  129.50



add_count
----------
:func:`add_count <dppd.single_verbs.add_count_DataFrame>` adds the group count to each row.

This is a good example verb to get started on writting own.

Example::

  >>> dp(mtcars).groupby('cyl').add_count().ungroup().sort_index().head(5).select(['name','cyl','count']).pd
		  name  cyl  count
  0          Mazda RX4    6      7
  1      Mazda RX4 Wag    6      7
  2         Datsun 710    4     11
  3     Hornet 4 Drive    6      7
  4  Hornet Sportabout    8     14



as_type
--------
:func:`as_type <dppd.single_verbs.as_type_DataFrame>` quickly converts the type of columns by
a column_specification.

Example:

  >>> dp(mtcars).astype(['-qsec', '-name'], int).pd.head()
		  name  mpg  cyl  disp   hp  drat  wt   qsec  vs  am  gear  carb
  0          Mazda RX4   21    6   160  110     3   2  16.46   0   1     4     4
  1      Mazda RX4 Wag   21    6   160  110     3   2  17.02   0   1     4     4
  2         Datsun 710   22    4   108   93     3   2  18.61   1   1     4     1
  3     Hornet 4 Drive   21    6   258  110     3   3  19.44   1   0     3     1
  4  Hornet Sportabout   18    8   360  175     3   3  17.02   0   0     3     2






.. [#f1] Except for the deprecated :meth:`pandas.DataFrame.select`, which is shadowed
         by our verb :meth:`select <dppd.single_verbs.select>`.

.. [#f2] 'drop' is already a pandas method name - :meth:`pandas.DataFrame.drop`
