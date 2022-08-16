#!/usr/bin/env python

# @author    Muzaffer Citir
# @date      2022.08.11
# @location  Berlin, Germany
# @version   1.0

# @brief   This is the main file of the project to run simulation via TraCI.

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import time
import sumolib.statistics
from sumolib.xml import parse_fast_nested, parse_fast_structured
from collections import OrderedDict
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import xmltodict
import numpy as np

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  #
import traci  # noqa
import csv
import dataframe_image as dfi


def parse_xml(xml_file):
    # parse the xml file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root


def random_route(routes):
    selected_route = [random.choice(list(routes.keys()))]
    return selected_route


def get_order_in_datalist(datalist, key):
    return datalist.index(key)


def concat_list_elements(datalist):
    return ' '.join(['{}'.format(item) for item in datalist])


def get_property(car, property_, stats):
    # get the property of the car
    property_of_car = stats.loc[stats['carID'] == car][property_].tolist()[0]
    return property_of_car


def dump_xml_to_df(root):
    df_total = pd.DataFrame(columns=['time', 'carID', 'edgeID', 'laneID', 'pos', 'speed'])
    for time in root:
        for child in time:
            for child2 in child:

                for child3 in child2:
                    dictSeries = {'time': str(time.attrib['time']),
                                  'carID': str(child3.attrib['id']),
                                  'edgeID': str(child.attrib['id']),
                                  'laneID': str(child2.attrib['id']),
                                  'pos': str(child3.attrib['pos']),
                                  'speed': str(child3.attrib['speed'])}
                    temporary_df = pd.DataFrame([dictSeries])
                    df_total = pd.concat([df_total, temporary_df], ignore_index=True, keys=['time', 'carID'])
    # df_total = df_total.sort_values(['time', 'carID']).reset_index(drop=True)
    return df_total


def tripinfo_xml_to_df(root):
    df_total = pd.DataFrame(
        columns=['carID', 'depart', 'departLane', 'departPos', 'departSpeed', 'departDelay', 'arrival', 'arrivalLane',
                 'arrivalPos', 'arrivalSpeed', 'duration', 'routeLength', 'waitingTime', 'rerouteNo', 'speedFactor',
                 'vaporized'])
    for tripinfo in root:
        dictSeries = {'carID': tripinfo.attrib['id'],
                      'depart': tripinfo.attrib['depart'],
                      'departLane': tripinfo.attrib['departLane'],
                      'departPos': tripinfo.attrib['departPos'],
                      'departSpeed': tripinfo.attrib['departSpeed'],
                      'departDelay': tripinfo.attrib['departDelay'],
                      'arrival': tripinfo.attrib['arrival'],
                      'arrivalLane': tripinfo.attrib['arrivalLane'],
                      'arrivalPos': tripinfo.attrib['arrivalPos'],
                      'arrivalSpeed': tripinfo.attrib['arrivalSpeed'],
                      'duration': tripinfo.attrib['duration'],
                      'routeLength': tripinfo.attrib['routeLength'],
                      'waitingTime': tripinfo.attrib['waitingTime'],
                      'rerouteNo': tripinfo.attrib['rerouteNo'],
                      'speedFactor': tripinfo.attrib['speedFactor'],
                      'vaporized': tripinfo.attrib['vaporized']}
        temp_df = pd.DataFrame([dictSeries])
        df_total = pd.concat([df_total, temp_df], ignore_index=False)

    # df_total = df_total.sort_values(['carID']).reset_index(drop=True)
    return df_total


# noinspection SpellCheckingInspection
def generate_routefile():
    # Create a temporary dictionary to store the carID and onRouteAtStart
    assigned_routes = {}

    with open("straight.rou.xml", "w") as routes:
        print("""<?xml version="1.0" encoding="UTF-8"?>

<!-- generated via generate_routefile() in run.py -->

<routes>
    <vType id="CAR1" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="1" guiShape="passenger"/>

    <vehicle id="car1" type="CAR1" depart="0">
        <route edges="E0"/>
    </vehicle>
</routes>
""", file=routes)
    return assigned_routes


