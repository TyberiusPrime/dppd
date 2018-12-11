Summarize 2 columns
==================================================

R::

  mtcars %>% group_by(cyl) %>% summarize(disp_min = min(disp), hp_max = max(hp))


pandas::

  mtcars.groupby('cyl').agg({'disp': ['min'], 'hp': ['max']},)

This creates a multi index.

plydata::

  mtcars >> dp.arrange('cyl') >> dp.group_by("cyl") >> dp.summarize('min(disp)', 'max(hp)')

The seperate sorting is necessary, plydata does not sort by default in group_by!

dplython::

  dp.DplyFrame(mtcars) >> dp.group_by(X.cyl) >> dp.summarize(disp_min=X.disp.min(), hp_max = X.hp.max())


dfply::

  mtcars >> dp.group_by('cyl') >> dp.summarise(disp_min = X.disp.min(), hp_max=X.hp.max())


dppd::

  dp(mtcars).groupby('cyl').summarise((X.disp, np.min, 'disp_min'), (X.hp, np.max, 'hp_max')).pd


