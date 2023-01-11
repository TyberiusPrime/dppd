import re
import pandas as pd
import numpy as np


def series_and_strings_to_names(columns):
    return [x.name if isinstance(x, pd.Series) else x for x in columns]


def _parse_column_spec_return_from_bool_vector(df_columns, vector, return_list):
    if return_list is True:
        return list(df_columns[vector])
    elif return_list == 2:
        return [(x, False) for x in df_columns[vector]]
    else:
        return vector


def _parse_column_spec_regexps_search_single_level(df_columns, regexps_list):
    chosen = np.zeros(len(df_columns), bool)
    for r in regexps_list:  #
        r = re.compile(r)
        for ii, c in enumerate(df_columns):
            if r.search(c):
                chosen[ii] = True
    return chosen


def _parse_column_spec_regexps_search_multiple_levels(df_columns, regexps_list):
    level_count = len(df_columns.levels)
    while len(regexps_list) < level_count:
        regexps_list.append(None)

    chosen = np.zeros(
        (
            len(df_columns),
            level_count,
        ),
        bool,
    )
    for ii in range(0, level_count):
        rr = regexps_list[ii]
        if rr is None:
            chosen[:, ii] = True
        else:
            rr = re.compile(rr)
            for yy, c in enumerate(df_columns):
                if rr.search(c[ii]):
                    chosen[yy, ii] = True
    return chosen.all(axis=1)


def _parse_column_spec_from_strings(df_columns, column_spec, return_list):
    if len(column_spec) == 0:
        return _parse_column_spec_return_from_bool_vector(
            df_columns, np.zeros(len(df_columns), bool), return_list
        )

    ordered = []
    forward_seen = False
    inverse_seen = False
    true_seen = False
    for c in column_spec:
        if c is True:
            for oc in df_columns:
                if not (oc, True) in ordered and not (oc, False) in ordered:
                    ordered.append((oc, False))
            true_seen = True
            break  # everything beyond the True is ignored
        if c in df_columns:
            if isinstance(c, str) and c[0] == "-" and c[1:] in df_columns:
                raise ValueError(
                    f"There is both a column {c[1:]} and {c} - cowardly refusing to interpret"
                )
            ordered.append((c, False))
            forward_seen = True
        else:
            if (
                c and isinstance(c, str) and c[0] == "-" and c[1:] in df_columns
            ):  # an empty column name is valid pandas!
                ordered.append((c[1:], True))
                inverse_seen = True
            else:
                raise KeyError(f"Column not found {c}")
    if return_list == 2:
        return ordered
    else:
        if forward_seen and inverse_seen and not true_seen:
            raise ValueError(
                "Must not mix normal and inversed (-column_name) specification"
            )
        elif forward_seen:
            if return_list:
                return [x[0] for x in ordered if not x[1]]
            else:
                return df_columns.isin(column_spec)
        elif inverse_seen:
            res = ~df_columns.isin([c[1:] for c in column_spec])
            if return_list:
                return list(df_columns[res])
            else:
                return res
        elif true_seen:  # query was [True]
            return sorted(df_columns)
        else:  # pragma: no cover
            raise ValueError("This else should not be reached")


def parse_column_specification(df, column_spec, return_list=False):
    """Parse a column specification


    Parameters
    ----------
        column_spec : various
            * str, [str] - select columns by name, (always returns an DataFrame, never a Series)
            * [b, a, -c, True] - select b, a (by name, in order) drop c, then add everything else in alphabetical order
            * pd.Series / np.ndarray, dtype == bool: select columns matching this bool vector, example: ``select(X.name.str.startswith('c'))``
            * pd.Series, [pd.Series] - select columns by series.name
            * "-column_name" or ["-column_name1","-column_name2"]: drop all other columns (or invert search order in arrange)
            * pd.Index - interpreted as a list of column names - example: select(X.select_dtypes(int).columns)
            * (regexps_str, ) tuple - run re.search() on each column name
            * (regexps_str, None, regexps_str ) tuple - run re.search() on each level of the column names. Logical and (like DataFrame.xs but more so).
            * {level: regexs_str,...) - re.search on these levels (logical and)
            * a callable f, which takes a string column name and returns a bool whether to include the column.
            * a type, in which case the request will be forwarded to pandas.DataFrame.select_dtypes(include=...)). Example: numpy.number
            * None -> all columns

        return_list : int
            * If return_list is falsiy, return a boolean vector.
            * If return_list is True, return a list of columns, either in input order (if available), or in df_columns order if not.
            * if return_list is 2, return (forward_list, reverse_list) if input was a list, other wise see 'return_list is True'

    """
    result = None
    df_columns = df.columns
    # the easy cases
    if column_spec is None:
        if return_list:
            return df_columns
        else:
            return np.array([True] * len(df.columns), dtype=bool)
    elif (
        isinstance(column_spec, pd.Series) or isinstance(column_spec, np.ndarray)
    ) and column_spec.dtype == bool:
        result = column_spec
    elif isinstance(column_spec, tuple):
        if not hasattr(df_columns, "levels"):
            if len(column_spec) > 1:
                raise ValueError(
                    "DataFrame has no levels on it's columns, but you passed in more than one regexps"
                )
            result = _parse_column_spec_regexps_search_single_level(
                df_columns, column_spec
            )
        else:
            result = _parse_column_spec_regexps_search_multiple_levels(
                df_columns, list(column_spec)
            )
    elif isinstance(column_spec, dict):
        if not hasattr(df_columns, "levels"):
            raise ValueError(
                "DataFrame has no levels on it's columns. Perhaps you meant select_and_rename?"
            )
        for k in column_spec:
            if not k in df_columns.names:
                raise KeyError(
                    f"{k} not in DataFrame.columns.names. Available {df_columns.names}"
                )
        # reuse the tuple engine
        search_tuple = []
        for k in df_columns.names:
            search_tuple.append(column_spec.get(k, None))
        result = _parse_column_spec_regexps_search_multiple_levels(
            df_columns, list(search_tuple)
        )

    elif isinstance(column_spec, type):
        ok = df.select_dtypes(column_spec).columns
        result = np.array([c in ok for c in df_columns], bool)
    elif callable(column_spec):
        result = np.array([column_spec(c) for c in df_columns], bool)
    if result is not None:
        return _parse_column_spec_return_from_bool_vector(
            df_columns, result, return_list
        )

    # now prepropcess into constant format
    if isinstance(column_spec, str):
        column_spec = [column_spec]
    elif isinstance(column_spec, pd.Index):
        column_spec = list(column_spec)
    elif isinstance(column_spec, pd.Series):
        column_spec = [column_spec.name]
    if isinstance(column_spec, list):
        column_spec = series_and_strings_to_names(column_spec)
        return _parse_column_spec_from_strings(df_columns, column_spec, return_list)

    else:
        raise ValueError(
            "Could not understand column definition, type was %s" % (type(column_spec))
        )
