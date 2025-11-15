const socket = io();
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let gameState = null;

// Algorithm effects mapping
const algorithmEffects = {
    "First Come First Serve": [
        "• Player may lag behind enemies",
        "• Convoy effect visible", 
        "• Unpredictable response",
        "• Poor for interactive systems"
    ],
    "Round Robin": [
        "• Fair time sharing",
        "• Consistent delays",
        "• Moderate responsiveness",
        "• Good for multi-user systems"
    ],
    "Shortest Job First": [
        "• Shortest tasks execute first",
        "• Minimizes average waiting time",
        "• Quick movements get priority",
        "• Longer tasks may starve"
    ],
    "Priority (Non-Preemptive)": [
        "• Player gets priority",
        "• Enemies may starve",
        "• Better player control",
        "• Can't interrupt running processes"
    ],
    "Priority (Preemptive)": [
        "• Best player response",
        "• Real-time performance", 
        "• Optimal for gaming",
        "• Can interrupt low priority processes"
    ]
};

// Socket event handlers
socket.on('game_update', (data) => {
    console.log('Received game update:', data);
    gameState = data;
    updateUI();
    drawGame();
    updateOSStatus();
});

socket.on('connect', () => {
    console.log('Connected to server');
});

// Button event handlers
document.getElementById('startBtn').onclick = () => socket.emit('start_game');
document.getElementById('pauseBtn').onclick = () => socket.emit('pause_game');
document.getElementById('resetBtn').onclick = () => socket.emit('reset_game');

// Algorithm dropdown handler
document.getElementById('algorithmSelect').onchange = (e) => {
    socket.emit('select_algorithm', {index: parseInt(e.target.value)});
};

// Keyboard controls
document.addEventListener('keydown', (e) => {
    let dx = 0, dy = 0;
    switch(e.key.toLowerCase()) {
        case 'w': case 'arrowup': dy = -1; break;
        case 's': case 'arrowdown': dy = 1; break;
        case 'a': case 'arrowleft': dx = -1; break;
        case 'd': case 'arrowright': dx = 1; break;
        case ' ': socket.emit('pause_game'); e.preventDefault(); break;
        case 'r': socket.emit('reset_game'); break;
    }
    if (dx !== 0 || dy !== 0) {
        socket.emit('player_move', {dx, dy});
    }
});

function updateUI() {
    if (!gameState) return;
    
    // Update algorithm dropdown
    const algorithmNames = [
        'First Come First Serve',
        'Round Robin',
        'Shortest Job First',
        'Priority (Non-Preemptive)',
        'Priority (Preemptive)'
    ];
    const currentIndex = algorithmNames.indexOf(gameState.scheduler.name);
    if (currentIndex >= 0) {
        document.getElementById('algorithmSelect').value = currentIndex;
    }
    
    // Update algorithm effects
    const effects = algorithmEffects[gameState.scheduler.name] || [];
    document.getElementById('algorithmEffects').innerHTML = effects.join('<br>');
    
    // Update metrics
    document.getElementById('gameTime').textContent = gameState.game.time.toFixed(1) + 's';
    document.getElementById('attempts').textContent = gameState.game.attempts;
    document.getElementById('activeProcesses').textContent = gameState.scheduler.active_processes;
    document.getElementById('completedProcesses').textContent = gameState.scheduler.completed_processes;
    document.getElementById('contextSwitches').textContent = gameState.scheduler.context_switches || 0;
    
    // Update process queue
    updateProcessQueue();
    
    // Update current algorithm stats
    updateCurrentStats();
    
    // Update process table
    updateProcessTable();
}

