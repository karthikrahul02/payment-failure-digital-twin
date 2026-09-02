def simulate_payment_recovery(payment, policy):

    probability = 0.30

    # Customer behaviour
    success_rate = payment["customer_success_rate"]

    if success_rate >= 0.90:
        probability += 0.20
    elif success_rate >= 0.70:
        probability += 0.10
    else:
        probability -= 0.05

    # Failure reason behaviour
    failure_reason = payment["failure_reason"]

    if failure_reason == "TEMPORARY_BANK_ERROR":
        if policy["action"] == "RETRY":
            probability += 0.20

        if policy["delay_hours"] >= 4:
            probability += 0.10

    elif failure_reason == "INSUFFICIENT_FUNDS":

        if policy["action"] == "RETRY":
            if policy["delay_hours"] < 2:
                probability -= 0.20
            else:
                probability += 0.10

    elif failure_reason == "USER_ABANDONMENT":

        if policy["action"] == "PAYMENT_LINK":
            probability += 0.20

        if policy["action"] == "RETRY":
            probability -= 0.10

    # Retry count
    if payment["retry_count"] >= 2:
        probability -= 0.10

    # Payment link behaviour
    if policy["action"] == "PAYMENT_LINK":
        probability += 0.05

    # Wait behaviour
    if policy["action"] == "WAIT":
        probability -= 0.10

    # Keep probability between 0 and 1
    probability = max(0, min(probability, 1))

    return {
        "policy": policy["name"],
        "recovery_probability": round(probability, 2)
    }