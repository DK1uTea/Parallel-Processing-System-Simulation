# Parallel Processing System Simulation

This project simulates a parallel processing system similar to an HTTP server handling requests. It demonstrates different concurrency models (single process, multithreading, multiprocessing) and provides tools to benchmark and compare their performance.

## Features

- Master-Worker architecture for task processing
- Three concurrency models:
  - Single process (sequential processing)
  - Multithreading (concurrent processing with threads)
  - Multiprocessing (parallel processing with multiple processes)
- Task simulation for I/O-bound, CPU-bound, and mixed workloads
- Performance benchmarking and visualization
- Resource usage monitoring (CPU, memory)

## Requirements

- Python 3.7+
- Dependencies in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running a Specific Model

To run a specific concurrency model:

```bash
python main.py --model [single|threaded|multiprocess] --workers [num_workers] --tasks [num_tasks]
```

Examples:
```bash
# Run single process model with 50 tasks
python main.py --model single --tasks 50

# Run threaded model with 8 workers and 100 tasks
python main.py --model threaded --workers 8 --tasks 100

# Run multiprocess model with 4 workers and 50 tasks
python main.py --model multiprocess --workers 4 --tasks 50
```

### Running Comprehensive Benchmarks

To run comprehensive benchmarks comparing all models:

```bash
python main.py --benchmark
```

This will:
1. Run each model with varying numbers of workers and tasks
2. Generate performance comparison charts
3. Create a summary report in the `results` directory

## Project Structure

- `main.py`: Main entry point
- `master.py`: Master process implementations for different models
- `worker.py`: Worker implementations (thread and process based)
- `task.py`: Task definitions and utilities
- `logger.py`: Logging and performance monitoring utilities
- `benchmark.py`: Benchmarking and visualization tools

## Results

After running benchmarks, results will be available in:
- `results/`: JSON data and text summaries
- `plots/`: Performance comparison charts
- `logs/`: Execution logs

## Example Output

The benchmark results will include:
- Execution time comparison
- Tasks per second for each model
- Memory usage comparison
- CPU utilization

## Performance Considerations

- Single process: Simple but limited performance
- Multithreading: Good for I/O-bound tasks, limited by GIL for CPU-bound tasks
- Multiprocessing: Best for CPU-bound tasks, higher memory overhead

## License

[MIT License](LICENSE)