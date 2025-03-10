"""
Benchmark for comparing different concurrency models in the HTTP server simulation.
"""

import time
import os
import json
import matplotlib.pyplot as plt
from typing import List, Dict, Any
import psutil

from master import SingleProcessMaster, ThreadedMaster, MultiprocessMaster
from logger import Logger

def get_cpu_count():
    """Get the number of CPU cores."""
    return os.cpu_count() or 4

def run_comprehensive_benchmark(task_counts: List[int] = None, worker_counts: List[int] = None) -> Dict[str, Any]:
    """Run benchmarks for different models with varying task and worker counts."""
    logger = Logger("benchmark")
    
    if task_counts is None:
        task_counts = [10, 50, 100]
        
    if worker_counts is None:
        cpu_count = get_cpu_count()
        worker_counts = [1, cpu_count // 2, cpu_count, cpu_count * 2]
    
    results = {
        'single': [],
        'threaded': [],
        'multiprocess': []
    }
    
    for task_count in task_counts:
        logger.info(f"Running benchmarks with {task_count} tasks")
        
        # Single process benchmark (only one worker)
        logger.info("Running single process benchmark...")
        single = SingleProcessMaster()
        single_result = single.run_benchmark(task_count)
        results['single'].append(single_result)
        
        # Threaded and multiprocess benchmarks with varying worker counts
        for worker_count in worker_counts:
            logger.info(f"Running with {worker_count} workers")
            
            # Threaded benchmark
            logger.info("Running threaded benchmark...")
            threaded = ThreadedMaster(worker_count)
            threaded_result = threaded.run_benchmark(task_count)
            results['threaded'].append(threaded_result)
            
            # Multiprocess benchmark
            logger.info("Running multiprocess benchmark...")
            multiprocess = MultiprocessMaster(worker_count)
            multiprocess_result = multiprocess.run_benchmark(task_count)
            results['multiprocess'].append(multiprocess_result)
    
    # Save results to file
    os.makedirs("results", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"results/benchmark_{timestamp}.json", 'w') as f:
        json.dump(results, f, indent=2)
        
    return results

def visualize_results(results: Dict[str, Any]):
    """Visualize benchmark results."""
    # Extract the data we need for plotting
    models = ['single', 'threaded', 'multiprocess']
    model_labels = {
        'single': 'Single Process',
        'threaded': 'Multi-threading',
        'multiprocess': 'Multi-processing'
    }
    
    # Group by task count and worker count
    datasets = {}
    for model in models:
        for result in results[model]:
            task_count = result['num_tasks']
            worker_count = result['num_workers']
            key = f"{task_count}_{worker_count}"
            
            if key not in datasets:
                datasets[key] = {
                    'task_count': task_count,
                    'worker_count': worker_count,
                    'models': []
                }
            
            datasets[key]['models'].append({
                'name': model_labels[model],
                'total_time': result['total_time'],
                'tasks_per_second': result['tasks_per_second'],
                'memory_mb': result['memory_mb']
            })
    
    # Create plots
    os.makedirs("plots", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # 1. Performance comparison for all models
    plt.figure(figsize=(12, 8))
    
    # Get unique task counts and worker counts
    task_counts = sorted(set(data['task_count'] for data in datasets.values()))
    worker_counts = sorted(set(data['worker_count'] for data in datasets.values()))
    
    # Plot tasks per second for each model and task count
    for task_count in task_counts:
        x_labels = []
        threaded_tps = []
        multiprocess_tps = []
        single_tps = []
        
        for worker_count in worker_counts:
            key = f"{task_count}_{worker_count}"
            if key in datasets:
                data = datasets[key]
                x_labels.append(f"{worker_count}")
                
                for model in data['models']:
                    if model['name'] == 'Single Process':
                        single_tps.append(model['tasks_per_second'])
                    elif model['name'] == 'Multi-threading':
                        threaded_tps.append(model['tasks_per_second'])
                    elif model['name'] == 'Multi-processing':
                        multiprocess_tps.append(model['tasks_per_second'])
        
        # Skip if no data for this task count
        if not x_labels:
            continue
            
        plt.figure(figsize=(10, 6))
        
        # Plot the data
        if single_tps:
            plt.plot([x_labels[0]], single_tps, 'bo-', label='Single Process')
        if threaded_tps:
            plt.plot(x_labels, threaded_tps, 'ro-', label='Multi-threading')
        if multiprocess_tps:
            plt.plot(x_labels, multiprocess_tps, 'go-', label='Multi-processing')
        
        plt.title(f'Performance Comparison ({task_count} tasks)')
        plt.xlabel('Number of Workers')
        plt.ylabel('Tasks Per Second')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"plots/performance_{task_count}_tasks_{timestamp}.png")
        plt.close()
    
    # 2. Memory usage comparison
    plt.figure(figsize=(10, 6))
    
    # Collect memory data for different models
    task_counts_str = [str(tc) for tc in task_counts]
    mem_single = []
    mem_threaded = []
    mem_multiprocess = []
    
    for task_count in task_counts:
        # Use the first worker count entry for each task count
        for worker_count in worker_counts:
            key = f"{task_count}_{worker_count}"
            if key in datasets:
                data = datasets[key]
                for model in data['models']:
                    if model['name'] == 'Single Process':
                        mem_single.append(model['memory_mb'])
                        break
                        
        # Use the highest worker count for multi-threading and multi-processing
        max_worker = max(worker_counts)
        key = f"{task_count}_{max_worker}"
        if key in datasets:
            data = datasets[key]
            for model in data['models']:
                if model['name'] == 'Multi-threading':
                    mem_threaded.append(model['memory_mb'])
                elif model['name'] == 'Multi-processing':
                    mem_multiprocess.append(model['memory_mb'])
    
    # Plot memory usage
    x = list(range(len(task_counts_str)))
    width = 0.25
    
    plt.bar([i - width for i in x], mem_single, width, label='Single Process', color='blue')
    plt.bar(x, mem_threaded, width, label='Multi-threading', color='red')
    plt.bar([i + width for i in x], mem_multiprocess, width, label='Multi-processing', color='green')
    
    plt.xlabel('Number of Tasks')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage Comparison')
    plt.xticks(x, task_counts_str)
    plt.legend()
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig(f"plots/memory_comparison_{timestamp}.png")
    plt.close()

    # Create a summary report
    with open(f"results/summary_{timestamp}.txt", 'w') as f:
        f.write("Benchmark Summary\n")
        f.write("=================\n\n")
        
        for task_count in task_counts:
            f.write(f"\nTask Count: {task_count}\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Model':<20} {'Workers':<10} {'Time (s)':<12} {'Tasks/s':<12} {'Memory (MB)':<12}\n")
            f.write("-" * 70 + "\n")
            
            # Single process data
            for data in results['single']:
                if data['num_tasks'] == task_count:
                    f.write(f"{'Single Process':<20} {data['num_workers']:<10} {data['total_time']:<12.2f} {data['tasks_per_second']:<12.2f} {data['memory_mb']:<12.2f}\n")
                    break
            
            # Threaded data
            for worker_count in worker_counts:
                for data in results['threaded']:
                    if data['num_tasks'] == task_count and data['num_workers'] == worker_count:
                        f.write(f"{'Multi-threading':<20} {data['num_workers']:<10} {data['total_time']:<12.2f} {data['tasks_per_second']:<12.2f} {data['memory_mb']:<12.2f}\n")
                        break
            
            # Multiprocess data
            for worker_count in worker_counts:
                for data in results['multiprocess']:
                    if data['num_tasks'] == task_count and data['num_workers'] == worker_count:
                        f.write(f"{'Multi-processing':<20} {data['num_workers']:<10} {data['total_time']:<12.2f} {data['tasks_per_second']:<12.2f} {data['memory_mb']:<12.2f}\n")
                        break
            
            f.write("\n")

def main():
    """Main entry point for running benchmarks."""
    logger = Logger("main")
    logger.info("Starting HTTP server simulation benchmark")
    
    # Run benchmarks
    cpu_count = get_cpu_count()
    logger.info(f"Detected {cpu_count} CPU cores")
    
    # Configure benchmark parameters
    task_counts = [10, 50, 100]
    worker_counts = [1, max(1, cpu_count // 2), cpu_count, cpu_count * 2]
    
    logger.info(f"Task counts: {task_counts}")
    logger.info(f"Worker counts: {worker_counts}")
    
    # Run the comprehensive benchmark
    results = run_comprehensive_benchmark(task_counts, worker_counts)
    
    # Visualize results
    logger.info("Creating visualizations...")
    visualize_results(results)
    
    logger.info("Benchmark completed")

if __name__ == "__main__":
    main()