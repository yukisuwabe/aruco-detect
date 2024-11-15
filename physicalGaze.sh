
#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <input>"
  exit 1
fi

# Run detect.py with the provided argument
python3 detect.py "$1"