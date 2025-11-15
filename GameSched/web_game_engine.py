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
        # Start with FCFS
        self.scheduler = {'name': 'First Come First Serve', 'type': 'fcfs'}
        self.current_algorithm_name = 'First Come First Serve'
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
    
    def apply_powerup_algorithm(self, algorithm_name):
        """Apply new scheduling algorithm from power-up"""
        algo_map = {
            'SJF': {'name': 'Shortest Job First', 'type': 'sjf'},
            'SRTF': {'name': 'Shortest Remaining Time First', 'type': 'sjf'},
            'Round Robin': {'name': 'Round Robin', 'type': 'rr'},
            'Priority (Non-Preemptive)': {'name': 'Priority (Non-Preemptive)', 'type': 'priority'},
            'Priority (Preemptive)': {'name': 'Priority (Preemptive)', 'type': 'priority_p'}
        }
        
        if algorithm_name in algo_map:
            self.scheduler = algo_map[algorithm_name]
            self.current_algorithm_name = self.scheduler['name']
            self.ready_queue = []
            self.running_process = None
    
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
        
        self.level = 1
        self.max_level = 5
        self.boss_level = False
        self.boss_enemy = None
        self.boss_required_algorithm = None
        
        self.player = WebEntity(self.start_line_x, 200, 'player', priority=1)
        
        self.enemies = []
        self.create_level_enemies()
        
        # Create 5 power-ups with random algorithm assignment (excluding FCFS as it's the starting algorithm)
        self.powerups = []
        algorithms = ['SJF', 'SRTF', 'Round Robin', 'Priority (Non-Preemptive)', 'Priority (Preemptive)']
        random.shuffle(algorithms)
        
        for i in range(5):
            powerup = WebEntity(
                random.randint(150 + i * 80, 200 + i * 80),
                random.randint(80 + (i % 2) * 150, 120 + (i % 2) * 150),
                'powerup',
                priority=0
            )
            powerup.algorithm = algorithms[i]
            self.powerups.append(powerup)
        
        # Create 3 keys to collect
        self.keys = []
        key_positions = [(250, 150), (450, 250), (550, 120)]
        for i in range(3):
            key = WebEntity(
                key_positions[i][0] + random.randint(-30, 30),
                key_positions[i][1] + random.randint(-30, 30),
                'key',
                priority=0
            )
            self.keys.append(key)
        
        # Create 3 locks at the finish line
        self.locks = []
        for i in range(3):
            lock = WebEntity(
                self.finish_line_x - 20,
                120 + i * 60,
                'lock',
                priority=0
            )
            self.locks.append(lock)
        
        self.powerups_collected = 0
        self.keys_collected = 0
        self.current_powerup_popup = None
        self.popup_timer = 0
        
        self.entities = [self.player] + self.enemies + self.powerups + self.keys + self.locks
        self.game_won = False
        self.game_time = 0
        self.attempts = 0
        self.lives = max(1, 4 - self.level)
        self.game_over = False
        self.show_game_over = False
        self.game_over_timer = 0
        
    def create_level_enemies(self):
        enemy_speed_multiplier = 1 + (self.level - 1) * 0.3
        
        # Check if this is a boss level (every 3rd level)
        self.boss_level = (self.level % 3 == 0)
        
        if self.boss_level:
            # Create boss enemy
            self.boss_enemy = WebEntity(400, 200, 'boss', priority=2)
            self.boss_enemy.direction = 1
            self.boss_enemy.speed = 1.5 * enemy_speed_multiplier
            self.boss_enemy.size = 40
            
            boss_algorithms = ['Round Robin', 'Priority (Preemptive)', 'Shortest Job First']
            self.boss_required_algorithm = boss_algorithms[(self.level // 3 - 1) % len(boss_algorithms)]
            
            self.enemies = [self.boss_enemy]
            # Add 4 regular enemies on boss levels
            for i in range(4):
                x_pos = 200 + i * 100
                y_pos = 80 if i % 2 == 0 else 320
                enemy = WebEntity(x_pos, y_pos, 'enemy', priority=3)
                enemy.direction = 1 if i % 2 == 0 else -1
                enemy.speed = random.uniform(2, 3) * enemy_speed_multiplier
                self.enemies.append(enemy)
        else:
            # Regular level - exactly 7 enemies
            for i in range(7):
                x_pos = 150 + i * 70  # Spread between start (100) and finish (700)
                y_pos = 80 if i % 2 == 0 else 320  # Alternate top and bottom
                enemy = WebEntity(x_pos, y_pos, 'enemy', priority=3)
                enemy.direction = 1 if i % 2 == 0 else -1  # Top enemies go down, bottom go up
                enemy.speed = random.uniform(2, 4) * enemy_speed_multiplier
                self.enemies.append(enemy)
    
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
        self.lives = max(1, 4 - self.level)
        
        self.reset_positions()
        
        # Respawn powerups with new random algorithms
        self.powerups = []
        algorithms = ['SJF', 'SRTF', 'Round Robin', 'Priority (Non-Preemptive)', 'Priority (Preemptive)']
        random.shuffle(algorithms)
        
        for i in range(5):
            powerup = WebEntity(
                random.randint(150 + i * 80, 200 + i * 80),
                random.randint(80 + (i % 2) * 150, 120 + (i % 2) * 150),
                'powerup',
                priority=0
            )
            powerup.algorithm = algorithms[i]
            self.powerups.append(powerup)
        
        # Respawn keys
        self.keys = []
        key_positions = [(250, 150), (450, 250), (550, 120)]
        for i in range(3):
            key = WebEntity(
                key_positions[i][0] + random.randint(-30, 30),
                key_positions[i][1] + random.randint(-30, 30),
                'key',
                priority=0
            )
            self.keys.append(key)
        
        # Respawn locks at finish line
        self.locks = []
        for i in range(3):
            lock = WebEntity(
                self.finish_line_x - 20,
                120 + i * 60,
                'lock',
                priority=0
            )
            self.locks.append(lock)
        
        self.powerups_collected = 0
        self.keys_collected = 0
        self.current_powerup_popup = None
        self.popup_timer = 0
        self.scheduler = WebScheduler()
        
        self.create_level_enemies()
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
                    self.game_over_timer = 3.0
                    self.attempts += 1
                else:
                    self.reset_positions()
                return
        
        # Check collision with keys
        for key in self.keys[:]:
            if abs(self.player.x - key.x) < 25 and abs(self.player.y - key.y) < 25:
                self.keys_collected += 1
                self.keys.remove(key)
                self.entities.remove(key)
        
        # Check collision with locks (only if player has keys)
        if self.keys_collected > 0:
            for lock in self.locks[:]:
                if abs(self.player.x - lock.x) < 25 and abs(self.player.y - lock.y) < 25:
                    self.keys_collected -= 1
                    self.locks.remove(lock)
                    self.entities.remove(lock)
                    break
        
        # Check collision with powerups
        for powerup in self.powerups[:]:
            if abs(self.player.x - powerup.x) < 25 and abs(self.player.y - powerup.y) < 25:
                self.powerups_collected += 1
                self.scheduler.apply_powerup_algorithm(powerup.algorithm)
                self.current_powerup_popup = powerup.algorithm
                self.popup_timer = 3.0
                self.powerups.remove(powerup)
        
        # Handle popup timer
        if self.popup_timer > 0:
            self.popup_timer -= dt
            if self.popup_timer <= 0:
                self.current_powerup_popup = None
        
        # Check boss defeat condition
        if self.boss_level and self.boss_enemy and self.boss_enemy in self.enemies:
            if self.scheduler.scheduler['name'] == self.boss_required_algorithm:
                if abs(self.player.x - self.boss_enemy.x) < 40 and abs(self.player.y - self.boss_enemy.y) < 40:
                    self.enemies.remove(self.boss_enemy)
                    self.entities.remove(self.boss_enemy)
                    self.boss_enemy = None
        
        # Check win condition at finish line
        if self.player.x >= self.finish_line_x:
            boss_defeated = not self.boss_level or self.boss_enemy is None
            all_locks_opened = len(self.locks) == 0
            
            if all_locks_opened and boss_defeated:
                if self.level < self.max_level:
                    self.level += 1
                    self.reset_game()
                    return
                else:
                    self.game_won = True
                    return
            
            # Block player if conditions not met
            self.player.x = self.finish_line_x - 5
    
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
                'has_powerup': False
            },
            'enemies': [{
                'x': enemy.x,
                'y': enemy.y,
                'blocked': enemy.blocked,
                'color': enemy.color,
                'is_boss': enemy.entity_type == 'boss',
                'size': getattr(enemy, 'size', 20)
            } for enemy in self.enemies],
            'powerups': [{
                'x': powerup.x,
                'y': powerup.y,
                'color': (255, 255, 0),
                'algorithm': powerup.algorithm
            } for powerup in self.powerups],
            'keys': [{
                'x': key.x,
                'y': key.y,
                'color': (0, 255, 255)
            } for key in self.keys],
            'locks': [{
                'x': lock.x,
                'y': lock.y,
                'color': (128, 128, 128)
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
                'finish_line_x': self.finish_line_x,
                'start_line_x': self.start_line_x,
                'show_game_over': self.show_game_over,
                'game_over_timer': self.game_over_timer,
                'powerups_collected': self.powerups_collected,
                'keys_collected': self.keys_collected,
                'current_powerup_popup': self.current_powerup_popup,
                'level': self.level,
                'max_level': self.max_level,
                'boss_level': self.boss_level,
                'boss_required_algorithm': self.boss_required_algorithm
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