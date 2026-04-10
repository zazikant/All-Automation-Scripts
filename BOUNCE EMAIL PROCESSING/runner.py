import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# The worker script that fetches emails
worker_script = "/home/zazikant/process_bounces.py"

logging.info("Executing worker script for a single batch.")

# Run the worker script as a subprocess
result = subprocess.run(
    [sys.executable, worker_script],
    capture_output=True,
    text=True
)

# Always print the output from the worker script for the agent to see.
print("--- BATCH OUTPUT ---")
print(result.stdout)
if result.stderr:
    print("--- BATCH ERRORS ---")
    print(result.stderr)
print("--- END BATCH ---")

# Check the worker's output to see if it found any emails.
if "No new emails found" in result.stdout or "---GEMINI_EMAIL_SEPARATOR---" not in result.stdout:
    logging.info("Worker script reported no more new emails.")
else:
    logging.info("Batch processed. Ready for next instruction.")

logging.info("Runner has finished for this batch.")