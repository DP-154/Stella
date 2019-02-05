import dropbox

from dropbox.exceptions import ApiError

from collections import namedtuple


class DropBoxDataProvider:

    def __init__(self, acs_token):
        self.dbx = dropbox.Dropbox(acs_token)

    def get_list_of_objects(self, dbx_folder='') -> list:
        result = namedtuple('Result', ['filename', 'filepatch'])
        try:
            return [result(el.name, el.path_lower) for el in self.dbx.files_list_folder(dbx_folder).entries]
        except ApiError:
            return []

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
