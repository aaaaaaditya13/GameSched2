import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class ProcessMetrics:
    pid: int
    arrival_time: float
    start_time: float
    completion_time: float
    burst_time: float
    waiting_time: float
    turnaround_time: float
    response_time: float
    algorithm: str

class MetricsCollector:
    def __init__(self):
        self.process_history = []
        self.algorithm_performance = defaultdict(list)
        self.fps_history = deque(maxlen=60)  # Last 60 FPS readings
        self.context_switches = 0
        self.throughput_data = defaultdict(int)
        self.current_fps = 0
        self.start_time = time.time()
        
    def record_process_completion(self, process, algorithm_name):
        """Record metrics when a process completes"""
        if not hasattr(process, 'start_time') or process.start_time is None:
            process.start_time = process.arrival_time
            
        completion_time = time.time()
        waiting_time = process.start_time - process.arrival_time
        turnaround_time = completion_time - process.arrival_time
        response_time = process.start_time - process.arrival_time
        
        metrics = ProcessMetrics(
            pid=process.pid,
            arrival_time=process.arrival_time,
            start_time=process.start_time,
            completion_time=completion_time,
            burst_time=process.burst_time,
            waiting_time=max(0, waiting_time),
            turnaround_time=max(0, turnaround_time),
            response_time=max(0, response_time),
            algorithm=algorithm_name
        )
        
        self.process_history.append(metrics)
        self.algorithm_performance[algorithm_name].append(metrics)
        self.throughput_data[algorithm_name] += 1
        
    def record_context_switch(self):
        """Record when a context switch occurs"""
        self.context_switches += 1
        
    def update_fps(self, fps):
        """Update FPS tracking"""
        self.current_fps = fps
        self.fps_history.append(fps)
        
    def get_algorithm_stats(self, algorithm_name):
        """Get performance statistics for an algorithm"""
        processes = self.algorithm_performance[algorithm_name]
        if not processes:
            return {
                'avg_waiting_time': 0,
                'avg_turnaround_time': 0,
                'avg_response_time': 0,
                'throughput': 0,
                'process_count': 0
            }
            
        return {
            'avg_waiting_time': sum(p.waiting_time for p in processes) / len(processes),
            'avg_turnaround_time': sum(p.turnaround_time for p in processes) / len(processes),
            'avg_response_time': sum(p.response_time for p in processes) / len(processes),
            'throughput': len(processes) / max(1, time.time() - self.start_time),
            'process_count': len(processes)
        }
        
    def get_comparison_data(self):
        """Get data for algorithm comparison charts"""
        algorithms = ['First Come First Serve', 'Round Robin', 'Priority (Non-Preemptive)', 'Priority (Preemptive)']
        comparison = {}
        
        for algo in algorithms:
            stats = self.get_algorithm_stats(algo)
            comparison[algo] = {
                'waiting_time': stats['avg_waiting_time'],
                'turnaround_time': stats['avg_turnaround_time'],
                'response_time': stats['avg_response_time'],
                'throughput': stats['throughput']
            }
            
        return comparison
        
    def get_fps_stats(self):
        """Get FPS statistics"""
        if not self.fps_history:
            return {'current': 0, 'average': 0, 'min': 0, 'max': 0}
            
        fps_list = list(self.fps_history)
        return {
            'current': self.current_fps,
            'average': sum(fps_list) / len(fps_list),
            'min': min(fps_list),
            'max': max(fps_list)
        }
        
    def get_gantt_data(self, limit=20):
        """Get data for Gantt chart visualization"""
        recent_processes = self.process_history[-limit:] if self.process_history else []
        gantt_data = []
        
        for process in recent_processes:
            gantt_data.append({
                'pid': process.pid,
                'algorithm': process.algorithm,
                'start': process.start_time,
                'duration': process.burst_time,
                'entity_type': 'player' if process.pid % 5 == 1 else 'enemy'  # Simple heuristic
            })
            
        return gantt_data
        
    def reset_metrics(self):
        """Reset all metrics"""
        self.process_history = []
        self.algorithm_performance = defaultdict(list)
        self.context_switches = 0
        self.throughput_data = defaultdict(int)
        self.start_time = time.time()