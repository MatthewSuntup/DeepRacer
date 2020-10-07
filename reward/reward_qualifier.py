def reward_function(params):
    '''
    Reward function for AWS DeepRacer
    Used in USYD 2020 Qualifier in the 2019 Championship track
    Team: IndestruciRacer
    Authors: Matthew Suntup, Georgia Markham, Ashan Abey
    August 2020
    '''
    
    import math
    import numpy as np
    
    # Parameters
    FUTURE_STEP = 7
    MID_STEP = 4
    TURN_THRESHOLD = 10     # degrees
    DIST_THRESHOLD = 1.2    # metres
    SPEED_THRESHOLD = 1.8   # m/s


    def identify_corner(waypoints, closest_waypoints, future_step):

        # Identify next waypoint and a further waypoint
        point_prev = waypoints[closest_waypoints[0]]
        point_next = waypoints[closest_waypoints[1]]
        point_future = waypoints[min(len(waypoints) - 1, 
                                     closest_waypoints[1] + future_step)]

        # Calculate headings to waypoints
        heading_current = math.degrees(math.atan2(point_prev[1] - point_next[1], 
                                                 point_prev[0] - point_next[0]))
        heading_future = math.degrees(math.atan2(point_prev[1] - point_future[1], 
                                                 point_prev[0]-point_future[0]))

        # Calculate the difference between the headings
        diff_heading = abs(heading_current - heading_future)

        # Check we didn't choose the reflex angle
        if diff_heading > 180:
            diff_heading = 360 - diff_heading

        # Calculate distance to further waypoint
        dist_future = np.linalg.norm([point_next[0] - point_future[0],
                                      point_next[1] - point_future[1]])  

        return diff_heading, dist_future


    def select_speed(waypoints, closest_waypoints, future_step, mid_step):

        # Identify if a corner is in the future
        diff_heading, dist_future = identify_corner(waypoints, 
                                                    closest_waypoints, 
                                                    future_step)

        if diff_heading < TURN_THRESHOLD:
            # If there's no corner encourage going faster
            go_fast = True
        else:
            if dist_future < DIST_THRESHOLD:
                # If there is a corner and it's close encourage going slower
                go_fast = False
            else:
                # If the corner is far away, re-assess closer points
                diff_heading_mid, dist_mid = identify_corner(waypoints, 
                                                             closest_waypoints, 
                                                             mid_step)

                if diff_heading_mid < TURN_THRESHOLD:
                    # If there's no corner encourage going faster
                    go_fast = True
                else:
                    # If there is a corner and it's close encourage going slower
                    go_fast = False

        return go_fast


    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    is_offtrack = params['is_offtrack']
    progress = params['progress']
    speed = params['speed']
    steps = params['steps']
    track_width = params['track_width']
    waypoints = params['waypoints']

    # Strongly discourage going off track
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3
        return float(reward)
    
    # Give higher reward if the car is closer to centre line and vice versa
    # 0 if you're on edge of track, 1 if you're centre of track
    reward = 1 - (distance_from_center/(track_width/2))**(1/4) 
             + progress/steps

    go_fast = select_speed(waypoints, closest_waypoints, FUTURE_STEP, MID_STEP)

    # Implement speed incentive
    if go_fast and speed > SPEED_THRESHOLD:
        reward += 0.5

    elif not go_fast and speed < SPEED_THRESHOLD:
        reward += 0.5    
      
    return float(reward)