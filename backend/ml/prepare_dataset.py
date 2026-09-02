from pathlib import Path

import pandas as pd

from sklearn.model_selection import GroupShuffleSplit


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "recovery_scenarios.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

TRAIN_FILE = OUTPUT_DIR / "train.csv"
TEST_FILE = OUTPUT_DIR / "test.csv"


# --------------------------------------------------
# FEATURE CONFIGURATION
# --------------------------------------------------

FEATURE_COLUMNS = [

    # CUSTOMER CONTEXT
    "customer_segment",
    "historical_success_rate",
    "average_transaction_amount",

    # TRANSACTION CONTEXT
    "amount",
    "payment_method",
    "transaction_hour",
    "failure_reason",
    "retry_count",

    # RECOVERY ACTION
    "strategy_id",
    "action",
    "delay_hours"
]


TARGET_COLUMN = "recovered"


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def engineer_features(df):

    df = df.copy()


    # ----------------------------------------------
    # PAYMENT VALUE RATIO
    # ----------------------------------------------

    # Compare current transaction value
    # with the customer's normal transaction size.

    df["amount_to_average_ratio"] = (
        df["amount"]
        / df["average_transaction_amount"].replace(0, 1)
    )


    # ----------------------------------------------
    # HIGH VALUE TRANSACTION FLAG
    # ----------------------------------------------

    df["is_high_value_transaction"] = (
        df["amount_to_average_ratio"] > 2
    ).astype(int)


    # ----------------------------------------------
    # LATE NIGHT FLAG
    # ----------------------------------------------

    df["is_late_night"] = (
        df["transaction_hour"]
        .between(0, 5)
    ).astype(int)


    # ----------------------------------------------
    # CUSTOMER SUCCESS CATEGORY
    # ----------------------------------------------

    df["customer_success_category"] = pd.cut(

        df["historical_success_rate"],

        bins=[
            0,
            0.60,
            0.80,
            1.0
        ],

        labels=[
            "LOW",
            "MEDIUM",
            "HIGH"
        ],

        include_lowest=True
    )


    return df


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nML DATASET PREPARATION")
    print("=" * 55)


    # ----------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ----------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # ----------------------------------------------
    # LOAD DATA
    # ----------------------------------------------

    print("\n1. Loading recovery scenarios...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"   Loaded {len(df)} scenarios"
    )


    print(
        f"   Unique failed payments: "
        f"{df['transaction_id'].nunique()}"
    )


    # ----------------------------------------------
    # FEATURE ENGINEERING
    # ----------------------------------------------

    print(
        "\n2. Engineering features..."
    )

    df = engineer_features(df)


    # Add engineered features to model features

    model_features = (
        FEATURE_COLUMNS
        +
        [
            "amount_to_average_ratio",
            "is_high_value_transaction",
            "is_late_night",
            "customer_success_category"
        ]
    )


    print("\n   Final model features:")

    for feature in model_features:

        print(f"   - {feature}")


    # ----------------------------------------------
    # KEEP ONLY REQUIRED COLUMNS
    # ----------------------------------------------

    model_df = df[
        [
            "transaction_id",
            *model_features,
            TARGET_COLUMN
        ]
    ].copy()


    # ----------------------------------------------
    # CHECK MISSING VALUES
    # ----------------------------------------------

    print(
        "\n3. Checking missing values..."
    )

    missing_values = (
        model_df.isnull().sum()
    )

    if missing_values.sum() == 0:

        print(
            "   ✓ No missing values found"
        )

    else:

        print(
            missing_values[
                missing_values > 0
            ]
        )


    # ----------------------------------------------
    # GROUP-BASED TRAIN / TEST SPLIT
    # ----------------------------------------------

    print(
        "\n4. Creating grouped train/test split..."
    )

    splitter = GroupShuffleSplit(

        n_splits=1,

        test_size=0.20,

        random_state=42
    )


    train_index, test_index = next(

        splitter.split(

            model_df,

            groups=model_df[
                "transaction_id"
            ]
        )
    )


    train_df = model_df.iloc[
        train_index
    ].copy()


    test_df = model_df.iloc[
        test_index
    ].copy()


    # ----------------------------------------------
    # REMOVE TRANSACTION ID FROM ML DATA
    # ----------------------------------------------

    # We keep it only for checking leakage.
    # The model itself will not use transaction_id.

    train_ids = set(
        train_df["transaction_id"]
    )

    test_ids = set(
        test_df["transaction_id"]
    )


    overlap = (
        train_ids.intersection(test_ids)
    )


    print(
        f"   Training scenarios: "
        f"{len(train_df)}"
    )

    print(
        f"   Testing scenarios: "
        f"{len(test_df)}"
    )

    print(
        f"   Training transactions: "
        f"{len(train_ids)}"
    )

    print(
        f"   Testing transactions: "
        f"{len(test_ids)}"
    )

    print(
        f"   Transaction overlap: "
        f"{len(overlap)}"
    )


    if len(overlap) == 0:

        print(
            "   ✓ No transaction leakage detected"
        )

    else:

        print(
            "   ✗ WARNING: Transaction leakage detected"
        )


    # ----------------------------------------------
    # SAVE DATASETS
    # ----------------------------------------------

    print(
        "\n5. Saving processed datasets..."
    )


    train_df.to_csv(

        TRAIN_FILE,

        index=False
    )


    test_df.to_csv(

        TEST_FILE,

        index=False
    )


    print(
        f"   Train saved: {TRAIN_FILE}"
    )

    print(
        f"   Test saved: {TEST_FILE}"
    )


    # ----------------------------------------------
    # TARGET DISTRIBUTION
    # ----------------------------------------------

    print(
        "\n6. Recovery distribution..."
    )


    print(
        "\nTRAIN:"
    )

    print(
        (
            train_df[TARGET_COLUMN]
            .value_counts(normalize=True)
            * 100
        ).round(2)
    )


    print(
        "\nTEST:"
    )

    print(
        (
            test_df[TARGET_COLUMN]
            .value_counts(normalize=True)
            * 100
        ).round(2)
    )


    # ----------------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------------

    print("\n" + "=" * 55)

    print(
        "ML DATASET PREPARATION COMPLETE"
    )

    print(
        f"\nTotal features: "
        f"{len(model_features)}"
    )

    print(
        f"Train rows: {len(train_df)}"
    )

    print(
        f"Test rows: {len(test_df)}"
    )

    print("=" * 55)


if __name__ == "__main__":
    main()