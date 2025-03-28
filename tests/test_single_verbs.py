import pytest
from dppd import dppd
import pandas as pd
import numpy as np
import pandas.testing
from plotnine.data import mtcars, diamonds
from collections import OrderedDict, Counter

assert_series_equal = pandas.testing.assert_series_equal


def assert_frame_equal(left, right, check_column_order=True, **kwargs):
    if not check_column_order:
        assert set(left.columns) == set(right.columns)
        left = left.loc[:, right.columns]
    return pandas.testing.assert_frame_equal(left, right, **kwargs)


dp, X = dppd()

__author__ = "Florian Finkernagel"
__copyright__ = "Florian Finkernagel"
__license__ = "mit"


def ordered_DataFrame(d, index=None):
    """Prior to pandas 0.23 (and python 3.6) the order
    of columns in a DataFrame only followed the definition order for OrderedDicts.
    """
    od = OrderedDict(d)
    return pd.DataFrame(od, index=index)


def test_head():
    df = pd.DataFrame({"a": list(range(10))})
    actual = dp(df).head(5).pd
    should = df.head(5)
    assert_frame_equal(should, actual)


def test_ends():
    df = pd.DataFrame({"a": list(range(10))})
    actual = dp(df).ends(2).pd
    should = df.head(2)
    should = pd.concat([should, df.tail(2)], axis=0)
    assert_frame_equal(should, actual)


def test_2_stage_concat():
    df = pd.DataFrame({"a": list(range(10))})
    a = dp(df).head(5).pd
    actual = dp(df).concat(a).pd
    should = pd.concat([df, a], axis=0)
    assert_frame_equal(should, actual)


def test_list_concat():
    df = pd.DataFrame({"a": list(range(10))})
    should = pd.concat([df, df, df], axis=0)
    actual = dp(df).concat([df, df]).pd
    assert_frame_equal(should, actual)


def test_arrange():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    should = df.sort_values("bb", ascending=False)
    actual = dp(df).arrange("bb").pd
    assert_frame_equal(should, actual)


def test_arrange_column_spec():
    df = pd.DataFrame(
        {
            "a": [str(x) for x in (range(10))],
            "bb": list(range(10)),
            "ccc": list(range(10)),
        }
    ).set_index("a")
    should = df.sort_values("bb", ascending=False)
    actual = dp(df).arrange([x for x in X.columns if len(x) == 2]).pd
    assert_frame_equal(should, actual)


def test_arrange_column_spec_empty():
    with pytest.raises(ValueError):
        dp(mtcars).arrange(X.columns.str.startswith("nosuchcolumn"))


def test_arrange_grouped_column_spec_empty():
    with pytest.raises(ValueError):
        dp(mtcars).groupby("cyl").arrange(lambda x: "nosuchcolumn" in x)


def test_arrange_column_spec_inverse():
    actual = dp(mtcars).select("hp").arrange("-hp").pd
    should = mtcars.sort_values("hp", ascending=True)[["hp"]]
    assert_frame_equal(should, actual)


def test_arrange_kind_allowed():
    with pytest.raises(ValueError):
        dp(mtcars).select(["hp", "qsec"]).arrange("hp", "qsec")


def test_arrange_column_spec_inverse2():
    actual = dp(mtcars).select(["hp", "qsec"]).arrange(["hp", "qsec"]).pd
    should = mtcars.sort_values(["hp", "qsec"], ascending=[False, False])[
        ["hp", "qsec"]
    ]
    assert_frame_equal(should, actual)

    actual = dp(mtcars).select(["hp", "qsec"]).arrange(["-hp", "qsec"]).pd
    should = mtcars.sort_values(["hp", "qsec"], ascending=[True, False])[["hp", "qsec"]]
    assert_frame_equal(should, actual)

    actual = dp(mtcars).select(["hp", "qsec"]).arrange(["hp", "-qsec"]).pd
    should = mtcars.sort_values(["hp", "qsec"], ascending=[False, True])[["hp", "qsec"]]
    assert_frame_equal(should, actual)


def test_mutate():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    should = df.assign(d=list(range(30, 40)))
    actual = dp(df).mutate(d=X["ccc"] + X["bb"]).pd
    assert_frame_equal(should, actual)


