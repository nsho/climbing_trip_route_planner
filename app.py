import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px 
import pandas as pd 
#import sqlite3 as sql
import os 
# Local Python Files
#import climbing_queries as sql
#import recommenders as rec 
#import ui_components as ui 
import trip_route_planner as tp
import os.path
from os import path

external_scripts = ['https://polyfill.io/v3/polyfill.min.js?features=default', 'https://maps.googleapis.com/maps/api/js?key=AIzaSyDpi3ouWiwr7SeDtT3nyFgIdsxOWpyw4Ic&callback=initMap&libraries=&v=weekly']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = app.server
# Load Up a Recommender
#recommender = rec.SurpriseRecommender()
#recommender.load_recommender('svd')
#TMP_UIDS = recommender.sample()

API_key = "AIzaSyDpi3ouWiwr7SeDtT3nyFgIdsxOWpyw4Ic"

#add waypoints, separated by pipes, max of 20
mode = "driving" #options: driving, walking, transit, bicycle

#app = dash.Dash(__name__, external_scripts=external_scripts)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climbing Route Trip Planner'
##hardcoded lat longs for testing
#romeLat = 41.9
#romeLong = 12.49
#milanLat = 45.46
#milanLong = 9.19

#start = "(41.9,12.49)"
#end = "(45.46,9.19)"

max_routes = 4
user_id = 10106
excursion_length = 8
default_score_table = './data/%d_%d_%d_%s_%s_score_table.csv' % (user_id,excursion_length,max_routes,'knn',mode)
default_score_table = pd.read_csv(default_score_table)
default_score_table = pd.DataFrame(default_score_table)
default_score_table = default_score_table.nlargest(10,'total_score')
#default_score_table = default_score_table[default_score_table.columns.drop(list(default_score_table.filter(regex='coords')))]
#default_score_table = default_score_table[default_score_table.columns.drop(list(default_score_table.filter(regex='dist')))]
#default_score_table = default_score_table[default_score_table.columns.drop(list(default_score_table.filter(regex='time')))]


def get_gmaps_data(df):
    'function to set google maps data.'
    #get lat long of best scored trip
    waypoints = ''
    for index,row in df.iterrows():
            if row.total_score == df['total_score'].max():
                top_row = index
                origin = str(row['seed_coords'])
                for i in range(2,max_routes+1):

                    if str(row['route_%d_coords' % (i)]) == 'nan': 
                        destination = str(row['route_%d_coords' % (2)])
                        break
                    if i == max_routes - 1:
                        waypoints = waypoints + str(row['route_%d_coords' % (i)])
                    elif i < max_routes:
                        waypoints = waypoints + str(row['route_%d_coords' % (i)]) + '|'
                    if i == max_routes:
                        destination = str(row['route_%d_coords' % (i)])
    
    waypoints = waypoints.replace(' ','')
    waypoints = waypoints.replace('(','')
    waypoints = waypoints.replace(')','')
    waypoints = waypoints.strip('|')        
    origin = origin.replace(' ','')
    origin = origin.replace('(','')
    origin = origin.replace(')','')
    destination = destination.replace(' ','')
    destination = destination.replace('(','')
    destination = destination.replace(')','')
    #print('origin:',origin)
    #print('waypoints:', waypoints)        
    #print('destination:',destination)        
    gmaps_src="https://www.google.com/maps/embed/v1/directions?key="+API_key+"&mode="+mode+"&origin="+origin+"&waypoints="+waypoints+"&destination="+destination
    #print(gmaps_src)
    return gmaps_src

gmaps_src = get_gmaps_data(default_score_table)

