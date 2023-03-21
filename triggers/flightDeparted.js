exports = function(changeEvent) {
  const fullDocument = changeEvent.fullDocument;

  if (fullDocument['endDate'] == undefined) {
    const collection = context.services.get('DemoCluster').db('flights').collection('events');
    let result = collection.insertOne({
      eventType: 'FLIGHT_DEPARTED',
      eventDate: fullDocument['startDate'],
      flightId: fullDocument['_id']
    });
  }
};
