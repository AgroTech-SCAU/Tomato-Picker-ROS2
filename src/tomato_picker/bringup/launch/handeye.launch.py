from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_profile = LaunchConfiguration("robot_profile")
    profile_file = LaunchConfiguration("profile_file")
    resource_paths = LaunchConfiguration("resource_paths")
    serial_port = LaunchConfiguration("serial_port")
    baudrate = LaunchConfiguration("baudrate")
    bus = LaunchConfiguration("bus")
    pose_topic = LaunchConfiguration("pose_topic")
    publish_rate = LaunchConfiguration("publish_rate")

    handeye_bridge = Node(
        package="tomato_picker_bringup",
        executable="handeye_bridge",
        name="handeye_bridge",
        output="screen",
        emulate_tty=True,
        parameters=[
            {
                "robot_profile": ParameterValue(robot_profile, value_type=str),
                "profile_file": ParameterValue(profile_file, value_type=str),
                "resource_paths": ParameterValue(resource_paths, value_type=str),
                "serial_port": ParameterValue(serial_port, value_type=str),
                "baudrate": ParameterValue(baudrate, value_type=str),
                "bus": ParameterValue(bus, value_type=str),
                "pose_topic": ParameterValue(pose_topic, value_type=str),
                "publish_rate": ParameterValue(publish_rate, value_type=float),
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_profile", default_value="tomato_picker"),
            DeclareLaunchArgument(
                "profile_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("tomato_picker_bringup"), "config", "robot_profiles.yaml"]
                ),
            ),
            DeclareLaunchArgument("resource_paths", default_value=""),
            DeclareLaunchArgument("serial_port", default_value=""),
            DeclareLaunchArgument("baudrate", default_value=""),
            DeclareLaunchArgument("bus", default_value=""),
            DeclareLaunchArgument("pose_topic", default_value="/arm/pose"),
            DeclareLaunchArgument("publish_rate", default_value="30.0"),
            handeye_bridge,
        ]
    )
