# Autonomous Robotics Course - Ex1

## Autonomous Drone 🛸 🚁 📍
This project is a simulation of an autonomous drone navigating a 2D environment using various sensors. The goal of the drone is to explore the area as much as possible (it is expressed with yellow coloring) and return to the starting point when the battery level drops to 50%. 🔋 <br /> 
The drone is equipped with distance sensors (left, right, forward, backward), an orientation sensor (IMU), and an optical flow sensor to aid in navigation and obstacle avoidance.

### Task Description:
__Part 1:__ Familiarization with the Platform
The first part of the task involved understanding autonomous drone control and navigation, including the use of various sensors to model the drone's perception of its environment. The focus was on searching for a platform that allows 2D or 3D modeling of a structure as sensed by the drone's sensors, given its position and speed. We choose to implement it with PyGame.

__Part 2:__ Developing the Control System
In the second part of the task, we built a basic control system for the drone. The objective of the control system is to allow the drone to cover as much area as possible. When the battery level reaches 50%, the drone should navigate back to the starting point.

### Project Implementation:
**Environment Setup** <br />
The environment is represented by a 2D map where white pixels represent navigable areas and black pixels represent obstacles. Each pixel corresponds to a 2.5 cm² area. The drone has a radius of 10 cm and sensors with a maximum detection range of 300 cm.

## Sensors and Drone Movement<br />
**The drone uses the following sensors:** <br />
Distance Sensors: Measure distances in the left, right, forward, and backward directions.<br />
IMU (Inertial Measurement Unit): Provides the drone's orientation in degrees.<br />
Optical Flow Sensor: Measures the drone's velocity relative to the ground.<br />
Battery Sensor: Indicates the remaining battery percentage.<br />
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

**The drone can perform the following actions:** <br />
Rotate left or right.<br />
Move forward or backward.<br />
Stop movement.<br />
Stop rotation.<br />
Autonomous Control<br />
The drone's control system is implemented in the DroneController class. <br />

**The main functionalities include:** <br />
Path Planning: The drone adds checkpoints as it navigates the environment.<br />
Obstacle Avoidance: The drone uses distance sensors to avoid obstacles by adjusting its direction when an obstacle is detected within a certain threshold.<br />
Returning Home: When the battery level drops to 50%, the drone starts returning to the starting point using the recorded checkpoints.<br />

**Functions:** <br />
navigate_to_position<br />
This function is used to navigate the drone to a specified target position while avoiding obstacles. It calculates the desired heading and adjusts the drone's orientation and movement accordingly.
The drone uses various sensors to perceive its environment and avoid obstacles, ensuring efficient navigation and exploration.

**Manual Control** 🎮<br />
In addition to its autonomous navigation capabilities, the drone can also be manually controlled using the arrow keys on your keyboard:<br />

⬆️ Up Arrow: Move the drone forward.<br />
⬇️ Down Arrow: Move the drone backward.<br />
⬅️ Left Arrow: Rotate the drone left.<br />
➡️ Right Arrow: Rotate the drone right.<br />
This feature allows you to control the drone's movement and orientation directly, providing an interactive way to navigate the environment and avoid obstacles manually.<br />

### How to Run: <br />
1. Ensure you have Python and Pygame installed.<br />
2. Place the Maps directory with the required map files in the project directory.<br />
3. Run the script using: python your_script_name.py<br />
