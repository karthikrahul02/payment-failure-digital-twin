import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Trophy,
  TrendingUp,
  IndianRupee,
  Gauge,
  Check,
  ArrowUpRight,
  BrainCircuit,
  BarChart3,
  User,
  CreditCard,
  Clock3,
  CircleCheck,
  Grid2X2,
} from "lucide-react";

function ResultsDashboard({
  result,
  onBack,
  onRunSensitivity,
}) {

  // ----------------------------------------
  // WHAT-IF ANALYSIS STATE
  // ----------------------------------------

  const [sensitivityResult, setSensitivityResult] =
    useState(null);

  const [sensitivityLoading, setSensitivityLoading] =
    useState(false);

  const [sensitivityError, setSensitivityError] =
    useState(null);

  const [sensitivityData, setSensitivityData] =
    useState(null);

  const [isRunningSensitivity, setIsRunningSensitivity] =
    useState(false);

  // ----------------------------------------
// MODEL PERFORMANCE
// ----------------------------------------

const [modelPerformance, setModelPerformance] =
  useState(null);

const [modelPerformanceLoading, setModelPerformanceLoading] =
  useState(true);

const [modelPerformanceError, setModelPerformanceError] =
  useState(null);

const [evaluationResults, setEvaluationResults] = useState(null);

const [evaluationLoading, setEvaluationLoading] = useState(true);

const [evaluationError, setEvaluationError] = useState(null);


  // ----------------------------------------
// LOAD MODEL PERFORMANCE
// ----------------------------------------

useEffect(() => {

  const fetchModelPerformance = async () => {

    try {

      setModelPerformanceLoading(true);
      setModelPerformanceError(null);

      const response = await fetch(
        "http://127.0.0.1:8000/model-performance"
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load model performance."
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.error ||
          "Model performance unavailable."
        );
      }

      setModelPerformance(data.metrics);

    } catch (error) {

      console.error(
        "Model performance failed:",
        error
      );

      setModelPerformanceError(
        error.message ||
        "Unable to load model performance."
      );

    } finally {

      setModelPerformanceLoading(false);

    }

  };

  fetchModelPerformance();

}, []);

useEffect(() => {
  const fetchEvaluationResults = async () => {
    try {
      setEvaluationLoading(true);
      setEvaluationError(null);

      const response = await fetch(
        "http://127.0.0.1:8000/evaluation-results"
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load Digital Twin evaluation results."
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.error ||
          "Digital Twin evaluation results unavailable."
        );
      }

      setEvaluationResults(data.evaluation);
    } catch (error) {
      console.error(
        "Digital Twin evaluation failed:",
        error
      );

      setEvaluationError(
        error.message ||
        "Unable to load Digital Twin evaluation results."
      );
    } finally {
      setEvaluationLoading(false);
    }
  };

  fetchEvaluationResults();
}, []);

  // ----------------------------------------
  // SAFETY CHECK
  // ----------------------------------------

  if (!result) return null;

  // ----------------------------------------
  // EXTRACT BACKEND RESPONSE
  // ----------------------------------------

  const simulation = result.simulation || result;

  const confusionMatrix =
  modelPerformance?.confusion_matrix || [
    [0, 0],
    [0, 0],
  ];

  const featureImportance =
  modelPerformance?.feature_importance || [];

const topFeatures = featureImportance
  .slice(0, 10);

const digitalTwinMeanUtility =
  Number(
    evaluationResults?.digital_twin_mean_utility ?? 0
  );

const bestFixedPolicy =
  evaluationResults?.best_fixed_policy ||
  "Not available";

const bestFixedPolicyUtility =
  Number(
    evaluationResults?.best_fixed_policy_utility ?? 0
  );

const digitalTwinAdvantage =
  Number(
    evaluationResults?.advantage_over_best_fixed_policy ?? 0
  );

const digitalTwinImprovement =
  Number(
    evaluationResults?.percentage_improvement_over_best_fixed ?? 0
  );

const evaluationTransactionCount =
  Number(
    evaluationResults?.test_transactions ?? 0
  );

const trueNegative = confusionMatrix[0]?.[0] ?? 0;
const falsePositive = confusionMatrix[0]?.[1] ?? 0;
const falseNegative = confusionMatrix[1]?.[0] ?? 0;
const truePositive = confusionMatrix[1]?.[1] ?? 0;

  const inputPayment =
    result.input_payment ||
    simulation.failed_payment ||
    {};

  const recommendedStrategy =
    simulation.recommended_strategy || {};

  const recommendedStrategyName =
    recommendedStrategy.strategy_name ||
    recommendedStrategy.strategy ||
    recommendedStrategy.name ||
    recommendedStrategy.action ||
    "No recommendation available";

  const recoveryProbability =
    recommendedStrategy.recovery_probability ?? 0;

  const expectedRecovery =
    recommendedStrategy.expected_recovered_amount ??
    recommendedStrategy.expected_recovery ??
    0;

  const utilityScore =
    recommendedStrategy.utility_score ?? 0;

  const strategies =
    simulation.simulations ||
    simulation.strategies ||
    simulation.results ||
    [];

  // ----------------------------------------
  // SORT STRATEGIES BY UTILITY
  // ----------------------------------------

  const sortedStrategies = [...strategies].sort(
    (a, b) =>
      (b.utility_score ?? 0) -
      (a.utility_score ?? 0)
  );
    const bestStrategy = sortedStrategies[0];
  const secondBestStrategy = sortedStrategies[1];

  const getStrategyName = (strategy) =>
    strategy?.strategy ||
    strategy?.strategy_name ||
    strategy?.name ||
    strategy?.action ||
    "Unknown strategy";

  const getProbability = (strategy) =>
    Number(
      strategy?.recovery_probability ??
      strategy?.recoveryProbability ??
      0
    );

  const getRecovery = (strategy) =>
    Number(
      strategy?.expected_recovery ??
      strategy?.expectedRecovery ??
      strategy?.expected_recovered_amount ??
      0
    );

  const getUtility = (strategy) =>
    Number(
      strategy?.utility_score ??
      strategy?.utilityScore ??
      0
    );

  const utilityAdvantage =
    bestStrategy && secondBestStrategy
      ? getUtility(bestStrategy) - getUtility(secondBestStrategy)
      : 0;

  const probabilityAdvantage =
    bestStrategy && secondBestStrategy
      ? getProbability(bestStrategy) -
        getProbability(secondBestStrategy)
      : 0;

  const recoveryAdvantage =
    bestStrategy && secondBestStrategy
      ? getRecovery(bestStrategy) -
        getRecovery(secondBestStrategy)
      : 0;

      // ----------------------------------------
// SENSITIVITY ANALYSIS DATA
// ----------------------------------------

const sensitivityAnalysis =
  result.sensitivity_analysis ||
  simulation.sensitivity_analysis ||
  null;

const sensitivityResults =
  sensitivityAnalysis?.sensitivity_results || [];

const sensitivityBaseResult =
  sensitivityAnalysis?.base_result || null;

// ----------------------------------------
// RISK & CONFIDENCE ANALYSIS
// ----------------------------------------

const stableScenarioCount = sensitivityResults.filter(
  (scenario) => {
    const scenarioStrategy = getStrategyName(
      scenario.recommended_strategy
    );

    const baselineStrategy = sensitivityBaseResult
      ? getStrategyName(
          sensitivityBaseResult.recommended_strategy
        )
      : recommendedStrategyName;

    return scenarioStrategy === baselineStrategy;
  }
).length;

const totalScenarioCount = sensitivityResults.length;

const stabilityPercentage =
  totalScenarioCount > 0
    ? Math.round(
        (stableScenarioCount / totalScenarioCount) * 100
      )
    : null;

const utilityGap =
  bestStrategy && secondBestStrategy
    ? getUtility(bestStrategy) - getUtility(secondBestStrategy)
    : 0;

let confidenceLevel = "Not established";
let riskLevel = "Not established";

if (totalScenarioCount > 0) {
  confidenceLevel = "High";
  riskLevel = "Low";

  if (stabilityPercentage < 60 || utilityGap < 25) {
    confidenceLevel = "Moderate";
    riskLevel = "Medium";
  }

  if (stabilityPercentage < 40 || utilityGap < 10) {
    confidenceLevel = "Low";
    riskLevel = "High";
  }
}

