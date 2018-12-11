Filter column by list of accepted values
--------------------------------------------------

Example cut down mtcars to two named cars.

.. highlight:: R

R::

  mtcars = as.tibble(mtcars)
  mtcars = rownames_to_column(mtcars)
  mtcars %>% filter(rowname %in% c("Fiat 128", "Lotus Europa"))


.. highlight:: python

pandas::

  mtcars[mtcars.name.isin(["Fiat 128", "Lotus Europa"]]


plydata::

  mtcars >> dp.query('name.isin(["Fiat 128", "Lotus Europa"])')


dplython::

  dp.DplyFrame(mtcars) >> dp.arrange(X.cyl) >> dp.sift(X.name.isin(['Lotus Europa', 'Fiat 128']))


dfply::

  mtcars >> dp.arrange(X.cyl) >>dp.filter_by(X.name.isin(['Lotus Europa', 'Fiat 128']))


pandas_ply::

  mtcars.ply_where(X.name.isin(['Lotus Europa', 'Fiat 128']))

dppd::

  dp(mtcars).arrange('cyl').filter_by(X.name.isin(['Lotus Europa', 'Fiat 128'])).pd


