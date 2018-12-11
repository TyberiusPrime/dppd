import pytest
import numpy as np
import pandas as pd
import pandas.testing
from plotnine.data import mtcars
from dppd import dppd
from dppd.single_verbs import parse_column_specification

assert_series_equal = pandas.testing.assert_series_equal
assert_frame_equal = pandas.testing.assert_frame_equal
dp, X = dppd()

__author__ = "Florian Finkernagel"
__copyright__ = "Florian Finkernagel"
__license__ = "mit"


def test_select():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df[["a"]]
    actual = dp(df).select("a").pd
    assert_frame_equal(should, actual)


def test_unselect():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df.drop("a", axis=1)
    actual = dp(df).unselect("a").pd
    assert_frame_equal(should, actual)


def test_select_list():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df[["a", "bb"]]
    actual = dp(df).select(["a", "bb"]).pd
    assert_frame_equal(should, actual)


def test_unselect_list():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df.drop(["a", "bb"], axis=1)
    actual = dp(df).unselect(["a", "bb"]).pd
    assert_frame_equal(should, actual)


def test_select_X_Columns():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df[["a", "bb"]]
    actual = dp(df).select([X.a, X.bb]).pd
    assert_frame_equal(should, actual)


def test_unselect_X_Columns():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df.drop(["a", "bb"], axis=1)
    actual = dp(df).unselect([X.a, X["bb"]]).pd
    assert_frame_equal(should, actual)


def test_select_mix_multiple():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df[["a", "bb"]]
    actual = dp(df).select([X.a, "bb"]).pd
    assert_frame_equal(should, actual)


def test_unselect_mix_multiple():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "cc": list(range(10))}
    )
    should = df.drop(["a", "bb"], axis=1)
    actual = dp(df).unselect([X.a, "bb"]).pd
    assert_frame_equal(should, actual)


def test_select_columns_list_comprehension():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    )
    should = df[["bb"]]
    actual = dp(df).select([x for x in X.columns if len(x) == 2]).pd
    assert_frame_equal(should, actual)


def test_select_columns_str_operation():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    )
    should = df[["bb"]]
    actual = dp(df)
    actual = actual.select(X.columns.str.len() == 2)
    actual = actual.pd
    assert_frame_equal(should, actual)


def test_unselect_columns_list_comprehension():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    )
    should = df[["a", "ccc"]]
    actual = dp(df).unselect([x for x in X.columns if len(x) == 2]).pd
    assert_frame_equal(should, actual)


def test_unselect_columns_str_operation():
    df = pd.DataFrame(
        {"a": list(range(10)), "bb": list(range(10)), "ccc": list(range(10))}
    )
    should = df[["a", "ccc"]]
    actual = dp(df)
    actual = actual.unselect(X.columns.str.len() == 2)
    actual = actual.pd
    assert_frame_equal(should, actual)


def test_select_renaming():
    actual = dp(mtcars).select({"nn": "name", "HP": X.hp}).pd
    should = mtcars[["name", "hp"]].rename(columns={"name": "nn", "hp": "HP"})
    assert_frame_equal(actual, should)


def test_select_renaming_raises_on_group():
    with pytest.raises(ValueError):
        dp(mtcars).groupby("cyl").select({"nn": "name", "HP": X.hp})


def test_select_by_function():
    actual = dp(mtcars).select(lambda x: len(x) == 3)
    assert (actual.columns == ["mpg", "cyl"]).all()


def test_select_regexps():
    actual = dp(mtcars).select(("^m|n",)).pd
    assert (actual.columns == ["name", "mpg"]).all()


def test_unselect_renaming_raises():
    with pytest.raises(ValueError):
        dp(mtcars).unselect({"nn": "name", "HP": X.hp}).pd


def test_unselect_grouped_renaming_raises():
    with pytest.raises(ValueError):
        dp(mtcars).groupby("cyl").unselect({"nn": "name", "HP": X.hp}).pd


def test_unselect_by_function():
    actual = dp(mtcars).unselect(lambda x: len(x) == 3).pd
    assert (
        actual.columns == [x for x in mtcars.columns if x not in ["mpg", "cyl"]]
    ).all()


def test_unselect_regexps():
    actual = dp(mtcars).unselect(("^m|n",)).pd
    assert (
        actual.columns == [x for x in mtcars.columns if x not in ["name", "mpg"]]
    ).all()


def test_unselect_dict_raises():
    with pytest.raises(ValueError):
        dp(mtcars).unselect({"nn": "name", "HP": X.hp}).pd


