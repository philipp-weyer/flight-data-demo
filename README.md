# Flight Data Demo

__Demonstrates some of the MongoDB Atlas Data Platform features, using a flight data themed sample set__

---
## Description

The goal of this repo is to be a simple starting place for Atlas that demonstrates some data platform features, everything based on a very basic flight data set.

These capabilities are namely:

__1. Aggregation Framework - Working with and Transforming Data__

__2. Triggers - Reacting to Changes and Building Event-Driven Architectures__

__3. Charts - Visualising Data Directly in MongoDB Atlas__

---
## Setup

__1. Configure System__
* Ensure mongosh is already installed on your system, mainly to enable the Mongo Shell

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com)  and navigate to your project
* In the project's Security tab, go to Database Access and choose to add a new user called __main_user__. For this user select the Built-In Role __Read and write to any database__ and add the user (make a note of the password you specify)
* Create an __M0__ based 3 node free replica-set in a single region of your choice with default settings. The name should be chosen to be __DemoCluster__, otherwise a few of the further scripts will have to be adapted.
* In the project's Security tab, go to Network Access and add your current IP address, in order to be able to access the clusters in your project.

__3. Setup Python Environment__
* Go to your Database overview, navigate to the cluster you just created and hit __Connect__
* Select the option of connecting your application, select the Python driver and the version that you will be using
* Copy the connection string with the username and password method, replace the placeholder in the file __connection.txt.template__ and rename the file to __connection.txt__
* Execute the following commands to setup your python environment:

```bash
python3 -m venv venv
. ./venv/bin/activate
pip3 install -r requirements.txt
```

---
## Data Preparation

Navigate to your Databases view and go to the M0 cluster, that you created earlier. On the menu on the side, select __Load Sample Dataset__ and confirm loading it.
After the data set is loaded, it is a good idea to move the dataset in question to its separate database, so that we can continue with a clean slate.
With your mongosh, connect to the cluster in question and execute the following commands:

```node
use sample_training
db.routes.aggregate([{$out: {db: 'flights', coll: 'routes'}}])
```

The resulting __flights__ database is going to be the source of all data, in the course of this demo.
The __routes__ collection now contains some information of airlines that serve routes between airports and how many stops are required between them.
On top of this, the local directory __data_generation/__ contains the file __airport-codes_json.json__, which has a lot more data on individual airports across the world. This data can be loaded with the file as follows:

```bash
cd data_generation
python3 uploadAirportData.py
```

From this data, it is now possible to create a collection called __history__, which will take our route data and relate the location information from the __airports__ collection to simulate flight histories, with realistic flight times being generated. This can be done as follows:

```bash
python3 generateFlights.py
```

---
## Aggregation Framework

A couple of simple aggregation pipeline examples have been included in this repository, in the folder __aggregations/__.

* __```airportsByElevation.json```__ runs on the __airports__ collection. It filters the airports by continent and type, before sorting them by elevation and calculating an elevation in metres, from the elevation in feet.
* __```flightsByDuration.json```__ runs on the __history__ collection. It takes all of the flights in the history and calculates a duration from the start and end dates in the documents. Based on this calculated field, the results are then sorted to yield the longest flight present in the database.
* __```averageDuration30Days.json```__ runs on the __history__ collection. It uses the $expr operator to match on multiple conditions. A specific route id and a start date between now and 30 days ago. The route_id will have to be replaced to fit an actual route that has been referenced in the __history__ collection.
* __```flightsOverTime.json```__ runs on the __history__ collection. It uses the $lookup operator to find, for every hour in the database, all the flights where start and end date lay between this point in time to evaluate how many flights are in the air at any given point in time.

The aggregation pipelines can be tested directly in the Atlas interface. For this, navigate to your cluster and click __Browse Collections__. Navigate to your database and collection and select the __Aggregation__ tab on the right. When pressing on __Create New__ > __Pipeline from Text__, you can paste the contents from your aggregation pipeline file and analyse the results.

---
## Triggers

The triggers that are included in this repository are meant to display basic functionalities of how triggers can be used to build event-driven architectures and perform incremental/real-time analytics on data that is coming in. Two triggers are included in the folder __triggers/__.

* __```flightDeparted.js```__ will be executed, when a document is inserted into the __history__ collection. If the endDate is not present, the flight is considered to just have departed, causing the trigger to insert a document into a new __events__ collection.
* __```flightLanded.js```__ will be executed, when a document is inserted or updated in the __history__ collection. If the endDate is present in the document, an aggregation pipeline is executed, calculating the average duration for the specific route for the last 30 days. If there is a sufficient difference in time between the current flight and the last 30 days, an event signifying this is generated. This is one application of real-time analytics being applied on events on the database.

A Trigger can be created by heading to the __Triggers__ under the Services section on the left-hand side in the Atlas UI. When adding a Trigger, give it a name that makes sense to you (e.g. FlightDepartedTrigger) and link your data source by selecting the Cluster you created under __Link Data Source(s)__. In the Trigger Source Details, select your cluster again, as well as the __flights__ database and __history__ collection. For the flightDeparted Trigger, select just Inserts for execution, for the flightLanded trigger, select both Inserts and Updates. Check also the __Full Document__ Trigger before pasting the contents of the files from this repo and saving the triggers.

With this in place, the triggers can be tested by executing the python scripts
in the __trigger_test__ folder.

* __```flightDeparture.py```__ script will generate documents, lacking the endDate field every 5 seconds.
* __```flightArrival.py```__ script will generate documents, including the endDate field every 5 seconds.

It's important to note, that these scripts will need to be adapted to the specific data, since it is relying on a route_id that has been referenced in the __history__ collection. Simply inspect your data and replace the ObjectId with a field that is present in the collection.

After executing the following, you can see new events being generated in the __events__ collection:

```bash
python3 flightDeparture.py
python3 flightArrival.py
```

The flightArrival script will generate some documents with flights being on time, some flights being delayed and some flights arriving early. This will be reflected in the respective events being generated.

---
## Charts

The file __charts/Air Operations.charts__ contains an example dashboard in MongoDB Atlas that can be imported and used directly.

After navigating to the Charts tab inside Atlas, you can select to import a dashboard from the dropdown menu next to the __Add Dashboard__ button. After selecting our __Air Operations.charts__ file, a dashboard will be created, referencing our data from the cluster we created. If you gave your cluster a different name than __DemoCluster__ in the first step, they can be remapped in the UI after upload of the template.

The charts display a fraction of the possiblities available in MongoDB Atlas Charts. Feel free to explore more possibilities by editing the existing charts or creating new ones.

The usage is fairly straightforward. When editing an existing or adding a new chart, the data source can be selected in the top left. If required, an aggregation pipeline can be inserted to transform the data before it's being sampled. After sampling, Charts automatically recognises the field names and data types in the left column. Depending on the chart type, these can the be dragged and dropped to the fields specified to create the visualisations. Further documentation for this can be found at this URL: [MongoDB Atlas Charts Documentation](https://www.mongodb.com/docs/charts/)
