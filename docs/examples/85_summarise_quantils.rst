Summarize by quantiles
==================================================

We want to summarise displacement in each cylinder-range quantiles in 0.1 increments:

R::

  mtcars %>% group_by(cyl) %>% summarize(
    q0.1 = quantile(disp, probs=.1),
    q0.2 = quantile(disp, probs=.2),
    ...
  )


I'm certain you could make the summarize much smarter.


pandas::

  mtcars.sort_values('cyl').groupby('cyl')['disp'].aggregate({"q%.2f" % q: lambda x,q=q:
    x.quantile(q) for q in np.arange(0,1.1,0.1)})

This is sensitive to function-variable binding issue (only happens on initial define, except
for default variables (common bug to forget),
and using a dict for the aggregation is deprecated.


pandas version 2::

  lambdas = [lambda x,q=q: x.quantile(q) for q in np.arange(0,1.1,0.1)]
  for l, q in zip(lambdas, np.arange(0,1.1,0.1)):
    l.__name__ = "q%.2f" % q
  mtcars.sort_values('cyl').groupby('cyl')['disp'].aggregate(lambdas)

Using named functions - not quick, but cleaner

plydata::

  (mtcars 
  >> dp.arrange('cyl') 
  >> dp.group_by("cyl") 
  >> dp.summarize(**{"q%.2f" % f: "disp.quantile(%.2f)" % f for f in np.arange(0,1.1,0.1)})
  )


dplython::

  (dp.DplyFrame(mtcars) 
  >> dp.arrange(X.cyl) 
  >> dp.group_by(X.cyl) 
  >> dp.summarize(**{'q%.2f' % q: X.disp.quantile(q) for q in np.arange(0,1.1,0.1)})
  )


dfply::

  (mtcars 
  >>dp.arrange("cyl") 
  >> dp.group_by('cyl') 
  >> dp.summarise(**{"q%.2f" % f: X.disp.quantile(f) for f in np.arange(0,1.1,0.1)})
  )


dppd::

  dp(mtcars).sort_values('cyl').groupby('cyl').summarise(*[
    ('disp', lambda x,q=q: x.quantile(q), 'q%.2f' % q) for q in np.arange(0,1.1,0.1)
  ]).pd


