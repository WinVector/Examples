from functools import cache
import numpy as np
import pandas as pd
from scipy.special import comb
from typing import List, Optional, Tuple


# define our deck shuffling tool
def k_array_with_t_true(k: int, t: int, *, rng):
    """Create a length-k boolean array with t-True values"""
    is_true = np.array([False] * k, dtype=bool)
    is_true[rng.choice(k, size=t, replace=False)] = True
    return is_true


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
    satiation_point: int,
    bet_strategy,
    limit_to_basic_strat: bool,
) -> float:
    stake = int(initial_stake)
    trajectory = [stake]
    n_red_remaining = int(np.sum(is_red))
    n_black_remaining = len(is_red) - n_red_remaining
    for i, _ in enumerate(is_red):
        # form bet
        bet_red = 0
        bet_black = 0
        net_bet = bet_strategy(
            stake, n_black_remaining, n_red_remaining, satiation_point, limit_to_basic_strat=limit_to_basic_strat,
        )
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
    return (stake / initial_stake, trajectory)


def basic_bet_rules(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
    *,
    limit_to_basic_strat: bool,
) -> Optional[int]:
    """return signed bet (positive black, negative red) if implied by basic rules"""
    if (holdings <= 0) or (n_black_remaining == n_red_remaining):
        return 0  # no favorable bet available
    if n_red_remaining <= 0:
        return holdings  # forced win
    if n_black_remaining <= 0:
        return -holdings  # forced win
    if (holdings <= 1) and (n_black_remaining > 0) and (n_red_remaining > 0):
        return 0  # don't trade entire holdings into uncertainty
    return None


def basic_bet_strategy(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
    *,
    limit_to_basic_strat: bool,
) -> int:
    """return signed bet (positive black, negative red)"""
    if n_red_remaining > n_black_remaining:
        return -basic_bet_strategy(
            holdings=holdings, 
            n_black_remaining=n_red_remaining,   # swap
            n_red_remaining=n_black_remaining,
            satiation_point=satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )
    bet = basic_bet_rules(holdings, n_black_remaining, n_red_remaining, satiation_point,
                          limit_to_basic_strat=limit_to_basic_strat)
    if bet is not None:
        return bet
    v = int(
        max(
            0,
            min(
                holdings,
                np.round(
                    holdings
                    * (n_black_remaining - n_red_remaining)
                    / (n_black_remaining + n_red_remaining)
                ),
            ),
        )
    )
    if (
        (v > 0)
        and (v >= holdings)
        and (n_black_remaining > 0)
        and (n_red_remaining > 0)
    ):
        v = v - 1  # don't trade entire holdings into uncertainty
    return v


@cache
def _bet_amt_min(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
    *,
    limit_to_basic_strat: bool,
) -> Tuple[int, int]:
    """Compute unsigned bet size (internal function use bet_amt_min() as public API)"""
    best_black_bet = None
    best_min_return = None
    basic_bet = basic_bet_strategy(
        holdings, n_black_remaining, n_red_remaining, satiation_point,
        limit_to_basic_strat=limit_to_basic_strat)
    for black_bet in range(holdings + 1):
        if (limit_to_basic_strat) and (black_bet > 0) and (black_bet > basic_bet):
            break
        a = bet_amt_min(
            holdings + black_bet,
            n_black_remaining - 1,
            n_red_remaining,
            satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )
        b = bet_amt_min(
            holdings - black_bet,
            n_black_remaining,
            n_red_remaining - 1,
            satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )
        min_return = int(min(a[1], b[1]))
        if (best_black_bet is None) or (min_return >= best_min_return):  
            # go for largest bet subject to maximizing min_return
            best_black_bet = black_bet
            best_min_return = min_return
    return (best_black_bet, best_min_return)


def bet_amt_min(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
    *,
    limit_to_basic_strat: bool,
) -> Tuple[int, int]:
    """Compute truncated unsigned bet size to achieve highest lower bound. Some value paths truncated by satiation_point."""
    # regularize and eliminate some cases
    if holdings <= 0:
        return (0, 0)
    if n_black_remaining < n_red_remaining:
        n_black_remaining, n_red_remaining = n_red_remaining, n_black_remaining
    # have n_black_remaining >= n_red_remaining and holdings > 0
    if n_black_remaining == n_red_remaining:
        sub = bet_amt_min(
            holdings, n_black_remaining, n_red_remaining - 1, satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )
        return (0, sub[1])
    # have n_black_remaining > n_red_remaining
    if n_red_remaining <= 0:
        return (holdings, holdings * 2**n_black_remaining)
    if (
        holdings > satiation_point
    ):  # early exit to prevent tracking too many possible holdings
        return (0, holdings)  # artificial "don't bet" as not needed to establish minimum
    return _bet_amt_min(
        holdings, n_black_remaining, n_red_remaining, satiation_point,
        limit_to_basic_strat=limit_to_basic_strat,
    )


def dynprog_bet_strategy(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int,
    *,
    limit_to_basic_strat: bool,
) -> int:
    """return signed bet (positive black, negative red)"""
    if n_red_remaining > n_black_remaining:
        return -dynprog_bet_strategy(
            holdings=holdings, 
            n_black_remaining=n_red_remaining, # swap
            n_red_remaining=n_black_remaining, 
            satiation_point=satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )
    bet = basic_bet_rules(holdings, n_black_remaining, n_red_remaining, satiation_point,
                          limit_to_basic_strat=limit_to_basic_strat)
    if bet is not None:
        return bet
    if holdings >= satiation_point:  # for large values, bet near ideal value
        v = int(
            max(
                0,
                min(
                    holdings,
                    np.round(
                        holdings
                        * (n_black_remaining - n_red_remaining)
                        / (n_black_remaining + n_red_remaining)
                    ),
                ),
            )
        )
    else:
        v = bet_amt_min(
            holdings, n_black_remaining, n_red_remaining, satiation_point,
            limit_to_basic_strat=limit_to_basic_strat,
        )[0]
    if (
        (v > 0)
        and (v >= holdings)
        and (n_black_remaining > 0)
        and (n_red_remaining > 0)
    ):
        v = v - 1  # don't trade entire holdings into uncertainty
    return v


def mk_traj_frame(i, 
                  *, 
                  initial_stake: int, satiation_point: int, bet_strategy, decks,
                  limit_to_basic_strat: bool):
    _, traj = run_bets_int(
        decks[i],
        initial_stake=initial_stake,
        satiation_point=satiation_point,
        bet_strategy=bet_strategy,
        limit_to_basic_strat=limit_to_basic_strat,
    )
    return pd.DataFrame(
        {
            "step": range(len(traj)),
            "stake": np.array(traj) / initial_stake,
            "strategy": bet_strategy.__name__,
            "trajectory": i,
        }
    )
