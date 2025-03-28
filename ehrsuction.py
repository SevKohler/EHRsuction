from requests.auth import HTTPBasicAuth
import FileHandler as fh
import EHRSuctionClient as oc
from Variables import ExportType, Platforms
import yaml


def main():
	with open("config.yaml", "r") as file:
		config = yaml.safe_load(file)
	# Assign values from config
	base_url = config["base_url"]
	output_folder = config["output_folder"]
	platform = Platforms[config["platform"].upper()]  # Convert string to Platforms Enum
	exportType = ExportType[config["export_type"].upper()]  # Convert string to ExportType Enum
	steps = config["steps"]
	auth = HTTPBasicAuth(config["auth"]["username"], config["auth"]["password"])

	# check if output folder already exists change if you want flat to EXPO
	file_handler = fh.FileHandler(exportType, output_folder + "EHR_export/")
	file_handler.register_already_downloaded_files()
	ehr_suction_client = oc.EHRSuctionClient(base_url, auth, platform, file_handler, steps)
	ehr_suction_client.suction(exportType)

if __name__ == "__main__":
	main()
