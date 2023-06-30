from typing import Dict, Hashable, Iterable, List, Tuple
from collections import deque
from Preferences import Preferences


def match_Gale_Shapley(
    left_preferences: Dict[Hashable, Iterable[Hashable]],
    right_preferences: Dict[Hashable, Iterable[Hashable]],
) -> List[Tuple[int, int]]:
    """
    Compute a stable matching using the Gale Shapley algorithm. Non-matches allowed.

    :param left_preferences: map of ordered preference for accepting side.
    :param right_preferences: map of ordered preferences for proposing side.
    :return: map from left IDs to assigned matches.
    """
    # copy left preferences
    left_preferences = {k: Preferences(v) for k, v in left_preferences.items()}
    # copy right preferences
    right_preferences = {k: deque(v) for k, v in right_preferences.items()}
    for v in right_preferences.values():
        assert len(v) == len(set(v))
    # build initial assignment
    left_choices = {k: None for k in left_preferences.keys()}
    right_choices = {k: None for k in right_preferences.keys()}
    do_continue = True
    while do_continue:
        do_continue = False  # hope to end
        # iterate through proposals from unmached rights
        for r, r_list in right_preferences.items():
            # run down right item's preferences
            while (right_choices[r] is None) and (len(r_list) > 0):
                r_candidate = r_list.popleft()
                r_candidate_competition = left_choices[r_candidate]
                r_candidate_prefs = left_preferences[r_candidate]
                if r_candidate_prefs.considers(r) and (
                    (r_candidate_competition is None)
                    or r_candidate_prefs.prefers(r, r_candidate_competition)
                ):
                    # break up any old pairing
                    if r_candidate_competition is not None:
                        cur_match_other = right_choices[r_candidate_competition]
                        assert right_choices[r_candidate_competition] == cur_match_other
                        assert left_choices[cur_match_other] == r_candidate_competition
                        right_choices[r_candidate_competition] = None
                        left_choices[cur_match_other] = None
                    # write in new pairing
                    right_choices[r] = r_candidate
                    left_choices[r_candidate] = r
                    # signal we are not done
                    do_continue = True
    keys = sorted(left_choices.keys())
    return [(k, left_choices[k]) for k in keys if left_choices[k] is not None]
