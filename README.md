# nextgen-camera-users

Files and support for users of next generation camera software from the Straw
Lab.

## Downloads

The most recent files can be downloaded [here](https://www.dropbox.com/sh/x1xbephf6pj8sau/AADdy2NB5erGRk-dB2M8B86Ta?dl=0).

## Live 3D pose estimates

The script in this repository `scripts/flydra2_retransmit_udp.py` is an example
of parsing live, low-latency 3D tracking data.

## Analysis of saved trajectories from Braid

Remember, you can view your `.braidz` file at https://braidz.strawlab.org/.

### Convert `.braidz` file to flydra mainbrain `.h5` file

By converting from `.braidz` to a mainbrain `.h5` file, you can use the
wide range of analysis programs from [flydra](https://github.com/strawlab/flydra).

For example, let's say you have the file `20190924_161153.braidz` saved by the
Braid program. We will use the script `convert_kalmanized_csv_to_flydra_h5.py`
to do this conversion:

    python ~/src/nextgen-camera-users/scripts/convert_kalmanized_csv_to_flydra_h5.py 20190924_161153.braidz

Upon success, there will be a new file saved with the suffix `.h5`. In this
case, it will be named `20190924_161153.braidz.h5`.

We can do the above but making use of bash variables to save typing later `BRAIDZ_FILE`.

    BRAIDZ_FILE=20190924_161153.braidz
    DATAFILE="$BRAIDZ_FILE.h5"
    python ~/src/nextgen-camera-users/scripts/convert_kalmanized_csv_to_flydra_h5.py $BRAIDZ_FILE

Note that this conversion requires the program `compute-flydra1-compat` to be on your path if
you are converting 3D trajectories.



### Run MultiCamSelfCal on data collected with Braid

You can collect data and calibrate similar to [the description for Flydra](https://github.com/strawlab/flydra/blob/c9f20d5f8f4feb7e1fe008cf0ee67fbbc70b1ba0/docs/flydra-sphinx-docs/calibrating.md)

If your mainbrain `.h5` file is in the location `$DATAFILE`, you can run the [MultiCamSelfCal](https://github.com/strawlab/MultiCamSelfCal)
program on this data to generate a multiple camera calibration.

    flydra_analysis_generate_recalibration --2d-data $DATAFILE --disable-kalman-objs $DATAFILE --undistort-intrinsics-yaml=$HOME/.config/strand-cam/camera_info  --run-mcsc --use-nth-observation=4

This will print various pieces of imformation to the console when it runs. First it will print something like this:

```
851 points
by camera id:
 Basler_40022057: 802
 Basler_40025037: 816
 Basler_40025042: 657
 Basler_40025383: 846
by n points:
 3: 283
 4: 568
```

This means that 851 frames were acquired in which 3 or more cameras detected exactly one point.
The contribution from each camera is listed. In this example, all cameras had between 657 and
846 points. Then, the number of points detected by exactly 3 cameras is shown (283 such frames)
and exactly 4 cameras (568 frames).

Important things to watch for are listed here. These may be useful, but are rather
rough guidelines to provide some orientation:

- No camera should have very few points, otherwise this camera will not contribute much to
  the overall calibration and will likely have a bad calibration itself.

- The number of points used should be somewhere between 300 and 1000. Fewer than 300 points
  often results in poor quality calibrations. More than 1000 points results in the calibration
  procedure being very slow. The `--use-nth-observation` command line argument can be used
  to change the number of points used.

After running succesfully, the console output should look something like this:

```
********** After 0 iteration *******************************************
RANSAC validation step running with tolerance threshold: 10.00 ...
RANSAC: 1 samples, 811 inliers out of 811 points
RANSAC: 2 samples, 811 inliers out of 811 points
RANSAC: 2 samples, 762 inliers out of 762 points
RANSAC: 1 samples, 617 inliers out of 617 points
811 points/frames have survived validations so far
Filling of missing points is running ...
Repr. error in proj. space (no fact./fact.) is ...  0.386139 0.379033
************************************************************
Number of detected outliers:   0
About cameras (Id, 2D reprojection error, #inliers):
CamId    std       mean  #inliers
  1      0.41      0.41    762
  2      0.33      0.33    811
  3      0.49      0.41    617
  4      0.33      0.37    811
***************************************************************
**************************************************************
Refinement by using Bundle Adjustment
Repr. error in proj. space (no fact./fact./BA) is ...  0.388949 0.381359 0.358052
2D reprojection error
All points: mean  0.36 pixels, std is 0.31

finished: result in  /home/strawlab/20190924_161153.braidz.h5.recal/result
```

Important things to watch for:

- There should only be one iteration (numbered `0`).

- The mean reprojection error should be low. Certainly less than
  1 pixel and ideally less than 0.5 pixels as shown here.

- The low reprojeciton error should be low across all cameras.

The above example calibration is a good one.

Using this calibration, you can perform 3D tracking of the data with:

    flydra_kalmanize ${DATAFILE} -r ${DATAFILE}.recal/result

You can view these results with:

    DATAFILE_RETRACKED=`python -c "print '${DATAFILE}'[:-3]"`.kalmanized.h5
    flydra_analysis_plot_timeseries_2d_3d ${DATAFILE} -k ${DATAFILE_RETRACKED} --disable-kalman-smoothing

Now you have a working calibration, which is NOT aligned or scaled to the flycube coordinate system, but is able to track. Scaling can be quite important for good tracking.

Next we will align the calibration.

    flydra_analysis_calibration_align_gui --stim-xml ~/src/rust-cam/_submodules/flydra/flydra_analysis/flydra_analysis/a2/sample_bowl.xml ${DATAFILE_RETRACKED}

### Convert mainbrain `.h5` file to a simple `.h5` file.

For your own analysis, convert flydra mainbrain .h5 files to simple .h5
files with `flydra_analysis_export_flydra_hdf5`. These files are much simpler
and have only the 3D trajectories, so are much smaller and have already been
through smoothing. The format is documented
[here](https://strawlab.org/schemas/flydra/1.3).
