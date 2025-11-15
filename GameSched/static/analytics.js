const socket = io();

let performanceChart, fpsChart, waitingTimeChart, throughputChart;
let metricsData = null;

// Initialize charts
function initCharts() {
    // Performance Comparison Chart
    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(perfCtx, {
        type: 'radar',
        data: {
            labels: ['Waiting Time', 'Turnaround Time', 'Response Time', 'Throughput'],
            datasets: [
                {
                    label: 'FCFS',
                    data: [0, 0, 0, 0],
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)'
                },
                {
                    label: 'Round Robin',
                    data: [0, 0, 0, 0],
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)'
                },
                {
                    label: 'Priority',
                    data: [0, 0, 0, 0],
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)'
                },
                {
                    label: 'Priority (P)',
                    data: [0, 0, 0, 0],
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#E5E7EB' } }
            },
            scales: {
                r: {
                    ticks: { color: '#E5E7EB' },
                    grid: { color: '#374151' }
                }
            }
        }
    });

    // FPS Chart
    const fpsCtx = document.getElementById('fpsChart').getContext('2d');
    fpsChart = new Chart(fpsCtx, {
        type: 'line',
        data: {
            labels: Array.from({length: 60}, (_, i) => i),
            datasets: [{
                label: 'FPS',
                data: Array(60).fill(0),
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#E5E7EB' } }
            },
            scales: {
                y: {
                    ticks: { color: '#E5E7EB' },
                    grid: { color: '#374151' },
                    min: 0,
                    max: 60
                },
                x: {
                    ticks: { color: '#E5E7EB' },
                    grid: { color: '#374151' }
                }
            }
        }
    });

    // Waiting Time Chart
    const waitCtx = document.getElementById('waitingTimeChart').getContext('2d');
    waitingTimeChart = new Chart(waitCtx, {
        type: 'bar',
        data: {
            labels: ['FCFS', 'Round Robin', 'Priority', 'Priority (P)'],
            datasets: [{
                label: 'Average Waiting Time (ms)',
                data: [0, 0, 0, 0],
                backgroundColor: ['#EF4444', '#F59E0B', '#10B981', '#8B5CF6']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#E5E7EB' } }
            },
            scales: {
                y: {
                    ticks: { color: '#E5E7EB' },
                    grid: { color: '#374151' }
                },
                x: {
                    ticks: { color: '#E5E7EB' },
                    grid: { color: '#374151' }
                }
            }
        }
    });

    // Throughput Chart
    const throughputCtx = document.getElementById('throughputChart').getContext('2d');
    throughputChart = new Chart(throughputCtx, {
        type: 'doughnut',
        data: {
            labels: ['FCFS', 'Round Robin', 'Priority', 'Priority (P)'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#EF4444', '#F59E0B', '#10B981', '#8B5CF6']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#E5E7EB' } }
            }
        }
    });
}

// Update charts with new data
function updateCharts(data) {
    if (!data) return;

    const algorithms = ['First Come First Serve', 'Round Robin', 'Priority (Non-Preemptive)', 'Priority (Preemptive)'];
    
    // Update performance radar chart
    algorithms.forEach((algo, index) => {
        const stats = data.comparison[algo] || {};
        performanceChart.data.datasets[index].data = [
            stats.waiting_time || 0,
            stats.turnaround_time || 0,
            stats.response_time || 0,
            stats.throughput || 0
        ];
    });
    performanceChart.update();

    // Update FPS chart
    if (data.fps_history) {
        fpsChart.data.datasets[0].data = data.fps_history;
        fpsChart.update();
    }

    // Update waiting time chart
    waitingTimeChart.data.datasets[0].data = algorithms.map(algo => 
        (data.comparison[algo]?.waiting_time || 0) * 1000
    );
    waitingTimeChart.update();

    // Update throughput chart
    throughputChart.data.datasets[0].data = algorithms.map(algo => 
        data.comparison[algo]?.throughput || 0
    );
    throughputChart.update();
}

// Update key metrics
function updateMetrics(data) {
    if (!data) return;

    document.getElementById('totalProcesses').textContent = data.total_processes || 0;
    document.getElementById('contextSwitches').textContent = data.context_switches || 0;
    document.getElementById('avgFPS').textContent = (data.fps_stats?.average || 0).toFixed(1);
    
    // Find best algorithm (lowest waiting time)
    let bestAlgo = 'None';
    let bestTime = Infinity;
    Object.entries(data.comparison || {}).forEach(([algo, stats]) => {
        if (stats.waiting_time < bestTime && stats.waiting_time > 0) {
            bestTime = stats.waiting_time;
            bestAlgo = algo.split(' ')[0]; // Shorten name
        }
    });
    document.getElementById('bestAlgorithm').textContent = bestAlgo;
}

// Update statistics table
function updateStatsTable(data) {
    const tbody = document.getElementById('statsTable');
    tbody.innerHTML = '';

    const algorithms = ['First Come First Serve', 'Round Robin', 'Priority (Non-Preemptive)', 'Priority (Preemptive)'];
    
    algorithms.forEach(algo => {
        const stats = data.comparison[algo] || {};
        const row = document.createElement('tr');
        row.className = 'border-b border-gray-700';
        
        row.innerHTML = `
            <td class="p-2 font-medium">${algo}</td>
            <td class="p-2">${(stats.waiting_time * 1000 || 0).toFixed(2)}ms</td>
            <td class="p-2">${(stats.turnaround_time * 1000 || 0).toFixed(2)}ms</td>
            <td class="p-2">${(stats.response_time * 1000 || 0).toFixed(2)}ms</td>
            <td class="p-2">${(stats.throughput || 0).toFixed(2)}/s</td>
            <td class="p-2">${data.algorithm_stats?.[algo]?.process_count || 0}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Create Gantt chart
function createGanttChart(data) {
    const container = document.getElementById('ganttChart');
    if (!data.gantt_data || data.gantt_data.length === 0) {
        container.innerHTML = '<div class="min-w-full h-64 bg-gray-700 rounded flex items-center justify-center"><span class="text-gray-400">No process execution data available</span></div>';
        return;
    }

    const ganttData = data.gantt_data;
    const maxTime = Math.max(...ganttData.map(p => p.start + p.duration));
    const scale = 800 / maxTime; // Scale to fit 800px width

    let html = '<div class="relative h-64 bg-gray-700 rounded" style="width: 800px;">';
    
    ganttData.forEach((process, index) => {
        const left = process.start * scale;
        const width = process.duration * scale;
        const top = (index % 10) * 24 + 10; // Stack processes
        const color = process.entity_type === 'player' ? '#10B981' : '#EF4444';
        
        html += `
            <div class="absolute rounded text-xs text-white px-2 py-1" 
                 style="left: ${left}px; top: ${top}px; width: ${width}px; background-color: ${color};">
                P${process.pid} (${process.algorithm.split(' ')[0]})
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Socket event handlers
socket.on('metrics_update', (data) => {
    metricsData = data;
    updateCharts(data);
    updateMetrics(data);
    updateStatsTable(data);
    createGanttChart(data);
});

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    socket.emit('request_metrics');
});

// Request metrics every 2 seconds
setInterval(() => {
    socket.emit('request_metrics');
}, 2000);