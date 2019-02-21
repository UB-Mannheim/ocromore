"""
The following file contains an LCS Algorithm by Gonzalo Exequiel Pedone,
there's a test below which shows how to applicate the algorithm and
use pivot possibilities. This was only implemented for testing purposes,
the final implementation uses other algorithm.
"""

import numpy as np

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Recursive sequences alignment algorithm, based on LCS.
# Copyright (C) 2012  Gonzalo Exequiel Pedone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with This program. If not, see <http://www.gnu.org/licenses/>.
#
# Email   : hipersayan DOT x AT gmail DOT com
# Web-Site: http://hipersayanx.blogspot.com/
#
# This sequences alignment algorithm consist in findind the LCS of two sequences
# and then resolve the alignment of the sequences before and after the LCS
# recursively.

# Longest Common Subsequence, Shift algorithm.
# Copyright (C) 2012  Gonzalo Exequiel Pedone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with This program. If not, see <http://www.gnu.org/licenses/>.
#
# Email   : hipersayan DOT x AT gmail DOT com
# Web-Site: http://hipersayanx.blogspot.com/
#
# The shift algorithm consist on finding the Longest Common Subsequence between
# a sequence 'a' and 'b' by comparing the last element of 'a' with the first
# element of 'b', and finding the longest sequence between the common elements,
# then shifting 'a' to the right, and comparing the next two elements, and so
# on, until reach the right wall, then shifting 'b' to the left until reach the
# left wall.
# This is a non-recursive algorithm, and the maximum number of comparissons are:
# (len(a) + len(b) - 1)**2.
#
#                 ===>
#             __ __ __ __
#          a |__|__|__|__|__ __ ) right wall
# left wall (         |__|__|__| b
#                        <===

def lcs(a=[], b=[]):
    if a == [] or b == []:
        return []

    l = len(a) + len(b) - 1

    # Fill non-comparable elements with null spaces.
    sa = a + (len(b) - 1) * ['']
    sb = (len(a) - 1) * [''] + b

    longest = []

    for k in range(l):
        cur = []

        for c in range(l):
            if sa[c] != '' and sb[c] != '' and sa[c] == sb[c]:
                cur.append(sa[c])
            else:
                if len(cur) > len(longest):
                    longest = cur

                cur = []

        if len(cur) > len(longest):
            longest = cur

        if sa[len(sa) - 1] == '':
            # Shift 'a' to the right.
            sa = [''] + sa[: len(sa) - 1]
        else:
            # Shift 'b' to the left.
            sb = sb[1:] + ['']

    return longest

def findSubList(l=[], sub=[]):
    if len(sub) > len(l):
        return -1

    for i in range(len(l) - len(sub) + 1):
        j = 0
        eq = True

        for s in sub:
            if l[i + j] != s:
                eq = False

                break

            j += 1

        if eq:
            return i

    return -1


def alignSequences(sequence1=[], sequence2=[]):
    # lcs is the Longest Common Subsequence function.
    cs = lcs(sequence1, sequence2)

    if cs == []:
        return sequence1 + [''] * len(sequence2), \
               [''] * len(sequence1) + sequence2
    else:
        # Remainings non-aligned sequences in the left side.
        left1 = sequence1[: findSubList(sequence1, cs)]
        left2 = sequence2[: findSubList(sequence2, cs)]

        # Remainings non-aligned sequences in the right side.
        right1 = sequence1[findSubList(sequence1, cs) + len(cs):]
        right2 = sequence2[findSubList(sequence2, cs) + len(cs):]

        # Align the sequences in the left and right sides:
        leftAlign = alignSequences(left1, left2)
        rightAlign = alignSequences(right1, right2)

        return leftAlign[0] + cs + rightAlign[0], \
               leftAlign[1] + cs + rightAlign[1]


def unalignSequence(sequence=[]):
    return [element for element in sequence if element != '']


def sequenceCount(sequences=[], sequence=[]):
    count = 0

    for s in sequences:
        if unalignSequence(s) == unalignSequence(sequence):
            count += 1

    return count


def alignScore(aSequence1=[], aSequence2=[]):
    score = 0

    for i in range(len(aSequence1)):
        if aSequence1[i] == aSequence2[i]:
            # match
            score += 1
        else:
            # gap
            score -= 1

    return score


