The why of dppd
=======================================

Undoubtly, in R dplyr is a highly useful library
since many of it's verbs are not available otherwise.

But pandas, which has been moving to support `method chaining <https://tomaugspurger.github.io/method-chaining.html>`_
in the last few releases
already does most of dplyr's verbs, so why is there half a dozen 
dplyr clones for python, including this one (see <comparison>)?

Part of it is likely to be historic - the clone projects started before
pandas DataFrames were as chainable as they are today.

Another part is the power of R's non-standard-evaluation, which, if unpythonic, 
has a certain allure.

Dppd brings three things to pandas:
 * the proxy that always points to the latest DataFrame (or object), which 'fakes'
   non-standard-evaluation at the full power of python
 * filtering on groupby()ed DataFrames
 * R like column specifications for selection and sorting.


Proxy X
-------

X is always the latest object::

  >>> dp(mtcars).assign(kwh=X.hp * 0.74).filter_by(X.kwh > 100).head(5).pd
		  name   mpg  cyl   disp   hp  drat    wt   qsec  vs  am  gear  carb    kwh
  4   Hornet Sportabout  18.7    8  360.0  175  3.15  3.44  17.02   0   0     3     2  129.5
  6          Duster 360  14.3    8  360.0  245  3.21  3.57  15.84   0   0     3     4  181.3
  11         Merc 450SE  16.4    8  275.8  180  3.07  4.07  17.40   0   0     3     3  133.2
  12         Merc 450SL  17.3    8  275.8  180  3.07  3.73  17.60   0   0     3     3  133.2
  13        Merc 450SLC  15.2    8  275.8  180  3.07  3.78  18.00   0   0     3     3  133.2
  

Filtering groupbyed DataFrames
--------------------------------------------------

Let's take the example from our Readme, which calculates the highest cars by kwh
from the mtcars dataset (allowing for ties)::


   >>> from plotnine.data import mtcars
   >>> from dppd import dppd
   >>> dp, X = dppd()
  >>> (dp(mtcars)
  ...       .mutate(kwh = X.hp * 0.74)
  ...       .groupby('cyl')
  ...       .filter_by(X.kwh.rank() < 2)
  ...       .ungroup().pd
  ...       )
    
      cyl              name   mpg   disp   hp  drat     wt   qsec  vs  am  gear  carb     kwh
   5     6           Valiant  18.1  225.0  105  2.76  3.460  20.22   1   0     3     1   77.70
   18    4       Honda Civic  30.4   75.7   52  4.93  1.615  18.52   1   1     4     2   38.48
   21    8  Dodge Challenger  15.5  318.0  150  2.76  3.520  16.87   0   0     3     2  111.00
   22    8       AMC Javelin  15.2  304.0  150  3.15  3.435  17.30   0   0     3     2  111.00


And the pandas equivalent::

  >>> mtcars = mtcars.assign(kwh = mtcars['hp'] * 0.74)
  >>> ranks = mtcars.groupby('cyl').kwh.rank()
  >>> mtcars[ranks < 2]
		  name   mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear  carb     kwh
  5            Valiant  18.1    6  225.0  105  2.76  3.460  20.22   1   0     3     1   77.70
  18       Honda Civic  30.4    4   75.7   52  4.93  1.615  18.52   1   1     4     2   38.48
  21  Dodge Challenger  15.5    8  318.0  150  2.76  3.520  16.87   0   0     3     2  111.00
  22       AMC Javelin  15.2    8  304.0  150  3.15  3.435  17.30   0   0     3     2  111.00


Column specifications
----------------------

Selecting columns in pandas is alread powerful, using the df.columns.str.whatever
methods. It is verbose though, and sort_values with it's 'ascending' parameter
is way to many characters just to invert the sorting order on a column.

Dppd supports a mini language for column specifications - see
:func:`dppd.column_spec.parse_column_specification` for details::

  # drop column name
  >>> dp(mtcars).select('-name').head(1).pd  
      mpg  cyl   disp   hp  drat    wt   qsec  vs  am  gear  carb   kwh
  0  21.0    6  160.0  110   3.9  2.62  16.46   0   1     4     4  81.4

  # sort by hp inverted
  >>> dp(mtcars).arrange('-hp').head(2).select(['name','cyl','hp']).pd
	    name  cyl  hp
  18  Honda Civic    4  52
  7     Merc 240D    4  62



Single dispatch 'clean monkey patching' engine
------------------------------------------------


Dppd internally is in essence a clean monkey-patching single dispatch engine that 
allows you to wrap types beyond the DataFrame.e