app.layout = html.Div(children=[
        html.H1('Climbing Trip Route Planner'),
        html.Label('Select Recommender'),
            dcc.Dropdown(
                id='recommender_dropdown',
                options=[
                    {'label':'KNN Recommender', 'value': '1'},
                    {'label':'MF Recommender', 'value': '2'}
                    #,{'label':'Top K Recommender', 'value': }
                ],
                value='1'
                ),
        html.Label('Select Transit Mode'),
            dcc.Dropdown(
                id='transit_dropdown',
                options=[
                    {'label':'Walking', 'value': '1'},
                    {'label':'Driving', 'value': '2'},
                    {'label':'Transit', 'value': '3'},
                    {'label':'Bicycling', 'value': '4'}
                    #,{'label':'Top K Recommender', 'value': }
                ],
                value='2'
                ),
        html.Label('Select User ID'),
            dcc.Dropdown(
                id='user_id_dropdown',
                options=[
                    {'label': '10101', 'value': '10101'},
                    {'label': '10102', 'value': '10102'},
                    {'label': '10106', 'value': '10106'},
                    {'label': '10116', 'value': '10116'},
                    {'label': '10118', 'value': '10118'},
                    {'label': '10121', 'value': '10121'},
                    {'label': '10112', 'value': '10112'}
                ],
                value='10106'
            ),
        html.Label('Select Excursion Length'),
    dcc.Slider(
        id='excursion_length_slider',
        min=0,
        max=15,
        marks={i: 'Hours {}'.format(i) if i == 1 else str(i) for i in range(1, 15)},
        value=8,
        ),
        html.Label('Select Maximum Routes'),
    dcc.Slider(
        id='max_route_slider',
        min=2,
        max=15,
        marks={i: 'Route Count {}'.format(i) if i == 1 else str(i) for i in range(1, 15)},
        value=4,
        ),
        html.Iframe(id='gmap', width="100%", height="100%", src=gmaps_src),
    
        dash_table.DataTable(id='score_table',
                             data=default_score_table.to_dict('records'),
                             columns=[{"name": i, "id": i, "selectable": True} for i in default_score_table.columns],sort_action="native",
        sort_mode="multi")

        ],id = 'main'
                      #,style={'columnCount': 1}
                     )


# app.index_string = test

#cleaned_routes = pd.read_csv('./data/cleaned_routes.csv')

#cleaned_routes = pd.DataFrame(cleaned_routes)

@app.callback(
    [Output('score_table', 'data'), Output('score_table', 'columns'),
     Output('gmap', 'src')
    ],
    [Input('recommender_dropdown', 'value'),
     Input('user_id_dropdown', 'value'),
     Input('excursion_length_slider', 'value'),
     Input('max_route_slider', 'value')
    ])
def create_score_table(recommender_input, user_id_input, excursion_length_input, max_route_input):
    max_routes = int(max_route_input)
    user_id = int(user_id_input)
    excursion_length = int(excursion_length_input)
    mode = 'driving'
    if recommender_input == '1':
        pp = 'knn'
    elif recommender_input == '2':
        pp = 'mf'
    else: print('Invalid Recommender')
    score_table = './data/%d_%d_%d_%s_%s_score_table.csv' % (user_id,excursion_length,max_routes,pp,mode)
    
    if path.isfile(score_table): #checks cache for whether this particular inputs results already exist.
        score_table = pd.read_csv(score_table)
        score_table = pd.DataFrame(score_table)
    else:
        #if doesn't exist, run trip planner to create new one.
        score_table = tp.trip_planner(user_id, excursion_length, max_routes, recommender_input)
        #score_table = score_table.drop(columns=['Unnamed: 0'])
        
    gmaps_src = get_gmaps_data(score_table)
    gmaps_src = str(gmaps_src)
    print('updated src:', gmaps_src)
    
    #drop rows and columns from display
    #return top ten rows only
    score_table = score_table.nlargest(10,'total_score')
    #drop columns
    
    score_table = score_table[score_table.columns.drop(list(score_table.filter(regex='coords')))]
    score_table = score_table[score_table.columns.drop(list(score_table.filter(regex='dist')))]
    score_table = score_table[score_table.columns.drop(list(score_table.filter(regex='time')))]
    #set columns
    columns=[{"name": i, "id": i} for i in score_table.columns]
  
    if score_table.empty == True:
        score_table = './data/empty_scores.csv'
        score_table = pd.read_csv(score_table)
        score_table = pd.DataFrame(score_table)
    
    return score_table.to_dict('records'), columns, gmaps_src

if __name__ == '__main__':
    
    app.run_server(debug=True)
