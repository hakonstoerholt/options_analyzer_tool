"""
Visual report for an analyzed strategy: a payoff diagram for the top opportunity,
a screening scatter across strikes (annualized return vs probability, coloured by
IV), and an expected-move map showing where the strikes sit relative to the
one-sigma move. Saves a single dark-themed figure.
"""

import os
import datetime as dt

import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless: write PNGs without a display
import matplotlib.pyplot as plt
from matplotlib import gridspec

BG = "#0e1116"
FG = "#e6e6e6"
GRID = "#2a2f3a"
ACCENT = "#f5b301"             # amber
PROFIT = "#3fb950"
LOSS = "#f85149"
SPOT = "#58a6ff"


def _style(ax):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=FG, labelsize=8)
    ax.grid(True, color=GRID, lw=0.5, alpha=0.6)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)


def _payoff(strike, premium, spot, S, strategy):
    """Per-contract (100 share) P/L at expiry across underlying prices S."""
    if strategy == "cash_secured_put":
        # short put: keep premium above strike, lose intrinsic below it
        return (premium - np.maximum(strike - S, 0.0)) * 100
    # covered_call: long stock from spot, short call capped at strike
    return (np.minimum(S, strike) - spot + premium) * 100


def _payoff_panel(ax, opp, spot, strategy):
    strike, premium = opp["strike"], opp["bid"]
    lo = max(0.01, min(strike, spot) * 0.80)
    hi = max(strike, spot) * 1.20
    S = np.linspace(lo, hi, 400)
    pl = _payoff(strike, premium, spot, S, strategy)

    ax.plot(S, pl, color=ACCENT, lw=2)
    ax.axhline(0, color=FG, lw=0.8, alpha=0.5)
    ax.fill_between(S, pl, 0, where=(pl >= 0), color=PROFIT, alpha=0.18)
    ax.fill_between(S, pl, 0, where=(pl < 0), color=LOSS, alpha=0.18)

    breakeven = strike - premium if strategy == "cash_secured_put" else spot - premium
    ax.axvline(spot, color=SPOT, ls=":", lw=1.2, label=f"spot {spot:.0f}")
    ax.axvline(strike, color=FG, ls="--", lw=1, alpha=0.7, label=f"strike {strike:g}")
    ax.axvline(breakeven, color=PROFIT, ls="-.", lw=1, alpha=0.7,
               label=f"breakeven {breakeven:.1f}")

    ax.set_title("Payoff at expiry (top strike by yield)", fontsize=9)
    ax.set_xlabel("underlying at expiry")
    ax.set_ylabel("P/L per contract ($)")
    leg = ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID, labelcolor=FG)
    leg.get_frame().set_alpha(0.7)
    _style(ax)


def _screen_panel(ax, opps):
    x = [o["probability_otm"] for o in opps]          # %
    y = [o["annualized_return"] for o in opps]         # %
    iv = [o["implied_volatility"] * 100 for o in opps]  # %
    sc = ax.scatter(x, y, c=iv, cmap="viridis", s=46,
                    edgecolor="black", linewidth=0.3, alpha=0.9)
    # ring the top pick (the one shown in the payoff panel)
    ax.scatter([opps[0]["probability_otm"]], [opps[0]["annualized_return"]],
               s=160, facecolors="none", edgecolors=ACCENT, linewidths=1.6)

    cbar = ax.figure.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("implied vol (%)", color=FG, fontsize=8)
    cbar.ax.tick_params(colors=FG, labelsize=7)
    cbar.outline.set_edgecolor(GRID)

    ax.set_title("Strike screen: yield vs probability", fontsize=9)
    ax.set_xlabel("probability OTM (%)")
    ax.set_ylabel("annualized return (%)")
    _style(ax)


def _move_panel(ax, opps, spot, vol_metrics):
    days = opps[0]["days_to_expiry"]
    iv = vol_metrics.get("implied_volatility", 0.0)
    one_sigma = spot * iv * np.sqrt(days / 365.0)

    if one_sigma > 0:
        ax.axvspan(spot - 2 * one_sigma, spot + 2 * one_sigma,
                   color=SPOT, alpha=0.07, label="+/- 2 sigma")
        ax.axvspan(spot - one_sigma, spot + one_sigma,
                   color=SPOT, alpha=0.15, label="+/- 1 sigma")
    ax.axvline(spot, color=SPOT, ls=":", lw=1.4)

    strikes = [o["strike"] for o in opps]
    ann = [o["annualized_return"] for o in opps]
    sc = ax.scatter(strikes, np.zeros_like(strikes), c=ann, cmap="plasma",
                    s=60, edgecolor="black", linewidth=0.3, zorder=3)
    cbar = ax.figure.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("annualized return (%)", color=FG, fontsize=8)
    cbar.ax.tick_params(colors=FG, labelsize=7)
    cbar.outline.set_edgecolor(GRID)

    ax.set_yticks([])
    ax.set_title(f"Candidate strikes vs expected move ({days}d, IV {iv*100:.0f}%)",
                 fontsize=9)
    ax.set_xlabel("price")
    leg = ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID, labelcolor=FG, loc="upper right")
    leg.get_frame().set_alpha(0.7)
    _style(ax)


def build_report(ticker, strategy, results, expiration, out_dir="charts"):
    """Render the three-panel report and return the saved file path."""
    opps = results.get("opportunities", [])
    if not opps:
        raise ValueError("No opportunities to chart")

    spot = results["stock_info"]["current_price"]
    vol_metrics = results.get("volatility_metrics", {})

    fig = plt.figure(figsize=(12, 8), facecolor=BG)
    gs = gridspec.GridSpec(2, 2, height_ratios=[3, 2], hspace=0.38, wspace=0.22)
    _payoff_panel(fig.add_subplot(gs[0, 0]), opps[0], spot, strategy)
    _screen_panel(fig.add_subplot(gs[0, 1]), opps)
    _move_panel(fig.add_subplot(gs[1, :]), opps, spot, vol_metrics)

    pretty = strategy.replace("_", " ")
    fig.suptitle(f"{ticker}   {pretty}   exp {expiration}   spot ${spot:.2f}",
                 color=FG, fontsize=13, y=0.98)

    os.makedirs(out_dir, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d")
    path = os.path.join(out_dir, f"{ticker}_{strategy}_{stamp}.png")
    fig.savefig(path, dpi=130, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path
