import dropbox

from dropbox.exceptions import ApiError

import requests

from collections import namedtuple

class DataProviderBase:
    smoke_url = None

    @staticmethod
    def make_get_request(url) -> requests.Response:
        r = requests.get(url)
        r.raise_for_status()
        return r

    def smoke(self) -> tuple:
        if not self.smoke_url:
            raise ValueError('You have to specify URL for smoke testing')
        result = self.make_get_request(self.smoke_url)
        return result.status_code, result.text

    def api_smoke(self):
        raise NotImplementedError


class DropBoxDataProvider(DataProviderBase):
    smoke_url = 'https://dropbox.com'

    def __init__(self, acs_token):
        self.dbx = dropbox.Dropbox(acs_token)

    def api_smoke(self) -> None:
        if not self.dbx.files_list_folder('').entries:
            raise Exception('There are no files in your Dropbox account')

    def get_list_of_objects(self, dbx_folder='') -> list:
        result = namedtuple('Result', ['filename', 'filepatch'])
        try:
            return [result(el.name, el.path_lower) for el in self.dbx.files_list_folder(dbx_folder).entries]
        except ApiError:
            return None

    def file_delete(self, dbx_file) -> bool:
        try:
            self.dbx.files_delete_v2(dbx_file)
        except ApiError:
            return False
        return True

    def file_download(self, local_file, dbx_file) -> bool:
        try:
            self.dbx.files_download_to_file(local_file, dbx_file)
        except ApiError:
            return False
        return True

    def file_upload(self, local_file, dbx_file) -> bool:
        with open(local_file, 'rb') as f:
            try:
                self.dbx.files_upload(f.read(), dbx_file)
            except ApiError:
                return False
        return True

    def file_move(self, dbx_file_from, dbx_file_to) -> bool:
        try:
            self.dbx.files_move_v2(dbx_file_from, dbx_file_to)
        except ApiError:
            return False
        return True
