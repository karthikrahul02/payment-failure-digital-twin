import { useState } from "react";
import { motion } from "framer-motion";
import ResultsDashboard from "./components/ResultsDashboard";
import {
  Activity,
  ArrowUpRight,
  ArrowLeft,
  ShieldCheck,
  Sparkles,
  Play,
  RotateCcw,
  TrendingUp,
  IndianRupee,
  Trophy,
  Check,
  AlertTriangle,
  CreditCard,
  User,
  Clock3,
  ChevronDown,
} from "lucide-react";
import "./App.css";
import { simulatePayment } from "./services/api";

function App() {
  
  const [showWorkspace, setShowWorkspace] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    transaction_id: "TXN_001",
    customer_id: "CUST_001",
    amount: "5000",
    payment_method: "UPI",
    failure_reason: "TEMPORARY_BANK_ERROR",
    customer_segment: "REGULAR",
    historical_success_rate: "0.85",
    average_transaction_amount: "4500",
    transaction_hour: "14",
  });

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSimulation = async () => {
  try {
    setIsLoading(true);
    setError(null);
    setSimulationResult(null);

    const payload = {
      ...formData,
      amount: Number(formData.amount),
      historical_success_rate: Number(formData.historical_success_rate),
      average_transaction_amount: Number(
        formData.average_transaction_amount
      ),
      transaction_hour: Number(formData.transaction_hour),
    };

    const result = await simulatePayment(payload);

    console.log("Simulation result:", result);

    setSimulationResult(result);
  } catch (error) {
    console.error("Simulation failed:", error);
    setError(error.message);
  } finally {
    setIsLoading(false);
  }
};
const handleSensitivityAnalysis = async (inputData) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/sensitivity", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(inputData),
    });

    if (!response.ok) {
      throw new Error("Sensitivity analysis failed");
    }

    const data = await response.json();

    console.log("Sensitivity result:", data);

    return data;
  } catch (error) {
    console.error("Sensitivity analysis error:", error);
    return null;
  }
};
if (simulationResult) {
  return (
    <ResultsDashboard
      result={simulationResult}
      onBack={() => setSimulationResult(null)}
      onRunSensitivity={handleSensitivityAnalysis}
    />
  );
}
  if (showWorkspace) {
    return (
      <main className="app workspace-page">
        <div className="ambient ambient-one" />
        <div className="ambient ambient-two" />

        <nav className="navbar">
          <div className="brand">
            <div className="brand-icon">
              <Activity size={18} strokeWidth={2.5} />
            </div>

            <span>Recovery Twin</span>
          </div>

          <div className="nav-status">
            <span className="status-dot" />
            System Online
          </div>
        </nav>

        <section className="workspace">
          <div className="workspace-header">
            <div>
              <button
                className="back-button"
                onClick={() => setShowWorkspace(false)}
              >
                <ArrowLeft size={17} />
                Back to overview
              </button>

              <div className="workspace-title-row">
                <div>
                  <span className="workspace-eyebrow">
                    DIGITAL TWIN SIMULATION
                  </span>

                  <h1>Simulate a recovery future.</h1>

                  <p>
                    Configure the failed payment and let the recovery engine
                    evaluate the best possible actions.
                  </p>
                </div>

                <div className="simulation-status">
                  <span className="status-dot" />
                  Ready to simulate
                </div>
              </div>
            </div>
          </div>

          <div className="workspace-grid">
            <section className="simulation-form glass-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-number">01</span>
                  <h2>Failed payment</h2>
                  <p>Enter the transaction that needs recovery.</p>
                </div>

                <AlertTriangle size={22} />
              </div>

              <div className="form-grid">
                <div className="input-group">
                  <label>
                    <CreditCard size={15} />
                    Transaction ID
                  </label>

                  <input
                    type="text"
                    name="transaction_id"
                    value={formData.transaction_id}
                    onChange={handleChange}
                  />
                </div>

                <div className="input-group">
                  <label>
                    <User size={15} />
                    Customer ID
                  </label>

                  <input
                    type="text"
                    name="customer_id"
                    value={formData.customer_id}
                    onChange={handleChange}
                  />
                </div>

                <div className="input-group">
                  <label>
                    <IndianRupee size={15} />
                    Transaction Amount
                  </label>

                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                  />
                </div>

                <div className="input-group">
                  <label>Payment Method</label>

                  <div className="select-wrapper">
                    <select
                      name="payment_method"
                      value={formData.payment_method}
                      onChange={handleChange}
                    >
                      <option value="UPI">UPI</option>
                      <option value="CARD">Card</option>
                      <option value="NET_BANKING">Net Banking</option>
                      <option value="WALLET">Wallet</option>
                    </select>

                    <ChevronDown size={16} />
                  </div>
                </div>

                <div className="input-group full-width">
                  <label>Failure Reason</label>

                  <div className="select-wrapper">
                    <select
                      name="failure_reason"
                      value={formData.failure_reason}
                      onChange={handleChange}
                    >
                      <option value="TEMPORARY_BANK_ERROR">
                        Temporary Bank Error
                      </option>

                      <option value="INSUFFICIENT_FUNDS">
                        Insufficient Funds
                      </option>

                      <option value="NETWORK_ERROR">
                        Network Error
                      </option>

                      <option value="USER_CANCELLED">
                        User Cancelled
                      </option>
                    </select>

                    <ChevronDown size={16} />
                  </div>
                </div>
              </div>

              <div className="form-divider" />

              <div className="panel-header compact">
                <div>
                  <span className="panel-number">02</span>
                  <h2>Customer context</h2>
                  <p>Provide context to improve recovery prediction.</p>
                </div>
              </div>

              <div className="form-grid">
                <div className="input-group">
                  <label>Customer Segment</label>

                  <div className="select-wrapper">
                    <select
                      name="customer_segment"
                      value={formData.customer_segment}
                      onChange={handleChange}
                    >
                      <option value="REGULAR">Regular</option>
                      <option value="PREMIUM">Premium</option>
                      <option value="HIGH_VALUE">High Value</option>
                    </select>

                    <ChevronDown size={16} />
                  </div>
                </div>

                <div className="input-group">
                  <label>Historical Success Rate</label>

                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    name="historical_success_rate"
                    value={formData.historical_success_rate}
                    onChange={handleChange}
                  />
                </div>

                <div className="input-group">
                  <label>Average Transaction Amount</label>

                  <input
                    type="number"
                    name="average_transaction_amount"
                    value={formData.average_transaction_amount}
                    onChange={handleChange}
                  />
                </div>

                <div className="input-group">
                  <label>
                    <Clock3 size={15} />
                    Transaction Hour
                  </label>

                  <input
                    type="number"
                    min="0"
                    max="23"
                    name="transaction_hour"
                    value={formData.transaction_hour}
                    onChange={handleChange}
                  />
                </div>
              </div>

                            <button
                className="simulate-button"
                onClick={handleSimulation}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Activity size={18} className="spin-icon" />
                    Running Simulation...
                  </>
                ) : (
                  <>
                    <Play size={18} fill="currentColor" />
                    Run Digital Twin Simulation
                    <ArrowUpRight size={18} />
                  </>
                )}
              </button>
                {error && (
                  <div className="simulation-error">
                    {error}
                  </div>
                )}
            </section>

            <aside className="workspace-sidebar">
              <div className="sidebar-card glass-panel">
                <div className="sidebar-icon">
                  <Activity size={22} />
                </div>

                <span className="sidebar-label">Simulation Engine</span>

                <h3>Four possible futures.</h3>

                <p>
                  The Digital Twin will evaluate multiple recovery strategies
                  against this failed payment.
                </p>

                <div className="strategy-preview">
                  <div>
                    <span className="strategy-dot" />
                    Retry after 30 min
                  </div>

                  <div>
                    <span className="strategy-dot" />
                    Retry after 6 hours
                  </div>

                  <div>
                    <span className="strategy-dot" />
                    Wait
                  </div>

                  <div>
                    <span className="strategy-dot" />
                    Send Payment Link
                  </div>
                </div>
              </div>

              <div className="sidebar-card glass-panel insight-card">
                <Sparkles size={20} />

                <span className="sidebar-label">Decision Intelligence</span>

                <p>
                  Recommendations are ranked using predicted recovery,
                  operational cost, and customer friction.
                </p>

                <div className="insight-footer">
                  <ShieldCheck size={16} />
                  Utility-based optimization
                </div>
              </div>
            </aside>
          </div>
        
        </section>
      </main>
    );
  }
  return (
    <main className="app">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <nav className="navbar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={18} strokeWidth={2.5} />
          </div>

          <span>Recovery Twin</span>
        </div>

        <div className="nav-status">
          <span className="status-dot" />
          System Online
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <div className="eyebrow">
            <Sparkles size={15} />
            AI-POWERED PAYMENT RECOVERY
          </div>

          <h1>
            Turn payment failures
            <span> into recovery decisions.</span>
          </h1>

          <p>
            Simulate multiple recovery futures, compare outcomes, and identify
            the optimal action for every failed payment.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => setShowWorkspace(true)}
            >
              Launch Simulation
              <ArrowUpRight size={18} />
            </button>

            <div className="security-note">
              <ShieldCheck size={18} />
              <span>Decision intelligence powered by AI</span>
            </div>
          </div>
        </div>

        <div className="hero-visual glass-panel">
          <div className="visual-grid" />

          <div className="twin-core">
            <div className="core-ring ring-one" />
            <div className="core-ring ring-two" />

            <div className="core-center">
              <Activity size={34} />
            </div>
          </div>

          <div className="floating-card card-top">
            <span className="card-label">Recovery confidence</span>
            <strong>70.1%</strong>
          </div>

          <div className="floating-card card-bottom">
            <span className="card-label">Recommended action</span>
            <strong>Retry · 30 min</strong>
          </div>
        </div>
      </section>

      <section className="metrics">
        <div className="metric glass-panel">
          <span>Recovery Strategies</span>
          <strong>04</strong>
          <small>Simulated outcomes</small>
        </div>

        <div className="metric glass-panel">
          <span>Decision Engine</span>
          <strong>AI</strong>
          <small>Recovery probability model</small>
        </div>

        <div className="metric glass-panel">
          <span>Optimization</span>
          <strong>₹</strong>
          <small>Utility-based recommendation</small>
        </div>
      </section>
    </main>
  );
}

export default App;