function updateProcessQueue() {
    const queueDiv = document.getElementById('processQueue');
    queueDiv.innerHTML = '';
    
    if (!gameState.processes || gameState.processes.length === 0) {
        queueDiv.innerHTML = `
            <div class="text-center text-gray-400 py-4">
                <div>No processes in queue</div>
                <div class="text-xs">Processes will appear when game starts</div>
            </div>
        `;
        return;
    }
    
    gameState.processes.slice(0, 8).forEach((process, index) => {
        const processDiv = document.createElement('div');
        processDiv.className = 'bg-gray-700 p-3 rounded border-l-4';
        
        const entityType = process.entity_type === 'player' ? 'Player' : 'Enemy';
        const color = process.entity_type === 'player' ? 'text-green-400' : 'text-red-400';
        const borderColor = process.entity_type === 'player' ? 'border-green-500' : 'border-red-500';
        
        processDiv.className += ` ${borderColor}`;
        
        const progress = ((process.burst_time - process.remaining_time) / process.burst_time * 100);
        const status = process.status || (index === 0 ? 'RUNNING' : 'WAITING');
        const statusColor = status === 'RUNNING' ? 'text-yellow-400' : 'text-gray-400';
        
        processDiv.innerHTML = `
            <div class="flex justify-between items-center mb-2">
                <span class="${color} font-semibold">${entityType} Process</span>
                <span class="${statusColor} text-xs font-bold">${status}</span>
            </div>
            <div class="flex justify-between items-center mb-2">
                <span class="text-xs text-gray-300">PID: ${process.pid}</span>
                <span class="text-xs text-gray-300">Priority: ${process.priority}</span>
                <span class="text-xs text-gray-300">${process.remaining_time.toFixed(1)}s left</span>
            </div>
            <div class="w-full bg-gray-600 rounded-full h-2">
                <div class="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300" 
                     style="width: ${progress}%"></div>
            </div>
        `;
        queueDiv.appendChild(processDiv);
    });
}

function updateOSStatus() {
    if (!gameState) return;
    
    const currentActionEl = document.getElementById('currentAction');
    const schedulerMessageEl = document.getElementById('schedulerMessage');
    
    const algorithm = gameState.scheduler.name;
    const activeProcesses = gameState.scheduler.active_processes;
    const runningProcess = gameState.processes && gameState.processes.find(p => p.status === 'RUNNING');
    
    // Update current action
    if (runningProcess) {
        const processType = runningProcess.task_type === 'input' ? 'User Input Process' : 'Background AI Process';
        currentActionEl.textContent = `Executing ${processType} (PID: ${runningProcess.pid})`;
    } else if (activeProcesses > 0) {
        currentActionEl.textContent = 'CPU Idle - Selecting next process...';
    } else {
        currentActionEl.textContent = 'No processes in ready queue';
    }
    
    // Update scheduler message based on algorithm
    let message = '';
    switch (algorithm) {
        case 'First Come First Serve':
            if (runningProcess) {
                if (runningProcess.entity_type === 'player') {
                    message = '🟢 FCFS: Player process finally got CPU after waiting for all enemy processes!';
                } else {
                    message = `🔴 FCFS BLOCKING: Enemy process running for ${runningProcess.remaining_time.toFixed(1)}s more. Player is COMPLETELY BLOCKED!`;
                }
            } else {
                message = 'FCFS: Strict arrival order. If enemies arrive first, player must wait for ALL of them to complete!';
            }
            break;
            
        case 'Round Robin':
            if (runningProcess) {
                message = `🔄 Round Robin: Current process gets fair time slice. All processes get equal CPU time.`;
            } else {
                message = 'Round Robin: Each process gets equal time slices. Provides fair scheduling for all processes.';
            }
            break;
            
        case 'Shortest Job First':
            if (runningProcess) {
                message = `🔵 SJF: Shortest remaining time process is running. Optimal average waiting time.`;
            } else {
                message = 'SJF: Shortest Job First minimizes average waiting time but may cause starvation.';
            }
            break;
            
        case 'Priority (Non-Preemptive)':
            if (runningProcess) {
                if (runningProcess.entity_type === 'player') {
                    message = '🔵 Priority: Player process (Priority 1) is running. Much better responsiveness than FCFS!';
                } else {
                    message = '🔵 Priority: Enemy process running because no player processes are waiting. Player gets priority when needed.';
                }
            } else {
                message = 'Priority: Higher priority processes execute first. Player=Priority 1, Enemies=Priority 3.';
            }
            break;
            
        case 'Priority (Preemptive)':
            if (runningProcess) {
                if (runningProcess.entity_type === 'player') {
                    message = '⚡ Preemptive Priority: Player process running with highest priority. Can interrupt any lower priority process!';
                } else {
                    message = '⚡ Preemptive Priority: Enemy process running, but will be immediately interrupted if player process arrives.';
                }
            } else {
                message = 'Preemptive Priority: Best for real-time systems. High priority processes can interrupt low priority ones.';
            }
            break;
    }
    
    schedulerMessageEl.textContent = message;
}

