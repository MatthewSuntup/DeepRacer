# <img src="img/deepracer.png?raw=true" height="70">

<p align = center>
  <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/-AWS-232F3E?logo=amazon-aws&logoColor=white"/>
  <img src="https://img.shields.io/badge/-Sublime%20Text-DB6204?logo=sublime-text&logoColor=white"/>
  <img src="https://img.shields.io/badge/-Atom-239120?logo=atom&logoColor=white"/>
  <img src="https://img.shields.io/badge/-Git-D51007?logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white"/>
</p>

## About
This README provides an overview of how our team approached the University of Sydney's 2020 [AWS DeepRacer](https://aws.amazon.com/deepracer/) competition. This was a competition run by the School of Computer Science which provided teams with AWS credits to develop and train a DeepRacer model. Over the course of the model's development it was necessary to define an action space, develop a reward function for reinforcement learning, and experiment with various hyper-parameters controlling the underlying 3-layer neural network.

<p align="center">
<img src="img/race.png" width="50%">
</p>

### Team
<p align="center">
<a href="https://www.linkedin.com/in/ashanabey01/"><img src="img/linkedin_profile_aa.png" width="30%"></a>
<a href="https://www.linkedin.com/in/georgia-markham-37a905180/"><img src="img/linkedin_profile_gm.png" width="30%"></a>
<a href="https://www.linkedin.com/in/matthewsuntup/"><img src="img/linkedin_profile_ms.png" width="30%"></a>
</p>

