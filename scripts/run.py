import subprocess
import time

# Path to the script you want to run
script_path = "/home/hdt71/e-Paper/RaspberryPi_JetsonNano/python/examples/epd.py"

# Function to run the script
def run_script():
    try:
        # Run the target script
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        print(f"Script output:\n{result.stdout}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script every minute
while True:
    run_script()
    # Wait for 1 minute
    time.sleep(60)
