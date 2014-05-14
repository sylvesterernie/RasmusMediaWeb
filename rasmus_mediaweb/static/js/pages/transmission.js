define(['jquery', 'knockout', 'rasmusmediaweb/transmissionmanager', 'rasmusmediaweb/hash', 'rasmusmediaweb/utils'], function ($, ko, transmissionmanager, hash, utils) {
    var lib = {};

    lib.torrent_status_map = [
        'status-paused', // stopped
        'status-check-pending progress-striped active', // check pending
        'status-checking progress-striped active', // checking
        'status-download-pending progress-striped active', // download pending
        'status-downloading progress-striped active', // download
        'status-pending progress-striped active', // seed pending
        'status-seeding progress-striped active' // seeding
    ];

    lib.Torrent = function (kwargs, transmissionpage) {
        var self = this;
        self.transmissionpage = transmissionpage;

        self.id = ko.observable(kwargs.id);
        self.name = ko.observable(kwargs.name);
        self.totalSize = ko.observable(kwargs.totalSize);
        self.rateDownload = ko.observable(kwargs.rateDownload);
        self.rateUpload = ko.observable(kwargs.rateUpload);
        self.percentDone = ko.observable(kwargs.percentDone);
        self.status = ko.observable(kwargs.status);
        self.status_text = ko.computed(function () {
            return [
                'Stopped',
                'Check pending',
                'Checking',
                'Download pending',
                'Downloading',
                'Seed pending',
                'Seeding'
            ][self.status()];
        });

        self.size = ko.computed(function () {
            return utils.format_size(self.totalSize());
        });
        self.down_speed = ko.computed(function () {
            return utils.format_size(self.rateDownload());
        });
        self.up_speed = ko.computed(function () {
            return utils.format_size(self.rateUpload());
        });
        self.progress = ko.computed(function () {
            return utils.format_progress(self.percentDone());
        });

        self.progress_classes = ko.computed(function () {
            return 'progress ' + lib.torrent_status_map[self.status()];
        });

        self.progress_bar_classes = ko.computed(function () {
            var s = 'progress-bar ';
            if (self.percentDone() == 1) {
                s = s + ' progress-bar-success';
            }
            return s;
        });

        self.torrent_actions = ko.observableArray([
                                                      new lib.TorrentAction(self, 'Pause', 'pause',
                                                                            function () {
                                                                                self.transmissionpage.tmanager.pause_torrents(self.id())
                                                                                    .done(function () {
                                                                                              self.transmissionpage.refresh();
                                                                                          });
                                                                            },
                                                                            function () {
                                                                                return self.status() > 0;
                                                                            }),

                                                      new lib.TorrentAction(self, 'Play', 'play',
                                                                            function () {
                                                                                self.transmissionpage.tmanager.play_torrents(self.id())
                                                                                    .done(function () {
                                                                                              self.transmissionpage.refresh();
                                                                                          });
                                                                            },
                                                                            function () {
                                                                                return self.status() == 0;
                                                                            }),

                                                      new lib.TorrentAction(self, 'Remove', 'remove',
                                                                            function () {
                                                                                self.transmissionpage.tmanager.remove_torrents(self.id())
                                                                                    .done(function () {
                                                                                              self.transmissionpage.refresh();
                                                                                          });
                                                                            }),

                                                      new lib.TorrentAction(self, 'Remove and trash files', 'remove-circle',
                                                                            function (transmissionpage, torrent) {
                                                                                transmissionpage.confirm_dialog.show('Remove and trash files?', 'This action will delete <strong>' + torrent.name() + '</strong> and all downloaded files, are you sure?', function (dialog) {
                                                                                    transmissionpage.tmanager.remove_torrents(self.id(), true)
                                                                                        .done(function () {
                                                                                                  dialog.close();
                                                                                                  transmissionpage.refresh();
                                                                                              });
                                                                                });
                                                                            })
                                                  ]);
    };

    lib.TorrentAction = function (torrent, title, icon, callback, check) {
        var self = this;
        self.title = title;
        self.torrent = torrent;
        self.classes = ko.computed(function () {
            var s = 'btn btn-xs';
            if (check && !check())
                s += ' hide';
            return s;
        });
        self.icon_classes = ko.observable('glyphicon glyphicon-' + icon);
        self.run = function () {
            callback(torrent.transmissionpage, torrent);
        };
    };

    lib.SortableField = function (sorter, label, sort_field) {
        var self = this;

        self.label = label;
        self.sort_field = sort_field;
        self.active = ko.observable();
        self.classes = ko.observable('');
        self.descending = ko.observable(false);
        self.ascending = ko.observable(false);

        self.activate = function (obj, evt) {
            if (evt)
                evt.preventDefault();
            self.sort();
        };

        self.sort = function (order) {
            sorter.sort_torrents(sort_field, true);

            $.each(sorter.sort_fields(), function (x, field) {
                field.classes('');
            });

            var split = sorter.last_sort_on.split(':');
            if (order == null)
                order = split[1];
            self.classes('active ' + split[1]);
            self.ascending(false);
            self.descending(false);
            if (order == 'asc')
                self.ascending(true);
            else if (order == 'desc')
                self.descending(true);
        };
    };

    lib.Dialog = function (modal) {
        var $modal = $(modal);
        var $confirm_button = $modal.find('.btn.confirm');

        var self = this;

        self.title = ko.observable();
        self.body = ko.observable();

        $modal.on('shown.bs.modal', function (e) {
            $modal.find('.btn-primary').focus();
        });

        self.show = function (title, body, confirm_callback) {
            self.title(title);
            self.body(body);
            $modal.modal();

            $confirm_button.off('click.rasmus');
            if (confirm_callback != null) {
                $confirm_button.on('click.rasmus', function () {
                    confirm_callback(self);
                });
            }

            return self;
        };

        self.close = function () {
            $modal.modal('hide');
        };
    };

    lib.TransmissionPage = function (url) {
        var self = this;

        self.interval_time = 5000;
        self.tmanager = new transmissionmanager.TransmissionManager(url);

        self.inactive = ko.observable(true);
        self.active = ko.computed(function () {
            return !self.inactive();
        });

        self.torrents = ko.observableArray([]);
        self.torrent_list = new lib.ItemList(self.torrents);

        self.sort_fields = ko.observableArray([
                                                  new lib.SortableField(self, 'Name', 'name'),
                                                  new lib.SortableField(self, 'Size', 'totalSize'),
                                                  new lib.SortableField(self, 'Down', 'rateDownload'),
                                                  new lib.SortableField(self, 'Up', 'rateUpload'),
                                                  new lib.SortableField(self, 'Progress', 'percentDone')
                                              ]);

        self._setup = function () {
            self.refresh();
            self.setup_interval(self.interval_time);
            var sort_on = hash.hash_manager.get('sort_on');
            if (!sort_on)
                sort_on = 'name:asc';
            var split = sort_on.split(':');

            $.each(self.sort_fields(), function (x, field) {
                if (field.sort_field == split[0]) {
                    field.sort(split[1]);
                    return true;
                }
            });
            self.sort_torrents(sort_on);
        };

        self.setup = function () {
            // deferred loading of bootstrap because it messes with intern
            //require(['bootstrap']);

            self._setup();
        };

        self.confirm_dialog = new lib.Dialog('#confirm-dialog');


        self.default_focus = function () {
            $('#add_torrent_field').focus();
        };

        self.play_all_torrents = function () {
            self.tmanager.play_all_torrents().done(function () {
                self.refresh();
            });
            self.default_focus();
        };

        self.pause_all_torrents = function () {
            self.tmanager.pause_all_torrents().done(function () {
                self.refresh();
            });
            self.default_focus();
        };

        self.setup_interval = function (time) {
            if (self.interval != null)
                clearInterval(self.interval);
            self.interval_time = time;
            self.interval = setInterval(self.refresh, time);
            console.log('Setting up refresh interval for ' + (time / 1000) + ' seconds');
        };

        self.torrent_uri = ko.observable();
        self.add_torrent_button_classes = ko.observable('btn btn-primary');
        self.add_torrent_button_enabled = ko.observable(true);

        self.add_torrent = function () {
            self.add_torrent_button_enabled(false);
            var req = self.tmanager.add_torrent(self.torrent_uri())
                .done(function (req) {
                          self.add_torrent_button_enabled(true);
                      });
        };

        self.status = {
            down_speed: ko.observable('0'),
            up_speed: ko.observable('0'),
            last_updated: ko.observable('')
        };

        self.sort_torrents = function (sort_on, reverse) {
            var split = sort_on.split(':');
            if (split.length == 1)
                split.push('asc');
            var sort_field = split[0];
            var sort_order = split[1];

            var new_sort_on = sort_field + ':' + sort_order;
            if (reverse && new_sort_on == self.last_sort_on) {
                if (sort_order == 'asc')
                    sort_order = 'desc';
                else
                    sort_order = 'asc';
            }
            self.last_sort_on = sort_field + ':' + sort_order;
            hash.hash_manager.set('sort_on', self.last_sort_on);

            var sort_fields = [self.last_sort_on];
            if (sort_field != 'name')
                sort_fields.push('name:asc');

            self.torrents.sort(function (x, y) {
                var index = 0;

                while (true) {
                    var split = sort_fields[index].split(':');
                    var sort_field = split[0];
                    var sort_order = split[1];

                    var field1 = x[sort_field]();
                    var field2 = y[sort_field]();
                    if (sort_order == 'asc') {
                        field1 = y[sort_field]();
                        field2 = x[sort_field]();
                    }

                    if (field2 > field1)
                        return 1;
                    else if (field1 > field2)
                        return -1
                    else {
                        if (index + 1 >= sort_fields.length)
                            return 0;
                    }
                    index++;
                }
            });
        };

        self.update_torrents = function () {
            return self.tmanager.list_torrents().done(function (res) {
                var new_torrents = [];
                for (var x = 0; x < res.arguments.torrents.length; x++)
                    new_torrents.push(new lib.Torrent(res.arguments.torrents[x], self));
                self.torrent_list.ensure_same(new_torrents);
                if (self.last_sort_on)
                    self.sort_torrents(self.last_sort_on);
            });
        };

        self.refresh = function () {
            var failed = function (res) {
                self.setup_interval(self.interval_time + self.interval_time);
                if (res.status == 0)
                    self.show_info('Error communicating with backend', 'danger');
                else
                    self.show_info('Unknown error while refreshing',
                                   'danger');
            };

            self.update_status().done(function () {
                self.update_torrents().done(function () {
                    self.inactive(false);
                }).fail(failed);
            }).fail(failed);
        };

        self.info = ko.observable();
        self.info_classes = ko.observable('hide');
        self.info_empty = ko.computed(function () {
            if (self.info())
                return false;
            return true;
        });
        self.show_info = function (msg, msg_type) {
            self.info(msg);
            if (msg_type)
                self.info_classes('alert alert-' + msg_type);
            else
                self.info_classes('alert');
        };

        self.update_status = function () {
            var req = self.tmanager.get_status();
            req.done(function (res) {
                self.status.up_speed(utils.format_size(res.arguments.uploadSpeed));
                self.status.down_speed(utils.format_size(res.arguments.downloadSpeed));
                self.status.last_updated(new Date());
            });
            return req;
        };
    };

    lib.ItemList = function (observable_array) {
        var self = this;
        self._items = {};
        self.observable_array = observable_array;

        self.update = function (item) {
            var existing = self._items[item.id()];
            if (existing) {
                var pt = ko.observable().prototype;
                for (var k in item) {
                    var v1 = existing[k];
                    var v2 = item[k];

                    if (v1.name === 'observable')
                        v1(v2());
                }
            } else {
                observable_array.push(item);
                self._items[item.id()] = item;
            }
        };

        self.ensure_same = function (items) {
            var removed = observable_array.remove(function (x) {
                var found = false;
                for (var index = 0; index < items.length; index++) {
                    if (items[index].id() == x.id()) {
                        found = true;
                        break;
                    }
                }
                return !found;
            });
            $.each(items, function (x, item) {
                self.update(item);
            });
        };

        self.clear = function () {
            self._items = {};
            observable_array.removeAll();
        };
    };

    lib.init = function () {
        var tmanager = new lib.TransmissionPage(globs.urls.transmission_api);
        tmanager.setup();
        ko.applyBindings(tmanager);

    };

    return lib;
});
