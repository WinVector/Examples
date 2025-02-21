from functools import cache
import numpy as np
import pandas as pd
from scipy.special import comb
from typing import List, Optional


# define our deck shuffling tool
def k_array_with_t_true(k: int, t: int, *, rng):
    """Create a length-k boolean array with t-True values"""
    is_true = np.array([False] * k, dtype=bool)
    is_true[rng.choice(k, size=t, replace=False)] = True
    return tuple(is_true)


# implement our betting strategy
def run_bets(is_red, *, trajectory: Optional[List] = None) -> float:
    """Run the Kelly betting strategy for continuous values"""
    stake = 1.0
    if trajectory is not None:
        trajectory.append(stake)
    n_red_remaining = int(np.sum(is_red))
    n_black_remaining = len(is_red) - n_red_remaining
    for i, _ in enumerate(is_red):
        # form bet
        bet_red = 0
        bet_black = 0
        fraction = np.abs(n_red_remaining - n_black_remaining) / (
            n_red_remaining + n_black_remaining
        )
        if n_red_remaining > n_black_remaining:
            bet_red = stake * fraction
        elif n_black_remaining > n_red_remaining:
            bet_black = stake * fraction
        # derive outcome
        stake = stake - (bet_red + bet_black)
        if is_red[i]:
            stake = stake + 2 * bet_red
            n_red_remaining = n_red_remaining - 1
        else:
            stake = stake + 2 * bet_black
            n_black_remaining = n_black_remaining - 1
        if trajectory is not None:
            trajectory.append(stake)
    return stake


def theoretical_payout(red_remaining: int, black_remaining: int):
    return 2 ** (red_remaining + black_remaining) / comb(
        red_remaining + black_remaining, red_remaining, exact=True
    )


def run_bets_int(
    is_red,
    *,
    verbose: bool = False,
    initial_stake: int,
    satiation_point: Optional[int],
    bet_strategy,
) -> float:
    stake = int(initial_stake)
    trajectory = [stake]
    n_red_remaining = int(np.sum(is_red))
    n_black_remaining = len(is_red) - n_red_remaining
    for i, _ in enumerate(is_red):
        # form bet
        bet_red = 0
        bet_black = 0
        net_bet = bet_strategy(stake, n_black_remaining, n_red_remaining, satiation_point)
        assert net_bet is not None
        assert isinstance(net_bet, int)
        assert np.abs(net_bet) <= stake
        if net_bet > 0:
            assert n_black_remaining > 0
            bet_black = net_bet
        elif net_bet < 0:
            assert n_red_remaining > 0
            bet_red = -net_bet
        assert bet_red >= 0
        assert bet_black >= 0
        if verbose:
            bet_color = "none"
            if bet_red > 0:
                bet_color = "red"
            elif bet_black > 0:
                bet_color = "black"
            print(
                f"step({i}, color: {'red' if is_red[i] else 'black'}) stake: {stake}, bet {bet_color}: {bet_red + bet_black}"
            )
        # derive outcome
        stake = stake - (bet_red + bet_black)
        if is_red[i]:
            stake = stake + 2 * bet_red
            n_red_remaining = n_red_remaining - 1
        else:
            stake = stake + 2 * bet_black
            n_black_remaining = n_black_remaining - 1
        trajectory.append(stake)
    return (stake / initial_stake, np.array(trajectory, dtype=int))


def basic_bet_rules(
    *,
    holdings: int, n_black_remaining: int, n_red_remaining: int
) -> Optional[int]:
    """return signed bet (positive black, negative red) if implied by basic rules"""
    if (holdings <= 0) or (n_black_remaining == n_red_remaining):
        return 0  # no favorable bet available
    if n_red_remaining <= 0:
        return holdings  # forced win
    if n_black_remaining <= 0:
        return -holdings  # forced win
    # now know (holdings > 0) (n_black_remaining > 0) and (n_red_remaining > 0)
    if holdings <= 1:
        return 0  # don't trade entire holdings into uncertainty
    return None  # bet not forced by basic rules


