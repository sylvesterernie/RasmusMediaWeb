define([
    'intern!object',
    'intern/chai!assert',
    'rasmusmediaweb/tests/testutils'
], function (registerSuite, assert, testutils) {

    testutils.setup_window();
    var transmission = require('rasmusmediaweb/transmission');
    var ko = require('knockout');

    registerSuite({
        name: 'transmission.ItemList',

        test_update: function () {
            ko_array = ko.observableArray();

            var list = new transmission.ItemList(ko_array);

            list.update({id: function () {
                return 1;
            }});
            assert.strictEqual(ko_array().length, 1);
        },

        test_ensure_same: function () {
            ko_array = ko.observableArray();

            var list = new transmission.ItemList(ko_array);

            list.ensure_same([
                {id: function () {
                    return 1;
                } },
                {id: function () {
                    return 2;
                } }
            ]);
            assert.strictEqual(ko_array().length, 2);

            list.ensure_same([
                {id: function () {
                    return 1;
                }}
            ]);
            assert.strictEqual(ko_array().length, 1);

        }

    });
});
