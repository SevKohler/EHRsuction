import logging
import os
from datetime import datetime
import yaml

# Load config.yaml
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Get log levels from config and convert string to logging levels
if config["logging"]["cmd_level"].upper() == "INFO":
    cmd_level = logging.INFO
elif config["logging"]["cmd_level"].upper() == "DEBUG":
    cmd_level = logging.DEBUG
elif config["logging"]["cmd_level"].upper() == "ERROR":
    cmd_level = logging.ERROR
else:
    raise ValueError("Only info, error or debug are supported for cmd_level logging ")  # This will stop the program with a ValueError

if config["logging"]["file_level"].upper() == "INFO":
    file_level = logging.INFO
elif config["logging"]["file_level"].upper() == "DEBUG":
    file_level = logging.DEBUG
elif config["logging"]["cmd_level"].upper() == "ERROR":
    file_level = logging.ERROR
else:
    raise ValueError("Only info, error or debug are supported for file_level logging ")  # This will stop the program with a ValueError


# Define 'log' directory relative to the current directory
log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
os.makedirs(log, exist_ok=True)

# Define log filename inside the 'log' folder
log_filename = os.path.join(log, f"ehr_suction_{datetime.now().strftime('%Y-%m-%d')}.log")

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the overall logging level to DEBUG

# Create a file handler for writing logs to a file
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(file_level)  # Log at the level specified in the config for files

# Create a console handler for printing logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(cmd_level)  # Log at the level specified in the config for console

# Define a log format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example usage
logger.info("Logging initialized successfully.")
logger.debug(f"Logs are saved in {log_filename}")
