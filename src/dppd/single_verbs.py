import pandas as pd
import numpy as np
from .base import register_verb, register_type_methods_as_verbs
from .column_spec import parse_column_specification, series_and_strings_to_names

# register all pandas.DataFrame functions and properties.
DataFrameGroupBy = pd.core.groupby.DataFrameGroupBy
SeriesGroupBy = pd.core.groupby.SeriesGroupBy


register_type_methods_as_verbs(
    pd.DataFrame,
    excluded=[
        "select",  # deprecated in pandas and overwritten by our select verb
        "astype",  # replaced by our implementation
        # "drop",  # redefined as pass_full_df below
    ],
)

register_type_methods_as_verbs(pd.Series, ["select"])
register_type_methods_as_verbs(DataFrameGroupBy, ["select"])
register_type_methods_as_verbs(SeriesGroupBy, [])


def group_variables(grp):
    return grp.grouper.names


def group_extract_params(grp):
    if grp.axis != 0:
        raise ValueError(f"Verbs assume that groupby is on axis=0, was {grp.axis}")
    res = {"by": group_variables(grp)}
    for k in ["squeeze", "axis", "level", "as_index", "sort", "group_keys", "observed"]:
        if hasattr(grp, k):
            res[k] = getattr(grp, k)
        else:  # pragma: no cover
            pass  # pragma: no cover
    return res


# verbs


@register_verb(types=None)  # yeah, that one always works
def identity(df):
    """Verb: No-op."""
    return df


@register_verb(name="print", types=None)
def _print(obj):
    print(obj)
    return obj


@register_verb(name="debug", types=None)
def _debug(obj, k=5):
    d = obj.iloc[np.r_[0:k, -k:0]]
    print(d)
    return obj


@register_verb(name="print_type", types=None)
def _type(obj):
    """Verb: No-op."""
    print(type(obj))
    return obj


@register_verb(name="print_dir", types=None, pass_dppd=True)
def _dir(obj):
    """Verb: print dir(obj)"""
    print(dir(obj))
    return obj


@register_verb(name="display", types=None)
def _display(obj):  # pragma: no cover
    display(obj)  # noqa: F821 - Jupyter only, needs to import.
    return obj


@register_verb("ungroup", types=[DataFrameGroupBy])
def ungroup_DataFrameGroupBy(grp):
    df = grp._selected_obj
    columns = group_variables(grp)
    other_cols = [x for x in df.columns if x not in columns]
    return df[columns + other_cols]


@register_verb(["iter_tuples", "itertuples"], types=[DataFrameGroupBy])
def iter_tuples_DataFrameGroupBy(grp):
    df = grp._selected_obj
    columns = group_variables(grp)
    by_key = {}
    for tup in df.itertuples():
        key = tuple(
            (getattr(tup, c) for c in columns)
        )  # replacing this by a evaled() lambda offers no speedup
        if not key in by_key:
            by_key[key] = []
        by_key[key].append(tup)
    for key, tups in by_key.items():
        yield key, tups


@register_verb("concat", types=[pd.DataFrame, pd.Series])
def concat_DataFrame(df, other, axis=0):
    """Verb: Concat this and one ore multiple others.

    Wrapper around :func:`pandas.concat`.

    Parameters
    -----------
        other : df or [df, df, ...]
        axis :  join on rows (axis= 0) or columns (axis = 1)
    """
    if isinstance(other, list):
        return pd.concat([df] + other, axis=axis)
    else:
        return pd.concat([df, other], axis=axis)


@register_verb("select", types=[pd.DataFrame])
def select_DataFrame(df, columns):
    """Verb: Pick columns from a DataFrame

    Improved variant of df[columns]

    Parameters
    ----------
    colummns : column specifiation or dict
         see :func:`dppd.single_verbs.parse_column_specification`

    (for the previous 'rename on dict' behaviour, see select_and_rename
    """
    columns = parse_column_specification(
        df, columns, return_list=True
    )  # we want to keep the order if the user passed one in
    return df.loc[:, columns]


