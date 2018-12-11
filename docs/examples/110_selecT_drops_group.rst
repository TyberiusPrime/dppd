select dropping a grouping variable - what happens?
============================================================ 

dplython::
  (dp.DplyFrame(mtcars) >> dp.group_by(X.cyl, X.am) >> dp.select(X.hp)).columns
  -> ['cyl', 'am', 'hp'], grouping retained
  # there is no drop?


dfply::
  (mtcars >> dp.group_by('cyl','am') >> dp.select('hp')).columns
  -> ['hp'], grouping is lost select
  (mtcars >> dp.group_by('cyl','am') >> dp.select('cyl','am', 'hp')).columns
  -> ['cyl', 'am', 'hp'], grouping is retained!

  (mtcars >> dp.group_by('cyl','am') >> dp.drop('cyl')).columns
  -> all but ['cyl'], grouping is lost on drop

  (mtcars >> dp.group_by('cyl','am') >> dp.drop('hp')).columns
  -> all but ['cyl'], grouping is retained!

It is dependend on the actual columns being kept/dropped
whether grouping is retained.


dppd::
  dp(mtcars).groupby(['cyl','am']).select('hp').pd.columns
  -> [cyl, am, hp], groups still intact

  dp(mtcars).groupby(['cyl','am']).drop('am').pd.columns
  -> all columns, groups still intact

  dp(mtcars).groupby(['cyl','am']).loc[:,'am'].pd.columns
  -> [am], grouping dropped

Verbs/pandas methods implicitly add grouping columns, accesors
drop them.


