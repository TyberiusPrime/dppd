# dppd

| Build status: | [![Build Status](https://travis-ci.com/TyberiusPrime/dppd.svg?branch=master)](https://travis-ci.com/TyberiusPrime/dppd)|
|---------------|-----------------------------------------------------------------------------|
| Documentation | https://dppd.readthedocs.io/en/latest/

| Code style    | ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Dppd is a python [dplyr](dplyr.tidyverse.org) clone.


It allows you to use code like this


```python
   >>> from plotnine.data import mtcars
   >>> from dppd import dppd
   >>> dp, X = dppd()
   >>> dp(mtcars).mutate(kwh = X.hp * 0.74).groupby('cyl').filter_by(X.kwh.rank() < 2).ungroup().pd
      cyl              name   mpg   disp   hp  drat     wt   qsec  vs  am  gear  carb     kwh
   5     6           Valiant  18.1  225.0  105  2.76  3.460  20.22   1   0     3     1   77.70
   18    4       Honda Civic  30.4   75.7   52  4.93  1.615  18.52   1   1     4     2   38.48
   21    8  Dodge Challenger  15.5  318.0  150  2.76  3.520  16.87   0   0     3     2  111.00
   22    8       AMC Javelin  15.2  304.0  150  3.15  3.435  17.30   0   0     3     2  111.00
```


Briefly, it uses a data-manipulater instance (dp above) together with a proxied 
reference to the latest created DataFrame (the X above) to achive for pandas what dpylr's 
non-standard-evaluation based verbs does for R.


Please see our full documentation at https://dppd.readthedocs.io/en/latest/
for more details and a list of the supported verbs.


Also check out [dppd_plotnine](https://github.com/TyberiusPrime/dppd_plotnine)


