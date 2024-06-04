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
3. Once you are done, commit and push your changes.
   ```
   git add *
   git commit -m "feat: worked on something"
   git push
   ```
4. Once you are done with the issue, go to GitHub and submit a [merge request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request). We can review each other's work to merge it into main. Note that merging will fail if the tests fail.

