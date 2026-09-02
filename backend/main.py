from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import FailedPaymentRequest
from digital_twin.twin_engine import PaymentFailureDigitalTwin

import json
from pathlib import Path


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title="Payment Failure Digital Twin API",
    description="""
    AI-powered payment recovery decision engine.

    The system simulates multiple recovery strategies
    and recommends the best action based on predicted
    recovery probability, expected revenue, cost and
    customer friction.
    """,
    version="1.0.0"
)


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# LOAD DIGITAL TWIN
# ==========================================================

print("Initializing Payment Failure Digital Twin...")

try:
    twin = PaymentFailureDigitalTwin()
    print("Digital Twin initialized successfully.")

except Exception as error:
    print(f"Failed to initialize Digital Twin: {error}")
    raise


# ==========================================================
# HELPER FUNCTION
# ==========================================================

def convert_to_serializable(data):
    """
    Converts numpy/pandas values into normal
    Python values that can be returned as JSON.
    """

    if isinstance(data, dict):

        return {
            key: convert_to_serializable(value)
            for key, value in data.items()
        }

    elif isinstance(data, list):

        return [
            convert_to_serializable(item)
            for item in data
        ]

    elif isinstance(data, tuple):

        return [
            convert_to_serializable(item)
            for item in data
        ]

    elif hasattr(data, "item"):

        try:
            return data.item()
        except Exception:
            return data

    return data


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/")
def home():

    return {
        "message": "Payment Failure Digital Twin API is running",
        "status": "healthy"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "digital_twin": "ready"
    }


# ==========================================================
# SIMULATION ENDPOINT
# ==========================================================

@app.post("/simulate")
def simulate_payment_failure(
    failed_payment: FailedPaymentRequest
):

    try:

        # --------------------------------------------------
        # Convert Pydantic model into dictionary
        # --------------------------------------------------

        payment_data = failed_payment.model_dump()

        # --------------------------------------------------
        # Add default average transaction amount if missing
        # --------------------------------------------------

        if payment_data.get("average_transaction_amount") is None:

            payment_data["average_transaction_amount"] = (
                payment_data["amount"]
            )

        # --------------------------------------------------
        # Run Digital Twin
        # --------------------------------------------------

        result = twin.simulate(payment_data)

        # --------------------------------------------------
        # Convert numpy/pandas values into JSON-safe values
        # --------------------------------------------------

        result = convert_to_serializable(result)

        # --------------------------------------------------
        # Return response
        # --------------------------------------------------

        return {
            "success": True,
            "input_payment": payment_data,
            "simulation": result
        }

    except Exception as error:

        print(f"Simulation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while running the payment simulation."
        )


# ==========================================================
# SENSITIVITY ANALYSIS ENDPOINT
# ==========================================================

