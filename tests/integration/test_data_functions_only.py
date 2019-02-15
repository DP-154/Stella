import os
from unittest.mock import patch, Mock, PropertyMock

import pytest

import tests.integration.required_data as con
from transport.data_provider import DropBoxDataProvider


ACS_TOKEN = os.environ['DROPBOX_TOKEN']


@pytest.fixture(scope='function')
def my_setup(request):
    path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
    os.makedirs(path)
    dbdp = DropBoxDataProvider(ACS_TOKEN)

    with open(con.local_file, 'w') as f:
        f.write(str(con.rand))

    dbdp.file_upload(con.local_file, con.dbx_file)
    dbdp.create_folder(con.dbx_empty_folder)
    dbdp.file_upload(con.local_file, con.dbx_not_empty_folder_file)

    def my_teardown():
        path = os.path.join(os.path.dirname(__file__), 'dpb_download/')
        file_from = os.path.join(os.path.dirname(__file__), 'dpb_download/' + con.file_name)
        os.remove(file_from)
        os.rmdir(path)
        dbdp.file_delete(con.dbx_folder)
        dbdp.file_delete(con.dbx_empty_folder)
        dbdp.file_delete(con.dbx_folder_file_to_move)
        dbdp.file_delete(con.dbx_not_empty_folder)

    request.addfinalizer(my_teardown)


@pytest.mark.xfail(raises=ValueError)
def test_smoke_missed_url():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    dbdp.smoke_url = None
    dbdp.smoke()


@patch('transport.data_provider.DataProviderBase.make_get_request',
       new=Mock(return_value=Mock(status_code=200, text='Ok')), )
def test_smoke_positive():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    assert dbdp.smoke()[0] == 200
    assert dbdp.smoke()[1] == 'Ok'


def test_api_smoke_positive():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    res = dbdp.api_smoke()
    exp = 1
    assert res == exp


@pytest.mark.xfail(raises=Exception)
def test_api_smoke_negative():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    dbdp.dbx.files_list_folder = Mock(return_value=Mock(entries=None))
    dbdp.api_smoke()


def test_empty_get_list_of_objects_success(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    assert isinstance(dbdp.get_list_of_objects(con.dbx_empty_folder), list)


def test_not_empty_get_list_of_objects_success():
    dbdp = DropBoxDataProvider(ACS_TOKEN)

    dummy_file_object = Mock(path_lower='/ss_dpb_test_not_empty_folder/dropbox_t_file.txt')
    n = PropertyMock(return_value='dropbox_t_file.txt')
    type(dummy_file_object).name = n

    dbdp.dbx.files_list_folder = Mock(return_value=Mock(entries=tuple([dummy_file_object])))
    list_of_objects = dbdp.get_list_of_objects()

    assert isinstance(list_of_objects, list)
    assert isinstance(list_of_objects[0], tuple)
    assert list_of_objects[0].filename == 'dropbox_t_file.txt'
    assert list_of_objects[0].filepatch == '/ss_dpb_test_not_empty_folder/dropbox_t_file.txt'


def test_file_download_success(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    res = dbdp.file_download(con.local_file, con.dbx_file)
    exp = str(con.dbx_file)
    assert res == exp


@pytest.mark.xfail(raises=FileNotFoundError)
def test_file_download_file_not_found_failed():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
    dbdp.file_download(wrong_local_file, con.dbx_file)


def test_file_move_success(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    res = dbdp.file_move(con.dbx_file, con.dbx_file_to_move)
    exp = str(con.dbx_file_to_move)

    assert res == exp


def test_file_move_failed(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    assert dbdp.file_move(con.dbx_no_file, con.dbx_file_to_move) is None


def test_file_download_file_None_failed(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    assert dbdp.file_download(con.local_file, con.dbx_file_empty) is None


@pytest.mark.xfail(raises=FileNotFoundError)
def test_file_upload_failed_file_not_found():
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    wrong_local_file = os.path.join(os.path.dirname(__file__), 'dpb_downloa/' + con.file_name)
    dbdp.file_upload(wrong_local_file, con.dbx_file)


def test_file_upload_success(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    res = dbdp.file_upload(con.local_file, con.dbx_file)
    exp = str(con.dbx_file)
    assert res == exp


def test_file_delete_success(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    res = dbdp.file_delete(con.dbx_file)
    exp = con.dbx_file
    assert res == exp


def test_file_delete_failed(my_setup):
    dbdp = DropBoxDataProvider(ACS_TOKEN)
    assert dbdp.file_delete(con.dbx_file_empty) is None
