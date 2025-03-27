import logging
from datetime import datetime

# Generate a log filename with the current date
log_filename = f"ehr_suction_{datetime.now().strftime('%Y-%m-%d')}.log"

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level (DEBUG, INFO, WARNING, ERROR)

# Create a file handler for writing logs to a file
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)  # Log everything to the file

# Create a console handler for printing logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Only print INFO+ messages to the console

# Define a log format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
