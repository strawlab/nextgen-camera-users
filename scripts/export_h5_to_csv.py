import sys
import os
import errno
import tables
import pandas
from collections import defaultdict
import flydra_analysis.a2.calibration_to_xml as calibration_to_xml

fname = sys.argv[1]
outdir, ext = os.path.splitext(fname)
assert ext == '.h5' or ext == '.hdf5'

try:
    os.makedirs(outdir)
except OSError as err:
    if err.errno == errno.EEXIST:
        pass
    else:
        raise

with tables.open_file(fname) as h5:
    # 2d data ------
    d2d = h5.root.data2d_distorted[:]
    df = pandas.DataFrame(d2d)
    csv_fname = os.path.join(outdir, 'data2d_distorted.csv')
    df.to_csv(csv_fname, index=False, float_format='%r')

    # cam info ------
    cam_info = h5.root.cam_info[:]
    df = pandas.DataFrame(cam_info)
    csv_fname = os.path.join(outdir, 'cam_info.csv')
    df.to_csv(csv_fname, index=False, float_format='%r')

class Options:
    pass

options = Options()
options.scaled = False
options.dest = os.path.join(outdir, 'calibration.xml')

calibration_to_xml.doit(fname, options)
