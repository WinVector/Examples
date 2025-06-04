
from typing import Dict, Set
from collections import OrderedDict


class TransitiveCache:
    """cache that store start->end _transitions and compute transitive closure on lookup"""
    _absorbing_states: OrderedDict
    _transitions: OrderedDict
    _max_size: int

    def __init__(self, *, max_size : int = 1000000):
        assert isinstance(max_size, int)
        self._absorbing_states = OrderedDict()
        self._transitions = OrderedDict()
        self._max_size = max_size

    def store_transition(self, start, end) -> None:
        assert start is not None
        assert end is not None
        if start == end:
            self._absorbing_states[start] = True
            while len(self._absorbing_states) > self._max_size:
                self._absorbing_states.popitem(last=False)
        else:
            self._transitions[start] = end
            while len(self._transitions) > self._max_size:
                self._transitions.popitem(last=False)
    
    def __contains__(self, item):
        assert item is not None
        have = False
        if item in self._absorbing_states:
            self._absorbing_states.move_to_end(item)
            have = True
        if (not have) and (item in self._transitions):
            self._transitions.move_to_end(item)
            have = True
        return have

    def lookup_result(self, start):
        assert start is not None
        if start not in self:
            return None
        seen = set()
        end = start
        try:
            while end not in self._absorbing_states:
                if end in seen:
                    raise ValueError("cycle")
                seen.add(end)
                end = self._transitions[end]
        except KeyError:
            pass
        if start != end:
            self.store_transition(start, end)
            self._transitions.move_to_end(start)
        return end
