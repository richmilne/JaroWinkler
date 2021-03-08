"""
Python translation of the original Jaro-Winkler functions.

The Jaro-Winkler functions compare two strings and return a score indicating
how closely the strings match. The score ranges from 0 (no match) to 1
(perfect match).

Two null strings ('') will compare as equal. Strings should be unicode
strings, and will be compared as given; the caller is responsible for
capitalisations and trimming leading/trailing spaces.

You should normally only need to use either the jaro_metric() or
jaro_winkler_metric() functions defined here. If you want to implement your
own, non-standard metrics, look at the comments and functions in the jaro.py
submodule.

The C-source code containing the original functions was found here:

http://web.archive.org/web/20100227020019/http://www.census.gov/geo/msb/stand/strcmp.c

This module should output exactly the same numbers as that code, for all
trimmed strings which can be represented in ASCII.

To help understand the code and comments in this module, see the Wikipedia
article

    http://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance

which links to the the Java LingPipe documentation

    http://alias-i.com/lingpipe/docs/api/com/aliasi/spell/JaroWinklerDistance.html

which expands on Wikipedia's explanation and provided the base of this
module's tests."""
from . import jaro
from . import typo_tables

def jaro_metric(string1, string2):
    return jaro.metric_jaro(string1, string2)
setattr(jaro_metric, '__doc__', jaro.metric_jaro.__doc__)

def jaro_winkler_metric(string1, string2):
    return jaro.metric_jaro_winkler(string1, string2)
setattr(jaro_winkler_metric, '__doc__', jaro.metric_jaro_winkler.__doc__)

def original_metric(string1, string2):
    return jaro.metric_original(string1, string2)
setattr(original_metric, '__doc__', jaro.metric_original.__doc__)

def custom_metric(string1, string2, typo_table, typo_scale,
                              boost_threshold, pre_len, pre_scale, longer_prob):
    return jaro.metric_custom(string1, string2, typo_table,
                   typo_scale, boost_threshold, pre_len, pre_scale, longer_prob)
setattr(custom_metric, '__doc__', jaro.metric_custom.__doc__)

def create_typo_table(typo_chars, score=3):
    return typo_tables.create_typo_table(typo_chars, score)
setattr(create_typo_table, '__doc__', typo_tables.create_typo_table.__doc__)

"""
jaro_metric = jaro.metric_jaro
# setattr(jaro_metric, '__doc__', jaro.jaro_metric.__doc__)

setattr(sys.modules[mod_name], 'new_function', typo_tables.create_typo_table)
"""