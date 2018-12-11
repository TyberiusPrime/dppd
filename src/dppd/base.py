import pandas as pd
import warnings
import wrapt

verb_registry = {}
property_registry = {}
dppd_types = set([None])  # which types are handled by dppd, others drop out of the pipe


class register_verb:
    """Register a function to act as a Dppd verb.
    First parameter of the function must be the DataFrame being worked on.
    Note that for grouped Dppds, the function get's called once per group.

    Example::

        register_verb('upper_case_all_columns')(
            lambda df: df.assign(**{
                name: df[name].str.upper() for name in df.columns})


    """

    def __init__(self, name=None, types=None):
        """
        Parameters:
        -----------
            name : str or None
                Must be a valid identifer.
                May be omitted, then it get's set to the functions __name__.
            types : type or [type, type,...]
                this verb only applies to these types
            full_replacement : bool
                This verb will do a full replacement of the DataFrame,
                and will be called as verb(df, dppd._groups),
                where dppd._groups is either None, or a tuple (sort_before_grouping (bool),
                group columns [str,...]

            pass_group_key : bool
                if True, the function get's passed a named paramater group_key
                which is a tuple with the current grouping variables.
                Basically, x[0] for x in df.groupby(...) per call

            pass_complete_df :
                This verb will not be called per group,
                but with the complete df.
                Mostly an optimization for select, drop etc.

    """
        self.name = name
        if not isinstance(types, list):
            types = [types]
        self.types = types
        for t in types:
            dppd_types.add(t)

    def __call__(self, func):
        if self.name is None:
            real_name = func.__name__
        else:
            real_name = self.name
        if not real_name.isidentifier():
            raise TypeError(
                "name passed to register_verb must be a valid python identifier"
            )
        for t in self.types:
            if (real_name, t) in verb_registry and verb_registry[
                (real_name, t)
            ] != func:
                warnings.warn(f"redefining verb {real_name} for type {t}")
            if t in property_registry and real_name in property_registry[t]:
                warnings.warn(f"verb {real_name} shadows property for type {t}")

        def outer(dppd):
            def inner(*args, **kwargs):
                result = func(dppd.df, *args, **kwargs)
                # no verbs:
                if type(result) in dppd_types:
                    return dppd._descend(result)
                else:
                    return result

            return inner

        outer.__doc__ == func.__doc__
        for t in self.types:
            verb_registry[real_name, t] = outer
        return func


def alias_verb(new_name, old_name):
    """Alias one verb as another.

    """
    any_found = False
    for t in dppd_types:
        if (old_name, t) in verb_registry:
            if (new_name, t) in verb_registry and (
                verb_registry[old_name, t] != verb_registry[new_name, t]
            ):
                warnings.warn(f"Redefining {new_name} by alias")
            verb_registry[new_name, t] = verb_registry[old_name, t]
            any_found = True
    if not any_found:
        raise KeyError(f"Could not alias non existing verb {old_name}")


def register_property(name, types=None):
    """Register a property/indexed accessor to be forwarded (.something[])
    """
    if not isinstance(types, list):
        types = [types]
    for t in types:
        if (name, t) in verb_registry:
            warnings.warn("Property always shadowed by verb: %s" % name)
        if not t in property_registry:
            property_registry[t] = set()
        property_registry[t].add(name)
        dppd_types.add(t)


def register_type_methods_as_verbs(cls, excluded):
    for df_method in dir(cls):
        if df_method not in excluded:
            attr = getattr(cls, df_method)
            if not df_method.startswith("_"):
                if hasattr(attr, "__call__"):
                    register_verb(df_method, types=cls)(attr)
                else:
                    register_property(df_method, types=cls)


