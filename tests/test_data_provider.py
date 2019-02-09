import os
from collections import namedtuple
from unittest.mock import patch, Mock

import pytest

import tests.constants as con
from tests.constants import dbdp


@patch('transport.data_provider.dropbox')
class TestDataProvider:

    @patch(
        'transport.data_provider.DataProviderBase.make_get_request',
        new=Mock(return_value=Mock(status_code=200, text='Ok')),
    )
    def setup_class(cls):
        path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
        os.makedirs(path)

        for i in range(11):
            file_name_create = 'dropbox_t_file' + str(i) + '.txt'
            file_from = path + file_name_create
            with open(file_from, 'w') as f:
                f.write(str(i))

    def teardown_class(cls):
        path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
        for i in range(11):
            file_name = 'dropbox_t_file' + str(i) + '.txt'
            file_from = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
            os.remove(file_from)
        os.rmdir(path)

    def test_smoke_positive(self):
        assert dbdp.smoke()[0] == 200
        assert dbdp.smoke()[1] == 'Ok'

    @pytest.mark.xfail(raises=ValueError)
    def test_smoke_missed_url(self):
        dbdp.smoke_url = None
        dbdp.smoke()

    def test_api_smoke_positive(self):
        dbdp.dbx = Mock()
        dbdp.api_smoke()

    @pytest.mark.xfail(raises=Exception)
    def test_api_smoke_negative(self):
        dbdp.dbx.files_list_folder = Mock(return_value=Mock(entries=None))
        dbdp.api_smoke()

    def test_get_list_of_objects_wrong_folder(self):
        dbx_empty_folder = '/ss_dpb_test_empty_folder'
        assert dbdp.get_list_of_objects(dbx_empty_folder) == None

    def test_empty_get_list_of_objects_success(self):
        dbx_empty_folder = '/ss_dpb_test_empty_folder'
        assert isinstance(dbdp.get_list_of_objects(dbx_empty_folder), list)

    def test_not_empty_get_list_of_objects_success(self):
        dbx_not_empty_folder = '/ss_dpb_test_not_empty_folder/dropbox_t_file.txt'
        result = namedtuple('Result', [con.file_name, dbx_not_empty_folder])
        assert dbdp.get_list_of_objects(dbx_not_empty_folder) == result

    @pytest.mark.xfail(raises=FileNotFoundError)
    def test_file_upload_failed_file_not_found(self):
        wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
        dbdp.file_upload(wrong_local_file, con.dbx_file)

    def test_file_upload_success(self):
        assert dbdp.file_upload(con.local_file, con.dbx_file) == con.dbx_file

    def test_file_move_success(self):
        assert dbdp.file_move(con.dbx_file, con.dbx_file_to_move) == con.dbx_file_to_move

    def test_file_move_failed(self):
        dbx_no_file = '/ss_dpb_test/1'
        assert dbdp.file_move(dbx_no_file, con.dbx_file_to_move) == None

    def test_file_download_success(self):
        assert dbdp.file_download(con.local_file, con.dbx_file) == con.dbx_file

    @pytest.mark.xfail(raises=FileNotFoundError)
    def test_file_download_file_not_found_failed(self):
        wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
        dbdp.file_download(wrong_local_file, con.dbx_file)

    def test_file_download_file_None_failed(self):
        assert dbdp.file_download(con.local_file, con.dbx_file) is None

    def test_file_delete_success(self):
        assert dbdp.file_delete(con.dbx_file) == con.dbx_file

    def test_file_delete_failed(self):
        assert dbdp.file_delete(con.dbx_file) == None
