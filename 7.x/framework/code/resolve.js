
// Absolute path
var path1 = resolve('/views/myview.html');

// Relative path - in this case, the resource must be in the same folder
var path2 = resolve('myview.html');

// Relative path (same as above)
var path3 = resolve('./myview.html');

// Relative path - resource is one level up
var path4 = resolve('../myview.html');