def test_transmutate():
    df = pd.DataFrame(
        {"a": [str(x) for x in (range(10))], "bb": 10, "ccc": list(range(20, 30))}
    ).set_index("a")
    should = pd.DataFrame({"d": list(range(30, 40))}).set_index(df.index)
    actual = dp(df).transmutate(d=X["ccc"] + X["bb"]).pd
    assert_frame_equal(should, actual)


def test_distinct_dataFrame():
    df = pd.DataFrame({"a": list(range(5)) + list(range(5)), "b": list(range(10))})
    should = df.head(5)
    actual = dp(df).distinct("a").pd
    assert_frame_equal(should, actual)


def test_distinct_dataFrame_all_columns():
    df = pd.DataFrame({"a": list(range(5)) + list(range(5)), "b": list(range(10))})
    should = df
    actual = dp(df).distinct().pd
    assert_frame_equal(should, actual)

    df = pd.DataFrame({"a": list(range(5)) + list(range(5))})
    should = df.head(5)
    actual = dp(df).distinct().pd
    assert_frame_equal(should, actual)


def test_distinct_series():
    a = pd.Series(["a", "a", "b", "c", "d", "b"])
    should = a.iloc[[0, 2, 3, 4]]
    actual = dp(a).distinct().pd
    assert_series_equal(should, actual)


def test_filter():
    actual = dp(mtcars).filter_by(X.name.str.contains("Merc")).pd
    should = mtcars[mtcars.name.str.contains("Merc")]
    assert_frame_equal(should, actual)


def test_filter_combo():
    actual = dp(mtcars).filter_by(X.name.str.contains("Merc") & (X.hp > 62)).pd
    should = mtcars[mtcars.name.str.contains("Merc") & (mtcars.hp > 62)]
    assert_frame_equal(should, actual)


def test_add_count():
    df = pd.DataFrame({"x": [1, 5, 2, 2, 4, 0, 4], "y": [1, 2, 3, 4, 5, 6, 5]})
    actual = dp(df).add_count().pd
    should = pd.DataFrame(
        OrderedDict(
            [
                ("x", [1, 5, 2, 2, 4, 0, 4]),
                ("y", [1, 2, 3, 4, 5, 6, 5]),
                ("count", len(df)),
            ]
        )
    )
    # should.index = [5, 0, 2, 3, 4, 6, 1]
    assert_frame_equal(should, actual)


def test_groupby_add_count():
    df = pd.DataFrame({"x": [1, 5, 2, 2, 4, 0, 4], "y": [1, 2, 3, 4, 5, 6, 5]})
    actual = dp(df).groupby("x").add_count().ungroup().pd
    should = ordered_DataFrame(
        {
            "x": [1, 5, 2, 2, 4, 0, 4],
            "y": [1, 2, 3, 4, 5, 6, 5],
            "count": [1, 1, 2, 2, 2, 1, 2],
        }
    )
    # should.index = [5, 0, 2, 3, 4, 6, 1]
    assert_frame_equal(should, actual)


def test_groupby_head():
    actual = dp(mtcars).groupby("cyl").head(1).select("name").pd
    should = (
        pd.DataFrame(
            {
                "name": ["Datsun 710", "Mazda RX4", "Hornet Sportabout"],
                "cyl": [4, 6, 8],
                "idx": [2, 0, 4],
            }
        )
        .set_index("idx")
        .sort_index()[["name"]]
    )
    should.index.name = None
    assert_frame_equal(should, actual)


def test_groupby_ungroup_head():
    actual = dp(mtcars).groupby("cyl").identity().ungroup().head(1).pd
    should = mtcars.iloc[[0]]
    should = should[["cyl"] + [x for x in should.columns if x != "cyl"]]
    assert_frame_equal(should, actual)


def test_ungroup_on_non_grouped_raises():
    with pytest.raises(AttributeError):
        dp(mtcars).ungroup()


def test_groupby_summarise():
    actual = dp(mtcars).groupby("cyl").summarise(("name", len, "count")).pd
    should = (
        pd.DataFrame({"cyl": [4, 6, 8], "count": [11, 7, 14]})
        .set_index("cyl")
        .reset_index()
    )
    assert_frame_equal(should, actual)


def test_sorting_within_groups():
    actual = dp(mtcars).groupby(X.cyl).arrange("qsec").ungroup().pd
    should = mtcars.sort_values(["cyl", "qsec"])
    should = should[actual.columns]
    assert_frame_equal(should, actual)


