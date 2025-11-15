from process import Process
from fcfs import FCFS
from round_robin import RoundRobin
from priority import Priority

class GameScheduler:
    def __init__(self):
        # Initialize all 4 scheduling algorithms we want to demonstrate
        # Each algorithm will affect game responsiveness differently
        self.schedulers = [
            FCFS(),                          # Worst for gaming - convoy effect
            RoundRobin(time_quantum=1),      # Fair but laggy - everyone gets 1 second
            Priority(preemptive=False),      # Better - player gets priority but can't interrupt
            Priority(preemptive=True)        # Best - player can interrupt enemies instantly
        ]
        self.current_scheduler_index = 0
        self.scheduler = self.schedulers[0]  # Start with FCFS to show the problem
        
        # Track all game processes (player movement, enemy AI, etc.)
        self.game_processes = []             # Active processes waiting for CPU
        self.current_time = 0
        self.current_process = None
        self.running_process = None
        self.last_running_process = None
        self.completed_processes = []        # Finished processes
        self.process_id_counter = 0          # Track process IDs
        
    def add_game_process(self, entity, task_type, burst_time):
        # Create a new process for game entity (player input, enemy AI, etc.)
        # This simulates how real games create threads for different tasks
        self.process_id_counter += 1
        pid = self.process_id_counter
        priority = entity.priority  # Player=1 (high), Enemy=3 (low)
        
        process = Process(pid, self.current_time, burst_time, priority)
        process.entity = entity     # Link process to game character
        process.task_type = task_type  # What this process does: movement, AI, collision, etc.
        
        # Add to process queue - scheduler will decide when it runs
        self.game_processes.append(process)
        return process
    
    def get_scheduling_delay(self, entity):
        # This is the KEY function - calculates how long entity waits for CPU time
        # Different algorithms = different delays = different game feel
        base_delay = 0.1  # Minimum delay (100ms)
        
        if isinstance(self.scheduler, FCFS):
            # FCFS PROBLEM: Later arrivals wait for ALL earlier processes to finish
            # If 5 enemies arrived before player input, player waits for ALL of them!
            queue_position = sum(1 for p in self.game_processes 
                               if hasattr(p, 'entity') and p.entity != entity and p not in self.completed_processes)
            # Each position in queue adds more delay - this creates the "frozen" feeling
            return base_delay * max(1, queue_position)  # Could be 0.5s+ delay!
            
        elif isinstance(self.scheduler, RoundRobin):
            # Round Robin: Everyone gets fair time slices, so consistent delay
            # Not great for gaming but predictable - no one gets starved
            return base_delay * 0.5  # Fixed 50ms delay for everyone
            
        elif isinstance(self.scheduler, Priority):
            # Priority scheduling: Higher priority = lower delay
            # This is why games feel responsive - player input gets priority!
            if entity.priority == 1:  # High priority (player)
                return base_delay * 0.2  # 20ms - very responsive
            elif entity.priority == 2:  # Medium priority
                return base_delay * 0.5  # 50ms - noticeable but ok
            else:  # Low priority (enemies)
                return base_delay * 1.5  # 150ms - laggy but acceptable for AI
        
        return base_delay
    
    def switch_scheduler(self):
        # Cycle through scheduling algorithms - this is the magic!
        # Player can instantly feel the difference between algorithms
        self.current_scheduler_index = (self.current_scheduler_index + 1) % len(self.schedulers)
        self.scheduler = self.schedulers[self.current_scheduler_index]
        self.reset()  # Clear process queue to start fresh with new algorithm
    
    def reset(self):
        # Clear all processes when switching algorithms or restarting game
        # This ensures fair comparison between scheduling methods
        self.game_processes = []      # Clear process queue
        self.completed_processes = [] # Clear completed processes
        self.current_process = None   # No process currently running
        self.running_process = None
        self.last_running_process = None
        self.process_id_counter = 0   # Reset process ID counter
        self.current_time = 0         # Reset time
        
        # Reset algorithm-specific state (Round Robin needs this)
        if hasattr(self.scheduler, 'queue'):
            self.scheduler.queue = []           # Clear Round Robin queue
            self.scheduler.current_quantum = 0  # Reset time slice counter
    
    def update(self, dt):
        # Update scheduler simulation - processes "execute" and complete over time
        self.current_time += dt
        
        # Simulate process execution - in real OS, CPU actually runs the code
        # Here we just decrement remaining time to simulate work being done
        if self.game_processes:
            for process in self.game_processes[:]:
                process.remaining_time -= dt  # "Execute" the process
                
                # Process finished - move from active to completed queue
                if process.remaining_time <= 0 and process not in self.completed_processes:
                    self.completed_processes.append(process)
                    if process in self.game_processes:
                        self.game_processes.remove(process)  # Remove from active queue