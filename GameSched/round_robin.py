class RoundRobin:
    def __init__(self, time_quantum=2):
        self.name = "Round Robin"
        self.time_quantum = time_quantum  # Each process gets this much CPU time
        self.queue = []                   # Circular queue of processes
        self.current_quantum = 0          # How much time current process has used
        
    def get_next_process(self, processes, completed_processes, current_time):
        # Add newly arrived processes to the round-robin queue
        for p in processes:
            if (p.arrival_time <= current_time and 
                p not in completed_processes and 
                p not in self.queue and
                p.remaining_time > 0):
                self.queue.append(p)  # Add to end of circular queue
        
        # Return first process in queue (FIFO within the time slices)
        if self.queue:
            return self.queue[0]
        return None
    
    def should_preempt(self, current_process):
        # Preempt when time quantum is used up
        if current_process and self.current_quantum >= self.time_quantum:
            self.current_quantum = 0  # Reset quantum counter
            
            # Move current process to end of queue (round-robin)
            if current_process in self.queue:
                self.queue.remove(current_process)
                if current_process.remaining_time > 0:
                    self.queue.append(current_process)  # Back to end of line
            return True
        return False
    
    def update_quantum(self, dt):
        # Track how much time current process has used
        self.current_quantum += dt
    
    def process_completed(self, process):
        # Remove completed process from queue
        if process in self.queue:
            self.queue.remove(process)
        self.current_quantum = 0
    
    def is_preemptive(self):
        # Yes, preemptive - processes get interrupted after time quantum
        return True