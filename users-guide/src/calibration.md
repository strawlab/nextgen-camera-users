# Calibration

## What is a calibration?

In our usage here, we refer to a calibration as a model of a camera which allows
us to compute the 2D image location of a given 3D point. Braid can use
calibrations of multiple cameras to calculate the 3D position of a given point
when viewed in 2D camera images.

For a given camera, the calibration is divided into two parts. The "extrinsics",
or extrinsic parameters, define the pose of the camera. This is the 3D position
and orientation of the camera. The "intrinsics", or intrinsic parameters, define
the projection of 3D coordinates relative to the camera to an image point in
pixels. In Braid, the camera model is a pinhole model with warping distortion.
The intrinsic parameters include focal length, the pixel coordinates of the
optical axis, and the radial and tangential parameters of a "plumb bob"
distortion model.

## Step 1: setup cameras (zoom, focus, aperture, gain) and lights

Setup camera position, zoom, focus (using an object in the tracking volume) and
aperture (slightly stopped down from wide-open). Exposure times and gains are
set in Strand Cam for each camera individually. Note that if you intend to run
at 100 frames per second, exposure times must be less than 10 milliseconds.

Try to a luminance distribution which extends across the entire dynamic range of
your sensor (from intensity values 0 to 255) with very little clipping.

## Step 2: run "Checkerboard Calibration" to get the camera intrinsic parameters

In Strand Cam, there is a region called "Checkerboard Calibration" which allows
you to calibrate the camera intrinsic parameters. Show a checkerboard to the
camera. You must enter your the checkerboard parameters into the user interface.
For example, a standard 8x8 checkerboard would have 7x7 corners. Try to show the
checkerboard at different distances and angles. Do not forget to show the
checkerboard corners in the corners of the camera field of view. There is a
field which shows the number of checkerboard collected - this should increase as
the system detects checkerboards. When you have gathered a good set of
checkerboards, click the "Perform and Save Calibration" button. The results of
this calibration are saved to the directory
`$HOME/.config/strand-cam/camera_info`.

Repeat this for all cameras before proceeding to the next step.

## Step 3: collect calibration data and run MCSC

Room lights should be off.

Synchronize your cameras and start saving data and begin to collect data by
moving a LED in the arena (try move the LED in the whole arena volume, also turn
it off and on sometimes to validate synchronization). When you are done, stop
saving.

From here, follow the instructions
[here](https://github.com/strawlab/nextgen-camera-users/#convert-braidz-file-to-flydra-mainbrain-h5-file).
