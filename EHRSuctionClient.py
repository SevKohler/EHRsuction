import requests
import os
from Variables import ExportType, Platforms
import psutil
import gc
from logger_config import logger
class EHRSuctionClient:
    def __init__(self, url, auth, platform, fileHandler, steps):
        self.auth = auth
        self.base_url = url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.platform = platform
        if platform == Platforms.EHRBASE:
            self.base_url = url + "/ehrbase/rest/openehr/v1"
            self.query_endpoint = self.base_url + "/query/aql"
            self.view_endpoint = self.base_url + "????" # change if you have a different view
        elif platform == Platforms.BETTER:
            self.base_url = url + "/rest/openehr/v1"
            self.better_url = url + "/rest/v1"
            self.query_endpoint = self.base_url + "/query/aql"
            self.view_endpoint = self.better_url + "/view/export::Flat_compositions_ehr" # change if you have a different view
        self.steps = steps
        self.offset = 0
        self.limit = self.steps
        self.fileHandler = fileHandler
        self.composition_types_amount = {}
        self.params = {'limit': self.limit, 'offset': self.offset, 'ehr': '0'}
        self.session = self.set_session()

    def set_session(self):
        session = requests.Session()
        session.proxies = {}  #proxy off ------------------ DELETE IF PROXY necessary
        session.trust_env = False #proxy off -------------- DELETE IF PROXY necessary
        session.auth = self.auth
        session.headers.update(self.headers)
        return session

    def check_connection(self):
        response = self.session.get(self.base_url+ "/definition/template/adl1.4", verify=False)
        if response.status_code == 200:
            logger.info('========Connection successful to openEHR platform ========="')
            return True
        else:
            logger.error("Connection error:" + str(response.content) + "retry !")
            return False

    def generate_control_number_ehrs(self):
        response = self.session.post(
            self.query_endpoint,
            headers=self.headers,
            json={"q": "SELECT COUNT(e) FROM EHR e"},
            auth=self.auth,
            verify=False  # This disables SSL verification
        )

        if response.status_code == 200:
            self.control_ehrs = response.json()['resultSet'][0]['#0']
        elif response.status_code == 204:
            logger.warning("Repository is empty, no EHRs found")
        else:
            logger.error(f"Query failed with status code {response.status_code}")

    def generate_control_number_compositions(self):
        response = self.session.post(
            self.query_endpoint,
            headers=self.headers,
            json={"q": "SELECT COUNT(c) FROM EHR e CONTAINS COMPOSITION c"},
            auth=self.auth,
            verify=False  # This disables SSL verification
        )

        if response.status_code == 200:
            self.control_compositions = response.json()['resultSet'][0]['#0']
        elif response.status_code == 204:
            logger.info("Repository is empty, no compositions found")
        else:
            logger.error(f"Query failed with status code {response.status_code}")
            logger.error(response.text)

    def suction(self, exportType):
        self.check_connection()
        self.create_all_ehr_folders()
        if exportType == ExportType.CANONICAL:
            self.asd() # should use here class overload ...
        if exportType == ExportType.FLAT:
            self.export_query_flat()
        self.session.close()

    def create_all_ehr_folders(self):
        aql = "SELECT e/ehr_id/value FROM EHR e"
        if self.platform == Platforms.EHRBASE:
            aql =  aql + " ORDER BY e/ehr_id/value" # bad performance but does not support time_created yet
        else:
            aql =  aql + " ORDER BY e/time_created/value" # bad performance but does not support time_created yet
        self.session
        response = self.session.post(
            self.query_endpoint,
            headers=self.headers,
            json={"q": aql},
            auth=self.auth,
            verify=False  # This disables SSL verification
        )
        if response.status_code == 200:
            logger.info("Query was successful.")
            self.process_ehr_ids(response.json())
        else:
            logger.error(f"Query failed with status code {response.status_code}")
            logger.error(response.text)

    def process_ehr_ids(self, response):
        for item in response.get("rows"):
            self.fileHandler.write_ehr_folder(item[0])

    def asd(self):
        count = 0
        for ehr_id in self.fileHandler.get_ehr_id_list():
            count = count +1
            logger.info(f"=== Processing data from EHR {ehr_id}")
            logger.info(f"=== EHR {count} of {len(self.fileHandler.get_ehr_id_list())}")
            self.export_query_canonical(ehr_id, self.limit, self.offset)

    def export_query_canonical(self,ehr_id, limit, offset):
        count = 0
        while True: # changed to loop to save memory from recursion
            aql = (
                "SELECT e/ehr_id/value, c FROM EHR e CONTAINS Composition c "
                "WHERE e/ehr_id/value = '{}' "
                "ORDER BY c/context/start_time/value LIMIT {} OFFSET {}"
            ).format(ehr_id, limit, offset)
            response = self.session.post(
                self.query_endpoint,
                headers=self.headers,
                json={"q": aql},
                auth=self.auth,
                verify=False  # Disables SSL verification
            )
            logger.info(f"Memory usage: {psutil.virtual_memory().percent}%")

            if response.status_code == 200:
                logger.info("Query was successful.")
                self.process_response_query(response.json())
                offset += self.steps  # Move offset forward
                gc.collect()  # Explicit garbage collection
                if self.check_rows_empty(response):
                    break
            elif response.status_code == 204:
                logger.info("Finished.")
                self.actual_ehrs = len(self.fileHandler.get_ehr_id_list())
                self.actual_compositions = len(self.fileHandler.get_composition_uid_list())
                logger.info(f"Created ehr_id folders: {self.actual_ehrs}")
                logger.info(f"Composition types: {self.composition_types_amount}")
                logger.info(f"Saved jsons: {self.actual_compositions}")
                self.check_everything_saved(self.actual_ehrs, self.actual_compositions)
                break  # Stop the loop when finished
            else:
                logger.info(f"Query failed with status code {response.status_code}")
                logger.info(response.text)
                break  # Avoid infinite loop on failure

    def check_everything_saved(self, actual_ehrs, actual_compositions):
        self.generate_control_number_compositions()
        self.generate_control_number_ehrs()
        if actual_ehrs != self.control_ehrs:
            logger.error("The amount of ehrs downloaded does not match the counted ehrs on the server!")
            logger.error(f"Amount of downloaded ehrs: {actual_ehrs}, expected: {self.control_ehrs}")
            logger.error("Check the script or server settings")
        if actual_compositions != self.control_compositions:
            logger.error("The amount of compositions downloaded does not match the counted compositions on the server!")
            logger.error(f"Amount of downloaded compositions: {actual_compositions}, expected: {self.control_compositions}")
            logger.error("Check the script or server settings")

    def process_response_query(self, response):
        if self.platform == Platforms.EHRBASE:
            for item in response.get("rows"):
                ehr_folder = os.path.join(self.fileHandler.get_output_folder(), item[0])  # Use first element as folder name
                self.fileHandler.write_composition(
                    item[1].get("uid", {}).get("value"),  # Extract UID value
                    item[1],  # Pass the full dictionary
                    ehr_folder
                )
                composition_type = item[1].get("name", {}).get("value")
                self.composition_types_amount_count(composition_type)

        if self.platform == Platforms.BETTER:
            for ehr_id, composition in response.get("rows", []):
                ehr_folder = os.path.join(self.fileHandler.get_output_folder(), ehr_id)  # Use EHR ID as folder name
                # Extract composition UID safely
                composition_uid = composition.get("uid", {}).get("value")
                # Write composition data
                self.fileHandler.write_composition(composition_uid, composition, ehr_folder)
                # Extract and count composition type
                composition_type = composition.get("name", {}).get("value")
                self.composition_types_amount_count(composition_type)

    def export_query_flat(self):
        count = 0
        for ehr_id in self.fileHandler.get_ehr_id_list():
            count = count +1
            logger.info(f"=== Processing data from EHR {ehr_id}")
            logger.info(f"=== EHR {count} of {len(self.fileHandler.get_ehr_id_list())}")
            self.request_view(ehr_id, self.offset, self.limit)
        logger.info("Finished.")
        logger.info("Created ehr_id folders: ", len(self.fileHandler.get_ehr_id_list()))
        logger.info("Composition types: ", self.composition_types_amount)
        logger.info("Saved jsons: ", len(self.fileHandler.get_composition_uid_list()))

    def request_view(self, ehr_id, offset, limit):
        self.params["ehr"] = ehr_id
        self.params["limit"] = limit
        self.params["offset"] = offset
        logger.info(f"Memory usage: {psutil.virtual_memory().percent}%")

        while True:  # Use a loop instead of recursion due to Memory problems otherwise
            response = self.session.post(
                self.view_endpoint,
                headers=self.headers,
                params=self.params,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                logger.info(f"Query successful for EHR {ehr_id} at offset {offset}")
                data = response.json()
                if not data:  # If response is empty, stop processing
                    logger.info(f"No more data for EHR {ehr_id}. Stopping.")
                    break  # Exit the loop
                self.process_flat_data(response.json(), os.path.join(self.fileHandler.get_output_folder(), ehr_id))
                # Update offset for next iteration
                offset += self.steps
                self.params["offset"] = offset
            else:
                logger.error(f"Query failed with status code {response.status_code}: {response.text}")
                break  # Stop retrying on failure

        # Reset offset & limit for next EHR
        self.offset = 0
        self.limit = self.steps


    def process_flat_data(self, response, ehr_folder):
        for item in response:
            for flat_path, value in item.items():
                if flat_path.endswith('/_uid'):
                    self.fileHandler.write_composition(value, item, ehr_folder)
                    composition_type = flat_path.split('/_uid')[0]
                    self.composition_types_amount_count(composition_type)

    def composition_types_amount_count(self, composition_type):
        if composition_type not in self.composition_types_amount:
            self.composition_types_amount[composition_type] = 0
        else:
            self.composition_types_amount[composition_type] = self.composition_types_amount[composition_type] + 1

    def check_rows_empty(self, response):
        if self.platform == Platforms.EHRBASE:
            if not response.json()['rows']:
                return True
        if self.platform == Platforms.BETTER:
            if not response.json.get("rows"):
                return True
        return False
