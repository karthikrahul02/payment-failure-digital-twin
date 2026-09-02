
from pathlib import Path
import joblib
import pandas as pd
import json

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

TRAIN_FILE = PROJECT_ROOT / "data" / "processed" / "train.csv"
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "test.csv"

MODEL_DIR = PROJECT_ROOT / "artifacts" / "models"

MODEL_FILE = MODEL_DIR / "recovery_predictor.joblib"
METRICS_FILE = MODEL_DIR / "model_metrics.json"


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TARGET_COLUMN = "recovered"
ID_COLUMN = "transaction_id"


# --------------------------------------------------
# MAIN TRAINING FUNCTION
# --------------------------------------------------

def main():

    print("\nRECOVERY PREDICTION MODEL TRAINING")
    print("=" * 60)

    # ----------------------------------------------
    # CREATE MODEL DIRECTORY
    # ----------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ----------------------------------------------
    # LOAD DATA
    # ----------------------------------------------

    print("\n1. Loading processed datasets...")

    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    print(f"   Training rows: {len(train_df)}")
    print(f"   Testing rows: {len(test_df)}")

    # ----------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # ----------------------------------------------

    required_columns = {
        TARGET_COLUMN,
        ID_COLUMN
    }

    missing_train = required_columns - set(train_df.columns)
    missing_test = required_columns - set(test_df.columns)

    if missing_train:
        raise ValueError(
            f"Missing columns in training data: {sorted(missing_train)}"
        )

    if missing_test:
        raise ValueError(
            f"Missing columns in test data: {sorted(missing_test)}"
        )

    # ----------------------------------------------
    # SPLIT FEATURES AND TARGET
    # ----------------------------------------------

    print("\n2. Preparing features and target...")

    X_train = train_df.drop(
        columns=[
            TARGET_COLUMN,
            ID_COLUMN
        ]
    )

    y_train = train_df[TARGET_COLUMN]

    X_test = test_df.drop(
        columns=[
            TARGET_COLUMN,
            ID_COLUMN
        ]
    )

    y_test = test_df[TARGET_COLUMN]

    # Make sure train/test have identical feature columns
    if list(X_train.columns) != list(X_test.columns):
        raise ValueError(
            "Training and test datasets do not have identical feature columns."
        )

    print(f"   Number of features: {X_train.shape[1]}")

    # ----------------------------------------------
    # IDENTIFY FEATURE TYPES
    # ----------------------------------------------

    categorical_features = (
        X_train
        .select_dtypes(
            include=["object", "category", "bool"]
        )
        .columns
        .tolist()
    )

    numerical_features = (
        X_train
        .select_dtypes(
            include=["number"]
        )
        .columns
        .tolist()
    )

    print(
        f"\n   Numerical features: "
        f"{len(numerical_features)}"
    )

    for feature in numerical_features:
        print(f"      - {feature}")

    print(
        f"\n   Categorical features: "
        f"{len(categorical_features)}"
    )

    for feature in categorical_features:
        print(f"      - {feature}")

    # ----------------------------------------------
    # PREPROCESSING
    # ----------------------------------------------

    print("\n3. Building preprocessing pipeline...")

    numerical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            )
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                )
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_transformer,
                numerical_features
            ),
            (
                "categorical",
                categorical_transformer,
                categorical_features
            )
        ]
    )

    # ----------------------------------------------
    # MODEL
    # ----------------------------------------------

    print("\n4. Creating Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    # ----------------------------------------------
    # COMPLETE PIPELINE
    # ----------------------------------------------

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    # ----------------------------------------------
    # TRAIN MODEL
    # ----------------------------------------------

    print("\n5. Training model...")

    pipeline.fit(
        X_train,
        y_train
    )

    print("   ✓ Training complete")

    # ----------------------------------------------
    # EVALUATE MODEL
    # ----------------------------------------------

    print("\n6. Evaluating model...")

    y_pred = pipeline.predict(X_test)

    y_prob = pipeline.predict_proba(X_test)[:, 1]

    # ----------------------------------------------
    # METRICS
    # ----------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    print("\nMODEL PERFORMANCE")

    print(f"\nAccuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    # ----------------------------------------------
    # CLASSIFICATION REPORT
    # ----------------------------------------------

    print("\nCLASSIFICATION REPORT")

    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )

    # ----------------------------------------------
    # CONFUSION MATRIX
    # ----------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print("CONFUSION MATRIX")
    print(cm)

    # ----------------------------------------------
    # FEATURE IMPORTANCE
    # ----------------------------------------------

    print("\n7. Calculating feature importance...")

    trained_model = pipeline.named_steps["model"]
    trained_preprocessor = pipeline.named_steps["preprocessor"]

    raw_importances = trained_model.feature_importances_

    transformed_feature_names = (
        trained_preprocessor.get_feature_names_out()
    )

    original_features = X_train.columns.tolist()

    feature_importance_map = {
        feature: 0.0
        for feature in original_features
    }

    for transformed_name, importance in zip(
        transformed_feature_names,
        raw_importances
    ):

        clean_name = transformed_name.split(
            "__",
            1
        )[-1]

        for original_feature in original_features:

            if (
                clean_name == original_feature
                or clean_name.startswith(
                    original_feature + "_"
                )
            ):

                feature_importance_map[
                    original_feature
                ] += float(importance)

                break

    # ----------------------------------------------
    # CONVERT TO PERCENTAGES
    # ----------------------------------------------

    total_importance = sum(
        feature_importance_map.values()
    )

    feature_importance = []

    if total_importance > 0:

        for feature, importance in (
            feature_importance_map.items()
        ):

            percentage = (
                importance / total_importance
            ) * 100

            feature_importance.append(
                {
                    "feature": feature,
                    "importance": round(
                        float(importance),
                        4
                    ),
                    "percentage": round(
                        float(percentage),
                        2
                    )
                }
            )

    # ----------------------------------------------
    # SORT BY IMPORTANCE
    # ----------------------------------------------

    feature_importance.sort(
        key=lambda item: item["importance"],
        reverse=True
    )

    top_feature_importance = feature_importance[:10]

    print("\nTOP FEATURE IMPORTANCE")

    for item in top_feature_importance:
        print(
            f"   {item['feature']}: "
            f"{item['percentage']:.2f}%"
        )

    # ----------------------------------------------
    # SAVE MODEL
    # ----------------------------------------------

    print("\n8. Saving trained model...")

    joblib.dump(
        pipeline,
        MODEL_FILE
    )

    print("   Model saved to:")
    print(f"   {MODEL_FILE}")

    # ----------------------------------------------
    # SAVE MODEL EVALUATION METRICS
    # ----------------------------------------------

    metrics = {

    "accuracy":
        round(float(accuracy), 4),

    "precision":
        round(float(precision), 4),

    "recall":
        round(float(recall), 4),

    "f1_score":
        round(float(f1), 4),

    "roc_auc":
        round(float(roc_auc), 4),

    "confusion_matrix":
        cm.tolist(),

    "model":
        "RandomForestClassifier",

    "n_estimators":
        300,

    "max_depth":
        12,

    "min_samples_split":
        10,

    "min_samples_leaf":
        5,

    "feature_importance":
        top_feature_importance
}

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    print("   Metrics saved to:")
    print(f"   {METRICS_FILE}")

    # ----------------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------------

    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETE")

    print(
        f"\nFinal ROC-AUC: "
        f"{roc_auc:.4f}"
    )

    print("Model location:")
    print(f"{MODEL_FILE}")

    print("=" * 60)


if __name__ == "__main__":
    main()

