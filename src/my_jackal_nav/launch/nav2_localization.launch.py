from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_dir = get_package_share_directory("my_jackal_nav")
    map_file = os.path.join(package_dir, "maps", "hospitaljackal.yaml")
    rviz_config = os.path.join(package_dir, "config", "localization.rviz")

    return LaunchDescription([

        # --- Map Server ---
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[
                {"use_sim_time": True},
                {"yaml_filename": map_file}
            ]
        ),

        # --- AMCL Localization ---
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            output="screen",
            parameters=[
                {"use_sim_time": True},
                {"base_frame_id": "base_link"},
                {"global_frame_id": "map"},
                {"odom_frame_id": "odom"},
                {"scan_topic": "/scan"},
                {"laser_frame_id": "Lidar"}
            ]
        ),

        # --- Static Transform for LIDAR ---
        # Replace 0.12 0.0 0.33 with your exact offsets from Isaac Sim
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="lidar_tf",
            arguments=["0.12", "0.0", "0.33", "0", "0", "0", "base_link", "Lidar"]
        ),

        # --- Lifecycle Manager (activates map_server + amcl) ---
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_localization",
            output="screen",
            parameters=[
                {"use_sim_time": True},
                {"autostart": True},
                {"node_names": ["map_server", "amcl"]}
            ]
        ),

        # --- RViz2 with map shown automatically ---
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config]
        )
    ])
