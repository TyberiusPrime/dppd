#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dppd import dppd, register_verb, alias_verb
from dppd.base import register_property
import pandas as pd
import numpy as np
import pandas.testing
import wrapt
from plotnine.data import mtcars, diamonds


__author__ = "Florian Finkernagel"
__copyright__ = "Florian Finkernagel"
__license__ = "mit"

assert_series_equal = pandas.testing.assert_series_equal
assert_frame_equal = pandas.testing.assert_frame_equal

dp, X = dppd()


def test_noop():
    df = pd.DataFrame({"a": list(range(10))})
    actual = dp(df)
    actual = actual.pd
    assert isinstance(actual, pd.DataFrame)
    should = df
    assert_frame_equal(should, actual)


def test_non_df_result():
    import dppd.base

    df = pd.DataFrame({"a": list(range(10))})
    shape = dp(df).head(5).shape
    assert not isinstance(shape, dppd.base.DPPDAwareProxy)
    assert shape == (5, 1)
    real_pd = shape.pd
    assert isinstance(real_pd, tuple)


def test_nested_dp_pd_calls():
    df = pd.DataFrame({"a": list(range(10))})
    actual = dp(df).head(5).concat(dp(df).tail(4).pd).pd
    should = pd.concat([df.head(5), df.tail(4)], axis=0)
    assert_frame_equal(should, actual)


def test_dp_pd_calls_nested_in_function_calls():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    ).set_index("a")

    def shu():
        return dp(df).head(1).pd

    def sha():
        return dp(df).tail(1).pd

    should = pd.concat([df.head(1), df.tail(1), df.head(1)])
    actual = dp(shu()).concat(sha()).concat(shu()).pd
    assert_frame_equal(should, actual)


def test_redefining_verb_vars():
    def noop(df):
        return df

    register_verb("test_redefining_verb_vars_noop")(noop)
    with pytest.warns(UserWarning):
        register_verb("test_redefining_verb_vars_noop")(noop)


def test_alias_unknown_raises():
    with pytest.raises(KeyError):
        alias_verb("test_alias_unknown_raises2", "test_alias_unknown_raises")


def test_redefining_alias_warns():
    def noop(df):
        return df

    register_verb("test_redefining_alias_warns")(noop)
    register_verb("test_redefining_alias_warns3")(noop)
    with pytest.warns(None) as record:
        alias_verb("test_redefining_alias_warns2", "test_redefining_alias_warns")
        assert len(record) == 0
    # redefining to the same is harmless
    with pytest.warns(None) as record:
        alias_verb("test_redefining_alias_warns2", "test_redefining_alias_warns")
        assert len(record) == 0

    with pytest.warns(UserWarning):
        alias_verb("test_redefining_alias_warns2", "test_redefining_alias_warns3")


def test_property_shadowed():
    with pytest.warns(UserWarning):
        register_property("select", pd.DataFrame)


def test_property_list_of_types():
    import dppd.base

    class A:
        pass

    class B:
        pass

    register_property("test_property_list_of_types", [A, B])
    assert "test_property_list_of_types" in dppd.base.property_registry[A]


def test_verb_shadows_property():
    def noop(df):
        return df

    register_property("test_verb_shadows_property_noop")

    with pytest.warns(UserWarning):
        register_verb("test_verb_shadows_property_noop")(noop)


def test_register_verb_raises_on_non_identifier():
    with pytest.raises(TypeError):
        register_verb(name="Hello world")(lambda x: x)


def test_verb_returning_non_df():
    df = pd.DataFrame({"a": [str(x) for x in (range(10))]})
    register_verb("da_length")(lambda df: len(df))
    assert 10 == dp(df).da_length()


def test_no_context_manager_non_df_returning_verbs():
    df = pd.DataFrame({"a": [str(x) for x in (range(10))]})
    dp(df)
    dp().head(1)
    assert len(X) == 1
    assert X.shape == (1, 1)
    actual = dp().pd
    assert actual.shape == (1, 1)
    assert actual.__len__() == 1


def test_no_attribute_no_verb_raises_attribute_error():
    df = pd.DataFrame({"a": [str(x) for x in (range(10))]})
    with pytest.raises(AttributeError):
        dp(df).shu()


def test_no_attribute_no_verb_raises_attribute_error_context_manager():
    df = pd.DataFrame({"a": [str(x) for x in (range(10))]})
    with pytest.raises(AttributeError):
        with dppd(df) as (dp, X):
            dp.shu()


def test_dp_on_empty_stack_raises():
    dp, X = dppd()
    with pytest.raises(ValueError):
        dp()


def test_dp_continuation():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    dp(df).head(5)
    dp().tail(1)
    actual = dp().pd
    should = df.iloc[4:5]
    assert_frame_equal(should, actual)


def test_context_manager():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    with dppd(df) as (d, X):
        d.head(5)
        d.tail(1)
    should = df.iloc[4:5]
    assert_frame_equal(X, should)


