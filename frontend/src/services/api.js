const API_BASE_URL = "http://127.0.0.1:8000";

export async function simulatePayment(paymentData) {
  const response = await fetch(`${API_BASE_URL}/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(paymentData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail || "Failed to run payment simulation"
    );
  }

  return response.json();
}