import os

import numpy as np
from gym import spaces
import vrep
from a2c_ppo_acktr.envs.SawyerEnv import SawyerEnv, normalise_coords

from a2c_ppo_acktr.envs.VrepEnv import check_for_errors

np.set_printoptions(precision=2, linewidth=200)  # DEBUG
dir_path = os.getcwd()

cube_lower = np.array([0.15, (-0.35), 0.025])
cube_upper = np.array([0.45, (-0.65), 0.5])


class ReachOverWallEnv(SawyerEnv):

    scene_path = dir_path + '/reach_over_wall.ttt'
    observation_space = spaces.Box(np.array([0] * 11), np.array([1] * 11), dtype=np.float32)
    timestep = 0

    def __init__(self, seed, rank, headless, ep_len=64):
        super().__init__(seed, rank, self.scene_path, headless)

        self.ep_len = ep_len

        return_code, self.end_handle = vrep.simxGetObjectHandle(self.cid,
                "Waypoint_tip", vrep.simx_opmode_blocking)
        check_for_errors(return_code)
        self.end_pose = self.get_end_pose()
        return_code, self.target_handle = vrep.simxGetObjectHandle(self.cid,
                "Cube", vrep.simx_opmode_blocking)
        check_for_errors(return_code)
        return_code, self.target_pos = vrep.simxGetObjectPosition(self.cid, self.target_handle,
                -1, vrep.simx_opmode_blocking)
        check_for_errors(return_code)
        self.target_norm = normalise_coords(self.target_pos, cube_lower, cube_upper)
        return_code, self.wall_handle = vrep.simxGetObjectHandle(self.cid,
                "Wall", vrep.simx_opmode_blocking)
        check_for_errors(return_code)
        self.init_wall_pos = vrep.simxGetObjectPosition(self.cid, self.wall_handle,
                -1, vrep.simx_opmode_blocking)[1]
        self.wall_distance = normalise_coords(self.init_wall_pos[0], lower=0, upper=1)
        self.init_wall_rot = vrep.simxGetObjectOrientation(self.cid,
                self.wall_handle, -1, vrep.simx_opmode_blocking)[1]
        self.wall_orientation = self.init_wall_rot

    def reset(self):
        super(ReachOverWallEnv, self).reset()
        vrep.simxSetObjectPosition(self.cid, self.wall_handle, -1, self.init_wall_pos,
                                   vrep.simx_opmode_blocking)
        vrep.simxSetObjectOrientation(self.cid, self.wall_handle, -1, self.init_wall_rot,
                                      vrep.simx_opmode_blocking)
        self.timestep = 0

        return self._get_obs()

    def step(self, a):
        self.target_velocities = a  # Residual RL
        vec = self.end_pose - self.target_pos

        self.timestep += 1
        self.update_sim()

        self.wall_orientation = vrep.simxGetObjectOrientation(self.cid, self.wall_handle, -1,
                                                              vrep.simx_opmode_blocking)[1]
        ob = self._get_obs()
        done = (self.timestep == self.ep_len)

        reward_dist = - np.linalg.norm(vec)
        reward_ctrl = - np.square(self.target_velocities).mean()
        reward_obstacle = - np.abs(self.wall_orientation).sum()
        reward = 0.01 * (reward_dist + reward_ctrl + 0.2 * reward_obstacle)

        return ob, reward, done, dict(reward_dist=reward_dist,
                                      reward_ctrl=reward_ctrl,
                                      reward_obstacle=reward_obstacle)

    def _get_obs(self):
        joint_obs = super(ReachOverWallEnv, self)._get_obs()
        self.end_pose = self.get_end_pose()

        return np.concatenate((joint_obs, self.target_norm, [self.wall_distance]))

    def get_end_pose(self):
        pose = vrep.simxGetObjectPosition(self.cid, self.end_handle, -1,
                                          vrep.simx_opmode_blocking)[1]
        return np.array(pose)


class ROWRandomTargetEnv(ReachOverWallEnv):

    def reset(self):
        self.target_pos[0] = self.np_random.uniform(cube_lower[0], cube_upper[0])
        self.target_pos[1] = self.np_random.uniform(cube_lower[1], cube_upper[1])
        self.target_norm = normalise_coords(self.target_pos, cube_lower, cube_upper)
        vrep.simxSetObjectPosition(self.cid, self.target_handle, -1, self.target_pos,
                                   vrep.simx_opmode_blocking)
        return super(ROWRandomTargetEnv, self).reset()


class ReachNoWallEnv(ROWRandomTargetEnv):

    observation_space = spaces.Box(np.array([0] * 10), np.array([1] * 10), dtype=np.float32)
    scene_path = dir_path + '/reach_no_wall.ttt'

    def step(self, a):
        self.target_velocities = a
        vec = self.end_pose - self.target_pos

        self.timestep += 1
        self.update_sim()

        ob = self._get_obs()
        done = (self.timestep == self.ep_len)

        reward_dist = - np.linalg.norm(vec)
        reward_ctrl = - np.square(self.target_velocities).mean()
        reward = 0.01 * (reward_dist + reward_ctrl)

        return ob, reward, done, dict(reward_dist=reward_dist, reward_ctrl=reward_ctrl)

    def _get_obs(self):
        full_obs = super(ReachNoWallEnv, self)._get_obs()
        return full_obs[:-1]