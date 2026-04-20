document.addEventListener("DOMContentLoaded", () => {
  AOS.init({ duration: 700, once: true, easing: "ease-out-cubic" });

  const loader = document.getElementById("page-loader");
  if (loader) {
    setTimeout(() => loader.classList.add("hide"), 500);
  }

  if (window.dashboardChartData) {
    const canvas = document.getElementById("adminAnalyticsChart");
    if (canvas) {
      new Chart(canvas, {
        type: "bar",
        data: {
          labels: window.dashboardChartData.labels,
          datasets: [{
            label: "Percentage",
            data: window.dashboardChartData.values,
            borderRadius: 8,
            backgroundColor: ["#5b6cff", "#8b5cf6"]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });
    }
  }
});
