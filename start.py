import subprocess
import sys
import os
import time
from datetime import datetime

def print_status(message, status="INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{status}] {message}")

def run_command(command, cwd=None):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("\nStarting FamilyHVSDN Trading System\n" + "="*40)
    
    # 1. Check Python environment
    print_status("Checking Python environment...")
    if sys.version_info < (3, 8):
        print_status("Python 3.8 or higher is required", "ERROR")
        return
    
    # 2. Install dependencies
    print_status("Installing dependencies...")
    success, output = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if not success:
        print_status("Failed to install dependencies", "ERROR")
        print(output)
        return
    
    # 3. Create necessary directories
    print_status("Creating directories...")
    os.makedirs("training_data/stocks", exist_ok=True)
    os.makedirs("training_data/indices", exist_ok=True)
    os.makedirs("training_data/news", exist_ok=True)
    os.makedirs("ai_models", exist_ok=True)
    
    # 4. Start data collector in background
    print_status("Starting data collector...")
    data_collector = subprocess.Popen(
        [sys.executable, "src/ai/data_collection/auto_data_collector.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 5. Wait for initial data collection
    print_status("Waiting for initial data collection...")
    time.sleep(10)  # Give it some time to start collecting data
    
    # 6. Check if system is working
    print_status("Testing system...")
    success, output = run_command([sys.executable, "src/test_system.py"])
    if not success:
        print_status("System test failed", "ERROR")
        print(output)
        return
    
    print("\n" + "="*40)
    print_status("System is ready!", "SUCCESS")
    print("""
The following components are running:
1. Data Collector (Background process)
2. AI Models (Ready for predictions)
3. Trading System (Ready for use)

You can now:
1. Make predictions using the trading system
2. Monitor data collection in training_data/logs/
3. View model performance in ai_models/logs/

To stop the system, press Ctrl+C
    """)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_status("Shutting down...")
        data_collector.terminate()
        print_status("System stopped", "SUCCESS")

if __name__ == "__main__":
    main()
