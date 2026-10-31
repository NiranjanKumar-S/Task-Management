/**
 * Chart.js Visualizations for Dashboard
 */

function initDashboardCharts(stats) {
    if (!stats) return;

    // 1. Status Doughnut Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statuses = stats.statuses || {};
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'In Progress', 'Completed'],
                datasets: [{
                    data: [
                        statuses['Pending'] || 0,
                        statuses['In Progress'] || 0,
                        statuses['Completed'] || 0
                    ],
                    backgroundColor: [
                        '#fbbf24', // Amber
                        '#3b82f6', // Blue
                        '#10b981'  // Emerald
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: 'Inter',
                                size: 12
                            },
                            padding: 18,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.raw;
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                return ` ${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '72%'
            }
        });
    }

    // 2. Priority Bar Chart
    const priorityCtx = document.getElementById('priorityChart');
    if (priorityCtx) {
        const priorities = stats.priorities || {};
        new Chart(priorityCtx, {
            type: 'bar',
            data: {
                labels: ['Low', 'Medium', 'High', 'Urgent'],
                datasets: [{
                    label: 'Number of Tasks',
                    data: [
                        priorities['Low'] || 0,
                        priorities['Medium'] || 0,
                        priorities['High'] || 0,
                        priorities['Urgent'] || 0
                    ],
                    backgroundColor: [
                        '#a7f3d0', // Light green
                        '#fde68a', // Light yellow
                        '#fed7aa', // Light orange
                        '#fecaca'  // Light red
                    ],
                    borderColor: [
                        '#059669', // Darker green
                        '#d97706', // Darker amber
                        '#ea580c', // Darker orange
                        '#dc2626'  // Darker red
                    ],
                    borderWidth: 1.5,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            font: {
                                family: 'Inter',
                                size: 11
                            }
                        },
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                family: 'Inter',
                                size: 11
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}
