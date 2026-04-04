import argparse
import subprocess
from pathlib import Path

def run_batch_ingestion(directory_path: str) -> None:
    """
    Recursively scans a directory for text and markdown files, 
    passing each one to the existing data pipeline.

    Args:
        directory_path (str): The relative or absolute path to the directory containing raw data.
    """
    target_dir = Path(directory_path)
    
    if not target_dir.is_dir():
        print(f"❌ Error: Directory '{directory_path}' not found.")
        return

    # We only support text formats right now as per the current pipeline limits
    supported_extensions = {".txt", ".md"}
    
    # Find all matching files recursively
    files_to_process = [
        f for f in target_dir.rglob("*") 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not files_to_process:
        print(f"⚠️ No supported files ({', '.join(supported_extensions)}) found in '{directory_path}'.")
        return

    print(f"🔍 Found {len(files_to_process)} files to process in '{directory_path}'.\n")

    success_count = 0
    failure_count = 0

    for file_path in files_to_process:
        print(f"⏳ Processing: {file_path.name}...")
        
        # Call the existing pipeline script as a separate process
        try:
            subprocess.run(
                ["python", "data_pipeline/run_pipeline.py", "--file", str(file_path)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Success: {file_path.name}")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {file_path.name}")
            # Print the last few lines of the error to help debug without flooding the terminal
            print(f"   Error details: {e.stderr.strip().split(chr(10))[-1]}")
            failure_count += 1

    print("-" * 50)
    print(f"🎉 Batch Ingestion Complete!")
    print(f"   Successfully processed: {success_count}")
    print(f"   Failed to process:      {failure_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process raw data files through the ETL pipeline.")
    parser.add_argument(
        "--dir", 
        type=str, 
        default="raw_data", 
        help="Directory containing the raw text files. Defaults to 'raw_data'."
    )
    args = parser.parse_args()
    
    run_batch_ingestion(args.dir)
    