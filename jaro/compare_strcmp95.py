import os
import sys
import subprocess
import io
from . import strcmp95
from .jaro_tests import gen_test_args, jaro_tests

# We want to write a Python version of the Jaro-Winkler function. To test
# whether our function works, we compare it to the original Jaro-Winkler C code.

# First, we instrument the orignal C code, so that it prints out the relevant
# values in its calculation. We then write our Python version to calculate and
# print out exactly the same values.

# This script runs the compiled C code and our Python function for a given set
# of inputs, and compares their outputs. If they match, our Python function is
# correct. We can then use the Python version as a reference while we
# refactor the code.

base = os.path.dirname(os.path.abspath(__file__))
basename = 'strcmp95'

oracle_cmd = [os.path.join(base, basename)]

if not os.path.isfile(oracle_cmd[0]):
    assert os.path.isfile(oracle_cmd[0] + '.c')
    print()
    print("Can't find compiled version of %s.c to test!" % basename)
    print('Try executing:')
    print('gcc "%s/%s.c" -o "%s/%s"' % (base, basename, base, basename))
    print()
    raise ImportError


def run_oracle(string1, string2, flag_str):
    cmd = oracle_cmd + [string1, string2, flag_str]
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    return output.decode('utf8')


def is_flag_str(s1, s2):
    return s1.startswith('flags') and s2.startswith('flags')


def flag_str_complement(s1, s2):
    flag_bits = [int(f) for f in s1[-3:].split()]
    comp_bits = ' '.join([str(int(not f)) for f in flag_bits])
    return comp_bits == s2[-3:]

if 0:
    s1, s2 = 'flags: 1 1', 'flags: 0 0'
    print(is_flag_str(s1, s2))
    print(flag_str_complement(s1, s2))
    sys.exit()


def align_stdouts(cout, pyout):
    buffer = []
    found_flags = False
    mismatch = False

    cout = cout.split('\n')
    pyout = pyout.split('\n')
    len1 = len(cout)
    len2 = len(pyout)
    for i in range(max(len1, len2)):
        s1 = cout[i] if i < len1 else ''
        s2 = pyout[i] if i < len2 else ''
        match = s1==s2

        both_strs = ' '.join((s1.ljust(47), s2))
        line = ''.join((str(match).ljust(6), both_strs))

        if not found_flags and is_flag_str(s1, s2):
            found_flags = True
            # Enable these tests later, once we've worked out where to invert
            # flags.
            # if flag_str_complement(s1, s2):
            #     line = ' '.join(('Compl', both_strs))
            #     match = True
            # else:
            #     match = False
        mismatch = mismatch or (not match)
        buffer.append(line)

    return mismatch, buffer


def compare(string1, string2, larger_tol, to_upper):

    old_stdout = sys.stdout

    flag_str = ''.join([str(int(f)) for f in [larger_tol, to_upper]])
    cout = run_oracle(string1, string2, flag_str)

    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    ans1 = strcmp95.strcmp95(string1, string2, not(larger_tol), not(to_upper))
    pyout = new_stdout.getvalue()
    new_stdout.close()

    sys.stdout = old_stdout

    mismatch, buffer = align_stdouts(cout, pyout)

    if mismatch:
        print()
        print('Mismatch!')
        for line in buffer:
            print(line)
        print()
        print(repr(cout))
        print(repr(pyout))
        raise AssertionError

def test():
    for larger_tol, to_upper, s1, s2 in gen_test_args(jaro_tests):

        both_upper = s1.isupper() and s2.isupper()
        all_pass = both_upper and not to_upper

        if not all_pass:
            # These are the only test cases that pass so far. TODO: Need to
            # investigate further and see what's wrong with the others - looks
            # like a mismatch between the flag inversions and what the C and
            # the Python code expect
            # continue
            pass

        if 1:
            print(str(larger_tol).ljust(5), end=' ')
            print(str(to_upper).ljust(5), end=' ')
            print((s1, s2))
        compare(s1, s2, larger_tol, to_upper)
        compare(s2, s1, larger_tol, to_upper)

if __name__ == '__main__':
    test()
