def reward_function(params):
    '''
    Reward function for AWS DeepRacer

    This reward function was experimented with when we first considered using
    waypoints to predict turns in the future. This function calculates a target
    heading using two base headings, AB and BC, where point A is the car's
    current position and point B and C are some waypoints ahead of the car.
    After using this function we found this was much less reliable than
    identifying corners by comparing the orientation of the track ahead with
    the orientation of the current track (using the two closest waypoints) and
    avoiding considering the exact position of the car. This concept was
    implemented in future reward functions.
    
    Team: IndestruciRacer
    Authors: Matthew Suntup, Georgia Markham, Ashan Abey
    August 2020
    '''
    
    import math
    import numpy as np
    
    # Multipliers used in calculating the weighting of the two headings for
    # the weighted average target
    AB_MULTIPLIER = 0.7
    BC_MULTIPLIER = 0.3

    FUTURE_STEP = 5

    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    is_offtrack = params['is_offtrack']
    speed = params['speed']
    steering_angle = params['steering_angle']
    waypoints = params['waypoints']
    x = params['x']
    y = params['y']
    
    # Strongly discourage going off track
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3
        return float(reward)
    
    # Identify next waypoint and further waypoint    
    point_b = waypoints[closest_waypoints[1]]
    point_c = waypoints[min(len(waypoints) - 1, 
                            closest_waypoints[1] + FUTURE_STEP)]
    
    # Calculate headings to waypoints
    ab_heading = math.degrees(math.atan2(point_b[1] - y, point_b[0] - x))
    bc_heading = math.degrees(math.atan2(point_c[1] - point_b[1], 
                                         point_c[0] - point_b[0]))
    
    # Calculate distance to waypoints
    ab_dist = np.linalg.norm([x-point_b[0],y-point_b[1]])
    ac_dist = np.linalg.norm([x-point_c[0],y-point_c[1]])

    # Weigh next waypoint proportionally with distance
    ab_weight = ab_dist * AB_MULTIPLIER
    
    # Weight further waypoint inversely proportionally with distance
    bc_weight = 1/ac_dist * BC_MULTIPLIER
    
    # Circular Heading Calculations
    if ab_heading > bc_heading and ab_heading - bc_heading > 180:
        heading_offset = 180 - ab_heading
        ab_heading = -180
        bc_heading = bc_heading + heading_offset
        heading = heading + heading_offset
        if heading > 180:
            heading = 360 - heading
        
    elif bc_heading > ab_heading and bc_heading - ab_heading > 180:
        heading_offset = 180 - bc_heading
        bc_heading = -180
        ab_heading = ab_heading + heading_offset
        heading = heading + heading_offset
        if heading > 180:
            heading = 360 - heading
    
    # Calculate weighted average of headings
    tot_weight = ab_weight + bc_weight
    goal_heading = (ab_heading*ab_weight + bc_heading*bc_weight)/tot_weight
    
    # Calculate heading error
    err_heading = abs(goal_heading - heading)
    if err_heading >= 180:
        err_heading = 180 - err_heading
    
    # Apply reward function to heading error
    reward = -1/(180**2)*err_heading**2 + 1
    
    # Encourage faster speed
    speed_mult = speed
    
    # Discourage sharp turns
    steering_mult = -1/(180**2)*steering_angle**2 + 1
    reward = reward*speed_mult
    
    if reward <= 1e-3:
        reward = 1e-3
    
    return float(reward)