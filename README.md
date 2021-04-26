# Photo Whittler
![PhotoWhittler](res/whittler_example.png)
## Program Description
This is meant to be a specific use tool of upvoting and downvoting photos that are meant to be 
then edited in a program like Adobe Lightroom or some other photo editing professional software. 
This is not  meant to replace a photo editing suite, but to augment and provide specially designed 
tools for specific parts of the editing work flow.

## Use-case
This program is meant to specifically augment my current photo work flow where I (personally) may 
take 500 or so photos over the course of a week's vacation. This program is meant to allow the 
user to choose which of the 500 or so raw files that are in the project folder actually need to be 
edited and which can be left on the cutting room floor so to speak.


## Program Installation (macOS)
1. Download the repo by either:
    1. Cloning the repo with git. This can be done with the command (assuming git is already set up)
       `git clone https://github.com/paradise-runner/photoWhittler.git`
    1. Downloading and unzipping the [repo](https://github.com/paradise-runner/photoWhittler)
1. Unzip the Photo Whittler.zip with a double-click
1. Double-click on the photoWhittler app to run!


## .app Creation Instructions (macOS)
Don't trust the .app provided in the .zip? No worries! Compile it yourself with the following 
instructions!
1. Open the terminal
1. Install the [homebrew cli](https://brew.sh/) (if not installed)
1. Install Python 3.9 with the command `brew install python@3.9`. Instructions found
   [here](https://formulae.brew.sh/formula/python@3.9)
1. Change Directories to wherever the repo should be installed. ex. 
   `cd Users/{your_username}/Documents` would move the terminal location to the `Documents` folder 
   on your computer. 
1. Download the repo by either:
    1. Cloning the repo with git. This can be done with the command (assuming git is already set up)
       `git clone https://github.com/paradise-runner/photoWhittler.git`
    1. Downloading and unzip the [repo](https://github.com/paradise-runner/photoWhittler)
        1. Copy the unzipped folder to wherever you moved to in step 4
1. Change directories again to the new photoWhittler folder what was just created with the 
   command (ex) `cd Users/{your_username}/Documents/photoWhittler`
1. Run the shell command `chmod +x ./build-dot-app.sh` in the terminal to enable the build script 
   to be ran   
   1. You're about to enable a shell script to be run on your machine! Now is a good time to read 
      the actual script, it has echos to explain all the steps its taking!
   1. Want to disable the build shell script after creating the .app? Run the command 
      `chmod -x ./build-dot-app.sh`, which will disable the build script from being run again.
1. Run the shell script `./build-dot-app.sh` in the terminal to build the app
