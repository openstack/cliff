# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import typing as ty

# Each edit operation is assigned different cost, such as:
#  'w' means swap operation, the cost is 0;
#  's' means substitution operation, the cost is 2;
#  'a' means insertion operation, the cost is 1;
#  'd' means deletion operation, the cost is 3;
# The smaller cost results in the better similarity.
COST = {'w': 0, 's': 2, 'a': 1, 'd': 3}


def damerau_levenshtein(s1: str, s2: str, cost: dict[str, int]) -> int:
    """Calculates the Damerau-Levenshtein distance between two strings.

    The Damerau-Levenshtein distance says the minimum number of single
    character edits (i.e. insertions, deletions, swap or substitution)
    required to change one string to the other.
    The idea is to reserve a matrix to hold the Levenshtein distances between
    all prefixes of the first string and all prefixes of the second, then we
    can compute the values in the matrix in a dynamic programming fashion. To
    avoid a large space complexity, only the last three rows in the matrix is
    needed.(row2 holds the current row, row1 holds the previous row, and row0
    the row before that.)

    More details:
        https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
        https://github.com/git/git/commit/8af84dadb142f7321ff0ce8690385e99da8ede2f
    """

    if s1 == s2:
        return 0

    len1 = len(s1)
    len2 = len(s2)

    if len1 == 0:
        return len2 * cost['a']
    if len2 == 0:
        return len1 * cost['d']

    row1 = [i * cost['a'] for i in range(len2 + 1)]
    row2 = row1[:]
    row0 = row1[:]

    for i in range(len1):
        row2[0] = (i + 1) * cost['d']

        for j in range(len2):
            # substitution
            sub_cost = row1[j] + (s1[i] != s2[j]) * cost['s']

            # insertion
            ins_cost = row2[j] + cost['a']

            # deletion
            del_cost = row1[j + 1] + cost['d']

            # swap
            swp_condition = (
                (i > 0)
                and (j > 0)
                and (s1[i - 1] == s2[j])
                and (s1[i] == s2[j - 1])
            )

            # min cost
            if swp_condition:
                swp_cost = row0[j - 1] + cost['w']
                p_cost = min(sub_cost, ins_cost, del_cost, swp_cost)
            else:
                p_cost = min(sub_cost, ins_cost, del_cost)

            row2[j + 1] = p_cost

        row0, row1, row2 = row1, row2, row0

    return row1[-1]


def terminal_width() -> ty.Optional[int]:
    """Return terminal width in columns

    Uses `os.get_terminal_size` function

    :returns: terminal width
    :rtype: int or None
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        return None
