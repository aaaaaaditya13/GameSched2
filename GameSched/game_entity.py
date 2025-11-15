import random
import pygame

class GameEntity:
    def __init__(self, x, y, entity_type, priority=1):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.entity_type = entity_type
        self.priority = priority
        self.speed = 3 if entity_type == 'player' else 2
        self.last_update = 0
        self.active = True
        self.blocked = False
        self.color = self.get_color()
        
    def get_color(self):
        colors = {
            'player': (0, 255, 0),
            'enemy': (255, 0, 0)
        }
        return colors.get(self.entity_type, (128, 128, 128))
    
    def update(self, current_time, scheduling_delay, finish_line_x):
        # This is where scheduling delay affects gameplay!
        # If scheduling_delay is high, entity can't update = frozen/laggy movement
        if not self.active or current_time - self.last_update < scheduling_delay:
            self.blocked = True  # Entity is "waiting for CPU time"
            return  # Can't move until scheduler gives us CPU time!
            
        # Got CPU time! Entity can now update/move
        self.blocked = False
        self.last_update = current_time
        
        if self.entity_type == 'enemy':
            # Simple AI: Try to block player by moving toward finish line
            # This simulates enemy AI processes competing for CPU time
            if self.x < finish_line_x - 50:
                self.x += self.speed  # Move toward finish line to block player
            
            # Add some vertical movement to make enemies more challenging
            if random.random() < 0.3:  # 30% chance to move vertically
                self.y += random.randint(-2, 2)
                self.y = max(100, min(500, self.y))  # Keep within bounds
    
    def move(self, dx, dy):
        # Player movement - only works if not blocked by scheduler!
        # This is the key to demonstrating scheduling effects
        if not self.blocked:  # Only move if we have CPU time
            self.x += dx * self.speed
            self.y += dy * self.speed
            # Keep player within game boundaries
            self.x = max(50, min(750, self.x))
            self.y = max(100, min(500, self.y))
        # If blocked, player input is ignored = frustrating gameplay!
    
    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
    
    def draw(self, screen):
        if self.active:
            # Draw the game character (player=green, enemy=red)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 15)
            
            # Visual feedback: Yellow ring when blocked by scheduler
            # This shows when entity is "waiting for CPU time"
            if self.blocked:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 20, 3)