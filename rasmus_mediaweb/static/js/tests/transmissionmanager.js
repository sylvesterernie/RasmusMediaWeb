define([
    'intern!object',
    'intern/chai!assert'
], function (registerSuite, assert, testutils) {

    var transmissionmanager = require('rasmusmediaweb/transmissionmanager');

    var calls = [];
    var manager = new transmissionmanager.TransmissionManager('http://nohost.noplace');

    var Deferred = function () {
        var self = this;
        self.fails = [];
        self.dones = [];

        self.fail = function (callback) {
            self.fails.push(callback);
            return self;
        };
        self.done = function (callback) {
            self.dones.push(callback);
            return self;
        };

        self.reject = function (obj) {
            for (var x = 0; x < self.fails; x++) {
                self.fails[x](obj);
            }
        };

        return self;
    };

    manager._ajax = function (kwargs) {
        calls.push(kwargs);
        return new Deferred();
    };

    manager._Deferred = Deferred();

    var clear_calls = function () {
        while (calls.length > 0)
            calls.pop();
    };

    registerSuite({
        name: 'transmissionmanager.TransmissionManager',

        test_exec: function () {
            var res = manager._exec('test-foo');
            assert.strictEqual(JSON.parse(calls[0].data).method, 'test-foo');
            assert.ok(res.done);

            res.reject({status: 409});
            //assert.strictEqual(calls.length, 2);

            clear_calls();
        },

        test_add_torrent: function () {
            var res = manager.add_torrent('some-uri');
            var parsed = JSON.parse(calls[0].data);
            assert.strictEqual(parsed.method, 'torrent-add');
            assert.deepEqual(parsed.arguments, {filename: 'some-uri'});
            assert.ok(res.done);
            clear_calls();
        },

        test_list_torrents: function () {
            var res = manager.list_torrents()
            assert.strictEqual(JSON.parse(calls[0].data).method, 'torrent-get');
            assert.ok(res.done);
            clear_calls();
        },

        test_get_status: function () {
            var res = manager.get_status();
            assert.strictEqual(JSON.parse(calls[0].data).method, 'session-stats');
            assert.ok(res.done);
            clear_calls();
        },

        test_pause_torrents: function () {
            var res = manager.pause_torrents(1);
            assert.strictEqual(JSON.parse(calls[0].data).method, 'torrent-stop');
            assert.ok(res.done);
            clear_calls();
        },

        test_play_torrents: function () {
            var res = manager.play_torrents(1);
            assert.strictEqual(JSON.parse(calls[0].data).method, 'torrent-start');
            assert.ok(res.done);
            clear_calls();
        },

        test_remove_torrents: function () {
            var res = manager.remove_torrents(1, false);
            var parsed = JSON.parse(calls[0].data);
            assert.strictEqual(parsed.method, 'torrent-remove');
            assert.deepEqual(parsed.arguments, {ids: [1], 'delete-local-data': false});
            assert.ok(res.done);
            clear_calls();
        },

        test_remove_torrents_and_delete: function () {
            var res = manager.remove_torrents(1, true);
            var parsed = JSON.parse(calls[0].data);
            assert.strictEqual(parsed.method, 'torrent-remove');
            assert.deepEqual(parsed.arguments, {ids: [1], 'delete-local-data': true});
            assert.ok(res.done);
            clear_calls();
        }

    });
});
