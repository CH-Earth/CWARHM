'''Extracts the timing of simulation components from individual log files and plots these as boxplots.
Summary figure is placed inside the log folder. Specifying a summary figure name is optional.
Usage: python SUMMA_plot_computational_times.py [log_folder] [name_of_summary_fig.png] [log file extension]'''

# Modules
import os
import re
import sys
import numpy as np
import statistics as sts
import matplotlib.pyplot as plt

# ----------------------
# Set defaults
summaryFig = '_log_times.png' # default, placed at the top of the log folder
ext = '.txt' 

# Handle input arguments
if len(sys.argv) == 1: # sys.argv only contains the script name
    sys.exit('Error: no input folder specified')
    
    
else: # at least 2 elements in sys.argv; len(sys.argv) cannot be zero or we wouldn't be in this script

    # The first input argument specifies the folder where the log files are 
    folder = sys.argv[1] # sys.argv values are strings by default so this is fine
    
    # Check if there are more arguments
    if len(sys.argv) == 3:
        
        # Assume the second argument is the name for the log file
        summaryFig = sys.argv[2] # string
    
    # No extra argument so no summary file name is specified
    elif len(sys.argv) == 4: 
        
        # Assume the second argument is the name for the log file and the third is the file extension
        summaryFig = sys.argv[2] # string
        ext = sys.argv[3] # string        

# End of input arguments
# ----------------------

# -------------   
# Sub functions

# Define a function to grab the last line in a file
# See: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail
def tail(folder, file, lines=1, _buffer=4098):
        
    """Tail a file and get X lines from the end"""
    
    # open the file
    with open(folder + '/' + file,'r') as f: 
    
        # place holder for the lines found
        lines_found = []

        # block counter will be multiplied by buffer to get the block size from the end
        block_counter = -1

        # loop until we find X lines
        while len(lines_found) < lines:
            try:
                f.seek(block_counter * _buffer, os.SEEK_END)
            except IOError:  # either file is too small, or too many lines requested
                f.seek(0)
                lines_found = f.readlines()
                break

            lines_found = f.readlines()

            # decrement the block counter to get the next X bytes
            block_counter -= 1

    return lines_found[-lines:]
    
# Function to grab the 7 different timing values from a SUMMA log file
def get_computation_time(file,nLines=30):
    
    # get the file contents
    log_txt = tail(folder,file,nLines)
    
    # only proceed if simulation was successful
    success = False
    nSkipped = 0
    for line in log_txt:                
        if 'successfully' in line:
            success = True
    if not success:
        print(f'{file} does not appear to log a successful SUMMA run. Skipping.')
        nSkipped += 1
        return
    
    # initialize the return values. Negative values allows for filtering outside this function if needed
    total = physics = write = read = restart = setup = init = -1
    
    # loop over the lines and act according to what's found in the line
    for line in log_txt:
        if 'elapsed time' in line:
            total = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed physics' in line:
            physics = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed write' in line:
            write = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed read' in line:
            read = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed restart' in line:
            restart = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed setup' in line:
            setup = float(re.sub("[^\d\.]", "", line))
        elif 'elapsed init' in line:
            init = float(re.sub("[^\d\.]", "", line))
        
    return total,physics,write,read,restart,setup,init,nSkipped

# End of sub functions
# --------------------

# -------------------
# Start of processing

# Remove the summar file if it exists
try:
    os.remove(folder + '/' + summaryFile)
except OSError:
    pass
    
# Find the .txt files in the folder
files = []
for file in os.listdir(folder):
    if file.endswith(ext):
        files.append(file)
files.sort()

# initialize the arrays
time_init = np.zeros(len(files))
time_setup = np.zeros(len(files))
time_restart = np.zeros(len(files))
time_read = np.zeros(len(files))
time_write = np.zeros(len(files))
time_physics = np.zeros(len(files))
time_total = np.zeros(len(files))

# loop over the files and extract the timing info into prepared arrays
for ii,file in enumerate(files):
    time_total[ii],time_physics[ii],time_write[ii],time_read[ii],\
    time_restart[ii],time_setup[ii],time_init[ii],nSkipped = get_computation_time(file)
    
# Prepare for the figure
plt.rcParams.update({'font.size': 16})
ttl = 'SUMMA computational times ({n} logs{isLog})' # general title
ttl_n = len(files)-nSkipped # number of log files included

# general plotting function
def plot_times(ax, title, xlog=False):
    ax.boxplot((time_setup, time_init, time_restart, time_read, time_physics, time_write, time_total),
             labels=('setup','init','restart','read','physics','write','total'),
             vert=0);
    ax.set_title(title)
    ax.set_xlabel('time [s]')
    if xlog: ax.set_xscale('log')
    return
    
# Create the boxplot
fig,axs = plt.subplots(2,1,figsize=(20,8))
plot_times(axs[0],ttl.format(n=ttl_n,isLog=''))
plot_times(axs[1],ttl.format(n=ttl_n,isLog='; logarithmic time axis'),xlog=True)
plt.tight_layout()
plt.savefig(folder + '/' +summaryFig)