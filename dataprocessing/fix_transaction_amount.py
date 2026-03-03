"""
fix_transaction_amount.py
Rewrites 'Transaction amount' in transactions.json to realistic VND values.

Logic:
  - NORMAL (everyday domestic transactions):
      Starbucks, Restaurant, Supermarket, Gas Station,
      Electricity Bill, Netflix Subscription
      → 20,000 – 2,000,000 VND

  - INCOME (salary-related):
      Monthly Salary, Interest Payment Received
      → 3,000,000 – 50,000,000 VND

  - SUSPICIOUS / ANOMALOUS (fraud indicators):
      P2P Game Transfer, P2P Lending Transfer,
      Betting Wallet Deposit, Casino Online Top-up,
      Gaming Chip Purchase, Virtual Slot Funding,
      Private Finance Support, Quick Loan Disbursement,
      Urgent Cash Out
      → 50,000,000 – 1,000,000,000 VND

  - FOREIGN GEO BOOST (outside VN cities) adds extra weight toward
    the high-end range regardless of detail type.
"""

import json
import random

INPUT_PATH  = r'c:\Users\Admin\Documents\dataset\dataset\transactions.json'
OUTPUT_PATH = r'c:\Users\Admin\Documents\dataset\dataset\transactions.json'


NORMAL_MIN    = 20_000
NORMAL_MAX    = 2_000_000

INCOME_MIN    = 3_000_000
INCOME_MAX    = 50_000_000

ANOMALY_MIN   = 50_000_000
ANOMALY_MAX   = 1_000_000_000

# ── Category sets ───────────────────────────────────────────────────────────
NORMAL_DETAILS = {
    'Starbucks', 'Restaurant', 'Supermarket',
    'Gas Station', 'Electricity Bill', 'Netflix Subscription',
}

INCOME_DETAILS = {
    'Monthly Salary', 'Interest Payment Received',
}

ANOMALY_DETAILS = {
    'P2P Game Transfer', 'P2P Lending Transfer',
    'Betting Wallet Deposit', 'Casino Online Top-up',
    'Gaming Chip Purchase', 'Virtual Slot Funding',
    'Private Finance Support', 'Quick Loan Disbursement',
    'Urgent Cash Out',
}

# Locations clearly outside Vietnam → treat as anomaly booster
FOREIGN_GEOS = {
    'Macau - CN', 'Manila - PH', 'Singapore - SG', 'Cambodia - KH',
}

# Round to the nearest 1,000 VND (feels more realistic)
ROUND_TO = 1_000


def round_to(value: float, nearest: int) -> int:
    return int(round(value / nearest) * nearest)


def generate_amount(detail: str, geo: str, rng: random.Random) -> int:
    is_foreign = geo in FOREIGN_GEOS

    if detail in ANOMALY_DETAILS or is_foreign:
        # Anomalous: skew toward higher end using a power distribution
        # so most values cluster in the tens-to-hundreds of millions
        raw = rng.uniform(ANOMALY_MIN, ANOMALY_MAX)
        # Apply a gentle skew: square root scaling biases toward lower end of
        # the anomaly range (so not EVERY fraud is 1 billion)
        skewed = ANOMALY_MIN + (raw - ANOMALY_MIN) ** 0.6 / \
                 (ANOMALY_MAX - ANOMALY_MIN) ** 0.6 * (ANOMALY_MAX - ANOMALY_MIN) * 0.7
        skewed = max(ANOMALY_MIN, min(ANOMALY_MAX, skewed))
        return round_to(skewed, ROUND_TO)

    elif detail in INCOME_DETAILS:
        # Salary-like: roughly log-normal centered around 10–20 million
        import math
        mu    = math.log(12_000_000)
        sigma = 0.6
        raw   = rng.lognormvariate(mu, sigma)
        raw   = max(INCOME_MIN, min(INCOME_MAX, raw))
        return round_to(raw, ROUND_TO)

    else:
        # Normal everyday spending: log-normal centered ~200,000 – 600,000 VND
        import math
        mu    = math.log(350_000)
        sigma = 1.1
        raw   = rng.lognormvariate(mu, sigma)
        raw   = max(NORMAL_MIN, min(NORMAL_MAX, raw))
        return round_to(raw, ROUND_TO)


def main():
    rng = random.Random(42)   # fixed seed for reproducibility

    print(f"Loading: {INPUT_PATH}")
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        transactions = json.load(f)

    print(f"Processing {len(transactions):,} transactions...")

    # Track stats
    categories = {'normal': 0, 'income': 0, 'anomaly': 0}

    for txn in transactions:
        detail = txn.get('Transaction Detail', '')
        geo    = txn.get('Geological', '')

        new_amount = generate_amount(detail, geo, rng)
        txn['Transaction amount'] = new_amount

        # Stats
        is_foreign = geo in FOREIGN_GEOS
        if detail in ANOMALY_DETAILS or is_foreign:
            categories['anomaly'] += 1
        elif detail in INCOME_DETAILS:
            categories['income'] += 1
        else:
            categories['normal'] += 1

    print(f"\nCategory breakdown:")
    for cat, count in categories.items():
        print(f"  {cat:10s}: {count:>6,} transactions")

    # Quick sanity check
    amounts = [t['Transaction amount'] for t in transactions]
    print(f"\nAmount stats:")
    print(f"  Min  : {min(amounts):>15,} VND")
    print(f"  Max  : {max(amounts):>15,} VND")
    print(f"  Avg  : {int(sum(amounts)/len(amounts)):>15,} VND")

    print(f"\nSaving to: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=4)

    print("Done!")


if __name__ == '__main__':
    main()
