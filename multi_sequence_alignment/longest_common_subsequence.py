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


class LCS(object):

    @staticmethod
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

    @staticmethod
    def lcs_with_wildcard(a=[], b=[], wildcard='¦'):
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
                    if sa[c]==wildcard and sb[c]==wildcard:
                        print('ok') # this is unlikely
                elif sa[c] == wildcard and sb[c]!='':
                    cur.append(sa[c])
                elif sb[c] == wildcard and sa[c]!='':
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