@register_verb("select_and_rename", types=[pd.DataFrame])
def select_and_rename_DataFrame(df, columns):
    """Verb: Pick columns from a DataFrame, and rename them in the process

    Parameters
    ----------
        columns:  dict {new_name: 'old_name'} - select and rename. old_name may be a str, or a
          :class:`Series <pd.Series>` (in which case the .name attribute is used)
    """

    if isinstance(columns, dict):
        columns = {
            series_and_strings_to_names([old_name])[0]: new_name
            for (new_name, old_name) in columns.items()
        }
        result = df[list(columns.keys())]
        result = result.rename(columns=columns)
        return result
    else:
        raise TypeError("Not a dict")


@register_verb("select", types=[DataFrameGroupBy])
def select_DataFrameGroupBy(grp, columns):
    if isinstance(columns, dict):
        raise ValueError("select on grouped by DataFrames does not support renaming")
    df = grp._selected_obj
    columns = parse_column_specification(
        df, columns, return_list=True
    )  # we want to keep the order if the user passed one in
    grp_params = group_extract_params(grp)
    for grp_by in grp_params["by"]:
        if not grp_by in columns:
            columns.append(grp_by)
    df_out = df.loc[:, columns]
    return df_out.groupby(**grp_params)


@register_verb("unselect", types=[pd.Series, pd.DataFrame])
def unselect_DataFrame(df, columns):
    """Verb: Select via an inversed column spec (ie. everything but these)

    Parameters
    ----------
    colummns : column specifiation or dict
        * column specification, see :func:`dppd.single_verbs.parse_column_specification`
    """
    column_bool_vector = parse_column_specification(df, columns)
    return df.loc[:, ~column_bool_vector]


@register_verb("unselect", types=[DataFrameGroupBy])
def unselect_DataFrameGroupBy(grp, columns):
    """Verb: Select via an inversed column spec (ie. everything but these)

    Parameters
    ----------
    colummns : column specifiation or dict
        * column specification, see :func:`dppd.single_verbs.parse_column_specification`
    """
    if isinstance(columns, dict):
        raise ValueError("unselect does not support renaming")
    df = grp._selected_obj
    grp_params = group_extract_params(grp)
    columns = parse_column_specification(
        df, columns, return_list=True
    )  # we want to keep the order if the user passed one in
    columns = [x for x in df.columns if (x not in columns) or (x in grp_params["by"])]
    df_out = df.loc[:, columns]
    return df_out.groupby(**grp_params)


@register_verb("drop", types=DataFrameGroupBy)
def drop_DataFrameGroupBy(grp, *args, **kwargs):
    df = grp._selected_obj
    grp_params = group_extract_params(grp)
    df_out = df.drop(*args, **kwargs)
    for k in grp_params["by"]:
        if not k in df_out.columns:
            df_out = df_out.assign(**{k: df[k]})
    return df_out.groupby(**grp_params)


@register_verb("itergroups", types=pd.DataFrame)
def itergroups_DataFrame(df):
    yield (None, df)


@register_verb("itergroups", types=DataFrameGroupBy)
def itergroups_DataFrameGroupBy(grp):
    yield from grp


@register_verb(name="distinct", types=pd.DataFrame)
def distinct_dataframe(df, column_spec=None, keep="first"):
    """Verb: select distinct/unique rows

    Parameters
    -----------

    column_spec : column specification
        only consider these columns when deciding on duplication
        see :func:`dppd.single_verbs.parse_column_specification`
    keep : str
        which instance to keep in case of duplicates (see :meth:`pandas.DataFrame.duplicated`)

    Returns
    -----
    DataFrame
        with possibly fewer rows, but unchanged columns.

    """
    subset = parse_column_specification(df, column_spec, return_list=True)
    duplicated = df.duplicated(subset, keep)
    return df[~duplicated]


