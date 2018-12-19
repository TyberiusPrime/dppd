import pandas as pd
import numpy as np
from .base import register_verb, alias_verb, register_type_methods_as_verbs
from .column_spec import parse_column_specification, series_and_strings_to_names

# register all pandas.DataFrame functions and properties.
DataFrameGroupBy = pd.core.groupby.groupby.DataFrameGroupBy
SeriesGroupBy = pd.core.groupby.groupby.SeriesGroupBy


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
register_type_methods_as_verbs(pd.core.groupby.groupby.SeriesGroupBy, [])


def group_variables(grp):
    return grp.grouper.names


def group_extract_params(grp):
    if grp.axis != 0:
        raise ValueError(f"Verbs assume that groupby is on axis=0, was {grp.axis}")
    res = {
        "by": group_variables(grp),
        "squeeze": grp.squeeze,
        "axis": grp.axis,
        "level": grp.level,
        "as_index": grp.as_index,
        "sort": grp.sort,
        "group_keys": grp.group_keys,
        "observed": grp.observed,
    }
    return res


# verbs


@register_verb(types=None)  # yeah, that one always works
def identity(df):
    """Verb: No-op."""
    return df


@register_verb("ungroup", types=[DataFrameGroupBy])
def ungroup_DataFrameGroupBy(grp):
    df = grp._selected_obj
    columns = group_variables(grp)
    other_cols = [x for x in df.columns if x not in columns]
    return df[columns + other_cols]


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
        * column specification, see :func:`dppd.single_verbs.parse_column_specification`
        * dict {old_name: 'new_name'} - select and rename. old_name may be a str, or a
          :class:`Series <pd.Series>` (in which case
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
        columns = parse_column_specification(
            df.columns, columns, return_list=True
        )  # we want to keep the order if the user passed one in
        return df.loc[:, columns]


@register_verb("select", types=[DataFrameGroupBy])
def select_DataFrameGroupBy(grp, columns):
    if isinstance(columns, dict):
        raise ValueError("select on grouped by DataFrames does not support renaming")
    df = grp._selected_obj
    columns = parse_column_specification(
        df.columns, columns, return_list=True
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
    if isinstance(columns, dict):
        raise ValueError("unselect does not support renaming (passing a dict)")
    else:
        column_bool_vector = parse_column_specification(df.columns, columns)
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
        df.columns, columns, return_list=True
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
    subset = parse_column_specification(df.columns, column_spec, return_list=True)
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


@register_verb(types=pd.DataFrame)
def transassign(df, **kwargs):
    """Verb: Creates a new dataframe from the columns of the old.

    This means that the index and row count is preserved
    """
    return pd.DataFrame(kwargs, index=df.index)


@register_verb("mutate", types=[pd.DataFrame])
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


@register_verb("mutate", types=[DataFrameGroupBy])
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
    """Verb: Add the cardinality of a row's group to the row as column 'count'
    """
    from .base import dppd

    with dppd(df) as (dp, X):
        return dp.mutate(count=len).pd


@register_verb("summarize", types=[pd.DataFrame, DataFrameGroupBy])
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
                for (g, i) in zip(groups, idx):
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

    value_vars = parse_column_specification(
        df.columns, value_var_column_spec, return_list=True
    )
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
    key = parse_column_specification(df.columns, key, return_list=True)
    if len(key) > 1:
        raise ValueError("key must be a single column")
    value = parse_column_specification(df.columns, value, return_list=True)
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

    columns = parse_column_specification(df.columns, column_spec, return_list=True)
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

    column = parse_column_specification(df.columns, column, return_list=True)
    if len(column) != 1:
        raise ValueError("Must pass in exactly one column")
    s = df[column[0]].str.split(sep, expand=True)
    s.columns = new_names
    s.index = df.index
    if remove:
        df = df.drop(column, axis=1)
    result = pd.concat([df, s], axis=1)
    return result


@register_verb("print", types=[pd.DataFrame, pd.Series])
def print_DataFrame(df):
    print(df)
    return df


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
    cols_plus_inversed = parse_column_specification(
        df.columns, column_spec, return_list=2
    )
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

    cols_plus_inversed = parse_column_specification(
        df.columns, column_spec, return_list=2
    )
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


@register_verb("astype", types=pd.DataFrame)
def astype_DataFrame(df, columns, dtype, **kwargs):
    columns = parse_column_specification(df.columns, columns, return_list=True)
    return df.assign(**{x: df[x].astype(dtype, **kwargs) for x in columns})


# dply aliases
alias_verb("define", "mutate")
alias_verb("transmutate", "transassign")
alias_verb("define", "mutate")
alias_verb("summarise", "summarize")
