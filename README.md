# Mobility Concept of ConnectiCity (**Ide3a**)
This is a script that runs on SUMO and was created to build the mobility concept on the ConnectiCity game. So there will be live traffic throughout the game. The traffic simulation will be updated every game round. During this update, it is built on the latest traffic situation from the previous game round.

To achieve this, 
- There is a defined number of vehicles in the city traffic.
- On the first game round, each vehicle chooses a route from the defined ones and starts moving through the city traffic.
- If an event occurs during that round, such as a flood, the roads in the area of the event are affected and the maximum vehicle speed on the roads is updated. 
- Thus, the traffic may continue to flow according to the new updated road conditions. 
- At the end of the game round, some vehicles may have completed their route, or may still be traveling on the route.
- When the next game round starts, if any vehicle completed its route in the previous round, it will choose a new route and continue moving in traffic.
- If there are still vehicles that have not completed their route, the vehicle continues to move in the traffic with the information from the previous round (position, speed, route, edge, lane, etc.). 

Thus, a more realistic city traffic can be achieved. Each game round represents a simulation over an equal time interval. 

Although the game concept is time-independent, this script creates a state of continuity so that the simulation can continue in accordance with this concept. 