@app.post("/sensitivity")
def sensitivity_analysis(
    failed_payment: FailedPaymentRequest
):

    try:

        # --------------------------------------------------
        # Convert request into dictionary
        # --------------------------------------------------

        base_payment = failed_payment.model_dump()

        # --------------------------------------------------
        # Add default average transaction amount
        # --------------------------------------------------

        if base_payment.get("average_transaction_amount") is None:

            base_payment["average_transaction_amount"] = (
                base_payment["amount"]
            )

        # --------------------------------------------------
        # DEFINE WHAT-IF SCENARIOS
        # --------------------------------------------------

        scenarios = [

            {
                "scenario_name": "Lower transaction amount",

                "change": "Amount decreased by 20%",

                "payment_data": {
                    **base_payment,

                    "amount": round(
                        base_payment["amount"] * 0.8,
                        2
                    )
                }
            },

            {
                "scenario_name": "Higher transaction amount",

                "change": "Amount increased by 20%",

                "payment_data": {
                    **base_payment,

                    "amount": round(
                        base_payment["amount"] * 1.2,
                        2
                    )
                }
            },

            {
                "scenario_name": "Lower customer success rate",

                "change": "Historical success rate decreased",

                "payment_data": {
                    **base_payment,

                    "historical_success_rate": max(
                        0,

                        round(
                            base_payment[
                                "historical_success_rate"
                            ] - 0.15,
                            2
                        )
                    )
                }
            },

            {
                "scenario_name": "Higher customer success rate",

                "change": "Historical success rate increased",

                "payment_data": {
                    **base_payment,

                    "historical_success_rate": min(
                        1,

                        round(
                            base_payment[
                                "historical_success_rate"
                            ] + 0.15,
                            2
                        )
                    )
                }
            },

            {
                "scenario_name": "Late-night transaction",

                "change": "Transaction hour changed to 23:00",

                "payment_data": {
                    **base_payment,

                    "transaction_hour": 23
                }
            }
        ]

        # --------------------------------------------------
        # RUN BASE SIMULATION
        # --------------------------------------------------

        base_result = twin.simulate(base_payment)

        # --------------------------------------------------
        # RUN WHAT-IF SCENARIOS
        # --------------------------------------------------

        sensitivity_results = []

        for scenario in scenarios:

            simulation_result = twin.simulate(
                scenario["payment_data"]
            )

            # --------------------------------------------------
            # Get recommended strategy
            # --------------------------------------------------

            recommended_strategy = simulation_result.get(
                "recommended_strategy",
                {}
            )

            # --------------------------------------------------
            # Make sure strategy is dictionary-like
            # --------------------------------------------------

            if not isinstance(recommended_strategy, dict):

                recommended_strategy = {}

            # --------------------------------------------------
            # Store scenario result
            # --------------------------------------------------

            sensitivity_results.append({

                "scenario_name":
                    scenario["scenario_name"],

                "change":
                    scenario["change"],

                "recommended_strategy":
                    recommended_strategy,

                "recovery_probability":
                    recommended_strategy.get(
                        "recovery_probability",
                        0
                    ),

                "expected_recovered_amount":
                    recommended_strategy.get(
                        "expected_recovered_amount",
                        0
                    ),

                "utility_score":
                    recommended_strategy.get(
                        "utility_score",
                        0
                    )
            })

        # --------------------------------------------------
        # CONVERT TO JSON-SAFE VALUES
        # --------------------------------------------------

        result = convert_to_serializable({

            "base_result":
                base_result,

            "sensitivity_results":
                sensitivity_results
        })

        # --------------------------------------------------
        # RETURN RESPONSE
        # --------------------------------------------------

        return {

            "success": True,

            "sensitivity_analysis":
                result
        }

    except Exception as error:

        print(f"Simulation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while running the payment simulation."
        )


# ==========================================================
# MODEL PERFORMANCE ENDPOINT
# ==========================================================

@app.get("/model-performance")
def get_model_performance():

    try:

        # --------------------------------------------------
        # Locate metrics file
        # --------------------------------------------------

        metrics_path = (
            Path(__file__).resolve().parent.parent
            / "artifacts"
            / "models"
            / "model_metrics.json"
        )

        # --------------------------------------------------
        # Check if metrics file exists
        # --------------------------------------------------

        if not metrics_path.exists():

            return {
                "success": False,
                "error": "Model metrics file not found."
            }

        # --------------------------------------------------
        # Load metrics
        # --------------------------------------------------

        with open(
            metrics_path,
            "r",
            encoding="utf-8"
        ) as file:

            metrics = json.load(file)

        # --------------------------------------------------
        # Return metrics
        # --------------------------------------------------

        return {

            "success": True,

            "metrics":
                convert_to_serializable(metrics)
        }

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="Model metrics file contains invalid JSON."
        )

    except Exception as error:

        print(f"Simulation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while running the payment simulation."
        )

# ==========================================================
# DIGITAL TWIN EVALUATION ENDPOINT
# ==========================================================

@app.get("/evaluation-results")
def get_evaluation_results():

    try:

        # --------------------------------------------------
        # Locate evaluation results file
        # --------------------------------------------------

        evaluation_path = (
            Path(__file__).resolve().parent.parent
            / "artifacts"
            / "evaluation"
            / "digital_twin_evaluation.json"
        )


        # --------------------------------------------------
        # Check if evaluation file exists
        # --------------------------------------------------

        if not evaluation_path.exists():

            return {
                "success": False,
                "error": (
                    "Digital Twin evaluation results "
                    "not found."
                )
            }


        # --------------------------------------------------
        # Load evaluation results
        # --------------------------------------------------

        with open(
            evaluation_path,
            "r",
            encoding="utf-8"
        ) as file:

            evaluation = json.load(file)


        # --------------------------------------------------
        # Return evaluation results
        # --------------------------------------------------

        return {
            "success": True,
            "evaluation": convert_to_serializable(
                evaluation
            )
        }


    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail=(
                "Digital Twin evaluation file "
                "contains invalid JSON."
            )
        )

    except Exception as error:

        print(f"Evaluation results error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading evaluation results."
        )