def test_sorting_within_groups_head():
    actual = dp(mtcars).groupby(X.cyl).print().sort_values("qsec").tail(1).pd
    dfs = []
    for cyl, sub_df in mtcars.groupby("cyl"):
        sub_df = sub_df.sort_values("qsec")
        dfs.append(sub_df.tail(1))
    should = pd.concat(dfs)[actual.columns]
    assert_frame_equal(should, actual)


def test_sorting_within_groups_head_ungroup():
    actual = dp(mtcars).groupby(X.cyl).arrange("qsec").ungroup().tail(1).pd
    for cyl, sub_df in mtcars.groupby("cyl"):
        sub_df = sub_df.sort_values("qsec")
        should = sub_df.tail(1)[actual.columns]
    assert_frame_equal(should, actual)


def test_select_in_grouping_keeps_groups():
    actual = dp(mtcars).groupby("cyl").select("qsec").ungroup().pd
    assert (actual.columns == ["cyl", "qsec"]).all()


def test_iter_groups():
    g = []
    ls = []
    for grp, sub_df in dp(mtcars).groupby("cyl").itergroups():
        g.append(grp)
        ls.append(len(sub_df))
    assert g == [4, 6, 8]
    assert ls == [11, 7, 14]


def test_grouped_mutate_returns_scalar_per_group():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count={grp: len(sub_df) for (grp, sub_df) in X.itergroups()})
        .select("count")
        .ungroup()
        .pd.sort_index()
    )
    should = mtcars.groupby("cyl").agg("count")["name"]
    should = ordered_DataFrame(
        {"cyl": mtcars.cyl, "count": [should[cyl] for cyl in mtcars.cyl]},
        index=mtcars.index,
    )
    assert_frame_equal(should, actual)


def test_grouped_mutate_returns_scalar_per_group_str():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count={grp: "X" + str(len(sub_df)) for (grp, sub_df) in X.itergroups()})
        .select("count")
        .ungroup()
        .pd.sort_index()
    )
    should = mtcars.groupby("cyl").agg("count")["name"]
    should = ordered_DataFrame(
        {"cyl": mtcars.cyl, "count": ["X" + str(should[cyl]) for cyl in mtcars.cyl]},
        index=mtcars.index,
    )
    assert_frame_equal(should, actual)


def test_grouped_mutate_returns_series_per_group():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(grp_rank={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()})
        .select("grp_rank")
        .ungroup()
        .pd.sort_index()
    )
    ac = []
    for grp, sub_df in mtcars.groupby("cyl"):
        x = sub_df["hp"].rank()
        ac.append(x)
    ac = pd.concat(ac)
    should = mtcars.assign(grp_rank=ac)[["cyl", "grp_rank"]]
    assert_frame_equal(should, actual)


def test_grouped_mutate_callable():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(max_hp=lambda x: x["hp"].max())
        .select(["cyl", "max_hp", "name"])
        .ungroup()
        .pd
    )
    ac = []
    for grp, sub_df in mtcars.groupby("cyl"):
        x = pd.Series(sub_df["hp"].max(), index=sub_df.index)
        ac.append(x)
    ac = pd.concat(ac)
    should = mtcars.assign(max_hp=ac)[["cyl", "max_hp", "name"]].sort_values("name")
    assert_frame_equal(should, actual.sort_values("name"))


def test_grouped_mutate_callable2():
    actual = (
        dp(mtcars)
        .groupby(["cyl", "qsec"])
        .mutate(max_hp=lambda x: x["hp"].max())
        .select(["cyl", "max_hp", "name"])
        .ungroup()
        .pd
    )
    ac = []
    for grp, sub_df in mtcars.groupby(["cyl", "qsec"]):
        x = pd.Series(sub_df["hp"].max(), index=sub_df.index)
        ac.append(x)
    ac = pd.concat(ac)
    should = mtcars.assign(max_hp=ac)[["cyl", "qsec", "max_hp", "name"]].sort_values(
        "name"
    )
    assert_frame_equal(should, actual.sort_values("name"))


def test_grouped_mutate_returns_scalar():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count=4)
        .select("count")
        .ungroup()
        .pd.sort_index()
    )
    should = mtcars.groupby("cyl").agg("count")["name"]
    should = ordered_DataFrame({"cyl": mtcars.cyl, "count": 4}, index=mtcars.index)
    assert_frame_equal(should, actual)


