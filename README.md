# README


## Project 5: Docker with Mongodb

 ### 
 ### Project by: Quinn Milionis


#### About
- Application calculates control times for brevets. 
- This essentially replaces the calcuator at https://rusa.org/octime_acp.html with flask and ajax. 
- Controls are essentially "checkpoints" where a ride has to get proof of passage. The control times are the minimum and maximum times by which the rider has to arrive at the location. 
- The algorithm for calculating controle times is described at
https://rusa.org/octime_alg.html .  Additional background information
is in https://rusa.org/pages/rulesForRiders .
- Updated version in this project included two new buttons, Submit and Display. 'Submit' transmits the table data to a database, while 'Display' returns those database entires on a sepeate page.

#### Instructions
- Navigate to the directory /brevets in terminal
- Run with python3 flask_brevets.py
- Access application with browser window, navigate to http://localhost:5000
- run tests with 'nosetests'