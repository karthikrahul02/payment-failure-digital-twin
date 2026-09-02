# Payment Failure Digital Twin

An AI-powered payment recovery decision engine that simulates multiple
recovery strategies after a failed payment, predicts recovery
probability, estimates expected recovered value, accounts for
operational cost and customer friction, and recommends the strategy with
the highest expected utility.

## Table of Contents

-   Project Overview
-   Problem Statement
-   Proposed Solution
-   Digital Twin
-   System Architecture
-   Recovery Strategies
-   Machine Learning Model
-   Model Training
-   Decision and Utility Engine
-   What-If / Sensitivity Analysis
-   Risk and Confidence
-   Experimental Validation
-   Model Performance
-   Backend API
-   Frontend Dashboard
-   Technology Stack
-   Project Structure
-   Installation
-   Running the Application
-   API Usage
-   Validation and Reliability
-   Evaluation Methodology and Limitations
-   Project Highlights
-   Future Improvements
-   Author

## Project Overview

Payment failures are not necessarily the end of a transaction. A failed
payment may be recoverable through a suitable follow-up action such as
retrying later or sending a payment link.

A fixed-policy system may apply the same action to every failed payment.
This project instead evaluates multiple possible recovery actions for
each failed payment and recommends the action with the highest expected
business utility.

The system combines:

1.  Historical transaction information
2.  Machine-learning recovery probability prediction
3.  Counterfactual strategy simulation
4.  Expected recovered amount
5.  Strategy cost
6.  Customer-friction penalty
7.  Utility-based ranking
8.  Sensitivity analysis
9.  Risk and confidence analysis
10. Fixed-policy baseline evaluation

## Problem Statement

The project asks:

> Given a failed payment, which recovery strategy should be selected to
> maximize expected utility while considering recovery probability,
> recovered value, operational cost, and customer friction?

Potential actions include:

-   Retry after 30 minutes
-   Retry after 6 hours
-   Send Payment Link
-   Wait

The optimal action can depend on transaction amount, payment method,
failure reason, customer reliability, historical success rate,
transaction timing, and the relationship between the failed amount and
the customer's typical transaction amount.

## Proposed Solution

The system follows:

``` text
Failed Payment
      ↓
FastAPI Backend
      ↓
Digital Twin Engine
      ↓
ML Recovery Predictor
      ↓
Generate Counterfactual Recovery Strategies
      ↓
Predict Recovery Probability
      ↓
Expected Recovered Amount
      ↓
Cost + Customer Friction Penalty
      ↓
Utility Score
      ↓
Recommended Strategy
      ↓
What-If / Sensitivity Analysis
      ↓
Risk & Confidence Analysis
      ↓
Executive Decision Summary
      ↓
React Dashboard
```

## Digital Twin

A failed payment is represented as a virtual object. The Digital Twin
creates alternative versions of the same payment, each representing a
different possible recovery intervention.

``` text
Failed Payment
     |
     +---- Retry after 30 minutes
     |
     +---- Retry after 6 hours
     |
     +---- Send Payment Link
     |
     +---- Wait
```

Each scenario is passed through the recovery model and evaluated using
the same decision framework.

The key distinction is that the system does not only predict whether a
payment will recover. It evaluates which intervention is expected to be
most useful for that specific payment.

## Recovery Strategies

The current Digital Twin evaluates:

  Strategy                 Description
  ------------------------ -----------------------------------
  Retry after 30 minutes   Retry after a short delay
  Retry after 6 hours      Retry at a later time
  Send Payment Link        Provide another payment mechanism
  Wait                     Take no immediate recovery action

Strategy-specific variables include:

-   `strategy_id`
-   `action`
-   `retry_count`
-   `delay_hours`
-   `amount_to_average_ratio`
-   `is_high_value_transaction`
-   `transaction_hour`
-   `is_late_night`

## Machine Learning Model

The recovery predictor is a `RandomForestClassifier`.

Configuration:

``` text
n_estimators = 300
max_depth = 12
min_samples_split = 10
min_samples_leaf = 5
class_weight = balanced
random_state = 42
n_jobs = -1
```

Target:

``` text
recovered
```

Preprocessing includes:

