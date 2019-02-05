import os
import random
from pprint import pprint

from transport.data_provider import DropBoxDataProvider

ACS_TOKEN = '******'

rand = random.randint(1, 10)
file_name = 'dropbox_t_file' + str(rand) + '.txt'
local_file = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
dbx_file = '/ss_dpb_test/' + file_name
dbx_file_to_move = '/ss_dpb_test_2/' + file_name


def main():

    dbdp = DropBoxDataProvider(ACS_TOKEN)

    print(file_name)
    list_of_objects = dbdp.get_list_of_objects()
    pprint(list_of_objects)

    for f in list_of_objects:

        if file_name not in f:
            dbdp.file_upload(local_file, dbx_file)

        else:
            print('file exist')
            dbdp.file_delete(dbx_file)
            break


if __name__ == '__main__':

    main()