def test_grouped_mutate_returns_series():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count=pd.Series(range(len(mtcars))))
        .select("count")
        .ungroup()
        .pd.sort_index()
    )
    should = mtcars.groupby("cyl").agg("count")["name"]
    should = ordered_DataFrame(
        {"cyl": mtcars.cyl, "count": pd.Series(range(len(mtcars)))}, index=mtcars.index
    )
    assert_frame_equal(should, actual)


def test_grouped_mutate_in_non_group():
    actual = (
        dp(mtcars)
        .mutate(count={grp: len(sub_df) for (grp, sub_df) in X.itergroups()})
        .select("count")
        .pd.sort_index()
    )
    should = ordered_DataFrame(
        {"count": [len(mtcars)] * len(mtcars)}, index=mtcars.index
    )
    assert_frame_equal(should, actual)


def test_grouped_mutate_in_non_group_invalid_key():
    with pytest.raises(KeyError):
        dp(mtcars).mutate(
            count={"shu": len(sub_df) for (grp, sub_df) in X.itergroups()}
        )


def test_grouped_mutate_in_non_group_multile_keys():
    with pytest.raises(KeyError):
        dp(mtcars).mutate(count={None: 5, "shu": "hello"})


def test_grouped_mutate_repeated_keys():
    df = mtcars.copy()
    df.index = list(range(16)) + list(range(16))
    with pytest.raises(ValueError):  # cannot reindex from duplicate axis
        with dppd(df) as (ddf, X):
            ddf.groupby("cyl").mutate(
                grp_rank={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()}
            )


def test_grouped_mutate_non_sorted():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(grp_rank={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()})
        .select("grp_rank")
        .ungroup()
        .pd.sort_index()
    )
    ac = []
    for grp, sub_df in mtcars.groupby("cyl"):
        x = sub_df["hp"].rank()
        ac.append(x)
    ac = pd.concat(ac)
    should = mtcars.assign(grp_rank=ac)[["cyl", "grp_rank"]]
    assert_frame_equal(should, actual)


def test_groupby_two_summarize_grouped():
    actual = (
        dp(diamonds).groupby(["color", "cut"]).summarise(("price", len, "count")).pd
    )
    should = pd.DataFrame(
        diamonds.groupby(["color", "cut"], observed=False)["price"].agg("count")
    )
    should.columns = ["count"]
    should = should.reset_index()
    assert_frame_equal(should, actual)


def test_groupby_two_mutate_grouped():
    actual = (
        dp(mtcars)
        .groupby(["cyl", "vs"])
        .mutate(grp_rank={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()})
        .select("grp_rank")
        .ungroup()
        .pd.sort_index()
    )
    ac = []
    for grp, sub_df in mtcars.groupby(["cyl", "vs"]):
        x = sub_df["hp"].rank()
        ac.append(x)
    ac = pd.concat(ac)
    should = mtcars.assign(grp_rank=ac)[["cyl", "vs", "grp_rank"]]
    assert_frame_equal(should, actual)


def test_select_does_not_remove_group_columns():
    actual = dp(mtcars).groupby("cyl").select("name").ungroup().pd
    assert (actual.columns == ["cyl", "name"]).all()


def test_unselected_group_columns_is_ignored():
    actual = dp(mtcars).groupby("cyl").unselect("cyl").ungroup().pd
    assert "cyl" in actual.columns


def test_dropping_non_group_columns_works():
    actual = dp(mtcars).groupby("cyl").drop("name", axis=1).ungroup().pd
    assert "name" not in actual.columns


def test_dropping_group_columns_is_ignored():
    actual = dp(mtcars).groupby("cyl").drop("cyl", axis=1).ungroup().pd
    assert "cyl" in actual.columns


def test_groupby_sort_changes_order_but_not_result():
    a = (
        dp(mtcars)
        .groupby("cyl")
        .sort_values("hp")
        .mutate(count={grp: len(sub_df) for (grp, sub_df) in X.itergroups()})
        .ungroup()
        .pd
    )
    b = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count={grp: len(sub_df) for (grp, sub_df) in X.itergroups()})
        .ungroup()
        .pd
    )
    print(a, b)
    assert_frame_equal(a, b.loc[a.index])  #


def test_groupby_sort_changes_order_but_not_result2():
    a = (
        dp(mtcars)
        .groupby("cyl")
        .sort_values("hp")
        .mutate(count={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()})
        .ungroup()
        .pd
    )
    b = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count={grp: sub_df.hp.rank() for (grp, sub_df) in X.itergroups()})
        .ungroup()
        .pd
    )
    assert_frame_equal(a, b.loc[a.index])  #


