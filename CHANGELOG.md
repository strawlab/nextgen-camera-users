## 0.7.0 - unreleased

### Added

* [strand-cam, braid] In UI page, title and info link to Straw Lab website. A
  "loading..." indication is shown prior to main UI being loaded.

### Fixed

* [strand-cam] Do not print information about how to workaround a VLC bug by
  copying the h264 stream using ffmpeg. We discovered that this will lose
  precise timestamps and so it is dangerous and should not be done.

* [braid] Do not crash when attempting 3D tracking and some cameras are not in
  the calibration. (The data from these cameras will simply not contribute to
  3d tracking.)

* [braid] Prevent occasional crash with the involving triggerbox_comms thread.

## 0.6.0 - 2019-10-25

### Fixed

* [braid] Fixed some a bug in which Braid would crash due to a
  `NotDefinitePositive` error when doing 3D tracking.

## 0.5.0 - 2019-10-22

### Added

* [strand-cam] On systems with NVIDIA graphics cards, enable recording to H264
  encoded MKV files using hardware encoding, thus using hardly any CPU
  resources.

# ------------------------------------------------------------------------

## unreleased

### Fixed

* Do not draw an orientation in web browser when no theta detected.

### Added

* Added `Polygon` to possible `valid_region` types.
* Updated to use libvpx 1.8 for encoding MKV videos.
* Add checkerboard calibration within fview2

### Changed

* `flydra2` now saves all output as `.csv.gz` (not `.csv`) files.

## 0.20.29 - 2019-06-06

### Changed

* For `fview2` (all variants), build with jemalloc memory allocator. This
  appears to fix a "corrupted size vs. prev_size" error.

## 0.20.28 - 2019-06-01

### Added

* Created several ROS launch example files. They are in this repository in the
  `ros-launchfile-examples` directory.

### Fixed

* Fixed some bugs in the way .mkv files were created. There was a bug in which
  recordings longer than ~30 minutes were truncated at ~30 minutes. And another
  bug was that, when viewing the recorded video, skipping to a particular point
  in time and viewing the total duration did not work. With some light testing,
  these should both be fixed now.
* Fixed setting of acquisition frame rate on older GigE cameras.
* Provide mime type for .js files in fview, which stops browser warning about
  empty mime type.

### Changed

* For `fview2` (all variants, Pylon drivers), upgrade Pylon to version
  5.2.0.13457.
* In `flydra2-mainbrain`, changed the `--addr` command-line argument to
  `--lowlatency-camdata-udp-addr`.

## 0.20.25 - 2019-03-25

### Changed

* In `fview2` (all variants), CSV files from object detection have a new, more
  efficient format.

### Added

* In `fview2` (all variants), the maximum framerate for saving data to CSV files
  may be specified.

## 0.20.22 - 2019-02-24

### Changed

* In `fview2` (all variants, Pylon drivers), if a Pylon camera is already open,
  open a web browser to a guess of the correct URL. Disable with `--no-browser`.

## 0.20.21 - 2019-02-24

### Changed

* Substantial browser UI revision in `fview2` (all variants).

* `fview2-camtrig` will raise an error dialog in browser UI if contact
  to the camtrig USB device is lost.

* Default codec for MKV files is VP8 in `fview2` (all variants). This was a
  change from VP9 because there is seems to be a bug when saving to VP9 in which
  the encoded video is jerky.
