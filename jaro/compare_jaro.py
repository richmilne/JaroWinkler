import os
import sys
from . import jaro
from . import strcmp95

from .typo_tables import adjwt
from .jaro_tests import gen_test_args, jaro_tests
from .jaro import fn_jaro, fn_winkler, fn_longer, string_metrics

def all_metrics(string1, string2, longer_prob):

    pre_scale = 0.1
    typo_scale = 10

    ans = string_metrics(string1, string2,
                            boost_threshold=0.7, pre_len=4,
                               typo_table=adjwt, typo_scale=typo_scale,
                                  pre_scale=pre_scale, longer_prob=longer_prob)

    (len1, len2, num_matches, half_transposes,
                                     typo_score, pre_matches, adjust_long) = ans
    assert not (longer_prob or adjust_long) or longer_prob

    weight_jaro = fn_jaro(len1, len2, num_matches, half_transposes, 0, 1)
    weight_typo = fn_jaro(len1, len2, num_matches, half_transposes,
                                                         typo_score, typo_scale)
    weight_winkler = fn_winkler(weight_jaro, pre_matches, pre_scale)
    weight_winkler_typo = fn_winkler(weight_typo, pre_matches, pre_scale)
    weight_longer = weight_winkler_typo

    if adjust_long:
        weight_longer = fn_longer(weight_longer, len1, len2,
                                                       num_matches, pre_matches)

    return (len1, len2, num_matches, half_transposes,
                typo_score, pre_matches, adjust_long,
                    weight_jaro, weight_typo, weight_winkler,
                        weight_winkler_typo, weight_longer)

def compare(string1, string2, larger_tol):

    # strcmp95 always trims input, so we have to do the same for our tests
    s1, s2 = [s.strip() for s in [string1, string2]]
    if s1 == s2 == '': return

    ans1 = strcmp95.strcmp95(string1, string2, larger_tol, to_upper=0, debug=0)
    ans2 = all_metrics(s1, s2, longer_prob=larger_tol)

    weights = ans2[-5:]

    rearrange = ans1[:2]!=ans2[:2] and ans1[0]==ans2[1] and ans1[1]==ans2[0]
    check = ((rearrange and ans1[2:] == ans2[2:]) or
                                           (not rearrange and ans1 == ans2))

    # print ('-->', s1, s2, larger_tol, rearrange, check)
    if not check:
        print(rearrange)
        for a1, a2 in zip(ans1, ans2):
            print(str(a1==a2).ljust(5), a1, a2)
        print(ans1)
        print(ans2)
    assert check

    (weight_jaro, weight_typo, weight_winkler,
                                   weight_winkler_typo, weight_longer) = weights

    assert weight_jaro == jaro.metric_jaro(s1, s2)
    assert weight_winkler == jaro.metric_jaro_winkler(s1, s2)

    check_original = jaro.metric_original(s1, s2)
    if larger_tol:
        assert weight_longer == check_original
    else:
        assert weight_longer == weight_winkler_typo

def test():
    for larger_tol, to_upper, s1, s2 in gen_test_args(jaro_tests):
        compare(s1, s2, larger_tol)

if __name__ == '__main__':
    test()