exports.handle404 = function (err) {
  return {
    contentType: 'text/html',
    body: `
<html>
  <body>
      <h1>No page for you!</h1>
  </body>
</html>
`
  }
};

exports.handleError = function (err) {
  return {
    contentType: 'text/html',
    body: `
<html>
  <body>
      <h1>Error code "${err.status}" </h1>
  </body>
</html>
`
  }
};
