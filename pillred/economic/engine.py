"""
PILL RED Economic Engine (Gate 6).
Evaluates capital realization, friction, drawdown, and bankroll preservation across separate ledgers.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ActiveWagerLedger:
    """Tracks financial performance for events where active capital was staked."""
    wagers_count: int
    winning_wagers: int
    losing_wagers: int
    push_wagers: int
    total_stake: float
    gross_return: float
    friction_cost: float
    net_pnl: float
    roi_pct: float
    win_rate: float
    profit_factor: float
    max_drawdown_units: float
    max_drawdown_pct: float
    drawdown_duration_events: int
    capital_trajectory: List[float] = field(default_factory=list)


@dataclass
class AvoidedLossLedger:
    """Tracks bankroll preservation when predictions recommended skipping the event."""
    skipped_events_count: int
    correctly_avoided_losses_count: int
    missed_winning_opportunities_count: int
    capital_preserved: float
    missed_gross_profit: float
    net_preservation_benefit: float
    filter_precision: float


@dataclass
class EconomicEvaluationResult:
    """Standardized output of the PILL RED Economic Truth Engine."""
    active_ledger: ActiveWagerLedger
    avoided_ledger: AvoidedLossLedger
    total_events_observed: int
    valid_settled_events: int
    exposure_rate: float
    verdict: str  # "PASS" | "INCONCLUSIVE" | "FAIL"
    justification: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EconomicEngine:
    """
    Evaluates real-money and paper-trading economic performance without double-counting.
    """

    @classmethod
    def evaluate(
        cls,
        predictions: List[Any],
        actuals: List[Any],
        payout_multipliers: List[float],
        unit_stake: float = 1.0,
        stakes: Optional[List[float]] = None,
        house_edge_friction: float = 0.04, # e.g. 4% casino edge or broker fee
        initial_bankroll: float = 100.0,
        min_active_wagers: int = 10
    ) -> EconomicEvaluationResult:
        """
        Processes a sequence of predictions, outcomes, and payouts into separate economic ledgers.
        Strictly excludes unsettled, pending, or corrupt records.
        """
        n = len(predictions)
        if n != len(actuals) or n != len(payout_multipliers):
            raise ValueError("Predictions, actuals, and payout_multipliers must be identical lengths.")

        # 0. Strict Data Integrity: Filter out unsettled / None records
        valid_indices = []
        for i in range(n):
            p = predictions[i]
            a = actuals[i]
            m = payout_multipliers[i]
            if p is not None and a is not None and m is not None and str(a).strip().upper() not in ('NONE', 'UNSETTLED', 'NULL'):
                valid_indices.append(i)

        valid_n = len(valid_indices)
        if valid_n == 0:
            empty_active = ActiveWagerLedger(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, [initial_bankroll])
            empty_avoided = AvoidedLossLedger(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
            return EconomicEvaluationResult(empty_active, empty_avoided, n, 0, 0.0, "INCONCLUSIVE", "Zero settled events evaluated.")

        # Helper to get stake for event i
        def get_stake(idx: int) -> float:
            if stakes and idx < len(stakes) and stakes[idx] is not None and stakes[idx] > 0:
                return float(stakes[idx])
            return float(unit_stake)

        # --- 1. ACTIVE WAGER LEDGER ---
        active_valid_indices = [i for i in valid_indices if str(predictions[i]).strip().upper() not in ('0', 'NO_WIN', '0.0', 'SKIP', 'FALSE')]
        wagers_count = len(active_valid_indices)
        winning_wagers = 0
        losing_wagers = 0
        push_wagers = 0
        total_stake = sum(get_stake(i) for i in active_valid_indices)
        gross_return = 0.0
        gross_profit_sum = 0.0
        gross_loss_sum = 0.0

        current_bankroll = initial_bankroll
        peak_bankroll = initial_bankroll
        max_drawdown_units = 0.0
        max_drawdown_pct = 0.0
        current_dd_duration = 0
        max_dd_duration = 0
        trajectory = [current_bankroll]

        for i in active_valid_indices:
            p = str(predictions[i]).strip().upper()
            a = str(actuals[i]).strip().upper()
            mult = float(payout_multipliers[i])
            stk = get_stake(i)
            is_hit = (p == a)

            if is_hit and mult > 1.0:
                winning_wagers += 1
                payout = stk * mult
                profit = payout - stk
                gross_return += payout
                gross_profit_sum += profit
                current_bankroll += profit
            elif is_hit and mult == 1.0:
                # Push / Breakeven
                push_wagers += 1
                gross_return += stk
            else:
                losing_wagers += 1
                gross_loss_sum += stk
                current_bankroll -= stk

            trajectory.append(current_bankroll)

            # Drawdown Tracking
            if current_bankroll > peak_bankroll:
                peak_bankroll = current_bankroll
                current_dd_duration = 0
            else:
                current_dd_duration += 1
                dd_units = peak_bankroll - current_bankroll
                dd_pct = (dd_units / peak_bankroll) if peak_bankroll > 0 else 0.0
                if dd_units > max_drawdown_units:
                    max_drawdown_units = dd_units
                if dd_pct > max_drawdown_pct:
                    max_drawdown_pct = dd_pct
                if current_dd_duration > max_dd_duration:
                    max_dd_duration = current_dd_duration

        friction_cost = total_stake * house_edge_friction
        net_pnl = (gross_return - total_stake) - friction_cost
        roi_pct = (net_pnl / total_stake * 100.0) if total_stake > 0 else 0.0
        win_rate = (winning_wagers / wagers_count) if wagers_count > 0 else 0.0
        profit_factor = (gross_profit_sum / gross_loss_sum) if gross_loss_sum > 0 else (99.0 if gross_profit_sum > 0 else 0.0)

        active_ledger = ActiveWagerLedger(
            wagers_count=wagers_count,
            winning_wagers=winning_wagers,
            losing_wagers=losing_wagers,
            push_wagers=push_wagers,
            total_stake=total_stake,
            gross_return=gross_return,
            friction_cost=friction_cost,
            net_pnl=net_pnl,
            roi_pct=roi_pct,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown_units=max_drawdown_units,
            max_drawdown_pct=max_drawdown_pct,
            drawdown_duration_events=max_dd_duration,
            capital_trajectory=trajectory
        )

        # --- 2. AVOIDED LOSS LEDGER ---
        skipped_valid_indices = [i for i in valid_indices if str(predictions[i]).strip().upper() in ('0', 'NO_WIN', '0.0', 'SKIP', 'FALSE')]
        skipped_count = len(skipped_valid_indices)
        correctly_avoided = 0
        missed_wins = 0
        capital_preserved = 0.0
        missed_gross_profit = 0.0

        for i in skipped_valid_indices:
            a = str(actuals[i]).strip().upper()
            mult = float(payout_multipliers[i])
            stk = get_stake(i)
            if a in ('0', 'NO_WIN', '0.0', 'FALSE') or mult == 0:
                correctly_avoided += 1
                capital_preserved += stk
            else:
                missed_wins += 1
                missed_gross_profit += (stk * mult - stk)

        net_preservation_benefit = capital_preserved - missed_gross_profit
        filter_precision = (correctly_avoided / skipped_count) if skipped_count > 0 else 0.0

        avoided_ledger = AvoidedLossLedger(
            skipped_events_count=skipped_count,
            correctly_avoided_losses_count=correctly_avoided,
            missed_winning_opportunities_count=missed_wins,
            capital_preserved=capital_preserved,
            missed_gross_profit=missed_gross_profit,
            net_preservation_benefit=net_preservation_benefit,
            filter_precision=filter_precision
        )

        # --- 3. GATE 6 VERDICT ---
        exposure_rate = wagers_count / valid_n
        if wagers_count < min_active_wagers:
            if skipped_count >= min_active_wagers and net_preservation_benefit > 0:
                verdict = "INCONCLUSIVE"
                justification = f"Active wagers (N={wagers_count}) below minimum threshold; positive capital preservation (+{net_preservation_benefit:.2f} units) observed without active betting."
            else:
                verdict = "INCONCLUSIVE"
                justification = f"Insufficient active wagers (N={wagers_count} < {min_active_wagers}) to evaluate capital edge."
        elif net_pnl > 0.0 and max_drawdown_pct < 0.50:
            verdict = "PASS"
            justification = f"Positive realized net P/L (+{net_pnl:.2f} units, ROI: {roi_pct:+.1f}%) after {house_edge_friction*100:.1f}% friction, with controlled drawdown ({max_drawdown_pct*100:.1f}%)."
        else:
            verdict = "FAIL"
            justification = f"Negative or zero net P/L ({net_pnl:+.2f} units) after friction (ROI: {roi_pct:+.1f}%, Max Drawdown: {max_drawdown_pct*100:.1f}%)."

        return EconomicEvaluationResult(
            active_ledger=active_ledger,
            avoided_ledger=avoided_ledger,
            total_events_observed=n,
            valid_settled_events=valid_n,
            exposure_rate=exposure_rate,
            verdict=verdict,
            justification=justification
        )
