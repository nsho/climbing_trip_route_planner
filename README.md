# Rock Climbing Mult-Route Trip Planner

### Composite Trip Planner
The project builds upon recommender systems, and creates a multi-route rock climbing trip planner application. The trip-planner incorporates my project partner's recommender model work for scoring individual routes, and seeks to optimize a multi-route trip for a user. The user can visit the application in a web browser, select a recommender method, excursion length, travel mode and the maximum number of routes.
 
#### User Interface: DASH Framework

We explored a variety of user interface options. These ranged from a simple locally hosted webpage to web hosted Model-View-Controller Python frameworks such as Django or Web2py. Initially we considered hosting a Django project on pythonanywhere.com, but ultimately chose to locally host the application with the DASH python microframework. The DASH framework is itself a framework built upon the Flask framework. Prerequisites for DASH include Python programming skills along with basic knowledge of HTML, CSS and serving web pages.

The DASH frameworks allow a user to create a web application with Python, and provides a user ample documentation to make a basic UI with graphs, inputs, sliders and charts. Its comprehensive documentation advocates separating the app into two components: the layout and the functions that process inputs and outputs. It is a popular framework for Data Scientists to show their work.
 
####Trip Planner Application

The trip planner application follows the two component DASH structure closely. It comprises a layout that receives trip and recommender parameters, and outputs recommended trips. The layout also includes a Google Map rendering of the highest rated route sequence. The second component comprises the code that processes the input parameters, Mountain Project data and then compiles recommended sequences for the output. It also creates the Google Maps rendering API calls. The application includes two python scripts: **app.py** and **trip_route_planner.py**.

**App.py** includes the layout, data processing for the map rendering and some processing to cache results in the datasets folder. The caching mechanism allows for improved performance. The mechanism saves the returned table results for the selected parameters by a user. Without this mechanism, it may take 20-120s to return results depending on the parameters selected by a user. The advantages of caching are twofold. It allows for instantaneous returned results when the same parameters are reused, enabling a better user experience. It also reduces the load on the Google Maps Distance Matrix API, which otherwise drives up costs.

The second python file **trip_route_planner.py** is imported by **app.py** and contains the primary functions that create the recommended route sequences. In the following section we document these functions in depth.

#### Planner Application Functions

The primary function is **trip_planner**. This function ultimately calls all other functions, and aggregates the data into the scoring table. The scoring table is ultimately what is presented in the layout of the application.

Within **trip_planner**, there are several other functions: **best_route** and **add_multi_routes**. The function also imports the selected recommender as a pickle, and will execute the recommender function on waypoint and destination routes. Functions indirectly called include get_route_coords, haversine and get_distance_duration.

The **trip_planner** function accepts Mountain Project user ID, maximum time travelling (excursion length), preferred maximum number of routes and the selected recommender model. The function finds optimal multi-route sequences. It begins calling **best_route** to find the highest recommended route (the ‘seed route’) for a user.

After the function determines the seed route, the function executes add_multi_routes to build a sequence table of multiple rock climbing routes. The function then reruns the recommender on each climbing route ID in each sequence and begins building the Score Table. Details on the scoring criteria are provided in the methods section.

The **best_route** function accepts recommender file path and Mountain Project user ID. It returns the highest recommended route for the given user.

The **add_multi_routes** function accepts maximum excursion length, seed route ID and maximum routes. It compiles all the trip options that ultimately create the scoring table, but does not yet include the scores.
This function calls **get_route_coords** to calculate the coordinates for the seed route. It then loops through the mountain project routes data to find routes that fit the given criteria. Each subsequent route is either added as an additional sequence permutation and included in the trip option table, or passed as failing for failing the given criteria.
Each loop calls the haversine function to screen out unreasonably distant routes, and then uses **get_distance_duration** to receive distance and travel duration from the Distance Matrix API between each route in the currently accumulating sequence.

The **get_route_coords** function accepts two items, a route ID and Mountain Project set reference. It looks up the route ID and returns the latitude and longitude of the route location. The function is used in **add_multi_routes**.

The **haversine** function accepts a pair of origin and destination GPS coordinates. The function finds the ‘haversine’ distance between the two points and is executed in add_multi_routes. With the Earth considered a sphere, the haversine function finds the surface distance between the coordinates. Effectively this finds the raw distance between the two points mathematically. The haversine distance function lacks the nuance required to provide navigable directions, but executes with high efficiency. Additionally, the function quickly filters out unreasonably distant routes from the result set, and also reduces volume on the Distance Matrix API.

The **get_distance_duratio**n function accepts a pair of origin and destination GPS coordinates and the transit mode. It calls and returns data from the Google Maps Distance Matrix API. Data returned includes coordinate distance and travel duration.
 
#### Scoring Table Criteria

The trip planner returns the Score Table which builds up a multi-route score based on several criteria. Each individual route has an estimated rating between 1-5 based on the recommender algorithm selected. For example, if four routes are included in the sequence, they will receive up to 20 points for individual route ratings.
The sequence also benefits by reducing the amount of travel time. For each hour under the maximum excursion length selected, the hour is multiplied by 1.1 and added to the overall score. This constraint allows the recommended sequences to approach the optimal route sequence in accordance with common knapsack problems.
 
### Google Maps API Overview

The Google Maps API comprises many separate APIs. Google structures them by device (Android and iOS SDKs) or as web services. After some research, one can understand how they complement one another by considering the JavaScript Maps API as the parent API, and the many separate web service APIs as pieces of it.
 
The primary set up steps include: 1.) Create Google cloud console account and associate with billing information. Billing is rated on a per request basis. New users receive approximately $300 in free credit, which is suitable for many small application set ups. 2.) Obtain an API key for each particular sub-API utilized. For this project we use two separate APIs, but choose to reuse the same key. 3.) Review security settings and whitelist specific IPs as necessary to ensure that excessive public requests do not accrue unexpected charges.

As noted, the project incorporates two separate Google Maps APIs. The Distance Matrix API and the Maps Embed API.

The Distance Matrix API does not include a map rendering agent. It solely receives geo data and returns the requested data output. It can be incorporated into Python code by importing the googlemaps Python library. The API is a core piece of the general Google Maps API and many of the other Maps APIs reuse its core function.

The Distance Matrix API accepts location data (typically in the form of coordinates, but Google can look up real place names) from multiple locations and returns the distance (meters) and time (seconds) that it takes to traverse the distance. The required inputs are origin location, destination location and optional waypoints. (High numbers of waypoints incur higher API request fee rates.) Optional parameters that one can include transit mode (walking, driving, bicycling and transit).

The other Maps API incorporated is the Maps Embed API directions service. The directions service accepts the same inputs as the Distance Matrix API, but returns an iFrame Map rendering of the route for javascript-less integration into web pages. The map rendering can be enlarged to view standard Google Maps features, such as place information and satellite images of the routes.

A limitation to the API results in some instances where the Maps Embed API and the Distance Matrix API do not return equivalent distance and travel times with identical input coordinates and transit parameters. It seems that the Embed API rendering avoids returning hybrid walking/driving directions. This limitation is problematic as rock climbers often must access rarely traversed walking paths to arrive at a climbing route site. On the other hand, the Distance Matrix may be providing more precise walking/driving hybrid directions, but this remains unconfirmed as one cannot see waypoint additions in the API’s return data.
