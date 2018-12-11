Iterate over groups / build a new dataframe from dataframe of groups
======================================================================

R::

  dfnrow = function(df) (data.frame(count=nrow(df)))
  mtcars %>% group_by(cyl) %>%  do(dfnrow(.))


pandas::

  def something(grp):
      return pd.DataFrame({'count': [len(grp)]})
  pd.concat([something(group).assign(cyl=idx) for idx, group in mtcars.groupby('cyl')],axis=0)


pyldata::

  mtcars >> dp.group_by('cyl') >> dp.do(something)

No iterator over groups


dpylython::

  No do, no group iterator

dfply version 1::

  mtcars >> dp.group_by('cyl') >> dfply.dfpipe(something)()

Approach 1: turn something into a verb.


dfply version 2::

  @dfply.dfpipe
  def do(df, func, *args, **kwargs):
      return func(df, *args, **kwargs)
  mtcars >> dp.group_by('cyl') >> do(something)

Approach 2: introduce do verb.


dppd::

  dp(mtcars).groupby('cyl').do(something).pd

  or

  for idx, sub_df in dp(mtcars).groupby('cyl').itergroups():
    print(idx, something(sub_df))

dppd has a group iterator.