@register_verb(name="distinct", types=pd.Series)
def distinct_series(df, keep="first"):
    """Verb: select distinct values from Series

    Parameters
    -----------
        keep :  which instance to keep in case of duplicates (see :meth:`pandas.Series.duplicated`)
    """
    duplicated = df.duplicated(keep)
    return df[~duplicated]


@register_verb(["transassign", "transmutate"], types=pd.DataFrame)
def transassign(df, **kwargs):
    """Verb: Creates a new dataframe from the columns of the old.

    This means that the index and row count is preserved
    """
    return pd.DataFrame(kwargs, index=df.index)


@register_verb(["mutate", "define"], types=[pd.DataFrame])
def mutate_DataFrame(df, **kwargs):
    """Verb: add columns to a DataFrame defined by kwargs:

    Parameters
    ----------
            kwargs : scalar, pd.Series, callable, dict
                * scalar, pd.Series -> assign column
                * callable - call callable(df) and assign result
                * dict (None: column) - result of itergroups on non-grouped DF to have parity with mutate_DataFrameGroupBy
    Examples
    --------
    add a rank for one column::

        dp(mtcars).mutate(hp_rank = X.hp.rank)


    rank all columns::

        # dict comprehension for illustrative purposes
        dp(mtcars).mutate(**{f"{column}_rank": X[column].rank() for column in X.columns}).pd
        # more efficient
        dp(mtcars).rank().pd()

    one rank per group using callback::

        dp(mtcars).group_by('cyl').mutate(rank = lambda X: X['hp'].rank()).pd


    add_count variant 1 (see :func:`dppd.single_verbs.add_count`)::

        dp(mtcars).group_by('cyl').mutate(count=lambda x: len(x)).pd



    add_count variant 2::

        dp(mtcars).group_by('cyl').mutate(count={grp: len(sub_df) for (grp, sub_df) in X.itergroups()}).pd


    """
    for k, v in kwargs.items():
        if isinstance(v, dict):
            if len(v) != 1:
                raise KeyError("Expected dict with single key: None")
            kwargs[k] = v[None]
    to_assign = kwargs
    return df.assign(**to_assign)


@register_verb(["mutate", "define"], types=[DataFrameGroupBy])
def mutate_DataFrameGroupBy(grp, **kwargs):
    """Verb: add columns to the DataFrame used in the GroupBy.

    Parameters
    ----------
        **kwargs : scalar, pd.Series, callable, dict
                * scalar, pd.Series -> assign column
                * callable - call callable once per group (sub_df) and assign result
                * dict {grp_key: scalar_or_series}: assign this (these) value(s) for the group.  Use in conjunction with `dppd.Dppd.itergroups`.

    """
    df = grp._selected_obj
    grp_params = group_extract_params(grp)

    to_assign = {}
    for k, v in kwargs.items():
        if isinstance(v, dict):  # assume it's a dict of group->subset.
            parts = []
            for (
                group_key,
                sub_index,
            ) in grp.groups.items():  # todo: is there only a group_key one?
                try:
                    r = v[group_key]
                except KeyError:
                    raise KeyError(
                        f"Grouped mutate results did not contain data for {group_key}"
                    )
                r = pd.Series(r, index=sub_index)
                parts.append(r)
            parts = pd.concat(parts)
            v_out = parts
        elif callable(v):
            v_out = []
            parts = []
            for idx, sub_df in grp:
                if not isinstance(idx, tuple):
                    idx = (idx,)
                r = v(sub_df)
                r = pd.Series(r, index=sub_df.index)

                # r = r.assign(
                # **{
                # group_name: group_value
                # for (group_name, group_value) in zip(grp_keys, idx)
                # }
                # )
                # column_order = grp_keys + [x for x in df if x not in grp_keys]
                # df = df[column_order]
                parts.append(r)
            v_out = pd.concat(parts, axis=0)  # .set_index(grp_keys)
        elif isinstance(v, pd.Series):
            if len(v) == len(df):
                v_out = v
            else:
                group_indices = grp.groups
                if set(group_indices.keys()) == set(v.index):
                    keep = pd.Series(None, index=df.index, dtype=object)
                    for group_key, idx in group_indices.items():
                        keep[idx] = v.loc[group_key]
                    v_out = keep
                else:
                    raise pd.core.indexing.IndexingError(
                        "Passed series index did not match grouped or ungrouped index"
                    )

        else:
            v_out = v
        to_assign[k] = v_out
    df_out = df.assign(**to_assign)
    return df_out.groupby(**grp_params)