def msa(sequences1=[], sequences2=[]):
    sSequences1 = []
    sSequences2 = []
    scores = []

    for sequence2 in sequences2:
        for sequence1 in sequences1:
            aSequence1, aSequence2 = alignSequences(sequence1, sequence2)
            score = alignScore(aSequence1, aSequence2)

            if scores == []:
                sSequences1.append(aSequence1)
                sSequences2.append(aSequence2)
                scores.append(score)
            else:
                # Sort sequences by score.
                imin = 0
                imax = len(scores) - 1
                imid = (imax + imin) >> 1

                while True:
                    if score == scores[imid]:
                        sSequences1 = sSequences1[: imid + 1] + \
                                      [aSequence1] + \
                                      sSequences1[imid + 1:]

                        sSequences2 = sSequences2[: imid + 1] + \
                                      [aSequence2] + \
                                      sSequences2[imid + 1:]

                        scores = scores[: imid + 1] + \
                                 [score] + \
                                 scores[imid + 1:]

                        break
                    elif score < scores[imid]:
                        imax = imid
                    elif score > scores[imid]:
                        imin = imid

                    imid = (imax + imin) >> 1

                    if imid == imin or imid == imax:
                        if score < scores[imin]:
                            sSequences1 = sSequences1[: imin] + \
                                          [aSequence1] + \
                                          sSequences1[imin:]

                            sSequences2 = sSequences2[: imin] + \
                                          [aSequence2] + \
                                          sSequences2[imin:]

                            scores = scores[: imin] + [score] + scores[imin:]
                        elif score > scores[imax]:
                            sSequences1 = sSequences1[: imax + 1] + \
                                          [aSequence1] + \
                                          sSequences1[imax + 1:]

                            sSequences2 = sSequences2[: imax + 1] + \
                                          [aSequence2] + \
                                          sSequences2[imax + 1:]

                            scores = scores[: imax + 1] + \
                                     [score] + \
                                     scores[imax + 1:]
                        else:
                            sSequences1 = sSequences1[: imin + 1] + \
                                          [aSequence1] + \
                                          sSequences1[imin + 1:]

                            sSequences2 = sSequences2[: imin + 1] + \
                                          [aSequence2] + \
                                          sSequences2[imin + 1:]

                            scores = scores[: imin + 1] + \
                                     [score] + \
                                     scores[imin + 1:]

                        break

    i = 0

    while i < len(scores):
        count1 = sequenceCount(sSequences1, sSequences1[i])
        count2 = sequenceCount(sSequences2, sSequences2[i])

        if count1 > 1 and count2 > 1:
            del sSequences1[i]
            del sSequences2[i]
            del scores[i]

            i -= 1
        elif count1 > 1 and count2 < 2:
            sSequences2[i] = unalignSequence(sSequences2[i])
            sSequences1[i] = len(sSequences2[i]) * ['']
        elif count1 < 2 and count2 > 1:
            sSequences1[i] = unalignSequence(sSequences1[i])
            sSequences2[i] = len(sSequences1[i]) * ['']

        i += 1

    return sSequences1, sSequences2

"""
sequences1 = [list('ggagggcccagctcattcgggagaaagcct'),
              list('tgtggggatcttgtggtgtgaac'),
              list('gttgaaaagggtaccttcaattggaaccga'),
              list('tcgggggtggccggaggacaacccagt'),
              list('acttaaattatgagatc')]

sequences2 = [list('atattccctgtcagctctagttctttctcc'),
              list('agctgccgggcgcg'),
              list('gccacgagggaggcgggaggattca'),
              list('ccctttcggttccaactatggtgcggggag')]
"""
list_one = list('1. Wie funktioniert der Algorithmus')
list_two = list('2. Wie funktioniert hier der Algorithmus') # this is the pivot element
list_three = list('3. Wie der Algorithmus')

def compare(item_one, item_two, wildcard_character='¦'):
    sequences1 = [item_one]
    sequences2 = [item_two]

    sSequences1, sSequences2 = msa(sequences1, sequences2)
    """
    for i in range(len(sSequences1)):
        s1 = ''.join(['-' if element == '' else element \
                      for element in sSequences1[i]])
        s2 = ''.join(['-' if element == '' else element \
                      for element in sSequences2[i]])

        print(s1)
        print(s2)
        print()
    """
    s1 = ''.join([wildcard_character if element == '' else element \
                  for element in sSequences1[0]])
    s2 = ''.join([wildcard_character if element == '' else element \
                  for element in sSequences2[0]])

    return s1,s2

def get_same_count(c1, c2, c3):
    same_ctr = 0
    if c1 == c2:
        same_ctr += 1

    if c1 == c3:
        same_ctr +=1

    return same_ctr


def best_of_three_simple(line_1, line_2, line_3, index_best, wildcard_character='¦'):
    list_line_1 = list(line_1)
    list_line_2 = list(line_2)
    list_line_3 = list(line_3)


    accumulated_chars = ""
    for character_index, character_1 in enumerate(list_line_1):
        character_2 = list_line_2[character_index]
        character_3 = list_line_3[character_index]

        clist = [character_1,character_2,character_3]
        sc1 = get_same_count(character_1, character_2, character_3)
        sc2 = get_same_count(character_2, character_1, character_3)
        sc3 = get_same_count(character_3, character_2, character_1)
        maxindices = np.argmax([sc2, sc1, sc3])
        if maxindices == 0:
            accumulated_chars += character_2
        elif maxindices == 1:
            accumulated_chars += character_1
        else:
            accumulated_chars += character_3

    accumulated_chars_stripped = accumulated_chars.replace(wildcard_character,'')

    return accumulated_chars, accumulated_chars_stripped


res_one_1, res_two_1 = compare(list_one, list_two)
res_two_2, res_three_2 = compare(list_two, list_three)

print("A:", res_one_1)
print("B:", res_two_2)
print("C:", res_three_2)

best, best_stripped = best_of_three_simple(res_one_1, res_two_2, res_three_2, 1)  # res two is the best element
best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())

print("D:", best)
print("E:", best_stripped)
print("F:", best_stripped_non_multi_whitespace)