class FCFS:
    def __init__(self):
        self.name = "First Come First Serve"
        
    def get_next_process(self, processes, completed_processes, current_time):
        # FCFS: Execute processes in the order they arrived (queue order)
        # Problem: If a long process arrives first, everyone waits!
        available = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes]
        if available:
            # Always pick the earliest arrival - this creates the convoy effect
            return min(available, key=lambda p: p.arrival_time)
        return None
    
    def is_preemptive(self):
        # Non-preemptive: Once a process starts, it runs to completion
        # This makes the convoy effect even worse!
        return False