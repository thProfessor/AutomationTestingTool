console.log("working");
// Static data
var successPercentage = 0;
var failurePercentage = 0;
pieChart = document.getElementById("resultsChart");

function createData() {
    var dataset = document.getElementById("dataset");
    var data2 = dataset.innerText;
    var res = data2.replace(/'/g, '"');
    var check = JSON.parse(res);
    var fails = 0;
    var total = check.length;
    for (var i = 0; i < total; i++) {
        if (check[i].Status.includes("Failed") || check[i].ResponseTime.includes("Failed") || check[i].ResponseValidation.includes("Invalid") || check[i].ResponseValidation.includes("failed")) {
            fails++;
        }
    }

    successPercentage = total - fails;
    failurePercentage = fails;
    createChart();
}
// Function to create a static pie chart
function createChart() {
    const ctx = pieChart.getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Success', 'Failure'],
            datasets: [{
                data: [successPercentage, failurePercentage],
                backgroundColor: ['#00c851', '#ff4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
    });
}

createData();

