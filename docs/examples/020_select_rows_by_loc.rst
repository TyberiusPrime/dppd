Select by loc / rownames
==================================================

R:: 

    no rownames in tibbles

pandas::

    mtcars.loc[[6]]

plydata::

    (mtcars >>dp.call('.loc'))[[6]]


dpylython::

    dp.DplyFrame(mtcars) >> X._.loc[[6]]

dfply::

    @dfpipe
    def loc(df, a=None, b=None, c=None):
        print(type(a))
        if isinstance(a, (tuple, list)):
            indices = np.array(a)
        elif isinstance(a, pd.Series):
            indices = a.values
        elif isinstance(a, int) or isinstance(b, int) or isinstance(c, int):
            indices = slice(a,b,c)
        return df.loc[indices, :]

    mtcars >> loc([6,])

@dfpipe makes defining verbs easy. Converting function calls to slices is still a bit of work though.

dppd::
    dp(mtcars).loc[6,].pd()


