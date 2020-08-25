# Rock Climbing Mult-Route Trip Planner

Table of Contents
=================
* [Composite Trip Planner](#composite-trip-planner)
     * [User Interface: DASH Framework](#user-interface-dash-framework)
     * [Trip Planner Application](#trip-planner-application)
     * [Planner Application Functions](#planner-application-functions)
     * [Scoring Table Criteria](#scoring-table-criteria)
* [Google Maps API Overview](#google-maps-api-overview)
* [Background Literature](#background-literature)
* [References](#references)
     * [Climba Application Github: <a href="https://github.com/backslash451/Climba#version-history">https://github.com/backslash451/Climba#version-history</a>](#climba-application-github-httpsgithubcombackslash451climbaversion-history)

### Composite Trip Planner
The project builds upon recommender systems, and creates a multi-route rock climbing trip planner application. The trip-planner incorporates my project partner's recommender model work for scoring individual routes, and seeks to optimize a multi-route trip for a user. The user can visit the application in a web browser, select a recommender method, excursion length, travel mode and the maximum number of routes.
 
#### User Interface: DASH Framework

We explored a variety of user interface options. These ranged from a simple locally hosted webpage to web hosted Model-View-Controller Python frameworks such as Django or Web2py. Initially we considered hosting a Django project on pythonanywhere.com, but ultimately chose to locally host the application with the DASH python microframework. The DASH framework is itself a framework built upon the Flask framework. Prerequisites for DASH include Python programming skills along with basic knowledge of HTML, CSS and serving web pages.

The DASH frameworks allow a user to create a web application with Python, and provides a user ample documentation to make a basic UI with graphs, inputs, sliders and charts. Its comprehensive documentation advocates separating the app into two components: the layout and the functions that process inputs and outputs. It is a popular framework for Data Scientists to show their work.
 
#### Trip Planner Application

The trip planner application follows the two component DASH structure closely. It comprises a layout that receives trip and recommender parameters, and outputs recommended trips. The layout also includes a Google Map rendering of the highest rated route sequence. The second component comprises the code that processes the input parameters, Mountain Project data and then compiles recommended sequences for the output. It also creates the Google Maps rendering API calls. The application includes two python scripts: **app.py** and **trip_route_planner.py**.

**App.py** includes the layout, data processing for the map rendering and some processing to cache results in the datasets folder. The caching mechanism allows for improved performance. The mechanism saves the returned table results for the selected parameters by a user. Without this mechanism, it may take 20-120s to return results depending on the parameters selected by a user. The advantages of caching are twofold. It allows for instantaneous returned results when the same parameters are reused, enabling a better user experience. It also reduces the load on the Google Maps Distance Matrix API, which otherwise drives up costs.

The second python file **trip_route_planner.py** is imported by **app.py** and contains the primary functions that create the recommended route sequences. In the following section we document these functions in depth.

#### Planner Application Functions

The primary function is **trip_planner**. This function ultimately calls all other functions, and aggregates the data into the scoring table. The scoring table is ultimately what is presented in the layout of the application.

Within **trip_planner**, there are several other functions: **best_route** and **add_multi_routes**. The function also imports the selected recommender as a pickle, and will execute the recommender function on waypoint and destination routes. Functions indirectly called include get_route_coords, haversine and get_distance_duration.

**trip_planner**: accepts Mountain Project user ID, maximum time travelling (excursion length), preferred maximum number of routes and the selected recommender model. The function finds optimal multi-route sequences. It begins calling **best_route** to find the highest recommended route (the ‘seed route’) for a user.

After the function determines the seed route, the function executes add_multi_routes to build a sequence table of multiple rock climbing routes. The function then reruns the recommender on each climbing route ID in each sequence and begins building the Score Table. Details on the scoring criteria are provided in the methods section.

**best_route**: accepts recommender file path and Mountain Project user ID. It returns the highest recommended route for the given user.

**add_multi_routes**: accepts maximum excursion length, seed route ID and maximum routes. It compiles all the trip options that ultimately create the scoring table, but does not yet include the scores.

This function calls **get_route_coords** to calculate the coordinates for the seed route. It then loops through the mountain project routes data to find routes that fit the given criteria. Each subsequent route is either added as an additional sequence permutation and included in the trip option table, or passed as failing for failing the given criteria.

Each loop calls the haversine function to screen out unreasonably distant routes, and then uses **get_distance_duration** to receive distance and travel duration from the Distance Matrix API between each route in the currently accumulating sequence.

**get_route_coords**: accepts two items, a route ID and Mountain Project set reference. It looks up the route ID and returns the latitude and longitude of the route location. The function is used in **add_multi_routes**.

**haversine**: accepts a pair of origin and destination GPS coordinates. The function finds the ‘haversine’ distance between the two points and is executed in add_multi_routes. With the Earth considered a sphere, the haversine function finds the surface distance between the coordinates. Effectively this finds the raw distance between the two points mathematically. The haversine distance function lacks the nuance required to provide navigable directions, but executes with high efficiency. Additionally, the function quickly filters out unreasonably distant routes from the result set, and also reduces volume on the Distance Matrix API.

**get_distance_duratio**: accepts a pair of origin and destination GPS coordinates and the transit mode. It calls and returns data from the Google Maps Distance Matrix API. Data returned includes coordinate distance and travel duration.
 
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

### Background Literature

As noted, scant literature exists on recommender systems for rock climbing, however we observe in a project (Samuel, Maliki) that provides recommendations for Italian centric rock climbing routes. This initial project became the ‘Climba’ route finder application in which the project collected Italian climbing route rating data and provided recommendations in a user friendly iOS mobile application. (The application is no longer operational, but the code remains open source and available on github.) The authors attempted to model the project for their native Budung region in Indonesia. This paper also presents a framework for incorporating the Google Maps API as a method for looking up GPS coordinates, which we borrow for the Trip Planner application.

To research the trip planner application, we look towards travel recommender system research in general, rather than focusing on the sport of rock climbing specifically. We observe some common characteristics: location aware recommendation (Jiao), the concept of ‘mobile tourism’, where all relevant information can be accessed from the internet, and advocacy for collaborative filtering that creates user profiles (Gavalas). In general, personalization has been recognized as an important factor for providing satisfying composite trip recommendations (Gavalas).

The primary travel recommendation paper we detail is A Travel Recommender System for Combining Multiple Travel Regions to a Composite Trip (Herzog D). This informs the structure followed by the Multi-Route Trip Planner application. It asserts that few recommender systems exist that can assist travelers in determining between multiple destinations within a multi-destination trip. The authors outline methods for creating a multi-destination trip that requires finding destinations satisfying to a user via similarity comparisons to their known interests. They equivocate the combinatorial optimization task with the “Oregon Trail Knapsack Problem’ commonly discussed in Computer Science and Mathematics (Burg). Moreover, the authors consider how to avoid extended travel duration between destinations, while balancing the tradeoff of diminishing experiential diversity that may correlate with destinations with shorter distances between them.

The paper begins by explaining a simple example of Tourist Trip Design Problem (TTDP) that carries throughout the rest of the paper: An individual is booking a trip that must be completed within a certain timeframe and budget range--while simultaneously ensuring that it comprises numerous satisfying experiences. The composite destination sequences are scored continuously, and the highest scoring sequence will be recommended to a user. To score each sequence the authors give each location a user specific score and the sequence score accumulates. Some sequences include penalizing factors. The authors provide the outline for finding an optimal trip for a user to multiple geographic regions, while complying with trip duration and budget constraints.

Locations are scored based upon user preferences. Users are matched via collaborative filtering with a finite set of aggregated user behavioral profiles (i.e. ‘free spirit’ or ‘cultural explorer’). Based on the aggregate behavioral profile they are matched with destinations on a 5-point ‘Likert scale’. A Likert scale is commonly deployed in surveys and comprises ordinal categorical variables of user preferences (i.e. ‘very unsatisfied’ up to ‘very satisfied’). After location combinations are created, the authors explain how they implement the constraints and penalizing factors: preferred trip duration, budget range, location seasonality preference changes and security (comfort with crime levels). The preferred trip locations are grouped together as regions and subregions to reduce the computational load. They also argue that grouping nearby destinations into regional categories naturally results in more diverse experiences, as proximity can correlate with cultural similarity. To further distinguish regions, they penalize scores for regions that rate similarly to earlier destinations in the composite trip. This allows for the satisfaction derived from each individual destination to be partially dependent on other destinations within the composite trip.

In addition to penalizing regions that are distant from each other, the paper’s method also adds a penalizing factor to the length of stay in a destination. They assume (albeit arbitrarily) that satisfaction peaks by spending one week in a location, and diminishes if staying longer than a week. The authors rationalize that satisfaction decreases after a traveller thoroughly explores a region, and they apply this factor uniformly. (Meaning the presumed optimal length of stay does not change based on regional factors.)

The authors evaluate their multi-destination recommender model with an expert study. The study selected a group of ‘experts’ that have knowledge about travelling, destinations and the types of personality profiles of different types of travelers. The expert analyzes a large selection of trip recommendations for each user type. The selections are created with the authors own algorithm, and compare against two other baseline recommender models. The three recommendations for each user are presented blindly to the expert.

The expert rates each on a Likert scale in the following categories: A) General satisfaction, B) diversity of experiences, C) perceived overall fitness of experiences as a group and D) the reasonableness of routing. The recommendations are compared against recommendation sets from two other baseline algorithms. 1.) The first excludes the authors’ techniques to make ratings for each component trip partially dependent on the others and their penalty for destination visits that are less than the length of optimal stay. 2.) The second is a top-k approach and enables similar techniques to make component trip ratings partially dependent on others. However, due to the way they process the recommender, each region is evaluated only once when comparing with an earlier destination, and if filtered out cannot be reselected within a different combination of trips (Xie).

In the categories evaluated, the authors algorithm performed best in terms of A) overall satisfaction, C) regional fit and D) reasonableness of routing. The baseline algorithms both performed equally well and better than the authors’ algorithm for experiential diversity, and the top-k approach yielded better results than the first baseline for all other three categories. 
The paper acknowledges, but lacks information about sorting through large quantities of data and result sets. Many result trip sequences will have extraordinarily close overall scores to other sequences and it may be efficient to drop some or develop a new constraint or scoring feature to provide a more diverse range of result scores. 

