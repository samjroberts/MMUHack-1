## GreatUniHack '17 Project: SafeStride
--------------------------------------------

Thanks for checking out our repo, the winner of the American Express "Best Innovative Real Time Digital Travel Companion" category at GreatUniHack 2017 (a MLH season 18 round). Full results at https://greatunihack17.devpost.com/submissions. 


## The idea: a safer route home
--------------------------------------------

The idea is simple. Mapping applications such as Google Maps give you the fastest route
between A and B, but this often takes you through places where you no longer feel safe. 
But what if we were to run open source crime data through some sort of algorithm that will
determine the statisically safest route between these points?

You're welcome. 


## Using the SafeStride website
--------------------------------------------

- Navigate to: https://safestride.pythonanywhere.com/MMUHack/default/index
- Input where you're coming from and where you are going
- Click 'Show Map!' and the rest is done for you!


## How does it work?
--------------------------------------------

When we have got the input for the starting and finishing locations, we generate a
range of viable walking routes between the two locations. We then analyse the danger
along these routes by modelling them against recent crime.

Crime data is downloaded and plotted as a function of the starting and finishing locations
(latitude and longitude). By plotting the locations and densities of relevant crimes, we are 
able to generate a density that closely corresponds to the historic probability of a crime. 

We then need to analyse the viable routes and choose the safest route to present back. 
Standard B-spline surface fitting algorithms firstly perform the parametrization of data, 
which associate suitable parameter values for each input point, and then form a linear 
system with control points as unknowns. This enables an analysis of the total area 
occupied by a route as if we were performing a 2D line integral. 

The route occupying the smallest area, and thus the safest route, is returned. We
return that to the user, visualising it on the map. 



## The technical detail
--------------------------------------------

Currently the website is being hosted using pythonanywhere, an online service that makes use of Web2Py.
This meant we oly needed to make edits to the view (default.py) and to the template (index.html), as the
rest of the project dependencies were dealt with by application. However web2py has issues due to the 
controlled environment, which meant we had less control over the entire stack. 

Work is currently being done to move this over to a Django framework, where we have more control over all
elements of the code. This also gives us more control over our models and over our database. This alow a
much more scalable solution to be provided, as we can prodcutionise and play with changes in seperate 
environments before migrating any changes to the productionised server. 



