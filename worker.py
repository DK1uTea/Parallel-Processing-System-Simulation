"""
Worker implementation for the HTTP server simulation.
"""

import time
import os
from multiprocessing import Process
from threading import Thread
import queue
import signal

from logger import Logger
from task import Task, get_task_function

class Worker:
    """Base worker class for processing tasks."""
    
    def __init__(self, worker_id, task_queue, result_queue, worker_type="base"):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.worker_type = worker_type
        self.logger = Logger(f"{worker_type}.worker.{worker_id}")
        
    def process_task(self, task):
        """Process a single task and return the result."""
        self.logger.info(f"Starting task {task.id} ({task.task_type})")
        start_time = time.time()
        
        try:
            # Get the appropriate function for the task type
            task_func = get_task_function(task.task_type)
            
            # Execute the task
            result = task_func(task.payload)
            
            # Update task with result and processing time
            task.result = result
            task.processing_time = time.time() - start_time
            
            self.logger.info(f"Completed task {task.id} in {task.processing_time:.3f}s")
            return task
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            task.result = f"Error: {str(e)}"
            task.processing_time = time.time() - start_time
            return task
            
    def stop(self):
        """Stop the worker."""
        self.running = False

class ThreadWorker(Worker, Thread):
    """Worker implementation using threads."""
    
    def __init__(self, worker_id, task_queue, result_queue):
        Worker.__init__(self, worker_id, task_queue, result_queue, "thread")
        Thread.__init__(self, daemon=True)
        
    def run(self):
        """Main worker loop for processing tasks from the queue."""
        self.logger.info(f"Thread worker {self.worker_id} started")
        
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.5)
                if task is None:  # Poison pill
                    self.logger.info(f"Thread worker {self.worker_id} received shutdown signal")
                    break
                
                processed_task = self.process_task(task)
                self.result_queue.put(processed_task)
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error in worker: {str(e)}")
                
        self.logger.info(f"Thread worker {self.worker_id} stopped")

class ProcessWorker(Worker, Process):
    """Worker implementation using processes."""
    
    def __init__(self, worker_id, task_queue, result_queue):
        Worker.__init__(self, worker_id, task_queue, result_queue, "process")
        Process.__init__(self, daemon=True)
        
    def run(self):
        """Main worker loop for processing tasks from the queue."""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        self.logger.info(f"Process worker {self.worker_id} started (PID: {os.getpid()})")
        
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.5)
                if task is None:  # Poison pill
                    self.logger.info(f"Process worker {self.worker_id} received shutdown signal")
                    break
                
                processed_task = self.process_task(task)
                self.result_queue.put(processed_task)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error in worker: {str(e)}")
                
        self.logger.info(f"Process worker {self.worker_id} stopped")