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
