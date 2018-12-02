#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import subprocess
import glob
import argparse
import warnings

import numpy as np
import pandas as pd

import flydra_core.kalman.flydra_kalman_utils as flydra_kalman_utils
import flydra_core.reconstruct
from flydra_analysis.a2.tables_tools import open_file_safe
import scipy

parser = argparse.ArgumentParser()
parser.add_argument('data_dir',type=str,
                    help='input directory', nargs=1)
parser.add_argument('--2d-only', action='store_true',
                    help='convert only the 2D data')
parser.add_argument('--no-calibration', action='store_true',
                    help='do not copy the calibration')
parser.add_argument('--no-delete', action='store_true',
                    help='do not delete the original directory')
args = parser.parse_args()
data_dir = args.data_dir[0]
if data_dir.endswith(os.sep):
    data_dir = data_dir[:-1]
dest_filename = data_dir + '.h5'

d2d_r0 = None
d2d_r1 = None

def convert_pd_to_np(df):
    colnames = tuple(df.columns)
    n = len(df)
    formats = [df[colname].values.dtype.type for colname in colnames]
    data = np.zeros(n, dtype={'names': colnames, 'formats': formats})
    for colname in colnames:
        data[colname] = df[colname]
    return data

def recursive_get_files(dirname):
    """get all filenames in directory, including recursively in subdirs"""
    result = []
    for f in os.listdir(dirname):
        relname = os.path.join(dirname,f)
        if os.path.isdir(relname):
            result.extend(recursive_get_files(relname))
        else:
            result.append(relname)
    return result

def recursive_rmdir(dirname):
    """remove directory which must be empty or contain only empty directories"""
    for f in os.listdir(dirname):
        relname = os.path.join(dirname,f)
        if os.path.isdir(relname):
            recursive_rmdir(relname)
    os.rmdir(dirname)

def computed_dir(data_dir):
    return os.path.join(data_dir, "flydra1-compat-computed-offline")

def save_row(h5_row, row, colnames):
    for colname in colnames:
        h5_row[colname] = row[colname]
    h5_row.append()

def mysplit(s,sep):
    """split string on separator but do not return empty results"""
    r = s.split(sep)
    if len(r)==1 and r[0]=="":
        return []
    return r

def do_d2d(data_dir, h5file):
    data_2d_fname = os.path.join(data_dir, 'data2d_distorted.csv')
    data2d_df = pd.read_csv(data_2d_fname)

    # cache first and last rows
    global d2d_r0, d2d_r1
    d2d_r0 = data2d_df.iloc[0]
    d2d_r1 = data2d_df.iloc[-1]

    data = convert_pd_to_np(data2d_df)

    h5file.create_table(h5file.root,
        'data2d_distorted',
        description=data,
        title="2d data",
        )

    return [data_2d_fname]

def do_ml_estimates(data_dir, h5file):
    data_csv_fname = os.path.join(data_dir, 'kalman_estimates.csv')
    if not os.path.exists(data_csv_fname):
        print('no kalman estimates, not converting ML_estimates')
        return []

    # This file was used to create the vlarray_csv file
    orig_src_fname = os.path.join(data_dir, 'data_association.csv')
    ml_estimates_2d_idxs_fname = os.path.join(computed_dir(data_dir), 'ML_estimates_2d_idxs.vlarray_csv')
    h5_2d_obs = h5file.create_vlarray(
        h5file.root,
        'ML_estimates_2d_idxs',
        flydra_kalman_utils.ML_estimates_2d_idxs_type(),
        "camns and idxs")
    if ml_estimates_2d_idxs_fname is not None:
        with open(ml_estimates_2d_idxs_fname, mode='r') as fd:
            for input_line in fd:
                try:
                    camns_and_idxs = [int(x) for x in mysplit(input_line.strip(),',')]
                except:
                    print("bad line: %r" % input_line)
                    raise
                h5_2d_obs.append( camns_and_idxs )

    ml_estimates_fname = os.path.join(computed_dir(data_dir), 'ML_estimates.csv')
    assert(os.path.exists(ml_estimates_fname))
    h5_obs = h5file.create_table(
        h5file.root,'ML_estimates', flydra_kalman_utils.FilteredObservations,
        "observations of tracked object")
    ml_estimates_df = pd.read_csv(ml_estimates_fname)
    for _,row in ml_estimates_df.iterrows():
        save_row(h5_obs.row, row, h5_obs.colnames)

    return [orig_src_fname, ml_estimates_2d_idxs_fname, ml_estimates_fname]

