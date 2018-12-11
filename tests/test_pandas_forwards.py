#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dppd import dppd
import pandas as pd
import pandas.testing
from plotnine.data import mtcars


__author__ = "Florian Finkernagel"
__copyright__ = "Florian Finkernagel"
__license__ = "mit"

assert_series_equal = pandas.testing.assert_series_equal
assert_frame_equal = pandas.testing.assert_frame_equal

dp, X = dppd()


def test_iloc():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    )
    should = df.iloc[:3]
    actual = dp(df).iloc[:3].pd
    assert_frame_equal(should, actual)


def test_loc():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    ).set_index("a")
    should = df.loc[[3]]
    actual = dp(df).loc[[3]].pd
    assert_frame_equal(should, actual)


def test_loc_str():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    should = df.loc[["3"]]
    actual = dp(df).loc[["3"]].pd
    assert_frame_equal(should, actual)


def test_loc_returning_series():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    ).set_index("a")
    should = df.loc[3]
    actual = dp(df).loc[3].pd
    assert_series_equal(should, actual)


def test_at():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    value = dp(df).at["3", "bb"]
    assert value == 3


def test_iat():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10, 20)),
        }
    ).set_index("a")
    value = dp(df).iat[3, 0]
    assert value == 3


def test_sample():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    ).set_index("a")
    should = df.sample(3, random_state=3)
    actual = dp(df).sample(3, random_state=3).pd
    assert_frame_equal(should, actual)


def test_index():
    import dppd.base
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    index = dp(df).index
    assert (index == df.index).all()
    assert not isinstance(index, dppd.base.DPPDAwareProxy)


def test_sort_values():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    should = df.sort_values("bb", ascending=False)
    actual = dp(df).sort_values("bb", ascending=False).pd
    assert_frame_equal(should, actual)


def test_assign():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    should = df.assign(d=df["ccc"] * 2)
    actual = dp(df).assign(d=X["ccc"] * 2).pd
    assert_frame_equal(should, actual)


def test_assign_in_order():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    should = df.assign(d=list(range(30, 40)), d2=lambda x: x["d"] + 2)
    actual = dp(df).assign(d=X["ccc"] + X["bb"], d2=lambda x: x["d"] + 2).pd
    assert_frame_equal(should, actual)


def test_rename():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    )
    with dppd(df) as (ndf, X):
        ndf.rename(columns={"a": "a2", "bb": "ccc", "ccc": "c2"})
    assert (X.columns == ["a2", "ccc", "c2"]).all()


def test_dataframe_subscript():
    with dppd(mtcars) as (dp, X):
        actual = dp.head(5)["name"].pd
    should = mtcars["name"].head(5)
    assert_series_equal(actual, should)
