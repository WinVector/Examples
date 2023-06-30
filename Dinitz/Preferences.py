from typing import Dict, Hashable, Iterable, List, Tuple


class Preferences:
    """
    Class to record order preferences.
    """

    def __init__(self, prefs_list: Iterable[Hashable]) -> None:
        """
        Encode preferences.

        :param prefs_list: ordered list of keys prefering early items
        """
        self.prefs_list = list(prefs_list)
        self.consider_set = set(prefs_list)
        # check preferences are distinct, and Hashable keys
        assert len(self.prefs_list) == len(self.consider_set)
        for v in self.prefs_list:
            assert isinstance(v, Hashable)
        # re-code for fast lookup
        self.prefs = dict()
        for i in range(len(self.prefs_list)):
            self.prefs[self.prefs_list[i]] = set(self.prefs_list[0:i])

    def considers(self, i) -> bool:
        """
        Return True if i is considered as a possible match.

        :param i: first item
        :return: True, if i is comsidered a possible match
        """
        return i in self.consider_set

    def prefers(self, i, j) -> bool:
        """
        Return True if i prefered to j.

        :param i: first item
        :param j: second item
        :return: True, if i preferred to j
        """
        prefs_i = None
        prefs_j = None
        try:
            prefs_i = self.prefs[i]
        except KeyError:
            pass
        try:
            prefs_j = self.prefs[j]
        except KeyError:
            pass
        # special case out of unknown values
        if (prefs_i is None) or (prefs_j is None):
            # prefer known keys
            if prefs_i is not None:
                return True
            if prefs_i is not None:
                return False
            # neither known, fall back to order
            return i < j
        # stored relation
        return i in prefs_j
