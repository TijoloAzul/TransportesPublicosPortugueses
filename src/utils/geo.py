import geopy.distance as distance
import utils.logger as logger
import pandas as pd
import math

def compute_distance_in_path(paths):
    paths['prev_lat'] = paths.groupby('id')['lat'].shift(1)
    paths['prev_lon'] = paths.groupby('id')['lon'].shift(1)
    paths['increment'] = paths.apply(
        lambda pt: compute_dist([pt['prev_lat'], pt['prev_lon']],[pt['lat'], pt['lon']]),
        axis = 1)
    paths['distance'] = paths.groupby('id')['increment'].cumsum()
    return paths.drop(columns=['prev_lat', 'prev_lon', 'increment'])

def compute_dist(A, B):
    if math.isnan(A[0]) or math.isnan(A[1]):
        return 0
    return int(distance.great_circle((A[0], A[1]), (B[0], B[1])).meters)
