import os
import random
from transport.data_provider import DropBoxDataProvider

ACS_TOKEN = '******'

dbdp = DropBoxDataProvider(ACS_TOKEN)

rand = random.randint(1, 10)
file_name = 'dropbox_t_file' + str(rand) + '.txt'
local_file = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
dbx_file = '/ss_dpb_test/' + file_name
dbx_file_to_move = '/ss_dpb_test_2/' + file_name
dbx_folder = '/ss_dpb_test'


