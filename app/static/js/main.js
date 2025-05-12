/* Main JavaScript file for the Coinbase Automated Trader application */

// Function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Function to refresh data on dashboard
function refreshDashboardData() {
    // Only execute on the dashboard page
    if (!window.location.pathname.includes('/dashboard')) {
        return;
    }
    
    // Fetch latest balance
    fetch('/api/balance')
        .then(response => response.json())
        .then(data => {
            if (data.success && document.getElementById('balance-display')) {
                document.getElementById('balance-display').textContent = 
                    `${data.balance.balance} ${data.balance.currency}`;
            }
        })
        .catch(error => console.error('Error fetching balance:', error));
        
    // Fetch latest transactions
    fetch('/api/transactions')
        .then(response => response.json())
        .then(data => {
            // This would update the transaction table, but requires more DOM manipulation
            // than we're implementing in this simple example
            console.log('Transactions refreshed');
        })
        .catch(error => console.error('Error fetching transactions:', error));
}

// Set up automatic data refresh on dashboard (every 60 seconds)
if (window.location.pathname.includes('/dashboard')) {
    setInterval(refreshDashboardData, 60000);
}