function drawGame() {
    if (!gameState) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#6B7280';
        ctx.font = '20px Arial';
        ctx.fillText('Connecting...', 320, 200);
        return;
    }
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw start line
    ctx.strokeStyle = '#10B981';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(gameState.game.start_line_x, 50);
    ctx.lineTo(gameState.game.start_line_x, 350);
    ctx.stroke();
    
    ctx.fillStyle = '#10B981';
    ctx.font = '14px Arial';
    ctx.fillText('START', gameState.game.start_line_x - 15, 370);
    
    // Draw finish line
    const allLocksUnlocked = gameState.locks && gameState.locks.length === 0;
    ctx.strokeStyle = allLocksUnlocked ? '#10B981' : '#6B7280';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(gameState.game.finish_line_x, 50);
    ctx.lineTo(gameState.game.finish_line_x, 350);
    ctx.stroke();
    
    ctx.fillStyle = allLocksUnlocked ? '#10B981' : '#6B7280';
    ctx.font = '14px Arial';
    ctx.fillText(allLocksUnlocked ? 'FINISH' : 'UNLOCK ALL LOCKS', gameState.game.finish_line_x - 35, 370);
    
    // Draw level and CPU scheduler indicator
    ctx.fillStyle = '#8B5CF6';
    ctx.font = '12px Arial';
    ctx.fillText(`LEVEL ${gameState.game.level}/${gameState.game.max_level} - CPU SCHEDULER: ${gameState.scheduler.name}`, 10, 25);
    
    // Draw boss info if boss level
    if (gameState.game.boss_level && gameState.game.boss_required_algorithm) {
        ctx.fillStyle = '#FF4444';
        ctx.font = '14px Arial';
        ctx.fillText(`BOSS LEVEL! Use ${gameState.game.boss_required_algorithm} to defeat boss`, 10, 45);
    }
    
    // Draw player
    drawEntity(gameState.player, '#10B981', 'USER');
    
    // Draw enemies
    gameState.enemies.forEach((enemy, index) => {
        if (enemy.is_boss) {
            drawBossEntity(enemy);
        } else {
            drawEntity(enemy, '#EF4444', `BG${index + 1}`);
        }
    });
    
    // Draw powerups
    if (gameState.powerups) {
        gameState.powerups.forEach((powerup, index) => {
            ctx.fillStyle = '#FFD700';
            ctx.beginPath();
            ctx.arc(powerup.x, powerup.y, 18, 0, 2 * Math.PI);
            ctx.fill();
            
            const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#8A2BE2'];
            ctx.fillStyle = colors[index % colors.length];
            ctx.font = '20px Arial';
            ctx.fillText('⚡', powerup.x - 10, powerup.y + 7);
        });
    }
    
    // Draw keys
    if (gameState.keys) {
        gameState.keys.forEach((key, index) => {
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(key.x, key.y, 15, 0, 2 * Math.PI);
            ctx.fill();
            
            const keyColors = ['#FFD700', '#FF69B4', '#00FF7F'];
            ctx.fillStyle = keyColors[index % keyColors.length];
            ctx.font = '18px Arial';
            ctx.fillText('🔑', key.x - 9, key.y + 6);
        });
    }
    
    // Draw locks
    if (gameState.locks) {
        gameState.locks.forEach((lock, index) => {
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(lock.x, lock.y, 20, 0, 2 * Math.PI);
            ctx.fill();
            
            const lockColors = ['#8B4513', '#DC143C', '#4B0082'];
            ctx.fillStyle = lockColors[index % lockColors.length];
            ctx.font = '22px Arial';
            ctx.fillText('🔒', lock.x - 11, lock.y + 8);
        });
    }
    
    // Draw hearts for lives
    ctx.font = '20px Arial';
    for (let i = 0; i < 3; i++) {
        if (i < gameState.game.lives) {
            ctx.fillText('❤️', 10 + i * 30, 50);
        } else {
            ctx.fillText('🖤', 10 + i * 30, 50);
        }
    }
    
    ctx.fillStyle = '#00FFFF';
    ctx.fillText(`Keys: ${gameState.game.keys_collected}/3`, 10, 70);
    
    if (gameState.player.has_powerup) {
        ctx.fillStyle = '#FFD700';
        ctx.fillText(`⚡ POWERUP: ${gameState.game.powerup_time.toFixed(1)}s`, 10, 90);
    }
    
    // Draw win message
    if (gameState.game.won) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#10B981';
        ctx.font = 'bold 36px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('YOU WIN!', canvas.width/2, 180);
        
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '18px Arial';
        ctx.fillText(`Time: ${gameState.game.time.toFixed(1)}s`, canvas.width/2, 220);
        ctx.fillText(`Algorithm: ${gameState.scheduler.name}`, canvas.width/2, 250);
        
        ctx.textAlign = 'left';
    }
    
    // Draw game over message
    if (gameState.game.show_game_over) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#EF4444';
        ctx.font = 'bold 36px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('YOU LOSE!', canvas.width/2, 180);
        
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '18px Arial';
        ctx.fillText('All lives lost. Restarting in...', canvas.width/2, 220);
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 24px Arial';
        ctx.fillText(Math.ceil(gameState.game.game_over_timer), canvas.width/2, 250);
        
        ctx.textAlign = 'left';
    }
}

