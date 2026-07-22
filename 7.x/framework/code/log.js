// Log a simple message
log.debug('Hello World');

// Log a formatting message
log.info('Hello %s', 'World');

// Log a formatting message
log.warning('%s %s', 'Hello', 'World');

// Log using the built-in JSON converter
log.error('My JSON %s', object );

// Log an exception with stack trace
try {
  thisWillFail();
} catch (e) {
  log.error('An error occurred', e);
}

// Log a formatting message with exception stack trace
try {
  bean.run();
} catch (e) {
  log.error('Error in %s', 'myFunction', e);
}
