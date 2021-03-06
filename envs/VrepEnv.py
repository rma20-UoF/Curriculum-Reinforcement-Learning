import atexit
import os
import platform
import signal
import time

import numpy as np
from gym import Env
from subprocess import Popen, DEVNULL
import vrep


# Function to check for errors when calling a remote API function
def check_for_errors(code):
    if code == vrep.simx_return_ok:
        return
    elif code == vrep.simx_return_timeout_flag:
        raise RuntimeError('The function timed out (probably the network is down or too slow)')
    elif code == vrep.simx_return_novalue_flag:
        # Often, not really an error, so just ignore
        pass
    elif code == vrep.simx_return_illegal_opmode_flag:
        raise RuntimeError('The specified operation mode is not supported for the given function')
    elif code == vrep.simx_return_remote_error_flag:
        raise RuntimeError('The function caused an error on the server side (e.g. an invalid handle was specified)')
    elif code == vrep.simx_return_split_progress_flag:
        raise RuntimeError('The communication thread is still processing previous split command of the same type')
    elif code == vrep.simx_return_local_error_flag:
        raise RuntimeError('The function caused an error on the client side')
    elif code == vrep.simx_return_initialize_error_flag:
        raise RuntimeError('A connection to vrep has not been made yet. Have you called connect()?')


# Function to check for errors when calling a remote API function
def catch_errors(input):
    if isinstance(input, tuple):
        code = input[0]
        values = input[1] if len(input) == 2 else input[1:]
    else:
        code = input
        values = None
    check_for_errors(code)
    return values


# Define the port number where communication will be made to the V-Rep server
base_port_num = 19998
# Define the host where this communication is taking place
host = '127.0.0.1'

scene_dir_path = os.path.join(os.getcwd(), 'scenes')
# Insert path here - perhaps abstract this away to a config file?
vrep_path = os.path.expanduser('~/Applications/V-REP_PRO_EDU_V3_6_1_Mac/vrep.app'
                               '/Contents/MacOS/vrep') \
    if platform.system() == 'Darwin' else \
    os.path.expanduser('~/Desktop/V-REP_PRO_EDU_V3_6_1_Ubuntu18_04/vrep.sh')
# This allowed V-Rep to be run over SSH to an Ubuntu machine.
# See forum.coppeliarobotics.com/viewtopic.php?p=29772
xvfb_args = ['xvfb-run', '--auto-servernum', '--server-num=1'] \
    if not platform.system() == 'Darwin' else []


class VrepEnv(Env):
    """
    An environment with behind-the-scenes handled by a scene in V-Rep. This abstract parent class
    allows its children to function as any regular OpenAI Gym environment, handling the
    set-up and tear-down of an associated V-Rep scene.
    """

    def __init__(self, scene_name, rank, headless):
        # Launch a V-Rep server
        # Read more here: http://www.coppeliarobotics.com/helpFiles/en/commandLine.htm
        port_num = base_port_num + rank
        remote_api_string = '-gREMOTEAPISERVERSERVICE_' + str(port_num) + '_FALSE_TRUE'
        args = [*xvfb_args, vrep_path, '-h' if headless else '', remote_api_string]
        self.cid = -1
        while self.cid == -1:
            self.process = Popen(args, preexec_fn=os.setsid, stdout=DEVNULL)
            time.sleep(6)
            self.cid = vrep.simxStart(host, port_num, True, True, 5000, 5)
            if self.cid == -1:
                print(f"{rank} failed to connect to V-REP. Retrying...")
                try:
                    pgrp = os.getpgid(self.process.pid)
                    os.killpg(pgrp, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        catch_errors(vrep.simxSynchronous(self.cid, enable=True))

        scene_path = os.path.join(scene_dir_path, f'{scene_name}.ttt')
        catch_errors(vrep.simxLoadScene(self.cid, scene_path, 0, vrep.simx_opmode_blocking))
        atexit.register(self.close)

    # Function to call a Lua function in V-Rep
    # Read more here: http://www.coppeliarobotics.com/helpFiles/en/remoteApiExtension.htm
    def call_lua_function(self, lua_function, ints=[], floats=[], strings=[],
                          bytes=bytearray(), opmode=vrep.simx_opmode_blocking):
        return_code, out_ints, out_floats, out_strings, out_buffer = vrep.simxCallScriptFunction(
            self.cid, 'remote_api', vrep.sim_scripttype_customizationscript, lua_function, ints,
            floats, strings, bytes, opmode)
        check_for_errors(return_code)
        return out_ints, out_floats, out_strings, out_buffer

    def close(self):
        # Shutdown
        print("Closing VREP")
        vrep.simxStopSimulation(self.cid, vrep.simx_opmode_blocking)
        vrep.simxFinish(self.cid)
        atexit.unregister(self.close)
        try:
            pgrp = os.getpgid(self.process.pid)
            os.killpg(pgrp, signal.SIGKILL)
        except ProcessLookupError:
            pass

    # Rendering not implemented by default. See DishRackEnv for a more specific implementation.
    def render(self, mode='human'):
        pass

    # Returns a vector from one item to another under "from"s axes (not the world axes).
    def get_vector(self, from_handle, to_handle):
        pose = catch_errors(vrep.simxGetObjectPosition(
            self.cid, to_handle, from_handle, vrep.simx_opmode_blocking))
        return np.array(pose)

    def get_position(self, handle):
        return self.get_vector(-1, handle)

    def get_distance(self, from_handle, to_handle):
        return np.linalg.norm(self.get_vector(from_handle, to_handle))
