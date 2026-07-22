// Listen to a websocket event
exports.webSocketEvent = function (event) {

  if (event.type == 'open' && event.data.user == 'test') {
    // Do something on open
  }

  if (event.type == 'message') {
    // Do something on message recieved
  }

  if (event.type == 'close') {
    // Do something on close
  }

};
