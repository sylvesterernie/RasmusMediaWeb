define([], function () {

    return {
        setup_window: function () {
            var jsdom = require('jsdom')
            window = jsdom.jsdom().parentWindow;
        }
    };
});
