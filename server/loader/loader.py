#!/usr/bin/python3
import mysql.connector
from roslibpy import Topic, Ros
from time import gmtime, strftime

last_pose = None
db_connection = None


def get_time(stamp):
    return stamp['secs'] + stamp['nsecs'] * 10 ** (-9)


# Connection to db
def create_database_connection():
    global db_connection
    if db_connection is None:
        db_connection = mysql.connector.connect(
            host="<mysql server uri>",
            user="user",
            password="password",
            database="db"
        )


# Pose
def pose_callback(message):
    global last_pose, db_connection

    create_database_connection()

    x_position = message["pose"]['position']['x']
    timestamp = get_time(message['header']['stamp'])

    if last_pose is not None:
        delta_x = x_position - last_pose["pose"]['position']['x']
        delta_t = timestamp - get_time(last_pose['header']['stamp'])

        if delta_t > 0:
            velocity = delta_x / delta_t
        else:
            velocity = 0.0

        cursor = db_connection.cursor()
        insert_query = "INSERT INTO Macchinina (timestamp, velocita) VALUES (%s, %s)"
        cursor.execute(insert_query, (strftime("%Y-%m-%d %H:%M:%S", gmtime(timestamp)), velocity))
        db_connection.commit()
        cursor.close()

    last_pose = message


# LiDAR
def lidar_callback(message):
    global db_connection

    create_database_connection()

    timestamp = get_time(message['header']['stamp'])
    angles = message['angle_increment']
    distances = message['ranges']
    intensities = message['intensities']

    cursor = db_connection.cursor()
    for i in range(len(angles)):
        angle = angles[i]
        distance = distances[i]
        intensity = intensities[i] if intensities else None

        insert_query = "INSERT INTO Lidar (timestamp, angle, distance, intensita) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (timestamp, angle, distance, intensity))
    db_connection.commit()
    cursor.close()


# Camera
def camera_callback(message):
    global db_connection

    create_database_connection()

    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime(get_time(message['header']['stamp'])))
    image_data = message['data']

    cursor = db_connection.cursor()
    insert_query = "INSERT INTO Fotocamera (timestamp, immagine) VALUES (%s, %s)"
    cursor.execute(insert_query, (timestamp, image_data))
    db_connection.commit()
    cursor.close()


ros = Ros('<ros master uri>', port=9090, is_secure=True)
ros.run()

pose_topic = Topic(ros, '/pose', 'geometry_msgs/PoseStamped')
lidar_topic = Topic(ros, '/lidar', 'lidar_msgs/LaserScan')
camera_topic = Topic(ros, '/camera', 'sensor_msgs/CompressedImage')

pose_topic.subscribe(pose_callback)
lidar_topic.subscribe(lidar_callback)
camera_topic.subscribe(camera_callback)

try:
    while ros.is_connected:
        pass

    ros.terminate()
except KeyboardInterrupt:
    ros.terminate()