def test_select_invalid_column_spec():
    with pytest.raises(ValueError):
        dp(mtcars).unselect(5).pd
    with pytest.raises(KeyError):
        dp(mtcars).select([5]).pd
    with pytest.raises(KeyError):
        dp(mtcars).select(["doesnot_exist"]).pd
    with pytest.raises(KeyError):
        dp(mtcars).select("doesnot_exist").pd


def test_select_inverse():
    actual = dp(mtcars).select("-name").pd
    assert (actual.columns == [x for x in mtcars.columns if x not in ["name"]]).all()


def test_select_inverse_with_minus_column():
    m2 = mtcars.rename(columns={"name": "-name"})
    actual = dp(m2).select("-name").pd
    assert (actual.columns == ["-name"]).all()
    actual = dp(m2).select("--name").pd
    assert (actual.columns == [x for x in m2.columns if x not in ["-name"]]).all()


def test_select_inverse_with_minus_column_and_normal_column():
    # the rule is: if it's ambigous, raise
    m2 = mtcars.assign(**{"-name": mtcars.name})
    with pytest.raises(ValueError):  # this one is ambigous
        dp(m2).select("-name").pd
    actual = dp(m2).select("--name").pd  # this one isn't
    assert (actual.columns == [x for x in m2.columns if x not in ["-name"]]).all()
    with pytest.raises(KeyError):
        dp(m2).select("---name").pd  # and this one is not defined


def test_select_inverse_list():
    actual = dp(mtcars).select(["-name", "-hp"]).pd
    assert (
        actual.columns == [x for x in mtcars.columns if x not in ["name", "hp"]]
    ).all()


def test_select_inverse_list_mix_raises():
    with pytest.raises(ValueError):
        dp(mtcars).select(["-name", "hp"]).pd


def test_unselect_inverse():
    actual = dp(mtcars).unselect("-name").pd
    assert (actual.columns == [x for x in mtcars.columns if x in ["name"]]).all()


def test_unselect_inverse_with_minus_column():
    m2 = mtcars.rename(columns={"name": "-name"})
    actual = dp(m2).unselect("-name").pd
    assert (actual.columns == [x for x in m2.columns if x not in ["-name"]]).all()
    actual = dp(m2).unselect("--name").pd
    assert (actual.columns == ["-name"]).all()


def test_unselect_inverse_list():
    actual = dp(mtcars).unselect(["-name", "-hp"]).pd
    assert (actual.columns == [x for x in mtcars.columns if x in ["name", "hp"]]).all()


def test_unselect_inverse_list_mix_raises():
    with pytest.raises(ValueError):
        dp(mtcars).unselect(["-name", "hp"]).pd


def test_select_empty_list():
    actual = dp(mtcars).select([]).pd
    assert len(actual.columns) == 0


def test_unselect_empty_list():
    actual = dp(mtcars).unselect([]).pd
    assert (actual.columns == mtcars.columns).all()


def test_parse_column_spec_return_list_from_bool():
    c = pd.Series(["a", "b", "c", "d"])
    actual = parse_column_specification(
        c, np.array([True, False, False, True], bool), return_list=True
    )
    assert actual == ["a", "d"]


def test_parse_column_spec_return_list_from_empty_list():
    c = pd.Series(["a", "b", "c", "d"])
    actual = parse_column_specification(c, [], return_list=True)
    assert actual == []


def test_parse_column_spec_return_list_from_function():
    c = pd.Series(["a", "b", "c", "d"])
    actual = parse_column_specification(c, (lambda x: x == "a"), return_list=True)
    assert actual == ["a"]


def test_parse_column_spec_return_list_from_regexps():
    c = pd.Series(["a", "b", "c", "d"])
    actual = parse_column_specification(c, ("a|b",), return_list=True)
    assert actual == ["a", "b"]


def test_select_index():
    actual = dp(mtcars).select(X.select_dtypes(int).columns).pd
    should = mtcars[["cyl", "hp", "vs", "am", "gear", "carb"]]
    assert_frame_equal(actual, should)


def test_select_dtypes():
    actual = dp(mtcars).select_dtypes(int).pd
    should = mtcars[["cyl", "hp", "vs", "am", "gear", "carb"]]
    assert_frame_equal(actual, should)


def test_unselect_grouped_does_not_drop_group_column():
    actual = dp(mtcars).groupby("cyl").unselect(["cyl", "name"]).ungroup().pd
    should = mtcars[["cyl"] + [x for x in mtcars.columns if x not in ("name", "cyl")]]
    assert_frame_equal(actual, should)


def test_select_grouped():
    actual = (
        dp(mtcars)
        .groupby(["cyl", "hp"], group_keys=False)
        .select(["name", "qsec"])
        .ungroup()
        .pd
    )

    should = mtcars[["cyl", "hp", "name", "qsec"]]
    assert_frame_equal(actual, should)
