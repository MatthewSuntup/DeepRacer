def reward_function(params):
    '''
    Reward function for AWS DeepRacer
    Team: IndestruciRacer
    Authors: Matthew Suntup, Georgia Markham, Ashan Abey
    August 2020
    '''
    
    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    is_offtrack = params['is_offtrack']
    speed = params['speed']
    steering_angle = params['steering_angle']
    track_width = params['track_width']
    
    # Params
    max_speed = 4

    # Strongly discourage going off track
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3
        return float(reward)
    
    # Give higher reward if the car is closer to centre line and vice versa
    # 0 if you're on edge of track, 1 if you're centre of track
    reward = 1 - distance_from_center/(track_width/2)

    # Reward going faster when the car isn't turning
    if abs(steering_angle) < 10 and speed > 2:
        reward += speed/max_speed
      
    return float(reward)