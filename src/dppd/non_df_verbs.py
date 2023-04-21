from .base import register_verb  # , register_type_methods_as_verbs
import pandas as pd
import collections


@register_verb(name="to_frame", types=collections.Counter)
def collection_counter_to_df(counter, key_name="key", count_name="counts"):
    """Turn a collections.Counter into a DataFrame
    with two columns: key & count
    """
    return pd.DataFrame({key_name: list(counter.keys()), count_name: list(counter.values())})
