import os
import json
from logger_config import logger
from Variables import ExportType


class FileHandler:
    def __init__(self, exportFormat, output_folder):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_folder_canonical = os.path.join(output_folder, "output_canonical")
        self.output_folder_flat = os.path.join(output_folder, "output_flat")
        self.ehr_id_list = {}
        self.composition_uid_list = {}
        self.composition_types_amount = {}

        if exportFormat == ExportType.CANONICAL:
            self.output_folder = self.output_folder_canonical

        if exportFormat == ExportType.FLAT:
            self.output_folder = self.output_folder_flat

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def register_already_downloaded_files(self):
        self.register_existing_folders()
        self.register_existing_compositions()

    def register_existing_folders(self):
        for item in os.listdir(self.output_folder):
            # exclude .venv etc.
            if not item.startswith("."):
                ehr_id_folder = os.path.join(self.output_folder, item)
                if os.path.isdir(ehr_id_folder):
                    if ehr_id_folder not in self.ehr_id_list:
                        logger.debug("=== Old folder discovered adding EHR id =====" + item)
                        self.ehr_id_list[item] = ""

    def register_existing_compositions(self):
        for root, dirs, files in os.walk(self.output_folder):
            for file in files:
                if file not in self.composition_uid_list:
                    file = file[:-5]  # remove .json
                    logger.debug("=== Old file discovered adding Composition uid =====" + file)
                    self.composition_uid_list[file] = ""

    def write_composition(self, composition_uid, composition, ehr_folder):
        if composition_uid not in self.composition_uid_list:
            composition_file_path = os.path.join(ehr_folder, composition_uid + ".json")
            with open(composition_file_path, 'w') as fp:
                json.dump(composition, fp)
                logger.debug("New file created for Composition " + composition_file_path)
            self.composition_uid_list[composition_uid] = 'foobar'
        else:
            logger.debug("File "+composition_uid+ ".json"+" already existed.")

    def write_ehr_folder(self, ehr_id_value):
        if ehr_id_value not in self.ehr_id_list:
            ehr_folder = os.path.join(self.output_folder, ehr_id_value)
            os.makedirs(ehr_folder)
            logger.debug("New folder created for EHR " + ehr_folder)
            self.ehr_id_list[ehr_id_value] = 'foobar'
            return ehr_folder
        else:
            return os.path.join(self.output_folder, ehr_id_value)

    def get_composition_uid_list(self):
        return self.composition_uid_list

    def get_ehr_id_list(self):
        return self.ehr_id_list

    def get_output_folder(self):
        return self.output_folder