from digital_twin.twin_engine import PaymentFailureDigitalTwin


# Example failed payment
failed_payment = {

    "transaction_id": "TXN_TEST_001",

    "customer_id": "CUST_TEST_001",

    "customer_segment": "REGULAR",

    "historical_success_rate": 0.78,

    "average_transaction_amount": 4500,

    "amount": 5000,

    "payment_method": "UPI",

    "failure_reason": "TEMPORARY_BANK_ERROR",

    "customer_success_category": "MEDIUM",

    "transaction_hour": 14
}


def main():

    print("\nPAYMENT FAILURE DIGITAL TWIN")
    print("=" * 65)

    # Initialize the Digital Twin
    twin = PaymentFailureDigitalTwin()

    # Simulate different recovery strategies
    result = twin.simulate(failed_payment)

    print("\nFAILED PAYMENT")
    print("-" * 65)

    print(
        f"Transaction ID: "
        f"{result['failed_payment']['transaction_id']}"
    )

    print(
        f"Customer ID: "
        f"{result['failed_payment']['customer_id']}"
    )

    print(
        f"Amount: "
        f"₹{result['failed_payment']['amount']}"
    )

    print(
        f"Payment Method: "
        f"{result['failed_payment']['payment_method']}"
    )

    print(
        f"Failure Reason: "
        f"{result['failed_payment']['failure_reason']}"
    )

    print("\nSIMULATED FUTURES")
    print("=" * 65)

    for index, simulation in enumerate(
        result["simulations"],
        start=1
    ):

        print(
            f"\n{index}. {simulation['strategy_name']}"
        )

        print(
            f"   Recovery Probability: "
            f"{simulation['recovery_probability']}%"
        )

        print(
            f"   Expected Recovery: "
            f"₹{simulation['expected_recovered_amount']}"
        )

        print(
            f"   Strategy Cost: "
            f"₹{simulation['average_cost']}"
        )

        print(
            f"   Customer Friction: "
            f"{simulation['friction']}"
        )

        print(
            f"   Utility Score: "
            f"₹{simulation['utility_score']}"
        )

    recommendation = result["recommended_strategy"]

    print("\n" + "=" * 65)

    print("DIGITAL TWIN RECOMMENDATION")
    print("=" * 65)

    print(
        f"\nRecommended Action: "
        f"{recommendation['strategy_name']}"
    )

    print(
        f"Predicted Recovery Probability: "
        f"{recommendation['recovery_probability']}%"
    )

    print(
        f"Expected Recovered Amount: "
        f"₹{recommendation['expected_recovered_amount']}"
    )

    print(
        f"Expected Utility Score: "
        f"₹{recommendation['utility_score']}"
    )

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()