def test_grouped_mutate_missing_keys():
    actual = (
        dp(mtcars).groupby("cyl").mutate(count={4: 170, 6: 180, 8: 190}).ungroup().pd
    )
    assert (actual[actual.cyl == 4]["count"] == 170).all()
    assert (actual[actual.cyl == 6]["count"] == 180).all()
    with pytest.raises(KeyError):
        dp(mtcars).groupby("cyl").mutate(count={4: 170, 6: 180}).pd


def test_grouped_2_mutate_missing_keys():
    counts = {(4, 0): 40, (4, 1): 41, (6, 0): 60, (6, 1): 61, (8, 0): 80, (8, 1): 81}
    actual = dp(mtcars).groupby(["cyl", "vs"]).mutate(count=counts).ungroup().pd
    print(actual)
    assert (actual[(actual.cyl == 4) & (actual.vs == 0)]["count"] == 40).all()
    assert (actual[(actual.cyl == 4) & (actual.vs == 1)]["count"] == 41).all()
    assert (actual[(actual.cyl == 6) & (actual.vs == 0)]["count"] == 60).all()
    assert (actual[(actual.cyl == 6) & (actual.vs == 1)]["count"] == 61).all()
    assert (actual[(actual.cyl == 8) & (actual.vs == 0)]["count"] == 80).all()
    assert (actual[(actual.cyl == 8) & (actual.vs == 1)]["count"] == 81).all()

    with pytest.raises(KeyError):
        del counts[4, 0]
        dp(mtcars).groupby(["cyl", "vs"]).mutate(count=counts).pd


def test_basic_summary():
    actual = dp(mtcars).groupby("cyl").summarize((X.hp, len, "count")).pd
    should = mtcars.groupby("cyl")[["hp"]].agg("count")
    should.columns = ["count"]
    should = should.reset_index()
    assert_frame_equal(should, actual)  # will fail


def test_summary_quantiles():
    args = [
        ("disp", lambda x, q=q: x.quantile(q), "q%.2f" % q)
        for q in np.arange(0, 1.1, 0.1)
    ]
    actual = dp(mtcars).sort_values("cyl").groupby("cyl").summarise(*args).pd
    lambdas = [lambda x, q=q: x.quantile(q) for q in np.arange(0, 1.1, 0.1)]
    for ll, q in zip(lambdas, np.arange(0, 1.1, 0.1)):
        ll.__name__ = "q%.2f" % q
    should = (
        mtcars.sort_values("cyl")
        .groupby("cyl")["disp"]
        .aggregate(lambdas)
        .reset_index()
    )
    assert_frame_equal(should, actual)


def test_summary_repeated_target_names():
    with pytest.raises(ValueError):
        dp(mtcars).summarise((X.disp, np.mean, "one"), (X.hp, np.mean, "one")).pd


def test_empty_summarize_raises():
    with pytest.raises(ValueError):
        dp(mtcars).groupby("cyl").summarize()
    with pytest.raises(ValueError):
        dp(mtcars).summarize()


def test_summarise_non_tuple():
    with pytest.raises(ValueError):
        dp(mtcars).groupby("cyl").summarize(np.min)


def test_summarize_auto_name():
    actual = dp(mtcars).groupby("cyl").summarize(("hp", np.min)).pd
    assert "hp_amin" in actual.columns or "hp_min" in actual.columns


def test_do():
    def count_and_count_unique(df):
        return pd.DataFrame({"count": [len(df)], "unique": [(~df.duplicated()).sum()]})

    actual = dp(mtcars).groupby("cyl").select("hp").do(count_and_count_unique).pd
    should = pd.DataFrame(
        OrderedDict(
            [("cyl", [4, 6, 8]), ("count", [11, 7, 14]), ("unique", [10, 4, 9])]
        )
    )
    assert_frame_equal(should, actual)


def test_do_categorical_grouping():
    def count_and_count_unique(df):
        return pd.DataFrame({"count": [len(df)], "unique": [(~df.duplicated()).sum()]})

    actual = (
        dp(mtcars)
        .mutate(cyl=pd.Categorical(X.cyl))
        .groupby("cyl")
        .select("hp")
        .do(count_and_count_unique)
        .pd
    )
    should = pd.DataFrame(
        OrderedDict(
            [
                ("cyl", pd.Categorical([4, 6, 8])),
                ("count", [11, 7, 14]),
                ("unique", [10, 4, 9]),
            ]
        )
    )
    assert_frame_equal(should, actual)


