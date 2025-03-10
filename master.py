"""
Master process implementation for the HTTP server simulation.
"""

import time
import os
import signal
import multiprocessing
from multiprocessing import Queue as ProcessQueue
import queue
import threading
from typing import List, Dict, Any, Optional, Union
import psutil

from worker import ThreadWorker, ProcessWorker
from task import Task, generate_random_task
from logger import Logger, PerformanceMonitor

class Master:
    """Base master class for managing workers and tasks."""
    
    def __init__(self, name: str, num_workers: int = 4):
        self.name = name
        self.num_workers = num_workers
        self.workers = []
        self.task_queue = None
        self.result_queue = None
        self.logger = Logger(f"master.{name}")
        self.performance = PerformanceMonitor(f"master.{name}")
        self.running = False
        self.tasks_submitted = 0
        self.tasks_completed = 0
        self.create_queues()
        
    def create_queues(self):
        """Create task and result queues - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement create_queues")
        
    def create_workers(self):
        """Create worker processes/threads - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement create_workers")
        
    def start_workers(self):
        """Start all worker processes/threads."""
        self.logger.info(f"Starting {self.num_workers} workers...")
        for worker in self.workers:
            worker.start()
        self.running = True
        
    def stop_workers(self):
        """Stop all worker processes/threads."""
        if not self.running:
            return
            
        self.logger.info(f"Stopping {len(self.workers)} workers...")
        
        # Send poison pills to stop workers
        for _ in range(len(self.workers)):
            self.task_queue.put(None)
            
        # Join all workers
        for worker in self.workers:
            if hasattr(worker, 'join'):
                worker.join(timeout=2.0)
                
        self.running = False
        self.logger.info("All workers stopped")
        
    def submit_task(self, task: Task):
        """Submit a task to be processed."""
        self.task_queue.put(task)
        self.tasks_submitted += 1
        self.logger.info(f"Task {task.id} submitted ({task.task_type})")
        
    def collect_results(self, timeout: Optional[float] = 0.5) -> List[Task]:
        """Collect completed tasks from the result queue."""
        results = []
        
        try:
            while True:
                result = self.result_queue.get(block=False)
                results.append(result)
                self.tasks_completed += 1
                if hasattr(self.result_queue, 'task_done'):
                    self.result_queue.task_done()
        except Exception:  # Handle any queue empty exceptions
            pass
            
        return results
        
    def generate_workload(self, num_tasks: int):
        """Generate and submit a number of random tasks."""
        self.logger.info(f"Generating workload of {num_tasks} tasks...")
        self.performance.start()
        
        for i in range(num_tasks):
            task = generate_random_task(i+1)
            self.submit_task(task)
            
        return self.tasks_submitted
        
    def wait_for_completion(self, check_interval: float = 0.5, timeout: Optional[float] = None) -> List[Task]:
        """Wait for all submitted tasks to be completed."""
        all_results = []
        start_time = time.time()
        last_status_time = start_time
        
        self.logger.info(f"Waiting for {self.tasks_submitted} tasks to complete...")
        
        while self.tasks_completed < self.tasks_submitted:
            # Check for timeout
            if timeout and (time.time() - start_time) > timeout:
                self.logger.error(f"Timeout reached after {timeout} seconds")
                break
                
            # Collect any completed tasks
            results = self.collect_results()
            all_results.extend(results)
            
            # Print status every 5 seconds
            current_time = time.time()
            if current_time - last_status_time >= 5.0:
                self.logger.info(f"Progress: {self.tasks_completed}/{self.tasks_submitted} tasks completed")
                last_status_time = current_time
                
                # Log resource usage
                self.performance.log_memory_usage()
                
            time.sleep(check_interval)
            
        # Final collection of results
        results = self.collect_results()
        all_results.extend(results)
        
        duration = self.performance.stop()
        self.logger.info(f"Completed {self.tasks_completed}/{self.tasks_submitted} tasks in {duration:.2f}s")
        
        return all_results
        
    def run_benchmark(self, num_tasks: int = 50) -> Dict[str, Any]:
        """Run a benchmark with a fixed number of tasks."""
        try:
            self.start_workers()
            
            start_time = time.time()
            self.generate_workload(num_tasks)
            results = self.wait_for_completion()
            end_time = time.time()
            
            # Calculate statistics
            total_time = end_time - start_time
            tasks_per_second = num_tasks / total_time if total_time > 0 else 0
            
            task_times = [task.processing_time for task in results]
            avg_task_time = sum(task_times) / len(task_times) if task_times else 0
            
            # Group tasks by type
            task_types = {}
            for task in results:
                if task.task_type not in task_types:
                    task_types[task.task_type] = []
                task_types[task.task_type].append(task.processing_time)
            
            # Calculate average time by task type
            avg_by_type = {}
            for task_type, times in task_types.items():
                avg_by_type[task_type] = sum(times) / len(times)
                
            # Get memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            benchmark_result = {
                'master_type': self.name,
                'num_workers': self.num_workers,
                'num_tasks': num_tasks,
                'total_time': total_time,
                'tasks_per_second': tasks_per_second,
                'avg_task_time': avg_task_time,
                'avg_by_type': avg_by_type,
                'memory_mb': memory_mb
            }
            
            self.logger.info(f"Benchmark results for {self.name}:")
            self.logger.info(f"- Total time: {total_time:.3f}s")
            self.logger.info(f"- Tasks per second: {tasks_per_second:.3f}")
            self.logger.info(f"- Average task time: {avg_task_time:.3f}s")
            self.logger.info(f"- Memory usage: {memory_mb:.2f} MB")
            
            return benchmark_result
            
        finally:
            self.stop_workers()

class SingleProcessMaster(Master):
    """Master implementation using a single process for all tasks."""
    
    def __init__(self, num_workers: int = 1):
        super().__init__("single_process", num_workers=1)  # Always use 1 worker
        self.create_workers()
        
    def create_queues(self):
        """Create regular Python queues."""
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
    def create_workers(self):
        """Create a single worker that processes tasks sequentially."""
        self.workers = [ThreadWorker(1, self.task_queue, self.result_queue)]

class ThreadedMaster(Master):
    """Master implementation using multiple threads for concurrent processing."""
    
    def __init__(self, num_workers: int = 4):
        super().__init__("threaded", num_workers)
        self.create_workers()
        
    def create_queues(self):
        """Create thread-safe queues."""
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
    def create_workers(self):
        """Create multiple thread workers."""
        self.workers = [
            ThreadWorker(i+1, self.task_queue, self.result_queue)
            for i in range(self.num_workers)
        ]

class MultiprocessMaster(Master):
    """Master implementation using multiple processes for parallel processing."""
    
    def __init__(self, num_workers: int = 4):
        super().__init__("multiprocess", num_workers)
        self.create_workers()
        
    def create_queues(self):
        """Create process-safe queues."""
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        
    def create_workers(self):
        """Create multiple process workers."""
        self.workers = [
            ProcessWorker(i+1, self.task_queue, self.result_queue)
            for i in range(self.num_workers)
        ]