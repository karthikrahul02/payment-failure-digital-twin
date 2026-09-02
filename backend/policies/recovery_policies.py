RECOVERY_POLICIES = [
    {
        "strategy_id": "RETRY_30_MIN",
        "name": "Retry after 30 minutes",
        "action": "RETRY",
        "delay_hours": 0.5,
        "base_cost": 2.0,
        "base_friction": 0.15
    },
    {
        "strategy_id": "RETRY_6_HOURS",
        "name": "Retry after 6 hours",
        "action": "RETRY",
        "delay_hours": 6,
        "base_cost": 2.0,
        "base_friction": 0.10
    },
    {
        "strategy_id": "PAYMENT_LINK",
        "name": "Send Payment Link",
        "action": "PAYMENT_LINK",
        "delay_hours": 1,
        "base_cost": 8.0,
        "base_friction": 0.35
    },
    {
        "strategy_id": "WAIT",
        "name": "Wait",
        "action": "WAIT",
        "delay_hours": 12,
        "base_cost": 0.0,
        "base_friction": 0.05
    }
]