-   Median imputation for numerical variables
-   Most-frequent imputation for categorical variables
-   One-hot encoding
-   `handle_unknown="ignore"`

Model artifact:

``` text
artifacts/models/recovery_predictor.joblib
```

## Model Features

The system uses:

-   Transaction ID
-   Customer ID
-   Amount
-   Payment method
-   Failure reason
-   Customer segment
-   Historical success rate
-   Average transaction amount
-   Transaction hour
-   Customer success category

Training-data categories currently supported by the API are:

### Payment method

``` text
CARD
UPI
WALLET
NET_BANKING
```

### Failure reason

``` text
TEMPORARY_BANK_ERROR
INSUFFICIENT_FUNDS
TECHNICAL_ERROR
NETWORK_TIMEOUT
USER_ABANDONMENT
AUTHENTICATION_FAILURE
```

### Customer segment

``` text
MEDIUM_RELIABILITY
HIGH_RELIABILITY
LOW_RELIABILITY
```

### Customer success category

``` text
MEDIUM
HIGH
LOW
```

## Model Training

Training script:

``` text
backend/ml/train_model.py
```

Training data:

``` text
data/processed/train.csv
data/processed/test.csv
```

The pipeline:

``` text
Processed Data
   ↓
Separate Features / Target
   ↓
Identify Numerical + Categorical Features
   ↓
Imputation
   ↓
One-Hot Encoding
   ↓
Random Forest
   ↓
Held-Out Evaluation
   ↓
Save Model + Metrics
```

Persisted metrics:

``` text
artifacts/models/model_metrics.json
```

Evaluation includes:

-   Accuracy
-   Precision
-   Recall
-   F1 score
-   ROC-AUC
-   Classification report
-   Confusion matrix
-   Feature importance

## Decision and Utility Engine

For every strategy, the system calculates:

### Recovery probability

The ML model estimates:

``` text
P(recovery | payment + strategy)
```

### Expected recovered amount

Conceptually:

``` text
Expected Recovered Amount
=
Recovery Probability × Transaction Amount
```

### Cost and customer friction

The decision layer accounts for strategy cost and customer-friction
penalty.

### Utility

The strategy is ranked using expected business utility:

``` text
Expected Recovery
-
Strategy Cost
-
Customer Friction Penalty
=
Utility Score
```

The highest-utility strategy becomes the recommendation.

## What-If / Sensitivity Analysis

The system evaluates how recommendations change under altered
conditions.

Current scenarios:

1.  Lower transaction amount --- amount decreased by 20%
2.  Higher transaction amount --- amount increased by 20%
3.  Lower customer success rate --- historical success rate decreased by
    0.15
4.  Higher customer success rate --- historical success rate increased
    by 0.15
5.  Late-night transaction --- transaction hour changed to 23:00

This helps determine whether a recommendation is stable or sensitive to
changing assumptions.

## Risk and Confidence

The dashboard evaluates decision stability using:

-   Percentage of sensitivity scenarios retaining the same
    recommendation
-   Utility gap between the best and second-best strategies

The current interpretation uses:

``` text
High confidence / Low risk
Moderate confidence / Medium risk
Low confidence / High risk
```

This is decision-stability analysis; it is not a claim that the ML model
is highly accurate.

## Experimental Validation

The Digital Twin was evaluated on a held-out test set containing:

``` text
1,972 transactions
```

The corrected experiment compares the adaptive Digital Twin against
fixed policies applied consistently across the complete held-out test
set.

Results:

  Metric                                            Result
  ------------------------------------ -------------------
  Digital Twin mean utility                      2579.4868
  Best fixed policy                      Send Payment Link
  Best fixed-policy mean utility                 2431.5983
  Utility advantage                               147.8885
  Improvement over best fixed policy                 6.08%
  Test transactions                                  1,972

Therefore:

> The Digital Twin achieved a 6.08% higher mean utility than the best
> fixed policy in this held-out, model-based evaluation.

The 6.08% figure is an improvement in **mean utility**. It is not a
claim of 6.08% more recovered payments, 6.08% additional real-world
revenue, or guaranteed production improvement.

Evaluation artifact:

