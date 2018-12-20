Extending dppd
==============

Known extensions
-----------------
  * `dppd_plotnine <https://github.com/TyberiusPrime/dppd_plotnine>`_ allows plotting
    with plotnine, the python ggplot implementation.


Custom verbs
------------

Writing your own verbs can be as easy as sticking 
``@register_verb()`` on a function.

Example::

  >>>from dppd import register_verb
  >>> @register_verb()
  ... def sideways_head(df, n=5):
  ...   return df.iloc[:, :n]
  ... 
  >>> dp(mtcars).sideways_head(2).pd.head()
		  name   mpg
  0          Mazda RX4  21.0
  1      Mazda RX4 Wag  21.0
  2         Datsun 710  22.8
  3     Hornet 4 Drive  21.4
  4  Hornet Sportabout  18.7


A verb registered without passing a types argument to :class:`dppd.base.register_verb`
is registered for all types. ``sideways_head`` does raise an Exception on
DataFrameGroupBy objects though, since those don't support iloc.

Let's register a verb specifically for those::

  >>> @register_verb('sideways_head', types=pd.core.groupby.groupby.DataFrameGroupBy)
  ... def sideways_head_DataFrameGroupBy(grp, n=5):
  ...   return grp.apply(lambda X: X.iloc[:,: n])
  ... 
  >>> dp(mtcars).groupby('cyl').sideways_head(5).pd.head()
		  name   mpg  cyl   disp   hp
  0          Mazda RX4  21.0    6  160.0  110
  1      Mazda RX4 Wag  21.0    6  160.0  110
  2         Datsun 710  22.8    4  108.0   93
  3     Hornet 4 Drive  21.4    6  258.0  110
  4  Hornet Sportabout  18.7    8  360.0  175




Extending to other types
--------------------------

Dppd() objects dispatch their verbs on the type of their wrapped object.
register_verbs accepts a types argument which can be a single type or a list of types.
register_type_methods_as_verbs registers all  methods of a type (minus an exclusion list) as verbs for that type.

This allows you to define verbs on arbritrary types.


Just for kicks, because update on dict should always have returned the original dict::

  >>> register_type_methods_as_verbs(dict, ['update'])
  >>> @register_verb('update', types=dict)
  ... def update_dict(d, other):
    ... res = d.copy()
    ... res.update(other)
    ... return res

  >>> @register_verb('map', types=dict)
  ... def map_dict(d, callback):
  ...  return {k: callback(d[k]) for k in d}

  >>> print(dp({'hello': 'world'}).update({'no': 'regrets'}).map(str.upper).pd)
  {'hello': 'WORLD', 'no': 'REGRETS'}
  






