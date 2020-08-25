import pandas as pd
import numpy as np
#import yaml
import surprise
import pickle
#import sqlite3 as sql
import googlemaps
#from itertools import tee
from math import radians, cos, sin, asin, sqrt
import MountainProjectPublicAPI as mp
#import time


##Google Maps API information
#Performs request to use the Google Maps API web service
API_key = 'AIzaSyDpi3ouWiwr7SeDtT3nyFgIdsxOWpyw4Ic' #enter Google Maps API key
gmaps = googlemaps.Client(key=API_key)

##Set up cleaned_routes table
infile = pd.read_csv('./data/reduced_cleaned_routes.csv')
reduced_cleaned_routes = pd.DataFrame(infile)

#reduced_cleaned_routes = cleaned_routes[['id','lat','long']]
#reduced_cleaned_routes.to_csv('reduced_cleaned_routes.csv')
##set up rating table
#db_path = './data/climbing_full.sqlite'

#with sql.connect(db_path) as conn:
#     ratings = pd.read_sql_query('''
#    SELECT user_id, route_id, AVG(user_star) as rating
#    FROM ticks
#    WHERE user_star 
#    BETWEEN 0 AND 4
#    GROUP BY user_id, route_id
#  ''',conn)
        
# Remove any Non-Clean Routes
#ratings = ratings[ratings.route_id.isin(cleaned_routes.id.unique())]

ratings = pd.read_csv('./data/selected_ratings.csv')
ratings = pd.DataFrame(ratings)

#route coordinate lookup function
def get_route_coords(route_id, data):
    'Returns coordinates for route_id in given table.'
    for index,row in data.iterrows():
        if row.id == route_id:
            lat = row.lat
            long = row.long
    return lat,long