``` text
artifacts/evaluation/digital_twin_evaluation.json
```

## Model Performance

The recovery model has moderate predictive performance. Representative
results include:

  Metric         Result
  ----------- ---------
  Accuracy      \~63.5%
  Precision       \~72%
  Recall          \~69%
  F1 Score        \~71%
  ROC-AUC         \~66%

The exact current values are loaded from:

``` text
artifacts/models/model_metrics.json
```

An earlier recorded confusion matrix was:

``` text
[[395, 335],
 [380, 862]]
```

The project does not present the predictor as a perfect model. Its main
contribution is the decision layer built around prediction,
counterfactual simulation, utility optimization, sensitivity analysis,
and policy evaluation.

## Backend API

The backend uses FastAPI.

  Method   Endpoint                Purpose
  -------- ----------------------- ----------------------------------
  GET      `/`                     API status
  GET      `/health`               Health check
  POST     `/simulate`             Run recovery simulation
  POST     `/sensitivity`          Run what-if analysis
  GET      `/model-performance`    Retrieve model metrics
  GET      `/evaluation-results`   Retrieve Digital Twin evaluation

Swagger documentation:

``` text
http://127.0.0.1:8000/docs
```

## Frontend Dashboard

The React dashboard visualizes:

-   Failed payment context
-   Recommended strategy
-   Strategy comparison
-   Recovery probability
-   Expected recovered amount
-   Utility score
-   Decision intelligence
-   What-if analysis
-   Sensitivity results
-   Risk and confidence
-   Executive decision summary
-   Model performance
-   Feature importance
-   Confusion matrix information
-   Digital Twin validation
-   Digital Twin vs fixed-policy comparison
-   Complete baseline breakdown

## Technology Stack

### Backend

-   Python
-   FastAPI
-   Uvicorn
-   Pydantic
-   Pandas
-   NumPy
-   Scikit-learn
-   Joblib

### Machine Learning

-   Random Forest
-   Imputation
-   One-hot encoding
-   Classification metrics
-   ROC-AUC
-   Confusion matrix
-   Feature importance

### Frontend

-   React
-   Vite
-   Axios
-   Framer Motion
-   Lucide React
-   Three.js / React Three Fiber components
-   Data visualization components

### Development

-   Git
-   GitHub
-   VS Code
-   Python virtual environment

## Project Structure

``` text
payment-failure-digital-twin/
│
├── artifacts/
│   ├── evaluation/
│   │   └── digital_twin_evaluation.json
│   └── models/
│       ├── recovery_predictor.joblib
│       └── model_metrics.json
│
├── backend/
│   ├── analysis/
│   ├── api/
│   │   └── schemas.py
│   ├── data_generation/
│   ├── digital_twin/
│   │   └── twin_engine.py
│   ├── evaluation/
│   ├── ml/
│   │   └── train_model.py
│   ├── models/
│   ├── policies/
│   ├── simulation/
│   ├── main.py
│   ├── generate_data.py
│   ├── README.md
│   └── requirements.txt
│
├── data/
│   └── processed/
│       ├── train.csv
│       └── test.csv
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ResultsDashboard.jsx
│   │   └── App.jsx
│   └── ...
│
├── .gitignore
├── package.json
└── package-lock.json
```

## Installation

### Prerequisites

-   Python 3.14.x
-   Node.js
-   npm
-   Git

### Clone

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd payment-failure-digital-twin
```

### Backend

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backendequirements.txt
```

Current backend requirements:

``` text
fastapi
uvicorn
pandas
numpy
scikit-learn
joblib
```

### Frontend

``` powershell
npm install
```

## Running the Application

### Backend

From the project root:

``` powershell
cd backend
..\ .venv\Scripts\Activate.ps1
```

Use the PowerShell path without the space:

``` powershell
..\.venv\Scripts\Activate.ps1
```

Start the server:

