import random

class GameChallenge:
    def __init__(self):
        self.challenges = [
            {"name": "Survive 30 seconds", "type": "survival", "target": 30, "reward": 100},
            {"name": "Collect 5 powerups", "type": "collection", "target": 5, "reward": 150},
            {"name": "Defeat 3 enemies", "type": "combat", "target": 3, "reward": 200},
            {"name": "Maintain >80% efficiency", "type": "efficiency", "target": 0.8, "reward": 250}
        ]
        self.current_challenge = None
        self.progress = 0
        self.score = 0
        self.survival_time = 0
        self.powerups_collected = 0
        self.enemies_defeated = 0
        self.total_processes = 0
        self.completed_processes = 0
        
    def start_random_challenge(self):
        self.current_challenge = random.choice(self.challenges)
        self.progress = 0
        
    def update(self, dt, game_state):
        if not self.current_challenge:
            self.start_random_challenge()
            
        self.survival_time += dt
        
        # Update challenge progress
        if self.current_challenge["type"] == "survival":
            self.progress = self.survival_time
        elif self.current_challenge["type"] == "collection":
            self.progress = self.powerups_collected
        elif self.current_challenge["type"] == "combat":
            self.progress = self.enemies_defeated
        elif self.current_challenge["type"] == "efficiency":
            if self.total_processes > 0:
                self.progress = self.completed_processes / self.total_processes
        
        # Check if challenge completed
        if self.progress >= self.current_challenge["target"]:
            self.score += self.current_challenge["reward"]
            self.current_challenge = None
    
    def collect_powerup(self):
        self.powerups_collected += 1
        self.score += 10
    
    def defeat_enemy(self):
        self.enemies_defeated += 1
        self.score += 25
    
    def update_process_stats(self, total, completed):
        self.total_processes = total
        self.completed_processes = completed
    
    def get_efficiency_rating(self):
        if self.total_processes == 0:
            return "N/A"
        efficiency = self.completed_processes / self.total_processes
        if efficiency >= 0.9:
            return "Excellent"
        elif efficiency >= 0.7:
            return "Good"
        elif efficiency >= 0.5:
            return "Fair"
        else:
            return "Poor"