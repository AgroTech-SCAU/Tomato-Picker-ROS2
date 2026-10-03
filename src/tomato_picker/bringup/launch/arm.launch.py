from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from serial_arm import load_robot_profile_core


def _package_path(package: str, relative_path: str) -> str:
    return str(Path(get_package_share_directory(package)) / relative_path)


def _load_ros_profile(profile_file: str, profile_name: str):
    path = Path(profile_file)
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    profiles = data.get("profiles", {})
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        raise RuntimeError(
            f"robot_profile '{profile_name}' not found in {profile_file}; available: {available}"
        )
    profile = profiles[profile_name]
    for section in ("description", "controllers", "moveit"):
        if section not in profile:
            raise RuntimeError(
                f"robot_profile '{profile_name}' is missing ROS section '{section}'"
            )
    return profile


def _resolve_arm(context):
    robot_profile = LaunchConfiguration("robot_profile").perform(context)
    profile_file = LaunchConfiguration("profile_file").perform(context)
    serial_port = LaunchConfiguration("serial_port").perform(context)
    baudrate = LaunchConfiguration("baudrate").perform(context)
    bus = LaunchConfiguration("bus").perform(context)
    use_sim_time_text = LaunchConfiguration("use_sim_time").perform(context)
    use_sim_time = use_sim_time_text.lower() in ("true", "1", "yes")

    # Core + Hardware stay owned and resolved by SerialArm-Core.
    core_profile = load_robot_profile_core(robot_profile, profile_file)

    # Tomato owns only the ROS assembly fields layered above the framework-neutral Core profile.
    ros_profile = _load_ros_profile(profile_file, robot_profile)
    description = ros_profile["description"]
    controllers = ros_profile["controllers"]
    moveit = ros_profile["moveit"]

    description_xacro = _package_path(
        description["package"], description["ros2_control_xacro"]
    )
    controllers_file = _package_path(
        controllers["package"], controllers["config"]
    )
    moveit_package = moveit["package"]

    robot_description = Command(
        [
            FindExecutable(name="xacro"),
            " ",
            description_xacro,
            " config_file:=",
            core_profile.core_config_path,
            " hardware_plugin:=",
            core_profile.hardware_plugin,
            " hardware_config:=",
            core_profile.hardware_config_path,
            " serial_port:=",
            serial_port,
            " baudrate:=",
            baudrate,
            " bus:=",
            bus,
        ]
    )
    robot_description_param = ParameterValue(robot_description, value_type=str)

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description_param,
                "use_sim_time": use_sim_time,
            }
        ],
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[
            {"robot_description": robot_description_param},
            controllers_file,
        ],
        remappings=[("~/robot_description", "/robot_description")],
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    joint_trajectory_controller = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "joint_trajectory_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare(moveit_package), "launch", "move_group.launch.py"]
            )
        )
    )

    moveit_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare(moveit_package), "launch", "moveit_rviz.launch.py"]
            )
        )
    )

    return [
        robot_state_publisher,
        ros2_control_node,
        joint_state_broadcaster,
        joint_trajectory_controller,
        move_group,
        moveit_rviz,
    ]


def generate_launch_description():
    default_profile_file = PathJoinSubstitution(
        [FindPackageShare("tomato_picker_bringup"), "config", "robot_profiles.yaml"]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_profile", default_value="tomato_picker"),
            DeclareLaunchArgument("profile_file", default_value=default_profile_file),
            DeclareLaunchArgument("serial_port", default_value=""),
            DeclareLaunchArgument("baudrate", default_value=""),
            DeclareLaunchArgument("bus", default_value=""),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            OpaqueFunction(function=_resolve_arm),
        ]
    )
