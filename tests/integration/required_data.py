import os
import random


rand = random.randint(1, 10)
file_name = 'dropbox_t_file' + str(rand) + '.txt'
local_file = os.path.join(os.path.dirname(__file__), 'dpb_download/' + file_name)
dbx_file = '/ss_dpb_test/' + file_name
dbx_folder_file_to_move = '/ss_dpb_test_2'
dbx_file_to_move = '/ss_dpb_test_2/' + file_name
dbx_folder = '/ss_dpb_test'
dbx_empty_folder = '/ss_dpb_test_empty_folder'
dbx_file_empty = '/ss_dpb_test_empty_folder/' + file_name
dbx_not_empty_folder = '/ss_dpb_test_not_empty_folder'
dbx_not_empty_folder_file = '/ss_dpb_test_not_empty_folder/' + file_name
dbx_no_file = '/ss_dpb_test/1'




