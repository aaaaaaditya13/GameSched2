import random
import time
import json
import os
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
    def __init__(self, difficulty='easy'):
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
        
        # Time slices based on difficulty
        self.difficulty_time_slices = {
            'easy': 2.9,
            'normal': 1.9,
            'hard': 1.0,
            'super_hard': 1.0
        }
        self.entity_time_slice = self.difficulty_time_slices.get(difficulty, 2.9)
        
        # Powerup algorithm timer
        self.powerup_algorithm_timer = 0
        self.powerup_algorithm_duration = 3.0
        self.base_algorithm = {'name': 'First Come First Serve', 'type': 'fcfs'}
        
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
    
    def select_algorithm(self, index):
        algorithms = [
            {'name': 'First Come First Serve', 'type': 'fcfs'},
            {'name': 'Round Robin', 'type': 'rr'},
            {'name': 'Shortest Job First', 'type': 'sjf'},
            {'name': 'Priority (Non-Preemptive)', 'type': 'priority'},
            {'name': 'Priority (Preemptive)', 'type': 'priority_p'}
        ]
        if 0 <= index < len(algorithms):
            self.scheduler = algorithms[index]
            self.current_algorithm_name = self.scheduler['name']
    
    def apply_powerup_algorithm(self, algorithm_name):
        """Apply new scheduling algorithm from power-up for 3 seconds"""
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
            self.powerup_algorithm_timer = self.powerup_algorithm_duration
            # Don't clear queues to maintain process continuity
    
    def reset(self):
        self.ready_queue = []
        self.running_process = None
        self.completed_processes = []
        self.current_time = 0
        self.current_quantum_time = 0
        self.context_switches = 0
        for algo in self.algorithm_metrics:
            self.algorithm_metrics[algo] = {'total_time': 0, 'process_count': 0, 'waiting_times': [], 'turnaround_times': []}
    
    def add_process(self, entity, task_type):
        # Use entity time slice as burst time for equal scheduling
        burst_time = self.entity_time_slice
        pid = len(self.ready_queue) + len(self.completed_processes) + 1
        process = WebProcess(pid, self.current_time, burst_time, entity.priority)
        process.entity = entity
        process.task_type = task_type
        self.ready_queue.append(process)
        return process
    
    def update(self, dt):
        self.current_time += dt
        
        # Handle powerup algorithm timer
        if self.powerup_algorithm_timer > 0:
            self.powerup_algorithm_timer -= dt
            if self.powerup_algorithm_timer <= 0:
                # Revert to FCFS
                self.scheduler = self.base_algorithm.copy()
                self.current_algorithm_name = self.scheduler['name']
        
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
    def __init__(self, difficulty='easy'):
        self.scheduler = WebScheduler(difficulty)
        self.finish_line_x = 700
        self.start_line_x = 100
        self.game_width = 800
        self.game_height = 400
        self.process_speed = 1.0
        
        self.difficulty = difficulty
        self.boss_enemies = []
        self.boss_items = []
        self.boss_items_collected = 0
        self.level_start_time = 0
        self.high_scores = self.load_high_scores()
        
        self.player = WebEntity(self.start_line_x, 200, 'player', priority=1)
        
        self.enemies = []
        self.create_difficulty_enemies()
        
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
        
        self.entities = [self.player] + self.enemies + self.powerups + self.keys + self.locks + self.boss_items
        self.game_won = False
        self.game_time = 0
        self.attempts = 0
        self.lives = 3
        self.game_over = False
        self.show_game_over = False
        self.game_over_timer = 0
        
    def create_difficulty_enemies(self):
        self.enemies = []
        self.boss_enemies = []
        self.boss_items = []
        
        if self.difficulty == 'easy':
            enemy_count = 7
        elif self.difficulty == 'normal':
            enemy_count = 12
        elif self.difficulty == 'hard':
            enemy_count = 7
            self.create_boss(1)
        elif self.difficulty == 'super_hard':
            enemy_count = 7
            self.create_boss(2)
        
        # Create regular enemies
        for i in range(enemy_count):
            x_pos = self.start_line_x + 50 + i * ((self.finish_line_x - self.start_line_x - 100) // max(1, enemy_count))
            y_pos = 80 if i % 2 == 0 else 320
            enemy = WebEntity(x_pos, y_pos, 'enemy', priority=3)
            enemy.direction = 1 if i % 2 == 0 else -1
            enemy.speed = random.uniform(2, 4)
            self.enemies.append(enemy)
    
    def create_boss(self, boss_count):
        boss_colors = ['red', 'blue']
        for i in range(boss_count):
            boss_x = random.randint(self.start_line_x + 100, self.finish_line_x - 100)
            boss_y = 150 + i * 100
            boss = WebEntity(boss_x, boss_y, 'boss', priority=2)
            boss.direction = 1
            boss.speed = 2.0
            boss.size = 40
            boss.color_type = boss_colors[i]
            self.boss_enemies.append(boss)
            self.enemies.append(boss)
            
            # Create individual sword for each boss
            item_x = random.randint(self.start_line_x + 50, self.finish_line_x - 50)
            item_y = random.randint(100, 300)
            boss_item = WebEntity(item_x, item_y, 'boss_item', priority=0)
            boss_item.color_type = boss_colors[i]
            self.boss_items.append(boss_item)
    
    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f, indent=2)
    
    def update_high_score(self, level, time_taken, algorithm):
        level_key = f"level_{level}"
        if level_key not in self.high_scores:
            self.high_scores[level_key] = {'time': float('inf'), 'algorithm': None}
        
        if time_taken < self.high_scores[level_key]['time']:
            self.high_scores[level_key]['time'] = time_taken
            self.high_scores[level_key]['algorithm'] = algorithm
            self.save_high_scores()
            return True
        return False
    
    def set_process_speed(self, speed):
        self.process_speed = speed
    
    def reset_positions(self):
        self.player.x = self.start_line_x
        self.player.y = 200
        
        for i, enemy in enumerate(self.enemies):
            # Keep enemies within start and finish line bounds
            enemy.x = self.start_line_x + 50 + i * ((self.finish_line_x - self.start_line_x - 100) // max(1, len(self.enemies)))
            enemy.y = 80 if i % 2 == 0 else 320
            enemy.direction = 1 if i % 2 == 0 else -1
    
    def reset_game(self):
        self.game_won = False
        self.game_over = False
        self.game_time = 0
        self.level_start_time = time.time()
        self.lives = 3
        
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
        self.scheduler = WebScheduler(self.difficulty)
        
        self.create_difficulty_enemies()
        self.entities = [self.player] + self.enemies + self.powerups + self.keys + self.locks + self.boss_items
        self.scheduler.reset()
    
    def move_player(self, dx, dy):
        # Only allow movement if player's process is currently running
        if self.scheduler.running_process and self.scheduler.running_process.entity == self.player:
            self.player.x += dx * self.player.speed * 5
            self.player.y += dy * self.player.speed * 5
            self.player.x = max(50, min(750, self.player.x))
            self.player.y = max(50, min(350, self.player.y))
        
        # Add player process if not already in queue
        player_has_process = any(p.entity == self.player for p in self.scheduler.ready_queue) or \
                           (self.scheduler.running_process and self.scheduler.running_process.entity == self.player)
        
        if not player_has_process:
            self.scheduler.add_process(self.player, 'movement')
    
    def update(self, dt):
        if self.game_won:
            return
            
        self.game_time += dt
        self.scheduler.update(dt)
        current_time = time.time()
        
        # Add processes for all entities that don't have one
        all_entities = [self.player] + self.enemies
        for entity in all_entities:
            entity_has_process = any(p.entity == entity for p in self.scheduler.ready_queue) or \
                               (self.scheduler.running_process and self.scheduler.running_process.entity == entity)
            
            if not entity_has_process:
                task_type = 'movement' if entity == self.player else 'ai_movement'
                self.scheduler.add_process(entity, task_type)
        
        # Move enemies only when their process is running
        for enemy in self.enemies:
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
                self.current_powerup_popup = f"{powerup.algorithm} activated!"
                self.popup_timer = 1.0  # Short popup for activation
                self.powerups.remove(powerup)
                self.entities.remove(powerup)
        
        # Check collision with swords
        for boss_item in self.boss_items[:]:
            if abs(self.player.x - boss_item.x) < 25 and abs(self.player.y - boss_item.y) < 25:
                self.boss_items_collected += 1
                self.boss_items.remove(boss_item)
                if not hasattr(self.player, 'swords'):
                    self.player.swords = []
                self.player.swords.append(boss_item.color_type)
        
        # Check collision with bosses (need matching sword)
        if hasattr(self.player, 'swords'):
            for boss in self.boss_enemies[:]:
                if abs(self.player.x - boss.x) < 40 and abs(self.player.y - boss.y) < 40:
                    if boss.color_type in self.player.swords:
                        self.boss_enemies.remove(boss)
                        if boss in self.enemies:
                            self.enemies.remove(boss)
                        self.player.swords.remove(boss.color_type)
        
        # Handle popup timer
        if self.popup_timer > 0:
            self.popup_timer -= dt
            if self.popup_timer <= 0:
                self.current_powerup_popup = None
                
        # Show current algorithm info
        if self.scheduler.powerup_algorithm_timer > 0:
            if not self.current_powerup_popup:
                self.current_powerup_popup = f"{self.scheduler.current_algorithm_name} ({self.scheduler.powerup_algorithm_timer:.1f}s)"
            else:
                self.current_powerup_popup = f"{self.scheduler.current_algorithm_name} ({self.scheduler.powerup_algorithm_timer:.1f}s)"
        

        
        # Check win condition at finish line
        if self.player.x >= self.finish_line_x:
            all_bosses_defeated = len(self.boss_enemies) == 0
            all_locks_opened = len(self.locks) == 0
            
            if all_locks_opened and all_bosses_defeated:
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
            'boss_items': [{
                'x': item.x,
                'y': item.y,
                'color_type': item.color_type
            } for item in self.boss_items],
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
                'metrics': self.scheduler.algorithm_metrics,
                'powerup_timer': getattr(self.scheduler, 'powerup_algorithm_timer', 0),
                'entity_time_slice': getattr(self.scheduler, 'entity_time_slice', 2.9)
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
                'popup_timer': self.popup_timer,
                'difficulty': self.difficulty,
                'boss_items_collected': self.boss_items_collected,
                'bosses_remaining': len(self.boss_enemies),
                'high_scores': self.high_scores,
                'current_game_time': self.game_time
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