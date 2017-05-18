#!/usr/bin/env python

r"""
This module contains keyword functions to supplement robot's built in
functions and use in test where generic robot keywords don't support.

"""
import time
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries import DateTime
import re

###############################################################################


def run_until_keyword_fails(retry, retry_interval, name, *args):
    r"""
    Execute a robot keyword repeatedly until it either fails or the timeout
    value is exceeded.
    Note: Opposite of robot keyword "Wait Until Keyword Succeeds".

    Description of argument(s):
    retry              Max timeout time in hour(s).
    retry_interval     Time interval in minute(s) for looping.
    name               Robot keyword to execute.
    args               Robot keyword arguments.
    """

    # Convert the retry time in seconds
    retry_seconds = DateTime.convert_time(retry)
    timeout = time.time() + int(retry_seconds)

    # Convert the interval time in seconds
    interval_seconds = DateTime.convert_time(retry_interval)
    interval = int(interval_seconds)

    BuiltIn().log(timeout)
    BuiltIn().log(interval)

    while True:
        status = BuiltIn().run_keyword_and_return_status(name, *args)

        # Return if keywords returns as failure.
        if status is False:
            BuiltIn().log("Failed as expected")
            return False
        # Return if retry timeout as success.
        elif time.time() > timeout > 0:
            BuiltIn().log("Max retry timeout")
            return True
        time.sleep(interval)
        BuiltIn().log(time.time())

    return True
###############################################################################


###############################################################################
def htx_error_log_to_list(htx_error_log_output):

    r"""
    Parse htx error log output string and return list of strings in the form
    "<field name>:<field value>".
    The output of this function may be passed to the build_error_dict function.

    Description of argument(s):
    htx_error_log_output        Error entry string containing the stdout
                                generated by "htxcmdline -geterrlog".

    Example of htx_error_log_output contents:

    ######################## Result Starts Here ###############################
    Currently running ECG/MDT : /usr/lpp/htx/mdt/mdt.whit
    ===========================
    ---------------------------------------------------------------------
    Device id:/dev/nvidia0
    Timestamp:Mar 29 19:41:54 2017
    err=00000027
    sev=1
    Exerciser Name:hxenvidia
    Serial No:Not Available
    Part No:Not Available
    Location:Not Available
    FRU Number:Not Available
    Device:Not Available
    Error Text:cudaEventSynchronize for stopEvent returned err = 0039 from file
               , line 430.
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    Device id:/dev/nvidia0
    Timestamp:Mar 29 19:41:54 2017
    err=00000027
    sev=1
    Exerciser Name:hxenvidia
    Serial No:Not Available
    Part No:Not Available
    Location:Not Available
    FRU Number:Not Available
    Device:Not Available
    Error Text:Hardware Exerciser stopped on error
    ---------------------------------------------------------------------
    ######################### Result Ends Here ################################

    Example output:
    Returns the lists of error string per entry
    ['Device id:/dev/nvidia0',
     'Timestamp:Mar 29 19:41:54 2017',
     'err=00000027',
     'sev=1',
     'Exerciser Name:hxenvidia',
     'Serial No:Not Available',
     'Part No:Not Available',
     'Location:Not Available',
     'FRU Number:Not Available',
     'Device:Not Available',
     'Error Text:cudaEventSynchronize for stopEvent returned err = 0039
                 from file , line 430.']
    """

    # List which will hold all the list of entries.
    error_list = []

    temp_error_list = []
    parse_walk = False

    for line in htx_error_log_output.splitlines():
        # Skip lines starting with "#"
        if line.startswith("#"):
            continue

        # Mark line starting with "-" and set parse flag.
        if line.startswith("-") and parse_walk is False:
            parse_walk = True
            continue
        # Mark line starting with "-" and reset parse flag.
        # Set temp error list to EMPTY.
        elif line.startswith("-"):
            error_list.append(temp_error_list)
            parse_walk = False
            temp_error_list = []
        # Add entry to list if line is not emtpy
        elif parse_walk:
            temp_error_list.append(str(line))

    return error_list
###############################################################################


###############################################################################
def build_error_dict(htx_error_log_output):

    r"""
    Builds error list into a list of dictionary entries.

    Description of argument(s):
    error_list        Error list entries.

    Example output dictionary:
    {
      0:
        {
          'sev': '1',
          'err': '00000027',
          'Timestamp': 'Mar 29 19:41:54 2017',
          'Part No': 'Not Available',
          'Serial No': 'Not Available',
          'Device': 'Not Available',
          'FRU Number': 'Not Available',
          'Location': 'Not Available',
          'Device id': '/dev/nvidia0',
          'Error Text': 'cudaEventSynchronize for stopEvent returned err = 0039
                         from file , line 430.',
          'Exerciser Name': 'hxenvidia'
        },
      1:
        {
          'sev': '1',
          'err': '00000027',
          'Timestamp': 'Mar 29 19:41:54 2017',
          'Part No': 'Not Available',
          'Serial No': 'Not Available',
          'Device': 'Not Available',
          'FRU Number': 'Not Available',
          'Location': 'Not Available',
          'Device id': '/dev/nvidia0',
          'Error Text': 'Hardware Exerciser stopped on error',
          'Exerciser Name': 'hxenvidia'
        }
    },

    """

    # List which will hold all the list of entries.
    error_list = []
    error_list = htx_error_log_to_list(htx_error_log_output)

    # dictionary which holds the error dictionry entry.
    error_dict = {}

    temp_error_dict = {}
    error_index = 0

    # Loop through the error list.
    for entry_list in error_list:
        # Loop through the first error list entry.
        for entry in entry_list:
            # Split string into list for key value update.
            # Example: 'Device id:/dev/nvidia0'
            # Example: 'err=00000027'
            parm_split = re.split("[:=]", entry)
            # Populate temp dictionary with key value pair data.
            temp_error_dict[str(parm_split[0])] = parm_split[1]

        # Update the master dictionary per entry index.
        error_dict[error_index] = temp_error_dict
        # Reset temp dict to EMPTY and increment index count.
        temp_error_dict = {}
        error_index += 1

    return error_dict

###############################################################################
