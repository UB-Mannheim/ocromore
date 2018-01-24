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

from multi_sequence_alignment.longest_common_subsequence import LCS

class SequenceAlignment(object):
    # Auxiliary function for finding the first index in wich appears a sub-sequence.
    @staticmethod
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

    @staticmethod
    def alignSequences(sequence1=[], sequence2=[]):
        # lcs is the Longest Common Subsequence function.
        cs = LCS.lcs(sequence1, sequence2)

        if cs == []:
            return sequence1 + [''] * len(sequence2), \
                   [''] * len(sequence1) + sequence2
        else:
            # Remainings non-aligned sequences in the left side.
            left1 = sequence1[: SequenceAlignment.findSubList(sequence1, cs)]
            left2 = sequence2[: SequenceAlignment.findSubList(sequence2, cs)]

            # Remainings non-aligned sequences in the right side.
            right1 = sequence1[SequenceAlignment.findSubList(sequence1, cs) + len(cs):]
            right2 = sequence2[SequenceAlignment.findSubList(sequence2, cs) + len(cs):]

            # Align the sequences in the left and right sides:
            leftAlign = SequenceAlignment.alignSequences(left1, left2)
            rightAlign = SequenceAlignment.alignSequences(right1, right2)

            return leftAlign[0] + cs + rightAlign[0], \
                   leftAlign[1] + cs + rightAlign[1]