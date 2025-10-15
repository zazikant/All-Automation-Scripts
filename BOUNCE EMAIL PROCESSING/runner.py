
import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# The worker script that fetches emails
worker_script = "/home/zazikant/process_bounces.py"

# A safety limit to prevent potential infinite loops
max_runs = 200 
run_count = 0

logging.info("Starting the automated email processing runner.")

while run_count < max_runs:
    logging.info(f"Executing worker script, batch #{run_count + 1}")
    
    # Run the worker script as a subprocess
    result = subprocess.run(
        [sys.executable, worker_script],
        capture_output=True,
        text=True
    )

    # Always print the output from the worker script for the agent to see.
    # The agent will process this output after the runner completes.
    print("--- BATCH OUTPUT ---")
    print(result.stdout)
    if result.stderr:
        print("--- BATCH ERRORS ---")
        print(result.stderr)
    print("--- END BATCH ---")

    # Check the worker's output to see if it found any emails.
    # If not, we can stop the loop.
    if "No unread emails found" in result.stdout or "---GEMINI_EMAIL_SEPARATOR---" not in result.stdout:
        logging.info("Worker script reported no more unread emails. Halting runner.")
        break

    run_count += 1

if run_count >= max_runs:
    logging.warning(f"Runner stopped after reaching the maximum of {max_runs} runs.")

logging.info("Automated runner has finished.")