@register_verb("filter_by", types=[pd.DataFrame, DataFrameGroupBy])
def filter_by(obj, filter_arg):
    """Filter DataFrame


    Parameters
    ----------
        filter_arg : :class:`Series <pd.Series>` or :class:`array <np.ndarray>` or callable or dict or str
            # * Series/Array dtype==bool: return by .loc[filter_arg]
            * callable: Excepted to return a Series(dtype=bool)
            * str: a column name -> .loc[X[filter_arg].astype(bool)]
    """
    if isinstance(obj, pd.DataFrame):
        df = obj
        groups = None
    else:
        df = obj._selected_obj
        grp_params = group_extract_params(obj)
        groups = grp_params["by"]

    if isinstance(filter_arg, pd.Series) or isinstance(filter_arg, np.ndarray):
        if groups is None or len(filter_arg) == len(df):
            result = df.loc[filter_arg]
        else:
            group_indices = obj.groups
            if set(group_indices.keys()) == set(filter_arg.index):
                keep = pd.Series(False, index=df.index)
                for group_key, idx in group_indices.items():
                    keep[idx] = filter_arg.loc[group_key]
                result = df.loc[keep]
            else:
                raise pd.core.indexing.IndexingError(
                    "Passed series index did not match grouped or ungrouped index"
                )

    elif callable(filter_arg):
        if groups is None:
            result = df.loc[filter_arg]
        else:
            result = pd.concat(
                [sub_df.loc[filter_arg] for (idx, sub_df) in df.groupby(groups)]
            )
            # Todo: check performance
            result = result.loc[[x for x in df.index if x in result.index]]
    elif isinstance(filter_arg, dict):
        parts = []
        for idx, sub_df in df.groupby(groups):
            # if not idx in filter_arg and not isinstance(tuple(idx)):
            # idx = (idx,)
            keep = filter_arg[idx]
            parts.append(sub_df[keep])
        result = pd.concat(parts, axis=0)
    elif isinstance(filter_arg, str):
        if filter_arg in df.columns:
            result = df.loc[df[filter_arg].astype(bool)]
        else:
            raise ValueError("string was not a column name")
    else:
        raise ValueError("Could not interpret filter argument")
    if groups is not None:
        return result.groupby(**grp_params)
    else:
        return result


# * dict {grp: boolean_series}:  similar to :func:`mutate <dppd.single_verbs.mutate>`, this dict with group-indices as keys is expanded to a pd.Series(, dtype=bool)


@register_verb("add_count", types=[pd.DataFrame, DataFrameGroupBy])
def add_count(df):
    """Verb: Add the cardinality of a row's group to the row as column 'count'"""
    from .base import dppd

    with dppd(df) as (dp, X):
        return dp.mutate(count=len).pd


