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

    def __init__(self, name=None, types=None, pass_dppd=False):
        """
        Parameters:
        -----------
            names : str, list or None
                May be omitted, then it get's set to the functions __name__.
                If it's a list, register aliases right away
                Must be a valid identifer.
            types : type or [type, type,...]
                this verb only applies to these types
            pass_dppd:
                this func will get dppd instead of dppd.df (e.g. for dir)
    """
        self.names = name
        if not isinstance(types, list):
            types = [types]
        self.types = types
        for t in types:
            dppd_types.add(t)
            if not t in property_registry:
                property_registry[t] = set()
        self.pass_dppd = pass_dppd

    def __call__(self, func):
        if self.names is None:
            real_names = [func.__name__]
        else:
            if not isinstance(self.names, list):
                real_names = [self.names]
            else:
                real_names = self.names

        def outer(dppd):
            def inner(*args, **kwargs):
                if self.pass_dppd:
                    result = func(dppd, *args, **kwargs)
                else:
                    result = func(dppd.df, *args, **kwargs)
                # no verbs:
                if type(result) in dppd_types:
                    return dppd._descend(result)
                else:
                    return result

            return inner

        for real_name in real_names:
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

            outer.__doc__ == func.__doc__
            for t in self.types:
                verb_registry[real_name, t] = outer
        return func


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
            if not df_method.startswith("_"):
                try:
                    attr = getattr(cls, df_method)
                    if hasattr(attr, "__call__"):
                        register_verb(df_method, types=cls)(attr)
                    else:
                        register_property(df_method, types=cls)
                except AttributeError as e:  # pragma: no cover
                    # this happens in pandas < 0.23 for DataFrame.columns
                    if "'NoneType' object has no attribute '_data'" in str(e):
                        register_property(df_method, types=cls)
                    else:
                        # just a defensive measure
                        raise  # pragma: no cover


class Dppd:
    """
    Dataframe maniPulater maniPulates Dataframes

    A DataFrame manipulation object, offering verbs,
    and each verb returns another Dppd.

    All pandas.DataFrame methods have been turned into verbs.
    Accessors like loc also work.

    """

    def __init__(self, df, dppd_proxy, X, parent):
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
        self.parent = parent

    def _descend(self, new_df, parent=None):
        if new_df is None:
            raise ValueError()
        return Dppd(
            new_df,
            self._dppd_proxy,
            self.X,
            parent if parent is not None else self.parent,
        )

    @property
    def pd(self):
        """Return the actual, unproxyied DataFrame"""
        result = self.df
        if self.parent is not None:
            self._dppd_proxy._self_update_wrapped(self.parent)
            self.X._self_update_wrapped(self.parent.df)
        return result

    def __call__(self, df=None):
        if df is None:
            if self.df is None:
                raise ValueError("You have to call dp(df) before calling dp()")
            return self
        else:
            last = self._dppd_proxy._get_wrapped()
            return self._descend(df, parent=last)

    def __getattr__(self, attr):
        if attr == "__qualname__":  # pragma: no cover
            raise AttributeError(
                "%s object has no attribute '__qualname__'" % (type(self))
            )
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

    def __dir__(self):
        result = set()
        my_typ = type(self.df)
        for name, typ in verb_registry.keys():
            if typ is None or typ is my_typ:
                result.add(name)
        for name in property_registry[my_typ]:
            result.add(name)
        return sorted(result)


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
            return res.pd
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
        self.dppd = Dppd(self.df, self.__dppd_proxy, self.__X_proxy, None)

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
