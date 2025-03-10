"""
Main entry point for the HTTP server simulation.
"""

import argparse
import os
from benchmark import main as benchmark_main
from master import SingleProcessMaster, ThreadedMaster, MultiprocessMaster
from logger import Logger

def run_single_model(model_type, num_workers, num_tasks):
    """Run a specific model with given parameters."""
    logger = Logger("main")
    
    if model_type == "single":
        logger.info(f"Running single process model with {num_tasks} tasks")
        master = SingleProcessMaster()
    elif model_type == "threaded":
        logger.info(f"Running threaded model with {num_workers} workers and {num_tasks} tasks")
        master = ThreadedMaster(num_workers)
    elif model_type == "multiprocess":
        logger.info(f"Running multiprocess model with {num_workers} workers and {num_tasks} tasks")
        master = MultiprocessMaster(num_workers)
    else:
        logger.error(f"Unknown model type: {model_type}")
        return
    
    try:
        results = master.run_benchmark(num_tasks)
        logger.info(f"Results: {results['total_time']:.2f}s total, "
                   f"{results['tasks_per_second']:.2f} tasks/s, "
                   f"{results['memory_mb']:.2f}MB memory usage")
    except Exception as e:
        logger.error(f"Error running model: {str(e)}")

def main():
    """Parse command line arguments and run the simulation."""
    parser = argparse.ArgumentParser(description="HTTP Server Simulation")
    
    parser.add_argument("--benchmark", action="store_true", 
                        help="Run comprehensive benchmark comparing all models")
    parser.add_argument("--model", type=str, choices=["single", "threaded", "multiprocess"], 
                        help="Specific model to run")
    parser.add_argument("--workers", type=int, default=os.cpu_count(),
                        help="Number of workers (for threaded and multiprocess models)")
    parser.add_argument("--tasks", type=int, default=50,
                        help="Number of tasks to generate")
    
    args = parser.parse_args()
    
    if args.benchmark:
        benchmark_main()
    elif args.model:
        run_single_model(args.model, args.workers, args.tasks)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()