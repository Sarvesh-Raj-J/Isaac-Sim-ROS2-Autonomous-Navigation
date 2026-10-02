"""
Run this script in Isaac Sim's Script Editor:
  Window > Script Editor > paste this > Run

It finds the Jackal articulation root and adds a ROS2 Twist subscriber
action graph so the robot moves when nav2 publishes on /cmd_vel.
"""

import omni.graph.core as og
import omni.kit.commands
from pxr import Usd
import omni.usd

stage = omni.usd.get_context().get_stage()


def find_articulation_root(stage):
    """Walk stage and return the first prim with PhysicsArticulationRootAPI."""
    for prim in stage.Traverse():
        if prim.HasAPI("PhysicsArticulationRootAPI"):
            return prim.GetPath().pathString
    return None


robot_prim_path = find_articulation_root(stage)
if robot_prim_path is None:
    # Fallback: known path from this scene
    candidates = [
        "/World/_4_lnt/_3_lnt_bot/_0_lnt_wld_bot/jackal",
        "/World/jackal", "/jackal", "/World/Jackal", "/Jackal",
        "/World/Robot", "/Robot",
    ]
    for c in candidates:
        if stage.GetPrimAtPath(c).IsValid():
            robot_prim_path = c
            break

print(f"Robot articulation path: {robot_prim_path}")
if robot_prim_path is None:
    raise RuntimeError("Could not find robot articulation. Check prim paths in stage.")

# Jackal wheel params (standard clearpath values)
WHEEL_RADIUS = 0.098   # metres
WHEEL_BASE   = 0.37    # metres (distance between left and right wheels)
CMD_VEL_TOPIC = "/cmd_vel"

# ------------------------------------------------------------------
# Build the Action Graph
# ------------------------------------------------------------------
graph_path = "/World/DiffDriveGraph"

# Remove old graph if it exists
old = stage.GetPrimAtPath(graph_path)
if old.IsValid():
    omni.kit.commands.execute("DeletePrimsCommand", paths=[graph_path])

(graph, _, _, _) = og.Controller.edit(
    {"graph_path": graph_path, "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ROSContext",     "omni.isaac.ros2_bridge.ROS2Context"),
            ("SubTwist",       "omni.isaac.ros2_bridge.ROS2SubscribeTwist"),
            ("DiffDrive",      "omni.isaac.wheeled_robots.DifferentialController"),
            ("ArticCtrl",      "omni.isaac.core_nodes.IsaacArticulationController"),
        ],
        og.Controller.Keys.CONNECT: [
            # Tick drives everything
            ("OnPlaybackTick.outputs:tick",     "SubTwist.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick",     "ArticCtrl.inputs:execIn"),
            # ROS context
            ("ROSContext.outputs:context",      "SubTwist.inputs:context"),
            # Diff drive gets linear/angular from twist
            ("SubTwist.outputs:execOut",        "DiffDrive.inputs:execIn"),
            ("SubTwist.outputs:linearVelocity", "DiffDrive.inputs:linearVelocity"),
            ("SubTwist.outputs:angularVelocity","DiffDrive.inputs:angularVelocity"),
            # Diff drive outputs wheel speeds to articulation controller
            ("DiffDrive.outputs:velocityCommand","ArticCtrl.inputs:velocityCommands"),
        ],
        og.Controller.Keys.SET_VALUES: [
            ("SubTwist.inputs:topicName",        CMD_VEL_TOPIC),
            ("DiffDrive.inputs:wheelRadius",     WHEEL_RADIUS),
            ("DiffDrive.inputs:wheelDistance",   WHEEL_BASE),
            ("DiffDrive.inputs:maxLinearSpeed",  2.0),
            ("ArticCtrl.inputs:robotPath",       robot_prim_path),
            # Jackal wheel joint names (order: left, right)
            ("ArticCtrl.inputs:jointNames",      ["front_left_wheel_link", "front_right_wheel_link",
                                                  "rear_left_wheel_link", "rear_right_wheel_link"]),
            ("ArticCtrl.inputs:usePath",         True),
        ],
    },
)

print("SUCCESS: /cmd_vel differential drive graph created.")
print(f"  Robot: {robot_prim_path}")
print(f"  Subscribes to: {CMD_VEL_TOPIC}")
print(f"  Wheel radius: {WHEEL_RADIUS} m,  Wheel base: {WHEEL_BASE} m")
print("Press PLAY in Isaac Sim if it is not already running.")
