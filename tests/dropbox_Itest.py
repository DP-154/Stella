import os
import random
from pprint import pprint

from transport.data_provider import DropBoxDataProvider

ACS_TOKEN = '***********'
FILE_OVERWRITE = 'o'
FILE_MOVE = 'm'

rand = random.randint(1, 10)
file_name = 'dropbox_t_file' + str(rand) + '.txt'
local_file = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
dbx_file = '/ss_dpb_test/' + file_name
dbx_file_to_move = '/ss_dpb_test_2/' + file_name
dbx_folder = '/ss_dpb_test'


def main():

    dbdp = DropBoxDataProvider(ACS_TOKEN)

    print(file_name)
    list_of_objects = dbdp.get_list_of_objects(dbx_folder)
    pprint(list_of_objects)

    for f in list_of_objects:
        if file_name not in f:
            try:
                dbdp.file_upload(local_file, dbx_file)
            except IOError:
                print('File read error')

        else:
            user_choice = input('The file already exists what you want to do:\n'
                                '- Overwrite - press "O"\n'
                                '- Move - press "M"\n'
                                '-->')

            if str(user_choice).lower().isalpha():
                if user_choice in FILE_OVERWRITE and user_choice not in FILE_MOVE:
                    dbdp.file_upload(local_file, dbx_file)
                    break
                elif user_choice in FILE_MOVE and user_choice not in FILE_OVERWRITE:
                    dbdp.file_move(dbx_file, dbx_file_to_move)
                    break
                else:
                    print('You decide to make the wrong choice and the files will be deleted.')
                    dbdp.file_delete(dbx_file)
                    break


if __name__ == '__main__':
    main()
