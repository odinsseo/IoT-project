# IoT-project

 Set of ROS1-noetic nodes used for communicating with a mobile surveillance machine.

## Requirements

 For this code to work you need to install Python 3, ROS1-noetic and Rosbridge-noetic on the mobile device, while a MySQL server must be created on the server machine. A Rosbridge connection must be started before launching the nodes.

## Structure

The project is divided between machine-side and server-side: the former containes all the nodes implemented for a Raspberry Pi 3B+ with an Ubuntu 20.04 32-bit operating system and the latter contains a node whose purpose is to load the data on a MySQL database.

The project is implemented in Python 3 and the libraries required by each part are specified in a `requirements.txt` file. To install them simply run

```{bash}
pip install -r requirements.txt
```

## Nodes

Each part is then structured in folders which contain the nodes implemented. The convention that is followed is to name the script that implements the node with the same name of the folder it is contained in.

There is a total of five nodes which are grouped as follows:

- machine
  - camera
  - lidar
  - motor
  - transform
- server
  - loader

The nodes in *machine* provide a ROS1 interface for the device. In greater detail: *camera* publishes [`sensor_msgs/CompressedImage`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/CompressedImage.html) messages, which encode the images captured by the camera in a JPEG format, and [`sensor_msgs/CameraInfo`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/CameraInfo.html), which contains important information to decode the image sent; *lidar* publishes [`sensor_msgs/LaserScan`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/LaserScan.html) messages; *motor* subscribe to [`geometry_msgs/Twist`](https://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/Twist.html) messages and publishes [`geometry_msgs/PoseStamped`](https://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/PoseStamped.html) messages; *transform* subscribes to [`geometry_msgs/PoseStamped`](https://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/PoseStamped.html) messages and publishes [`geometry_msgs/TransformStamped`](https://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/TransformStamped.html) messages, which allow to represent the remote device's movement; *loader* subscribes to [`sensor_msgs/CompressedImage`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/CompressedImage.html), [`sensor_msgs/LaserScan`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/LaserScan.html) and [`geometry_msgs/PoseStamped`](https://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/PoseStamped.html) to elaborate their contents and upload them into the MySQL database.
