import matplotlib.pyplot as plt
import numpy as np
import math

FUTURE_STEP = 7
MID_STEP = 4
TURN_THRESHOLD = 10    # degrees
DIST_THRESHOLD = 1.2    # metres


def identify_corner(waypoints, i, future_step):
    closest_waypoints = [i-1, i]

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




# Track Name from Tracks List
track_name = "ChampionshipCup2019_track"
# Location of tracks folder
absolute_path = "."
# Get waypoints from numpy file
waypoints = np.load("%s.npy" % (track_name))
# Get number of waypoints
print("Number of waypoints = " + str(waypoints.shape[0]))
print("FUTURE_STEP: %d" % (FUTURE_STEP))
print("MID_STEP: %d" % (MID_STEP))
print("TURN_THRESHOLD: %d" % (TURN_THRESHOLD))
print("DIST_THRESHOLD: %.1f" % (DIST_THRESHOLD))


# Extract the x and y columns from the waypoints
waypoints = waypoints[:,2:4]

# Plot waypoints
fast_colour = '#ff7f0e'
slow_colour = '#1f77b4'
bonus_fast_colour = '#ff460e'
bonus_slow_colour = '#4e1fb4'
for i in range(len(waypoints)):
    diff_heading, dist_future = identify_corner(waypoints, i, FUTURE_STEP)

    if diff_heading < TURN_THRESHOLD:
        color = fast_colour
    else:
        if dist_future < DIST_THRESHOLD:
            color = slow_colour
        else:
            diff_heading_mid, dist_mid = identify_corner(waypoints, i, MID_STEP)

            if diff_heading_mid < TURN_THRESHOLD:
                color = bonus_fast_colour
            else:
                color = slow_colour

    if i/len(waypoints) > 0.80:
        color = bonus_slow_colour

    plt.scatter(waypoints[i][0], waypoints[i][1], c=color)
    # print("Waypoint " + str(i) + ": " + str(waypoints[i]))

plt.show()