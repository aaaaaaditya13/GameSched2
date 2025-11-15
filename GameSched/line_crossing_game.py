import pygame
import random
from game_entity import GameEntity
from game_scheduler import GameScheduler

class LineCrossingGame:
    def __init__(self):
        self.scheduler = GameScheduler()
        self.finish_line_x = 700
        self.start_line_x = 100
        self.game_width = 800
        self.game_height = 600
        
        # Create player at start line
        self.player = GameEntity(self.start_line_x, 300, 'player', priority=1)
        
        # Create AI enemies
        self.enemies = []
        for i in range(4):
            enemy_x = random.randint(200, 600)
            enemy_y = random.randint(150, 450)
            enemy = GameEntity(enemy_x, enemy_y, 'enemy', priority=3)
            self.enemies.append(enemy)
        
        self.entities = [self.player] + self.enemies
        self.game_won = False
        self.game_time = 0
        self.attempts = 0
        
    def reset_game(self):
        self.game_won = False
        self.game_time = 0
        self.attempts += 1
        
        # Reset player to start line
        self.player.x = self.start_line_x
        self.player.y = 300
        self.player.reset_position()
        
        # Randomize enemy positions
        for enemy in self.enemies:
            enemy.x = random.randint(200, 600)
            enemy.y = random.randint(150, 450)
            enemy.start_x = enemy.x
            enemy.start_y = enemy.y
            enemy.reset_position()
        
        self.scheduler.reset()
        
        # For priority algorithms, start with enemy processes
        from priority import Priority
        if isinstance(self.scheduler.scheduler, Priority):
            for enemy in self.enemies:
                self.scheduler.add_game_process(enemy, 'ai', random.uniform(0.5, 1.0))
    
    def update(self, dt, keys_pressed):
        if self.game_won:
            return
            
        self.game_time += dt
        
        # Update the scheduler simulation - processes complete over time
        self.scheduler.update(dt)
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Capture player input - this represents "user input events"
        dx = dy = 0
        player_has_input = False
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            dy = -1
            player_has_input = True
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            dy = 1
            player_has_input = True
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            dx = -1
            player_has_input = True
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            dx = 1
            player_has_input = True
        
        # Create player process ONLY when there's actual input AND no existing player process
        if player_has_input:
            has_player_process = any(p.entity == self.player for p in self.scheduler.game_processes)
            if not has_player_process:
                self.scheduler.add_game_process(self.player, 'input', random.uniform(0.2, 0.4))
        
        # Create enemy AI processes based on algorithm
        from priority import Priority
        if isinstance(self.scheduler.scheduler, Priority):
            # Priority: Always ensure each enemy has a process
            for enemy in self.enemies:
                has_enemy_process = any(p.entity == enemy for p in self.scheduler.game_processes)
                if not has_enemy_process:
                    self.scheduler.add_game_process(enemy, 'ai', random.uniform(0.5, 1.0))
        else:
            # FCFS/RR: Create processes randomly
            for enemy in self.enemies:
                has_enemy_process = any(p.entity == enemy for p in self.scheduler.game_processes)
                if not has_enemy_process and random.random() < 0.3:
                    self.scheduler.add_game_process(enemy, 'ai', random.uniform(0.3, 0.6))
        
        # Update all entities with scheduling delays
        for entity in self.entities:
            delay = self.scheduler.get_scheduling_delay(entity)
            entity.update(current_time, delay, self.finish_line_x)
        
        # Try to move player - but only if not blocked by scheduler!
        if player_has_input and not self.player.blocked:
            self.player.move(dx, dy)
        
        # Win condition: reach the finish line
        if self.player.x >= self.finish_line_x:
            self.game_won = True
    
    def draw(self, screen, font, small_font):
        # Draw game area
        game_rect = pygame.Rect(50, 100, self.game_width - 100, self.game_height - 200)
        pygame.draw.rect(screen, (240, 240, 240), game_rect)
        pygame.draw.rect(screen, (0, 0, 0), game_rect, 2)
        
        # Draw start line
        pygame.draw.line(screen, (0, 255, 0), (self.start_line_x, 120), (self.start_line_x, 480), 5)
        start_text = small_font.render("START", True, (0, 255, 0))
        screen.blit(start_text, (self.start_line_x - 20, 490))
        
        # Draw finish line
        pygame.draw.line(screen, (255, 0, 0), (self.finish_line_x, 120), (self.finish_line_x, 480), 5)
        finish_text = small_font.render("FINISH", True, (255, 0, 0))
        screen.blit(finish_text, (self.finish_line_x - 25, 490))
        
        # Draw entities
        for entity in self.entities:
            entity.draw(screen)
        
        # Draw scheduling effect indicators - this is the visual proof!
        # Ring colors show how responsive each entity is under current algorithm
        for entity in self.entities:
            delay = self.scheduler.get_scheduling_delay(entity)
            
            # Color-code the responsiveness:
            if delay > 0.3:
                color = (255, 0, 0)  # RED = High delay (>300ms) - Feels frozen/laggy
            elif delay > 0.1:
                color = (255, 255, 0)  # YELLOW = Medium delay (100-300ms) - Noticeable lag
            else:
                color = (0, 255, 0)  # GREEN = Low delay (<100ms) - Responsive
            
            # Draw colored ring around entity to show scheduling effect
            pygame.draw.circle(screen, color, (int(entity.x), int(entity.y)), 25, 2)
        
        # Draw game info
        info_y = 50
        algorithm_text = font.render(f"Algorithm: {self.scheduler.scheduler.name}", True, (0, 0, 0))
        screen.blit(algorithm_text, (50, info_y))
        
        time_text = small_font.render(f"Time: {self.game_time:.1f}s", True, (0, 0, 0))
        screen.blit(time_text, (400, info_y))
        
        attempts_text = small_font.render(f"Attempts: {self.attempts}", True, (0, 0, 0))
        screen.blit(attempts_text, (500, info_y))
        
        if self.game_won:
            win_text = font.render(f"SUCCESS! Time: {self.game_time:.1f}s", True, (0, 255, 0))
            screen.blit(win_text, (250, 250))
        
        # Draw legend
        legend_y = 520
        legend_items = [
            ("Green Circle: Player (High Priority)", (0, 255, 0)),
            ("Red Circle: AI Enemy (Low Priority)", (255, 0, 0)),
            ("Ring Color: Green=Responsive, Yellow=Delayed, Red=Blocked", (0, 0, 0))
        ]
        
        for i, (text, color) in enumerate(legend_items):
            legend_surface = small_font.render(text, True, color)
            screen.blit(legend_surface, (50, legend_y + i * 20))