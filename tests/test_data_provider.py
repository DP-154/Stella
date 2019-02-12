import os
from unittest.mock import patch, Mock, PropertyMock

import pytest
from dropbox.files import DeleteResult, FileMetadata, RelocationResult

import tests.required_data as con

from transport.data_provider import DropBoxDataProvider
#from asc_token import ACS_TOKEN

ACS_TOKEN = '****'

#dbdp = DropBoxDataProvider(ACS_TOKEN)


@pytest.fixture()
def my_setup(request):
    path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
    os.makedirs(path)

    for i in range(11):
        file_name_create = 'dropbox_t_file' + str(i) + '.txt'
        file_from = path + file_name_create
        with open(file_from, 'w') as f:
            f.write(str(i))

    def my_teardown():
        path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
        for i in range(11):
            file_name = 'dropbox_t_file' + str(i) + '.txt'
            file_from = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
            os.remove(file_from)
        os.rmdir(path)

    request.addfinalizer(my_teardown)


@pytest.mark.usefixtures("my_setup")
@patch('transport.data_provider.dropbox')
class TestDataProvider:

    @classmethod
    def setup_class(cls):
        dbdp = DropBoxDataProvider(ACS_TOKEN)
        return dbdp

    @classmethod
    def teardown_class(cls):
        pass

    @patch(
        'transport.data_provider.DataProviderBase.make_get_request',
        new=Mock(return_value=Mock(status_code=200, text='Ok')),
    )
    def test_smoke_positive(self):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        assert dbdp.smoke()[0] == 200
        assert dbdp.smoke()[1] == 'Ok'

    @pytest.mark.xfail(raises=ValueError)
    def test_smoke_missed_url(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        dbdp.smoke_url = None
        dbdp.smoke()

    def test_api_smoke_positive(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        dbdp.dbx = Mock()
        dbdp.api_smoke()

    @pytest.mark.xfail(raises=Exception)
    def test_api_smoke_negative(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        dbdp.dbx.files_list_folder = Mock(return_value=Mock(entries=None))
        dbdp.api_smoke()

    def test_empty_get_list_of_objects_success(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        dbx_empty_folder = '/ss_dpb_test_empty_folder'
        assert isinstance(dbdp.get_list_of_objects(dbx_empty_folder), list)

    def test_not_empty_get_list_of_objects_success(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        dummy_file_object = Mock(path_lower='/ss_dpb_test_not_empty_folder/dropbox_t_file.txt')
        n = PropertyMock(return_value='dropbox_t_file.txt')
        type(dummy_file_object).name = n

        dbdp.dbx.files_list_folder = Mock(return_value=Mock(entries=tuple([dummy_file_object])))
        list_of_objects = dbdp.get_list_of_objects()

        assert isinstance(list_of_objects, list)
        assert isinstance(list_of_objects[0], tuple)
        assert list_of_objects[0].filename == 'dropbox_t_file.txt'
        assert list_of_objects[0].filepatch == '/ss_dpb_test_not_empty_folder/dropbox_t_file.txt'

    @pytest.mark.xfail(raises=FileNotFoundError)
    def test_file_upload_failed_file_not_found(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
        dbdp.file_upload(wrong_local_file, con.dbx_file)

    def test_file_upload_success(self, my_setup):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        res = dbdp.file_upload(con.local_file, con.dbx_file)
        exp = con.dbx_file
        assert res == exp

    def test_file_move_success(self):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        res = dbdp.file_move(con.dbx_file, con.dbx_file_to_move)
        exp = con.dbx_file_to_move
        assert res == exp

    def test_file_move_failed(self):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        assert dbdp.file_move(con.dbx_no_file, con.dbx_file_to_move) is None

    def test_file_download_success(self, my_setup):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        res = dbdp.file_download(con.local_file, con.dbx_file)
        exp = FileMetadata(con.dbx_file).name
        assert res == exp

    @pytest.mark.xfail(raises=FileNotFoundError)
    def test_file_download_file_not_found_failed(self):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
        dbdp.file_download(wrong_local_file, con.dbx_file)

    def test_file_download_file_None_failed(self, my_setup):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        assert dbdp.file_download(con.local_file, con.dbx_file_empty) is None

    def test_file_delete_success(self):
        #dbdp = DropBoxDataProvider(ACS_TOKEN)
        res = dbdp.file_delete(con.dbx_file)
        exp = FileMetadata(con.dbx_file).name
        assert res == exp

    def test_file_delete_failed(self, my_setup):
        # dbdp = DropBoxDataProvider(ACS_TOKEN)
        assert dbdp.file_delete(con.dbx_file_empty) is None
