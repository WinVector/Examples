from functools import cache
import numpy as np
import pandas as pd
from scipy.special import comb
from IPython.display import display, Markdown
from typing import Optional, Tuple


# define our deck shuffling tool
def k_array_with_t_true(k: int, t: int, *, rng):
    """Create a length-k boolean array with t-True values"""
    is_true = np.array([False] * k, dtype=bool)
    is_true[rng.choice(k, size=t, replace=False)] = True
    return is_true


# implement our betting strategy
def run_bets(is_red) -> float:
    """Run the Kelly betting strategy for continuous values"""
    stake = 1.0
    n_red_remaining = int(np.sum(is_red))
    n_black_remaining = len(is_red) - n_red_remaining
    for i in range(len(is_red)):
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
) -> float:
    stake = int(initial_stake)
    trajectory = [stake]
    n_red_remaining = int(np.sum(is_red))
    n_black_remaining = len(is_red) - n_red_remaining
    for i in range(len(is_red)):
        # form bet
        bet_red = 0
        bet_black = 0
        net_bet = bet_strategy(
            stake, n_black_remaining, n_red_remaining, satiation_point
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
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int
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
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int
) -> int:
    """return signed bet (positive black, negative red)"""
    if n_red_remaining > n_black_remaining:
        return -basic_bet_strategy(
            holdings, n_red_remaining, n_black_remaining, satiation_point
        )
    bet = basic_bet_rules(holdings, n_black_remaining, n_red_remaining, satiation_point)
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
def _bet_amt_min_mean(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int
) -> Tuple[int, int, float]:
    """Compute unsigned bet size (internal function use bet_amt_min_mean() as public API)"""
    best_black_bet = None
    best_min_return = None
    best_mean_return = None
    for black_bet in range(holdings + 1):
        a = bet_amt_min_mean(
            holdings + black_bet,
            n_black_remaining - 1,
            n_red_remaining,
            satiation_point,
        )
        b = bet_amt_min_mean(
            holdings - black_bet,
            n_black_remaining,
            n_red_remaining - 1,
            satiation_point,
        )
        min_return = int(min(a[1], b[1]))
        mean_return = (n_black_remaining / (n_black_remaining + n_red_remaining)) * a[
            2
        ] + (n_red_remaining / (n_black_remaining + n_red_remaining)) * b[2]
        if (
            (best_black_bet is None)
            or (min_return > best_min_return)
            or ((min_return >= best_min_return) and (mean_return > best_mean_return))
        ):
            best_black_bet = black_bet
            best_min_return = min_return
            best_mean_return = mean_return
    return (best_black_bet, best_min_return, best_mean_return)


def bet_amt_min_mean(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int
) -> Tuple[int, int, float]:
    """Compute truncated unsigned bet size to achieve highest lower bound. Some value paths truncated by satiation_point."""
    # regularize and eliminate some cases
    if holdings <= 0:
        return (0, 0, 0)
    if n_black_remaining < n_red_remaining:
        n_black_remaining, n_red_remaining = n_red_remaining, n_black_remaining
    # have n_black_remaining >= n_red_remaining and holdings > 0
    if n_black_remaining == n_red_remaining:
        sub = bet_amt_min_mean(
            holdings, n_black_remaining, n_red_remaining - 1, satiation_point
        )
        return (0, sub[1], sub[2])
    # have n_black_remaining > n_red_remaining
    if n_red_remaining <= 0:
        return (
            holdings,
            holdings * 2**n_black_remaining,
            holdings * 2**n_black_remaining,
        )
    if (
        holdings > satiation_point
    ):  # early exit to prevent tracking too many possible holdings
        return (
            0,
            holdings,
            holdings,
        )  # artificial "don't bet" as not needed to establish minimum
    return _bet_amt_min_mean(
        holdings, n_black_remaining, n_red_remaining, satiation_point
    )


def dynprog_bet_strategy(
    holdings: int, n_black_remaining: int, n_red_remaining: int, satiation_point: int
) -> int:
    """return signed bet (positive black, negative red)"""
    if n_red_remaining > n_black_remaining:
        return -dynprog_bet_strategy(
            holdings, n_red_remaining, n_black_remaining, satiation_point
        )
    bet = basic_bet_rules(holdings, n_black_remaining, n_red_remaining, satiation_point)
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
        v = bet_amt_min_mean(
            holdings, n_black_remaining, n_red_remaining, satiation_point
        )[0]
    if (
        (v > 0)
        and (v >= holdings)
        and (n_black_remaining > 0)
        and (n_red_remaining > 0)
    ):
        v = v - 1  # don't trade entire holdings into uncertainty
    return v


def mk_traj_frame(i, *, initial_stake: int, satiation_point: int, bet_strategy, decks):
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