const recommendationConfidence =
  stabilityPercentage !== null
    ? stabilityPercentage
    : null;


  // ----------------------------------------
  // RUNNER-UP STRATEGY
  // ----------------------------------------

  const runnerUp = sortedStrategies[1];

  const runnerUpName =
    runnerUp?.strategy_name ||
    runnerUp?.strategy ||
    runnerUp?.name ||
    "No alternative";

  const runnerUpUtility =
    runnerUp?.utility_score ?? 0;

  const utilityDifference =
    utilityScore - runnerUpUtility;

  // ----------------------------------------
  // FORMAT HELPERS
  // ----------------------------------------

  const formatLabel = (value) => {
    if (!value) return "Not available";

    return String(value)
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };

  const maxUtility =
    Math.max(
      ...sortedStrategies.map(
        (strategy) =>
          Number(strategy.utility_score ?? 0)
      ),
      1
    );
      // ----------------------------------------
  // RUN WHAT-IF / SENSITIVITY ANALYSIS
  // ----------------------------------------

  const runWhatIfAnalysis = async () => {
    if (!onRunSensitivity) {
      setSensitivityError(
        "Sensitivity analysis is not connected."
      );
      return;
    }

    try {
      setSensitivityLoading(true);
      setSensitivityError(null);
      setSensitivityResult(null);

      const sensitivityData = {
        transaction_id:
          inputPayment.transaction_id,

        customer_id:
          inputPayment.customer_id,

        amount: Number(
          inputPayment.amount ?? 0
        ),

        payment_method:
          inputPayment.payment_method,

        failure_reason:
          inputPayment.failure_reason,

        customer_segment:
          inputPayment.customer_segment,

        historical_success_rate:
          Number(
            inputPayment.historical_success_rate ?? 0
          ),

        average_transaction_amount:
          Number(
            inputPayment.average_transaction_amount ??
            inputPayment.amount ??
            0
          ),

        transaction_hour:
          Number(
            inputPayment.transaction_hour ?? 0
          ),

        customer_success_category:
          inputPayment.customer_success_category ??
          "MEDIUM",
      };

      console.log(
        "Running What-If Analysis:",
        sensitivityData
      );

      const data =
        await onRunSensitivity(
          sensitivityData
        );

      if (!data) {
        throw new Error(
          "No sensitivity analysis response received."
        );
      }

      console.log(
        "What-If Analysis Result:",
        data
      );

      setSensitivityResult(data);
    } catch (error) {
      console.error(
        "What-If Analysis failed:",
        error
      );

      setSensitivityError(
        error.message ||
        "Sensitivity analysis failed."
      );
    } finally {
      setSensitivityLoading(false);
    }
  };


  return (
    <main className="results-page">

      {/* -------------------------------- */}
      {/* NAVIGATION */}
      {/* -------------------------------- */}

      <nav className="results-nav">

        <button
          className="back-button"
          onClick={onBack}
        >
          <ArrowLeft size={17} />
          Back to simulation
        </button>

        <div className="nav-status">
          <span className="status-dot" />
          Simulation complete
        </div>

      </nav>


      {/* -------------------------------- */}
      {/* HERO */}
      {/* -------------------------------- */}

      <motion.section
        className="results-hero"
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >

        <div>

          <span className="section-eyebrow">
            DIGITAL TWIN RESULT
          </span>

          <h1>
            Recommended recovery
            <span> action.</span>
          </h1>

          <p>
            The Digital Twin evaluated multiple recovery futures
            and selected the strategy with the strongest overall
            utility.
          </p>

        </div>

      </motion.section>


      {/* -------------------------------- */}
      {/* RECOMMENDED STRATEGY */}
      {/* -------------------------------- */}

      <motion.section
        className="recommendation-panel glass-panel"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.7,
          delay: 0.1,
        }}
      >

        <div className="recommendation-top">

          <div>

            <span className="section-eyebrow">
              RECOMMENDED STRATEGY
            </span>

            <h2>
              {recommendedStrategyName}
            </h2>

          </div>

          <div className="winner-badge">

            <Trophy size={18} />

            Best outcome

          </div>

        </div>


        <div className="result-metrics">

          <div className="result-metric">

            <div className="metric-icon">
              <TrendingUp size={19} />
            </div>

            <span>
              Recovery probability
            </span>

            <strong>
              {Number(recoveryProbability).toFixed(1)}%
            </strong>

          </div>


          <div className="result-metric">

            <div className="metric-icon">
              <IndianRupee size={19} />
            </div>

            <span>
              Expected recovery
            </span>

            <strong>
              ₹{Number(expectedRecovery).toFixed(2)}
            </strong>

          </div>


          <div className="result-metric">

            <div className="metric-icon">
              <Gauge size={19} />
            </div>

            <span>
              Utility score
            </span>

            <strong>
              {Number(utilityScore).toFixed(2)}
            </strong>

          </div>

        </div>

      </motion.section>


      {/* -------------------------------- */}
      {/* DECISION INTELLIGENCE */}
      {/* -------------------------------- */}

      <section className="analytics-grid">

        <motion.div
          className="decision-panel glass-panel"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.6,
            delay: 0.2,
          }}
        >

          <div className="analytics-panel-header">

            <div className="analytics-icon">
              <BrainCircuit size={20} />
            </div>

            <div>

              <span className="section-eyebrow">
                DECISION INTELLIGENCE
              </span>

              <h3>
                Why this strategy won.
              </h3>

            </div>

          </div>


          <div className="decision-insight">

            <div className="decision-insight-main">

              <CircleCheck size={20} />

              <p>
                <strong>
                  {recommendedStrategyName}
                </strong>{" "}
                produced the highest utility across all simulated
                recovery paths.
              </p>

            </div>


            {runnerUp && (

              <div className="comparison-insight">

                <span>
                  Utility advantage over
                </span>

                <strong>
                  {runnerUpName}
                </strong>

                <div className="utility-advantage">

                  +{Number(utilityDifference).toFixed(2)}

                </div>

              </div>

            )}

          </div>


          <div className="decision-factors">

            <div>

              <span>
                Recovery probability
              </span>

              <strong>
                {Number(recoveryProbability).toFixed(1)}%
              </strong>

            </div>

            <div>

              <span>
                Expected recovery
              </span>

              <strong>
                ₹{Number(expectedRecovery).toFixed(2)}
              </strong>

            </div>

            <div>

              <span>
                Optimization objective
              </span>

              <strong>
                Highest utility
              </strong>

            </div>

          </div>

        </motion.div>


        {/* -------------------------------- */}
        {/* INPUT CONTEXT */}
        {/* -------------------------------- */}

        <motion.div
          className="context-panel glass-panel"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.6,
            delay: 0.3,
          }}
        >

          <div className="analytics-panel-header">

            <div className="analytics-icon">
              <User size={20} />
            </div>

            <div>

              <span className="section-eyebrow">
                SIMULATION CONTEXT
              </span>

              <h3>
                What influenced the decision.
              </h3>

            </div>

          </div>


          <div className="context-list">

            <div className="context-row">

              <div className="context-label">

                <CreditCard size={17} />

                <span>
                  Payment method
                </span>

              </div>

              <strong>
                {formatLabel(
                  inputPayment.payment_method
                )}
              </strong>

            </div>


            <div className="context-row">

              <div className="context-label">

                <IndianRupee size={17} />

                <span>
                  Transaction amount
                </span>

              </div>

              <strong>
                ₹{Number(
                  inputPayment.amount ?? 0
                ).toFixed(2)}
              </strong>

            </div>


            <div className="context-row">

              <div className="context-label">

                <TrendingUp size={17} />

                <span>
                  Historical success
                </span>

              </div>

              <strong>
                {(
                  Number(
                    inputPayment.historical_success_rate ??
                    0
                  ) * 100
                ).toFixed(1)}%
              </strong>

            </div>


            <div className="context-row">

              <div className="context-label">

                <Clock3 size={17} />

                <span>
                  Transaction hour
                </span>

              </div>

              <strong>
                {inputPayment.transaction_hour ??
                  "N/A"}:00
              </strong>

            </div>

          </div>

        </motion.div>

      </section>


      {/* -------------------------------- */}
      {/* STRATEGY COMPARISON */}
      {/* -------------------------------- */}

      <section className="strategy-section">

        <div className="section-heading">

          <div>

            <span className="section-eyebrow">
              SIMULATED FUTURES
            </span>

            <h2>
              Strategy comparison.
            </h2>

            <p>
              Compare every recovery path evaluated
              by the Digital Twin.
            </p>

          </div>

        </div>


        {/* -------------------------------- */}
        {/* UTILITY COMPARISON */}
        {/* -------------------------------- */}

        <motion.div
          className="utility-chart glass-panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.6,
          }}
        >

          <div className="chart-header">

            <div>

              <div className="chart-title">

                <BarChart3 size={20} />

                <h3>
                  Utility comparison
                </h3>

              </div>

              <p>
                Strategies ranked by overall recovery
                utility.
              </p>

            </div>

          </div>


          <div className="utility-bars">

            {sortedStrategies.map(
              (strategy, index) => {

                const name =
                  strategy.strategy_name ||
                  strategy.strategy ||
                  strategy.name ||
                  strategy.action ||
                  `Strategy ${index + 1}`;

                const utility =
                  Number(
                    strategy.utility_score ?? 0
                  );

                const width =
                  (utility / maxUtility) * 100;

                const isRecommended =
                  name === recommendedStrategyName;

                return (

                  <div
                    className="utility-bar-row"
                    key={`${name}-${index}`}
                  >

                    <div className="utility-bar-label">

                      <span>
                        0{index + 1}
                      </span>

                      <strong>
                        {name}
                      </strong>

                    </div>


                    <div className="utility-bar-track">

                      <motion.div
                        className={`utility-bar-fill ${
                          isRecommended
                            ? "utility-bar-winner"
                            : ""
                        }`}
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width: `${width}%`,
                        }}
                        transition={{
                          duration: 0.9,
                          delay: index * 0.1,
                        }}
                      />

                    </div>


                    <strong className="utility-value">

                      {utility.toFixed(2)}

                    </strong>

                  </div>

                );
              }
            )}

          </div>

        </motion.div>


        {/* -------------------------------- */}
        {/* STRATEGY CARDS */}
        {/* -------------------------------- */}

        <div className="strategy-grid">

          {sortedStrategies.length > 0 ? (

            sortedStrategies.map(
              (strategy, index) => {

                const name =
                  strategy.strategy_name ||
                  strategy.strategy ||
                  strategy.name ||
                  strategy.action ||
                  `Strategy ${index + 1}`;

                const probability =
                  strategy.recovery_probability ?? 0;

                const recovery =
                  strategy.expected_recovered_amount ??
                  strategy.expected_recovery ??
                  0;

                const utility =
                  strategy.utility_score ?? 0;

                const isRecommended =
                  name === recommendedStrategyName;

                return (

                  <motion.div
                    key={`${name}-${index}`}
                    className={`strategy-card glass-panel ${
                      isRecommended
                        ? "strategy-card-winner"
                        : ""
                    }`}
                    initial={{
                      opacity: 0,
                      y: 20,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    transition={{
                      duration: 0.5,
                      delay: index * 0.1,
                    }}
                  >

                    <div className="strategy-card-top">

                      <span className="strategy-rank">
                        0{index + 1}
                      </span>


                      {isRecommended && (

                        <span className="recommended-tag">

                          <Check size={14} />

                          Recommended

                        </span>

                      )}

                    </div>


                    <h3>
                      {name}
                    </h3>


                    <div className="probability-row">

                      <span>
                        Recovery probability
                      </span>

                      <strong>
                        {Number(probability).toFixed(1)}%
                      </strong>

                    </div>


                    <div className="probability-track">

                      <motion.div
                        className="probability-fill"
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width: `${Math.min(
                            Number(probability),
                            100
                          )}%`,
                        }}
                        transition={{
                          duration: 0.8,
                          delay: index * 0.1,
                        }}
                      />

                    </div>


                    <div className="strategy-stats">

                      <div>

                        <span>
                          Expected recovery
                        </span>

                        <strong>
                          ₹{Number(recovery).toFixed(2)}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Utility
                        </span>

                        <strong>
                          {Number(utility).toFixed(2)}
                        </strong>

                      </div>

                    </div>


                    <div className="strategy-footer">

                      <span>

                        {isRecommended
                          ? "Highest utility outcome"
                          : "Alternative recovery path"}

                      </span>

                      <ArrowUpRight size={17} />

                    </div>

                  </motion.div>

                );
              }
            )

          ) : (

            <div className="empty-strategy-state glass-panel">

              <h3>
                Strategy comparison unavailable
              </h3>

              <p>
                No individual strategy results were
                returned by the simulation.
              </p>

            </div>

          )}

        </div>

            </section>

      {bestStrategy && secondBestStrategy && (
        <motion.section
          className="decision-insights glass-panel"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="insights-heading">
            <div>
              <span className="section-eyebrow">
                DECISION INSIGHTS
              </span>


              <h2>Why this strategy won.</h2>

              <p>
                The Digital Twin compared recovery probability, expected
                recovery, and overall utility across all simulated futures.
              </p>
            </div>
          </div>

          <div className="insight-summary">
            <div className="insight-main">
              <span>Recommended decision</span>

              <h3>
                {getStrategyName(bestStrategy)}
              </h3>

              <p>
                This strategy achieved the highest overall utility score among
                all simulated recovery paths.
              </p>
            </div>

            <div className="insight-metrics">
              <div className="insight-metric">
                <span>Utility advantage</span>

                <strong>
                  +{utilityAdvantage.toFixed(2)}
                </strong>

                <small>
                  compared with{" "}
                  {getStrategyName(secondBestStrategy)}
                </small>
              </div>

              <div className="insight-metric">
                <span>Recovery probability advantage</span>

                <strong>
                  {probabilityAdvantage >= 0 ? "+" : ""}
                  {probabilityAdvantage.toFixed(1)}%
                </strong>

                <small>
                  versus the next best alternative
                </small>
              </div>

              <div className="insight-metric">
                <span>Expected recovery difference</span>

                <strong>
                  {recoveryAdvantage >= 0 ? "+" : "-"}₹
                  {Math.abs(recoveryAdvantage).toFixed(2)}
                </strong>

                <small>
                  compared with the second-best strategy
                </small>
              </div>
            </div>
          </div>

          <div className="decision-explanation">
            <span>Digital Twin reasoning</span>

            <p>
              <strong>{getStrategyName(bestStrategy)}</strong> was selected
              because it produced the strongest overall balance between
              recovery likelihood and financial outcome. Its utility score was{" "}
              <strong>{utilityAdvantage.toFixed(2)} points higher</strong>{" "}
              than the next-best recovery strategy,
              {" "}
              <strong>
                {getStrategyName(secondBestStrategy)}
              </strong>.
            </p>
          </div>
          <div className="sensitivity-action">
            <div>
              <span className="section-eyebrow">
                WHAT-IF SCENARIO ANALYSIS
              </span>

              <h3>
                Test alternative payment conditions.
              </h3>

              <p>
                Re-run the Digital Twin under changing transaction
                conditions and observe whether the recommended
                recovery strategy remains stable.
              </p>
            </div>

            <button
              className="sensitivity-button"
              onClick={runWhatIfAnalysis}            
              disabled={isRunningSensitivity}
            >
              {isRunningSensitivity
                ? "Running scenarios..."
                : "Run What-If Analysis"}
            </button>
          </div>

          {sensitivityError && (
            <div className="sensitivity-error">
              {sensitivityError}
            </div>
          )}
        </motion.section>
      )}
            {/* -------------------------------- */}
      {/* WHAT-IF SCENARIO ANALYSIS */}
      {/* -------------------------------- */}

      <motion.section
        className="what-if-section glass-panel"
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.6,
          delay: 0.2,
        }}
      >
        <div className="what-if-header">
          <div>
            <span className="section-eyebrow">
              WHAT-IF SCENARIO ANALYSIS
            </span>

            <h2>
              Test alternative payment conditions.
            </h2>

            <p>
              Re-run the Digital Twin under changing
              transaction conditions and observe whether
              the recommended recovery strategy remains
              stable.
            </p>
          </div>

          <button
            className="what-if-button"
            onClick={runWhatIfAnalysis}
            disabled={sensitivityLoading}
          >
            {sensitivityLoading
              ? "Running Analysis..."
              : "Run What-If Analysis"}
          </button>
        </div>

        {sensitivityError && (
          <div className="what-if-error">
            {sensitivityError}
          </div>
        )}

        {sensitivityResult && (
          <div className="sensitivity-results">

            <div className="sensitivity-results-header">
              <div>
                <span className="section-eyebrow">
                  SENSITIVITY RESULTS
                </span>

                <h3>
                  How stable is the recommendation?
                </h3>

                <p>
                  The Digital Twin tested alternative
                  transaction conditions against the
                  original payment scenario.
                </p>
              </div>
            </div>

            {sensitivityResult.sensitivity_analysis && (
              <>
                <div className="sensitivity-base-result">
                  <span>
                    BASELINE RECOMMENDATION
                  </span>

                  <strong>
                    {getStrategyName(
                      sensitivityResult
                        .sensitivity_analysis
                        .base_result
                        ?.recommended_strategy
                    )}
                  </strong>
                </div>

                <div className="sensitivity-grid">
                  {(
                    sensitivityResult
                      .sensitivity_analysis
                      .sensitivity_results || []
                  ).map(
                    (scenario, index) => {

                      const scenarioStrategy =
                        scenario.recommended_strategy;

                      const scenarioName =
                        getStrategyName(
                          scenarioStrategy
                        );

                      const scenarioProbability =
                        Number(
                          scenario.recovery_probability ??
                          0
                        );

                      const scenarioRecovery =
                        Number(
                          scenario.expected_recovered_amount ??
                          scenario.expected_recovery ??
                          0
                        );

                      const scenarioUtility =
                        Number(
                          scenario.utility_score ??
                          0
                        );

                      const strategyChanged =
                        scenarioName !==
                        recommendedStrategyName;

                      return (
                        <motion.div
                          key={`${scenario.scenario_name}-${index}`}
                          className="sensitivity-card"
                          initial={{
                            opacity: 0,
                            y: 15,
                          }}
                          animate={{
                            opacity: 1,
                            y: 0,
                          }}
                          transition={{
                            duration: 0.4,
                            delay: index * 0.08,
                          }}
                        >
                          <div className="sensitivity-card-top">
                            <span>
                              0{index + 1}
                            </span>

                            <span
                              className={
                                strategyChanged
                                  ? "scenario-status changed"
                                  : "scenario-status stable"
                              }
                            >
                              {strategyChanged
                                ? "Strategy changed"
                                : "Recommendation stable"}
                            </span>
                          </div>

                          <h4>
                            {scenario.scenario_name}
                          </h4>

                          <p className="scenario-change">
                            {scenario.change}
                          </p>

                          <div className="scenario-recommendation">
                            <span>
                              Recommended strategy
                            </span>

                            <strong>
                              {scenarioName}
                            </strong>
                          </div>

                          <div className="scenario-metrics">

                            <div>
                              <span>
                                Recovery probability
                              </span>

                              <strong>
                                {scenarioProbability.toFixed(
                                  1
                                )}
                                %
                              </strong>
                            </div>

                            <div>
                              <span>
                                Expected recovery
                              </span>

                              <strong>
                                ₹
                                {scenarioRecovery.toFixed(
                                  2
                                )}
                              </strong>
                            </div>

                            <div>
                              <span>
                                Utility
                              </span>

                              <strong>
                                {scenarioUtility.toFixed(
                                  2
                                )}
                              </strong>
                            </div>

                          </div>
                        </motion.div>
                      );
                    }
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </motion.section>

      {/* -------------------------------- */}
{/* SENSITIVITY VISUALIZATION */}
{/* -------------------------------- */}

{sensitivityResults.length > 0 && (
  <motion.section
    className="sensitivity-visual-section"
    initial={{ opacity: 0, y: 25 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6 }}
  >

    <div className="sensitivity-visual-header">

      <div>
        <span className="section-eyebrow">
          SENSITIVITY ANALYSIS
        </span>

        <h2>
          How stable is the recommendation?
        </h2>

        <p>
          The Digital Twin tested alternative transaction
          conditions to determine whether the recommended
          recovery strategy remains consistent.
        </p>
      </div>

    </div>


    {/* BASELINE */}

    {sensitivityBaseResult && (
      <div className="sensitivity-baseline glass-panel">

        <div>
          <span className="sensitivity-label">
            BASELINE RECOMMENDATION
          </span>

          <h3>
            {getStrategyName(
              sensitivityBaseResult.recommended_strategy
            )}
          </h3>
        </div>

        <div className="baseline-metrics">

          <div>
            <span>Recovery probability</span>

            <strong>
              {Number(
                sensitivityBaseResult.recovery_probability ?? 0
              ).toFixed(1)}%
            </strong>
          </div>

          <div>
            <span>Expected recovery</span>

            <strong>
              ₹
              {Number(
                sensitivityBaseResult.expected_recovered_amount ??
                sensitivityBaseResult.expected_recovery ??
                0
              ).toFixed(2)}
            </strong>
          </div>

          <div>
            <span>Utility</span>

            <strong>
              {Number(
                sensitivityBaseResult.utility_score ?? 0
              ).toFixed(2)}
            </strong>
          </div>

        </div>

      </div>
    )}


    {/* SCENARIO RESULTS */}

    <div className="sensitivity-visual-grid">

      {sensitivityResults.map((scenario, index) => {

        const scenarioStrategy =
          scenario.recommended_strategy || {};

        const scenarioName =
          getStrategyName(scenarioStrategy);

        const scenarioProbability =
          Number(
            scenario.recovery_probability ?? 0
          );

        const scenarioRecovery =
          Number(
            scenario.expected_recovered_amount ??
            scenario.expected_recovery ??
            0
          );

        const scenarioUtility =
          Number(
            scenario.utility_score ?? 0
          );

        const baselineStrategy =
          sensitivityBaseResult
            ? getStrategyName(
                sensitivityBaseResult.recommended_strategy
              )
            : recommendedStrategyName;

        const isStable =
          scenarioName === baselineStrategy;

        return (
          <motion.div
            key={`${scenario.scenario_name}-${index}`}
            className="sensitivity-visual-card glass-panel"
            initial={{
              opacity: 0,
              y: 15,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.45,
              delay: index * 0.08,
            }}
          >

            <div className="sensitivity-visual-top">

              <span className="scenario-number">
                0{index + 1}
              </span>

              <span
                className={`scenario-status ${
                  isStable ? "stable" : "changed"
                }`}
              >
                {isStable ? "Stable" : "Changed"}
              </span>

            </div>


            <h3>
              {scenario.scenario_name ||
                `Scenario ${index + 1}`}
            </h3>

            <p className="scenario-description">
              {scenario.change ||
                "Alternative transaction conditions"}
            </p>


            <div className="scenario-strategy">

              <span>
                Recommended strategy
              </span>

              <strong>
                {scenarioName}
              </strong>

            </div>


            <div className="scenario-visual-metrics">

              <div>
                <span>
                  Recovery
                </span>

                <strong>
                  {scenarioProbability.toFixed(1)}%
                </strong>

                <div className="scenario-progress">
                  <div
                    style={{
                      width: `${Math.min(
                        scenarioProbability,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>


              <div>
                <span>
                  Expected recovery
                </span>

                <strong>
                  ₹{scenarioRecovery.toFixed(2)}
                </strong>
              </div>


              <div>
                <span>
                  Utility
                </span>

                <strong>
                  {scenarioUtility.toFixed(2)}
                </strong>
              </div>

            </div>

          </motion.div>
        );
      })}

    </div>


    {/* STABILITY SUMMARY */}

    <div className="sensitivity-stability glass-panel">

      <div>
        <span className="sensitivity-label">
          RECOMMENDATION STABILITY
        </span>

        <h3>
          {sensitivityResults.filter((scenario) => {

            const scenarioStrategy =
              getStrategyName(
                scenario.recommended_strategy
              );

            const baselineStrategy =
              sensitivityBaseResult
                ? getStrategyName(
                    sensitivityBaseResult.recommended_strategy
                  )
                : recommendedStrategyName;

            return scenarioStrategy === baselineStrategy;

          }).length} of {sensitivityResults.length} scenarios
          preserve the baseline recommendation.
        </h3>
      </div>

      <div className="stability-indicator">

        {Math.round(
          (
            sensitivityResults.filter((scenario) => {

              const scenarioStrategy =
                getStrategyName(
                  scenario.recommended_strategy
                );

              const baselineStrategy =
                sensitivityBaseResult
                  ? getStrategyName(
                      sensitivityBaseResult.recommended_strategy
                    )
                  : recommendedStrategyName;

              return scenarioStrategy === baselineStrategy;

            }).length /
            sensitivityResults.length
          ) * 100
        )}%

      </div>

    </div>

  </motion.section>
)}
{/* -------------------------------- */}
{/* RISK & CONFIDENCE ANALYSIS */}
{/* -------------------------------- */}

<motion.section
  className="risk-confidence-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="risk-confidence-header">

    <div>
      <span className="section-eyebrow">
        DECISION RISK & CONFIDENCE
      </span>

      <h2>
        How reliable is this recommendation?
      </h2>

      <p>
        Confidence is based on recommendation stability across
        tested scenarios and the utility advantage over the
        next-best recovery strategy.
      </p>
    </div>

  </div>


  <div className="risk-confidence-grid">

    {/* CONFIDENCE */}

    <div className="confidence-card glass-panel">

      <div className="confidence-card-top">

        <span className="confidence-label">
          RECOMMENDATION CONFIDENCE
        </span>

        <span
          className={`confidence-badge ${confidenceLevel
            .toLowerCase()
            .replace(" ", "-")}`}
        >
          {confidenceLevel}
        </span>

      </div>

      <div className="confidence-score">
        {recommendationConfidence !== null
          ? `${recommendationConfidence}%`
          : "Not established"}
      </div>

      <p>
        {stableScenarioCount} of{" "}
        {totalScenarioCount} tested scenarios
        preserve the baseline recommendation.
      </p>

      <div className="confidence-progress">

        <motion.div
          initial={{ width: 0 }}
          animate={{
            width: `${recommendationConfidence ?? 0}%`,
          }}
          transition={{
            duration: 0.9,
          }}
        />

      </div>

    </div>


    {/* RISK */}

    <div className="risk-card glass-panel">

      <div className="confidence-card-top">

        <span className="confidence-label">
          DECISION RISK
        </span>

        <span
          className={`confidence-badge ${riskLevel
            .toLowerCase()}`}
        >
          {riskLevel}
        </span>

      </div>

      <h3>
        {riskLevel === "Not established"
          ? "Recommendation risk has not been established."
          : riskLevel === "Low"
          ? "Recommendation is relatively robust."
          : riskLevel === "Medium"
          ? "Recommendation has some sensitivity."
          : "Recommendation is highly sensitive."}
      </h3>

      <p>
        {riskLevel === "Not established"
          ? "Run the What-If Analysis to evaluate how the recommendation responds to changing transaction conditions."
          : riskLevel === "Low"
          ? "Most tested conditions preserve the same recovery strategy."
          : riskLevel === "Medium"
          ? "Some changes in transaction conditions can influence the optimal recovery strategy."
          : "Small changes in transaction conditions can materially change the recommended recovery strategy."}
      </p>

    </div>


    {/* UTILITY ADVANTAGE */}

    <div className="risk-card glass-panel">

      <div className="confidence-card-top">

        <span className="confidence-label">
          UTILITY ADVANTAGE
        </span>

      </div>

      <div className="risk-big-number">
        +{Number(utilityGap).toFixed(2)}
      </div>

      <p>
        Utility points above the next-best recovery strategy.
      </p>

    </div>

  </div>


  {/* INTERPRETATION */}

  <div className="risk-interpretation glass-panel">

    <span className="confidence-label">
      DIGITAL TWIN INTERPRETATION
    </span>

    <p>

      The recommended strategy{" "}
      <strong>
        {recommendedStrategyName}
      </strong>{" "}

      {recommendationConfidence !== null ? (
        <>
          remains stable across{" "}
          <strong>
            {recommendationConfidence}%
          </strong>{" "}
          of the tested scenarios.
        </>
      ) : (
        <>
          has not yet been tested against alternative conditions.
        </>
      )}

      {" "}

      Its utility advantage over the next-best strategy is{" "}

      <strong>
        {Number(utilityGap).toFixed(2)}
      </strong>{" "}

      points.

      {" "}

      {riskLevel === "Low"
        ? "This indicates a relatively robust decision under the tested conditions."
        : riskLevel === "Medium"
        ? "This indicates that the decision should be monitored when transaction conditions change."
        : "This indicates that the decision is sensitive to changing transaction conditions and should be treated cautiously."}

    </p>

  </div>

</motion.section>

{/* -------------------------------- */}
{/* STEP 25 — DIGITAL TWIN ADVANTAGE */}
{/* -------------------------------- */}

<motion.section
  className="digital-twin-advantage-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="digital-twin-advantage-header">

    <div>

      <span className="section-eyebrow">
        DIGITAL TWIN VALIDATION
      </span>

      <h2>
        Why the Digital Twin adds value.
      </h2>

      <p>
        The Digital Twin was evaluated against fixed recovery
        policies using held-out payment transactions. The results
        measure whether adaptive strategy selection produces
        higher overall utility.
      </p>

    </div>

  </div>


  {/* MAIN VALIDATION CARD */}

  <div className="digital-twin-validation-card glass-panel">

    <div className="validation-main">

      <div className="validation-icon">
        <Trophy size={22} />
      </div>

      <div>

        <span className="validation-label">
          VALIDATED ADVANTAGE
        </span>

        <div className="validation-percentage">
          {evaluationLoading
            ? "—"
            : `+${digitalTwinImprovement.toFixed(2)}%`}
        </div>

        <p>
          Higher mean utility than the best fixed recovery policy.
        </p>

      </div>

    </div>


    <div className="validation-divider" />


    <div className="validation-metrics">

      {/* DIGITAL TWIN */}

      <div className="validation-metric">

        <span>
          Digital Twin mean utility
        </span>

        <strong>
          {evaluationLoading
            ? "—"
            : digitalTwinMeanUtility.toFixed(2)}
        </strong>

      </div>


      {/* BEST FIXED POLICY */}

      <div className="validation-metric">

        <span>
          Best fixed policy
        </span>

        <strong>
          {evaluationLoading
            ? "—"
            : bestFixedPolicy}
        </strong>

      </div>


      {/* FIXED POLICY UTILITY */}

      <div className="validation-metric">

        <span>
          Best fixed-policy utility
        </span>

        <strong>
          {evaluationLoading
            ? "—"
            : bestFixedPolicyUtility.toFixed(2)}
        </strong>

      </div>


      {/* UTILITY ADVANTAGE */}

      <div className="validation-metric">

        <span>
          Utility advantage
        </span>

        <strong>
          {evaluationLoading
            ? "—"
            : `+${digitalTwinAdvantage.toFixed(2)}`}
        </strong>

      </div>


      {/* TEST DATASET */}

      <div className="validation-metric">

        <span>
          Transactions evaluated
        </span>

        <strong>
          {evaluationLoading
            ? "—"
            : evaluationTransactionCount.toLocaleString()}
        </strong>

      </div>

    </div>

  </div>


  {/* EXPLANATION */}

  <div className="digital-twin-validation-explanation">

    <div className="validation-explanation-icon">
      <BrainCircuit size={19} />
    </div>

    <div>

      <span>
        WHAT THIS MEANS
      </span>

      <p>

        Instead of applying the same recovery action to every
        failed payment, the Digital Twin evaluates multiple
        possible recovery strategies for each transaction and
        selects the strategy with the highest expected utility.

        {" "}

        Across{" "}
        <strong>
          {evaluationLoading
            ? "the evaluated"
            : evaluationTransactionCount.toLocaleString()}
        </strong>{" "}
        held-out transactions, the Digital Twin achieved{" "}

        <strong>
          {evaluationLoading
            ? "a higher"
            : `${digitalTwinImprovement.toFixed(2)}% higher`}
        </strong>{" "}

        mean utility than the best fixed recovery policy.

      </p>

    </div>

  </div>


  {/* IMPORTANT METHODOLOGY NOTE */}

  <div className="digital-twin-validation-note">

    <span>
      EXPERIMENTAL EVIDENCE
    </span>

    <p>
      This percentage represents aggregate performance on the
      evaluation dataset. It is not a guarantee that every
      individual payment will recover by the same percentage.
    </p>

  </div>

</motion.section>

{/* -------------------------------- */}
{/* STEP 25E — POLICY COMPARISON */}
{/* -------------------------------- */}

<motion.section
  className="policy-comparison-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="policy-comparison-header">

    <div>

      <span className="section-eyebrow">
        POLICY COMPARISON
      </span>

      <h2>
        Adaptive decisions outperform fixed policies.
      </h2>

      <p>
        The Digital Twin dynamically selects a recovery strategy
        for each failed payment. This experiment compares that
        adaptive approach against applying one fixed recovery
        policy to every transaction.
      </p>

    </div>

  </div>


  {/* COMPARISON CARD */}

  <div className="policy-comparison-card glass-panel">

    <div className="policy-comparison-chart">

      {/* DIGITAL TWIN */}

      <div className="policy-bar-row">

        <div className="policy-bar-info">

          <div>

            <span className="policy-bar-label">
              DIGITAL TWIN
            </span>

            <strong>
              {evaluationLoading
                ? "—"
                : digitalTwinMeanUtility.toFixed(2)}
            </strong>

          </div>

          <span className="policy-bar-badge">
            Adaptive
          </span>

        </div>


        <div className="policy-bar-track">

          <motion.div
            className="policy-bar-fill policy-bar-digital-twin"
            initial={{ width: 0 }}
            animate={{
              width: evaluationLoading
                ? "0%"
                : `${Math.min(
                    (digitalTwinMeanUtility /
                      Math.max(
                        digitalTwinMeanUtility,
                        bestFixedPolicyUtility,
                        1
                      )) *
                      100,
                    100
                  )}%`,
            }}
            transition={{
              duration: 1,
              delay: 0.15,
            }}
          />

        </div>

      </div>


      {/* BEST FIXED POLICY */}

      <div className="policy-bar-row">

        <div className="policy-bar-info">

          <div>

            <span className="policy-bar-label">
              BEST FIXED POLICY
            </span>

            <strong>
              {evaluationLoading
                ? "—"
                : bestFixedPolicyUtility.toFixed(2)}
            </strong>

          </div>

          <span className="policy-bar-badge fixed">
            {evaluationLoading
              ? "Fixed"
              : bestFixedPolicy}
          </span>

        </div>


        <div className="policy-bar-track">

          <motion.div
            className="policy-bar-fill policy-bar-fixed"
            initial={{ width: 0 }}
            animate={{
              width: evaluationLoading
                ? "0%"
                : `${Math.min(
                    (bestFixedPolicyUtility /
                      Math.max(
                        digitalTwinMeanUtility,
                        bestFixedPolicyUtility,
                        1
                      )) *
                      100,
                    100
                  )}%`,
            }}
            transition={{
              duration: 1,
              delay: 0.3,
            }}
          />

        </div>

      </div>

    </div>


    {/* ADVANTAGE */}

    <div className="policy-comparison-result">

      <div className="policy-result-number">

        {evaluationLoading
          ? "—"
          : `+${digitalTwinAdvantage.toFixed(2)}`}

      </div>

      <div>

        <span>
          UTILITY ADVANTAGE
        </span>

        <p>

          The Digital Twin generated{" "}

          <strong>
            {evaluationLoading
              ? "higher"
              : `${digitalTwinAdvantage.toFixed(2)} more`}
          </strong>{" "}

          utility points than the best fixed recovery policy.

        </p>

      </div>

    </div>

  </div>


  {/* INTERPRETATION */}

  <div className="policy-comparison-insight">

    <div className="policy-insight-icon">
      <TrendingUp size={19} />
    </div>

    <div>

      <span>
        WHY THIS MATTERS
      </span>

      <p>

        A fixed policy treats every failed payment the same way.
        The Digital Twin instead evaluates the transaction context
        and chooses among multiple recovery strategies.

        {" "}

        In this evaluation, the adaptive approach achieved{" "}

        <strong>
          {evaluationLoading
            ? "higher"
            : `${digitalTwinImprovement.toFixed(2)}% higher`}
        </strong>{" "}

        mean utility than the best fixed policy across{" "}

        <strong>
          {evaluationLoading
            ? "the evaluation dataset"
            : evaluationTransactionCount.toLocaleString()}
        </strong>{" "}

        transactions.

      </p>

    </div>

  </div>


  {/* METHODOLOGY */}

  <div className="policy-comparison-methodology">

    <span>
      EVALUATION METHOD
    </span>

    <p>
      Each failed payment is evaluated using the same transaction
      context. The Digital Twin selects the highest-utility strategy
      for each transaction, while fixed-policy baselines apply the
      same recovery action throughout the evaluation set.
    </p>

  </div>

</motion.section>

{/* -------------------------------- */}
{/* STEP 25F — BASELINE BREAKDOWN */}
{/* -------------------------------- */}

<motion.section
  className="baseline-breakdown-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="baseline-breakdown-header">

    <span className="section-eyebrow">
      BASELINE ANALYSIS
    </span>

    <h2>
      How each recovery policy compares.
    </h2>

    <p>
      The Digital Twin is compared against every fixed recovery
      policy evaluated on the same held-out transaction set.
    </p>

  </div>


  {evaluationLoading ? (

    <div className="baseline-loading glass-panel">
      Loading baseline comparison...
    </div>

  ) : evaluationError ? (

    <div className="baseline-error glass-panel">
      {evaluationError}
    </div>

  ) : evaluationResults ? (

    <div className="baseline-breakdown-card glass-panel">

      <div className="baseline-table">

        {/* TABLE HEADER */}

        <div className="baseline-row baseline-header-row">

          <span>
            Recovery Policy
          </span>

          <span>
            Mean Utility
          </span>

          <span>
            vs Digital Twin
          </span>

        </div>


        {/* DIGITAL TWIN */}

        <div className="baseline-row baseline-digital-twin">

          <div className="baseline-policy-name">

            <strong>
              Digital Twin
            </strong>

            <span>
              Adaptive
            </span>

          </div>

          <strong className="baseline-utility">
            {digitalTwinMeanUtility.toFixed(2)}
          </strong>

          <span className="baseline-current-badge">
            Reference
          </span>

        </div>


        {/* PAYMENT LINK */}

        <div className="baseline-row">

          <div className="baseline-policy-name">

            <strong>
              Send Payment Link
            </strong>

            <span>
              Fixed policy
            </span>

          </div>

          <strong className="baseline-utility">
            {Number(
              evaluationResults
                ?.fixed_policy_mean_utility
                ?.["Send Payment Link"] ?? 0
            ).toFixed(2)}
          </strong>

          <span className="baseline-improvement">
            +{Number(
              evaluationResults
                ?.percentage_improvement
                ?.["Send Payment Link"] ?? 0
            ).toFixed(2)}%
          </span>

        </div>


        {/* RETRY 6 HOURS */}

        <div className="baseline-row">

          <div className="baseline-policy-name">

            <strong>
              Retry after 6 hours
            </strong>

            <span>
              Fixed policy
            </span>

          </div>

          <strong className="baseline-utility">
            {Number(
              evaluationResults
                ?.fixed_policy_mean_utility
                ?.["Retry after 6 hours"] ?? 0
            ).toFixed(2)}
          </strong>

          <span className="baseline-improvement">
            +{Number(
              evaluationResults
                ?.percentage_improvement
                ?.["Retry after 6 hours"] ?? 0
            ).toFixed(2)}%
          </span>

        </div>


        {/* WAIT */}

        <div className="baseline-row">

          <div className="baseline-policy-name">

            <strong>
              Wait
            </strong>

            <span>
              Fixed policy
            </span>

          </div>

          <strong className="baseline-utility">
            {Number(
              evaluationResults
                ?.fixed_policy_mean_utility
                ?.["Wait"] ?? 0
            ).toFixed(2)}
          </strong>

          <span className="baseline-improvement">
            +{Number(
              evaluationResults
                ?.percentage_improvement
                ?.["Wait"] ?? 0
            ).toFixed(2)}%
          </span>

        </div>


        {/* RETRY 30 MINUTES */}

        <div className="baseline-row">

          <div className="baseline-policy-name">

            <strong>
              Retry after 30 minutes
            </strong>

            <span>
              Fixed policy
            </span>

          </div>

          <strong className="baseline-utility">
            {Number(
              evaluationResults
                ?.fixed_policy_mean_utility
                ?.["Retry after 30 minutes"] ?? 0
            ).toFixed(2)}
          </strong>

          <span className="baseline-improvement">
            +{Number(
              evaluationResults
                ?.percentage_improvement
                ?.["Retry after 30 minutes"] ?? 0
            ).toFixed(2)}%
          </span>

        </div>

      </div>


      {/* SUMMARY */}

      <div className="baseline-summary">

        <div>

          <span>
            BEST FIXED BASELINE
          </span>

          <strong>
            {bestFixedPolicy}
          </strong>

        </div>


        <div>

          <span>
            DIGITAL TWIN IMPROVEMENT
          </span>

          <strong>
            +{digitalTwinImprovement.toFixed(2)}%
          </strong>

        </div>


        <div>

          <span>
            EVALUATION SET
          </span>

          <strong>
            {evaluationTransactionCount.toLocaleString()} transactions
          </strong>

        </div>

      </div>

    </div>

  ) : null}

</motion.section>

{/* -------------------------------- */}
{/* STEP 21 — MODEL PERFORMANCE */}
{/* -------------------------------- */}

<motion.section
  className="model-performance-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="model-performance-header">

    <span className="section-eyebrow">
      MODEL PERFORMANCE
    </span>

    <h2>
      How well does the prediction model perform?
    </h2>

    <p>
      Evaluation metrics from the trained recovery prediction
      model used by the Digital Twin.
    </p>

  </div>


  {modelPerformanceLoading && (
    <div className="model-performance-loading glass-panel">
      Loading model performance...
    </div>
  )}


  {modelPerformanceError && (
    <div className="model-performance-error glass-panel">
      {modelPerformanceError}
    </div>
  )}


  {modelPerformance && !modelPerformanceLoading && (
    <div className="model-performance-grid">

      {/* ACCURACY */}

      <div className="model-metric-card glass-panel">

        <span>
          Accuracy
        </span>

        <strong>
          {(Number(
            modelPerformance.accuracy ?? 0
          ) * 100).toFixed(2)}%
        </strong>

        <p>
          Overall prediction correctness.
        </p>

      </div>


      {/* PRECISION */}

      <div className="model-metric-card glass-panel">

        <span>
          Precision
        </span>

        <strong>
          {(Number(
            modelPerformance.precision ?? 0
          ) * 100).toFixed(2)}%
        </strong>

        <p>
          Reliability of positive recovery predictions.
        </p>

      </div>


      {/* RECALL */}

      <div className="model-metric-card glass-panel">

        <span>
          Recall
        </span>

        <strong>
          {(Number(
            modelPerformance.recall ?? 0
          ) * 100).toFixed(2)}%
        </strong>

        <p>
          Recovery cases correctly identified.
        </p>

      </div>


      {/* F1 SCORE */}

      <div className="model-metric-card glass-panel">

        <span>
          F1 Score
        </span>

        <strong>
          {(Number(
            modelPerformance.f1_score ?? 0
          ) * 100).toFixed(2)}%
        </strong>

        <p>
          Balance between precision and recall.
        </p>

      </div>


      {/* ROC-AUC */}

      <div className="model-metric-card glass-panel">

        <span>
          ROC-AUC
        </span>

        <strong>
          {(Number(
            modelPerformance.roc_auc ?? 0
          ) * 100).toFixed(2)}%
        </strong>

        <p>
          Ability to distinguish recovery outcomes.
        </p>

      </div>
      <div className="feature-importance-container">
  <div className="feature-importance-header">
    <div>
      <div className="section-eyebrow">
        <BrainCircuit size={15} />
        MODEL INTERPRETATION
      </div>

      <h3>What influences recovery?</h3>

      <p>
        The Random Forest identifies which transaction
        characteristics contribute most to recovery
        prediction.
      </p>
    </div>
  </div>

  {modelPerformanceLoading ? (
    <div className="feature-importance-state">
      Loading feature importance...
    </div>
  ) : modelPerformanceError ? (
    <div className="feature-importance-state error">
      Unable to load feature importance.
    </div>
  ) : topFeatures.length === 0 ? (
    <div className="feature-importance-state">
      Feature importance is not available.
    </div>
  ) : (
    <div className="feature-importance-list">
      {topFeatures.map((item, index) => {
        const featureName =
          item.feature
            ?.replaceAll("_", " ")
            .replace(/\b\w/g, (char) =>
              char.toUpperCase()
            ) || `Feature ${index + 1}`;

        const percentage =
          Number(item.percentage ?? 0);

        return (
          <motion.div
            className="feature-importance-row"
            key={item.feature || index}
            initial={{
              opacity: 0,
              x: -15,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
            transition={{
              duration: 0.4,
              delay: index * 0.06,
            }}
          >
            <div className="feature-importance-top">
              <div className="feature-importance-name">
                <span className="feature-rank">
                  {String(index + 1).padStart(2, "0")}
                </span>

                <strong>
                  {featureName}
                </strong>
              </div>

              <span className="feature-importance-value">
                {percentage.toFixed(2)}%
              </span>
            </div>

            <div className="feature-importance-track">
              <motion.div
                className="feature-importance-fill"
                initial={{
                  width: 0,
                }}
                animate={{
                  width: `${Math.min(
                    percentage,
                    100
                  )}%`,
                }}
                transition={{
                  duration: 0.7,
                  delay: index * 0.06,
                }}
              />
            </div>
          </motion.div>
        );
      })}
    </div>
  )}
</div>

    </div>
    
  )}
  <div className="confusion-matrix-container">
  <div className="confusion-matrix-header">
    <div>
      <div className="section-eyebrow">
        <Grid2X2 size={15} />
        MODEL DIAGNOSTICS
      </div>

      <h3>Confusion Matrix</h3>

      <p>
        How the recovery predictor classified successful and
        unsuccessful payment recovery outcomes.
      </p>
    </div>
  </div>

  <div className="confusion-matrix-wrapper">
    <div className="matrix-axis-label predicted-label">
      Predicted
    </div>

    <div className="matrix-axis-label actual-label">
      Actual
    </div>

    <div className="confusion-matrix">
      <div className="matrix-corner"></div>

      <div className="matrix-column-label">
        Not Recovered
      </div>

      <div className="matrix-column-label">
        Recovered
      </div>

      <div className="matrix-row-label">
        Not Recovered
      </div>

      <div className="matrix-cell true-negative">
        <span className="matrix-value">
          {trueNegative}
        </span>

        <span className="matrix-label">
          True Negative
        </span>
      </div>

      <div className="matrix-cell false-positive">
        <span className="matrix-value">
          {falsePositive}
        </span>

        <span className="matrix-label">
          False Positive
        </span>
      </div>

      <div className="matrix-row-label">
        Recovered
      </div>

      <div className="matrix-cell false-negative">
        <span className="matrix-value">
          {falseNegative}
        </span>

        <span className="matrix-label">
          False Negative
        </span>
      </div>

      <div className="matrix-cell true-positive">
        <span className="matrix-value">
          {truePositive}
        </span>

        <span className="matrix-label">
          True Positive
        </span>
      </div>
    </div>
  </div>

  <div className="confusion-matrix-insight">
    <BrainCircuit size={18} />

    <p>
      The model correctly identified{" "}
      <strong>{truePositive}</strong> recovered payments,
      while{" "}
      <strong>{falseNegative}</strong> recovered payments
      were incorrectly classified as unsuccessful.
    </p>
  </div>
</div>

</motion.section>

{/* -------------------------------- */}
{/* STEP 17 — EXECUTIVE DECISION SUMMARY */}
{/* -------------------------------- */}

<motion.section
  className="executive-summary-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="executive-summary-header">
    <span className="section-eyebrow">
      DECISION AT A GLANCE
    </span>

    <h2>
      The Digital Twin's decision.
    </h2>

    <p>
      A concise summary of the recommended recovery action,
      its expected financial outcome, and the conditions that
      influence the decision.
    </p>
  </div>


  <div className="executive-summary-card glass-panel">

    {/* MAIN DECISION */}

    <div className="executive-main-decision">

      <span className="sensitivity-label">
        RECOMMENDED ACTION
      </span>

      <h3>
        {recommendedStrategyName}
      </h3>

      <p>
        This recovery strategy produced the highest utility
        among the simulated recovery futures.
      </p>

    </div>


    {/* KEY NUMBERS */}

    <div className="executive-summary-metrics">

      <div className="executive-metric">

        <span>
          Recovery probability
        </span>

        <strong>
          {Number(
            recoveryProbability
          ).toFixed(1)}%
        </strong>

      </div>


      <div className="executive-metric">

        <span>
          Expected recovery
        </span>

        <strong>
          ₹{Number(
            expectedRecovery
          ).toFixed(2)}
        </strong>

      </div>


      <div className="executive-metric">

        <span>
          Utility score
        </span>

        <strong>
          {Number(
            utilityScore
          ).toFixed(2)}
        </strong>

      </div>


      <div className="executive-metric">

        <span>
          Decision confidence
        </span>

        <strong>
          {recommendationConfidence !== null
            ? `${recommendationConfidence}%`
            : "Not established"}
        </strong>

      </div>

    </div>


    {/* DECISION LOGIC */}

    <div className="executive-logic">

      <div className="executive-logic-item">

        <span className="logic-number">
          01
        </span>

        <div>
          <strong>
            Highest utility
          </strong>

          <p>
            The recommended strategy outperformed the
            next-best recovery path by{" "}
            <strong>
              {Number(utilityGap).toFixed(2)}
            </strong>{" "}
            utility points.
          </p>
        </div>

      </div>


      <div className="executive-logic-item">

        <span className="logic-number">
          02
        </span>

        <div>
          <strong>
            Scenario robustness
          </strong>

          <p>
            The recommendation remained stable across{" "}
            <strong>
  {recommendationConfidence !== null
    ? `${recommendationConfidence}%`
    : "Not established"}
</strong>{" "}
            of the tested alternative conditions.
          </p>
        </div>

      </div>


      <div className="executive-logic-item">

        <span className="logic-number">
          03
        </span>

        <div>
          <strong>
            Decision risk
          </strong>

          <p>
            Current decision risk is classified as{" "}
            <strong>
              {riskLevel}
            </strong>
            .
          </p>
        </div>

      </div>

    </div>


    {/* FINAL TAKEAWAY */}

    <div className="executive-takeaway">

      <span>
        FINAL TAKEAWAY
      </span>

      <p>

        <strong>
          {recommendedStrategyName}
        </strong>{" "}

        is currently the strongest recovery action.

        The Digital Twin estimates{" "}
        
        <strong>
          {Number(
            recoveryProbability
          ).toFixed(1)}%
        </strong>{" "}

        recovery probability with an expected recovery
        of{" "}

        <strong>
          ₹{Number(
            expectedRecovery
          ).toFixed(2)}
        </strong>
        .

        Based on the tested scenarios, the recommendation
        has{" "}

        <strong>
          {recommendationConfidence !== null
            ? `${recommendationConfidence}%`
            : "Not established"}
        </strong>{" "}

        scenario stability.

      </p>

    </div>

  </div>

</motion.section>
{/* -------------------------------- */}
{/* STEP 19 — DECISION AUDIT TRAIL */}
{/* -------------------------------- */}

<motion.section
  className="decision-audit-section"
  initial={{ opacity: 0, y: 25 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>

  <div className="decision-audit-header">

    <span className="section-eyebrow">
      DECISION AUDIT TRAIL
    </span>

    <h2>
      How the Digital Twin reached its decision.
    </h2>

    <p>
      The recommendation is generated through a sequence of
      simulation, financial evaluation, optimization, and
      sensitivity testing.
    </p>

  </div>


  <div className="decision-audit-card glass-panel">

    {/* STEP 01 */}

    <div className="audit-step">

      <div className="audit-step-number">
        01
      </div>

      <div className="audit-step-content">

        <span>
          INPUT
        </span>

        <h3>
          Payment failure identified
        </h3>

        <p>
          The Digital Twin begins with the failed transaction
          and its customer, payment, and transaction context.
        </p>

      </div>

      <div className="audit-step-value">

        ₹{Number(
          inputPayment.amount ?? 0
        ).toFixed(2)}

      </div>

    </div>


    {/* STEP 02 */}

    <div className="audit-step">

      <div className="audit-step-number">
        02
      </div>

      <div className="audit-step-content">

        <span>
          SIMULATION
        </span>

        <h3>
          Recovery strategies evaluated
        </h3>

        <p>
          The Digital Twin evaluates multiple recovery paths
          under the same payment conditions.
        </p>

      </div>

      <div className="audit-step-value">

        {sortedStrategies.length} strategies

      </div>

    </div>


    {/* STEP 03 */}

    <div className="audit-step">

      <div className="audit-step-number">
        03
      </div>

      <div className="audit-step-content">

        <span>
          PREDICTION
        </span>

        <h3>
          Recovery probability estimated
        </h3>

        <p>
          The trained recovery prediction model estimates the
          probability of successfully recovering the payment
          for each strategy.
        </p>

      </div>

      <div className="audit-step-value">

        {Number(
          recoveryProbability
        ).toFixed(1)}%

      </div>

    </div>


    {/* STEP 04 */}

    <div className="audit-step">

      <div className="audit-step-number">
        04
      </div>

      <div className="audit-step-content">

        <span>
          FINANCIAL OUTCOME
        </span>

        <h3>
          Expected recovery calculated
        </h3>

        <p>
          Recovery probability is translated into an expected
          monetary recovery for the failed transaction.
        </p>

      </div>

      <div className="audit-step-value">

        ₹{Number(
          expectedRecovery
        ).toFixed(2)}

      </div>

    </div>


    {/* STEP 05 */}

    <div className="audit-step">

      <div className="audit-step-number">
        05
      </div>

      <div className="audit-step-content">

        <span>
          OPTIMIZATION
        </span>

        <h3>
          Utility scores compared
        </h3>

        <p>
          Each recovery path is evaluated using expected
          recovery, operational cost, and customer friction.
        </p>

      </div>

      <div className="audit-step-value">

        {Number(
          utilityScore
        ).toFixed(2)}

      </div>

    </div>

    {/* UTILITY CALCULATION */}

<div className="audit-utility-breakdown">

  <div className="audit-utility-header">

    <div>

      <span>
        UTILITY CALCULATION
      </span>

      <h3>
        How the Digital Twin evaluates value.
      </h3>

    </div>

  </div>


  <div className="utility-formula">

    <div className="formula-item">

      <span>
        Expected recovery
      </span>

      <strong>
        ₹{Number(
          expectedRecovery
        ).toFixed(2)}
      </strong>

    </div>


    <div className="formula-operator">
      −
    </div>


    <div className="formula-item">

      <span>
        Strategy cost
      </span>

      <strong>
        ₹{Number(
          recommendedStrategy.average_cost ??
          recommendedStrategy.cost ??
          0
        ).toFixed(2)}
      </strong>

    </div>


    <div className="formula-operator">
      −
    </div>


    <div className="formula-item">

      <span>
        Friction penalty
      </span>

      <strong>
        ₹{Number(
          recommendedStrategy.friction_penalty ??
          (
            Number(inputPayment.amount ?? 0) *
            Number(recommendedStrategy.friction ?? 0) *
            0.05
          )
        ).toFixed(2)}
      </strong>

    </div>


    <div className="formula-operator">
      =
    </div>


    <div className="formula-item formula-result">

      <span>
        Utility score
      </span>

      <strong>
        {Number(
          utilityScore
        ).toFixed(2)}
      </strong>

    </div>

  </div>


  <p className="utility-explanation">

    The Digital Twin prioritizes strategies that maximize
    expected financial recovery while accounting for
    operational cost and customer friction.

  </p>

</div>


    {/* STEP 06 */}

    <div className="audit-step audit-step-final">

      <div className="audit-step-number">
        06
      </div>

      <div className="audit-step-content">

        <span>
          DECISION
        </span>

        <h3>
          Recommended strategy selected
        </h3>

        <p>
          The strategy with the highest overall utility becomes
          the Digital Twin's recommended recovery action.
        </p>

      </div>

      <div className="audit-step-value audit-winner">

        {recommendedStrategyName}

      </div>

    </div>

  </div>


  {/* FINAL DECISION STATEMENT */}

  <div className="audit-conclusion glass-panel">

    <div>

      <span className="sensitivity-label">
        DECISION TRACE
      </span>

      <h3>
        {recommendedStrategyName} is the current optimal action.
      </h3>

      <p>
        The Digital Twin selected this strategy because it
        produced the highest utility score of{" "}
        <strong>
          {Number(utilityScore).toFixed(2)}
        </strong>
        {" "}among the simulated recovery paths.

        {recommendationConfidence !== null && (
          <>
            {" "}The recommendation remained stable across{" "}
            <strong>
              {recommendationConfidence}%
            </strong>{" "}
            of the tested alternative conditions.
          </>
        )}
      </p>

    </div>

  </div>

</motion.section>

    </main>
  );
}

export default ResultsDashboard;