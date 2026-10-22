import logging
import os
from datetime import datetime

# Name of the log file, based on the current date and time
# Example: 2026-10-22_14-30-05.log
LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

# Create the "logs" folder in the current directory if it doesn't exist yet
# exist_ok=True prevents an error if the folder is already there
os.makedirs('logs', exist_ok=True)

# Full path to the log file, e.g. logs/2026-10-22_14-30-05.log
LOG_FILE_PATH = os.path.join('logs', LOG_FILE)

# Configure logging once, after the folder and path are ready
logging.basicConfig(
    filename=LOG_FILE_PATH,  # write logs to this file
    level=logging.INFO,      # record INFO and above (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # timestamp - level - message
)