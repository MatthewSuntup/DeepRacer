def reward_function(params):
    '''
    Reward function for AWS DeepRacer

    This reward function was used on some of our initial models, in lieu of 
    reward_simple.py. The function originates from Juv Chan's article, "Train a
    Viable Model in 45 minutes for AWS DeepRacer Beginner Challenge Virtual
    Community Race 2020", with the code itself a direct conglomerate of the AWS
    DeepRacer example reward functions. 
    
    Team: IndestruciRacer
    Authors: Georgia Markham, Matthew Suntup, Ashan Abey
    August 2020
    '''

    import math

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering = abs(params['steering_angle']) # Only need the absolute steering angle
    progress = params['progress']
    steps = params['steps']
    speed = params['speed']
    waypoints = params['waypoints']
    x = params['x']
    y = params['y']
    closest_waypoints = params['closest_waypoints']
    is_offtrack = params['is_offtrack']

    # Strongly discourage going off track
    if is_offtrack:
        reward = 1e-3
        return float(reward)

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

    # Steering penality threshold, change the number based on your action space setting
    ABS_STEERING_THRESHOLD = 15

    # Penalize reward if the agent is steering too much
    if steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8

    reward *= (progress/steps)*2

    ####################
    future_step = 5

    # Identify next waypoint and further waypoint
    point_prev = waypoints[closest_waypoints[0]]
    point_next = waypoints[closest_waypoints[1]]
    point_future = waypoints[min(len(waypoints)-1,closest_waypoints[1]+future_step)]

    # Calculate headings to waypoints
    heading_current = math.degrees(math.atan2(point_prev[1]-point_next[1], point_prev[0]-point_next[0]))
    heading_future = math.degrees(math.atan2(point_prev[1]-point_future[1], point_prev[0]-point_future[0]))

    # Circular Heading Calculations
    if heading_current > heading_future and heading_current - heading_future > 180:
        heading_offset = 180-heading_current
        heading_current = -180
        heading_future += heading_offset

    elif heading_future > heading_current and heading_future - heading_current > 180:
        heading_offset = 180-heading_future
        heading_future = -180
        heading_current += heading_offset

    # Calculate the difference between the headings
    diff_heading = abs(heading_current-heading_future)

    if diff_heading < 10 and speed > 2.5:
        reward *= 1.5

    if diff_heading > 10 and speed < 2.5:
        reward *= 1.5

    return float(reward)
