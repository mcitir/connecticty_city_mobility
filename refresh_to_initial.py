#!/usr/bin/env python

# @author    Muzaffer Citir
# @date      2022.08.16
# @location  Berlin, Germany
# @version   1.0

# @brief   This is a script to convert back to the initial state.
# Path: refresh_to_initial.py
import os
import sys

# delete the files 'simulationStats.csv', 'straight.rou.xml', 'dump.csv', 'tripinfo.csv', 'dump.xml', 'tripinfo.xml',
# 'df_dump_xml.png', 'df_tripinfo_xml.png', 'df_stats.png' if they exist
if os.path.exists("simulationStats.csv"):
    os.remove("simulationStats.csv")
if os.path.exists("straight.rou.xml"):
    os.remove("straight.rou.xml")
if os.path.exists("dump.csv"):
    os.remove("dump.csv")
if os.path.exists("tripinfo.csv"):
    os.remove("tripinfo.csv")
if os.path.exists("dump.xml"):
    os.remove("dump.xml")
if os.path.exists("tripinfo.xml"):
    os.remove("tripinfo.xml")
if os.path.exists("df_dump_xml.png"):
    os.remove("df_dump_xml.png")
if os.path.exists("df_tripinfo_xml.png"):
    os.remove("df_tripinfo_xml.png")
if os.path.exists("df_stats.png"):
    os.remove("df_stats.png")

print("Related files deleted.")