def compute_mean_fps(data_dir, h5file):
    global d2d_r0, d2d_r1
    if d2d_r0 is None or d2d_r1 is None:
        raise ValueError()
    t0 = d2d_r0.timestamp
    f0 = d2d_r0.frame
    t1 = d2d_r1.timestamp
    f1 = d2d_r1.frame
    dur = t1-t0
    frames = f1-f0
    fps = frames/dur
    return fps

def do_textlog(data_dir, h5file):
    textlog_fname = os.path.join(data_dir, 'textlog.csv')
    textlog_df = pd.read_csv(textlog_fname)

    orig_m0 = textlog_df['message'][0]
    m0 = orig_m0

    # fix potential unknown fps
    orig_bad_str = 'running at unknown fps'
    if orig_bad_str in m0:
        fps = compute_mean_fps(data_dir, h5file)
        new_good_str = 'running at %.2f fps' % fps
        m0 = m0.replace(orig_bad_str, new_good_str)

    # fix potential bad timezone
    orig_bad_str = 'time_tzname0 CET)'
    if orig_bad_str in m0:
        new_good_str = 'time_tzname0 Europe/Berlin)'
        m0 = m0.replace(orig_bad_str, new_good_str)

    # fix potential bad timezone
    orig_bad_str = 'time_tzname0 CEST)'
    if orig_bad_str in m0:
        new_good_str = 'time_tzname0 Europe/Berlin)'
        m0 = m0.replace(orig_bad_str, new_good_str)

    if m0 != orig_m0:
        colnum = list(textlog_df.columns).index('message')
        textlog_df.iat[0, colnum] = m0

    textlog_table = h5file.create_table(h5file.root,
        'textlog', flydra_core.data_descriptions.TextLogDescription,
        "text log")

    for _,row in textlog_df.iterrows():
        save_row(textlog_table.row, row, textlog_table.colnames)

    return [textlog_fname]

def do_trigger_clock_info(data_dir, h5file):
    trigger_clock_info_fname = os.path.join(data_dir, 'trigger_clock_info.csv')
    try:
        trigger_clock_info_df = pd.read_csv(trigger_clock_info_fname)
    except ValueError as err:
        trigger_clock_info_df = None
    except pd.io.common.EmptyDataError as err:
        trigger_clock_info_df = None
    trigger_clock_info_table = h5file.create_table(h5file.root,
        'trigger_clock_info', flydra_core.data_descriptions.TriggerClockInfo,
        "Trigger Clock Info")
    if trigger_clock_info_df is not None:
        for _,row in trigger_clock_info_df.iterrows():
            save_row(trigger_clock_info_table.row, row, trigger_clock_info_table.colnames)
    return [trigger_clock_info_fname]

def do_experiment_info(data_dir, h5file):
    experiment_info_fname = os.path.join(data_dir, 'experiment_info.csv')
    try:
        experiment_info_df = pd.read_csv(experiment_info_fname)
    except ValueError as err:
        # most likely no data in this file
        experiment_info_df = None
    if experiment_info_df is not None:
        experiment_info_table = h5file.create_table(h5file.root,
            'experiment_info', flydra_core.data_descriptions.ExperimentInfo,
            "Experiment Info")
    if experiment_info_df is not None:
        for _,row in experiment_info_df.iterrows():
            save_row(experiment_info_table.row, row, experiment_info_table.colnames)
    return [experiment_info_fname]

def do_cam_info(data_dir, h5file):
    cam_info_fname = os.path.join(data_dir, 'cam_info.csv')
    cam_info_df = pd.read_csv(cam_info_fname)
    cam_info_table = h5file.create_table(h5file.root,
        'cam_info', flydra_core.data_descriptions.CamSyncInfo, "Cam Sync Info")
    cols = cam_info_table.colnames[:]
    cols.remove('hostname')
    for _,row in cam_info_df.iterrows():
        save_row(cam_info_table.row, row, cols)
    return [cam_info_fname]

def do_calibration(data_dir, h5file):
    reconstruct_fname = os.path.join(data_dir, 'calibration.xml')
    reconstructor = flydra_core.reconstruct.Reconstructor(reconstruct_fname)
    reconstructor.save_to_h5file(h5file)
    return [reconstruct_fname]

