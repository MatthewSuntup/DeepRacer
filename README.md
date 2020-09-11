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

### Team
- [Ashan Abey](https://github.com/ashton3000)
- [Georgia Markham](https://github.com/georgiemarkham)
- [Matthew Suntup](https://github.com/MatthewSuntup)

<p align="center">
<img src="img/race.png" width="50%">
</p>

## Development
### Qualifier Model
#### Defining the action space
The qualifier track was the 2019 DeepRacer Championship Cup track, which is a relatively straightforward circular track with slight turns. We chose an action space with as few actions as possible (to reduce training time) while maintaining what we believed to be necessary actions to complete the track at speed. We chose a maximum speed of 3 m/s, as a result of trial and error racing similar models with 2 and 4 m/s maximum speeds. A "slow" speed option of 1.5 m/s was also chosen allowing the vehicle to achieve intermediate speeds when switching between them. As the turns are not extremely sharp, we limited the steering to 20 degrees, and found it useful to include an intermediate steering angle for smaller corrections.

<p align="center">
<img src="img/qualifier_action_space.png" width="80%">
</p>



## Results
### Qualifier
#### Track - 2019 DeepRacer Championship Cup
<p align="center">
<img src="img/qualifier_results.png" width="70%">
</p>

### Finals
#### Track - Circuit de Barcelona-Catalunya
<p align="center">
<img src="img/final_results.png" width="70%">
</p>
