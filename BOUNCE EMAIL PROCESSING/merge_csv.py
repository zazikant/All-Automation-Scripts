import os
import csv
import glob

# ---
# Configuration ---
OUTPUT_DIR = "/home/zazikant/output"
MERGED_FILE = os.path.join(OUTPUT_DIR, "merged_results.csv")
FILE_PATTERN = os.path.join(OUTPUT_DIR, "batch_*_results.csv")
# ---
# End Configuration ---

def merge_csv_files():
    """
    Merges all CSV files matching the FILE_PATTERN into a single
    CSV file.
    """
    # Get a list of all CSV files to merge
    csv_files = glob.glob(FILE_PATTERN)
    if not csv_files:
        print("No CSV files found to merge.")
        return

    # Sort files to maintain order (optional, but good practice)
    csv_files.sort()

    # Open the output file in write mode
    with open(MERGED_FILE, "w", newline="") as outfile:
        writer = csv.writer(outfile)

        # Process the first file to write the header
        first_file = True
        for filename in csv_files:
            # Skip empty files
            if os.path.getsize(filename) == 0:
                continue
            with open(filename, "r", newline="") as infile:
                reader = csv.reader(infile)
                try:
                    header = next(reader)
                except StopIteration:
                    continue # Skip empty file

                if first_file:
                    writer.writerow(header)
                    first_file = False

                # Write the rest of the rows
                for row in reader:
                    writer.writerow(row)

    print(f"Successfully merged {len(csv_files)} files into {MERGED_FILE}")

if __name__ == "__main__":
    merge_csv_files()
