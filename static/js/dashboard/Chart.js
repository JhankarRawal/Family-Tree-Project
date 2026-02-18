// Function to render Gender Distribution Pie Chart
function renderGenderChart(genderLabels, genderCounts, canvasId = 'genderChart') {

    if (!genderLabels.length || !genderCounts.length) {
        console.warn("No gender data available to display chart");
        return;
    }

    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error("Canvas element not found:", canvasId);
        return;
    }

    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: genderLabels,
            datasets: [{
                data: genderCounts,
                backgroundColor: [
                    '#4ade80', // green
                    '#60a5fa', // blue
                    '#facc15', // yellow
                    '#f87171', // red
                    '#a78bfa'  // purple
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}
