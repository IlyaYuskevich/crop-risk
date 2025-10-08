import ee
ee.Authenticate()
ee.Initialize(project='nala-earth-engine')

# Load district boundaries (France and Germany)
depar = ee.FeatureCollection("projects/ee-france/assets/IGN/ADMIN_EXPRESS/202208/DEPAR")
depar = depar.select(['NOM', 'INSEE_DEP']).map(lambda f: ee.Feature(ee.Geometry(f.geometry().centroid()), {'name': f.get('NOM'), 'num': f.get('INSEE_DEP')}))

lkreis = ee.FeatureCollection('projects/earth-engine-460512/assets/VG2500_KRS')
lkreis = lkreis.select(['GEN', 'NUTS']).map(lambda f: ee.Feature(ee.Geometry(f.geometry().centroid()), {'name': f.get('GEN'), 'num': f.get('NUTS')}))

# merge both FeatureCollections
centroids = depar.merge(lkreis)

centroids = centroids.filter(ee.Filter.neq('name', 'Guadeloupe'))
centroids = centroids.filter(ee.Filter.neq('name', 'Mayotte'))
centroids = centroids.filter(ee.Filter.neq('name', 'Bouches-du-Rhône'))
centroids = centroids.filter(ee.Filter.neq('name', 'Nordfriesland'))

missing_centroids = ee.FeatureCollection('users/zumbuhlnick/centroid_features')

centroids = centroids.merge(missing_centroids)

# Set the date range
start_date = ee.Date('2022-10-01')
end_date = ee.Date('2025-10-01')  # is excluded

# Define image collection and variables
era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start_date, end_date)

era5 = era5.select(['temperature_2m', 'temperature_2m_min', 'temperature_2m_max', 
                    # 'dewpoint_temperature_2m',
                    # 'soil_temperature_level_1','soil_temperature_level_2', 'soil_temperature_level_3','soil_temperature_level_4',
                    'volumetric_soil_water_layer_1','volumetric_soil_water_layer_2','volumetric_soil_water_layer_3','volumetric_soil_water_layer_4',
                    'total_precipitation_sum', 'total_evaporation_sum', 'potential_evaporation_sum', 
                    # 'runoff_sum', 'u_component_of_wind_10m', 'v_component_of_wind_10m',
                    # 'leaf_area_index_high_vegetation', 'leaf_area_index_low_vegetation'
                    ])

# Map over images to extract values at centroids
def extract(image):
    date_str = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
    sampled = image.reduceRegions(collection=centroids, reducer=ee.Reducer.first())
    return ee.FeatureCollection(sampled.map(lambda f: f.set('date', date_str)))

sampled_all = era5.map(extract).flatten()


task = ee.batch.Export.table.toDrive(
    collection=sampled_all,
    description='2022_2025',
    folder='GEE_exports',
    fileNamePrefix='2022_2025',
    fileFormat='CSV'
)
task.start()