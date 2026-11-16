
let nutrientChart;
let cropChart;

function updateCharts(n, p, k, crops) {

    if (nutrientChart) nutrientChart.destroy();
    if (cropChart) cropChart.destroy();

    nutrientChart = new Chart(
        document.getElementById("nutrientChart"),
        {
            type: "bar",
            data: {
                labels: ["Nitrogen", "Phosphorus", "Potassium"],
                datasets: [{
                    label: "NPK Values",
                    data: [n, p, k],
                    backgroundColor: [
                        "#32965a",
                        "#e6a23c",
                        "#4387c7"
                    ],
                    borderRadius: 7
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );

    cropChart = new Chart(
        document.getElementById("cropChart"),
        {
            type: "doughnut",
            data: {
                labels: crops.map(c => c.name),
                datasets: [{
                    data: crops.map(c => c.score),
                    backgroundColor: [
                        "#21834b",
                        "#e6a23c",
                        "#4387c7"
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        }
    );
}

document.getElementById("today").textContent =
    new Date().toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric"
    });
