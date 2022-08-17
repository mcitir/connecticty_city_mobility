#!/usr/bin/env python

# @author    Muzaffer Citir
# @date      2022.08.16
# @location  Berlin, Germany
# @version   1.0

# @brief   This is a script to convert back to the initial state.
# Path: refresh_to_initial.py
import os
import sys
import shutil

# if a folder 'csv' exists, delete it without getting access denied error
if os.path.exists('csv'):
    # os.rmdir('csv')
    shutil.rmtree(r'csv')
    print("Folder 'csv' deleted.")

# if a folder 'dump' exists, delete it
if os.path.exists('dump'):
    shutil.rmtree(r'dump')
    print("Folder 'dump' deleted.")

# if a folder 'stats' exists, delete it
if os.path.exists('stats'):
    shutil.rmtree(r'stats')
    print("Folder 'stats' deleted.")
