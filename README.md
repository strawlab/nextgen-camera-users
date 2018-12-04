# nextgen-camera-users

Files and support for users of next generation camera software from the Straw
Lab.

## Downloads

The most recent files can be downloaded [here](https://www.dropbox.com/sh/x1xbephf6pj8sau/AADdy2NB5erGRk-dB2M8B86Ta?dl=0).

## Analysis of saved trajectories

1. Convert directory of .csv files to flydra mainbrain .hdf5 files.

2. For your own analysis, convert flydra mainbrain .hdf5 files to simple .hdf5
   files with `flydra_analysis_export_flydra_hdf5`. These files are much simpler
   and have only the 3D trajectories, so are much smaller and have already been
   through smoothing. The format is documented
   [here](https://strawlab.org/schemas/flydra/1.3).