@register_verb(["summarize", "summarise"], types=[pd.DataFrame, DataFrameGroupBy])
def summarize(obj, *args):
    """Summarize by group.

    Parameters
    ----------
    *args : tuples
        (column_to_use, function_to_call)
        or
        (column_to_use, function_to_call, new_column_name)
    """
    if not args:
        raise ValueError("Must pass in some func tuples")
    sanitized_args = []
    result = {}
    names = set()
    for tup in args:
        if not isinstance(tup, tuple):
            raise ValueError(
                "All arguments must be tuples of (column_to_use, function_to_call, <new_name>)"
            )
        column = tup[0]
        func = tup[1]
        if isinstance(column, pd.Series):
            column = column.name
        elif isinstance(column, SeriesGroupBy):
            column = group_variables(column)[0]
        if len(tup) == 2:
            name = "%s_%s" % (column, func.__name__)
        else:
            name = tup[2]
        if name in names:
            raise ValueError("Repeated target names")
        names.add(name)
        tup = (column, func, name)
        sanitized_args.append(tup)
        result[name] = []

    if isinstance(obj, pd.DataFrame):
        it = ((None, obj) for x in [1])
        groups = None
        df = obj
    else:
        it = iter(obj)
        df = obj._selected_obj
        groups = group_variables(obj)
        for g in groups:
            result[g] = []

    for idx, sub_df in it:
        if groups is not None:
            if isinstance(idx, tuple):
                for g, i in zip(groups, idx):
                    result[g].append(i)
            else:
                result[groups[0]].append(idx)
        for column_name, func, new_name in sanitized_args:
            result[new_name].append(func(sub_df[column_name]))
    result = pd.DataFrame(result)
    if groups is not None:
        # push group variables to the front
        result = result[groups + [x for x in result.columns if x not in groups]]
        # restore category to categories
        for g in groups:
            if pd.api.types.is_categorical_dtype(df[g]):
                result = result.assign(
                    **{
                        g: pd.Categorical(
                            result[g], df[g].cat.categories, df[g].cat.ordered
                        )
                    }
                )
    return result


@register_verb("do", types=[pd.DataFrame, DataFrameGroupBy])
def do(obj, func, *args, **kwargs):
    """Verb: Do anything to any DataFrame, returning new dataframes

    Apply func to each group, collect results, concat them into
    a new DataFrame with the group information.

    Parameters
    ----------
        func :  callable
            Should take and return a DataFrame


    Example::

        >>> def count_and_count_unique(df):
        ...     return pd.DataFrame({"count": [len(df)], "unique": [(~df.duplicated()).sum()]})
        ...
        >>> dp(mtcars).select(['cyl','hp']).group_by('cyl').do(count_and_count_unique).pd
        cyl  count  unique
        0    4     11      10
        1    6      7       4
        2    8     14       9


    """
    if isinstance(obj, pd.DataFrame):
        df = obj
        groups = None
        it = ((None, df) for x in [1])
    else:
        df = obj._selected_obj
        groups = group_variables(obj)
        it = obj

    new_dfs = []
    for idx, sub_df in it:
        ndf = func(sub_df, *args, **kwargs)
        if groups is not None:
            if not isinstance(idx, tuple):
                idx = (idx,)
            ndf = ndf.assign(**{g: i for (g, i) in zip(groups, idx)})
        new_dfs.append(ndf)
    result = pd.concat(new_dfs)
    if groups is not None:
        # push group variables to the front
        result = result[groups + [x for x in result.columns if x not in groups]]
        # restore category to categories
        for g in groups:
            if pd.api.types.is_categorical_dtype(df[g]):
                result = result.assign(
                    **{
                        g: pd.Categorical(
                            result[g], df[g].cat.categories, df[g].cat.ordered
                        )
                    }
                )
    result = result.reset_index(drop=True)  # give it nice rownumbers
    return result


@register_verb(types=pd.DataFrame)
def gather(df, key, value, value_var_column_spec=None):
    """Verb: Gather multiple columns and collapse them into two.

    This used to be called melting and this is a column spec aware
    forward for pd.melt

    Paramter order is from dplyr.

    Parameters
    ----------
    key : str
        name of the new 'variable' column
    value : str
        name of the new 'value' column
    value_var_column_spec : column specification
        which columns contain the values to be mapped into key/value pairs?
        see :func:`dppd.single_verbs.parse_column_specification`


    Inverse of :func:`dppd.single_verbs.spread <spread>`.

    Example
    --------
    ::

        >>> dp(mtcars).select(['name','hp', 'cyl']).gather('variable', 'value', '-name').pd.head()
                        name variable  value
        0          Mazda RX4       hp    110
        1      Mazda RX4 Wag       hp    110
        2         Datsun 710       hp     93
        3     Hornet 4 Drive       hp    110
        4  Hornet Sportabout       hp    175



    """

    value_vars = parse_column_specification(df, value_var_column_spec, return_list=True)
    id_vars = [x for x in df.columns if x not in value_vars]
    return pd.melt(df, id_vars, value_vars, var_name=key, value_name=value)


