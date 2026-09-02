import random
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

RANDOM_SEED = 42

NUM_CUSTOMERS = 1000
MIN_TRANSACTIONS_PER_CUSTOMER = 5
MAX_TRANSACTIONS_PER_CUSTOMER = 15


random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# Project paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# CUSTOMER GENERATION
# --------------------------------------------------

def generate_customers():

    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"CUST_{i:05d}"

        # Customer reliability segment
        segment = random.choices(
            population=[
                "HIGH_RELIABILITY",
                "MEDIUM_RELIABILITY",
                "LOW_RELIABILITY"
            ],
            weights=[0.35, 0.45, 0.20],
            k=1
        )[0]

        # Different customer groups behave differently
        if segment == "HIGH_RELIABILITY":

            success_rate = round(
                np.random.uniform(0.88, 0.99),
                2
            )

            avg_amount = round(
                np.random.uniform(1000, 15000),
                2
            )

        elif segment == "MEDIUM_RELIABILITY":

            success_rate = round(
                np.random.uniform(0.65, 0.87),
                2
            )

            avg_amount = round(
                np.random.uniform(500, 10000),
                2
            )

        else:

            success_rate = round(
                np.random.uniform(0.35, 0.64),
                2
            )

            avg_amount = round(
                np.random.uniform(200, 7000),
                2
            )

        previous_transactions = random.randint(5, 100)

        previous_failures = int(
            previous_transactions * (1 - success_rate)
        )

        customers.append({
            "customer_id": customer_id,
            "customer_segment": segment,
            "historical_success_rate": success_rate,
            "average_transaction_amount": avg_amount,
            "previous_transactions": previous_transactions,
            "previous_failures": previous_failures
        })

    return pd.DataFrame(customers)


# --------------------------------------------------
# PAYMENT FAILURE LOGIC
# --------------------------------------------------

def calculate_failure_probability(customer, amount, payment_method):

    base_failure_probability = (
        1 - customer["historical_success_rate"]
    )

    probability = base_failure_probability

    # Very high-value transactions can have slightly
    # higher probability of failure
    if amount > customer["average_transaction_amount"] * 2:
        probability += 0.05

    # Payment method behaviour
    if payment_method == "CARD":
        probability += 0.03

    elif payment_method == "NET_BANKING":
        probability += 0.02

    # Keep probability within a reasonable range
    probability = max(0.02, min(probability, 0.60))

    return probability


def generate_failure_reason(payment_method):

    reasons = [
        "TEMPORARY_BANK_ERROR",
        "NETWORK_TIMEOUT",
        "INSUFFICIENT_FUNDS",
        "AUTHENTICATION_FAILURE",
        "USER_ABANDONMENT",
        "TECHNICAL_ERROR"
    ]

    weights = [
        0.25,
        0.20,
        0.20,
        0.15,
        0.10,
        0.10
    ]

    # Slight adjustment for UPI
    if payment_method == "UPI":

        reasons = [
            "TEMPORARY_BANK_ERROR",
            "NETWORK_TIMEOUT",
            "INSUFFICIENT_FUNDS",
            "AUTHENTICATION_FAILURE",
            "USER_ABANDONMENT",
            "TECHNICAL_ERROR"
        ]

        weights = [
            0.25,
            0.25,
            0.15,
            0.10,
            0.15,
            0.10
        ]

    return random.choices(
        population=reasons,
        weights=weights,
        k=1
    )[0]


# --------------------------------------------------
# TRANSACTION GENERATION
# --------------------------------------------------

def generate_transactions(customers_df):

    transactions = []

    transaction_counter = 1

    for _, customer in customers_df.iterrows():

        number_of_transactions = random.randint(
            MIN_TRANSACTIONS_PER_CUSTOMER,
            MAX_TRANSACTIONS_PER_CUSTOMER
        )

        for _ in range(number_of_transactions):

            transaction_id = (
                f"TXN_{transaction_counter:07d}"
            )

            transaction_counter += 1

            # Transaction amount varies around
            # customer's average behaviour
            amount = np.random.normal(
                loc=customer["average_transaction_amount"],
                scale=customer["average_transaction_amount"] * 0.40
            )

            amount = max(100, round(amount, 2))

            payment_method = random.choices(
                population=[
                    "UPI",
                    "CARD",
                    "NET_BANKING",
                    "WALLET"
                ],
                weights=[0.45, 0.30, 0.15, 0.10],
                k=1
            )[0]

            transaction_hour = random.randint(0, 23)

            failure_probability = calculate_failure_probability(
                customer,
                amount,
                payment_method
            )

            is_failed = (
                random.random() < failure_probability
            )

            if is_failed:

                status = "FAILED"

                failure_reason = generate_failure_reason(
                    payment_method
                )

                retry_count = random.choices(
                    population=[0, 1, 2, 3],
                    weights=[0.60, 0.25, 0.10, 0.05],
                    k=1
                )[0]

            else:

                status = "SUCCESS"

                failure_reason = None

                retry_count = 0

            transactions.append({
                "transaction_id": transaction_id,
                "customer_id": customer["customer_id"],
                "customer_segment": customer["customer_segment"],
                "historical_success_rate":
                    customer["historical_success_rate"],
                "average_transaction_amount":
                    customer["average_transaction_amount"],
                "amount": amount,
                "payment_method": payment_method,
                "transaction_hour": transaction_hour,
                "status": status,
                "failure_reason": failure_reason,
                "retry_count": retry_count
            })

    return pd.DataFrame(transactions)


# --------------------------------------------------
# SAVE DATA
# --------------------------------------------------

def save_datasets(customers_df, transactions_df):

    failed_payments_df = transactions_df[
        transactions_df["status"] == "FAILED"
    ].copy()

    customers_path = OUTPUT_DIR / "customers.csv"

    transactions_path = OUTPUT_DIR / "transactions.csv"

    failed_payments_path = (
        OUTPUT_DIR / "failed_payments.csv"
    )

    customers_df.to_csv(
        customers_path,
        index=False
    )

    transactions_df.to_csv(
        transactions_path,
        index=False
    )

    failed_payments_df.to_csv(
        failed_payments_path,
        index=False
    )

    return (
        customers_path,
        transactions_path,
        failed_payments_path
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nGENERATING SYNTHETIC PAYMENT DATA...\n")

    print("1. Generating customers...")

    customers_df = generate_customers()

    print(
        f"   Created {len(customers_df)} customers"
    )


    print("2. Generating transactions...")

    transactions_df = generate_transactions(
        customers_df
    )

    print(
        f"   Created {len(transactions_df)} transactions"
    )


    print("3. Extracting failed payments...")

    failed_payments = transactions_df[
        transactions_df["status"] == "FAILED"
    ]

    print(
        f"   Created {len(failed_payments)} failed payments"
    )


    print("4. Saving datasets...")

    paths = save_datasets(
        customers_df,
        transactions_df
    )

    print("\nDATASETS CREATED SUCCESSFULLY\n")

    print(f"Customers: {paths[0]}")
    print(f"Transactions: {paths[1]}")
    print(f"Failed Payments: {paths[2]}")


    print("\nPAYMENT STATUS DISTRIBUTION:")

    print(
        transactions_df["status"]
        .value_counts()
    )


    print("\nFAILURE REASON DISTRIBUTION:")

    print(
        failed_payments["failure_reason"]
        .value_counts()
    )


if __name__ == "__main__":
    main()