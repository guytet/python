import os
import argparse

"""
Takes <dir path> as arg value
Recurselivy prints all 0 byte files within <dir path
"""

class ZeroByteFileFinder:
    def __init__(self, directory):
        if not os.path.isdir(directory):
            raise ValueError(f"The path '{directory}' is not a valid directory.")
        self.directory = directory

    def find_zero_byte_files(self):
        zero_byte_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) == 0:
                        zero_byte_files.append(file_path)
                except OSError as e:
                    print(f"Error accessing file {file_path}: {e}")
        return zero_byte_files

def main():
    parser = argparse.ArgumentParser(description="Find all zero-byte files in a directory.")
    parser.add_argument("directory", help="Path to the directory to scan")
    args = parser.parse_args()

    try:
        finder = ZeroByteFileFinder(args.directory)
        empty_files = finder.find_zero_byte_files()
        if empty_files:
            print("Zero-byte files found:")
            for file in empty_files:
                print(file)
        else:
            print("No zero-byte files found.")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()

