import os
import glob

def print_jsonl_files():
    # Get the directory where this script is located (data folder)
    data_dir = '/home/yifan50/ReasonV-syn-bench/ReasonV/output'

    # Find all .jsonl files in the data directory
    jsonl_files = glob.glob(os.path.join(data_dir, "*.json"))

    # Print each file name
    print("JSONL files in data folder:")
    file_names = []
    for file_path in sorted(jsonl_files):
        file_name = os.path.basename(file_path)
        if 'language-letter-maze' in file_name:
            file_names.append(file_name)
    print(' '.join(file_names))

if __name__ == "__main__":
    print_jsonl_files()