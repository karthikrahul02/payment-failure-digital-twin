from pathlib import Path
import json

import pandas as pd


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

TEST_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "test.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "evaluation"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "digital_twin_evaluation.json"
)

CSV_FILE = (
    RESULTS_DIR
    / "digital_twin_evaluation.csv"
)


# ==========================================================
# DIGITAL TWIN
# ==========================================================

from digital_twin.twin_engine import PaymentFailureDigitalTwin


# ==========================================================
# CONFIGURATION
# ==========================================================

TARGET_COLUMN = "recovered"

ID_COLUMN = "transaction_id"


BASELINE_STRATEGIES = [
    "Retry after 30 minutes",
    "Retry after 6 hours",
    "Send Payment Link",
    "Wait",
]


# ==========================================================
# HELPERS
# ==========================================================

def get_strategy_name(strategy):

    return (
        strategy.get("strategy_name")
        or strategy.get("strategy")
        or strategy.get("name")
        or strategy.get("action")
        or "Unknown"
    )


def get_utility(strategy):

    return float(
        strategy.get(
            "utility_score",
            0
        ) or 0
    )


def get_probability(strategy):

    return float(
        strategy.get(
            "recovery_probability",
            0
        ) or 0
    )


def get_expected_recovery(strategy):

    return float(
        strategy.get(
            "expected_recovered_amount",
            0
        ) or 0
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print(
        "\nDIGITAL TWIN EXPERIMENTAL EVALUATION"
    )

    print(
        "=" * 60
    )


    # ------------------------------------------------------
    # CREATE RESULTS DIRECTORY
    # ------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # ------------------------------------------------------
    # LOAD TEST DATA
    # ------------------------------------------------------

    print(
        "\n1. Loading test dataset..."
    )

    test_df = pd.read_csv(
        TEST_FILE
    )

    print(
        f"   Test transactions: "
        f"{len(test_df)}"
    )


    # ------------------------------------------------------
    # INITIALIZE DIGITAL TWIN
    # ------------------------------------------------------

    print(
        "\n2. Initializing Digital Twin..."
    )

    twin = PaymentFailureDigitalTwin()

    print(
        "   Digital Twin initialized."
    )


    # ------------------------------------------------------
    # STORAGE
    # ------------------------------------------------------

    transaction_results = []


    # ------------------------------------------------------
    # RUN EVALUATION
    # ------------------------------------------------------

    print(
        "\n3. Evaluating transactions..."
    )


    for count, (index, row) in enumerate(test_df.iterrows()):

        # Keep actual historical outcome separately.
        actual_recovered = row.get(
            TARGET_COLUMN
        )


        # Convert row to dictionary.
        payment_data = row.to_dict()


        # Remove target before prediction.
        payment_data.pop(
            TARGET_COLUMN,
            None
        )


        try:

            result = twin.simulate(
                payment_data
            )

        except Exception as error:

            print(
                f"   Skipping transaction "
                f"{index}: {error}"
            )

            continue


        simulations = result.get(
            "simulations",
            []
        )


        recommended_strategy = (
            result.get(
                "recommended_strategy",
                {}
            )
        )


        recommended_name = (
            get_strategy_name(
                recommended_strategy
            )
        )


        # --------------------------------------------------
        # STRATEGY LOOKUP
        # --------------------------------------------------

        strategy_lookup = {
            get_strategy_name(strategy):
                strategy
            for strategy in simulations
        }


        # --------------------------------------------------
        # DIGITAL TWIN RESULT
        # --------------------------------------------------

        digital_twin_utility = (
            get_utility(
                recommended_strategy
            )
        )


        digital_twin_probability = (
            get_probability(
                recommended_strategy
            )
        )


        digital_twin_recovery = (
            get_expected_recovery(
                recommended_strategy
            )
        )


        # --------------------------------------------------
        # GET UTILITY OF EACH FIXED POLICY
        # --------------------------------------------------

        retry_30_utility = get_utility(
            strategy_lookup.get(
                "Retry after 30 minutes",
                {}
            )
        )


        retry_6h_utility = get_utility(
            strategy_lookup.get(
                "Retry after 6 hours",
                {}
            )
        )


        payment_link_utility = get_utility(
            strategy_lookup.get(
                "Send Payment Link",
                {}
            )
        )


        wait_utility = get_utility(
            strategy_lookup.get(
                "Wait",
                {}
            )
        )


        # --------------------------------------------------
        # STORE TRANSACTION RESULT
        # --------------------------------------------------

        transaction_results.append({

            "transaction_id":
                payment_data.get(
                    ID_COLUMN
                ),

            "recommended_strategy":
                recommended_name,

            "digital_twin_utility":
                round(
                    digital_twin_utility,
                    4
                ),

            "digital_twin_probability":
                round(
                    digital_twin_probability,
                    4
                ),

            "digital_twin_expected_recovery":
                round(
                    digital_twin_recovery,
                    2
                ),

            "retry_30_utility":
                round(
                    retry_30_utility,
                    4
                ),

            "retry_6h_utility":
                round(
                    retry_6h_utility,
                    4
                ),

            "payment_link_utility":
                round(
                    payment_link_utility,
                    4
                ),

            "wait_utility":
                round(
                    wait_utility,
                    4
                ),

            "actual_recovered":
                actual_recovered

        })


        # --------------------------------------------------
        # PROGRESS
        # --------------------------------------------------

        if (
            (count + 1) % 100 == 0
        ):

            print(
                f"   Processed "
                f"{count + 1}/"
                f"{len(test_df)}"
            )


    # ======================================================
    # DATAFRAME
    # ======================================================

    results_df = pd.DataFrame(
        transaction_results
    )


    if results_df.empty:

        print(
            "\nNo transactions were evaluated."
        )

        return


    # ======================================================
    # FIXED POLICY PERFORMANCE
    # ======================================================

    print(
        "\n4. Calculating policy performance..."
    )


    digital_twin_mean = (
        results_df[
            "digital_twin_utility"
        ].mean()
    )


    retry_30_mean = (
        results_df[
            "retry_30_utility"
        ].mean()
    )


    retry_6h_mean = (
        results_df[
            "retry_6h_utility"
        ].mean()
    )


    payment_link_mean = (
        results_df[
            "payment_link_utility"
        ].mean()
    )


    wait_mean = (
        results_df[
            "wait_utility"
        ].mean()
    )


    # ======================================================
    # ADVANTAGE OVER EACH BASELINE
    # ======================================================

    advantage_retry_30 = (
        digital_twin_mean
        - retry_30_mean
    )


    advantage_retry_6h = (
        digital_twin_mean
        - retry_6h_mean
    )


    advantage_payment_link = (
        digital_twin_mean
        - payment_link_mean
    )


    advantage_wait = (
        digital_twin_mean
        - wait_mean
    )


    # ======================================================
    # PERCENTAGE IMPROVEMENT
    # ======================================================

    def percentage_improvement(
        digital_twin,
        baseline
    ):

        if baseline == 0:

            return 0.0

        return (
            (
                digital_twin
                - baseline
            )
            / abs(baseline)
        ) * 100


    improvement_retry_30 = (
        percentage_improvement(
            digital_twin_mean,
            retry_30_mean
        )
    )


    improvement_retry_6h = (
        percentage_improvement(
            digital_twin_mean,
            retry_6h_mean
        )
    )


    improvement_payment_link = (
        percentage_improvement(
            digital_twin_mean,
            payment_link_mean
        )
    )


    improvement_wait = (
        percentage_improvement(
            digital_twin_mean,
            wait_mean
        )
    )


    # ======================================================
    # STRATEGY DISTRIBUTION
    # ======================================================

    strategy_distribution = (
        results_df[
            "recommended_strategy"
        ]
        .value_counts()
        .to_dict()
    )


    # ======================================================
    # BEST FIXED POLICY
    # ======================================================

    fixed_policy_scores = {

        "Retry after 30 minutes":
            retry_30_mean,

        "Retry after 6 hours":
            retry_6h_mean,

        "Send Payment Link":
            payment_link_mean,

        "Wait":
            wait_mean

    }


    best_fixed_policy = max(
        fixed_policy_scores,
        key=lambda x: fixed_policy_scores[x]
    )


    best_fixed_policy_utility = (
        fixed_policy_scores[
            best_fixed_policy
        ]
    )


    advantage_over_best_fixed = (
        digital_twin_mean
        - best_fixed_policy_utility
    )


    improvement_over_best_fixed = (
        percentage_improvement(
            digital_twin_mean,
            best_fixed_policy_utility
        )
    )


    # ======================================================
    # EXPERIMENT SUMMARY
    # ======================================================

    summary = {

        "experiment":
            "Digital Twin vs Fixed Recovery Policies",

        "evaluation_type":
            "Model-based policy evaluation",

        "test_transactions":
            int(len(results_df)),

        "digital_twin_mean_utility":
            round(
                float(
                    digital_twin_mean
                ),
                4
            ),

        "fixed_policy_mean_utility": {

            "Retry after 30 minutes":
                round(
                    float(
                        retry_30_mean
                    ),
                    4
                ),

            "Retry after 6 hours":
                round(
                    float(
                        retry_6h_mean
                    ),
                    4
                ),

            "Send Payment Link":
                round(
                    float(
                        payment_link_mean
                    ),
                    4
                ),

            "Wait":
                round(
                    float(
                        wait_mean
                    ),
                    4
                )

        },

        "advantage_over_fixed_policy": {

            "Retry after 30 minutes":
                round(
                    float(
                        advantage_retry_30
                    ),
                    4
                ),

            "Retry after 6 hours":
                round(
                    float(
                        advantage_retry_6h
                    ),
                    4
                ),

            "Send Payment Link":
                round(
                    float(
                        advantage_payment_link
                    ),
                    4
                ),

            "Wait":
                round(
                    float(
                        advantage_wait
                    ),
                    4
                )

        },

        "percentage_improvement": {

            "Retry after 30 minutes":
                round(
                    float(
                        improvement_retry_30
                    ),
                    2
                ),

            "Retry after 6 hours":
                round(
                    float(
                        improvement_retry_6h
                    ),
                    2
                ),

            "Send Payment Link":
                round(
                    float(
                        improvement_payment_link
                    ),
                    2
                ),

            "Wait":
                round(
                    float(
                        improvement_wait
                    ),
                    2
                )

        },

        "best_fixed_policy":
            best_fixed_policy,

        "best_fixed_policy_utility":
            round(
                float(
                    best_fixed_policy_utility
                ),
                4
            ),

        "advantage_over_best_fixed_policy":
            round(
                float(
                    advantage_over_best_fixed
                ),
                4
            ),

        "percentage_improvement_over_best_fixed":
            round(
                float(
                    improvement_over_best_fixed
                ),
                2
            ),

        "recommended_strategy_distribution":
            strategy_distribution

    }


    # ======================================================
    # SAVE JSON
    # ======================================================

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4
        )


    # ======================================================
    # SAVE CSV
    # ======================================================

    results_df.to_csv(
        CSV_FILE,
        index=False
    )


    # ======================================================
    # PRINT RESULTS
    # ======================================================

    print(
        "\nEXPERIMENT RESULTS"
    )

    print(
        "-" * 60
    )

    print(
        f"Transactions evaluated: "
        f"{len(results_df)}"
    )


    print(
        "\nMean utility:"
    )

    print(
        f"   Digital Twin: "
        f"{digital_twin_mean:.4f}"
    )

    print(
        f"   Retry 30 min: "
        f"{retry_30_mean:.4f}"
    )

    print(
        f"   Retry 6 hours: "
        f"{retry_6h_mean:.4f}"
    )

    print(
        f"   Payment Link: "
        f"{payment_link_mean:.4f}"
    )

    print(
        f"   Wait: "
        f"{wait_mean:.4f}"
    )


    print(
        "\nDigital Twin advantage:"
    )

    print(
        f"   vs Retry 30 min: "
        f"{advantage_retry_30:.4f}"
    )

    print(
        f"   vs Retry 6 hours: "
        f"{advantage_retry_6h:.4f}"
    )

    print(
        f"   vs Payment Link: "
        f"{advantage_payment_link:.4f}"
    )

    print(
        f"   vs Wait: "
        f"{advantage_wait:.4f}"
    )


    print(
        "\nBest fixed policy:"
    )

    print(
        f"   {best_fixed_policy}"
    )

    print(
        f"   Utility: "
        f"{best_fixed_policy_utility:.4f}"
    )


    print(
        "\nDigital Twin improvement "
        "over best fixed policy:"
    )

    print(
        f"   {improvement_over_best_fixed:.2f}%"
    )


    print(
        "\nRecommended strategy distribution:"
    )


    for strategy, count in (
        strategy_distribution.items()
    ):

        print(
            f"   {strategy}: {count}"
        )


    print(
        "\nEvaluation results saved to:"
    )

    print(
        RESULTS_FILE
    )

    print(
        CSV_FILE
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "EXPERIMENT COMPLETE"
    )

    print(
        "=" * 60
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()