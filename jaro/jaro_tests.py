import os
import sys
import math

# The basis of these tests taken from:
# http://alias-i.com/lingpipe/docs/api/com/aliasi/spell/JaroWinklerDistance.html
#
# That page is the discussion of the method and the Java class. The actual tests
# are found in the source code, which I was able to download from
# http://alias-i.com/lingpipe/web/downloadJarOrDistro.html
#
# Once downloaded, the test class was found in
# /lingpipe-4.1.0/src/com/aliasi/test/unit/spell/JaroWinklerDistanceTest.java

#                          +-- Number of matches
#                          |  +-- Number of half transpositions
#                          |  |  +-- Jaro metric
#                          |  |  |        +-- Winkler metric
#                          |  |  |        |        +-- Metric calculated by
#                          v  v  v        v        v   original reference C code
jaro_tests = r"""
SHACKLEFORD  SHACKELFORD  11  2  0.96970  0.98182  0.98864
DUNNINGHAM   CUNNIGHAM     8  0  0.89630  0.89630  0.93086
NICHLESON    NICHULSON     8  0  0.92593  0.95556  0.97667
JONES        JOHNSON       4  0  0.79048  0.83238  0.87383
MASSEY       MASSIE        5  0  0.88889  0.93333  0.95333
ABROMS       ABRAMS        5  0  0.88889  0.92222  0.95236
HARDIN       MARTINEZ      4  0  0.72222  0.72222  0.77431
ITMAN        SMITH         1  0  0.46667  0.46667  0.50667

JERALDINE    GERALDINE     8  0  0.92593  0.92593  0.96630
MARTHA       MARHTA        6  2  0.94444  0.96111  0.97083
MICHELLE     MICHAEL       6  0  0.86905  0.92143  0.94444
JULIES       JULIUS        5  0  0.88889  0.93333  0.95333
TANYA        TONYA         4  0  0.86667  0.88000  0.93280
DWAYNE       DUANE         4  0  0.82222  0.84000  0.89609
SEAN         SUSAN         3  0  0.78333  0.80500  0.84550
JON          JOHN          3  0  0.91667  0.93333  0.93333
JON          JAN           2  0  0.77778  0.80000  0.86000

DWAYNE       DYUANE        5  2  0.82222  0.84000  0.90250
CRATE        TRACE         3  0  0.73333  0.73333  0.77778
WIBBELLY     WOBRELBLY     7  3  0.83664  0.85298  0.91122
DIXON        DICKSONX      4  0  0.76667  0.81333  0.85394
MARHTA       MARTHA        6  2  0.94444  0.96111  0.97083
AL           AL            2  0  1.00000  1.00000  1.00000
aaaaaabc     aaaaaabd      7  0  0.91667  0.95000  0.96000

ABCVWXYZ     CABVWXYZ      8  3  0.95833  0.95833  0.97454
ABCAWXYZ     BCAWXYZ       7  3  0.91071  0.91071  0.94223
ABCVWXYZ     CBAWXYZ       7  2  0.91071  0.91071  0.94223
ABCDUVWXYZ   DABCUVWXYZ   10  4  0.93333  0.93333  0.96061
ABCDUVWXYZ   DBCAUVWXYZ   10  2  0.96667  0.96667  0.98030
ABBBUVWXYZ   BBBAUVWXYZ   10  2  0.96667  0.96667  0.98030
ABCDUV11lLZ  DBCAUVWXYZ    7  2  0.73117  0.73117  0.80130
ABBBUVWXYZ   BBB11L3VWXZ   7  0  0.77879  0.77879  0.83650

-            -             0  0  1.00000  1.00000  1.00000
A            A             1  0  1.00000  1.00000  1.00000
AB           AB            2  0  1.00000  1.00000  1.00000
ABC          ABC           3  0  1.00000  1.00000  1.00000
ABCD         ABCD          4  0  1.00000  1.00000  1.00000
ABCDE        ABCDE         5  0  1.00000  1.00000  1.00000
AA           AA            2  0  1.00000  1.00000  1.00000
AAA          AAA           3  0  1.00000  1.00000  1.00000
AAAA         AAAA          4  0  1.00000  1.00000  1.00000
AAAAA        AAAAA         5  0  1.00000  1.00000  1.00000

A            B             0  0  0.00000  0.00000  0.00000
-            ABC           0  0  0.00000  0.00000  0.00000
ABCD         -             0  0  0.00000  0.00000  0.00000
--           -             0  0  0.00000  0.00000  0.00000
--           ---           1  0  0.83333  0.83333  0.83333
"""
# We use hyphens to encode null strings and spaces.
# A sequence of n hyphens represents a string of (n-1) spaces.

# http://richardminerich.com/tag/jaro-winkler/
# http://richardminerich.com/2011/09/record-linkage-algorithms-in-f-jaro-winkler-distance-part-1/

# http://richardminerich.com/2011/09/record-linkage-in-f-token-matching-stable-marriages-and-the-gale-shapley-algorithm/
# http://en.wikipedia.org/wiki/Stable_marriage_problem [Gale Shapely]

# https://github.com/NaturalNode/natural/blob/master/lib/natural/distance/jaro-winkler_distance.js
# http://www.gettingcirrius.com/2011/01/calculating-similarity-part-2-jaccard.html

def parse_tests(rstring):

    tests = []
    lines = [l.rstrip() for l in rstring.split('\n')]

    for line in lines:
        if not line.strip(): continue

        bits = line.split()
        assert len(bits) == 7
        s1, s2, m, t, jaro, wink, orig = bits

        m, t = [int(v) for v in [m, t]]

        strings = []
        for string in [s1, s2]:
            if string[0] == '-':
                assert set(string) == set(['-'])
                string = ' ' * (len(string)-1)
            # string = string.decode('utf8')
            strings.append(string)
        s1, s2 = strings

        # print s1, s2, m, t, jaro, wink, matches
        tests.append((s1, s2, m, t, jaro, wink, orig))

    return tests


jaro_tests = parse_tests(jaro_tests)


def gen_test_args(test_tuples):

    for tup in test_tuples:
        arg1, arg2 = tup[:2]

        strings1 = set([arg1, arg1.lower(), arg1.upper()])
        strings2 = set([arg2, arg2.lower(), arg2.upper()])

        for larger_tol in [False, True]:
            for to_upper in [False, True]:
                for s1 in strings1:
                    for s2 in strings2:
                        yield larger_tol, to_upper, s1, s2


def test():
    from . import jaro

    for test in jaro_tests:
        # s1, s2, m, t, jaro, wink = test
        s1, s2 = test[:2]

        string_metrics = jaro.string_metrics(s1, s2)
        (len1, len2, num_matches, half_transposes,
                          typo_score, pre_matches, adjust_long) = string_metrics

        weight_jaro = jaro.metric_jaro(s1, s2)
        weight_winkler = jaro.metric_jaro_winkler(s1, s2)
        weight_original = jaro.metric_original(s1, s2)
        # TODO: Test for the custom function?

        weights = [weight_jaro, weight_winkler, weight_original]

        check = [num_matches, half_transposes]
        check.extend(['%7.5f' % w for w in weights])

        if check != list(test[2:]):
            print()
            print(s1, s2)
            print(check)
            print(test[2:])
            raise AssertionError

        strings = []
        for s in [s1, s2]:
            if s.strip() == '':
                s = '-'*(len(s)+1)
            strings.append(s.ljust(12))
        for n in [num_matches, half_transposes]:
            strings.append(str(n).rjust(2))
        for w in weights:
            strings.append(' %7.5f' % w)

        print(' '.join(strings))

if __name__ == '__main__':
    test()