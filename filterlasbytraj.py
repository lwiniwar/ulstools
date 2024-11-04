import argparse
from pathlib import Path
import numpy as np
from osgeo import ogr, osr
ogr.UseExceptions()
import laspy

DELTA = 10 * np.abs(286832.13239 - 286832.12739)  # sample of two subsequent entries in a trajectory file

def main(trajfilepath, lasfilepath, outdir):
    trajfile = ogr.Open(trajfilepath)
    lay = trajfile.GetLayer()
    times = []
    for feat in lay:
        time = feat.GetField(1)
        times.append(time)
    times = np.array(times)

    deltas = np.diff(times)
    stops = np.concatenate([np.argwhere(deltas > DELTA)[:,0], [times.shape[0]-1]])
    starts = np.concatenate([[0], np.argwhere(deltas > DELTA)[:,0]+1])

    las = laspy.read(lasfilepath)

    #times = times % (24*60*60)  # Convert to SOW (?)
    point_times = (las.points.gps_time + 1e9) % (7 * 24 * 60 * 60)  # convert to SOW (Seconds of GPS Week) as in the traj sbet file
    idnew = 0
    outdir = Path(outdir)
    for idx, (start, stop) in enumerate(zip(starts, stops)):
        tstart = times[start]
        tstop = times[stop]
        new_points = las.points[np.logical_and(point_times > tstart, point_times < tstop)]
        if len(new_points) > 0:
            sub_las = laspy.LasData(las.header)
            sub_las.points = new_points.copy()
            print(f"Strip {idnew:02d}: {len(new_points)} points from t={tstart} to {tstop}")
            sub_las.write(str(outdir / rf"{idnew:02d}.laz"))
            idnew += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = "filterlasbytraj.py",
        description= "Allows filtering of a laser scanning point cloud (las format) by a trajectory through "
                     "identifying temporal gaps and exporting the results as individual files."
    )
    parser.add_argument('trajectory')
    parser.add_argument('lasfile')
    parser.add_argument('outputdir')
    args = parser.parse_args()
    main(args.trajectory, args.lasfile, args.outputdir)