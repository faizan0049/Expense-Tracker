/**
 * charts.js
 * Contains helper functions for creating and updating charts throughout the application
 */

// Function to create a doughnut chart
function createDoughnutChart(ctx, labels, data, colors, title) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                }
            },
            cutout: '70%'
        }
    });
}

// Function to create a bar chart
function createBarChart(ctx, labels, datasets, title) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Function to create a line chart
function createLineChart(ctx, labels, datasets, title) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.4
                }
            }
        }
    });
}

// Function to fetch chart data from API
function fetchChartData(type, month, year) {
    return fetch(`/api/chart-data?type=${type}&month=${month}&year=${year}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            return [];
        });
}

// Function to update a chart with new data
function updateChart(chart, labels, data, colors) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    if (colors) {
        chart.data.datasets[0].backgroundColor = colors;
    }
    chart.update();
}

// Function to format currency
function formatCurrency(value) {
    return 'Rs. ' + new Intl.NumberFormat('en-IN', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Create a progress bar
function createProgressBar(container, value, maxValue, color) {
    const percentage = Math.min(Math.round((value / maxValue) * 100), 100);
    const progressBar = document.createElement('div');
    progressBar.className = 'progress';
    progressBar.style.height = '10px';
    
    const progressInner = document.createElement('div');
    progressInner.className = 'progress-bar';
    progressInner.style.width = `${percentage}%`;
    progressInner.style.backgroundColor = color || getProgressBarColor(percentage);
    progressInner.setAttribute('role', 'progressbar');
    progressInner.setAttribute('aria-valuenow', percentage);
    progressInner.setAttribute('aria-valuemin', 0);
    progressInner.setAttribute('aria-valuemax', 100);
    
    progressBar.appendChild(progressInner);
    container.appendChild(progressBar);
    
    return {
        update: function(newValue) {
            const newPercentage = Math.min(Math.round((newValue / maxValue) * 100), 100);
            progressInner.style.width = `${newPercentage}%`;
            progressInner.setAttribute('aria-valuenow', newPercentage);
        }
    };
}

// Get color for progress bar based on percentage
function getProgressBarColor(percentage) {
    if (percentage >= 90) {
        return '#dc3545'; // danger
    } else if (percentage >= 75) {
        return '#ffc107'; // warning
    } else {
        return '#198754'; // success
    }
}
