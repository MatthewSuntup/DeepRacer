def reward_function(params):
    '''
    Reward function for AWS DeepRacer

    This reward function was used on some of our initial models, in lieu of 
    reward_simple.py. The first part of the function originates from Juv Chan's 
    article, "Train a Viable Model in 45 minutes for AWS DeepRacer Beginner 
    Challenge Virtual Community Race 2020", who wrote a conglomerate of the AWS
    DeepRacer example reward functions. The second part of the function uses
    waypoints to identify a target heading and incentivise the vehicle towards
    it, similar to reward_extended.py.
    
    Team: IndestruciRacer
    Authors: Georgia Markham, Matthew Suntup, Ashan Abey
    August 2020
    '''

    import math

    # Read input parameters
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    is_offtrack = params['is_offtrack']
    progress = params['progress']
    speed = params['speed']
    steering = abs(params['steering_angle']) # Only need the absolute angle
    steps = params['steps']
    track_width = params['track_width']
    waypoints = params['waypoints']
    x = params['x']
    y = params['y']

    # Strongly discourage going off track
    if is_offtrack:
        reward = 1e-3
        return float(reward)

    # Calculate 3 markers that are at varying distances from the centre line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Give higher reward if the car is closer to centre line and vice versa
    if distance_from_center <= marker_1:
        reward = 1.0
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3 # likely crashed/ close to off track

    # Steering penality threshold, based on action space
    ABS_STEERING_THRESHOLD = 15

    # Penalize reward if the agent is steering too much
    if steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8

    reward *= (progress/steps)*2

    # Incentivising target heading using waypoint method
    FUTURE_STEP = 5

    # Identify next waypoint and further waypoint
    point_prev = waypoints[closest_waypoints[0]]
    point_next = waypoints[closest_waypoints[1]]
    point_future = waypoints[min(len(waypoints) - 1, 
                                 closest_waypoints[1] + FUTURE_STEP)]

    # Calculate headings to waypoints
    heading_current = math.degrees(math.atan2(point_prev[1] - point_next[1], 
                                              point_prev[0] - point_next[0]))
    heading_future = math.degrees(math.atan2(point_prev[1] - point_future[1], 
                                             point_prev[0] - point_future[0]))

    # Circular Heading Calculations
    if heading_current > heading_future and 
       heading_current - heading_future > 180:
        heading_offset = 180-heading_current
        heading_current = -180
        heading_future += heading_offset

    elif heading_future > heading_current and 
         heading_future - heading_current > 180:
        heading_offset = 180-heading_future
        heading_future = -180
        heading_current += heading_offset

    # Calculate the difference between the headings
    diff_heading = abs(heading_current - heading_future)

    if diff_heading < 10 and speed > 2.5:
        reward *= 1.5

    if diff_heading > 10 and speed < 2.5:
        reward *= 1.5

    return float(reward)
