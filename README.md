# OpenStreetMap Data Case Study

This is a Udacity project for the module "Data Wrangling" of the "Data Science for Business" course. The goal of this project was to use data munging techniques to clean the OpenStreetMap data for Rio de Janeiro, RJ, Brazil.

### Map Area

Rio de Janeiro, RJ, Brazil 

https://www.openstreetmap.org/relation/2697338

https://overpass-api.de/api/map?bbox=-43.7997,-23.1157,-43.0959,-22.7129

I chose this area because this is the city I currently live in. It would be nice to have the opportunity to contribute to its improvement. 

### Overview of the data

- The file has **280 MB**. 

- Number of unique users that have contributed to the map: 1,703
code number_users.py

- Number of nodes and ways: 
 'node': 117,986
 'way': 19,665

code Iterparse.py

- Number of "k" values for each "<tag>":
'lower': 522194, 
'lower_colon': 50664, 
'other': 22223, 
'problemchars': 2
