const socket = io.connect('http://localhost:6005');

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

socket.on('orderbook', (orderBook) => {
    const sortedBids = orderBook.bids.sort((a, b) => b[0] - a[0]);
    const sortedAsks = orderBook.asks.sort((a, b) => b[0] - a[0]);  // Sort asks in ascending order
    populateTable('bids', sortedBids, true);  // Populate 'bids' table with bids
    populateTable('asks', sortedAsks, false);  // Populate 'asks' table with asks
});
