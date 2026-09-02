from pathlib import Path

import pandas as pd


# -----------------------------------------
# PATH CONFIGURATION
# -----------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "recovery_scenarios.csv"
)


def main():

    print("\nRECOVERY DATA VALIDATION")
    print("=" * 50)


    # -----------------------------------------
    # 1. LOAD DATA
    # -----------------------------------------

    print("\n1. Loading dataset...")

    df = pd.read_csv(DATA_FILE)

    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")


    # -----------------------------------------
    # 2. BASIC DATASET INFORMATION
    # -----------------------------------------

    print("\n2. Dataset structure...\n")

    print("Columns:")

    for column in df.columns:
        print(f"   - {column}")


    # -----------------------------------------
    # 3. MISSING VALUES
    # -----------------------------------------

    print("\n3. Checking missing values...\n")

    missing_values = df.isnull().sum()

    total_missing = missing_values.sum()

    if total_missing == 0:

        print("   ✓ No missing values found")

    else:

        print(missing_values[missing_values > 0])


    # -----------------------------------------
    # 4. DUPLICATE ROWS
    # -----------------------------------------

    print("\n4. Checking duplicate rows...\n")

    duplicate_count = df.duplicated().sum()

    print(
        f"   Duplicate rows: {duplicate_count}"
    )


    # -----------------------------------------
    # 5. STRATEGY COVERAGE
    # -----------------------------------------

    print("\n5. Checking strategy coverage...\n")

    strategies_per_payment = (
        df.groupby("transaction_id")
        ["strategy_id"]
        .nunique()
    )

    print(
        strategies_per_payment
        .value_counts()
        .sort_index()
    )

    expected_strategies = 4

    invalid_payments = (
        strategies_per_payment[
            strategies_per_payment != expected_strategies
        ]
    )

    if len(invalid_payments) == 0:

        print(
            "\n   ✓ Every failed payment has "
            "all 4 recovery strategies"
        )

    else:

        print(
            f"\n   Warning: {len(invalid_payments)} "
            "payments do not have all strategies"
        )


    # -----------------------------------------
    # 6. RECOVERY DISTRIBUTION
    # -----------------------------------------

    print("\n6. Overall recovery distribution...\n")

    print(
        df["recovered"]
        .value_counts()
    )

    print("\nRecovery rate:")

    print(
        f"   {df['recovered'].mean() * 100:.2f}%"
    )


    # -----------------------------------------
    # 7. RECOVERY RATE BY STRATEGY
    # -----------------------------------------

    print("\n7. Recovery rate by strategy...\n")

    strategy_recovery = (
        df.groupby("strategy_name")
        .agg(
            recovery_rate=(
                "recovered",
                "mean"
            ),

            recovered_amount=(
                "recovered_amount",
                "sum"
            ),

            average_cost=(
                "recovery_cost",
                "mean"
            ),

            average_friction=(
                "customer_friction",
                "mean"
            )
        )
        .sort_values(
            "recovery_rate",
            ascending=False
        )
    )

    strategy_recovery["recovery_rate"] = (
        strategy_recovery["recovery_rate"] * 100
    ).round(2)

    print(strategy_recovery)


    # -----------------------------------------
    # 8. FAILURE REASON × STRATEGY
    # -----------------------------------------

    print(
        "\n8. Recovery rate by failure "
        "reason and strategy...\n"
    )

    failure_strategy = (
        df.pivot_table(
            index="failure_reason",
            columns="strategy_name",
            values="recovered",
            aggfunc="mean"
        )
        * 100
    ).round(2)

    print(failure_strategy)


    # -----------------------------------------
    # 9. BEST STRATEGY PER FAILURE TYPE
    # -----------------------------------------

    print(
        "\n9. Best strategy for each "
        "failure reason...\n"
    )

    for failure_reason, row in (
        failure_strategy.iterrows()
    ):

        best_strategy = row.idxmax()

        best_rate = row.max()

        print(
            f"{failure_reason}: "
            f"{best_strategy} "
            f"({best_rate:.2f}%)"
        )


    # -----------------------------------------
    # 10. VALUE VALIDATION
    # -----------------------------------------

    print(
        "\n10. Validating numeric ranges...\n"
    )

    problems = []


    if df["ground_truth_probability"].min() < 0:
        problems.append(
            "Probability below 0"
        )

    if df["ground_truth_probability"].max() > 1:
        problems.append(
            "Probability above 1"
        )

    if df["customer_friction"].min() < 0:
        problems.append(
            "Customer friction below 0"
        )

    if df["customer_friction"].max() > 1:
        problems.append(
            "Customer friction above 1"
        )

    if df["recovery_cost"].min() < 0:
        problems.append(
            "Negative recovery cost"
        )


    if not problems:

        print(
            "   ✓ All numeric ranges are valid"
        )

    else:

        for problem in problems:

            print(
                f"   ✗ {problem}"
            )


    # -----------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------

    print("\n" + "=" * 50)

    print("VALIDATION COMPLETE")

    print(
        f"\nTotal scenarios: {len(df)}"
    )

    print(
        f"Unique failed payments: "
        f"{df['transaction_id'].nunique()}"
    )

    print(
        f"Recovery strategies: "
        f"{df['strategy_id'].nunique()}"
    )

    print(
        f"Overall recovery rate: "
        f"{df['recovered'].mean() * 100:.2f}%"
    )

    print("=" * 50)


if __name__ == "__main__":
    main()