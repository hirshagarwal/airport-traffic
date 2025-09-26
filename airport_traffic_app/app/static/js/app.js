document.addEventListener("DOMContentLoaded", () => {
  const airportSelect = document.getElementById("airport-select");
  const resultContainer = document.getElementById("prediction-result");

  if (!airportSelect || !resultContainer) {
    return;
  }

  airportSelect.addEventListener("change", async (event) => {
    const airportCode = event.target.value;
    if (!airportCode) {
      return;
    }

    resultContainer.classList.add("d-none");
    resultContainer.textContent = "Fetching estimate...";
    resultContainer.classList.remove("d-none", "alert-danger");
    resultContainer.classList.add("alert-info");

    try {
      const response = await fetch(`/estimate/${airportCode}`);
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      resultContainer.textContent = `Predicted passenger load at ${data.airport}: ${data.predicted_passenger_load}`;
    } catch (error) {
      resultContainer.textContent = "Unable to fetch prediction. Please try again.";
      resultContainer.classList.remove("alert-info");
      resultContainer.classList.add("alert-danger");
    }
  });
});
