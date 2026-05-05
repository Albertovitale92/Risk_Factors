# Central Bank Remuneration Curve: Theory & Learning Guide

## Overview

The **Central Bank Remuneration Curve** represents the interest rates paid by a central bank (ECB) on reserve balances held by banks. In the Eurozone, the key rate is the **ECB Deposit Facility Rate (DFR)**, which is the rate the ECB pays banks on overnight deposits.

This curve is the foundation of all FTP pricing because it sets the **risk-free floor**—no bank will lend funds at a rate lower than what the ECB pays.

---

## Key Concepts

### 1. What is the ECB Deposit Facility Rate (DFR)?

The DFR is an **administered rate** set by the ECB's Governing Council as part of its monetary policy stance. As of May 2026:
- **DFR ≈ 3.5%** (hypothetical baseline)
- It's the rate the ECB pays on reserve balances held overnight.
- Banks can deposit any excess liquidity and earn this rate with zero credit risk.

### 2. Why is it Called "Remuneration"?

"Remuneration" simply means "payment for holding balances." It's the interest paid to compensate banks for keeping money at the central bank rather than deploying it elsewhere.

### 3. The Risk-Free Floor Concept

**Central Principle:** No bank lends at a rate lower than the risk-free rate (DFR).

Example:
- If DFR = 3.5%, Deutsche Bank will not lend to another bank at 3.4%.
- Even if Countercyclical Bank asks for a loan at 3.4%, Deutsche Bank would rather deposit €1M at the ECB and earn 3.5%.
- So the interbank lending rate (Overnight Index Swap, ESTR) = DFR + credit/liquidity spread.

Expressing this mathematically:
```
ESTR ≈ DFR + credit_spread
```

---

## How the Curve is Built

Unlike other curves (OIS, swap curves), the central bank remuneration curve is **trivial**: it's a single overnight point.

| Tenor | Maturity (years) | Rate | Curve Type |
|-------|------------------|------|-----------|
| 1D    | 1/365            | 3.5% | cental_bank_remuneration |

**Why only overnight?**
- Central bank deposits are overnight facilities. Longer-term rates are not directly set by the ECB at fixed maturities.
- To price longer-term deposits at the ECB, you'd use the OIS curve (which implicitly includes ECB expectations).

---

## FTP Application: Pricing Central Bank Cash

In our Deutsche Bank balance sheet, we have:
- **central_bank_cash: €130,000m**

### Pricing Logic

1. **Identify the balance:** €130,000m in central bank reserves.
2. **Assign the curve:** Central Bank Remuneration Curve (DFR = 3.5%).
3. **Calculate daily benefit:**
   - Daily interest earned: €130,000m × 3.5% / 365 = €1,246m per day.
   - Annual interest earned: €130,000m × 3.5% = €4,550m per year.

This is the **cost to the bank** of holding this liquidity internally (opportunity cost). From the perspective of the central bank cash portfolio, the FTP "charge" to other business units is essentially zero (they get the benefit of having this liquidity pool), and the Treasury function is credited with this remuneration.

### In FTP Terms

- **FTP Rate** for central bank cash: DFR = 3.5%.
- **FTP Transaction:** The balance-sheet owner (e.g., Liquidity team) receives a credit of €4,550m annually for holding this reserves.
- **Business Unit Impact:** This is a "treasury credit" reflecting the funding benefit of having liquid reserves.

---

## Historical Context & Changes

### Pre-2008: Fixed Rates
Before the financial crisis, reserve balances earned a fixed rate close to the main refinancing rate (MRR). There was little incentive to minimize excess reserves.

### 2008-2022: Near-Zero & Negative Rates
- ECB DFR fell to 0%, then **negative** (e.g., -0.5% in 2021).
- Banks were **penalized** for holding excess reserves, incentivizing lending.
- This inverted the FTP logic: holding central bank cash became a **cost** (negative "remuneration").

### 2022-Present: Hiking Cycle
- ECB raised rates sharply to fight inflation.
- DFR rose from -0.5% to +3.5% (hypothetical 2026).
- Holding reserves became attractive again.
- Liquidity management shifted: banks now want to maximize central bank placements (if they have excess liquidity after lending requirements).

---

## Learning Exercise: Opportunity Cost

### Scenario Setup

**Question:** Deutsche Bank has €130,000m in central bank reserves. The DFR is 3.5%. If the bank lent this cash to other banks at the ESTR (Overnight Index Swap rate) of 3.55%, how much would it earn additionally?

### Calculation

| Metric | Value |
|--------|-------|
| Reserve balance | €130,000m |
| DFR (ECB rate) | 3.5% |
| ESTR (market rate) | 3.55% |
| Spread | 5 bps (0.05%) |
| Annual interest at DFR | €130,000m × 3.5% = €4,550m |
| Annual interest at ESTR | €130,000m × 3.55% = €4,615m |
| **Opportunity cost (foregone profit)** | **€4,615m - €4,550m = €65m** |

### Interpretation

- If Deutsche Bank could lend all €130,000m at ESTR instead of holding at ECB, it would earn **€65m more annually**.
- However, the bank **must** hold a minimum reserve (regulatory requirement), so only the "excess" portion can be deployed.
- This illustrates why liquidity management is critical: even 5 bps on €130B is €65m per year.

### Stress Scenario

**What if rates rise?**

| Scenario | DFR | ESTR | Balance | Annual Benefit to Lend (vs. ECB) |
|----------|-----|------|---------|----------------------------------|
| Current | 3.5% | 3.55% | €130,000m | €65m |
| +100 bps | 4.5% | 4.55% | €130,000m | €65m (same spread!) |
| -50 bps | 3.0% | 3.05% | €130,000m | €65m (same spread!) |

