
// Create a websocket if websocket request.
exports.get = function (req) {

  if (!req.webSocket) {
    return {
      status: 404
    };
  }

  return {
    webSocket: {
      data: {
        user: "test"
      },
      subProtocols: ["text"]
    }
  };
};