def test_context_manager_with_non_df_args():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    with dppd(df) as (d, X):
        d.head(5)
        assert d.shape == (5, 2)
        d.tail(1)
    should = df.iloc[4:5]
    assert_frame_equal(X, should)


def test_context_manager_totally_to_pandas():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    with dppd(df) as (d, X):
        d.head(5)
        assert d.shape == (5, 2)
        d.tail(1)
    should = df.iloc[4:5]
    assert_frame_equal(X, should)
    assert isinstance(X, wrapt.ObjectProxy)
    X = X.pd
    assert not isinstance(X, wrapt.ObjectProxy)
    assert_frame_equal(X, should)


def test_interleaved_context_managers():
    with dppd(mtcars) as (dpX, X):
        with dppd(diamonds) as (dpY, Y):
            dpX.groupby("cyl")
            dpY.filter_by(Y.cut == "Ideal")
            dpX.summarize(("hp", np.mean, "mean_hp"))
            dpY.summarize(("price", np.max, "max_price"))
    should_X = (
        mtcars.groupby("cyl")[["hp"]].agg(np.mean).rename(columns={"hp": "mean_hp"})
    ).reset_index()
    should_Y = (
        pd.DataFrame(diamonds[diamonds.cut == "Ideal"].max()[["price"]])
        .transpose()
        .rename(columns={"price": "max_price"})
    )
    should_Y["max_price"] = should_Y["max_price"].astype(int)
    assert_frame_equal(X, should_X)
    assert_frame_equal(Y, should_Y)


def test_context_manager_chain():
    with dppd(mtcars) as (dp, X):
        dp.mutate(kw=X.hp * 0.7457)
    with dppd(X) as (dp, X):
        dp.mutate(watt=X.kw * 1000)
    assert "watt" in X.columns


def test_mixing_context_manager_and_dp():
    with dppd(mtcars) as (dpY, Y):
        dpY.sort_values("hp")
        dp(diamonds).filter_by(X.cut == "ideal")
        dpY.filter_by(Y.cyl.isin([4, 6]))
        actual_diamonds = dp().sort_values("price").head().pd
        actual_mtcars_full = dpY.pd
        dpY.head()
    actual_mtcars = dpY.pd
    should_diamonds = diamonds[diamonds.cut == "ideal"].sort_values("price").head()
    should_mtcars = mtcars.sort_values("hp")
    should_mtcars_full = should_mtcars[should_mtcars["cyl"].isin([4, 6])]
    should_mtcars = should_mtcars_full.head()
    assert_frame_equal(should_diamonds, actual_diamonds)
    assert_frame_equal(should_mtcars, actual_mtcars)
    assert_frame_equal(should_mtcars_full, actual_mtcars_full)


def test_dppd_raises_on_non_dataframe():
    with pytest.raises(ValueError):
        dp(5)


def test_straight_dp_raises():
    dp, X = dppd()
    with pytest.raises(ValueError):
        dp.select(["hp", "cyl"])

    with pytest.raises(ValueError):
        dp.loc[5]

def test_stacking():
    dp, X = dppd()
    a = dp(mtcars).select(['name','hp','cyl'])
    b = dp(mtcars).select('hp').pd
    assert_frame_equal(b, mtcars[['hp']])
    assert_frame_equal(X, mtcars[['name','hp','cyl']])
    c = dp.pd
    assert_frame_equal(c, mtcars[['name','hp','cyl']])
    assert (X == None) # since it's the proxy, is will fail

def test_forking():
    dp, X = dppd()
    a = dp(mtcars).select(["name", "hp", "cyl"])
    b = dp.unselect("hp").select(X.name).head().pd
    with pytest.raises(AttributeError):
        c = a.select(X.hp).head().pd
    c = dp(a).select(X.hp).head().pd
    assert_series_equal(c["hp"], mtcars["hp"].head())
    assert_series_equal(b["name"], mtcars["name"].head())
    assert (X == None) # since it's the proxy, is will fail


def test_forking_context_manager():
    with dppd(mtcars) as (dp, X):
        a = dp.select(["name", "hp", "cyl"])
        b = dp.select("name").head().pd
        c = a.select("hp").head().pd
        dp.head()
    assert_series_equal(c["hp"], mtcars["hp"].head())
    assert_series_equal(b["name"], mtcars["name"].head())
    assert_frame_equal(X, mtcars[["hp"]].head())


def test_dp_on_dp():
    import wrapt

    a = dp(mtcars)
    b = dp(a)
    assert not isinstance(a.df, wrapt.ObjectProxy)
    assert not isinstance(b.df, wrapt.ObjectProxy)


def test_descend_on_None_raises():
    with pytest.raises(ValueError):
        dp(mtcars)._descend(None)


def test_series_methods():
    actual = dp(mtcars).sum().to_frame().pd
    should = mtcars.sum().to_frame()
    assert_frame_equal(should, actual)


def test_group_on_series_raises():
    with pytest.raises(KeyError):
        dp(mtcars).sum().groupby("no_such_columns")
