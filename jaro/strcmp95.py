#! /usr/bin/env python
# coding: utf8
import os
import sys

# Python translation of Jaro-Winkler code found here:
# http://web.archive.org/web/20100227020019/http://www.census.gov/geo/msb/stand/strcmp.c

# This will be the 'oracle', against which we test our re-written and
# re-factored Jaro-Winkler functions. We confirm separately that the output of
# this code exactly matches the output of the original C code.

#define NOTNUM(c)   ((c>57) || (c<48))
#define INRANGE(c)      ((c>0)  && (c<91))
NOTNUM = lambda c: c > 57 or c < 48
INRANGE = lambda c: c > 0 and c < 91
#define MAX_VAR_SIZE 61
#define NULL60 "                                                            "

# static  char    sp[39][2] =
sp_table = \
 ['A','E',  'A','I',  'A','O',  'A','U',  'B','V',  'E','I',  'E','O',  'E','U',
  'I','O',  'I','U',  'O','U',  'I','Y',  'E','Y',  'C','G',  'E','F',
  'W','U',  'W','V',  'X','K',  'S','Z',  'X','S',  'Q','C',  'U','V',
  'M','N',  'L','I',  'Q','O',  'P','R',  'I','J',  '2','Z',  '5','S',
  '8','B',  '1','I',  '1','L',  '0','O',  '0','Q',  'C','K',  'G','J',
# 'E',' ',  'Y',' ',  'S',' '
# Commented out because initialisation code only iterated through 36 pairs, and
# not 39. Hence these last 3 pairs were never used.
  ]

adjwt = []
for i in range(91):
    adjwt.append([0]*91)