function drawEntity(entity, color, label) {
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';
    
    if (label === 'USER') {
        ctx.fillText('😊', entity.x, entity.y + 10);
    } else {
        const enemyFaces = ['💀', '💀', '☠️'];
        const faceIndex = parseInt(label.replace('BG', '')) % enemyFaces.length;
        ctx.fillText(enemyFaces[faceIndex], entity.x, entity.y + 10);
    }
    
    // Draw process state indicator
    if (entity.blocked) {
        ctx.strokeStyle = '#FCD34D';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(entity.x, entity.y, 25, 0, 2 * Math.PI);
        ctx.stroke();
        
        ctx.fillStyle = '#FCD34D';
        ctx.font = '10px Arial';
        ctx.fillText('WAITING', entity.x, entity.y - 30);
    } else {
        ctx.strokeStyle = '#10B981';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(entity.x, entity.y, 22, 0, 2 * Math.PI);
        ctx.stroke();
        
        ctx.fillStyle = '#10B981';
        ctx.font = '10px Arial';
        ctx.fillText('RUNNING', entity.x, entity.y - 30);
    }
    
    const priority = entity.entity_type === 'player' ? 'P1' : 'P3';
    ctx.fillStyle = entity.entity_type === 'player' ? '#10B981' : '#EF4444';
    ctx.font = '10px Arial';
    ctx.fillText(priority, entity.x, entity.y + 35);
    
    ctx.textAlign = 'left';
}

