import random
import time
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class WebEntity:
    x: float
    y: float
    entity_type: str
    priority: int
    speed: float = 3.0
    blocked: bool = False
    last_update: float = 0.0
    start_x: float = 0.0
    start_y: float = 0.0
    
    def __post_init__(self):
        self.start_x = self.x
        self.start_y = self.y
        self.color = (0, 255, 0) if self.entity_type == 'player' else (255, 0, 0)

class WebProcess:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.entity = None
        self.task_type = 'movement'

class WebScheduler:
    def __init__(self):
        self.schedulers = [
            {'name': 'First Come First Serve', 'type': 'fcfs'},
            {'name': 'Round Robin', 'type': 'rr'},
            {'name': 'Shortest Job First', 'type': 'sjf'},
            {'name': 'Priority (Non-Preemptive)', 'type': 'priority'},
            {'name': 'Priority (Preemptive)', 'type': 'priority_p'}
        ]
        self.current_index = 0
        self.scheduler = self.schedulers[0]
        self.ready_queue = []
        self.running_process = None
        self.completed_processes = []
        self.current_time = 0
        self.time_quantum = 2.0
        self.current_quantum_time = 0
        self.context_switches = 0
        self.algorithm_metrics = {
            'First Come First Serve': {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []},
            'Round Robin': {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []},
            'Shortest Job First': {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []},
            'Priority (Non-Preemptive)': {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []},
            'Priority (Preemptive)': {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []}
        }
    
    def can_entity_execute(self, entity):
        if self.running_process and self.running_process.entity == entity:
            return True
        return False
    
    def switch_scheduler(self):
        self.current_index = (self.current_index + 1) % len(self.schedulers)
        self.scheduler = self.schedulers[self.current_index]
        self.reset()
    
    def select_algorithm(self, index):
        if 0 <= index < len(self.schedulers):
            self.current_index = index
            self.scheduler = self.schedulers[index]
            self.reset()
    
    def reset(self):
        self.ready_queue = []
        self.running_process = None
        self.completed_processes = []
        self.current_time = 0
        self.current_quantum_time = 0
        self.context_switches = 0
        for algo in self.algorithm_metrics:
            self.algorithm_metrics[algo] = {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []}
    
    def add_process(self, entity, task_type, burst_time):
        pid = len(self.ready_queue) + len(self.completed_processes) + 1
        process = WebProcess(pid, self.current_time, burst_time, entity.priority)
        process.entity = entity
        process.task_type = task_type
        self.ready_queue.append(process)
        return process
    
    def update(self, dt):
        self.current_time += dt
        
        if not self.running_process and self.ready_queue:
            old_process = self.running_process
            
            if self.scheduler['type'] in ['priority', 'priority_p']:
                next_process = min(self.ready_queue, key=lambda p: p.priority)
                self.ready_queue.remove(next_process)
                self.running_process = next_process
            elif self.scheduler['type'] == 'sjf':
                next_process = min(self.ready_queue, key=lambda p: p.remaining_time)
                self.ready_queue.remove(next_process)
                self.running_process = next_process
            else:
                self.running_process = self.ready_queue.pop(0)
            
            self.current_quantum_time = 0
            if old_process != self.running_process:
                self.context_switches += 1
            
        if self.running_process:
            self.running_process.remaining_time -= dt
            self.current_quantum_time += dt
            
            if self.running_process.remaining_time <= 0:
                algo_name = self.scheduler['name']
                completion_time = self.current_time
                turnaround_time = completion_time - self.running_process.arrival_time
                waiting_time = turnaround_time - self.running_process.burst_time
                
                self.running_process.completion_time = completion_time
                self.running_process.turnaround_time = turnaround_time
                self.running_process.waiting_time = max(0, waiting_time)
                
                if algo_name in self.algorithm_metrics:
                    self.algorithm_metrics[algo_name]['total_time'] += completion_time
                    self.algorithm_metrics[algo_name]['process_count'] += 1
                    self.algorithm_metrics[algo_name]['waiting_times'].append(max(0, waiting_time))
                    self.algorithm_metrics[algo_name]['turnaround_times'].append(turnaround_time)
                
                self.completed_processes.append(self.running_process)
                self.running_process = None
                self.current_quantum_time = 0
                
            elif self.scheduler['type'] == 'rr' and self.current_quantum_time >= self.time_quantum:
                if self.running_process.remaining_time > 0:
                    self.ready_queue.append(self.running_process)
                self.running_process = None
                self.current_quantum_time = 0
                
            elif self.scheduler['type'] == 'priority_p':
                if self.ready_queue:
                    highest_priority = min(p.priority for p in self.ready_queue)
                    if highest_priority < self.running_process.priority:
                        self.ready_queue.insert(0, self.running_process)
                        self.running_process = None
                        self.current_quantum_time = 0