class Dppd:
    """
    Dataframe maniPulater maniPulates Dataframes

    A DataFrame manipulation object, offering verbs,
    and each verb returns another Dppd.

    All pandas.DataFrame methods have been turned into verbs.
    Accessors like loc also work.

    """

    def __init__(self, df, dppd_proxy, X):
        if isinstance(df, wrapt.ObjectProxy):
            df = df._get_wrapped()
        elif isinstance(df, Dppd):
            df = df.df
        if df is not None and type(df) not in dppd_types:

            raise ValueError(
                f"Dppd was passed a {type(df)} for which no properties have been registered. That sounds like a bug"
            )
        self.df = df
        self._dppd_proxy = dppd_proxy
        self.X = X  # the StackAwareDataframe proxy
        dppd_proxy._self_update_wrapped(self)
        self.X._self_update_wrapped(self.df)

    def _descend(self, new_df):
        if new_df is None:
            raise ValueError()
        return Dppd(new_df, self._dppd_proxy, self.X)

    @property
    def pd(self):
        """Return the actual, unproxyied DataFrame"""
        result = self.df
        return result

    def __call__(self, df=None):
        if df is None:
            if self.df is None:
                raise ValueError("You have to call dp(df) before calling dp()")
            return self
        else:
            return self._descend(df)

    def __getattr__(self, attr):
        if self.df is None:
            raise ValueError("Dppd not initialized with a DataFrame")
        if (attr, type(self.df)) in verb_registry:
            return verb_registry[attr, type(self.df)](self)
        elif (attr, None) in verb_registry:
            return verb_registry[attr, None](self)
        elif attr in property_registry[type(self.df)]:
            return GetItemProxy(getattr(self.df, attr), self)
        # if attr in property_registry[None]:
        # return GetItemProxy(getattr(self.df, attr), self)
        else:
            raise AttributeError(attr, type(self.df))

    def __getitem__(self, slice):
        return self._descend(self.df[slice])


class ReplacableProxy(wrapt.ObjectProxy):
    """A proxy that can change what it proxies for

   :autodoc_skip:
   """

    def _self_update_wrapped(self, w):
        self.__wrapped__ = w

    def _get_wrapped(self):
        return self.__wrapped__

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)

    @property
    def pd(self):
        res = self._get_wrapped()
        if isinstance(res, Dppd):
            return res.df
        else:
            return res


class DPPDAwareProxy(ReplacableProxy):
    """A replacable DataFrame proxy that also offers itergroups

   :autodoc_skip:
    """

    def __init__(self, wrapped, dppd_proxy):
        self._self_dppd_proxy = dppd_proxy
        super().__init__(wrapped)

    def itergroups(self):
        yield from self._self_dppd_proxy.itergroups()


class GetItemProxy(wrapt.ObjectProxy):
    """helper for accessor properties on DataFrames

   :autodoc_skip:
    """

    def __init__(self, wrapped, dppd):
        self._self_dppd = dppd
        super().__init__(wrapped)

    def __getitem__(self, slice):
        result = self.__wrapped__[slice]
        if isinstance(result, pd.DataFrame) or isinstance(result, pd.Series):
            return self._self_dppd._descend(result)
        else:
            return result

    @property
    def pd(self):
        return self.__wrapped__


class dppd:
    """Context manager for Dppd.

    Usage::

        ```
        with cdp(mtcars) as (dp, X):
            dp.groupby('cyl')
            dp.arrange(X.hp))
            dp.head(1)
        print(X)
        ```


    Both X and dp are a proxyied DataFrame after the context manager.
    They should work just like a DataFrame, use X.pd() to convert it into a true DataFrame.

    Alternate usage::

        dp, X = dppd()
        dp(df).mutate(y=X['column'] * 2, ...).filter(...).select(...).pd


    or::

        dp(df).mutate(...)
        dp.filter()
        dp.select()
        new_df = dp.pd
    """

    def __init__(self, df=None):
        self.df = df
        # So that dp() is always the lastes
        self.__dppd_proxy = ReplacableProxy(None)
        # and X is always the latest DataFrame.
        self.__X_proxy = DPPDAwareProxy(None, self.__dppd_proxy)
        self.dppd = Dppd(self.df, self.__dppd_proxy, self.__X_proxy)

    def __iter__(self):
        """Support to be able to say dp, X = dppd().
        hacky, but does work
        """
        # yield self.call_callback
        yield self.__dppd_proxy
        yield self.__X_proxy

    def __enter__(self):
        """Context manager support"""
        return (self.__dppd_proxy, self.__X_proxy)

    def __exit__(self, _type, _value, _traceback):
        # at midnight, both the carriage and the horses
        # turn back into (wrapped) DataFrames
        self.__X_proxy.__wrapped__ = self.__dppd_proxy.df
        self.__dppd_proxy.__wrapped__ = self.__dppd_proxy.df
        del self.df


all = [dppd, register_verb]
