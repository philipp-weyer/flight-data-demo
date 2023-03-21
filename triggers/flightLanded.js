exports = async function(changeEvent) {
  const fullDocument = changeEvent.fullDocument;

  if (fullDocument['endDate'] !== undefined) {
    const history = context.services.get('DemoCluster').db('flights').collection('history');
    const events = context.services.get('DemoCluster').db('flights').collection('events');

    let averageDuration = await history.aggregate([{
      $match: {
        $expr: {
          $and: [
            {$eq: ['$route_id', fullDocument['route_id']]},
            {$lte: ['$startDate', new Date()]},
            {$gte: ['$startDate', {$dateSubtract: {startDate: new Date(), amount: 30, unit: 'day'}}]}
          ]
        }
      }
    }, {
      $set: {
        duration: {
          $dateDiff: {
            startDate: '$startDate',
            endDate: '$endDate',
            unit: 'minute'
          }
        }
      }
    }, {
      $group: {
        _id: null,
        averageDuration: {
          $avg: '$duration'
        }
      }
    }]).toArray();

    averageDuration = averageDuration[0]['averageDuration'];
    
    let currentDuration = (fullDocument['endDate'] - fullDocument['startDate']) / 1000 / 60;
    
    let doc = {};

    if (currentDuration > averageDuration * 1.15) {
      doc = {
        eventType: 'FLIGHT_LANDED_DELAYED',
        eventDate: fullDocument['endDate'],
        flightId: fullDocument['_id'],
        delay: currentDuration - averageDuration,
        description: "Flight took more than 15% longer than usual in the past 30 days"
      };
    } else if (currentDuration < averageDuration * 0.85) {
      doc = {
        eventType: 'FLIGHT_LANDED_EARLY',
        eventDate: fullDocument['endDate'],
        flightId: fullDocument['_id'],
        advance: averageDuration - currentDuration,
        description: "Flight took more than 15% shorter than usual in the past 30 days"
      }; 
    } else {
      doc = {
        eventType: 'FLIGHT_LANDED',
        eventDate: fullDocument['endDate'],
        flightId: fullDocument['_id']
      };
    }

    let result = events.insertOne(doc);
  }
};
