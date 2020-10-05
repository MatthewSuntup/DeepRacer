def reward_function(params):
    '''
    Reward function for AWS DeepRacer

    This reward function builds on the reward_combined_examples.py function to
    incorporate corner identification similar to that which can be seen in
    the reward_qualifier.py and reward_final.py functions.
    
    Team: IndestruciRacer
    Authors: Georgia Markham, Matthew Suntup, Ashan Abey
    August 2020
    '''


    import math

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering = params['steering_angle'] # Only need the absolute steering angle
    progress = params['progress']
    steps = params['steps']
    is_offtrack = params['is_offtrack']
    closest_waypoints = params['closest_waypoints']
    waypoints = params['waypoints']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    track_width = params['track_width']

    # Strongly discourage going off track
    if is_offtrack:
        reward = 1e-3
        return float(reward)

    ############ Center line training ############
    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward = 1.0
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3 # likely crashed/ close to off track

    ######### Relative track shape #########

    future_step = 9

    # Identify next waypoint and a further waypoint
    point_prev = waypoints[closest_waypoints[0]]
    point_next = waypoints[closest_waypoints[1]]
    point_future = waypoints[min(len(waypoints)-1,closest_waypoints[1]+future_step)]

    # Calculate headings to waypoints
    heading_current = math.degrees(math.atan2(point_prev[1]-point_next[1], point_prev[0]-point_next[0]))
    heading_future = math.degrees(math.atan2(point_prev[1]-point_future[1], point_prev[0]-point_future[0]))

    # Calculate the difference between the headings
    diff_heading = abs(heading_current-heading_future)

    # Check we didn't choose the reflex angle
    if diff_heading > 180:
        diff_heading = 360 - diff_heading

    # Calculate distance to further waypoint
    #dist_future = np.linalg.norm([point_next[0]-point_future[0],point_next[1]-point_future[1]])

    #### Penalise zig zagging on straight ####
    if diff_heading < 10:

        # Steering penality threshold, change the number based on your action space setting
        ABS_STEERING_THRESHOLD = 10

        # Penalize reward if the agent is steering too much
        if abs(steering) > ABS_STEERING_THRESHOLD:
            reward -= 0.5

    reward += (progress/steps)

    reward = max(reward, 1e-3)

    return float(reward)
