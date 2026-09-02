import random
from pathlib import Path

import numpy as np
import pandas as pd

from policies.recovery_policies import RECOVERY_POLICIES


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "failed_payments.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "recovery_scenarios.csv"
)


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def sigmoid(value):
    """
    Converts any number into a probability
    between 0 and 1.
    """

    return 1 / (1 + np.exp(-value))


# --------------------------------------------------
# HIDDEN GROUND TRUTH ENGINE
# --------------------------------------------------

def calculate_ground_truth_probability(payment, policy):

    """
    This function represents the hidden behaviour
    of the payment ecosystem.

    Our future ML model will NOT use this function.

    It will only receive the generated scenarios
    and learn the patterns from data.
    """

    score = 0.0


    # ----------------------------------------------
    # CUSTOMER RELIABILITY
    # ----------------------------------------------

    success_rate = float(
        payment["historical_success_rate"]
    )

    # More reliable customers are generally
    # more likely to complete a recovery
    score += (success_rate - 0.5) * 2.2


    # ----------------------------------------------
    # RETRY COUNT PENALTY
    # ----------------------------------------------

    retry_count = int(
        payment["retry_count"]
    )

    # Too many retries may indicate a difficult
    # payment failure
    score -= retry_count * 0.25


    # ----------------------------------------------
    # FAILURE REASON
    # ----------------------------------------------

    failure_reason = payment["failure_reason"]

    strategy = policy["strategy_id"]


    # TEMPORARY BANK ERROR
    if failure_reason == "TEMPORARY_BANK_ERROR":

        if strategy == "RETRY_30_MIN":
            score += 0.7

        elif strategy == "RETRY_6_HOURS":
            score += 1.1

        elif strategy == "PAYMENT_LINK":
            score += 0.2

        elif strategy == "WAIT":
            score += 0.3


    # NETWORK TIMEOUT
    elif failure_reason == "NETWORK_TIMEOUT":

        if strategy == "RETRY_30_MIN":
            score += 0.9

        elif strategy == "RETRY_6_HOURS":
            score += 0.6

        elif strategy == "PAYMENT_LINK":
            score += 0.2

        elif strategy == "WAIT":
            score += 0.1


    # INSUFFICIENT FUNDS
    elif failure_reason == "INSUFFICIENT_FUNDS":

        if strategy == "RETRY_30_MIN":
            score -= 0.5

        elif strategy == "RETRY_6_HOURS":
            score += 0.5

        elif strategy == "PAYMENT_LINK":
            score += 0.2

        elif strategy == "WAIT":
            score += 0.4


    # AUTHENTICATION FAILURE
    elif failure_reason == "AUTHENTICATION_FAILURE":

        if strategy == "RETRY_30_MIN":
            score += 0.1

        elif strategy == "RETRY_6_HOURS":
            score += 0.2

        elif strategy == "PAYMENT_LINK":
            score += 0.9

        elif strategy == "WAIT":
            score -= 0.2


    # USER ABANDONMENT
    elif failure_reason == "USER_ABANDONMENT":

        if strategy == "RETRY_30_MIN":
            score -= 0.4

        elif strategy == "RETRY_6_HOURS":
            score -= 0.2

        elif strategy == "PAYMENT_LINK":
            score += 1.0

        elif strategy == "WAIT":
            score -= 0.5


    # TECHNICAL ERROR
    elif failure_reason == "TECHNICAL_ERROR":

        if strategy == "RETRY_30_MIN":
            score += 0.6

        elif strategy == "RETRY_6_HOURS":
            score += 0.8

        elif strategy == "PAYMENT_LINK":
            score += 0.3

        elif strategy == "WAIT":
            score += 0.2


    # ----------------------------------------------
    # PAYMENT METHOD EFFECT
    # ----------------------------------------------

    payment_method = payment["payment_method"]

    if payment_method == "UPI":

        if policy["action"] == "RETRY":
            score += 0.2

    elif payment_method == "CARD":

        if strategy == "PAYMENT_LINK":
            score += 0.15

    elif payment_method == "NET_BANKING":

        if policy["delay_hours"] >= 1:
            score += 0.1


    # ----------------------------------------------
    # TRANSACTION VALUE EFFECT
    # ----------------------------------------------

    amount = float(payment["amount"])

    average_amount = float(
        payment["average_transaction_amount"]
    )


    # Very high-value transactions may have slightly
    # lower spontaneous recovery probability
    if amount > average_amount * 2:
        score -= 0.2


    # ----------------------------------------------
    # TIME OF TRANSACTION
    # ----------------------------------------------

    transaction_hour = int(
        payment["transaction_hour"]
    )


    # Late-night payments can have slightly lower
    # immediate recovery rates
    if transaction_hour >= 0 and transaction_hour <= 5:

        if strategy == "RETRY_30_MIN":
            score -= 0.2

        elif strategy == "RETRY_6_HOURS":
            score += 0.2


    # ----------------------------------------------
    # NATURAL RANDOMNESS
    # ----------------------------------------------

    # Real payment systems are not deterministic.
    # We introduce controlled randomness.
    noise = np.random.normal(
        loc=0,
        scale=0.25
    )

    score += noise


    # ----------------------------------------------
    # FINAL PROBABILITY
    # ----------------------------------------------

    probability = sigmoid(score)

    # Keep probabilities realistic
    probability = max(
        0.02,
        min(probability, 0.98)
    )

    return round(probability, 4)


