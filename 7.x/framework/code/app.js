// Get application name
var name = app.name;  // com.enonic.app.superhero

// Get application version
var version = app.version;  // 1.2.0

// Get some config from the <app.name>.cfg file
var myKey = app.config.secretkey; // Reads the string stored in the "secretkey" property
