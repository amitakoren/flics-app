# FLICS Upgrade
## Python course final project, 2018
### Zvi Baratz, Amit Koren and Omer Granoviter

In our lab (Pablo Blinder's), we study the neurovascular response in mice _in vivo_. To that end, we need to measure blood flow, and changes in it, during imaging sessions. Up till recently, measuring blood flow required illuminating and scanning the mouse’s brain in a very specific pattern. This method works and has been validated on multiple occasions, but it very much limits the amount of information one can extract from these imaging sessions **besides** blood flow. 

In 2014 an Italian group published [this paper](https://www.nature.com/articles/srep07341), introducing a new method to measure blood flow from standard imaging sessions. Its input is a time lapse movie containing stained vasculature, as seen in the GIF below, and the regions of interest with vessels you wish to measure. A few other parameters, like the frame rate of the movie, are also required. Its output is the rate of blood flow over time in each region of interest. Recently we received the original code used in the article, with purpose in mind to use it for our own research, but unfortunately it’s absolutely horrifying. The code is extremely low quality, written in a very unclear manner with zero thought of performance and reusability.

![Stained vasculature example](bloodflow.gif)

Assuming the code is doing its job, albeit poorly, we want students in our lab to use this algorithm to calculate blood flow without writing more code. To that end we've written a GUI into which you load an existing time lapse movie of a recording you've made. Then you may choose the regions of interest in that image, and when you press a button it passes this data to the algorithm, displaying the result. This GUI is already written and working, but we'd like it further polished, especially in the back-end side of things - saving the results of the analysis is currently improperly handled, and we'd like to fix that.

## Tasks overview
The first thing you should do is read the paper. It's technical, but don't let the equations fool you, the actual implementation is much simpler (perhaps even alarmingly simple). Then you should all be able to run the basic code, located in the `flics` subdirectory, and receive similar results to the ones shown in the `review_box.docx` file. Finally, try running the GUI code named `XXX.py`. The GUI was written with PyQT and should be pretty simple to run and edit, once you have a basic understanding of QT applications.

## Subgroups division
### Code upgrade - Zvi
The code is [`flics_data/flics.py`](flics_data/flics.py). The first thing to do is to run it and verify that the results are similar to the ones in the article. Save these results and regard them as your "ground truth", since after you start refactoring you'll have to double check that you haven't changed the actual alogrithm's output.

Then starts the actual refactoring process. I trust in you to make wise decisions during your work, so I'll leave out the specific details on what exactly should be changed. Also, the code is in such bad shape that _any_ change you make will probably be a good one.

### GUI upgrade - Amit 
The actual application is run using a PyQT GUI, written by project students from our lab. The GUI needs to handle both inputs and outputs, meaning it should be able to process a TIFF stack and run the analysis on it. Currenlty, the input part mostly works, and your first task should be a "clean-up", i.e. verifying that each function works and document it. Then comes the I/O part - the GUI has to output the ROIs in a specific format that `flics.py` should read. You have to make sure you understand the current format (it's in the `.json` files) and see that whoever's working on the code knows it. Another important task is the documentation of the entire software - how to install, how to run, what do the parameters mean, etc. 

This task will probably take the longest, so once Zvi and Omer are done with theirs you should ask for their assistance. If you'll all work with version control and short, precise commits, this shouldn't be an issue.

### Global fit - Omer
The output of the cross-correlation has to be fitted (globally) in order to receive the final measurement values. We've received the result of the fit the original group did, and so the first goal is to receive their answer with our code, since they conduct the fit with a special statistics software which is unavailable for us. Once the results fit their original result, we can try working with our own data.
