define(['jquery'], function ($) {
    var lib = {};

    lib.TransmissionManager = function (url) {
        var self = this;

        self._ajax = $.ajax;
        self._Deferred = $.Deferred;

        self._exec = function (method, args, deferred, count) {
            var payload = {
                'method': method
            };
            if (args)
                payload.arguments = args;

            if (deferred == null)
                deferred = $.Deferred();

            if (count == null)
                count = 0;

            var req = self._ajax({
                                     url: url,
                                     type: 'POST',
                                     contentType: 'application/json',
                                     data: JSON.stringify(payload),
                                     headers: {
                                         'X-Transmission-Session-Id': self.session_id
                                     }
                                 }).fail(function (res) {
                if (res.status == 409) {
                    if (count >= 10)
                        deferred.reject();
                    else {
                        self.session_id = res.getResponseHeader('X-Transmission-Session-Id');
                        self._exec(method, args, deferred, count + 1);
                    }
                } else {
                    console.warn(res);
                    deferred.reject(res);
                }
            }).done(function (res) {
                deferred.resolve(res);
            });
            return deferred;
        };

        self.add_torrent = function (uri) {
            return self._exec('torrent-add', {
                filename: uri
            });
        };

        self.list_torrents = function () {
            return self._exec('torrent-get', {
                fields: [
                    'id',
                    'name',
                    'totalSize',
                    'rateDownload',
                    'rateUpload',
                    'percentDone',
                    'status'
                ]
            });
        };

        self.get_status = function () {
            return self._exec('session-stats');
        };

        self.pause_torrents = function (ids) {
            if (typeof(ids) != typeof([]))
                ids = [ids];
            return self._exec('torrent-stop', {'ids': ids});
        };

        self.play_torrents = function (ids) {
            if (typeof(ids) != typeof([]))
                ids = [ids];
            return self._exec('torrent-start', {'ids': ids});
        };

        self._all_ids = function () {
            var deferred = $.Deferred();
            self.list_torrents().done(function (res) {
                var ids = [];
                for (var x = 0; x < res.arguments.torrents.length; x++)
                    ids.push(res.arguments.torrents[x].id);
                deferred.resolve(ids);
            }).fail(function (res) {
                deferred.reject(res);
            });
            return deferred;
        };

        self.pause_all_torrents = function () {
            var deferred = $.Deferred();
            self._all_ids().done(function (ids) {
                self.pause_torrents(ids).done(function (res) {
                    deferred.resolve(res);
                });
            });
            return deferred;
        };

        self.play_all_torrents = function () {
            var deferred = $.Deferred();
            self._all_ids().done(function (ids) {
                self.play_torrents(ids).done(function (res) {
                    deferred.resolve(res);
                });
            });
            return deferred;
        };

        self.remove_torrents = function (ids, delete_local_data) {
            if (typeof(ids) != typeof([]))
                ids = [ids];
            delete_local_data = Boolean(delete_local_data);

            return self._exec('torrent-remove', {ids: ids, 'delete-local-data': delete_local_data});
        };
    };

    return lib;
});