def test_do_without_group():
    def count_and_count_unique(df):
        return pd.DataFrame({"count": [len(df)], "unique": [(~df.duplicated()).sum()]})

    actual = dp(mtcars).select("hp").do(count_and_count_unique).pd
    should = pd.DataFrame({"count": [32], "unique": [22]})
    assert_frame_equal(should, actual)


def test_do_group2():
    def count_and_count_unique(df):
        return pd.DataFrame({"count": [len(df)], "unique": [(~df.duplicated()).sum()]})

    actual = (
        dp(mtcars).groupby(["cyl", "am"]).select("hp").do(count_and_count_unique).pd
    )
    should = pd.DataFrame(
        OrderedDict(
            [
                ("cyl", {0: 4, 1: 4, 2: 6, 3: 6, 4: 8, 5: 8}),
                ("am", {0: 0, 1: 1, 2: 0, 3: 1, 4: 0, 5: 1}),
                ("count", {0: 3, 1: 8, 2: 4, 3: 3, 4: 12, 5: 2}),
                ("unique", {0: 3, 1: 7, 2: 3, 3: 2, 4: 7, 5: 2}),
            ]
        )
    )
    assert_frame_equal(should, actual)


def test_filter_by_callable():
    actual = dp(mtcars).filter_by(lambda x: x.hp > 100).pd
    should = mtcars[mtcars.hp > 100]
    assert_frame_equal(actual, should)


def test_filter_by_converted_column():
    actual = dp(mtcars).filter_by("am").pd
    should = mtcars[mtcars.am.astype(bool)]
    assert_frame_equal(actual, should)


def test_filter_by_bool_column():
    actual = (
        dp(mtcars).mutate(rx=X.name.str.contains("RX")).filter_by("rx").select("-rx").pd
    )
    actual2 = (
        dp(mtcars).mutate(rx=X.name.str.contains("RX")).filter_by(X.rx).select("-rx").pd
    )
    should = mtcars[mtcars.name.str.contains("RX")]
    assert_frame_equal(should, actual)
    assert_frame_equal(should, actual2)


def test_filter_by_column_raises_on_non_column():
    with pytest.raises(ValueError):
        dp(mtcars).filter_by("rx").pd


def test_filter_by_vector_grouped():
    actual = dp(mtcars).groupby("cyl").filter_by(X.hp.rank() <= 2).ungroup().pd
    keep = set()
    for grp, sub_df in mtcars.groupby("cyl"):
        keep.update(sub_df["name"][sub_df["hp"].rank() <= 2])
    should = mtcars[mtcars.name.isin(keep)]
    assert set(should.columns) == set(actual.columns)
    should = should[actual.columns]
    assert_frame_equal(actual, should)


def test_filter_by_callable_grouped():
    actual = (
        dp(mtcars).groupby("cyl").filter_by(lambda x: x.hp.rank() <= 2).ungroup().pd
    )
    keep = set()
    for grp, sub_df in mtcars.groupby("cyl"):
        keep.update(sub_df["name"][sub_df["hp"].rank() <= 2])
    should = mtcars[mtcars.name.isin(keep)]
    assert set(should.columns) == set(actual.columns)
    should = should[actual.columns]
    assert_frame_equal(actual, should)


def test_grouped_filter_by_returns_series():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .filter_by(
            {
                grp: sub_df.hp.rank(ascending=False) <= 2
                for (grp, sub_df) in X.itergroups()
            }
        )
        .ungroup()
        .pd.sort_index()
    )
    keep = set()
    for grp, sub_df in mtcars.groupby("cyl"):
        keep.update(sub_df["name"][sub_df["hp"].rank(ascending=False) <= 2])
    should = mtcars[mtcars.name.isin(keep)]
    assert set(should.columns) == set(actual.columns)
    should = should[actual.columns]
    assert_frame_equal(should, actual)


def test_filter_by_unkown_raises():
    with pytest.raises(ValueError):
        dp(mtcars).filter_by(55)


def test_mutate_series():
    with pytest.raises(AttributeError):
        dp(mtcars).sum().mutate(a="A")


def test_groupby_select():
    actual = dp(mtcars)[X.groupby("cyl").hp.rank(ascending=False) < 2].pd
    should = ["Lotus Europa", "Ferrari Dino", "Maserati Bora"]
    assert set(actual.name) == set(should)


