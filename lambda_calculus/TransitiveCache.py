
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

    def lookup_result(self, start):
        assert start is not None
        if (start in self._absorbing_states) or (start not in self._transitions):
            return start
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
        # short circuit all visited states to end
        for s in reversed(list(seen)):
            if s != end:
                self.store_transition(s, end)
                self._transitions.move_to_end(s)
        return end

    def store_absorbing(self, item) -> None:
        self._absorbing_states[item] = True
        while len(self._absorbing_states) > self._max_size:
            self._absorbing_states.popitem(last=False)

    def store_transition(self, start, end) -> None:
        assert start is not None
        assert end is not None
        assert start != end
        # try to avoid a -> b overwrittig a -> c (from earlier a -> b -> c)
        if end in self._transitions:
            end = self.lookup_result(end)
        self._transitions[start] = end
        while len(self._transitions) > self._max_size:
            self._transitions.popitem(last=False)
    
    def __contains__(self, item):
        assert item is not None
        if item in self._absorbing_states:
            self._absorbing_states.move_to_end(item)
            return True
        if item in self._transitions:
            self._transitions.move_to_end(item)
            return True
        return False