``` powershell
python -m uvicorn main:app --reload --port 8000
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

### Frontend

Open a second terminal at the project root:

``` powershell
npm run dev
```

Open the Vite URL shown by the terminal, normally:

``` text
http://localhost:5173
```

## API Usage

Example `/simulate` request:

``` json
{
  "transaction_id": "TXN_TEST_001",
  "customer_id": "CUST_TEST_001",
  "amount": 5000,
  "payment_method": "UPI",
  "failure_reason": "TEMPORARY_BANK_ERROR",
  "customer_segment": "MEDIUM_RELIABILITY",
  "historical_success_rate": 0.85,
  "average_transaction_amount": 4500,
  "transaction_hour": 14,
  "customer_success_category": "MEDIUM"
}
```

Response structure:

``` json
{
  "success": true,
  "input_payment": {},
  "simulation": {
    "failed_payment": {},
    "simulations": [],
    "recommended_strategy": {}
  }
}
```

## Validation and Reliability

Pydantic validation rejects invalid inputs before they reach the ML
model.

Examples:

``` text
amount > 0
0 <= historical_success_rate <= 1
0 <= transaction_hour <= 23
average_transaction_amount > 0 when supplied
```

Categorical values are restricted to the categories represented in the
training data.

For example:

``` text
payment_method = BITCOIN
```

is rejected with:

``` text
422 Unprocessable Content
```

Unexpected runtime failures are returned through controlled HTTP 500
responses while the technical error is retained in the backend terminal
for debugging.

## Evaluation Methodology and Limitations

The project distinguishes between predictive performance, offline policy
evaluation, and real-world business outcomes.

The ML model is probabilistic and has moderate predictive performance.

The Digital Twin evaluation is based on:

-   Held-out test transactions
-   The project's utility function
-   Consistent fixed-policy baselines
-   Model-based counterfactual simulation

The evaluation does not prove:

-   Causal effectiveness in production
-   Guaranteed additional revenue
-   Guaranteed payment recovery improvement
-   Identical performance on future production data

Production validation would require controlled experimentation such as
A/B testing or randomized policy evaluation, together with monitoring
and drift detection.

## Project Highlights

### Prediction + Decision

Moves from:

``` text
Will the payment recover?
```

to:

``` text
Which recovery action should be taken?
```

### Counterfactual simulation

Evaluates possible interventions before execution.

### Utility-based optimization

Ranks strategies by expected utility rather than recovery probability
alone.

### What-if analysis

Tests recommendation stability under changed assumptions.

### Risk-aware decision support

Uses sensitivity results and strategy separation to assess decision
confidence.

### Baseline comparison

Compares adaptive strategy selection with fixed policies.

### Evidence-driven dashboard

Displays model metrics and experimental policy evaluation instead of
presenting an unexplained AI recommendation.

### Modular engineering

Separates API, ML, Digital Twin, evaluation, data, artifacts, and
frontend components.

## Future Improvements

### Machine Learning

-   Hyperparameter optimization
-   Gradient boosting comparison
-   Probability calibration
-   Cross-validation
-   Threshold optimization
-   Temporal validation
-   Better feature engineering

### Decision Engine

-   More recovery actions
-   Dynamic strategy costs
-   Customer-specific friction models
-   Time-dependent recovery probabilities
-   Customer lifetime value
-   Budget-aware policy optimization

### Digital Twin

-   More counterfactual dimensions
-   Continuous parameter sweeps
-   Monte Carlo simulation
-   Uncertainty intervals
-   Scenario distributions

### Evaluation

-   Cross-validation of policy performance
-   Offline policy evaluation techniques
-   A/B testing
-   Randomized experiments
-   Production monitoring
-   Drift detection

### Engineering

-   Docker
-   Automated testing
-   CI/CD
-   Authentication
-   Centralized logging
-   Environment-based configuration
-   Cloud deployment

## Author

Developed as an end-to-end AI and software engineering project focused
on payment recovery decision intelligence.

The project demonstrates integration of:

``` text
Machine Learning
+
Backend Engineering
+
Digital Twin Simulation
+
Counterfactual Analysis
+
Decision Intelligence
+
Data Visualization
+
Experimental Evaluation
```

## License

Add the preferred open-source license if the repository is intended for
public distribution.

## Disclaimer

This is an experimental decision-support system. Model predictions and
simulated utility values are not guarantees of real-world payment
recovery or financial outcomes. Production deployment would require
additional validation, monitoring, security controls, and controlled
experimentation.
