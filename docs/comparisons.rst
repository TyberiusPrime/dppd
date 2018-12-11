Comparison of dplyr and various python approaches
##################################################

There have been various attempts to bring dplyr's ease of use to pandas DataFrames.
This document attempts a 'Rosetta stone' style translation and some characterization
about the individual libraries.

Please note that I'm not overly familar with each of these libraries,
pull requests to improve the 'translations' are welcome.


Libraries compared
====================
 - `dplyr <https://dplyr.tidyverse.org>`_

   - the R based original by the famous `Hadley Wickham <http://twitter.com/hadleywickham>`_.
   - based on 'pipeing_' with the %>% operator (see pipeing_)
   - could be used from python with rpy2


 - `pandas <https://pandas.pydata.org>`_
   the referenc Python DataFrame implementation could benefit from a chainable API

 - `plydata <plydata.readthedocs.io/en/stable/api.html>`_

   - pipeing_
   - evaluates strings as python code for non-standard-evaluation_
   - code suggest it could be extended to non-DataFrame objects


 - `dplython <https://pythonhosted.org/dplython/>`_

   - pipeing_
   - custom DataFrame class
   - magic X for non-standard-evaluation_


 - `dfply <https://github.com/kieferk/dfply>`_

   - pipeing_
   - magic X for non-standard-evaluation_
   - perhaps the most comprehensive python implementation (before dppd).
   - active development as of Dec. 2018
   - easy definition of new verbs


 - `pandas_ply <https://github.com/coursera/pandas-ply>`_

   - fluent API (method chaining) instead of pipeing_
   - magic X for non-standard-evaluation_
   - monkey-patches pd.DataFrame with exactly two methods: ply_select and ply_where.


 - `dpyr <https://github.com/cpcloud/dpyr>`_

   - no documentation
   - no examples
   - seems to introduce pipeing to `ibis <http://blog.ibis-project.org/design-composability/>`_


 - `dppd <https://github.com/TyberiusPrime/dppd>`_

   - fluent API (method chaining) instead of pipeing_
   - no non-standard-evaluation, based on proxy objects (a different magic X)
   - easy definition of new verbs




The magic of dpylr
==================
   
  
.. highlight:: R


.. _non-standard-evaluation:

  `Non standard evaluation <http://adv-r.had.co.nz/Computing-on-the-language.html>`_ 
  is R's killer feature that allows you to write statements that
  are evaluated 'later' in a different context, for example in that of your DataFrame.
  `mutate(df, new_column = old_column * 5)` for example creates a new dataframe with
  an additional column, which is set to `df$old_column * 5`.

  Python can approach it with its first-class-functions, but the lambda syntax remains
  cumbersome in comparison.


.. _pipeing:


  To understand how this piece of code works, you need to understand pipeing:

  It transforms an expression `df >> g >> f >> h` into the equivalent `h(f(g(df)))`

  This works around the limitation of R's object model, which always dispatches
  on functions and accordingly offers no method-chaining `fluent interfaces <https://en.wikipedia.org/wiki/Fluent_interface>`_.
  It combines beautifully with R's late-binding seemless `currying <https://en.wikipedia.org/wiki/Currying>`_.

  ::

    flights_sml %>% 
      group_by(year, month, day) %>%
      filter(rank(desc(arr_delay)) < 10)

  for example groups a DataFrame of flights by their date, orders a column (descending),
  turns it into a rank 1..n, and selects those from the original data frame that were in
  the top 10 (ie. worst delays) on each day.

  Dplyr is open in the sense that it's easy to extend both the set of verbs (trivialy by
  defining functions taking a dataframe and returning one) and the set of supported
  objects (for example to `database tables <https://dbplyr.tidyverse.org/articles/dbplyr.html>`_, less trivial).


A critique on the existing python dplyr clones (or why dppd)
============================================================

Most of the dplyr inspired Python libraries try very hard to reproduce the two core
aspects of dplyr, pipeing_ and non-standard-evaluation_. Pipeing is usually fairly well
implemented but reads unpythonic and is usually accompanied with namespace polution.
Non-standard-evaluation is harder to implement correctly, and every single
implementation so far serverly limits the expressiveness that Python offers (e.g. no list
comprehensions)

As an example, the following code is the dfply equivalent to the flight filtering R code above

.. highlight:: python

::

  from dfply import *
  ( flights_sml 
    >> group_by(X.year, X.month, X.day) 
    >> filter_by(
      make_symbolic(pd.Series.rank)(X.arr_delay, ascending=False) < 10)
  )

The big insight of dppd is that in many cases, this is not actually non-standard-evaluation 
that needs to be evaluted later, but simply a 'variable not available in context'
problem which can be solved with a proxy variable X that always points to the latest DataFrame
created. In the other cases, a fallback to functions/lambdas is not that bad / no more
ugly than having to wrap the function in a decorator.

Combined with a pythonic method-chaining fluent API, this looks like this

::

  from dppd import dppd
  dp, X = dppd()
  (
    dp(flights_sml)
    .filter_by(X.groupby(['year', 'month', 'day']).arr_delay.rank(ascending=False) < 10)
    .pd
  )


Examples
========

All datasets are provided either by ggplot2 (R) or plotnine.data (python)
For R, they've been converted to tibbles.

The python libraries are imported as dp (as opposed to `from x import *`),
with their magic variable also being imported.

dppd uses `from dppd import dppd; dp, X = dppd()`

So let's do some Rosetta-Stoning.

.. toctree::
  :maxdepth: 2
  :glob:
   

  examples/*
  


Summary:
========


## Summary notes:

  None of the X-marks-the-non-standard-evaluation is complete with regard to
  python's capabilitys - they already fail at such basic things as transform
  a function by a column.

  The 'eval a string' approach is better in this regard, but still fails
  for example on list comprehensions.




	all: could benefit from a 'delayed' row or valuewise callback function, both for columns
	and for rows. plydata (patsy?) might actually support list comprehensions!




plydata:

	 could benefit from loc/iloc ver
	 unclean exprots (dataframe)
	 no concat
	 query supports no Q
	 if_else is unecessary -> replace does the job
	 (case when ditto?)

dfply::
      missing loc verb
      unclean exports (warnings)
      the easy of dfpipe must not be underestimated

dpylython:
      unnecessary casting, results are not pd.DataFrame, (define rrshift on every method?)
      unclean exports (types)
      no concat
      select really rudimentary / does not take lists?
      unclear when you can do df >> and when you have to do Dplyframe(df)

