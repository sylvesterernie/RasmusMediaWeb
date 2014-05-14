define([
    'intern!object',
    'intern/chai!assert',
    'rasmusmediaweb/tests/testutils'
], function (registerSuite, assert, testutils) {

    testutils.setup_window();
    var hash = require('rasmusmediaweb/hash');

    registerSuite({
        name: 'hash.HashManager',

        test_set: function () {
            var manager = new hash.HashManager();
            manager.set('foo', 'bar');
            manager.set('abc', 'def');
            assert.strictEqual(window.location.hash, '#?foo=bar&abc=def');
        },

        test_get: function () {
            var manager = new hash.HashManager();
            manager.set('foo', 'bar');
            assert.strictEqual(manager.get('foo'), 'bar');
        }
    });
});