for i in range(len(sp_table) // 2):
    i0 = sp_table[i*2]
    i1 = sp_table[i*2+1]
    # print "indices sp[%d][0]=%s, sp[%d][1]=%s" % (i, i0, i, i1)
    i0, i1 = ord(i0), ord(i1)
    # print "  adjwt[%d][%d]=3, adjwt[%d][%d]=3" % (i0, i1, i1, i0)
    adjwt[i0][i1] = 3
    adjwt[i1][i0] = 3

def print_adjwt_table():
    # We want to find the indices of the non-empty rows and cols in the adjwt
    # table. To do this, we sum the values in the rows and cols. If the value
    # is greater than 0, it's non-empty.

    # The table should be symmetrical, so we should only have to calculate the
    # row indices (the simplest calculation) but we'll leave the option for
    # asymmetry open.
    rows = []
    col_sums = [] + adjwt[0]
    for i, row in enumerate(adjwt):
        row_sum = sum(row)
        if row_sum: rows.append(i)
        for j, el in enumerate(row):
            col_sums[j] += el
    cols = [i for i, total in enumerate(col_sums) if total]

    chars = []
    for indices in [rows, cols]:
        line = [chr(i) for i in indices]
        chars.append(''.join(line))
    row_chars, col_chars = chars

    print('  ' + col_chars)
    print(' +' + '-'*len(col_chars) + '+')
    for i, index in enumerate(rows):
        row = adjwt[index]
        row = [row[j] for j in cols]
        line = [row_chars[i], '|']
        for el in row:
            char = 'X' if el else '.'
            line.append(char)
        line.extend(['|', row_chars[i]])
        print(''.join(line))
    print(' +' + '-'*len(col_chars) + '+')
    print('  ' + col_chars)

default_ret = 0, 0, 0, 0, 0, 0, False, 0.0, 0.0, 0.0, 0.0, 0.0

def strcmp95(ying, yang, larger_tol=False, to_upper=False, debug=True):

    ying_len = len1 = len(ying)
    yang_len = len2 = len(yang)
    y_length = max(ying_len, yang_len)
    if debug:
        print("ying: '%s' (len %d)" % (ying, ying_len))
        print("yang: '%s' (len %d)" % (yang, yang_len))
        print("length:", y_length)
        print("flags:", int(not(larger_tol)), int(not(to_upper)))
        # We have to invert flags because original C code used them to signal
        # that some functionality should be turned off. We use it to activate
        # some functionality.

    # If either string is blank, return
    if not(ying.strip() and yang.strip()):
        return (ying_len, yang_len) + default_ret[2:]

    # Identify the strings to be compared by stripping off all leading and
    # trailing spaces.

    # To be compatible with the fixed buffer c-code, if they're not of equal
    # length to start with, we have to pad them...
    if ying_len != yang_len:
        diff = ying_len-yang_len
        if diff > 0:
            yang = yang + ' '*diff
        else:
            ying = ying + ' '*abs(diff)

    k, j = y_length - 1, 0
    i = k
    while ying[j]==' ' and j < k: j += 1
    while ying[i]==' ' and i > 0: i -= 1
    ying_length = i + 1 - j
    yi_st = j
    ying_hold = ying[yi_st:i+1]

    if debug:
        print()
        print("ying start: %d" % yi_st)
        print("ying length: %d" % ying_length)

    i, j = k, 0
    while yang[j]==' ' and j < k: j += 1
    while yang[i]==' ' and i > 0: i -= 1
    yang_length = i + 1 - j
    yang_hold = yang[j:i+1]

    if debug:
        print("yang start: %d" % j)
        print("yang length: %ld" % yang_length)

    if ying_length > yang_length:
        search_range = ying_length
        minv = yang_length
    else:
        search_range = yang_length
        minv = ying_length
    old_search = search_range
    search_range = (search_range // 2) - 1
    if search_range < 0: search_range = 0
    if debug:
        print("Search range: %d" % search_range)
        print("Minv: %d" % minv)

    ying_flag = [' '] * old_search
    yang_flag = [' '] * old_search

    # Convert all lower case characters to upper case.
    if to_upper:
        ying_hold = ying_hold.upper()
        yang_hold = yang_hold.upper()
    if debug:
        print("ying hold: '%s'" % ying_hold)
        print("yang hold: '%s'" % yang_hold)
        print()
    # Looking only within the search range, count and flag the matched pairs.
    Num_com = 0
    yl1 = yang_length - 1
    for i in range(ying_length):
        lowlim = max(i - search_range, 0)
        hilim  = min(i + search_range, yl1)
        if debug: print("%d. Looking for char %c in range [%ld, %ld (incl)]" % (i, ying_hold[i],lowlim, hilim))
        for j in range(lowlim, hilim+1):
            if debug: print("   j:%2d   char: %c" % (j, yang_hold[j]))
            if yang_flag[j] != '1' and yang_hold[j] == ying_hold[i]:
                yang_flag[j] = '1'
                ying_flag[i] = '1'
                Num_com += 1
                break
    if debug:
        print('Num com:', Num_com);
        print("ying flag: '%s'" % ''.join(ying_flag))
        print("yang flag: '%s'" % ''.join(yang_flag))

    # If no characters in common - return
    if not Num_com:
        return (len1, len2) + default_ret[2:]
    num_matches = Num_com
    where_matched = None

    # Count the number of transpositions
    k = N_trans = 0
    for i in range(ying_length):
        if ying_flag[i]=='1':
            for j in range(k, yang_length):
                if yang_flag[j]=='1':
                    k = j + 1
                    break
            if ying_hold[i] != yang_hold[j]:
                N_trans += 1
    if debug: print('Transpositions:', N_trans)
    half_transposes = N_trans
    N_trans //= 2

    # Main weight computation.
    weight =   Num_com / (ying_length*1.0) \
             + Num_com / (yang_length*1.0) \
             + (Num_com - N_trans) / (Num_com*1.0)
    weight /= 3.0
    weight_jaro = weight
    if debug: print("First weight: %.6f" % weight)

    # adjust for similarities in nonmatched characters
    N_simi = 0
    if minv > Num_com:
        for i in range(ying_length):
            row = ord(ying_hold[i])
            if ying_flag[i]==' ' and INRANGE(row):
                for j in range(yang_length):
                    col = ord(yang_hold[j])
                    if yang_flag[j]==' ' and INRANGE(col):
                        weight = adjwt[row][col]
                        if weight:
                            N_simi += weight
                            yang_flag[j] = '2'
                            break
    typo_score = N_simi
    Num_sim = N_simi / 10.0 + Num_com
    if debug:
        print('N_simi :', N_simi)
        print('Num sim: %.6f' % Num_sim)
        print("ying flag: '%s'" % ''.join(ying_flag))
        print("yang flag: '%s'" % ''.join(yang_flag))

    # Main weight computation.
    weight =   Num_sim / (ying_length*1.0) \
             + Num_sim / (yang_length*1.0) \
             + (Num_com - N_trans) / (Num_com*1.0)
    weight /= 3.0
    weight_typo = weight
    if debug: print("Weight: %.6f" % weight)

    weight_winkler = weight_jaro
    weight_winkler_typo = weight_longer = weight_typo
    pre_matches = 0
    adjust_long = False

    # Continue to boost the weight if the strings are similar
    if weight > 0.7:
        # Adjust for having up to the first 4 characters in common
        j = min(minv, 4)
        i = 0
        while i<j and ying_hold[i]==yang_hold[i] and NOTNUM(ord(ying_hold[i])):
            if debug: print("pre-match: %d" % i)
            i += 1
        # if yang_length: assert i >= 1
        if i:
            if debug: print("final pre-match: %d" % i)
            pre_matches = i
            weight += (i * 0.1 * (1.0 - weight))
            weight_winkler_typo = weight_longer = weight
            weight_winkler = weight_jaro + (i * 0.1 * (1.0 - weight_jaro))
        if debug: print("Adjusted weight: %.6f" % weight)

        # Optionally adjust for long strings.
        # After agreeing beginning chars, at least two more must agree and
        # the agreeing characters must be > .5 of remaining characters.
        if larger_tol and minv > 4 and Num_com > i+1 and 2*Num_com >= minv+i:
            if NOTNUM(ord(ying_hold[0])):
                adjust_long = True
                t = (1.0 * Num_com-i-1) / (ying_length + yang_length - i*2+2)
                weight += (1 - weight) * t
                weight_longer = weight
                if debug: print("Re-adjusted weight: %.6f" % weight)

    return (len1, len2, num_matches, half_transposes,
                typo_score, pre_matches, adjust_long,
                    weight_jaro, weight_typo, weight_winkler,
                        weight_winkler_typo, weight_longer)

if __name__ == '__main__':
    s1 = sys.argv[1]
    s2 = sys.argv[2]
    flag_str = sys.argv[3]
    flags = [not(bool(int(f))) for f in flag_str]
    larger_tol, to_upper = flags
    strcmp95(s1, s2, larger_tol, to_upper)

    # print_adjwt_table()