**Key Insight:** The spread is constant, so the opportunity cost scales with the balance size, not the absolute rate level.

---

## Connection to Other Curves

### Overnight Index Curve → Money Market Curve

The central bank remuneration curve feeds into the Overnight Index Curve:

```
ESTR = DFR + credit spread (typically 3-10 bps in normal times)
```

From there, you interpolate to other maturities:

```
EURIBOR 3M = ESTR + term premium + credit spread
EURIBOR 6M = ESTR + longer term premium + credit spread
```

### FTP Cascade

```
DFR (Central Bank Rate)
  ↓
ESTR (Overnight Index) = DFR + ~5 bps
  ↓
1M Money Market Rate = DFR + ~10 bps
  ↓
3M EURIBOR = DFR + ~20 bps
  ↓
6M EURIBOR = DFR + ~25 bps
  ↓
1Y Swap = DFR + ~30 bps
  ↓
Longer-term swap/funding curves
```

Each step adds liquidity premium, term premium, or credit spread.

---

## Interview Relevance

### Why Banks Ask About This

1. **Monetary Policy Understanding:**
   - "How does ECB policy transmission affect your FTP?"
   - Answer: ECB rate changes propagate through the DFR → ESTR → other curves.

2. **Liquidity Management:**
   - "How much excess liquidity does your bank hold, and why?"
   - Answer: Regulatory minima + buffer for contingencies. Held at DFR if earning positive real return.

3. **Negative Rate Era:**
   - "Your bank paid to hold central bank cash in 2021. How did that affect pricing?"
   - Answer: Made all deposit customers more expensive (had to pay them to hold deposits when we were being penalized by ECB). Liquidity became a cost, not an asset.

4. **IRRBB (Interest Rate Risk in Banking Book):**
   - "If the ECB raises rates 100 bps, how much does your NIM improve?"
   - Answer: Depends on asset/liability mix and repricing behavior, but excess liquidity at DFR improves significantly.

### Common Follow-ups

- **"How sensitive is your FTP to the DFR?"** → Very; it's the foundation.
- **"What assumptions do you make about future DFR?"** → Typically follow market forwards (OIS curve).
- **"How do you hedge DFR risk?"** → Via interest rate swaps or term repo facilities.

---

## Code Implementation

### Using the Curve in FTP

```python
from risk_factors.curves import (
    create_central_bank_remuneration_curve,
    compute_opportunity_cost_of_excess_liquidity,
    get_ecb_rates_snapshot,
)

# Step 1: Get today's ECB rates
ecb_rates = get_ecb_rates_snapshot(
    deposit_facility_rate=0.035,
    lending_facility_rate=0.060,
    as_of_date="2026-05-05"
)

# Step 2: Create the curve
dfr_curve = create_central_bank_remuneration_curve(dfr=0.035)
print(dfr_curve)

# Step 3: Calculate opportunity cost (learning exercise)
opportunity = compute_opportunity_cost_of_excess_liquidity(
    balance_eur_m=130_000,
    ecb_rate=0.035,
    market_rate=0.0355,
    annual=True
)
print(f"Annual opportunity cost: €{opportunity['opportunity_cost']:.0f}m")
```

### In FTP Simulation

In `ftp_simulation`, when pricing the `central_bank_cash` portfolio:

```python
from risk_factors.curves import create_central_bank_remuneration_curve

# Load prepared FTP balance sheet
prepared = prepare_ftp_balance_sheet(balance_sheet, repricing_rules, segmentation)

# Filter for central bank cash
cb_cash = prepared[prepared['ftp_model_portfolio'] == 'central_bank_cash']

# Load central bank remuneration curve
dfr = 0.035
dfr_curve = create_central_bank_remuneration_curve(dfr=dfr)

# Calculate FTP cost (credit for the bank)
cb_cash['ftp_rate'] = dfr
cb_cash['ftp_credit_eur_m'] = cb_cash['amount_eur_m'] * dfr / 365  # daily
```

---

## Summary Table

| Attribute | Value |
|-----------|-------|
| **Curve Name** | Central Bank Remuneration Curve |
| **Currency** | EUR |
| **Base Rate** | ECB Deposit Facility Rate (DFR) |
| **Maturity Range** | Overnight (1D) |
| **Tenor Range** | N/A (single point) |
| **Liquidity Premium** | None (risk-free) |
| **Credit Spread** | None (ECB is counterparty) |
| **Behavioural Model** | None (administered rate) |
| **Regulatory Component** | Reserve requirements (ECB) |
| **Data Source** | ECB official rates |
| **Update Frequency** | Daily (when ECB changes policy) |
| **Learning Objective** | Understand risk-free rates and monetary policy transmission |
| **Interview Relevance** | Explains how central bank policy affects bank funding costs and NIM |
| **Usage in FTP** | Pricing central bank deposits and excess liquidity buffers |

---

## Further Reading & Extensions

1. **ECB Policy Rates:** https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml
2. **ESTR (Euro Short-Term Rate):** Successor to EONIA; the new overnight benchmark.
3. **Negative Rate Era:** Study 2014-2021 period when DFR was negative (-0.5%); how banks priced deposits during this time.
4. **Term Structure:** If the ECB announces a 1-year fixed-rate deposit facility, you'd add a second point to the curve (1Y maturity).

---

## Next Steps

Once you're comfortable with this curve, proceed to:
1. **Overnight Index Curve** (ESTR/EONIA) → Learn how credit spreads are added.
2. **Money Market Curve** (EURIBOR) → Learn term premiums.
3. **Matched Swap Curve** → Learn multi-curve framework.

