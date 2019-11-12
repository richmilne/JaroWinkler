#! /usr/bin/env python
# coding: utf8

import os
import sys
from .typo_tables import adjwt

def fn_jaro(len1, len2, num_matches, half_transposes, typo_score, typo_scale):
    """Calculate the classic Jaro metric between two strings.

    The strings have lengths 'len1' and 'len2'. 'num_matches' and
    'half_transposes' are the output of the count_matches() and
    count_half_tranpositions() functions.

    'typo_score' is an optional argument, produced by the count_typos()
    function if you decide to check the strings for typos with a given
    typographical mapping. The typo score will be scaled by 'typo_scale'
    before being used."""

    if not len1:
        if not len2: return 1.0
        return 0.0
    if not num_matches: return 0.0

    similar = (typo_score / typo_scale) + num_matches
    weight = (  similar / len1
              + similar / len2
              + (num_matches - half_transposes//2) / num_matches)

    return weight / 3

def fn_winkler(weight_jaro, pre_matches, pre_scale):
    """
    Scale the standard Jaro metric by 'pre_scale' units per 'pre_matches'.

    Note the warning in the docstring of jaro_winkler() regarding the scale.
    """
    weight_jaro += pre_matches * pre_scale * (1.0 - weight_jaro)
    assert weight_jaro <= 1.0
    return weight_jaro

def fn_longer(weight, len1, len2, num_matches, pre_matches):
    num = num_matches - pre_matches - 1
    den = len1 + len2 - 2*pre_matches + 2
    num = (1.0 - weight) * num
    return weight + (num / den)

def count_matches(s1, s2, len1, len2):
    """
    For every character in string s1, count the number of characters in
    string s2 which match, within a given range.

    len1 and len2 are the pre-calculated lengths of string s1 and s2
    respectively. s1 must be the shorter string.

    The function returns the count of matched characters, and two bit arrays
    showing which characters in each string this function managed to match
    up."""
    # If you want to know which characters matched where, un-comment the lines
    # involving the 'where_matched' variable below.
    assert len1 and len1 <= len2
    search_range = max(len2//2-1, 0)
    num_matches = 0

    # Bit arrays to mark which chars in the strings have already matched
    flags1 = [0]*len1
    flags2 = [0]*len2
    # where_matched = [-1]*len1

    # Looking only within the search range, count and flag the matched pairs.
    for i, char in enumerate(s1):
        lolim = max(i - search_range, 0)
        hilim = min(i + search_range, len2 - 1)
        for j in range(lolim, hilim + 1):
            if not flags2[j] and char == s2[j]:
                flags1[i] = flags2[j] = 1
                # where_matched[i] = j
                num_matches += 1
                break

    return num_matches, flags1, flags2#, where_matched

def count_half_transpositions(s1, s2, flags1, flags2):
    """Count the number of half transpositions between two strings.

    A half transposition, roughly defined, is two characters, taken from the
    sequence of paired matched chars, which are unequal to each other.

    The arguments 'flags1' and 'flags2' are the bit arrays produced by the
    count_matches() function."""
    half_transposes = 0
    k = 0

    for i, flag in enumerate(flags1):
        if not flag: continue
        # Iterate through every matched char in the first string.

        # For every char in the first string, we look for the next matched
        # char in second string (starting from where we left off last, k).
        while not flags2[k]: k += 1

        # Once we've found two matched chars, we compare them. If they're not
        # equal, it counts as a transposition.
        if s1[i] != s2[k]:
            half_transposes += 1
        k += 1

    return half_transposes

def count_typos(s1, s2, flags1, flags2, typo_table):
    """
    Check unmatched characters in strings 's1' and 's2' for typos.

    The typos (or known phonetic or character recognition errors) are
    defined in the 'typo_table' argument, which defines the mapping between
    similar characters, and a score to assign to each. [See the
    typo_tables.py module].

    The function returns the total typo score, and updates the 'field2' bit
    array to mark which characters were adjudged similar.
    """
    assert 0 in flags1
    # Only call this routine if the smallest string still has some unmatched
    # characters.

    typo_score = 0
    for i, flag1 in enumerate(flags1):
        if flag1: continue          # Iterate through unmatched chars
        row = s1[i]
        if row not in typo_table:
            # If we don't have a similarity mapping for the char, continue
            continue
        typo_row = typo_table[row]

        # Now look through all the unmatched chars in the second string to
        # see if we can find a char similar to the first.
        for j, flag2 in enumerate(flags2):
            if flag2: continue
            col = s2[j]
            if col not in typo_row: continue

            # print 'Similarity!', row, col
            typo_score += typo_row[col]
            flags2[j] = 2
            break

    return typo_score, flags2

def string_metrics(s1, s2, typo_table=None, typo_scale=1, boost_threshold=None,
                   pre_len=0, pre_scale=0, longer_prob=False):
    """
    Calculate the string params and flags required by Jaro Winkler routines.

    For more detail of what the various arguments to this function mean and
    do, see the metric_custom() function.
    """
    # Defaults are chosen to do least work necessary to get the valuesfor the
    # Jaro metric.
    assert isinstance(s1, str)
    assert isinstance(s2, str)
    assert typo_scale > 0
    assert boost_threshold is None or boost_threshold > 0
    assert pre_len >= 0
    assert 1 >= pre_scale >= 0

    len1 = len(s1)
    len2 = len(s2)

    if len2 < len1:
        s1, s2 = s2, s1
        len1, len2 = len2, len1
    assert len1 <= len2

    if not (len1 and len2): return len1, len2, 0, 0, 0, 0, False

    num_matches, flags1, flags2 = count_matches(s1, s2, len1, len2)

    # If no characters in common - return
    if not num_matches: return len1, len2, 0, 0, 0, 0, False

    half_transposes = count_half_transpositions(s1, s2, flags1, flags2)

    # adjust for similarities in non-matched characters
    typo_score = 0
    if typo_table and len1 > num_matches:
        typo_score, flags2 = count_typos(s1, s2, flags1, flags2, typo_table)

    if not boost_threshold:
        return len1, len2, num_matches, half_transposes, typo_score, 0, 0

    pre_matches = 0
    adjust_long = False
    weight_typo = fn_jaro(len1, len2, num_matches, half_transposes,
                                                         typo_score, typo_scale)

    # Continue to boost the weight if the strings are similar
    if weight_typo > boost_threshold:
        # Adjust for having up to first 'pre_len' chars (not digits) in common
        limit = min(len1, pre_len)
        while pre_matches < limit:
            char1 = s1[pre_matches]
            if not( char1.isalpha() and char1 == s2[pre_matches] ):
                break
            pre_matches += 1

        # Optionally adjust for long strings.
        # After agreeing beginning chars, at least two more must agree and the
        # agreeing characters must be more than half of remaining characters.
        if longer_prob:
            cond = len1 > pre_len
            cond = cond and num_matches > pre_matches + 1
            cond = cond and 2 * num_matches >= len1 + pre_matches
            cond = cond and s1[0].isalpha()
            if cond:
                adjust_long = True

    return (len1, len2, num_matches, half_transposes,
                typo_score, pre_matches, adjust_long)

def metric_jaro(string1, string2):
    "The standard, basic Jaro string metric."

    ans = string_metrics(string1, string2)
    len1, len2, num_matches, half_transposes = ans[:4]
    assert ans[4:] == (0, 0, False)

    return fn_jaro(len1, len2, num_matches, half_transposes, 0, 1)

def metric_jaro_winkler(string1, string2):
    """The Jaro metric adjusted with Winkler's modification, which boosts
    the metric for strings whose prefixes match."""

    pre_scale = 0.1

    ans = string_metrics(string1, string2,
                             boost_threshold=0.7, pre_len=4,
                                # typo_table=adjwt, typo_scale=type_scale,
                                     pre_scale=pre_scale, longer_prob=False)

    (len1, len2, num_matches, half_transposes,
                                     typo_score, pre_matches, adjust_long) = ans
    assert typo_score == int(adjust_long) == 0

    weight_jaro = fn_jaro(len1, len2, num_matches, half_transposes, 0, 1)
    return fn_winkler(weight_jaro, pre_matches, pre_scale)

def metric_original(string1, string2):
    """The same metric that would be returned from the reference Jaro-Winkler
    C code, taking as it does into account a typo table and adjustments for
    longer strings.

    This function uses the original table from the reference C code
    ('adjwt'), which contained only ASCII capital letters and numbers. If
    you want to adjust for lower case letters and different character sets,
    you need to define your own table. See the typo_tables.py module for
    more detail."""
    pre_scale = 0.1
    typo_scale = 10

    ans = string_metrics(string1, string2,
                             boost_threshold=0.7, pre_len=4,
                                typo_table=adjwt, typo_scale=typo_scale,
                                     pre_scale=pre_scale, longer_prob=True)

    (len1, len2, num_matches, half_transposes,
                                     typo_score, pre_matches, adjust_long) = ans

    weight_typo = fn_jaro(len1, len2, num_matches, half_transposes,
                                                         typo_score, typo_scale)
    weight_longer = fn_winkler(weight_typo, pre_matches, pre_scale)

    if adjust_long:
        weight_longer = fn_longer(weight_longer, len1, len2,
                                                       num_matches, pre_matches)

    return weight_longer

def metric_custom(string1, string2, typo_table, typo_scale,
                              boost_threshold, pre_len, pre_scale, longer_prob):
    """
    Calculate the Jaro-Winkler metric with parameters of your own choosing.

    If you'd like to check your strings for typos, pass in a typo_table
    arg. Any similar, but unmatched, chars from your strings in this table
    will be used to proportionally (divided by typo_scale) increase the
    count of matched chars between your strings.

    If 'pre_len' is non-zero, the metric calculated will be boosted when the
    first alpha chars, out of the first 'pre_len' chars of the strings,
    match. The metric is adjusted up by 'pre_scale' for every matching char
    [see fn_winkler()].

    Take care that 'pre_scale' is no larger than 1 / 'pre_len', otherwise
    the distance can become larger than 1.

    The 'longer' flag tells the functions to make a further adjustment to
    the distance if the strings have a longer prefix in common."""
    ans = string_metrics(string1, string2,
                            typo_table, typo_scale,
                                boost_threshold, pre_len,
                                    pre_scale, longer_prob)

    (len1, len2, num_matches, half_transposes,
                                     typo_score, pre_matches, adjust_long) = ans

    weight_typo = fn_jaro(len1, len2, num_matches, half_transposes,
                                                         typo_score, typo_scale)
    weight_winkler_typo = fn_winkler(weight_typo, pre_matches, pre_scale)
    weight_longer = weight_winkler_typo
    if adjust_long:
        weight_longer = fn_longer(weight_longer, len1, len2,
                                                       num_matches, pre_matches)

    return weight_longer

if __name__ == '__main__':

    # print metric_custom('abc', 'cba', adjwt, 10, 0.7, 4, 0.1, True)

    if len(sys.argv) < 3:
        sys.exit()

    # s1, s2 = [s.decode('utf8') for s in sys.argv[1:3]]
    s1, s2 = sys.argv[1:3]
    print('Jaro: %7.5f, Jaro-Winkler: %7.5f, Original: %7.5f.' % (
      metric_jaro(s1, s2), metric_jaro_winkler(s1, s2), metric_original(s1, s2)))