# --------------------------------------------------
# GENERATE CUSTOMER FRICTION
# --------------------------------------------------

def calculate_customer_friction(payment, policy):

    friction = policy["base_friction"]

    retry_count = int(
        payment["retry_count"]
    )

    # Multiple previous retries increase annoyance
    friction += retry_count * 0.08


    # Payment links require user interaction
    if policy["action"] == "PAYMENT_LINK":
        friction += 0.10


    # Keep friction between 0 and 1
    friction = max(
        0,
        min(friction, 1)
    )

    return round(friction, 3)


# --------------------------------------------------
# GENERATE RECOVERY COST
# --------------------------------------------------

def calculate_recovery_cost(payment, policy):

    cost = policy["base_cost"]

    amount = float(payment["amount"])

    # Larger transactions can involve slightly
    # more operational value at risk
    if amount > 10000:
        cost += 1.5

    elif amount > 5000:
        cost += 0.5


    # Add small real-world variation
    variation = np.random.uniform(
        -0.25,
        0.25
    )

    cost += variation

    cost = max(0, cost)

    return round(cost, 2)


# --------------------------------------------------
# GENERATE RECOVERY SCENARIOS
# --------------------------------------------------

def generate_recovery_scenarios(failed_payments_df):

    scenarios = []

    total_payments = len(failed_payments_df)


    for index, (_, payment) in enumerate(
        failed_payments_df.iterrows(),
        start=1
    ):

        for policy in RECOVERY_POLICIES:


            # Calculate hidden probability
            probability = (
                calculate_ground_truth_probability(
                    payment,
                    policy
                )
            )


            # Generate actual outcome
            recovered = int(
                random.random() < probability
            )


            # Recovery amount
            amount = float(payment["amount"])

            if recovered:
                recovered_amount = amount
            else:
                recovered_amount = 0.0


            # Cost
            recovery_cost = (
                calculate_recovery_cost(
                    payment,
                    policy
                )
            )


            # Customer friction
            customer_friction = (
                calculate_customer_friction(
                    payment,
                    policy
                )
            )


            scenarios.append({

                # ----------------------------------
                # PAYMENT INFORMATION
                # ----------------------------------

                "transaction_id":
                    payment["transaction_id"],

                "customer_id":
                    payment["customer_id"],

                "customer_segment":
                    payment["customer_segment"],

                "historical_success_rate":
                    payment[
                        "historical_success_rate"
                    ],

                "average_transaction_amount":
                    payment[
                        "average_transaction_amount"
                    ],

                "amount":
                    amount,

                "payment_method":
                    payment["payment_method"],

                "transaction_hour":
                    payment["transaction_hour"],

                "failure_reason":
                    payment["failure_reason"],

                "retry_count":
                    payment["retry_count"],


                # ----------------------------------
                # RECOVERY STRATEGY
                # ----------------------------------

                "strategy_id":
                    policy["strategy_id"],

                "strategy_name":
                    policy["name"],

                "action":
                    policy["action"],

                "delay_hours":
                    policy["delay_hours"],


                # ----------------------------------
                # SIMULATED GROUND TRUTH
                # ----------------------------------

                "ground_truth_probability":
                    probability,

                "recovered":
                    recovered,

                "recovered_amount":
                    recovered_amount,

                "recovery_cost":
                    recovery_cost,

                "customer_friction":
                    customer_friction
            })


        # Progress update
        if index % 500 == 0:

            print(
                f"Processed "
                f"{index}/{total_payments} "
                f"failed payments"
            )


    return pd.DataFrame(scenarios)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print(
        "\nGENERATING RECOVERY SCENARIOS...\n"
    )


    # ----------------------------------------------
    # LOAD FAILED PAYMENTS
    # ----------------------------------------------

    print(
        "1. Loading failed payments..."
    )

    failed_payments_df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"   Loaded "
        f"{len(failed_payments_df)} "
        f"failed payments"
    )


    # ----------------------------------------------
    # GENERATE SCENARIOS
    # ----------------------------------------------

    print(
        "\n2. Generating recovery scenarios..."
    )

    scenarios_df = (
        generate_recovery_scenarios(
            failed_payments_df
        )
    )

    print(
        f"   Generated "
        f"{len(scenarios_df)} "
        f"recovery scenarios"
    )


    # ----------------------------------------------
    # SAVE DATASET
    # ----------------------------------------------

    print(
        "\n3. Saving recovery scenarios..."
    )

    scenarios_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"   Saved to: {OUTPUT_FILE}"
    )


    # ----------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------

    print(
        "\nRECOVERY SCENARIOS CREATED SUCCESSFULLY"
    )


    print(
        "\nRECOVERY RATE BY STRATEGY:\n"
    )

    print(
        scenarios_df
        .groupby("strategy_name")["recovered"]
        .mean()
        .sort_values(
            ascending=False
        )
    )


    print(
        "\nAVERAGE RECOVERY COST:\n"
    )

    print(
        scenarios_df
        .groupby("strategy_name")["recovery_cost"]
        .mean()
        .sort_values(
            ascending=True
        )
    )


    print(
        "\nAVERAGE CUSTOMER FRICTION:\n"
    )

    print(
        scenarios_df
        .groupby("strategy_name")["customer_friction"]
        .mean()
        .sort_values(
            ascending=True
        )
    )


if __name__ == "__main__":
    main()