### Contents
- [About](#About)
- [Results](#Results)
- [Development](#Development)
  - [Qualifier Model](#Qualifier-Model)
  - [Finals Model](#Finals-Model)
- [Conclusion](#Conclusion)
- [Acknowledgments](#Acknowledgments)

## Results
### USYD 2020 Finals (1st Place)
#### Track - Circuit de Barcelona-Catalunya
<p align="center">
<img src="img/final_results.png" width="70%">
</p>

### USYD 2020 Qualifier (1st Place)
#### Track - 2019 DeepRacer Championship Cup
<p align="center">
<img src="img/qualifier_results.png" width="70%">
</p>

## Development
### Qualifier Model
#### Defining the action space
The qualifier track was the 2019 DeepRacer Championship Cup track, which is a relatively straightforward loop with minor turns. We chose an action space with as few actions as possible (to reduce training time) while maintaining what we believed to be necessary actions to complete the track at speed. We chose a maximum speed of 3 m/s as a result of trial and error racing similar models with 2 and 4 m/s maximum speeds. A slower speed of 1.5 m/s was also chosen, allowing the vehicle to achieve intermediate speeds by switching between the two. As the turns are relatively smooth on this track, we limited the steering to 20 degrees, but still found it useful to include an intermediate steering angle for smaller corrections.

<p align="center">
<img src="img/qualifier_action_space.png" width="80%">
</p>

#### Developing the reward function
Initially, we trained the model on the much simpler Oval and Bowtie tracks using a centreline-following reward function with an incentive for faster speeds while travelling straight.

<p align="center">
<img src="img/simple_tracks.png" width=80%>
</p>

The sub-rewards can be seen in this code snippet from [reward_simple.py](reward/reward_simple.py):

```python
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
```
Note that we chose to add sub-rewards rather than multiply them, based on the experience of Daniel Gonzalez shared in "[An Advanced Guide to AWS DeepRacer](https://towardsdatascience.com/an-advanced-guide-to-aws-deepracer-2b462c37eea)".

We realised that a linear incentive for staying near the centre of the track would be limiting for the vehicle when it would be faster to "cut" the curvature of a turn. So the linear centreline sub-reward was replaced by a quadratic one, which meant the reward was less sensitive to small movements away from the centreline:

```python
# Give higher reward if the car is closer to centre line and vice versa
# 0 if you're on edge of track, 1 if you're centre of track
reward = 1 - (distance_from_center/(track_width/2))**2
```

An additional sub-reward was also included to encourage the vehicle to progress through the track faster relative to the number of steps taken (note the step-rate is constant at 15 Hz).
```python
# Reward progress
reward += progress/steps
```

Once the model was demonstrating a basic ability to follow the simple tracks, we moved onto the 2019 DeepRacer Championship Cup track.
<p align="center">
<img src="img/qualifier_track.png" width=40%>
</p>

A noticeable sticking point that the model ran into was an inability to take the North-West corner at high speeds (note this track is traversed anti-clockwise). Often it would approach the turn too quickly and be unable to position itself appropriately in time to take the turn successfully, an issue which we occasionally observed on other turns as well.  To address this, we implemented a method of detecting corners ahead of the vehicle using waypoint information and incentivised going slower in response to future corners.

```python
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
```

The `identify_corner()` function can be used to identify whether a corner exists between the car and a specified waypoint in the future. However, the spacing of waypoints is not consistent, so searching a constant number of waypoints ahead for a corner may cause the car to slow down unnecessarily when a corner is still far away. To mitigate this, after identifying a corner we check if it is within a minimum distance of the car. If not, the function is called again for a closer waypoint. We only use this method to check if a corner is too far away, as the identification of a far away straight almost always meant that the track prior was also straight due to both our method for identifying corners and the layout of this track.

```python
def select_speed(waypoints, closest_waypoints, future_step, mid_step):

    # Identify if a corner is in the future
    diff_heading, dist_future = identify_corner(waypoints, closest_waypoints, future_step)

    if diff_heading < TURN_THRESHOLD:
        # If there's no corner encourage going faster
        go_fast = True
    else:
        if dist_future < DIST_THRESHOLD:
            # If there is a corner and it's close encourage going slower
            go_fast = False
        else:
            # If the corner is far away, re-assess closer points
            diff_heading_mid, dist_mid = identify_corner(waypoints, closest_waypoints, mid_step)

            if diff_heading_mid < TURN_THRESHOLD:
                # If there's no corner encourage going faster
                go_fast = True
            else:
                # If there is a corner and it's close encourage going slower
                go_fast = False

    return go_fast
```
```python
# Implement speed incentive
go_fast = select_speed(waypoints, closest_waypoints, FUTURE_STEP, MID_STEP)

if go_fast and speed > SPEED_THRESHOLD:
    reward += 0.5

elif not go_fast and speed < SPEED_THRESHOLD:
    reward += 0.5  
```

We've now defined multiple parameters for our reward function which will affect when the car is incentivised to go faster or slower. To determine what the best values of these are, it is useful to visualise their effect. Using the track data provided by the Autonomous Race Car Community's [waypoint-visualization](https://github.com/ARCC-RACE/waypoint-visualization) git repository , and again taking inspiration from the [Advanced Guide to AWS DeepRacer](https://towardsdatascience.com/an-advanced-guide-to-aws-deepracer-2b462c37eea) article, we developed our own visualisation tool ([qualifier_planner.py](planning/qualifier_planner.py)) which identifies regions of the track where our [reward_qualifier.py](reward/reward_qualifier.py) function will reward the car for going faster or slower.

<p align="center">
<img src="img/qualifier_planner.png" width=80%>
</p>

The points labelled "Bonus Fast" show the effect of the additional distance check implemented in the `select_speed()` function discussed earlier (i.e. points which would have been marked "Slow" if the distance check was not incorporated). The actual reward function does not differentiate between "Fast" and "Bonus Fast" regions.

#### Tuning Hyperparameters
Tuning the hyperparameters of the neural network was crucial to ensuring the model was trained in a practical timeframe. Between training sessions, we would assess the reward graph and the Amazon Kinesis video stream of the evaluation runs to inform the modification of hyperparameters. Training sessions were between 45 minutes and 3 hours depending on the length of the track, stability of the most recent model, and hyperparameters chosen.

The most significant indicator for tuning was the average percentage completion during evaluation (the red points in the reward graph). These represented how far the car progressed before driving off course during evaluation runs. Early in the training process, it was beneficial to prioritise exploration of the action space through faster learning. To achieve this we use greater values for the learning rate, and reduce the gradient descent batch size and number of epochs. The reward graph below shows an example of an early version of our qualifier model, using training parameters that encourage much faster learning. The large variations in the average percentage completion (during evaluation) are reflective of this approach.

<p align="center">
<img src="img/qualifier_reward_graph_fast.png" width=50%>
</p>

As the model improved and our focus tended towards making minor adjustments to the driving style to benefit speed and reliability, we sought to stabilise learning. This was primarily achieved by reducing the learning rate, and increasing the gradient descent batch size, number of epochs, and number of experience episodes between each policy-updating iteration. The reward graph below is taken from one of the last training sessions on our qualifier model, and demonstrates more stable learning.

<p align="center">
<img src="img/qualifier_reward_graph_stable.png" width=50%>
</p>

### Finals Model
#### Redefining the action space
The finals track was the Circuit de Barcelona-Catalunya track, which consists of many sharp turns. It quickly became evident that our qualifier model would not be suited to the significantly different requirements of this track.
<p align="center">
<img src="img/finals_track.png" width=40%>
</p>

For the qualifier, we exclusively used the AWS DeepRacer console to setup the action space, however, this only allows for barebone customisation options, enforcing a linear distribution of actions. One of the greatest drawbacks of this is the wasted actions involving high speeds and high steering angles (as these are almost never used, unless the maximum speed is set very low). Manually modifying the action space is detailed in Kire Galev's "[AWS DeepRacer Expert Boot Camp](https://www.youtube.com/watch?v=BUMbqn4NqQA&ab_channel=AWSDeepRacerCommunity)", and allows us to initialise the model with a linear space using a low max speed, and then increase the speeds of the actions with lower steering angles. Doing this forms a bell curve shape, which enables us to have fewer overall actions than a linear action space would have required for this track. The result of this is reduced training time, as the underlying neural network becomes smaller.

We found that it was best to train this model with the slow, linear action space until it could reliably complete the course, and then increase the speed of specific actions before training it further to learn how to adapt to the new speeds. Repeating this process allowed us to rapidly improve the race time of the model. The process required significant trial and error to gauge the limits of how much the action space can stably be modified between training. The modifications that were trained along the way (disregarding reverted attempts) are shown below.

<p align="center">
<img src="img/finals_action_space_mods.png" width=70%>
</p>

It was most effective to increase the speed of actions associated with slow speed and low steering angles, as these are only used when the vehicle is travelling straight and generally reflected the model being overly cautious. The action space of the model that was entered into the finals race is shown below.

<p align="center">
<img src="img/finals_action_space.png" width="70%">
</p>

#### Iterating the reward function
The reward function used for the qualifier was the basis for that of the finals track ([reward_final.py](rewards/reward_final.py)). Some modifications were made, including the removal of the distance check used when calling the ```identify_corner()``` function which ensured we weren't looking too far ahead, as the waypoints for this track were spaced much more consistently.

```python
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
```
The visualisation script was updated to reflect this change ([final_planner.py](planning/final_planner.py)) and again used to determine the parameters relating to the speed incentive.

<p align="center">
<img src="img/finals_speed_planner.png" width=80%>
</p>

We noticed that over much of the course, the model was not actively being incentivised to go fast and straight (due to conservative parameters used for identifying corners), and some swerving behaviour was emerging. This was addressed with the addition of a sub-reward for maintaining steering angles within a bounded range. The condition for this to be applied used the same ```identify_corner()``` function that the speed sub-reward utilises, but with different parameters. This allowed us to encourage straighter driving over regions of the track where we did not necessarily want to incentivise faster speeds.

```python
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
```

<p align="center">
<img src="img/finals_straight_planner.png" width=80%>
</p>

Finally, to push the model to achieve faster lap times, the sub-reward incentivising progress was also modified to try and achieve specific targets. Since, steps occur at a rate of 15Hz (representing each action taken by the model), we can set a ```TOTAL_NUM_STEPS``` parameter to a value corresponding to a specific desired lap time. We would modify this number as the car achieved better lap times, generally setting it to be slightly below that of its previous best lap time. In the final training sessions we were aiming for a 45 second lap, and so set this value to 675 steps.

```python
# Every 50 steps, if it's ahead of expected position, give reward relative
# to how far ahead it is
if (steps % 50) == 0 and progress/100 > (steps/TOTAL_NUM_STEPS):
    # reward += 2.22 for each second faster than 45s projected
    reward += progress - (steps/TOTAL_NUM_STEPS)*100
```

## Conclusion
If nothing else, DeepRacer offers an exciting and fun application of machine learning. We all found this project to be an enjoyable activity to do alongside university studies and work commitments. While our team had a mix of past experiences with AWS and artificial intelligence, for all of us this was the first hands on experience we had with reinforcement learning algorithms. As is evident in the various articles referenced throughout this README, there's a lot more to explore in DeepRacer. If we do end up diving further into DeepRacer as hobby, I think we would all be keen to further leverage our familiarity with ROS and explore local training, as well as researching more into the inner workings of the training process.

## Acknowledgments
Our team would like to thank Zhiyong Wang from the University of Sydney for organising the competition, as well as Zoran Talesk and Jenny Davies from Amazon for their support throughout the development of our model.
