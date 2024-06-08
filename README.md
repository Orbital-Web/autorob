# Autorob (pybullet version testment)

## Overview
This repo contains a demo of uisng mr2 robot for basic control and interaction. Also,it contains two implementation of pr2 motionplaning exmaple using a-star algorithm and rrt-algorithm
## Prerequisites
Before you begin, ensure you have met the following requirements:
- You need to install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

## Installation

### Step 1: Install Conda
If you don't have Conda installed, follow these steps to install it:

#### For Windows:
1. Download the [Miniconda installer for Windows](https://docs.conda.io/en/latest/miniconda.html).
2. Run the installer and follow the instructions on the screen.

#### For macOS:
1. Download the [Miniconda installer for macOS](https://docs.conda.io/en/latest/miniconda.html).
2. Open the terminal and run:
    ```sh
    bash Miniconda3-latest-MacOSX-x86_64.sh
    ```
3. Follow the instructions on the screen.

#### For Linux:
1. Download the [Miniconda installer for Linux](https://docs.conda.io/en/latest/miniconda.html).
2. Open the terminal and run:
    ```sh
    bash Miniconda3-latest-Linux-x86_64.sh
    ```
3. Follow the instructions on the screen.

### Step 2: Set Up the Environment
Once Conda is installed, you can create the environment using the provided `environment.yml` file. Environment name should be autorob

1. Clone the repository:
    ```sh
    git clone https://github.com/Orbital-Web/autorob/tree/8-finish-render-function-in-kinevalpy
    ```
2. Switch to pybullet_demo branch
   ```sh
    git checkout pybullet_demo
    ```
2. Create the environment:
    ```sh
    conda env create -f environment.yml
    ```

3. Activate the environment:
    ```sh
    conda activate autorob
    ```

## Usage
### MR2 demo example
   You can run the mr2 demo using following command
    ```sh
    python3 mr2_demo.py
    ```
### PR2 example
   You can run the mr2 demo using following command
    ```sh
    python3 mr2_demo.py
    ```
### PR2 astar example
   You can run the mr2 demo using following command
    ```sh
    python3 astar_template.py
    ```
### PR2 rrt example
   You can run the mr2 demo using following command
    ```sh
    python3 rrt_template.py
    ```
### TODO