def update_routefile():
    # Create a temporary dictionary to store the carID and onRouteAtStart
    assigned_routes = {}

    with open("straight.rou.xml", "w") as update_routes:
        print(f"""<?xml version="1.0" encoding="UTF-8"?>
        <!-- generated via update_routefile() in run.py -->
        <routes>
            <vType id="passenger1" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" """ 
              f"""maxSpeed="33.33" guiShape="passenger"/>
         """, file=update_routes)
        for key, value in routes.items():
            print(f"""
            <route id="{key}" edges="{concat_list_elements(value)}"/>""", file=update_routes)
        for i in range(10):
            # "car{i}" in the list of 'carIDs_from_previous_simulation'
            if 'car{}'.format(i) in carIDs_from_previous_simulation:
                # Assign selected route to the car:
                assigned_routes[f'car{i}'] = df_stats_last_time.loc[df_stats_last_time['carID'] == f'car{i}',
                                                                    'onRouteAtStart'].iloc[0]

                pos_is_ = get_property("car{}".format(i), 'pos', df_stats_last_time)
                speed_is_ = get_property("car{}".format(i), 'speed', df_stats_last_time)
                edge_is_ = get_order_in_datalist(routes[assigned_routes[f'car{i}']],
                                                 get_property("car{}".format(i), 'edgeID', df_stats_last_time))
                lane_is_ = get_property("car{}".format(i), 'laneID', df_stats_last_time)

                print(f"""
                <vehicle id="car{i}" type="passenger1" route="{assigned_routes[f'car{i}']}" """
                      f"""depart="0" departLane="{lane_is_.split('_')[-1]}" departEdge="{edge_is_}" """
                      f"""departPos="{pos_is_}" departSpeed="{speed_is_}"/>""", file=update_routes)
                del edge_is_, lane_is_, pos_is_, speed_is_
            else:
                selected = random_route(routes)
                assigned_routes[f'car{i}'] = selected[0]
                print(f"""
                <vehicle id="car{i}" type="passenger1" route="{assigned_routes[f'car{i}']}" """ 
                      f"""departPos="0.00"  depart="0"/>""", file=update_routes)
        print("""
        </routes>""", file=update_routes)
    return assigned_routes


def generate_netfile():
    random.seed(42)  # make tests reproducible

    with open("straight.net.xml", "w") as nets:
        print("""<?xml version="1.0" encoding="UTF-8"?>""", file=nets)


