def reward_function(params):
    '''
    Our custom reward function
    '''
    
    import math
    import numpy as np
    
    # Params
    FUTURE_STEP = 7
    MID_STEP = 4
    TURN_THRESHOLD = 10     # degrees
    DIST_THRESHOLD = 1.2    # metres

    def identify_corner(waypoints, closest_waypoints, future_step):

        # Identify next waypoint and further waypoint
        point_prev = waypoints[closest_waypoints[0]]
        point_next = waypoints[closest_waypoints[1]]
        point_future = waypoints[min(len(waypoints)-1,closest_waypoints[1]+future_step)]

        # Calculate headings to waypoints
        heading_current = math.degrees(math.atan2(point_prev[1]-point_next[1], point_prev[0] - point_next[0]))
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

        # Calculate distance to waypoints
        dist_future = np.linalg.norm([point_next[0]-point_future[0],point_next[1]-point_future[1]])  

        return diff_heading, dist_future


    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    is_offtrack = params['is_offtrack']
    progress = params['progress']
    speed = params['speed']
    steering_angle = params['steering_angle']
    steps = params['steps']
    track_width = params['track_width']
    waypoints = params['waypoints']

    # Strongly discourage going off track
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3
        return float(reward)
    
    # Give higher reward if the car is closer to centre line and vice versa
    # 0 if you're on edge of track, 1 if you're centre of track
    reward = 1 - (distance_from_center/(track_width/2))**(1/4) + progress/steps

    diff_heading, dist_future = identify_corner(waypoints, closest_waypoints, FUTURE_STEP)

    go_fast = True

    if diff_heading < TURN_THRESHOLD:
        go_fast = True

    else:
        if dist_future < DIST_THRESHOLD:
            go_fast = True
        else:
            diff_heading_mid, dist_mid = identify_corner(waypoints, closest_waypoints, MID_STEP)

            if diff_heading_mid < TURN_THRESHOLD:
                go_fast = True
            else:
                go_fast = False

    # Slow down towards the end of the track
    if progress > 80:
        go_fast = False

    if go_fast and speed > 2:
        reward += 0.5

    elif not go_fast and speed < 2:
        reward += 0.5    
      
    return float(reward)