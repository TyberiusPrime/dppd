from .base import register_verb  # , register_type_methods_as_verbs
import pandas as pd
import collections


@register_verb(name="to_frame", types=collections.Counter)
def collection_counter_to_df(counter):
    """Turn a collections.Counter into a DataFrame
    with two columns: key & count
    """
    return pd.DataFrame({"key": list(counter.keys()), "counts": list(counter.values())})