def basic_bet_strategy(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: Optional[int] = None,
) -> int:
    """return signed bet (positive black, negative red)"""
    bet = basic_bet_rules(holdings=holdings, n_black_remaining=n_black_remaining, n_red_remaining=n_red_remaining)
    if bet is not None:
        return bet
    if n_red_remaining > n_black_remaining:
        return -basic_bet_strategy(
            holdings=holdings, 
            n_black_remaining=n_red_remaining,   # swap
            n_red_remaining=n_black_remaining,
        )
    # ideal fractional bet is holdings * (n_black_remaining - n_red_remaining) / (n_black_remaining + n_red_remaining)
    # search for integer maximizing E[log(return)] instead of rounding
    fractional_bet = holdings * (n_black_remaining - n_red_remaining) / (n_black_remaining + n_red_remaining)
    best_black_bet = None
    best_expected_log_return = None
    p_win = n_black_remaining / (n_black_remaining + n_red_remaining)
    for black_bet in range(int(np.floor(fractional_bet)) - 1, int(np.ceil(fractional_bet) + 1)):   # use convexity to bracket soln
        if (black_bet >= 0) and (black_bet < holdings):  # try all bets except total instead of rounding
            expected_log_return = p_win * np.log(holdings + black_bet) + (1 - p_win) * np.log(holdings - black_bet)
            if (best_black_bet is None) or (expected_log_return > best_expected_log_return):
                best_black_bet = black_bet
                best_expected_log_return = expected_log_return
    return best_black_bet


@cache
def _minmax_bet_value(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
) -> int:
    """Compute minmax value of position under optimal betting (internal function use minmax_bet_value() as public API) for non base cases"""
    assert holdings > 0
    assert satiation_point > holdings
    assert n_black_remaining > 0
    assert n_red_remaining > 0
    assert n_black_remaining > n_red_remaining
    best_min_return = None
    for black_bet in range(holdings):  # simulate betting on black, but do not bet all as there is remaining uncertainty
        a = minmax_bet_value(   # black win case
            holdings + black_bet,
            n_black_remaining - 1,
            n_red_remaining,
            satiation_point,
        )
        b = minmax_bet_value(   # black lose case
            holdings - black_bet,
            n_black_remaining,
            n_red_remaining - 1,
            satiation_point,
        )
        min_return = int(min(a, b))
        if (best_min_return is None) or (min_return > best_min_return):
            best_min_return = min_return
    assert best_min_return is not None
    return best_min_return


def minmax_bet_value(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
) -> int:
    """Compute minmax value of satiation_point truncated position."""
    # regularize and eliminate some cases
    if holdings <= 0:  # no bet possible continuation
        return 0
    if holdings >= satiation_point:  # early exit to prevent tracking too many possible holdings
        return satiation_point  # artificial "don't bet" as not needed to establish minimum
    if (n_black_remaining <= 0) or (n_red_remaining <= 0):  # sure thing continuation
        return min(holdings * 2**(n_black_remaining + n_red_remaining), satiation_point)
    if n_black_remaining == n_red_remaining:  # no bet
        draw_1 = minmax_bet_value(holdings, n_black_remaining, n_red_remaining - 1, satiation_point)
        draw_2 = minmax_bet_value(holdings, n_black_remaining - 1, n_red_remaining, satiation_point)
        return min(draw_1, draw_2)
    if n_black_remaining < n_red_remaining:  # swap to canonical form to cache less (and have simpler cached code)
        n_black_remaining, n_red_remaining = n_red_remaining, n_black_remaining
    # now have n_black_remaining > n_red_remaining > 0 and satiation_point > holdings > 0
    return _minmax_bet_value(  # dynamic program: memonized recursion
        holdings, n_black_remaining, n_red_remaining, satiation_point,
    )


@cache
def _dynprog_bet_strategy_by_search(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
) -> int:
    # retrieve a best bet from dynprog table with maximal expected 1 step log return
    best_black_bet = None
    best_min_return = None
    best_expected_log_return = None
    p_win = n_black_remaining / (n_black_remaining + n_red_remaining)
    for black_bet in range(holdings):  # don't bet all of holdings on non sure thing
        expected_log_return = p_win * np.log(holdings + black_bet) + (1 - p_win) * np.log(holdings - black_bet)
        a = minmax_bet_value(
            holdings + black_bet,
            n_black_remaining - 1,
            n_red_remaining,
            satiation_point,
        )
        b = minmax_bet_value(
            holdings - black_bet,
            n_black_remaining,
            n_red_remaining - 1,
            satiation_point,
        )
        min_return = int(min(a, b))
        if (
            (best_black_bet is None) 
            or (min_return > best_min_return)
            or ((min_return >= best_min_return) and (expected_log_return > best_expected_log_return))
        ):
            best_black_bet = black_bet
            best_min_return = min_return
            best_expected_log_return = expected_log_return
    return best_black_bet


