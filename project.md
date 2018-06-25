# FLICS Upgrade
## Python course final project, 2018
### Zvi Baratz, Amit Koren and Omer Granoviter

In our lab, we study the neurovascular response in mice _in vivo_. To that end, we need to measure blood flow, and changes in it, 
during imaging sessions. Up till recently, measuring blood flow required illuminating and scanning the mouse’s brain in a very 
specific pattern. This method works and has been validated on multiple occasions, but it very much limits the amount of information 
one can extract from these imaging sessions *besides* blood flow.

In 2014 an Italian group published [this paper](https://www.nature.com/articles/srep07341), introducing a new method to measure blood 
flow from standard imaging sessions. Only recently we were able to get the original code used for the article, and it’s absolutely 
horrifying. The code is extremely low quality, written in a very unclear manner with zero thought of performance and reusability.

The first goal is to re
