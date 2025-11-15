class Priority:
    def __init__(self, preemptive=False):
        self.name = "Priority (Preemptive)" if preemptive else "Priority (Non-Preemptive)"
        self.preemptive = preemptive
        
    def get_next_process(self, processes, completed_processes, current_time):
        # Priority scheduling: Always pick the highest priority process
        # This is why games feel responsive - player input gets priority!
        available = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes and p.remaining_time > 0]
        if available:
            # Lower number = higher priority (1=highest, 3=lowest)
            # Player=1, Enemy=3, so player always goes first
            return min(available, key=lambda p: p.priority)
        return None
    
    def should_preempt(self, current_process, processes, current_time):
        # Preemptive version: Higher priority process can interrupt lower priority
        if not self.preemptive or not current_process:
            return False
        
        # Check if a higher priority process has arrived
        next_process = self.get_next_process(processes, [], current_time)
        # If new process has higher priority (lower number), interrupt current process
        return next_process and next_process.priority < current_process.priority
    
    def is_preemptive(self):
        return self.preemptive