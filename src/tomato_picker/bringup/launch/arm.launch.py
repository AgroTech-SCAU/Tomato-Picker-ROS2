from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_profile = LaunchConfiguration("robot_profile")
    profile_file = LaunchConfiguration("profile_file")
    resource_paths = LaunchConfiguration("resource_paths")
    serial_port = LaunchConfiguration("serial_port")
    baudrate = LaunchConfiguration("baudrate")
    bus = LaunchConfiguration("bus")
    use_sim_time = LaunchConfiguration("use_sim_time")
    controller_manager_name = LaunchConfiguration("controller_manager_name")

    serial_arm_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("serial_arm_ros2_control"),
                    "launch",
                    "moveit.launch.py",
                ]
            )
        ),
        launch_arguments={
            "robot_profile": robot_profile,
            "profile_file": profile_file,
            "resource_paths": resource_paths,
            "serial_port": serial_port,
            "baudrate": baudrate,
            "bus": bus,
            "use_sim_time": use_sim_time,
            "controller_manager_name": controller_manager_name,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_profile", default_value="tomato_picker"),
            DeclareLaunchArgument(
                "profile_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("tomato_picker_bringup"),
                        "config",
                        "robot_profiles.yaml",
                    ]
                ),
            ),
            DeclareLaunchArgument("resource_paths", default_value=""),
            DeclareLaunchArgument("serial_port", default_value=""),
            DeclareLaunchArgument("baudrate", default_value=""),
            DeclareLaunchArgument("bus", default_value=""),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument(
                "controller_manager_name", default_value="/controller_manager"
            ),
            serial_arm_moveit,
        ]
    )
