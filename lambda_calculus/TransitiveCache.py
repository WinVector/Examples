
from typing import Dict, Set


class TransitiveCache:
    """cache that store start->end _transitions and compute transitive closure on lookup"""
    _absorbing_states: Set
    _transitions: Dict

    def __init__(self):
        self._absorbing_states = set()
        self._transitions = dict()

    def store_transition(self, start, end) -> None:
        assert start is not None
        assert end is not None
        if start == end:
            self._absorbing_states.add(start)
        else:
            self._transitions[start] = end
    
    def __contains__(self, item):
        assert item is not None
        return (item in self._absorbing_states) or (item in self._transitions)
    
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
        return end
