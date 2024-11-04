import argparse
import numpy as np
from osgeo import ogr, osr
ogr.UseExceptions()

import pandas as pd

def main(sbetfile, gpkgfile):
    sbet = pd.read_csv(sbetfile, delim_whitespace=True)
    sbet = sbet.iloc[1:,:]
    t = sbet['%'].values
    lat = sbet['Time'].astype(np.float64).values * 180 / np.pi
    lon = sbet['Latitude'].astype(np.float64).values * 180 / np.pi
    alt = sbet['Longitude'].astype(np.float64).values

    driver = ogr.GetDriverByName("GPKG")
    ds = driver.CreateDataSource(gpkgfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = ds.CreateLayer("trajectory", srs, ogr.wkbPoint25D)

    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(idField)

    timeField = ogr.FieldDefn("time", ogr.OFTReal)
    layer.CreateField(timeField)

    # Create the feature and set values
    featureDefn = layer.GetLayerDefn()

    for id, (s_lat, s_lon, s_alt, s_time) in enumerate(zip(lat, lon, alt, t)):
        feat = ogr.Feature(featureDefn)
        geom = ogr.Geometry(ogr.wkbPoint25D)
        geom.AddPoint(s_lon,s_lat, s_alt)
        feat.SetGeometry(geom)
        feat.SetField("id", id)
        feat.SetField("time", s_time)

        layer.CreateFeature(feat)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = "sbet2gpkg.py",
        description= "Converts an ASCII TXT SBET trajectory file to GPKG."
    )
    parser.add_argument('sbetfile', help="")
    parser.add_argument('gpkgfile', help="")
    args = parser.parse_args()
    main(args.sbetfile, args.gpkgfile)