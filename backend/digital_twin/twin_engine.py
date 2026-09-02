from pathlib import Path
import joblib
import pandas as pd


class PaymentFailureDigitalTwin:

    def __init__(self):

        # Go from:
        # backend/digital_twin/twin_engine.py
        # to:
        # payment-failure-digital-twin/
        base_dir = Path(__file__).resolve().parents[2]

        model_path = (
            base_dir
            / "artifacts"
            / "models"
            / "recovery_predictor.joblib"
        )

        print(f"Loading model from: {model_path}")

        self.model = joblib.load(model_path)

        self.strategies = {
            "Retry after 30 minutes": {
                "retry_delay_hours": 0.5,
                "strategy_id": "STRAT_01",
                "action": "RETRY",
                "average_cost": 2.30,
                "friction": 0.07,
                "retry_count": 1
            },

            "Retry after 6 hours": {
                "retry_delay_hours": 6,
                "strategy_id": "STRAT_02",
                "action": "RETRY",
                "average_cost": 2.30,
                "friction": 0.15,
                "retry_count": 1
            },

            "Send Payment Link": {
                "retry_delay_hours": 0,
                "strategy_id": "STRAT_03",
                "action": "PAYMENT_LINK",
                "average_cost": 8.30,
                "friction": 0.50,
                "retry_count": 0
            },

            "Wait": {
                "retry_delay_hours": 24,
                "strategy_id": "STRAT_04",
                "action": "WAIT",
                "average_cost": 0.34,
                "friction": 0.10,
                "retry_count": 0
            }
        }

    def get_expected_columns(self):

        """
        Get the exact input columns expected by
        the trained preprocessing pipeline.
        """

        # Case 1: Pipeline directly exposes feature names
        if hasattr(self.model, "feature_names_in_"):
            return list(self.model.feature_names_in_)

        # Case 2: Pipeline contains a preprocessing step
        if hasattr(self.model, "named_steps"):

            if "preprocessor" in self.model.named_steps:

                preprocessor = (
                    self.model.named_steps["preprocessor"]
                )

                if hasattr(preprocessor, "feature_names_in_"):
                    return list(
                        preprocessor.feature_names_in_
                    )

        return None

    def create_scenarios(self, failed_payment):

        scenarios = []

        for strategy_name, strategy in self.strategies.items():

            # IMPORTANT:
            # Start with the COMPLETE original payment
            scenario = dict(failed_payment)

            # Add strategy-specific features
            scenario["strategy_id"] = (
                strategy["strategy_id"]
            )

            scenario["action"] = (
                strategy["action"]
            )

            scenario["retry_count"] = (
                strategy["retry_count"]
            )

            scenario["delay_hours"] = (
                strategy["retry_delay_hours"]
            )

            # Calculate amount compared to customer's
            # historical average transaction value
            average_amount = scenario.get(
                "average_transaction_amount",
                1
            )

            if average_amount == 0:
                average_amount = 1

            scenario["amount_to_average_ratio"] = round(
                scenario["amount"] / average_amount,
                2
            )

            # High-value payment
            scenario["is_high_value_transaction"] = int(
                scenario["amount"] >= 10000
            )

            # Transaction hour
            transaction_hour = scenario.get(
                "transaction_hour",
                12
            )

            scenario["transaction_hour"] = transaction_hour

            # Late-night transaction
            scenario["is_late_night"] = int(
                transaction_hour >= 23
                or transaction_hour <= 5
            )

            scenarios.append({
                "strategy_name": strategy_name,
                "data": scenario,
                "cost": strategy["average_cost"],
                "friction": strategy["friction"]
            })

        return scenarios

    def prepare_model_input(self, scenario):

        """
        Prepare the scenario using exactly the columns
        expected by the trained ML model.
        """

        expected_columns = self.get_expected_columns()

        df = pd.DataFrame([scenario])

        #print("\nModel expected columns:")
        #print(expected_columns)

        #print("\nScenario columns:")
        #print(list(df.columns))

        if expected_columns is not None:

            # Check what is missing
            missing_columns = set(
                expected_columns
            ) - set(df.columns)

            if missing_columns:
                raise ValueError(
                    f"Digital Twin is missing features: "
                    f"{missing_columns}"
                )

            # Keep only the columns used during training
            # and preserve their expected order
            df = df[expected_columns]

        return df

    def predict_recovery_probability(self, scenario):

        df = self.prepare_model_input(scenario)

        probability = (
            self.model.predict_proba(df)[0][1]
        )

        return float(probability)

    def calculate_utility(
        self,
        amount,
        recovery_probability,
        cost,
        friction
    ):

        expected_recovered_amount = (
            amount * recovery_probability
        )

        friction_penalty = (
            amount
            * friction
            * 0.05
        )

        utility_score = (
            expected_recovered_amount
            - cost
            - friction_penalty
        )

        return {
            "expected_recovered_amount": round(
                expected_recovered_amount,
                2
            ),

            "friction_penalty": round(
                friction_penalty,
                2
            ),

            "utility_score": round(
                utility_score,
                2
            )
        }

    def simulate(self, failed_payment):

        scenarios = self.create_scenarios(
            failed_payment
        )

        results = []

        for scenario in scenarios:

            probability = (
                self.predict_recovery_probability(
                    scenario["data"]
                )
            )

            utility = self.calculate_utility(
                amount=failed_payment["amount"],
                recovery_probability=probability,
                cost=scenario["cost"],
                friction=scenario["friction"]
            )

            recovery_probability_percent = round(
                probability * 100,
                2
            )

            # Recovery risk is the probability that
            # the failed payment will NOT be recovered.
            recovery_risk_percent = round(
                (1 - probability) * 100,
                2
            )

            results.append({
                "strategy_name": scenario["strategy_name"],

                # Store probability as 0-1 because that is the actual
                # probability returned by the ML model.
                "recovery_probability":
                    round(probability, 4),

                # Human-readable percentage.
                "recovery_probability_percent":
                    recovery_probability_percent,

                "recovery_risk_percent":
                    recovery_risk_percent,

                "average_cost":
                    scenario["cost"],

                "friction":
                    scenario["friction"],

                "expected_recovered_amount":
                    utility["expected_recovered_amount"],

                "friction_penalty":
                    utility["friction_penalty"],

                "utility_score":
                    utility["utility_score"]
            })

        # Highest utility first
        results = sorted(
            results,
            key=lambda x: x["utility_score"],
            reverse=True
        )

        # ---------------------------------------------
        # DECISION ANALYTICS
        # ---------------------------------------------

        recommended = results[0]

        second_best = (
            results[1]
            if len(results) > 1
            else None
        )

        # Difference between the winning strategy
        # and the second-best strategy.
        if second_best:

            utility_advantage = round(
                recommended["utility_score"]
                - second_best["utility_score"],
                2
            )

            recovery_probability_advantage = round(
                recommended["recovery_probability"]
                - second_best["recovery_probability"],
                2
            )

            expected_recovery_difference = round(
                recommended["expected_recovered_amount"]
                - second_best["expected_recovered_amount"],
                2
            )

        else:

            utility_advantage = 0

            recovery_probability_advantage = 0

            expected_recovery_difference = 0

        # ---------------------------------------------
        # DECISION CONFIDENCE
        # ---------------------------------------------

        # A larger utility gap means the recommendation
        # is more clearly separated from alternatives.
        #
        # This is NOT ML model confidence.
        # It is decision confidence based on the
        # separation between the top two strategies.

        if utility_advantage >= 100:
            decision_confidence = "HIGH"

        elif utility_advantage >= 25:
            decision_confidence = "MEDIUM"

        else:
            decision_confidence = "LOW"

        # ---------------------------------------------
        # RECOMMENDATION
        # ---------------------------------------------

        recommended_strategy = {
            **recommended,

            "decision_confidence":
                decision_confidence,

            "utility_advantage":
                utility_advantage,

            "recovery_probability_advantage":
                recovery_probability_advantage,

            "expected_recovery_difference":
                expected_recovery_difference,

            "second_best_strategy":
                second_best["strategy_name"]
                if second_best
                else None
        }

        return {
            "failed_payment": failed_payment,

            "simulations": results,

            "recommended_strategy":
                recommended_strategy
        }