def dynprog_bet_strategy(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
) -> int:
    """return signed bet (positive black, negative red)"""
    bet = basic_bet_rules(holdings=holdings, n_black_remaining=n_black_remaining, n_red_remaining=n_red_remaining)
    if bet is not None:
        return bet
    if holdings >= satiation_point:  # for large values, bet near ideal value, prevents dynamic programming table blow up
        return basic_bet_strategy(holdings, n_black_remaining, n_red_remaining)
    if n_red_remaining > n_black_remaining:
        return -dynprog_bet_strategy(
            holdings=holdings, 
            n_black_remaining=n_red_remaining, # swap
            n_red_remaining=n_black_remaining, 
            satiation_point=satiation_point,
        )
    return _dynprog_bet_strategy_by_search(holdings, n_black_remaining, n_red_remaining, satiation_point)


def mk_traj_frame(i, 
                  *, 
                  initial_stake: int, satiation_point: Optional[int], bet_strategy, decks):
    _, traj = run_bets_int(
        decks[i],
        initial_stake=initial_stake,
        satiation_point=satiation_point,
        bet_strategy=bet_strategy,
    )
    return pd.DataFrame(
        {
            "step": range(len(traj)),
            "stake": np.array(traj) / initial_stake,
            "strategy": bet_strategy.__name__,
            "trajectory": i,
        }
    )



def find_worst_deck(
    holdings: int, n_black_remaining: int, n_red_remaining: int,
    *,
    satiation_point: Optional[int],
    bet_strategy,
):
    """return worst deck, deck value, and estimated number such"""
    @cache
    def find_worst_deck_r_(holdings: int, n_black_remaining: int, n_red_remaining: int):
        """return worst deck, deck value, and estimated number such"""
        # get base cases
        assert holdings >= 0
        assert n_black_remaining >= 0
        assert n_red_remaining >= 0
        if n_black_remaining + n_red_remaining <= 0:
            return [], holdings, 1
        if holdings <= 0:
            return (
                ([False] * n_black_remaining) + ([True] * n_red_remaining), 
                0,
                comb(n_black_remaining + n_red_remaining, n_red_remaining, exact=True),
            )
        # query the strategy
        bet = bet_strategy(holdings, n_black_remaining, n_red_remaining, satiation_point)
        assert bet is not None
        assert isinstance(bet, int)
        assert np.abs(bet) <= holdings
        deck_black, v_black, n_black, dec_red, v_red, n_red = None, None, None, None, None, None
        if n_black_remaining > 0:  # draw black outcomes
            deck_black, v_black, n_black = find_worst_deck_r_(
                int(holdings - np.abs(bet) + 2 * max(bet, 0)), n_black_remaining - 1, n_red_remaining)
        if n_red_remaining > 0:  # draw red outcomes
            dec_red, v_red, n_red = find_worst_deck_r_(
                int(holdings - np.abs(bet) + 2 * max(-bet, 0)), n_black_remaining, n_red_remaining - 1)
        if dec_red is None:
            assert deck_black is not None
            return [False] + deck_black, v_black, n_black
        if deck_black is None:
            return [True] + dec_red, v_red, n_red
        if v_black < v_red:
            return [False] + deck_black, v_black, n_black
        if v_red < v_black:
            return [True] + dec_red, v_red, n_red
        return [True] + dec_red, v_red, n_black + n_red  # Knuth-like estimate of number of nodes
    deck, example_value, n_examples = find_worst_deck_r_(holdings, n_black_remaining, n_red_remaining)
    assert len(deck) == n_black_remaining + n_red_remaining
    assert np.sum(deck) == n_red_remaining
    return np.array(deck), example_value, n_examples
        