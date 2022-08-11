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

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  #
import traci  # noqa


# noinspection SpellCheckingInspection
def generate_routefile():
    random.seed(42)  # make tests reproducible

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


def update_routefile():
    random.seed(42)  # make tests reproducible

    with open("straight.rou.xml", "w") as update_routes:
        print("""<?xml version="1.0" encoding="UTF-8"?>
        
        <!-- generated via update_routefile() in run.py -->
   
        """, file=update_routes)


def generate_netfile():
    random.seed(42)  # make tests reproducible

    with open("straight.net.xml", "w") as nets:
        print("""<?xml version="1.0" encoding="UTF-8"?>""", file=nets)


def run():
    """execute the TraCI control loop"""
    step = 0
    while step < 100:
        traci.simulationStep()
        print("simulation step {}".format(step))
        for veh_id in traci.vehicle.getIDList():
            print("vehicle {} at position {}".format(veh_id, traci.vehicle.getPosition(veh_id)))
        step += 1
        # time.sleep(0.2)
        print(sumolib.statistics.round(1.5))
        s = sumolib.statistics.Statistics(10)
        print(s.toString())
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

    # first, generate the route file for this simulation
    # if os.path.exists("tripinfo.xml"):
    #     update_routefile()
    # else:
    #     generate_routefile()
    generate_routefile()
    # generate_netfile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "straight.sumocfg",
                 "--tripinfo-output", "tripinfo.xml", "--tripinfo-output.write-unfinished", "True",
                 "--start", "--quit-on-end", "--netstate-dump", "dump.xml"])
    run()
    nested = OrderedDict((('vehicle ', ['id']), ('edge', ['id'])))
    for step in parse_fast_nested('dump.xml', 'timestep', ['time'], 'vehicle', ['id', 'pos', 'speed']):
        print(step)
        print(step[1].pos)
    test1 = list(parse_fast_nested('dump.xml', 'timestep', ['time'], 'vehicle', ['id', 'pos', 'speed']))
    print(type(test1[-1][1][0]), test1[-1][1][1])