@register_verb(types=pd.DataFrame)
def spread(df, key, value):
    """Verb: Spread a key-value pair across multiple columns

    Parameters
    ----------
    key : str or pd.Series
        key column to spread (if series, .name is used)
    value : str or pd.Series
        value column to spread (if series, .name is used)


    Inverse of :func:`dppd.single_verbs.gather <gather>`.

    Example
    --------
    ::

        >>> df = pd.DataFrame({'key': ['a','b'] * 5, 'id': ['c','c','d','d','e','e','f','f','g','g'], 'value':np.random.rand(10)})
        >>> dp(df).spread('key','value')
        >>> dp(df).spread('key','value').pd
        key id         a         b
        0    c  0.650358  0.931324
        1    d  0.633024  0.380125
        2    e  0.983000  0.367837
        3    f  0.989504  0.706933
        4    g  0.245418  0.108165


    """
    key = parse_column_specification(df, key, return_list=True)
    if len(key) > 1:
        raise ValueError("key must be a single column")
    value = parse_column_specification(df, value, return_list=True)
    if len(value) > 1:
        raise ValueError("value must be a single column")

    columns = key[0]
    values = value[0]
    index = [x for x in df.columns if x not in (columns, values)]

    def agg_func(values):
        if len(values) == 1:
            return values.iloc[0]
        else:
            raise ValueError("Duplicate identifiers")

    result = df.pivot_table(
        values=values, columns=columns, index=index, aggfunc=agg_func
    )
    result = result.reset_index()
    return result


@register_verb(types=pd.DataFrame)
def unite(df, column_spec, sep="_"):
    """Verb: string join multiple columns

    Parameters
    ----------
    column_spec :  column_spec
        which columns to join.
        see :func:`dppd.single_verbs.parse_column_specification`

    sep : str
        Seperator to join on
    """

    columns = parse_column_specification(df, column_spec, return_list=True)
    return df[columns].apply(lambda x: sep.join(x.astype(str)), axis=1)


@register_verb(types=pd.DataFrame)
def seperate(df, column, new_names, sep=".", remove=False):
    """Verb: split strings on a seperator.

    Inverse of :func:`unite`

    Parameters
    ----------
    column : str or pd.Series
        column to split on (Series.name is named in case of a series)
    new_names : list
        list of new column names
    sep : str
        what to split on (pd.Series.str.split)
    remove : bool
        wether to drop column
    """

    column = parse_column_specification(df, column, return_list=True)
    if len(column) != 1:
        raise ValueError("Must pass in exactly one column")
    c = df[column[0]]
    if isinstance(c, pd.DataFrame):
        raise ValueError(
            "Multiple columns with the same name - don't know which one to pick"
        )
    s = c.str.split(sep, expand=True)
    s.columns = new_names
    s.index = df.index
    if remove:
        df = df.drop(column, axis=1)
    result = pd.concat([df, s], axis=1)
    return result


@register_verb("print", types=DataFrameGroupBy)
def print_DataFrameGroupBy(grps):
    print("groups: %s" % (grps.grouper.names))
    print(grps._selected_obj)
    return grps


@register_verb("arrange", types=pd.DataFrame)
def arrange_DataFrame(df, column_spec, kind="quicksort", na_position="last"):
    """Sort DataFrame based on column spec.

    Wrapper around sort_values

    Parameters
    ----------
        column_spec : column specification
            see :func:`dppd.single_verbs.parse_column_specification`

        ... :  see :meth:`pandas.DataFrame.sort_values`
    """
    allowed_kinds = "quicksort", "mergesort", "heapsort"
    if not kind in allowed_kinds:
        raise ValueError(f"kind  must be one of {allowed_kinds}")
    cols_plus_inversed = parse_column_specification(df, column_spec, return_list=2)
    if not cols_plus_inversed:
        raise ValueError("No columns passed spec - don't know how to sort")
    columns = [x[0] for x in cols_plus_inversed]
    ascending = [x[1] for x in cols_plus_inversed]
    return df.sort_values(
        columns, ascending=ascending, kind=kind, na_position=na_position
    )


