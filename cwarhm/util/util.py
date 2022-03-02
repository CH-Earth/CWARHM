import os
import re
from pathlib import Path
from datetime import datetime
import configparser
import argparse
import subprocess
import ast
import logging
import logging.config
logger = logging.getLogger('fileOutput')

'''
This file holds a collection of functions that support reading of control files
making folder structures etc.
'''

def read_summa_workflow_control_file(workflow_control_file,comment_char='#',option_char='|'):
    """Read complete control data from the SUMMAworkflow (https://github.com/CH-Earth/summaWorkflow_public)
       format control file

    :param workflow_control_file: SUMMAworkflow control file path i.e./summaWorkflow_public/0_control_files/control_active.txt
    :type workflow_control_file: string
    :return: dictionary containing all options from the control file
    :rtype: dict
    """    
    control_options = {}
    f = open(workflow_control_file)
    for line in f:
        # First, remove comments:
        if comment_char in line:
            # split on comment char, keep only the part before
            line, comment = line.split(comment_char, 1)
            print(line)
        # Second, find lines with an option=value:
        if option_char in line:
            # split on option char:
            option, value = line.split(option_char, 1)
            # strip spaces:
            option = option.strip()
            value = value.strip()
            # If value is 'default' exchange default value with default path given in comments
            if value=='default':
                # regex the default path from the comment
                pattern = r"([^']*[^'])"
                default_path_in_comment = re.findall(pattern,comment)[-2] #one to last, because of point at the end
                # default path is always of the form root_path/domain_[name]/[last_part_of_path]
                # replace 'root_path' with actual root_path from control
                value = default_path_in_comment.replace('root_path',control_options['root_path'])
                # replace '[name]' with domain name from control file
                value = value.replace('[name]',control_options['domain_name'])
                print('value')
            # store in dictionary:
            control_options[option] = value

    f.close()

    return control_options

def get_summa_workflow_control_setting(workflow_control_file, setting):
    """Read  line item  from the SUMMAworkflow (https://github.com/CH-Earth/summaWorkflow_public)
       format control file.
    Parameters
    ----------
    file : SUMMAworkflow control file path
        i.e./summaWorkflow_public/0_control_files/control_active.txt
    setting : line item of SUMMA workflow control file
        i.e. catchment_shp_name
    Returns
    -------
    substring : configuration setting from control file
        i.e. bow_distributed_elevation_zone.shp
    """

    # Open 'control_active.txt' and ...
    with open(workflow_control_file) as contents:
        for line in contents:
            # ... find the line with the requested setting
            if setting in line:
                break

    # Extract the setting's value
    substring = line.split('|', 1)[1]  # Remove the setting's name (split into 2 based on '|', keep only 2nd part)
    substring = substring.split('#', 1)[0]  # Remove comments, does nothing if no '#' is found
    substring = substring.strip()  # Remove leading and trailing whitespace, tabs, newlines

    # Return this value
    return substring

def start_logger(file_name='log_file'):
    '''This function will create a logs folder and file in the same directory as the main script
        It uses the logger_config.ini to set properties
    Parameters
    ----------
    file_name : str
        optional argument for name to be given to logfile
    Returns
    -------
    logger : logging object
        logger can be called with logger.debug("") etc to log to the console and output file
    '''

    now = datetime.now()
    log_file_name = f'{file_name}_{now.strftime("%Y-%m-%d_%H:%M:%S")}.log'
    working_folder = os.getcwd()

    Path(working_folder,'logs').mkdir(parents=True, exist_ok=True)
    logfile = os.path.join(working_folder,'logs',log_file_name)

    logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)),'logger_config.ini'), defaults={'logfilename':logfile},disable_existing_loggers=False)
    logging.getLogger('matplotlib.font_manager').disabled = True
    logger = logging.getLogger('fileOutput')
    logger.info(f'Log File Generated: {logfile}')

    return logger

def log_subprocess_output(pipe):
    '''Function to log the output from a subprocess call'''
    for line in iter(pipe.readline, b''):  # b'\n'-separated lines
        logging.info('External script logging: %r', line)

def isstrbool(instr):
    """Function to convert True to boolean"""
    if instr == 'True':
        flag = True
    else:
        flag = False
    return flag


def get_git_revision_hash(directory = "") -> str:
    """Function to retrieve and log the git hash
    If no directory is provided, the local git will be used.
    An alternate git repo could also be referenced.
    """
    return subprocess.check_output(['git', 'rev-parse', 'HEAD',f'{directory}']).decode('ascii').strip()
