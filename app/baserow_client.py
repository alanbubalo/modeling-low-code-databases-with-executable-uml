"""Module with a class for easily sending responses to the Baserow"""
import requests

URL = 'https://api.baserow.io'

BR_URL = f"{URL}/api/"

class BaserowClient:
    """A client for managing Baserow operations with requests."""
    def __init__(self):
        self.__token_status__ = None
        self.__access_token__ = None
        self.__refresh_token__ = None
        self.__get_headers__ = None
        self.__post_patch_headers__ = None

    def new_session_email(self, email, password):
        """Create a new session"""
        token_response = self.token_auth(email, password)
        self.__token_status__ = token_response.status_code
        if self.is_token_valid():
            self.__access_token__ = token_response.json()["access_token"]
            self.__refresh_token__ = token_response.json()["refresh_token"]
            self.__get_headers__ = {"Authorization": f"JWT {self.__access_token__}"}
            self.__post_patch_headers__ = {
                **self.__get_headers__,
                "Content-Type": "application/json"
            }

    def new_session_token(self, refresh_token):
        """Create a new session"""
        token_response = self.token_refresh(refresh_token)
        self.__token_status__ = token_response.status_code
        if self.is_token_valid():
            self.__access_token__ = token_response.json()["access_token"]
            self.__refresh_token__ = refresh_token
            self.__get_headers__ = {"Authorization": f"JWT {self.__access_token__}"}
            self.__post_patch_headers__ = {
                **self.__get_headers__,
                "Content-Type": "application/json"
            }

    def is_token_valid(self):
        """Returns `True` if a token status code is 200 otherwise `False`"""
        return self.__token_status__ == 200

    def get_settings(self):
        """Returns a response to settings"""
        return requests.get(f"{BR_URL}settings/", timeout=None)

    def token_auth(self, email: str, password: str):
        """Returns a response to a newly created token authentication for a user"""
        return requests.post(
            f"{BR_URL}user/token-auth/",
            json={"email": email, "password": password},
            timeout=None)

    def token_refresh(self, refresh_token: str):
        """Returns a response of a refreshed token"""
        return requests.post(
            f"{BR_URL}user/token-refresh/",
            json={"refresh_token": refresh_token},
            timeout=None)

    def token_verify(self, refresh_token: str):
        """Returns a response of a token verification"""
        return requests.post(
            f"{BR_URL}user/token-verify/",
            json={"refresh_token": refresh_token},
            timeout=None)

    def list_groups(self):
        """Returns a response to a list of groups"""
        return requests.get(f"{BR_URL}groups/", headers=self.__get_headers__, timeout=None)

    def create_group(self, name: str):
        """Returns a response to a newly created group"""
        return requests.post(
            f"{BR_URL}groups/",
            headers=self.__post_patch_headers__,
            json={"name": name},
            timeout=None)

    def list_all_applications(self):
        """Returns a response to a list of all applications (databases)"""
        return requests.get(f"{BR_URL}applications/", headers=self.__get_headers__, timeout=None)

    def create_application(self, group_id: int, name: str, app_type: str):
        """Returns a response to a newly created application"""
        return requests.post(
            f"{BR_URL}applications/group/{group_id}/",
            headers=self.__post_patch_headers__,
            json={"name": name, "type": app_type},
            timeout=None)

    def get_application(self, application_id: int):
        """Returns a response to a newly created application (database)"""
        return requests.get(
            f"{BR_URL}applications/{application_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def delete_application(self, application_id: int):
        """Returns a response to delete an application (database)"""
        return requests.delete(
            f"{BR_URL}applications/{application_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def list_applications(self, group_id: int):
        """Returns a response to a list of applications (databases) in a given group"""
        return requests.get(
            f"{BR_URL}applications/group/{group_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def list_database_tables(self, database_id: int):
        """Returns a response to a list of tables in a given database"""
        return requests.get(
            f"{BR_URL}database/tables/database/{database_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def get_database_table(self, table_id: int):
        """Return a response to a database table"""
        return requests.get(
            f"{BR_URL}database/tables/{table_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def create_database_table(self, database_id: int, table: object):
        """Returns a response to a newly created table"""
        return requests.post(
            f"{BR_URL}database/tables/database/{database_id}/",
            headers=self.__post_patch_headers__,
            json=table,
            timeout=None)

    def update_database_table(self, table_id: int, name: str):
        """Return a response to a newly updated table"""
        return requests.post(
            f"{BR_URL}database/tables/{table_id}/",
            headers=self.__post_patch_headers__,
            json={"name": name},
            timeout=None)

    def delete_database_table(self, table_id: int):
        """Returns a response to a deleted table"""
        return requests.delete(
            f"{BR_URL}database/table/{table_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def create_database_table_field(self, table_id: int, field: object):
        """Returns a response to a newly created table field"""
        return requests.post(
            f"{BR_URL}database/fields/table/{table_id}/",
            headers=self.__post_patch_headers__,
            json=field,
            timeout=None)

    def get_database_table_field(self, field_id: int):
        """Returns a response to a field found by id"""
        return requests.get(
            f"{BR_URL}database/fields/{field_id}/",
            headers=self.__get_headers__,
            timeout=None)

    def update_database_table_field(self, field_id: int, field: object):
        """Returns a response to an updated field found by id"""
        return requests.patch(
            f"{BR_URL}database/fields/{field_id}/",
            headers=self.__post_patch_headers__,
            json=field,
            timeout=None)

    def list_database_table_fields(self, table_id: int):
        """Returns a response to a list of all fields found in a table"""
        return requests.get(
            f"{BR_URL}database/fields/table/{table_id}/",
            headers=self.__get_headers__,
            timeout=None)

    # ----------------------------------------------------------------
    def get_baserow_id(self, class_id: str) -> int:
        """Get a baserow table id with a class id"""
        return requests.get(
            url=f"http://127.0.0.1:5000/baserow_id/{class_id}",
            headers=self.__get_headers__,
            timeout=None
        ).json()['data']

    def get_uml_id(self, baserow_id: str) -> str:
        """Get a class id from a baserow table id"""
        return requests.get(
            url=f"http://127.0.0.1:5000/uml_id/{baserow_id}",
            headers=self.__get_headers__,
            timeout=None
        ).json()['data']

    def put_id_pair(self, table_id: int, class_id: str):
        """Put a id pair"""
        requests.post(
            url="http://127.0.0.1:5000/id_pairs",
            headers=self.__get_headers__,
            json={
                "uml_model": table_id,
                "baserow": class_id
            },
            timeout=None
        )
