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

##

# Giải thích Vai Trò Các File Trong Dự Án Parallel Processing System Simulation

Dự án này mô phỏng một hệ thống xử lý song song tương tự như máy chủ HTTP, với các mô hình xử lý khác nhau để so sánh hiệu năng. Dưới đây là vai trò chi tiết của mỗi file:

## 1. `main.py`
- **Tác dụng chính**: Điểm khởi đầu của chương trình, xử lý tham số dòng lệnh
- **Chi tiết xử lý**:
  - Phân tích các đối số dòng lệnh (model, số worker, số task)
  - Điều hướng việc chạy một mô hình cụ thể hoặc chạy benchmark toàn diện
  - Thiết lập và khởi chạy các master theo loại mô hình được chọn

## 2. `master.py`
- **Tác dụng chính**: Định nghĩa các lớp master quản lý công việc và worker
- **Chi tiết xử lý**:
  - `Master`: Lớp cơ sở với logic quản lý task và worker
  - `SingleProcessMaster`: Xử lý tất cả task trong một tiến trình đơn
  - `ThreadedMaster`: Sử dụng đa luồng để xử lý task song song
  - `MultiprocessMaster`: Sử dụng đa tiến trình để xử lý task song song

## 3. `worker.py`
- **Tác dụng chính**: Triển khai các worker xử lý task
- **Chi tiết xử lý**:
  - `Worker`: Lớp cơ sở định nghĩa cách xử lý task
  - `ThreadWorker`: Worker chạy trong luồng riêng
  - `ProcessWorker`: Worker chạy trong tiến trình riêng

## 4. `task.py`
- **Tác dụng chính**: Định nghĩa cấu trúc task và các hàm mô phỏng công việc
- **Chi tiết xử lý**:
  - Định nghĩa class `Task` lưu trữ thông tin task
  - Triển khai các loại task khác nhau:
    - `io_task`: Mô phỏng task I/O-bound (đọc/ghi tệp)
    - `cpu_task`: Mô phỏng task CPU-bound (tính toán nặng)
    - `mixed_task`: Mô phỏng task kết hợp cả I/O và CPU
  - Sinh tạo task ngẫu nhiên cho kiểm thử

## 5. `logger.py`
- **Tác dụng chính**: Cung cấp tiện ích ghi log và theo dõi hiệu năng
- **Chi tiết xử lý**:
  - `Logger`: Lớp ghi log an toàn với thread/process
  - `PerformanceMonitor`: Theo dõi hiệu năng (thời gian, CPU, bộ nhớ)

## 6. `benchmark.py`
- **Tác dụng chính**: Chạy các benchmark so sánh và tạo biểu đồ trực quan
- **Chi tiết xử lý**:
  - `run_comprehensive_benchmark`: Chạy tất cả mô hình với các số lượng worker và task khác nhau
  - `visualize_results`: Tạo biểu đồ và báo cáo từ kết quả benchmark
  - Lưu kết quả vào hai thư mục:
    - results: Chứa dữ liệu JSON và báo cáo tóm tắt
    - plots: Chứa các biểu đồ so sánh hiệu năng

## 7. `requirements.txt`
- **Tác dụng**: Liệt kê các dependency cần thiết
- Các thư viện: matplotlib (vẽ biểu đồ) và psutil (giám sát tài nguyên hệ thống)

## Luồng hoạt động chung:

1. main.py xử lý đối số dòng lệnh và khởi chạy Master phù hợp
2. Master tạo hàng đợi task và khởi tạo các worker
3. Master tạo và gửi các task vào hàng đợi
4. Worker nhận task từ hàng đợi và xử lý chúng
5. Kết quả được trả về Master thông qua hàng đợi kết quả
6. Trong quá trình chạy, logger.py theo dõi và ghi lại thông tin
7. Nếu chạy benchmark, benchmark.py sẽ chạy mọi mô hình và tạo báo cáo so sánh
