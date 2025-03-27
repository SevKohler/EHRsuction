from requests.auth import HTTPBasicAuth
import FileHandler as fh
import EHRSuctionClient as oc
from Variables import ExportType, Platforms

#========= CONFIG=========
base_url = "base_url" # base_url of platform, script will add the rest for ehrbase and better
output_folder = "/home/USER/Downloads/" # folder you want to export to
platform = Platforms.BETTER # Better
exportType = ExportType.CANONICAL # flat
steps = 10000 # bulk export steps
auth=HTTPBasicAuth('username', 'password')
#========= CONFIG=========


def main():
	# check if output folder already exists change if you want flat to EXPO
	file_handler = fh.FileHandler(exportType, output_folder + "EHR_export/")
	file_handler.register_already_downloaded_files()
	ehr_suction_client = oc.EHRSuctionClient(base_url, auth, platform, file_handler, steps)
	ehr_suction_client.suction(exportType)

if __name__ == "__main__":
	main()
