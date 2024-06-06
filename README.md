# Autonomous Robotics Course - Ex1

## Autonomous Drone 🛸 🚁 📍
This project is a simulation of an autonomous drone navigating a 2D environment using various sensors. The goal of the drone is to explore the area as much as possible (it is expressed with yellow coloring) and return to the starting point when the battery level drops to 50%. 🔋 <br /> 
The drone is equipped with distance sensors (left, right, forward, backward), an orientation sensor (IMU), and an optical flow sensor to aid in navigation and obstacle avoidance.

### Project Implementation:
**Environment Setup** <br />
We choose to implement it on the Pygame platform.
The environment is represented by a 2D map where white pixels represent navigable areas and black pixels represent obstacles. Each pixel corresponds to a 2.5 cm² area. The drone has a radius of 10 cm and sensors with a maximum detection range of 300 cm.

### Sensors and Drone Movement<br />
**The drone uses the following sensors:** <br />
Distance Sensors: Measure distances in the left, right, forward, and backward directions.<br />
IMU (Inertial Measurement Unit): Provides the drone's orientation in degrees.<br />
Optical Flow Sensor: Measures the drone's velocity relative to the ground.<br />
Battery Sensor: Indicates the remaining battery percentage.<br />
**In all the sensors we add wrong data by 1% and inaccuracy in values ​​by 2%.**
<br />

**How It Works?** <br />
Navigation and Obstacle Avoidance: The drone uses its sensors to navigate and avoid obstacles. 🚧<br />
Path Recording: As the drone moves, it records checkpoints. 📍<br />
Returning Home: When the battery level reaches 50%, the drone uses the recorded path to return to the starting point. ➡️<br />
<br />
**The Features:** <br />
* 🗺️ __2D Environment:__ <br />
The drone navigates a 2D map where white pixels represent navigable areas and black pixels represent obstacles.<br />
* 📍 __Checkpoints:__ <br /> 
The drone records its path with checkpoints for efficient return navigation.<br />
* ⚙️ __Autonomous Control:__ <br /> 
The drone autonomously adjusts its movement and direction based on sensor readings.<br />
* 🔋 __Battery Management:__ <br /> 
The drone monitors its battery level and returns home when the battery drops to 50%.<br />
* 🎮 __Manual Control:__ <br /> 
You can manually control the drone's movement using the arrow keys.<br />

**Code Structure** <br />
The code is split into two main classes: Drone and Controller.<br />
The Drone class is responsible for managing the drone position in the windows, calculating the sensor's values, and displaying the relevant data on the screen. <br />
The Controller class is responsible for controlling the movement of the drone, both manual and autonomous. <br />
In order to control the drone, the controller calculates the drone's relative position according to the sensor's data - the IMU and optical flow sensors. <br />
<br />
The autonomous control function has a few stages - 
- moving forward - when there are no obstacles in front of the drone
- moving in "tunnel" - when the drone is in a narrow place it's trying to be in the center of the tunnel and move forward.
- keep to the right - keeping a constant distance from the right wall
- returning home - rotate the drone to the last checkpoint it visit
- Stuck in an obstacle - try to move backward and rotate to move away from the obstacle
<br />

**Manual Control** 🎮<br />
Changing the manual flag in the drone.py file can change it to manual control. <br />
In addition to its autonomous navigation capabilities, the drone can also be manually controlled using the arrow keys on your keyboard:<br />

⬆️ Up Arrow: Move the drone forward.<br />
⬇️ Down Arrow: Move the drone backward.<br />
⬅️ Left Arrow: Rotate the drone left.<br />
➡️ Right Arrow: Rotate the drone right.<br />
This feature allows you to control the drone's movement and orientation directly, providing an interactive way to navigate the environment and avoid obstacles manually. <br />

### How to Run: <br />
1. Ensure you have Python and Pygame installed.<br />
2. Choose a map that you are interested in running from the 'Maps' directory by changing the MAP const in drone.py. <br />
3. Run the script using: python drone.py. <br />
