Groups and summaries
=========================


Dppd's grouping is based on :meth:`pandas.DataFrame.groupby`,
which is supported in the fluent api::	

  >>>dp(mtcars).groupby('cyl').mean().filter_by(X.hp>100).select(['mpg', 'disp', 'hp']).pd 
	    mpg        disp          hp
  cyl                                   
  6    19.742857  183.314286  122.285714
  8    15.100000  353.100000  209.214286


Select, mutate and filter_by work on the underlying DataFrame::


  >>> dp(mtcars).groupby('cyl').select('name').head(1).pd
		  name  cyl
  0          Mazda RX4    6
  2         Datsun 710    4
  4  Hornet Sportabout    8

  # Note how selecting on a DataFrameGroupBy does always preserve the grouping columns 


During this mutate, X is the DataFrameGroupBy object, and the ranks are per group
accordingly::


  >>> dp(mtcars).groupby('cyl').mutate(hp_rank=X.hp.rank()).ungroup().select(['name', 'cyl', 'hp', 'hp_rank']).pd.head()
		  name  cyl   hp  hp_rank
  0          Mazda RX4    6  110      3.0
  1      Mazda RX4 Wag    6  110      3.0
  2         Datsun 710    4   93      7.0
  3     Hornet 4 Drive    6  110      3.0
  4  Hornet Sportabout    8  175      3.5


And the same in filter_by::


  >>> dp(mtcars).groupby('cyl').filter_by(X.hp.rank() <= 2).ungroup().select(['name', 'cyl', 'hp']).pd
		  name  cyl   hp
  5            Valiant    6  105
  7          Merc 240D    4   62
  18       Honda Civic    4   52
  21  Dodge Challenger    8  150
  22       AMC Javelin    8  150


Note that both mutate and filter_by play nice with the callables,
they're distributed by group - either directly, or via :meth:`pandas.DataFrameGroupBy.apply`::


  >>> a = dp(mtcars).groupby('cyl').mutate(str_count = lambda x: "%.2i" % len(x)).ungroup().pd
  >>> b = dp(mtcars).groupby('cyl').mutate(str_count = X.apply(lambda x: "%.2i" % len(x))).ungroup().pd
  >>> (a == b).all().all()
  True
  >>> a.head()
    cyl               name   mpg   disp   hp  drat     wt   qsec  vs  am  gear  carb str_count
  0    6          Mazda RX4  21.0  160.0  110  3.90  2.620  16.46   0   1     4     4        07
  1    6      Mazda RX4 Wag  21.0  160.0  110  3.90  2.875  17.02   0   1     4     4        07
  2    4         Datsun 710  22.8  108.0   93  3.85  2.320  18.61   1   1     4     1        11
  3    6     Hornet 4 Drive  21.4  258.0  110  3.08  3.215  19.44   1   0     3     1        07
  4    8  Hornet Sportabout  18.7  360.0  175  3.15  3.440  17.02   0   0     3     2        14





Summaries
---------

First off, you can summarize groupby objects with the usual pandas methods
:meth:`pandas.DataFrame.agg`, and stay in the pipe::

  >>> dp(mtcars).groupby('cyl').agg([np.mean, np.std]).select(['hp', 'gear']).pd
	      hp                 gear          
	    mean        std      mean       std
  cyl                                           
  4     82.636364  20.934530  4.090909  0.539360
  6    122.285714  24.260491  3.857143  0.690066
  8    209.214286  50.976886  3.285714  0.726273
  
  #note the interaction of select and the MultiIndex column names.

In addition, we have the :func:`summarize <dppd.single_verbs.summarize>` verb,
which any number of tuples (column_name, function) or (column_name, function,
new_name) as arguments::

  >>> (dp(mtcars).groupby('cyl').summarize(('hp', np.mean), ('hp', np.std), ('gear', np.mean), ('gear', np.std)).pd)
    cyl     hp_mean     hp_std  gear_mean  gear_std
  0    4   82.636364  19.960291   4.090909  0.514259
  1    6  122.285714  22.460850   3.857143  0.638877
  2    8  209.214286  49.122556   3.285714  0.699854

