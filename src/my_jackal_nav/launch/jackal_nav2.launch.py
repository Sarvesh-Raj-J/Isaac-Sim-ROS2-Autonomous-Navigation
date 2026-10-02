from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

MAP = "/home/robotics/jackal_ws/src/my_jackal_nav/maps/final_occ_map.yaml"
PARAMS = "/home/robotics/jackal_ws/src/my_jackal_nav/config/nav2_params.yaml"

def generate_launch_description():
    nav2_bringup_dir = get_package_share_directory("nav2_bringup")

    # Static TF: base_link -> sick_lms1xx_lidar_frame
    # (map->world is NOT published as static — AMCL publishes it dynamically
    #  with odom_frame_id="world", so AMCL owns map->world and there is no
    #  TF loop with Isaac Sim's world->odom.)
    # Isaac Sim publishes scan with frame_id=sick_lms1xx_lidar_frame but
    # does NOT put this frame in the TF tree. These offsets match the
    # standard Clearpath Jackal SICK LMS1xx mount.
    lidar_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="base_to_lidar",
        arguments=["0.234", "0", "0.197", "0", "0", "0", "base_link", "sick_lms1xx_lidar_frame"],
        output="screen",
    )

    # Full nav2 bringup (localization + navigation + map server)
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, "launch", "bringup_launch.py")
        ),
        launch_arguments={
            "map": MAP,
            "use_sim_time": "true",
            "params_file": PARAMS,
            "autostart": "true",
            "use_composition": "True",
            "use_respawn": "False",
        }.items(),
    )

    # RViz with nav2 default view — delayed so nav2 is up first
    rviz = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=[
                    "-d",
                    os.path.join(nav2_bringup_dir, "rviz", "nav2_default_view.rviz"),
                ],
                parameters=[{"use_sim_time": True}],
                output="screen",
            )
        ],
    )

    return LaunchDescription([
        lidar_tf,
        nav2,
        rviz,
    ])
