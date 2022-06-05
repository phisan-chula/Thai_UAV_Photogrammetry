#
#
# Plot_GeoTag : read jpeg files acquired from UAV mission. JPEG files are placed
#               in a folder and read then produced KML/GPKG gis files. 
#               With KML positions are plot in timestamped 3D points. 
#
#
import pandas as pd
import geopandas as gpd
from pathlib import Path
from exif import Image
import simplekml
from simplekml import Kml, Style

def dms2dd( dms):
    return dms[0]+dms[1]/60+dms[2]/3600.

def WriteKML(df , KMLFILE ):
    sharedstyle = Style()
    sharedstyle.iconstyle.color = 'ffffffff'
    sharedstyle.iconstyle.scale = 1  # Icon thrice as big
    sharedstyle.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/square.png'
    sharedstyle.labelstyle.color = 'ff0000ff'  # Red
    kml = simplekml.Kml()
    fol = kml.newfolder(name="Image")
    for i,row in df.iterrows():
        pnt = fol.newpoint( name=f'{row.Name}' )
        pnt.coords= [ (row.Longitude, row.Latitude, row.Altitude ) ]
        #import pdb; pdb.set_trace()
        pnt.timestamp.when = str(row.DT).replace(' ','T')
        pnt.style=sharedstyle
        pnt.altitudemode = simplekml.AltitudeMode.absolute
        #pnt.altitudemode = simplekml.AltitudeMode.relativetoground 
        pnt.extrude = 1
    kml.save( KMLFILE )
    return

####################################################################

FILES = Path('20220408_ChulaUniv_M300P1/').glob('./P1/DJI*.JPG')

data = list()
for f in FILES:
    with open( f, 'rb') as im:
        im = Image(im)
        dt = im.datetime_digitized.split(' ')
        dt0,dt1 = dt[0].replace(':','-'),dt[1]
        data.append(  [f.stem[-4:], f'{dt0} {dt1}', dms2dd(im.gps_latitude),
                       dms2dd(im.gps_longitude), im.gps_altitude ] ) 
df = pd.DataFrame( data, columns=['Name','DT','Latitude','Longitude','Altitude'] )
df['DT'] = pd.to_datetime( df['DT'] )

df = gpd.GeoDataFrame( df, crs='EPSG:4326',
        geometry=gpd.points_from_xy( df.Longitude,df.Latitude, z=df.Altitude) )

WriteKML( df, 'df_GeoTag.kml' )
if 0:
    df.to_file( 'df_GeoTag.gpkg', driver='GPKG', layer='GeoTag' )
#import pdb; pdb.set_trace()
