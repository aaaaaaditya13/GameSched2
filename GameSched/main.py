import pygame
import random
import sys
from line_crossing_game import LineCrossingGame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
GRAY = (200, 200, 200)

class LineCrossingVisualizer:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Line Crossing - CPU Scheduling Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        self.game = LineCrossingGame()
        self.running = True
        self.paused = False
    
    def switch_scheduler(self):
        self.game.scheduler.switch_scheduler()
    
    def reset_game(self):
        self.game.reset_game()
    
    def update_game(self):
        if self.paused:
            return
        
        dt = 1/30  # 30 FPS
        keys = pygame.key.get_pressed()
        self.game.update(dt, keys)
    

    
    def draw_process_queue(self):
        x_start = 850
        y_start = 100
        
        title = self.font.render("Process Queue", True, BLACK)
        self.screen.blit(title, (x_start, y_start - 30))
        
        # Draw queue visualization
        queue_processes = [p for p in self.game.scheduler.game_processes if p not in self.game.scheduler.completed_processes]
        
        for i, process in enumerate(queue_processes[:10]):  # Show max 10 processes
            y = y_start + i * 25
            
            # Color based on entity type
            if hasattr(process, 'entity'):
                color = process.entity.color
            else:
                color = GRAY
            
            # Draw process box
            pygame.draw.rect(self.screen, color, (x_start, y, 180, 20))
            pygame.draw.rect(self.screen, BLACK, (x_start, y, 180, 20), 1)
            
            # Draw process info
            if hasattr(process, 'entity'):
                entity_type = "Player" if process.entity.entity_type == 'player' else "Enemy"
                text = f"{entity_type} P{process.priority}"
            else:
                text = f"Process P{process.priority}"
            
            text_surface = self.small_font.render(text, True, BLACK)
            self.screen.blit(text_surface, (x_start + 5, y + 3))
            
            # Draw remaining time bar
            if process.burst_time > 0:
                progress = 1 - (process.remaining_time / process.burst_time)
                bar_width = int(160 * progress)
                pygame.draw.rect(self.screen, GREEN, (x_start + 10, y + 15, bar_width, 2))
    
    def draw_algorithm_comparison(self):
        x_start = 850
        y_start = 400
        
        title = self.font.render("Algorithm Effects", True, BLACK)
        self.screen.blit(title, (x_start, y_start - 30))
        
        algorithm_effects = {
            "First Come First Serve": ["Player may lag behind enemies", "Convoy effect visible", "Unpredictable response"],
            "Round Robin": ["Fair time sharing", "Consistent delays", "Moderate responsiveness"],
            "Priority (Non-Preemptive)": ["Player gets priority", "Enemies may starve", "Better player control"],
            "Priority (Preemptive)": ["Best player response", "Real-time performance", "Optimal for gaming"]
        }
        
        current_algo = self.game.scheduler.scheduler.name
        if current_algo in algorithm_effects:
            effects = algorithm_effects[current_algo]
            for i, effect in enumerate(effects):
                text = self.small_font.render(f"• {effect}", True, BLACK)
                self.screen.blit(text, (x_start, y_start + i * 20))
        
        # Draw performance stats
        stats_y = y_start + 80
        stats = [
            f"Game Time: {self.game.game_time:.1f}s",
            f"Attempts: {self.game.attempts}",
            f"Active Processes: {len(self.game.scheduler.game_processes)}",
            f"Completed: {len(self.game.scheduler.completed_processes)}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, BLACK)
            self.screen.blit(text, (x_start, stats_y + i * 20))
    
    def draw_controls(self):
        controls = [
            "Controls:",
            "WASD/Arrow Keys - Move Player",
            "SPACE - Play/Pause",
            "S - Switch Algorithm",
            "R - Reset Game",
            "ESC - Exit",
            "",
            "Objective: Reach the red finish line",
            "Red enemies try to block your path"
        ]
        
        for i, control in enumerate(controls):
            color = BLUE if "Objective" in control or "Red enemies" in control else BLACK
            text = self.small_font.render(control, True, color)
            self.screen.blit(text, (850, 550 + i * 18))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_s:
                    self.switch_scheduler()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            
            self.screen.fill(WHITE)
            self.game.draw(self.screen, self.font, self.small_font)
            self.draw_process_queue()
            self.draw_algorithm_comparison()
            self.draw_controls()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    visualizer = LineCrossingVisualizer()
    visualizer.run()