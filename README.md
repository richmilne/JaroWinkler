JaroWinkler
===========

Original, standard and customisable versions of the Jaro-Winkler functions.

<pre>
>>> import jaro
>>> jaro.jaro_winkler_metric(u'SHACKLEFORD', u'SHACKELFORD')
0.9818181
>>> help(jaro)

Help on package jaro:

<strong>NAME</strong>
    jaro - Python translation of the original Jaro-Winkler functions.`

<strong>DESCRIPTION</strong>
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

<strong>PACKAGE CONTENTS</strong>
   ...
   jaro
   strcmp95
   ...

<strong>FUNCTIONS</strong>
    <strong>jaro_metric</strong>(string1, string2)
        The standard, basic Jaro string metric.

    <strong>jaro_winkler_metric</strong>(string1, string2)
        The Jaro metric adjusted with Winkler's modification, which boosts
        the metric for strings whose prefixes match.

    <strong>original_metric</strong>(string1, string2)
        The same metric that would be returned from the reference Jaro-Winkler
        C code, taking as it does into account a typo table and adjustments for
        longer strings.
        ...

    <strong>custom_metric</strong>(string1, string2, typo_table, typo_scale,
                               boost_threshold, pre_len, pre_scale, longer_prob)
        Calculate the Jaro-Winkler metric with parameters of your own choosing.
        ...
</pre>