def test_groupby_within_chain():
    actual = dp(mtcars).groupby("cyl").select("hp").mean().pd
    should = mtcars.groupby("cyl")[["hp"]].mean()
    assert_frame_equal(should, actual)


def test_groupby_within_chain_select_on_group():
    actual = dp(mtcars).groupby("cyl").select("hp").mean().pd
    should = mtcars.groupby("cyl")[["hp"]].mean()
    assert_frame_equal(should, actual)


def test_groupby_axis_1_raises_on_verb():
    # this is ok
    dp(mtcars).groupby(level=0, axis=1).pd
    with pytest.raises(ValueError):
        dp(mtcars).groupby(level=0, axis=1).select("cyl")


def test_grouped_filter_by_X_apply():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .filter_by(X.apply(len, include_groups=False) > 10)
        .ungroup()
        .pd
    )
    g = mtcars.groupby("cyl").apply(len, include_groups=False) > 10
    should = mtcars[mtcars.cyl.isin(g.index[g])]
    assert_frame_equal(should, actual, check_column_order=False)


def test_grouped_filter_by_wrong_length_of_series():
    with pytest.raises(pd.core.indexing.IndexingError):
        dp(mtcars).groupby("cyl").filter_by(pd.Series([True, False], index=[4, 8]))


def test__lenght_of_series():
    with pytest.raises(pd.core.indexing.IndexingError):
        dp(mtcars).filter_by(pd.Series([True, False], index=[4, 8]))


def test_grouped_mutate_X_apply():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count=X.apply(len, include_groups=False))
        .ungroup()
        .pd
    )
    should = dp(mtcars).groupby("cyl").add_count().ungroup().pd
    assert_frame_equal(should, actual, check_column_order=False, check_dtype=False)


def test_grouped_mutate_X_apply_str():
    actual = (
        dp(mtcars)
        .groupby("cyl")
        .mutate(count=X.apply(lambda x: str(len(x)), include_groups=False))
        .ungroup()
        .pd
    )
    should = (
        dp(mtcars)
        .groupby("cyl")
        .add_count()
        .ungroup()
        .mutate(count=X["count"].astype(str))
        .pd
    )
    assert_frame_equal(should, actual, check_column_order=False)


def test_grouped_mutate_wrong_length():
    with pytest.raises(pd.core.indexing.IndexingError):
        dp(mtcars).groupby("cyl").mutate(count=pd.Series([True, False], index=[4, 8]))


def test_mutate_wrong_length():
    with pytest.raises(pd.core.indexing.IndexingError):
        dp(mtcars).groupby("cyl").mutate(count=pd.Series([True, False], index=[4, 8]))


def test_as_type():
    actual = dp(mtcars).astype("-hp", str).pd
    should = mtcars.assign(
        **{x: mtcars[x].astype(str) for x in mtcars.columns if x != "hp"}
    )
    assert_frame_equal(should, actual)


def test_as_type_kwargs():
    with pytest.raises(ValueError):
        dp(mtcars).astype(X.columns, int).pd
    actual = dp(mtcars).astype(X.columns, int, errors="ignore").pd
    should = mtcars.assign(
        **{x: mtcars[x].astype(int) for x in mtcars.columns if x != "name"}
    )
    assert_frame_equal(should, actual)


def test_categorize():
    df = pd.DataFrame(
        {"a": ["hello", "hello", "world"], "b": ["zanother", "category", "level"]}
    )
    actual = dp(df).categorize("a").pd
    actual2 = dp(df).categorize().pd
    assert isinstance(actual["a"].dtype, pd.api.types.CategoricalDtype)
    assert not isinstance(actual["b"].dtype, pd.api.types.CategoricalDtype)
    assert isinstance(actual2["a"].dtype, pd.api.types.CategoricalDtype)
    assert isinstance(actual2["b"].dtype, pd.api.types.CategoricalDtype)
    assert list(actual2["b"].cat.categories) == ["zanother", "category", "level"]
    actual3 = (
        dp(df).categorize(None, ["hello", "world", "another", "category", "level"]).pd
    )
    assert len(actual3["a"].cat.categories) == 5


def test_print(capsys):
    assert isinstance(dp(mtcars).head().print().pd, pd.DataFrame)
    captured = capsys.readouterr().out
    print(mtcars.head())
    captured2 = capsys.readouterr().out
    assert captured == captured2


