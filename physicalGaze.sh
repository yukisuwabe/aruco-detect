#!/bin/bash

# Check if at least one input folder is provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 <input_folder1> [input_folder2] ..."
  exit 1
fi

# Loop through all provided folders and run detect.py
for INPUT_FOLDER in "$@"; 
do
  python3 detect.py "$INPUT_FOLDER"
done
