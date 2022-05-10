import os

from pathlib import Path
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cwarhm.util.util as utl

control_file = '../dependencies/cwarhm-summa/0_control_files/control_Bow_at_Banff.txt'
control_dict = utl.read_summa_workflow_control_file(control_file,comment_char='#',option_char='|')
print(control_dict)