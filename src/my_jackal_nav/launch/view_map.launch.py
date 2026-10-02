# my_jackal_nav/launch/view_map.launch.py

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    Launch file to start the Nav2 map server, its lifecycle manager,
    and RViz2 to visualize a pre-existing map.
    """
    # Get the directory of this package
    pkg_dir = get_package_share_directory('my_jackal_nav')

    # Define the path to the map's YAML configuration file
    map_yaml_path = os.path.join(pkg_dir, 'maps', 'hospitaljackal.yaml')

    # Define the path to the RViz configuration file
    # IMPORTANT: Make sure this file exists at the specified path!
    rviz_config_path = os.path.join(pkg_dir, 'rviz', 'view_map.rviz')

    # --- Nodes ---

    # 1. Map Server Node
    # Loads the map from the YAML file and serves it on the /map topic.
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'use_sim_time': False},
            {'yaml_filename': map_yaml_path}
        ]
    )

    # 2. Lifecycle Manager Node
    # Manages the lifecycle of the map server, bringing it up correctly.
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['map_server']}
        ]
    )

    # 3. RViz2 Node
    # Launches RViz2 with a pre-configured display setup.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    # Return the list of nodes to be launched
    return LaunchDescription([
        map_server_node,
        lifecycle_manager_node,
        rviz_node
    ])

