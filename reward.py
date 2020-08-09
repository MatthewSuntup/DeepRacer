def reward_function(params):
    '''
    Our custom reward function
    '''
    
    import math
    import numpy as np
    
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
    point_c = waypoints[min(len(waypoints)-1,closest_waypoints[1]+5)]
    
    # Calculate headings to waypoints
    ab_heading = math.degrees(math.atan2(point_b[1]-y, point_b[0] - x))
    bc_heading = math.degrees(math.atan2(point_c[1]-point_b[1], point_c[0]-point_b[0]))
    
    # Calculate distance to waypoints
    ab_dist = np.linalg.norm([x-point_b[0],y-point_b[1]])
    ac_dist = np.linalg.norm([x-point_c[0],y-point_c[1]])

    # Weigh next waypoint proportionally with distance
    ab_weight = ab_dist * 0.7
    
    # Weight further waypoint inversely proportionally with distance
    bc_weight = 1/ac_dist * 0.3
    
    # Circular Heading Calculations
    if ab_heading > bc_heading and ab_heading - bc_heading > 180:
        heading_offset = 180-ab_heading
        ab_heading = -180
        bc_heading = bc_heading + heading_offset
        heading = heading + heading_offset
        if heading > 180:
            heading = 360 - heading
        
    elif bc_heading > ab_heading and bc_heading - ab_heading > 180:
        heading_offset = 180-bc_heading
        bc_heading = -180
        ab_heading = ab_heading + heading_offset
        heading = heading + heading_offset
        if heading > 180:
            heading = 360 - heading
    
    # Calculate weighted average of headings
    tot_weight = ab_weight + bc_weight
    goal_heading = (ab_heading*ab_weight + bc_heading*bc_weight)/tot_weight
    
    # Calculate heading error
    err_heading = abs(goal_heading-heading)
    if err_heading >= 180:
        err_heading = 180 - err_heading
    
    # Apply reward function to heading error
    reward = -1/(180**2) *err_heading**2 + 1
    
    # Encourage faster speed
    max_speed = 1
    speed_mult = speed/max_speed
    
    # Discourage sharp turns
    steering_mult = -1/(180**2) *steering_angle**2 + 1
    reward = reward*speed_mult
    
    if reward <= 1e-3:
        reward = 1e-3
    
    return float(reward)