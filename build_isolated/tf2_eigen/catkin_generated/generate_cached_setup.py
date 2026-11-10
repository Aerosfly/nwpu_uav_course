# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import stat
import sys

# find the import for catkin's python package - either from source space or from an installed underlay
if os.path.exists(os.path.join('/opt/ros/noetic/share/catkin/cmake', 'catkinConfig.cmake.in')):
    sys.path.insert(0, os.path.join('/opt/ros/noetic/share/catkin/cmake', '..', 'python'))
try:
    from catkin.environment_cache import generate_environment_script
except ImportError:
    # search for catkin package in all workspaces and prepend to path
    for workspace in '/home/tianbot/tt_ws/devel_isolated/tf2_bullet;/home/tianbot/tt_ws/devel_isolated/tf2;/home/tianbot/tt_ws/devel_isolated/tf2_msgs;/home/tianbot/tt_ws/devel_isolated/rmtt_tracker;/home/tianbot/tt_ws/devel_isolated/rmtt_teleop;/home/tianbot/tt_ws/devel_isolated/rmtt_ros;/home/tianbot/tt_ws/devel_isolated/rmtt_driver;/home/tianbot/tt_ws/devel_isolated/rmtt_description;/home/tianbot/tt_ws/devel_isolated/rmtt_apriltag;/home/tianbot/tt_ws/devel_isolated/geometry2;/home/tianbot/tt_ws/devel_isolated/apriltag_ros;/home/tianbot/study_ws/devel;/home/tianbot/manipulation_ws/devel;/home/tianbot/tianbot_mini_ws/devel;/home/tianbot/tianbot_ws/devel;/home/tianbot/catkin_ws/devel;/opt/ros/noetic'.split(';'):
        python_path = os.path.join(workspace, 'lib/python3/dist-packages')
        if os.path.isdir(os.path.join(python_path, 'catkin')):
            sys.path.insert(0, python_path)
            break
    from catkin.environment_cache import generate_environment_script

code = generate_environment_script('/home/tianbot/tt_ws/devel_isolated/tf2_eigen/env.sh')

output_filename = '/home/tianbot/tt_ws/build_isolated/tf2_eigen/catkin_generated/setup_cached.sh'
with open(output_filename, 'w') as f:
    # print('Generate script for cached setup "%s"' % output_filename)
    f.write('\n'.join(code))

mode = os.stat(output_filename).st_mode
os.chmod(output_filename, mode | stat.S_IXUSR)