@register_verb("arrange", types=DataFrameGroupBy)
def arrange_DataFrameGroupBy(grp, column_spec, kind="quicksort", na_position="last"):
    df = grp._selected_obj
    grp_params = group_extract_params(grp)

    cols_plus_inversed = parse_column_specification(df, column_spec, return_list=2)
    if not cols_plus_inversed:
        raise ValueError("No columns passed spec - don't know how to sort")
    columns = grp_params["by"].copy()
    ascending = [True] * len(columns)
    columns += [x[0] for x in cols_plus_inversed]
    ascending += [~x[1] for x in cols_plus_inversed]
    df_out = df.sort_values(
        columns, ascending=ascending, kind=kind, na_position=na_position
    )
    df_out = df_out.groupby(**grp_params)
    return df_out


@register_verb("sort_values", types=DataFrameGroupBy)
def sort_values_DataFrameGroupBy(
    grp, column_spec, kind="quicksort", na_position="last"
):
    """Alias for arrange for groupby-objects"""
    return arrange_DataFrameGroupBy(grp, column_spec, kind, na_position)


@register_verb("natsort", types=pd.DataFrame)
def natsort_DataFrame(df, column):
    from natsort import order_by_index, index_natsorted

    return df.reindex(index=order_by_index(df.index, index_natsorted(df[column])))


@register_verb(["astype", "as_type"], types=pd.DataFrame)
def astype_DataFrame(df, columns, dtype, **kwargs):
    columns = parse_column_specification(df, columns, return_list=True)
    return df.assign(**{x: df[x].astype(dtype, **kwargs) for x in columns})


use_df_order = object()


def unique_in_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


@register_verb("categorize", types=pd.DataFrame)
def categorize_DataFrame(df, columns=None, categories=use_df_order, ordered=None):
    """Turn columns into pandas.Categorical.
    By default, they get ordered by their occurrences in the column.
    You can pass False, then pd.Categorical will sort alphabetically,
    or 'natsorted', in which case they'll be passed through natsort.natsorted
    """
    columns = parse_column_specification(df, columns, return_list=True)
    if categories is use_df_order:
        new = {}
        for c in columns:
            new[c] = pd.Categorical(df[c], unique_in_order(df[c]), ordered)
    elif isinstance(categories, str) and categories in ("natsorted", "natsort"):
        import natsort

        new = {}
        for c in columns:
            new[c] = pd.Categorical(df[c], natsort.natsorted(df[c].unique()), ordered)
    else:
        new = {c: pd.Categorical(df[c], categories, ordered) for c in columns}

    df = mutate_DataFrame(df, **new)
    return df


@register_verb(["reset_columns", "rename_columns"], types=pd.DataFrame)
def reset_columns_DataFrame(df, new_columns=None):
    """
    Rename *all* columns in a dataframe (and return a copy).
    Possible new_columns values:

    - None: df.columns = list(df.columns)
    - List: df.columns =  new_columns
    - callable: df.columns = [new_columns(x) for x in df.columns]
    - str && df.shape[1] == 1: df.columns = [new_columns]


    new_columns=None is useful when you were transposing categorical indices and
    now can no longer assign columns.  (Arguably a pandas bug)

    """
    if new_columns is None:
        df.columns = list(df.columns)
    elif isinstance(new_columns, list) or isinstance(new_columns, pd.MultiIndex):
        df.columns = new_columns
    elif isinstance(new_columns, str):
        if df.shape[1] == 1:
            df.columns = [new_columns]
        else:
            raise ValueError("Single string only supported for dfs with 1 column")
    else:
        df.columns = [new_columns(x) for x in df.columns]

    return df