def do_kalman_estimates(data_dir, h5file):
    converted = []
    warnings.warn('not converting dynamic model')

    orig_src_fname = os.path.join(data_dir, 'kalman_estimates.csv')
    data_csv_fname = os.path.join(computed_dir(data_dir),
        'contiguous_kalman_estimates.csv')
    converted.extend([orig_src_fname, data_csv_fname])

    try:
        kalman_estimates_df = pd.read_csv(data_csv_fname)
    except pd.io.common.EmptyDataError as err:
        kalman_estimates_df = None

    if kalman_estimates_df is not None:
        data = convert_pd_to_np(kalman_estimates_df)
        h5file.create_table(h5file.root,
            'kalman_estimates',
            description=data,
            title="Kalman a posteriori estimates of tracked object",
        )
    return converted

def do_host_clock_info(data_dir, h5file):
    # Create this table even if file does not exist to avoid
    # error in old flydra analysis versions.
    host_clock_info_table = h5file.create_table(h5file.root,
        'host_clock_info', flydra_core.data_descriptions.HostClockInfo,
        "Host Clock Info")

    host_clock_info_fname = os.path.join(data_dir, 'host_clock_info.csv')
    converted = []
    if os.path.exists(host_clock_info_fname):
        try:
            host_clock_info_df = pd.read_csv(host_clock_info_fname)
        except pd.io.common.EmptyDataError as err:
            host_clock_info_df = None
        if host_clock_info_df is not None:
            for _,row in host_clock_info_df.iterrows():
                save_row(host_clock_info_table.row, row, host_clock_info_table.colnames)
        converted.append(host_clock_info_fname)
    return converted

def do_images(data_dir, h5file):
    converted = []
    image_glob = os.path.join(data_dir, 'images', '*.png')
    image_files = glob.glob(image_glob)

    # save raw image from each camera
    img = h5file.create_group(h5file.root, 'images', 'sample images')

    for fname in image_files:
        cam_id = os.path.splitext(os.path.split(fname)[1])[0]
        image = scipy.misc.imread(fname)
        if image.ndim != 2:
            raise NotImplementedError('only luminance images currently implemented')
        h5file.create_array( img, cam_id, image, 'sample image from %s'%cam_id )
        converted.append(fname)
    return converted

if not os.path.exists(data_dir):
    print('ERROR: input does not exist: %s'%data_dir, file=sys.stderr)
    sys.exit(1)

delete_original = not args.no_delete
with open_file_safe(dest_filename, mode="w", title="tracked Flydra data file",
                    delete_on_error=True) as h5file:

    if vars(args)['2d_only']:
        print("converting 2D data only")
    else:
        if not os.path.exists(computed_dir(data_dir)):
            cmd = "compute-flydra1-compat %s" % data_dir
            print(cmd)
            subprocess.check_call(cmd, shell=True)
        else:
            print("flydra1 compat data already computed, not re-computing.")

    converted = []
    converted.extend(do_images(data_dir, h5file))
    converted.extend(do_host_clock_info(data_dir, h5file))
    if not vars(args)['2d_only']:
        converted.extend(do_ml_estimates(data_dir, h5file))
    converted.extend(do_d2d(data_dir, h5file))
    converted.extend(do_textlog(data_dir, h5file))
    if not vars(args)['2d_only']:
        converted.extend(do_trigger_clock_info(data_dir, h5file))
    if not vars(args)['2d_only']:
        converted.extend(do_experiment_info(data_dir, h5file))
    converted.extend(do_cam_info(data_dir, h5file))
    if not vars(args)['no_calibration']:
        converted.extend(do_calibration(data_dir, h5file))
    if not vars(args)['2d_only']:
        converted.extend(do_kalman_estimates(data_dir, h5file))

all_files = recursive_get_files(data_dir)

hmm_files = set(converted) - set(all_files)
if len(hmm_files) > 0:
    raise RuntimeError("Delete file(s) that do not exist? %s"%hmm_files)

leftover_files = set(all_files) - set(converted)
if len(leftover_files) > 0:
    print('ERROR: unconverted file(s) detected: %s'%leftover_files, file=sys.stderr)
    sys.exit(1)

if delete_original:
    for f in converted:
        os.unlink(f)
    recursive_rmdir(data_dir)
