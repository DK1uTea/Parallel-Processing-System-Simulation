"""
Task definition and utilities for the HTTP server simulation.
"""

import time
import random
import os
from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict

@dataclass
class Task:
    """Represents a task to be processed by a worker."""
    id: int
    task_type: str  # 'io', 'cpu', or 'mixed'
    payload: Dict[str, Any]
    result: Any = None
    processing_time: float = 0.0
    
    def __str__(self):
        return f"Task({self.id}, {self.task_type}, processed in {self.processing_time:.3f}s)"

def io_task(payload: Dict[str, Any]) -> Any:
    """Simulates an I/O bound task like file operations."""
    filename = payload.get('filename', f"temp_{random.randint(1000, 9999)}.txt")
    content = payload.get('content', f"Content generated at {time.time()}")
    size = payload.get('size', 1024)  # Default 1KB
    
    # Simulate file writing
    filepath = os.path.join("temp_files", filename)
    os.makedirs("temp_files", exist_ok=True)
    
    with open(filepath, 'w') as f:
        # Write in small chunks to simulate longer I/O operation
        chunk_size = 128
        for i in range(0, size, chunk_size):
            f.write(content[:chunk_size] + '\n')
            time.sleep(0.001)  # Simulate disk I/O delay
    
    # Simulate file reading
    with open(filepath, 'r') as f:
        data = f.read()
        
    return {'filepath': filepath, 'size': len(data)}

def cpu_task(payload: Dict[str, Any]) -> Any:
    """Simulates a CPU bound task like data processing."""
    iterations = payload.get('iterations', 1000000)
    complexity = payload.get('complexity', 1)
    
    result = 0
    for i in range(iterations):
        # Simulating complex computation
        result += i ** complexity % (i + 1 if i > 0 else 1)
        
    return {'iterations_completed': iterations, 'result': result}

def mixed_task(payload: Dict[str, Any]) -> Any:
    """Performs both I/O and CPU operations."""
    # First do some CPU work
    cpu_result = cpu_task({
        'iterations': payload.get('iterations', 500000),
        'complexity': payload.get('complexity', 1)
    })
    
    # Then some I/O work
    io_result = io_task({
        'filename': payload.get('filename', f"mixed_{random.randint(1000, 9999)}.txt"),
        'content': f"Result: {cpu_result['result']}",
        'size': payload.get('size', 512)
    })
    
    return {'cpu_result': cpu_result, 'io_result': io_result}

def get_task_function(task_type: str) -> Callable:
    """Returns the appropriate task function based on task type."""
    task_functions = {
        'io': io_task,
        'cpu': cpu_task,
        'mixed': mixed_task
    }
    return task_functions.get(task_type, cpu_task)  # Default to CPU task if unknown type

def generate_random_task(task_id: int) -> Task:
    """Generate a random task for testing."""
    task_types = ['io', 'cpu', 'mixed']
    task_type = random.choice(task_types)
    
    payload = {}
    if task_type == 'io':
        payload = {
            'filename': f"file_{task_id}.txt",
            'content': f"Content for task {task_id}",
            'size': random.randint(512, 2048)
        }
    elif task_type == 'cpu':
        payload = {
            'iterations': random.randint(100000, 1000000),
            'complexity': random.randint(1, 2)
        }
    else:  # mixed
        payload = {
            'filename': f"mixed_{task_id}.txt",
            'iterations': random.randint(50000, 500000),
            'complexity': random.randint(1, 2),
            'size': random.randint(256, 1024)
        }
    
    return Task(id=task_id, task_type=task_type, payload=payload)