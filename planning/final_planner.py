import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button

TRACK_FILE = "Spain_track.npy"

# Parameters for Speed Incentive
FUTURE_STEP_SPEED = 6
TURN_THRESHOLD_SPEED = 6    # degrees

# Parameters for Straightness Incentive
FUTURE_STEP_STRAIGHT = 8
TURN_THRESHOLD_STRAIGHT = 25    # degrees

FAST = 0
SLOW = 1

STRAIGHT = 0
CURVE = 1


def identify_corner(waypoints, closest_waypoints, future_step):

    # Identify next waypoint and a further waypoint
    point_prev = waypoints[closest_waypoints[0]]
    point_next = waypoints[closest_waypoints[1]]
    point_future = waypoints[min(len(waypoints)-1,closest_waypoints[1]+future_step)]

    # Calculate headings to waypoints
    heading_current = math.degrees(math.atan2(point_prev[1]-point_next[1], point_prev[0] - point_next[0]))
    heading_future = math.degrees(math.atan2(point_prev[1]-point_future[1], point_prev[0]-point_future[0]))

    # Calculate the difference between the headings
    diff_heading = abs(heading_current-heading_future)

    # Check we didn't choose the reflex angle
    if diff_heading > 180:
        diff_heading = 360 - diff_heading

    # Calculate distance to further waypoint
    dist_future = np.linalg.norm([point_next[0]-point_future[0],point_next[1]-point_future[1]])  

    return diff_heading, dist_future


def select_speed(waypoints, closest_waypoints, future_step):

    # Identify if a corner is in the future
    diff_heading, dist_future = identify_corner(waypoints, closest_waypoints, future_step)

    if diff_heading < TURN_THRESHOLD_SPEED:
        # If there's no corner encourage going faster
        go_fast = True
    else:
        # If there is a corner encourage slowing down
        go_fast = False

    return go_fast


def select_straight(waypoints, closest_waypoints, future_step):

    # Identify if a corner is in the future
    diff_heading, dist_future = identify_corner(waypoints, closest_waypoints, future_step)

    if diff_heading < TURN_THRESHOLD_STRAIGHT:
        # If there's no corner encourage going straighter
        go_straight = True
    else:
        # If there is a corner don't encourage going straighter
        go_straight = False

    return go_straight


# Get waypoints from numpy file
waypoints = np.load(TRACK_FILE)

print("--------- Parameters ---------")
print("      FUTURE_STEP_SPEED: %d" % (FUTURE_STEP_SPEED))
print("   TURN_THRESHOLD_SPEED: %d" % (TURN_THRESHOLD_SPEED))
print("   FUTURE_STEP_STRAIGHT: %d" % (FUTURE_STEP_STRAIGHT))
print("TURN_THRESHOLD_STRAIGHT: %d" % (TURN_THRESHOLD_STRAIGHT))
print("------------------------------")

# Extract the x and y columns from the waypoints
waypoints = waypoints[:,2:4]

speed_color_dict = {0:'#ff7f0e', 1:'#1f77b4'}
speed_label_dict = {0:'Fast Incentive', 1:'Slow Incentive'}

straight_color_dict = {0:'#ff7f0e', 1:'#1f77b4'}
straight_label_dict = {0:'Straight Incentive', 1:'No Incentive'}

speed_colours = []
straight_colours = []

for i in range(len(waypoints)):
    # Simulate input parameter
    closest_waypoints = [i-1, i]

    go_fast = select_speed(waypoints, closest_waypoints, FUTURE_STEP_SPEED)
    if go_fast:
        color = FAST
        speed_colours.append(color)
    else:
        color = SLOW
        speed_colours.append(color)

    go_straight = select_straight(waypoints, closest_waypoints, FUTURE_STEP_STRAIGHT)
    if go_straight:
        color = STRAIGHT
        straight_colours.append(color)
    else:
        color = CURVE
        straight_colours.append(color)


# Plot the points for the speed graph
fig_speed, ax_speed = plt.subplots()

for g in np.unique(speed_colours):
    ix = np.where(speed_colours==g)
    ax_speed.scatter(waypoints[ix,0], waypoints[ix,1], c=speed_color_dict[g], label=speed_label_dict[g])

# ax_speed.legend(title="Speed Incentive")
ax_speed.legend(loc='lower center', bbox_to_anchor=(0.5,-0.3), ncol=2, fancybox=True, shadow=True)
# ax_speed.set_title("Rewarded Speeds - Finals Track")
ax_speed.set_aspect('equal')
plt.axis('off')

# Set the points for the straight graph
fig_straight, ax_straight = plt.subplots()

for g in np.unique(straight_colours):
    ix = np.where(straight_colours==g)
    ax_straight.scatter(waypoints[ix,0], waypoints[ix,1], c=straight_color_dict[g], label=straight_label_dict[g])

# ax_straight.legend(title="Straight Incentive")
ax_straight.legend(loc='lower center', bbox_to_anchor=(0.5,-0.3), ncol=2, fancybox=True, shadow=True)
# ax_straight.set_title("Rewarded Straightness - Finals Track")
ax_straight.set_aspect('equal')
plt.axis('off')

plt.show()