#raw point to point distance function
#This can be used to filter distance lookups and reduce load on gmap api
def haversine(origins, destination):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    #code source: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    # convert decimal degrees to radians
    x1, y1 = origins 
    x2, y2 = destination
    x1, y1, x2, y2 = map(radians, [x1, y1, x2, y2])

    # haversine formula 
    dlon = x2 - x1 
    dlat = y2 - y1 
    a = sin(dlat/2)**2 + cos(y1) * cos(y2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in miles. Use 6371 for kilometers.

    return c * r

#google distance and time lookup
def get_distance_duration(origins,destination,mode='driving'):
    "Get distance and time with google distance matrix API."
    dist = gmaps.distance_matrix(origins, destination, mode='driving')["rows"][0]["elements"][0]["distance"]["value"]
    travel_time = gmaps.distance_matrix(origins, destination, mode='driving')["rows"][0]["elements"][0]["duration"]["value"]
      
    #add comparison for walking vs. driving
    return dist, travel_time

#looks up favorite route and score
def best_route(pickle_path,user_id):
    'Return highest recommended route to selected user.'
    #issue. This is recommending a route already travelled.

    # Load returns tuple (predictions , recommender)
    _, recommender = surprise.dump.load(pickle_path)
    
    
    max_est_rating = 0
    max_est_rating_list = []
    for idx, row in ratings.iterrows():
        if row.user_id == user_id:
            uid = user_id
            iid = row.route_id
            true_rating = row.rating
            uid, iid, _, est, info = recommender.predict(uid,iid)
            if est > max_est_rating:
                max_est_rating = est
                max_user_id = uid
                max_route_id = int(iid)
                idxlast = idx
            if idx > 200: break 
    return max_user_id, max_route_id, max_est_rating, idxlast


def add_multi_routes(excursion_length, seed_route, max_routes=10):
    'Builds and creates table of multi-route trip sequences.'
   # t0 = time.time()
    seed_route_lat, seed_route_long = get_route_coords(seed_route, reduced_cleaned_routes)
    origins = seed_route_lat,seed_route_long

    trip_length_hours = 0
    n=2
    trip_options = pd.DataFrame(columns=['seed_route'])
    all_routes = []
    while trip_length_hours <= excursion_length:
        
        #add conditional for seed route or subsequent loop
        for idx, route in reduced_cleaned_routes.iterrows():
            if n > 2: break
            if route.id == seed_route: continue
            if idx > 200: break
            destination = route.lat,route.long
            raw_distance = round(haversine(origins, destination),2)
            if raw_distance > 50: continue #200 mile filter for raw distance between routes. this is added to reduce load on gmaps API requests.
            else: 
                dist_meters,time_seconds = get_distance_duration(origins, destination) #gmap call for directions dist and duration
                dist_miles = dist_meters/(1609.34) #converts meters to miles
                trip_length_hours = time_seconds/(60*60) + 1 #add one for approximate time spent climbing route
                if trip_length_hours > excursion_length: continue
                else:
                    new_row = {'seed_coords': origins,'seed_route': int(seed_route), 'total_trip_length': trip_length_hours, ('route_%d_id' % (n)): route.id, ('route_%d_coords' % (n)): destination, ('dist_to_route_%d' % (n)): dist_miles, ('time_to_route_%d' % (n)): trip_length_hours}
                    trip_options = trip_options.append(new_row, ignore_index=True)
                    if route.id not in all_routes: all_routes.append(route.id)
 
        #subsequent route stop loops
        n = n + 1
        
        #initialize
        vars()[('route_%d_id' % (n))] = [None]*len(trip_options.index)
        vars()[('route_%d_coords' % (n))] = [None]*len(trip_options.index)
        vars()[('dist_to_route_%d' % (n))] = [None]*len(trip_options.index)
        vars()[('time_to_route_%d' % (n))] = [None]*len(trip_options.index)

        #create columns
        trip_options[('route_%d_id' % (n))] = vars()[('route_%d_id' % (n))]
        trip_options[('route_%d_coords' % (n))] = vars()[('route_%d_coords' % (n))]
        trip_options[('dist_to_route_%d' % (n))] = vars()[('dist_to_route_%d' % (n))]
        trip_options[('time_to_route_%d' % (n))] = vars()[('time_to_route_%d' % (n))]
        
        for idx,row in trip_options.iterrows():
            #previous_coords = vars()[('route_%d_coords' % (n-1))]
            if row[('route_%d_coords' % (n-1))] is None: continue
            origins = row[('route_%d_coords' % (n-1))]
            for idx2, route in reduced_cleaned_routes.iterrows():
                for i in range(2,n):
                    if route.id == seed_route or route.id == row[('route_%d_id' % (n-1))]: 
                        skip_id = True
                    else: skip_id = False
                if skip_id == True: continue
                         #skips routes already added to trip options table
                if idx2 > 100: break #limits dataset for QA purposes
                destination = route.lat,route.long
                raw_distance = round(haversine(origins, destination),2)
                
                if raw_distance > 50: continue #filters out longer distances for efficiency and to reduce gmap calls
                
                dist_meters,time_seconds = get_distance_duration(origins, destination) #gmap call for directions dist and duration
                dist_miles = dist_meters/(1609.34) #converts meters to miles
                current_trip_length_hours = time_seconds/(60*60) + 1 #add one for approximate time spent climbing route
                total_trip_length = (current_trip_length_hours + row['total_trip_length'])
                
                if total_trip_length > excursion_length: continue
                
                new_row = {**row.to_dict(),('route_%d_id' % (n)): route.id, ('route_%d_coords' % (n)): destination, ('dist_to_route_%d' % (n)): dist_miles, ('time_to_route_%d' % (n)): current_trip_length_hours}
                new_row['total_trip_length'] = total_trip_length
                
                #create all routes list
                if route.id not in all_routes: all_routes.append(route.id)
                #add row to trip option table
                if row[('route_%d_id' % (n-1))] is not None:
                    trip_options = trip_options.append(new_row, ignore_index=True)
                  
        if n >= max_routes: break
        
        #create all routes list
    #print('Time Elapsed:', time.time() - t0)
    return trip_options, all_routes

def trip_planner(user_id, excursion_length, max_routes,selected_recommender):
    'Returns best recommended route for a user with a combination of nearby climbs.'
    t0 = time.time()
    mode = 'driving'
    ## Path to Picked Recommender
    if selected_recommender == '1':
        pickle_path = './recommenders/knn_recommender.pickle'
        pp='knn'
    elif selected_recommender == '2':
        pickle_path = './recommenders/mf_recommender.pickle'
        pp='mf'
    else: print('Invalid Recommender')
    user_id, route_id, est_rating,__  = best_route(pickle_path, user_id) #returns information on seed reco route
    
    #triptime = 1 #first climb

    trip_options = add_multi_routes(excursion_length, route_id, max_routes)
    
   # t1 = time.time() - t0
    #print("Time Elapsed, route combos added: ", t1)
    
    #create score table 
    score_table, all_routes = trip_options
    _, recommender = surprise.dump.load(pickle_path)
    
    route_est_score_dict = {} #create dict of estimate route scores for user based on itinerary.
    for i in all_routes:
        user_id, route_id, _, est, info = recommender.predict(user_id,i)
        route_est_score_dict[route_id] = est
    
    score_table['seed_route_score'] = est_rating
    score_table.insert(1, "total_score", score_table['seed_route_score'])
    for i in range(2,max_routes+1):
        #vars()[('route_%d_score' % (i))] = [None]*len(score_table.index)
        #create columns
        #score_table[('route_%d_score' % (i))] = vars()[('route_%d_score' % (i))]
        score_table[('route_%d_score' % (i))] = [None]*len(score_table.index)
        for idx, row in score_table.iterrows():
           
            #if row[('route_%d_id' % (i)) is not None: continue
            if row['route_%d_id' % (i)] is None:
                if i == (max_routes):
                #add score bonus for being under max length
                    score_table.loc[idx,'total_score'] = row['total_score'] + (excursion_length - row['total_trip_length'])*1.1
            else:
                score_table.loc[idx,'route_%d_score' % (i)] = route_est_score_dict[row['route_%d_id' % (i)]]
                score_table.loc[idx,'total_score'] = row['total_score'] + route_est_score_dict[row['route_%d_id' % (i)]]

                if i == (max_routes):
                    #add score bonus for being under max length
                    score_table.loc[idx,'total_score'] = row['total_score'] + (excursion_length - row['total_trip_length'])*1.1

    #t2 = time.time() - t0
    #print("Time Elapsed: return score table ", t2)
    
    score_table.to_csv('./data/%d_%d_%d_%s_%s_score_table.csv' % (user_id, excursion_length, max_routes,pp,mode))
    return score_table
