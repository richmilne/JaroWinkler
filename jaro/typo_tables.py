# coding: utf8
import os
import sys

# The original typo table from the Jaro-Winkler C code.
__sp_table = \
 ['A','E',  'A','I',  'A','O',  'A','U',  'B','V',  'E','I',  'E','O',  'E','U',
  'I','O',  'I','U',  'O','U',  'I','Y',  'E','Y',  'C','G',  'E','F',
  'W','U',  'W','V',  'X','K',  'S','Z',  'X','S',  'Q','C',  'U','V',
  'M','N',  'L','I',  'Q','O',  'P','R',  'I','J',  '2','Z',  '5','S',
  '8','B',  '1','I',  '1','L',  '0','O',  '0','Q',  'C','K',  'G','J',
# 'E',' ',  'Y',' ',  'S',' '
]

def create_typo_table(typo_chars, score=3):
    """Create a dictionary mapping typographically similar characters to each
    other.

    Input is a list (of even length) of characters. The characters are
    assummed to be listed in pairs, and their presence states that the first
    character is typographically similar to the second.

    Each pairing of similar characters is given the value (the 'score'
    argument). The Jaro-Winkler routines use this score to increase the
    amount of characters matching in their input strings.

    An example:

    >>> typo_chars = ['B', '8', '0', 'O', '0', 'Q', 'I', 'l']
    >>> typo_table = create_typo_table(typo_chars, score=2)

    This function returns a symmetrical dictionary of dictionaries:

    >>> typo_table['B']['8'] == typo_table['8']['B']
    True

    ... but note that this symmetry is not carried through in future
    assignments:

    >>> typo_table['8']['B'] = 5
    >>> print_typo_table(typo_table)
      08BIOQl
     +-------+
    0|....22.|0
    8|..5....|8
    B|.2.....|B
    I|......2|I
    O|2......|O
    Q|2......|Q
    l|...2...|l
     +-------+
      08BIOQl
    """
    typo_table = {}

    for i in range(len(typo_chars) // 2):
        row_char = typo_chars[i*2]
        col_char = typo_chars[i*2+1]
        # Create the symmetric mappings from row_char to col_char,
        # and vice versa.
        for row, col in [(row_char, col_char), (col_char, row_char)]:
            try:
                row_dict = typo_table[row]
            except KeyError:
                typo_table[row] = row_dict = {}
            if col in row_dict:
                msg = "Redundant entry (%s) in typo_chars." % col
                raise ValueError(msg)

            row_dict[col] = score

    return typo_table

def print_typo_table(typo_table):
    row_chars = list(typo_table.keys())
    col_chars = set([])
    # The table should be symmetrical, and so row_chars should equal col_chars,
    # but we'll leave the option for asymmetry open.
    for row in row_chars:
        cols = list(typo_table[row].keys())
        col_chars.update(cols)

    chars = []
    for indices in [row_chars, col_chars]:
        line = [i for i in sorted(indices)]
        chars.append(''.join(line))
    row_chars, col_chars = chars

    print('  ' + col_chars)
    print(' +' + '-'*len(col_chars) + '+')
    for row in row_chars:
        line = [row, '|']
        row_dict = typo_table[row]
        for col in col_chars:
            # char = 'X' if col in row_dict else '.'
            if col in row_dict:
                char = str(row_dict[col])
                assert len(char) == 1
            else:
                char = '.'
            line.append(char)
        line.extend(['|', row])
        print(''.join(line))
    print(' +' + '-'*len(col_chars) + '+')
    print('  ' + col_chars)

adjwt = create_typo_table(__sp_table)

if __name__ == '__main__':
    print_typo_table(adjwt)
