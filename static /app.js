function fetchOrderBook() {
    return fetch('http://localhost:6006/api/orderbook')
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}

function populateTable(tableId, data, isBid) {
    const table = document.getElementById(tableId).getElementsByTagName('table')[0];
    let cumulativeVolumes = {};

    data.forEach(([price, quantity]) => {
        if (cumulativeVolumes[price]) {
            cumulativeVolumes[price] += quantity;
        } else {
            cumulativeVolumes[price] = quantity;
        }
    
        const row = table.insertRow(-1);
        row.insertCell(0).textContent = price;
        row.insertCell(1).textContent = cumulativeVolumes[price];
        row.style.backgroundColor = isBid ? 'rgb(124, 258, 124)' : 'rgb(255, 162, 163)'; 
    });
}


fetchOrderBook().then(orderBook => {
    // Sort bids in descending order and asks in ascending order
    const sortedBids = orderBook.bids.sort((a, b) => b[0] - a[0]);
    const sortedAsks = orderBook.asks.sort((a, b) => a[0] - b[0]);  
    populateTable('bids', sortedBids, true);
    populateTable('asks', sortedAsks, false);
});