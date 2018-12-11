import pytest
from dppd import dppd
import pandas as pd
import numpy as np
import pandas.testing
from plotnine.data import mtcars

assert_series_equal = pandas.testing.assert_series_equal
assert_frame_equal = pandas.testing.assert_frame_equal
dp, X = dppd()

__author__ = "Florian Finkernagel"
__copyright__ = "Florian Finkernagel"
__license__ = "mit"


def get_stocks():
    return pd.DataFrame(
        {
            "time": pd.date_range("2009-01-01", "2009-01-10"),
            "X": np.random.normal(0, 1, size=10),
            "Y": np.random.normal(0, 2, size=10),
            "Z": np.random.normal(0, 4, size=10),
        }
    )


def test_basic_gather():
    stocks = get_stocks()

    actual = dp(stocks).gather("stock", "price", ["X", "Y", "Z"]).pd
    should = pd.melt(stocks, ["time"], ["X", "Y", "Z"], "stock", "price")
    assert_frame_equal(should, actual)

    actual = dp(stocks).gather("stock", "price", "-time").pd
    should = pd.melt(stocks, ["time"], ["X", "Y", "Z"], "stock", "price")
    assert_frame_equal(should, actual)


def test_gather_iris():
    mini_iris = pd.DataFrame(
        {
            "sepal.length": {0: 5.1, 50: 7.0, 100: 6.3},
            "sepal.width": {0: 3.5, 50: 3.2, 100: 3.3},
            "petal.length": {0: 1.4, 50: 4.7, 100: 6.0},
            "petal.width": {0: 0.2, 50: 1.4, 100: 2.5},
            "target": {0: "setosa", 50: "versicolor", 100: "virginica"},
        }
    )
    actual = (
        dp(mini_iris)
        .gather(
            "flower_att",
            "measurement",
            ["sepal.length", "sepal.width", "petal.length", "petal.width"],
        )
        .pd
    )
    should = pd.DataFrame(
        {
            "target": [
                "setosa",
                "versicolor",
                "virginica",
                "setosa",
                "versicolor",
                "virginica",
                "setosa",
                "versicolor",
                "virginica",
                "setosa",
                "versicolor",
                "virginica",
            ],
            "flower_att": [
                "sepal.length",
                "sepal.length",
                "sepal.length",
                "sepal.width",
                "sepal.width",
                "sepal.width",
                "petal.length",
                "petal.length",
                "petal.length",
                "petal.width",
                "petal.width",
                "petal.width",
            ],
            "measurement": [5.1, 7.0, 6.3, 3.5, 3.2, 3.3, 1.4, 4.7, 6.0, 0.2, 1.4, 2.5],
        }
    )
    assert_frame_equal(actual, should)
    actual2 = dp(mini_iris).gather("flower_att", "measurement", "-target").pd
    assert_frame_equal(actual, actual2)


def test_basic_spread():
    stocks = get_stocks()
    tidy_stocks = dp(stocks).gather("stock", "price", "-time").pd
    actual = dp(tidy_stocks).spread("stock", "price").pd
    actual.columns.name = None  # our spread set's a name...
    assert_frame_equal(actual, stocks)

    actual = dp(tidy_stocks).spread("time", "price").pd
    assert (actual.columns == ["stock"] + list(stocks.time)).all()


def test_spread_raises_on_multiple_keys():
    with pytest.raises(ValueError):
        dp(mtcars).spread(["name", "cyl"], ["hp"]).pd


def test_spread_raises_on_multiple_values():
    with pytest.raises(ValueError):
        dp(mtcars).spread(["name"], ["hp", "cyl"]).pd


def test_spread_raises_on_duplicate_values():
    stocks = pd.concat([get_stocks(), get_stocks()])
    tidy_stocks = dp(stocks).gather("stock", "price", "-time").pd
    with pytest.raises(ValueError):
        dp(tidy_stocks).spread("stock", "price").pd


def test_seperate():
    df = pd.DataFrame({"X": [None, "a.b", "a.d", "b.c"]})
    actual = dp(df).seperate(X.X, ["A", "B"]).pd
    assert actual.A.iloc[0] is None
    assert actual.B.iloc[0] is None
    assert (actual.A.iloc[1:] == ["a", "a", "b"]).all()
    assert (actual.B.iloc[1:] == ["b", "d", "c"]).all()
    assert "X" in actual.columns


def test_seperate_and_remove():
    df = pd.DataFrame({"X": [None, "a.b", "a.d", "b.c"]})
    actual = dp(df).seperate(X.X, ["A", "B"], remove=True).pd
    assert actual.A.iloc[0] is None
    assert actual.B.iloc[0] is None
    assert (actual.A.iloc[1:] == ["a", "a", "b"]).all()
    assert (actual.B.iloc[1:] == ["b", "d", "c"]).all()
    assert "X" not in actual.columns


def test_seperate_raises_on_Multip_column():
    df = pd.DataFrame({"X": [None, "a.b", "a.d", "b.c"], "Y": 5})
    with pytest.raises(ValueError):
        dp(df).seperate([X.X, X.Y], ["A", "B"])


def test_unite():
    actual = dp(mtcars).unite(["vs", "am"], "---").pd
    should = [str(vs) + "---" + str(am) for (vs, am) in zip(mtcars.vs, mtcars.am)]
    assert (actual == should).all()


def test_print(capsys):
    dp(mtcars).print()
    captured = capsys.readouterr()
    assert "Mazda RX4" in captured.out
    dp(mtcars).groupby("cyl").print()
    captured = capsys.readouterr()
    assert "groups: ['cyl']" in captured.out
    assert "Mazda RX4" in captured.out
