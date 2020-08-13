def reward_function(params):
    '''
    Our custom reward function
    '''
    
    import math
    import numpy as np
    
    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    heading = params['heading']
    is_offtrack = params['is_offtrack']
    progress = params['progress']
    speed = params['speed']
    steering_angle = params['steering_angle']
    steps = params['steps']
    track_width = params['track_width']
    waypoints = params['waypoints']
    x = params['x']
    y = params['y']
    
    # Params
    max_speed = 4

    # Strongly discourage going off track
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3
        return float(reward)
    
    # Give higher reward if the car is closer to centre line and vice versa
    # 0 if you're on edge of track, 1 if you're centre of track
    reward = 1 - (distance_from_center/(track_width/2))**(1/4) + progress/steps

    if abs(steering_angle) < 10 and speed > 2:
        reward += 0.5

    if abs(steering_angle) > 10 and speed < 2:
        reward += 0.5
      
    return float(reward)