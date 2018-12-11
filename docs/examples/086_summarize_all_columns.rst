summarize all columns by mean and std
==================================================

R::
  mtcars %>% summarize_all(funs(mean, sd)) # Non-numerical columns turn into NA + a warning
  mtcars %>% select_if(is.numeric) %>% summarize_all(funs(mean, sd)

plydata::

  mtcars >> dp.summarise_all((np.mean, np.std))  # exception due to the string column

  mtcars >> dp.call('select_dtypes',int) >>dp.summarise_all((np.mean, np.std))

  mtcars >> dp.summarize_if('is_numeric', (np.mean, np.std))


dpylthon::

  # won't return - no comprehensions with X.anything
  dp.DplyFrame(mtcars) >> dp.summarize(**{f"{x}_mean": X[x].mean() for x in X.columns})

  #have to use the datafram, and the merge-dicts syntax (python 3.5+)
  dp.DplyFrame(mtcars) >> dp.summarize(**{
    **{f"{x}_mean": X[x].mean() for x in mtcars.select_dtypes(int).columns},
    **{f"{x}_std": X[x].std() for x in mtcars.select_dtypes(int).columns}
    })


dfplyr::

  mtcars >> dp.summarize(**{
    **{f"{x}_mean": X[x].mean() for x in mtcars.select_dtypes(int).columns},
    **{f"{x}_std": X[x].std() for x in mtcars.select_dtypes(int).columns}
    })

can't select first, because I can't iterate over X.columns




dpdp::

  dp(mtcars).select_dtypes(np.number).summarize(*
    [(c, np.mean) for c in X.columns]
    + [(c, np.std) for c in X.columns]
  ).pd


