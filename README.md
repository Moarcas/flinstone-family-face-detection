# Flintstone Family Facial Detection Project

## Overview

This project utilizes Histogram of Oriented Gradients (HOG) descriptors and a Support Vector Machine (SVM) implemented through the LinearSVC class from scikit-learn to perform facial detection on images of the Flintstone Family. The README provides information on the required libraries and instructions for running the code.

## Libraries Used

- **numpy**: For numerical operations and array manipulation.
- **scikit-learn**: Specifically, the LinearSVC class for implementing the SVM.
- **matplotlib**: Used for plotting and visualization.
- **glob**: To easily retrieve a list of file paths matching a specified pattern.
- **cv2 (OpenCV)**: For image processing tasks.
- **pdb**: Python Debugger for debugging purposes.
- **pickle**: For serializing and deserializing Python objects.
- **ntpath**: To handle file paths.
- **copy**: Used for creating deep copies of objects.
- **timeit**: To measure the execution time of code blocks.
- **skimage.feature**: Provides the HOG feature extraction method.
- **collections**: Used for specialized container data structures.
- **scipy.ndimage**: Used for image rotation.

## Instructions for Running the Code

### 1. Setup Environment

Make sure you have Python installed on your system. You can install the required libraries using the following command:

```bash
pip install numpy scikit-learn matplotlib opencv-python scikit-image scipy
```

### 2. Clone the Repository

Clone the Flintstone Family Facial Detection Project repository from GitHub:

```bash
git clone https://github.com/Moarcas/flintstone-family-face-detection
```

### 3. Go to the desired task folder
```bash
cd flinstone-family-face-detection/cod/task1
```
or 
```bash
cd flinstone-family-face-detection/cod/task2
```

### 3. Run the project
```bash
python3 RunProject.py