def test_print_tipe(capsys):
    assert isinstance(dp(mtcars).head().print_type().pd, pd.DataFrame)
    captured = capsys.readouterr().out
    print(type(mtcars.head()))
    captured2 = capsys.readouterr().out
    assert captured == captured2


def test_print_dir(capsys):
    assert isinstance(dp(mtcars).head().print_dir().pd, pd.DataFrame)
    captured = capsys.readouterr().out
    assert "mutate" in captured


def test_iter_tuples_in_group_by():
    actual = {k: list(v) for (k, v) in dp(mtcars).groupby("cyl").itertuples()}
    should = {}
    for key, sub_df in mtcars.groupby("cyl"):
        should[key,] = list(sub_df.itertuples())
    assert actual == should


def test_natsort():
    df = pd.DataFrame({"a": ["1", "16", "2"], "b": ["another", "category", "level"]})
    df = dp(df).natsort("a").pd
    assert (df["a"] == ["1", "2", "16"]).all()


def test_reset_column():
    df = pd.DataFrame({"a": ["1", "16", "2"], "b": ["another", "category", "level"]})
    df.columns = pd.Categorical(df.columns)
    assert isinstance(df.columns, pd.CategoricalIndex)
    df = dp(df).reset_columns().pd
    assert not isinstance(df.columns, pd.CategoricalIndex)

    df.columns = pd.Categorical(df.columns)
    assert isinstance(df.columns, pd.CategoricalIndex)
    df = dp(df).reset_columns(["x", "y"]).pd
    assert not isinstance(df.columns, pd.CategoricalIndex)
    assert df.columns[0] == "x"

    df.columns = pd.Categorical(df.columns)
    assert isinstance(df.columns, pd.CategoricalIndex)
    df = dp(df).reset_columns(str.upper).pd
    assert not isinstance(df.columns, pd.CategoricalIndex)
    assert df.columns[0] == "X"


def test_reset_columns_single_column_str():
    df = pd.DataFrame({"a": [1]})
    actual = dp(df).reset_columns("b").pd
    assert actual.columns == ["b"]
    with pytest.raises(ValueError):
        dp(pd.DataFrame({"a": [1], "b": [1]})).reset_columns("b").pd


def test_rename_columns():
    df = pd.DataFrame({"a": ["1", "16", "2"], "b": ["another", "category", "level"]})
    df2 = dp(df).rename_columns(str.upper).pd
    assert (df2.columns == ["A", "B"]).all()
    df3 = dp(df).rename_columns(["c", "d"]).pd
    assert (df3.columns == ["c", "d"]).all()


def test_binarize():
    df = pd.DataFrame({"x": [1, 2, 3], "group": ["a", "a", "b"]})
    actual = dp(df).categorize("group").binarize("group").pd
    should = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "group-a": [True, True, False],
            "group-b": [False, False, True],
        }
    )
    assert_frame_equal(should, actual)


def test_binarize_no_drop():
    df = pd.DataFrame({"x": [1, 2, 3], "group": ["a", "a", "b"]})
    actual = dp(df).categorize("group").binarize("group", drop=False).pd
    should = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "group": pd.Categorical(["a", "a", "b"]),
            "group-a": [True, True, False],
            "group-b": [False, False, True],
        }
    )
    assert_frame_equal(should, actual)


def test_dataframe_from_dict():
    actual = dp({"x": [1, 2, 3], "y": ["a", "b", "c"]}).to_frame().pd
    should = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    assert_frame_equal(actual, should)

    actual = dp({"a": 1, "b": 2}).to_frame(orient="index").pd
    print(actual)
    should = pd.DataFrame({0: [1, 2]}, index=["a", "b"])
    assert_frame_equal(actual, should)


def test_dataframe_from_counter():
    c = Counter("llama")
    actual = dp(c).to_frame(key_name="X", count_name="Y").pd
    actual = actual.sort_values("X").reset_index(drop=True)
    should = pd.DataFrame({"X": ["a", "l", "m"], "Y": [2, 2, 1]})
    assert_frame_equal(
        actual,
        should,
    )


def test_dataframe_insert():
    actual = (
        dp(pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]}))
        .insert(0, "a", [4, 5, 6])
        .pd
    )
    should = pd.DataFrame({"a": [4, 5, 6], "x": [1, 2, 3], "y": ["a", "b", "c"]})
    assert_frame_equal(actual, should)