The only measure that they take is to reduce the number of destinations by combining them in the same region. This will not be applicable for the climbing application as climbing trips need to be within the same region, so that a climber can reasonably visit multiple routes in the same day.

The authors also acknowledge that the expert study shows that their algorithm performs marginally worse for the primary category they were attempting to improve upon: B) diversity of experiences. They suggest that adding to the penalty factor could improve on this limitation. This will not be relevant for the climbing application however, as the primary experiential difference can be deterministically evaluated by the route difficulty and type. Despite the noted limitations, the authors provide a clear framework for creating a composite trip recommender algorithm. They offer important discussion around constraints and the importance of retaining diverse experience between trip components. The authors successfully argue that travel recommendations are more complex than single recommendations, as tourists have to deal with budget and time constraints.

While the paper remains extremely instructive for the Climbing Trip Planner app, travelling between climbing routes is not as clean cut as between large cities. A climber may need to traverse difficult terrain on foot, rather than hopping in a car or plane. Climbers may enjoy similar difficulties if distance is short, but may be willing to travel a farther distance for a particularly challenging or fun climb. 

Additionally, a climber may choose to find a non-rope boulder sequences outside of combinations with equipment heavy climbs or to structure their climbing  route sequence based on varying route difficulty. For these reasons, the methods that the paper proposes to provide experiential diversity have limited relevance to our Climbing Trip Planner project.


### Future Development

Additional work for the multi-route climbing recommendation system should also include user based collaborative filtering to create aggregate user profiles. With reduced quantity of user lookups we can determine that sequence recommendations can be processed with significantly more efficiency. Additionally we could allow for additional customization parameters in the application so that, for example, a user can deterministically filter recommendations based on difficulty rating or climbing types. This would ensure that a user receives experiential diversification while retaining the spontaneity that results from recommender systems. Evaluating trip sequences in terms of user satisfaction remains subjective, however a user survey along with application usage analytics could be deployed to inform continued application enhancements.

### References

##### Climba Application Github: https://github.com/backslash451/Climba#version-history

##### DASH source:
https://www.tutorialspoint.com/python_web_development_libraries/python_web_development_libraries_dash_framework.htm#:~:text=Dash%20is%20an%20open%2Dsource,very%20familiar%20with%20web%20development.
 
##### Haversine distance:
 
https://en.wikipedia.org/wiki/Haversine_formula#:~:text=The%20haversine%20formula%20determines%20the,and%20angles%20of%20spherical%20triangles.
 
https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

##### Google Maps APIs: 
https://developers.google.com/maps/apis-by-platform

