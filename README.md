# CAOS Xmas Tree
A 3D-mapped LED Christmas tree using 650 individually addressable LEDs. 

Uses computer vision to determine each LED's position and renders animations in 3D space on the tree.

## Index

- [Features](#features)
- [Hardware Used](#hardware-used)
- [Technology Used](#technology-used)
- [Setup](#setup)
- [Process](#process)
- [Future Milestones](#future-milestones)

## Features

- 650 individually addressable LEDs

- 3D LED position mapping using computer vision

- LEDs controlled via Raspberry Pi

- Supports custom animations

- Resume LED capture if interrupted

## Hardware Used

- 650x WS2811 RGB String Lights (12V)

- Raspberry Pi 4

- 12V 30A Power Supply

- Jumper Wires (for GPIO connections)


## Technology Used

- Python 3

- Libraries:
    - numpy
    - opencv-python
    - matplotlib
    - rpi-ws281x



## Setup

1. Clone the repo

```git clone https://github.com/zakattack157/CAOS_Xmas_Tree.git```

``` cd CAOS_Xmas_Tree```

2. Create Virtual Environment

```python3 -m venv venv```

```source venv/bin/activate```

3. Install Dependencies:

```pip install -r requirements.txt```

4. Run LED Test

```python strandtest.py```

## Process

1. Hardware Setup
- Wire the LEDs together
- Connect the 12V power supply
- Connect Raspberry Pi

2. Initial Testing
- SSH into the Raspberry Pi (Locally)
- Run LED tests to make sure all LEDs work
- Run basic RGB test patterns

3. Coordinate Mapping (X, Y)
- Only one LED is turned on at a time during capture
- Run ```get_images.py``` to capture an image for each lit LED using a webcam (works best in dark room)
- ```strandtest.py``` must be run at the same time to turn on each individual LED 
- OpenCV used to detect brightest pixel
- (X, Y) coords are saved for each LED
- Coordinate results are saved to ```coords_xy.txt``` within the ```coords``` directory
- All images will be saved within the ```xy``` directory. You can check for any false positives there

4. Depth Mapping (Z-coord)
- Rotate tree 90 degrees
- Change ```COORD_FILE``` and ```SAVE_DIR``` in ```get_images.py``` from 'xy' to 'zy'
- Repeat capture process
- Coordinate results are saved to ```coords_zy.txt``` within the ```coords``` directory
- All images will be saved within the ```zy``` directory. You can check for any false positives there

5. 3D Coordinate Generation
- Run ```stitch_coords.py``` to merge coordinate datasets
- This creates the full (X, Y, Z) coordinates and is saved within the ```coords``` directory as ```coords.3d```

6. Animations
- Adapted code to work with ```rpi-ws281x```
- Imported animations from external projects
- Use animations to test the 3D coordinates

### Coordinate Image Capturing Notes
- Only one LED should be active during capture
- The brightest pixel detected is assumed to be the LED position
- Consistent lighting will help accuracy immensely
- Consistent webcam and tree position will also help immensely
- Raspberry Pi and computer capturing images must stay synchronized so the correct LED is lit during each image

### Capture Recovery
- The starting LED index can be manually adjusted in ```get_images.py```
- This allows the capture process to resume from a specific LED if interrupted

> This is very useful if the script stops mid-run, you won't need to restart the entire capture process.


## Future Milestones 

* Cleaning up the repo (better organization)

* Automating ```get_images.py```

* Adding more animations

* Creating a virtual tree simulation for easier testing (possibly within Unity)

* Streamlining everything for future use 

* Add a video demo to this README
