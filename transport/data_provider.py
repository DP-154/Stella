from collections import namedtuple
from time import sleep

import requests
from dropbox import Dropbox
from dropbox.exceptions import ApiError

DROPBOX_SMOKE_URL = 'https://dropbox.com'


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


def _error_handler(f):
    def wrapper(*args):
        try:
            return f(*args)
        except ApiError:
            return None

    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


@for_all_methods(_error_handler)
class DropBoxDataProvider(DataProviderBase):
    smoke_url = DROPBOX_SMOKE_URL

    def __init__(self, acs_token):
        self.dbx = Dropbox(acs_token)

    def api_smoke(self) -> int:
        return len(self.dbx.files_list_folder('').entries)

    def get_list_of_objects(self, dbx_folder='') -> list:
        result = namedtuple('Result', ['filename', 'filepatch'])
        return [result(el.name, el.path_lower) for el in self.dbx.files_list_folder(dbx_folder).entries]

    def file_delete(self, dbx_file) -> str:
        return self.dbx.files_delete_v2(dbx_file).metadata.path_lower

    def file_download(self, local_file, dbx_file) -> str:
        return self.dbx.files_download_to_file(local_file, dbx_file).path_lower

    def file_upload(self, local_file, dbx_file) -> str:
        if isinstance(local_file, str):
            if local_file.startswith("https://"):
                waiting_time = 3
                waiting_attempt = 60
                url_result = self.dbx.files_save_url(dbx_file, local_file)
                job_id = url_result.get_async_job_id()
                while waiting_attempt > 0:
                    st = self.dbx.files_save_url_check_job_status(job_id)
                    if st.is_complete():
                        return st.get_complete().path_lower
                    sleep(waiting_time)
                    waiting_attempt -= 1
            else:
                with open(local_file, 'rb') as f:
                    return self.dbx.files_upload(f.read(), dbx_file, autorename=True).path_lower
        else:
            return self.dbx.files_upload(local_file.read(), dbx_file, autorename=True).path_lower

    def file_move(self, dbx_file_from, dbx_file_to) -> str:
        return self.dbx.files_move_v2(dbx_file_from, dbx_file_to).metadata.path_lower

    def create_folder(self, dbx_folder) -> str:
        return self.dbx.files_create_folder_v2(dbx_folder).metadata.path_lower

    def get_file_tmp_link(self, dbx_path) -> str:
        return self.dbx.files_get_temporary_link(dbx_path).link
