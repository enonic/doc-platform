var authLib = require('/lib/xp/auth');

// Filter every reqeust
exports.autoLogin = function (req) {
    log.info('Invoked only unless user is already authenticated');
};

// Override error handler when authentication is required
exports.handle401 = function (req) {
    var body = generateLoginPage();
    return {
        status: 401,
        contentType: 'text/html',
        body: body
    };
};

// Triggered when user visits the ID providers login endpoint
exports.login = function (req) {

    var redirectUrl = req.validTicket ? req.params.redirect : undefined;

    var body = generateLoginPage(redirectUrl);
    return {
        contentType: 'text/html',
        body: body
    };
};

// Triggered when user visits the ID providers logout endpoint
exports.logout = function (req) {

    // Sign user out of XP
    authLib.logout();

    var redirectUrl = req.validTicket ? req.params.redirect : undefined;

    if (redirectUrl) {
        return {
            redirect: redirectUrl
        };
    } else {
        var body = generateLoginPage();
        return {
            contentType: 'text/html',
            body: body
        };
    }
};
