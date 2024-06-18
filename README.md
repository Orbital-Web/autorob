# Autorob
This is the repository for Autorob 24-25. Note that students will not be seeing this repository (though it will probably be very similar, minus the solutions to the projects).

## Setup

### Pre-requisites

1. Make sure you have [Git](https://www.git-scm.com) and [Python](https://www.python.org/downloads/) installed.
2. You are recommended to use [VS Code](https://code.visualstudio.com) to sync extensions (though not required).

### Environment

1. In your terminal, create a Python venv and install the required modules.
   ```
   py -m venv .venv
   py -m pip install -r requirements.txt
   ```
2. If you have [VS Code](https://code.visualstudio.com), you should install the [Python Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) so your code is automatically formatted. Make sure to follow the instructions on the extension page to enable automatic formatting upon save.

### Workflow

1. To work on a new feature, create a new branch from an issue. Then in your terminal, switch to that branch.
   ```
   git checkout -b BRANCH_NAME
   ```
2. Enable your Python venv. On Windows, it will look something like this.
   ```
   .\venv\Scripts\activate
   ```
   On Mac, it will look something like this.
   ```
   source .venv/bin/activate
   ```
3. Once you are done, commit and push your changes.
   ```
   git add *
   git commit -m "feat: worked on something"
   git push
   ```
4. Once you are done with the issue, go to GitHub and submit a [merge request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request). We can review each other's work to merge it into main. Note that merging will fail if the tests fail.

### Code Structure
The main entry point for the program is through `main.py` in the root directory. This creates a new Kineval object which handles all the rendering, updates, etc. Inside `Kineval` you will put all the initialization function that runs at the start at the bottom of `init`, and all the updates that needs to run every frame inside `update`. In general, code that the student writes will be defined in another file, and we will have those code imported and running inside either `init` or `update` (take a look at how forward kinematics is done). 

The rendering of the robot, world, and GUI is handled inside `renderer`. In [PyVista](https://docs.pyvista.org/version/stable/), once you add an object to the plotter, it will remain in the scene until it is removed or hidden. You can change the shape, color, and other visual properties in the renderer by updating the object's property inside `update`. GUI is handled by PyQT. There are tons of tutorials out there, and ChatGPT is also very useful for this. 

Inside `geometries` are function which will generate a PyVista `Actor` object, which you can add to the plotter inside `renderer` to display. The pre-existing geometries should be sufficient, but you may add new ones using [this documentation](https://docs.pyvista.org/version/stable/api/utilities/geometric).

`controls` has all the functions that has to do with user input, such as moving the robot or turning a joint. If you want new user controls, please define them in here, and either add them inside `Kineval.update` if you want to continuously check for them, or inside `renderer.KinevalWindow.onKeyPress` if you only want the function to run once per key press. 

`gui` has all the code for widget classes that are used inside the renderer's gui. 

`robot` is the base structure for the robot. Please try to keep it as simple as possible and avoid adding unnecessary member functions. The same goes for the `world`. Actual examples of a robot or a world can be found inside `robots` and `worlds`, respectively. 

Lastly, `types` just has useful type hinting annotations such as vectors and matrices. They can be imported from `kineval` or from `kineval.types`. 

Forward kinematics and robot initialization is already written. Please reference these for how to extend the project to add other functions such as inverse kinematics. 
