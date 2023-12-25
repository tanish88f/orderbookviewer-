const socket = io.connect('http://localhost:6005');
let chart;

socket.on('connect', () => {
    console.log('Connected to server');
});

function populateTable(tableId, data, isBid) {
    const table = document.getElementById(tableId).getElementsByTagName('table')[0];
    while (table.rows.length > 0) {
        table.deleteRow(0);
    }
    if (isBid) {
        const labelRow = table.insertRow(-1);
        const priceCell = labelRow.insertCell(0);
        const volumeCell = labelRow.insertCell(1);
        priceCell.textContent = 'Price';
        volumeCell.textContent = 'Volume';

        // Make the labels bolder and black, and fill the cell with light gray
        priceCell.style.fontWeight = 'bold';
        volumeCell.style.fontWeight = 'bold';
        priceCell.style.color = 'black';
        volumeCell.style.color = 'black';
        priceCell.style.backgroundColor = 'lightgray';
        volumeCell.style.backgroundColor = 'lightgray';
    }
    let cumulativeVolumes = {};
    let totalVolume = 0;  
    data.forEach(([price, quantity]) => {
        if (cumulativeVolumes[price]) {
            cumulativeVolumes[price] += quantity;
        } else {
            cumulativeVolumes[price] = quantity;
        }
        totalVolume += quantity;
    });

    data.forEach(([price, quantity]) => {
        const row = table.insertRow(-1);
        row.insertCell(0).textContent = price;
        row.insertCell(1).textContent = cumulativeVolumes[price];
        const volumePercentage = cumulativeVolumes[price] / totalVolume;
        const defaultIntensity = 60;  // Default color intensity
        const minIntensity = 50;  // Minimum color intensity
        const maxIntensity = 200;  // Maximum color intensity
        let colorIntensity = defaultIntensity + Math.floor((255 - defaultIntensity) * (1 - volumePercentage));  // Adjust the color intensity
        colorIntensity = Math.max(minIntensity, colorIntensity);  // Ensure colorIntensity does not go below minIntensity
        colorIntensity = Math.min(maxIntensity, colorIntensity);  // Ensure colorIntensity does not go above maxIntensity
        row.style.backgroundColor = isBid ? `rgb(${colorIntensity}, 255, ${colorIntensity})` : `rgb(255, ${colorIntensity}, ${colorIntensity})`; 
    });
}
document.getElementById('update-button').addEventListener('click', function() {
    const symbol = document.getElementById('symbol-select').value;
    fetch('/update_symbol', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol: symbol }),
    });
});


window.onload = function() {
    const ctx = document.getElementById('myChart').getContext('2d');
    chart = new Chart(ctx, { // Assign to chart here
        type: 'line',
        data: {
            labels: [], // This will be filled with the indices of the data array
            datasets: [{
                label: '',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            animation: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
};

function clearChart(chart) {
    chart.data.labels = [];
    chart.data.datasets = [];
    chart.update();
}
socket.on('price_paths', (pricePaths) => {
    // Clear the chart
    clearChart(chart);

    // Add the new price paths to the chart
    chart.data.labels = Array.from({length: pricePaths[0].length}, (_, i) => i + 1);
    pricePaths.forEach((pricePath, index) => {
        chart.data.datasets.push({
            label: 'Price Path ' + (index + 1),
            data: pricePath,
            backgroundColor: 'rgba(0, 0, 0, 0)', // Transparent background
            borderColor: `hsl(${index * 360 / pricePaths.length}, 100%, 50%)`, // Different color for each path
            borderWidth: 1,
            lineTension: 0, // Makes the line straight instead of curved
            pointRadius: 0, // Hides the points along the line
        });
    });

    // Update the chart
    chart.update();
});

socket.on('orderbook', (orderBook) => {
    const sortedBids = orderBook.bids.sort((a, b) => b[0] - a[0]);
    const sortedAsks = orderBook.asks.sort((a, b) => b[0] - a[0]);  // Sort asks in ascending order
    populateTable('bids', sortedBids, true);  // Populate 'bids' table with bids
    populateTable('asks', sortedAsks, false);  // Populate 'asks' table with asks
});
