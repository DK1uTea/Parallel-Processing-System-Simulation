"""
Logging utilities for the HTTP server simulation.
"""

import logging
import os
import time
from typing import Optional
import multiprocessing
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger("server_simulation")

class Logger:
    """A thread-safe logger for the simulation."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(f"server_simulation.{name}")
        
        if log_file:
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(f"logs/{log_file}")
            file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log an info message with process/thread information."""
        pid = os.getpid()
        thread_id = threading.get_ident()
        self.logger.info(f"[PID={pid}|TID={thread_id}] {message}")
    
    def error(self, message: str):
        """Log an error message with process/thread information."""
        pid = os.getpid()
        thread_id = threading.get_ident()
        self.logger.error(f"[PID={pid}|TID={thread_id}] {message}")
    
    def debug(self, message: str):
        """Log a debug message with process/thread information."""
        pid = os.getpid()
        thread_id = threading.get_ident()
        self.logger.debug(f"[PID={pid}|TID={thread_id}] {message}")

class PerformanceMonitor:
    """Tracks performance metrics for processes."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.logger = Logger(f"performance.{name}")
        
    def start(self):
        """Start the performance tracking."""
        self.start_time = time.time()
        self.logger.info(f"Starting performance tracking for {self.name}")
        
    def stop(self):
        """Stop the performance tracking and return duration."""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.logger.info(f"Performance tracking for {self.name} completed in {duration:.3f}s")
        return duration
    
    def log_memory_usage(self, process=None):
        """Log memory usage of the current or specified process."""
        import psutil
        
        if process is None:
            process = psutil.Process(os.getpid())
        
        mem_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)
        
        self.logger.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB | "
                         f"CPU: {cpu_percent:.1f}%")
        
        return {
            'memory_mb': mem_info.rss / 1024 / 1024,
            'cpu_percent': cpu_percent
        }