@register_verb("ends", types=pd.DataFrame)
def ends(df, n=5):
    """Head(n)&Tail(n) at once"""
    return df.iloc[np.r_[0:n, -n:0]]  # noqa: E213


@register_verb("binarize", types=pd.DataFrame)
def binarize(df, col_spec, drop=True):
    """Convert categorical columns into
    'regression columns', i.e. X with values a,b,c becomes
    three binary columns X-a, X-b, X-c which are True exactly
    where X was a, etc.
    """
    cols = parse_column_specification(df, col_spec, return_list=True)
    if drop:
        out = [df.drop(cols, axis=1)]
    else:
        out = [df]
    for c in cols:
        levels = df[c].cat.categories
        here = {}
        for ll in levels:
            name = "%s-%s" % (c, ll)
            here[name] = df[c] == ll
        out.append(pd.DataFrame(here))
    return pd.concat(out, axis=1)


@register_verb("to_frame", types=dict)
def to_frame_dict(d, **kwargs):
    """``pd.DataFrame.from_dict(d, **kwargs)``,
    so you can say ``dp({}).to_frame()``"""
    return pd.DataFrame.from_dict(d, **kwargs)


@register_verb("norm_0_to_1", types=pd.DataFrame)
def norm_0_to_1(df, axis=1):
    """Normalize a (numeric) data frame so that
    it goes from 0 to 1 in each row (axis=1) or column (axis=0)
    Usefully for PCA, correlation, etc. because then
    the dimensions are comparable in size"""
    if axis == 1:
        a1 = 1
        a2 = 0
    else:
        a1 = 0
        a2 = 1
    df_normed = df.sub(df.min(axis=a1), axis=a2)
    df_normed = df.div(df.max(axis=a1), axis=a2)
    return df_normed


@register_verb("log2", types=pd.DataFrame)
def log2(df):
    df = df.select_dtypes(np.number)
    res = {c: np.log2(df[c]) for c in df.columns}
    return pd.DataFrame(res, index=df.index)


@register_verb("zscore", types=pd.DataFrame)
def norm_zscore(df, axis=1):
    """apply zcore transform (X - mu) / std via scipy.stats.zcore an the given axis"""
    import scipy.stats

    return pd.DataFrame(
        scipy.stats.zscore(df, axis=1), columns=df.columns, index=df.index
    )


@register_verb("colspec", types=pd.DataFrame)
def colspec_DataFrame(df, columns, invert=False):
    """Return columns as defined by your column specification, so you can use
    colspec in set_index etc

        * column specification, see :func:`dppd.single_verbs.parse_column_specification`
    """
    res = parse_column_specification(
        df, columns, return_list=True
    )  # we want to keep the order if the user passed one in
    if not invert:
        return res
    else:
        return [x for x in df.columns if x not in res]


@register_verb("pca", types=pd.DataFrame)
def pca_dataframe(df, whiten=False, random_state=None, n_components=2):
    """Perform 2 component PCA using sklearn.decomposition.PCA.
    Expects samples in rows!
    Returns a tuple (DataFrame{sample, 1st, 2nd},
    whith an additiona l, explained_variance_ratio_ attribute
    """
    from sklearn.decomposition import PCA
    import warnings

    p = PCA(n_components=n_components, whiten=whiten, random_state=random_state)
    df_fit = pd.DataFrame(p.fit_transform(df))
    df_fit.columns = ["1st", "2nd"]
    df_fit.index = df.index
    df_fit.index.name = "sample"
    df_fit = df_fit.reset_index()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_fit.explained_variance_ratio_ = p.explained_variance_ratio_
    return df_fit


@register_verb("insert", types=pd.DataFrame, ignore_redefine=True)
def insert_return_self(df, loc, column, value, **kwargs):
    """DataFrame.insert, but return self.
    """
    df.insert(loc, column, value, **kwargs)
    return df