def run():
    """execute the TraCI control loop"""
    step = 0
    while step < 101:
        traci.simulationStep()
        step += 1
        time.sleep(0.05)
        # print(sumolib.statistics.round(1.5))
        # s = sumolib.statistics.Statistics(10)
        # print(s.toString())
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    # Define variables
    routes = {'route0': ['E0', 'E12', 'E4', 'E7'],
              'route1': ['-E7', '-E4', '-E12', '-E0'],
              'route2': ['-E6', '-E12', 'E2']}

    # Import data from the csv file and store it in a dataframe named df_stats
    df_stats = pd.read_csv('simulationStats.csv', dtype=str, keep_default_na=False)

    # filter for the last time step
    df_stats_last_time = df_stats.loc[df_stats['time'] == df_stats['time'].tail(1).tolist()[0]]

    # Keep track how many times the simulation has been restarted
    if 'HasRun' not in df_stats_last_time.columns:
        HasRun = 1
    else:
        HasRun = int(df_stats_last_time['HasRun'].tolist()[0]) + 1

    # List of vehicle IDs that did not complete their route in the previous simulation step
    carIDs_from_previous_simulation = df_stats_last_time['carID'].tolist()
    print("From previous simulation:", carIDs_from_previous_simulation)

    # Generate the route file for this simulation
    if os.path.exists("tripinfo.xml"):
        assigned_routes = update_routefile()
        print("OnRoute:")
        print(assigned_routes)
    else:
        assigned_routes = generate_routefile()
    # generate_routefile()
    # generate_netfile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "straight.sumocfg",
                 "--tripinfo-output", "tripinfo.xml", "--tripinfo-output.write-unfinished", "True",
                 "--start", "--quit-on-end", "--netstate-dump", "dump.xml"])
    run()

    dump_root = parse_xml('dump.xml')
    df_dump_xml = dump_xml_to_df(dump_root)

    tripinfo_root = parse_xml('tripinfo.xml')
    df_tripinfo_xml = tripinfo_xml_to_df(tripinfo_root)

    last_time_step = str(dump_root[len(dump_root) - 1].attrib['time'])
    print("Last time:", last_time_step)

    df_stats = pd.merge(df_dump_xml, df_tripinfo_xml, on='carID', how='left')
    df_stats = df_stats[['time', 'carID', 'depart', 'edgeID',
                         'departLane', 'laneID', 'arrivalLane',
                         'departPos', 'pos', 'arrivalPos',
                         'departSpeed', 'speed', 'arrivalSpeed',
                         'departDelay', 'waitingTime', 'duration', 'arrival',
                         'routeLength', 'rerouteNo', 'speedFactor', 'vaporized']]

    # Add a new column to dataframe which counts how many times the simulation has been restarted
    df_stats['HasRun'] = HasRun

    # Add a new column to dataframe which records the routes assigned to each vehicle
    df_stats['onRouteAtStart'] = df_stats['carID'].map(assigned_routes)

    pd.DataFrame.to_csv(df_stats, 'simulationStats.csv', index=False, quoting=csv.QUOTE_ALL)
    pd.DataFrame.to_csv(df_dump_xml, 'dump.csv', index=False, quoting=csv.QUOTE_ALL)
    pd.DataFrame.to_csv(df_tripinfo_xml, 'tripinfo.csv', index=False, quoting=csv.QUOTE_ALL)

    dfi.export(df_dump_xml, 'df_dump_xml.png', max_rows=20)
    dfi.export(df_tripinfo_xml, 'df_tripinfo_xml.png', max_rows=20)
    dfi.export(df_stats, 'df_stats.png', max_rows=40)





































    # nested = OrderedDict((('vehicle ', ['id']), ('edge', ['id'])))
    # for step in parse_fast_nested('dump.xml', 'timestep', ['time'], 'vehicle', ['id', 'pos', 'speed']):
    #     print(step)
    #     print(step[1].pos)
    # test1 = list(parse_fast_nested('dump.xml', 'timestep', ['time'], 'vehicle', ['id', 'pos', 'speed']))
    # #print(type(test1[-1][1][0]), test1[-1][1][1])
    # print("Last time step: {}".format(test1[-1][0][0]))
    #
    # print("length:", len(test1[-1]))
    #
    # # for param in last_element:
    # #     print(param)
    #
    # dataFrame = pd.DataFrame(test1)
    # print("Last of timestep:", dataFrame[0].iloc[-1].time)
    #
    # print("Filtered:")
    # print(list(dataFrame))
    # # filter the dataframe if time is equal to last time step
    # #     filtered = dataFrame[dataFrame[0].iloc[-1]== dataFrame[0].iloc[-1].time]
    # dataFrame.rename(columns={list(dataFrame)[0]: 'timestep', list(dataFrame)[1]: 'vehicle'}, inplace=True)
    # for col in dataFrame.columns:
    #     print(col)
    # # temp = dataFrame.timestep.iloc[-1].time
    # # print("Last time step:", temp)
    # # print(dataFrame['vehicle'].iloc[dataFrame['timestep'] == temp])
    # # print(dataFrame[0].iloc[-1])
    # # dataFrame.loc[(dataFrame.time == dataFrame[0].iloc[-1].time)]
    # # for ele in dataFrame:
    # #     print("Data Frame Column: {}".format(ele))
    # print("TEST 2:")
    # xml = ET.parse('dump.xml')
    #
    # csvfile = open("dumpCSV.csv", "w", encoding="utf-8")
    # csvfile_writer = csv.writer(csvfile)
    #
    # csvfile_writer.writerow(["time", "vehicle_id", "pos", "speed", "lane_id", "edge_id"])
    # i = 0
    # for timestep in xml.findall("timestep"):
    #     # print("Timestep: {}".format(timestep))
    #     if timestep:
    #         time = timestep.get('time')
    #         vehicle_id = list(timestep)[0][0][0].get('id')
    #         edge_id = list(timestep)[0].get('id')
    #         lane_id = list(timestep)[0][0].get('id')
    #     print(f"Time {i}: {time}, {vehicle_id}, {edge_id}, {lane_id}")
    #     i += 1
    # handle = open("dump.xml", "r")
    # content = handle.read()
    # xmldict = xmltodict.parse(content)
    # print("Content--------------------")
    # print(xmldict['netstate']['timestep'])
    # print("Shape: ", np.shape(xmldict))
    #
    # df_xmltodict = pd.DataFrame.from_dict(xmldict['netstate']['timestep'])
    # print("Shape: ", np.shape(df_xmltodict))
    # print(type(df_xmltodict))
    # print("DataFrame:")
    # # access dataframe of df_xmltodict if time is equal to '99.00'
    # print(df_xmltodict[df_xmltodict['@time'] == '99.00'])



        #     pos = timestep.find("pos")
        #     speed = timestep.find("speed")
        #     lane_id = timestep.find("lane_id")
        #     edge_id = timestep.find("edge_id")
        #
        #     csvline = [time, vehicle_id.text, pos.text, speed.text, lane_id.text, edge_id.text]
        #     csvfile_writer.writerow(csvline)
    # print(len(xml.findall("timestep")))
    # csvfile.close()


    # ET.dump(test2)  # print the xml file
    # list1 = {}
    # last_time_step = root.findall('./timestep')[-1]
    # last_time = "\""+last_time_step.attrib['time']+"\""
    #
    # for elm in root.findall(f"./timestep[@time={last_time}]/edge/lane/vehicle"):
    #     # list1.append(elm.attrib['id', 'pos', 'speed'])
    #     # print(list1)
    #     print(elm.tag, elm.attrib)


