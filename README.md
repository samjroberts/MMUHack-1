## GreatUniHack '17 Project: SafeStride
--------------------------------------------

Thanks for checking out our repo! 


## The idea: a safer route home
--------------------------------------------

The idea is simple. Mapping applications to give you the fastest route between A and B,
but this often takes you through places where you no longer feel safe. What if we can 
run open source crime data through some an algorithm that will determine the 
statisically safest route home?

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