class WebLineCrossingGame:
    def __init__(self):
        self.scheduler = WebScheduler()
        self.finish_line_x = 700
        self.start_line_x = 100
        self.game_width = 800
        self.game_height = 400
        self.process_speed = 1.0
        
        self.player = WebEntity(self.start_line_x, 200, 'player', priority=1)
        
        self.enemies = []
        for i in range(6):
            enemy = WebEntity(
                150 + i * 100,
                50,
                'enemy',
                priority=3
            )
            enemy.direction = 1  # 1 for down, -1 for up
            enemy.speed = random.uniform(2, 4)
            self.enemies.append(enemy)
        
        self.powerups = []
        for i in range(3):
            powerup = WebEntity(
                random.randint(200, 600),
                random.randint(100, 300),
                'powerup',
                priority=0
            )
            self.powerups.append(powerup)
        
        self.keys = []
        for i in range(3):
            key = WebEntity(
                random.randint(200, 600),
                random.randint(100, 300),
                'key',
                priority=0
            )
            self.keys.append(key)
        
        # Create 3 locks at finish line
        self.locks = []
        for i in range(3):
            lock = WebEntity(
                self.finish_line_x - 30,
                120 + i * 80,
                'lock',
                priority=0
            )
            lock.lock_id = i
            lock.unlocked = False
            self.locks.append(lock)
        
        # Assign IDs to keys
        for i, key in enumerate(self.keys):
            key.key_id = i
        
        self.entities = [self.player] + self.enemies + self.powerups + self.keys + self.locks
        self.game_won = False
        self.game_time = 0
        self.attempts = 0
        self.lives = 3
        self.game_over = False
        self.player_has_powerup = False
        self.powerup_time = 0
        self.keys_collected = 0
        self.total_keys = 3
        self.show_game_over = False
        self.game_over_timer = 0
        self.locks_unlocked = [False, False, False]
        
    def set_process_speed(self, speed):
        self.process_speed = speed
    
    def reset_positions(self):
        self.player.x = self.start_line_x
        self.player.y = 200
        
        for i, enemy in enumerate(self.enemies):
            enemy.x = 150 + i * 100
            enemy.y = 50
            enemy.direction = 1
    
    def reset_game(self):
        self.game_won = False
        self.game_over = False
        self.game_time = 0
        self.lives = 3
        self.player_has_powerup = False
        self.powerup_time = 0
        self.player.priority = 1
        
        self.reset_positions()
        
        # Respawn powerups
        self.powerups = []
        for i in range(3):
            powerup = WebEntity(
                random.randint(200, 600),
                random.randint(100, 300),
                'powerup',
                priority=0
            )
            self.powerups.append(powerup)
        
        # Respawn keys
        self.keys = []
        for i in range(3):
            key = WebEntity(
                random.randint(200, 600),
                random.randint(100, 300),
                'key',
                priority=0
            )
            key.key_id = i
            self.keys.append(key)
        
        # Reset locks
        for lock in self.locks:
            lock.unlocked = False
        
        self.keys_collected = 0
        self.locks_unlocked = [False, False, False]
        self.entities = [self.player] + self.enemies + self.powerups + self.keys + self.locks
        self.scheduler.reset()
    
    def move_player(self, dx, dy):
        player_has_process = any(p.entity == self.player for p in self.scheduler.ready_queue) or \
                           (self.scheduler.running_process and self.scheduler.running_process.entity == self.player)
        
        if not player_has_process:
            burst_time = random.uniform(0.5, 1.5)
            self.scheduler.add_process(self.player, 'input', burst_time)
        
        # Always move player when input is received, regardless of scheduler
        self.player.x += dx * self.player.speed * 5
        self.player.y += dy * self.player.speed * 5
        self.player.x = max(50, min(750, self.player.x))
        self.player.y = max(50, min(350, self.player.y))
    
    def update(self, dt):
        if self.game_won:
            return
            
        self.game_time += dt
        self.scheduler.update(dt)
        current_time = time.time()
        
        for enemy in self.enemies:
            enemy_has_process = any(p.entity == enemy for p in self.scheduler.ready_queue) or \
                              (self.scheduler.running_process and self.scheduler.running_process.entity == enemy)
            
            if not enemy_has_process and random.random() < 0.3 * self.process_speed:
                burst_time = random.uniform(1.5, 3.0)
                self.scheduler.add_process(enemy, 'ai', burst_time)
            
            # Move enemy vertically only
            if self.scheduler.can_entity_execute(enemy):
                enemy.y += enemy.direction * enemy.speed * dt * 30
                
                # Bounce at top and bottom
                if enemy.y <= 50:
                    enemy.y = 50
                    enemy.direction = 1
                elif enemy.y >= 350:
                    enemy.y = 350
                    enemy.direction = -1
        
        for entity in self.entities:
            can_execute = self.scheduler.can_entity_execute(entity)
            entity.blocked = not can_execute
            
            if can_execute:
                entity.last_update = current_time
        
        # Handle game over timer
        if self.show_game_over:
            self.game_over_timer -= dt
            if self.game_over_timer <= 0:
                self.show_game_over = False
                self.lives = 3
                self.reset_game()
            return
        
        # Check collision with enemies
        for enemy in self.enemies:
            if abs(self.player.x - enemy.x) < 30 and abs(self.player.y - enemy.y) < 30:
                self.lives -= 1
                if self.lives <= 0:
                    self.show_game_over = True
                    self.game_over_timer = 3.0  # Show message for 3 seconds
                    self.attempts += 1
                else:
                    self.reset_positions()
                return
        
        # Check collision with powerups
        for powerup in self.powerups[:]:
            if abs(self.player.x - powerup.x) < 25 and abs(self.player.y - powerup.y) < 25:
                self.player_has_powerup = True
                self.powerup_time = 5.0  # 5 seconds
                self.player.priority = 0  # Highest priority
                self.powerups.remove(powerup)
        
        # Check collision with keys
        for key in self.keys[:]:
            if abs(self.player.x - key.x) < 25 and abs(self.player.y - key.y) < 25:
                self.keys_collected += 1
                self.keys.remove(key)
        
        # Check collision with locks to unlock them
        for lock in self.locks:
            if abs(self.player.x - lock.x) < 30 and abs(self.player.y - lock.y) < 30:
                if not lock.unlocked and self.keys_collected > lock.lock_id:
                    lock.unlocked = True
                    self.locks_unlocked[lock.lock_id] = True
        
        # Handle powerup timer
        if self.player_has_powerup:
            self.powerup_time -= dt
            if self.powerup_time <= 0:
                self.player_has_powerup = False
                self.player.priority = 1  # Back to normal
        
        if self.player.x >= self.finish_line_x:
            if all(self.locks_unlocked):
                self.game_won = True
            else:
                # Push player back if not all locks unlocked
                self.player.x = self.finish_line_x - 10
    
    def _get_process_queue_display(self):
        processes = []
        
        if self.scheduler.running_process:
            p = self.scheduler.running_process
            processes.append({
                'pid': p.pid,
                'priority': p.priority,
                'remaining_time': p.remaining_time,
                'burst_time': p.burst_time,
                'entity_type': p.entity.entity_type if p.entity else 'system',
                'task_type': p.task_type,
                'status': 'RUNNING'
            })
        
        for p in self.scheduler.ready_queue:
            processes.append({
                'pid': p.pid,
                'priority': p.priority,
                'remaining_time': p.remaining_time,
                'burst_time': p.burst_time,
                'entity_type': p.entity.entity_type if p.entity else 'system',
                'task_type': p.task_type,
                'status': 'WAITING'
            })
            
        return processes
    

    

    
    def get_state(self):
        return {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'blocked': self.player.blocked,
                'color': self.player.color,
                'has_powerup': self.player_has_powerup
            },
            'enemies': [{
                'x': enemy.x,
                'y': enemy.y,
                'blocked': enemy.blocked,
                'color': enemy.color
            } for enemy in self.enemies],
            'powerups': [{
                'x': powerup.x,
                'y': powerup.y,
                'color': (255, 255, 0)
            } for powerup in self.powerups],
            'keys': [{
                'x': key.x,
                'y': key.y,
                'color': (0, 255, 255),
                'key_id': key.key_id
            } for key in self.keys],
            'locks': [{
                'x': lock.x,
                'y': lock.y,
                'lock_id': lock.lock_id,
                'unlocked': lock.unlocked
            } for lock in self.locks],
            'scheduler': {
                'name': self.scheduler.scheduler['name'],
                'active_processes': len(self.scheduler.ready_queue) + (1 if self.scheduler.running_process else 0),
                'completed_processes': len(self.scheduler.completed_processes),
                'context_switches': getattr(self.scheduler, 'context_switches', 0),
                'metrics': self.scheduler.algorithm_metrics
            },
            'game': {
                'time': self.game_time,
                'attempts': self.attempts,
                'won': self.game_won,
                'lives': self.lives,
                'game_over': self.game_over,
                'powerup_time': self.powerup_time,
                'finish_line_x': self.finish_line_x,
                'start_line_x': self.start_line_x,
                'keys_collected': self.keys_collected,
                'total_keys': self.total_keys,
                'show_game_over': self.show_game_over,
                'game_over_timer': self.game_over_timer
            },
            'processes': self._get_process_queue_display(),
            'performance_data': self._get_performance_data(),
            'process_table': self._get_process_table_data()
        }
    def _get_performance_data(self):
        performance = {}
        
        for algo_name, metrics in self.scheduler.algorithm_metrics.items():
            if metrics['process_count'] > 0:
                avg_waiting_time = sum(metrics['waiting_times']) / len(metrics['waiting_times'])
                avg_turnaround = sum(metrics['turnaround_times']) / len(metrics['turnaround_times'])
                avg_completion_time = metrics['total_time'] / metrics['process_count']
                throughput = metrics['process_count'] / max(1, self.game_time)
                
                performance[algo_name] = {
                    'avg_waiting_time': avg_waiting_time * 1000,
                    'avg_turnaround_time': avg_turnaround,
                    'avg_completion_time': avg_completion_time,
                    'throughput': throughput,
                    'process_count': metrics['process_count']
                }
            else:
                performance[algo_name] = {
                    'avg_waiting_time': 0,
                    'avg_turnaround_time': 0,
                    'avg_completion_time': 0,
                    'throughput': 0,
                    'process_count': 0
                }
        
        return performance
    
    def _get_process_table_data(self):
        table_data = []
        
        for p in self.scheduler.completed_processes[-10:]:
            table_data.append({
                'pid': p.pid,
                'entity_type': p.entity.entity_type if p.entity else 'system',
                'task_type': p.task_type,
                'priority': p.priority,
                'arrival_time': round(p.arrival_time, 2),
                'burst_time': round(p.burst_time, 2),
                'completion_time': round(getattr(p, 'completion_time', 0), 2),
                'turnaround_time': round(getattr(p, 'turnaround_time', 0), 2),
                'waiting_time': round(getattr(p, 'waiting_time', 0), 2)
            })
        
        return table_data