function drawBossEntity(enemy) {
    ctx.font = '50px Arial';
    ctx.textAlign = 'center';
    
    // Draw boss with different appearance
    ctx.fillText('👹', enemy.x, enemy.y + 15);
    
    // Draw larger process state indicator for boss
    if (enemy.blocked) {
        ctx.strokeStyle = '#FCD34D';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(enemy.x, enemy.y, 35, 0, 2 * Math.PI);
        ctx.stroke();
        
        ctx.fillStyle = '#FCD34D';
        ctx.font = '12px Arial';
        ctx.fillText('BOSS WAITING', enemy.x, enemy.y - 45);
    } else {
        ctx.strokeStyle = '#FF4444';
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.arc(enemy.x, enemy.y, 32, 0, 2 * Math.PI);
        ctx.stroke();
        
        ctx.fillStyle = '#FF4444';
        ctx.font = '12px Arial';
        ctx.fillText('BOSS ACTIVE', enemy.x, enemy.y - 45);
    }
    
    ctx.fillStyle = '#FF4444';
    ctx.font = '10px Arial';
    ctx.fillText('P2', enemy.x, enemy.y + 45);
    
    ctx.textAlign = 'left';
}



function updateCurrentStats() {
    if (!gameState?.performance_data || !gameState?.scheduler?.name) return;
    
    const currentAlgo = gameState.scheduler.name;
    const stats = gameState.performance_data[currentAlgo];
    
    if (stats) {
        document.getElementById('currentWaitTime').textContent = stats.avg_waiting_time.toFixed(1) + 'ms';
        document.getElementById('currentThroughput').textContent = stats.throughput.toFixed(2) + '/s';
        
        const maxWaitTime = Math.max(...Object.values(gameState.performance_data).map(s => s.avg_waiting_time));
        const efficiency = maxWaitTime > 0 ? ((maxWaitTime - stats.avg_waiting_time) / maxWaitTime * 100) : 100;
        document.getElementById('currentEfficiency').textContent = efficiency.toFixed(1) + '%';
    }
}

function updateProcessTable() {
    if (!gameState?.process_table) return;
    
    const tbody = document.getElementById('processTableBody');
    
    if (gameState.process_table.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="px-4 py-6 text-center text-gray-400">
                    No completed processes yet. Click Start to begin.
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = '';
    
    gameState.process_table.forEach(process => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-700 transition-colors';
        
        const typeColor = process.entity_type === 'player' ? 'text-green-400' : 'text-red-400';
        const taskBadge = process.task_type === 'input' ? 
            '<span class="bg-blue-600 px-2 py-1 rounded text-xs">INPUT</span>' : 
            '<span class="bg-purple-600 px-2 py-1 rounded text-xs">AI</span>';
        
        row.innerHTML = `
            <td class="px-3 py-2 font-mono border-r border-gray-700">${process.pid}</td>
            <td class="px-3 py-2 ${typeColor} font-semibold border-r border-gray-700">${process.entity_type.toUpperCase()}</td>
            <td class="px-3 py-2 border-r border-gray-700">${taskBadge}</td>
            <td class="px-3 py-2 text-center border-r border-gray-700">
                <span class="${process.priority === 1 ? 'text-green-400' : 'text-yellow-400'} font-bold">
                    P${process.priority}
                </span>
            </td>
            <td class="px-3 py-2 text-gray-300 border-r border-gray-700">${process.arrival_time}</td>
            <td class="px-3 py-2 text-blue-400 font-bold border-r border-gray-700">${process.burst_time}</td>
            <td class="px-3 py-2 text-gray-300 border-r border-gray-700">${process.completion_time}</td>
            <td class="px-3 py-2 text-purple-400 font-bold border-r border-gray-700">${process.turnaround_time}</td>
            <td class="px-3 py-2 text-yellow-400 font-bold text-lg">${process.waiting_time}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Initialize game on page load
document.addEventListener('DOMContentLoaded', () => {
    drawGame();
});
