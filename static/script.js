let moodChart;

document.getElementById("moodForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const entry = document.getElementById("entry").value;

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entry }),
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const raw = await res.text();
    console.log("Raw response:", raw);

    let data;
    try {
      data = JSON.parse(raw);
    } catch (err) {
      throw new Error("Invalid JSON response");
    }

    document.getElementById("result").innerText = `Mood: ${data.mood} (${data.score}%)`;
    loadChart();
  } catch (err) {
    console.error("Error:", err.message);
    document.getElementById("result").innerText = `Error: ${err.message}`;
  }
});

async function loadChart() {
  try {
    const res = await fetch("/history");
    if (!res.ok) throw new Error("Failed to fetch history");

    const raw = await res.text();
    const data = JSON.parse(raw);

    const labels = data.map(d => new Date(d.timestamp).toLocaleString());
    const scores = data.map(d => d.score);

    const ctx = document.getElementById("moodChart").getContext("2d");
    // Destroy previous chart if it exists
    if (moodChart) {
      moodChart.destroy();
    }

    // Create new chart and assign to global variable

    moodChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Mood Score",
          data: scores,
          borderColor: "blue",
          fill: false
        }]
      }
    });
  } catch (err) {
    console.error("Chart error:", err.message);
  }
}

document.getElementById("result").innerText = "Analyzing Mood...";