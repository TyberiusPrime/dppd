Filter by value wise callback 
======================================================================

Prelude::

  cb = lambda x: 'Europa' in str(x)


pandas::

  mtcars.loc[[cb(x) for x in mtcars.name]]


plydata::

 mtcars.query('[cb(x) for x in mtcars.name]') -> 'PandasExprVisitor' object has no attribute 'visit_ListComp'
 

plydata::

 mtcars >> dp.define(mf='[cb(x) for x in name]') >> dp.query('mf') > cb is not defined

 mtcars >> dp.define(mf=[cb(x) for x in mtcars.name]) >> dp.query('mf') #note repetition
 
 mtcars >> dp.call('.__getitem__', [cb(x) for x in mtcars.name]) # note repetition
 

dpylython::

 dp.DplyFrame(mtcars) >> dp.sift([cb(x) for x in X.name]) >  does not return

 dp.DplyFrame(mtcars) >> dp.sift([cb(x) for x in mtcars.name]) -> list object has no attr evaluate # bool array won't work either

 mutate + list comprehension -> no return

 dp.DplyFrame(mtcars) >> dp.mutate(mf= [cb(x) for x in mtcars.name]) >> dp.sift(X.mf) # note reference to actual DF


dfply::

 mtcars >> dp.filter_by([cb(x) for x in X.name]) _> iter() returned non-iterator of type Intention

 mtcars >> dp.mutate(mf=[cb(x) for x in mtcars.name]) >> dp.filter_by(X.mf) # note repetition

 mtcars >> dp.mutate(mf=dfply.make_symbolic(cb)(X.name)) >> dp.filter_by(X.mf) -> always True!

 Working:

 mtcars >> dp.mutate(mf=dfply.make_symbolic(lambda series: [cb(x) for x in series])(X.name)) >> dp.filter_by(X.mf)

 mtcars >> dp.filter_by(dfply.make_symbolic(lambda series: pd.Series([cb(x) for x in
 series]))(X.name))

Functions have to be symbol aware, and return series for filtering to work

dppd::

  dp(mtcars).filter_by([cb(x) for x in X.name]).pd()



