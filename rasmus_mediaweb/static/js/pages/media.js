define(['jquery', 'knockout', 'rasmusmediaweb/hash', 'rasmusmediaweb/utils', 'jqtree'], function ($, ko, hash, utils) {
    var lib = {
        init: function () {
            var page = new lib.MediaPage();
            page.setup();
            ko.applyBindings(page);
        }
    };

    lib.item_cmp = function (x, y) {
        var real1 = x.name.toLowerCase();
        var real2 = y.name.toLowerCase();

        if (real1 > real2)
            return 1;
        if (real2 > real1)
            return -1;
        return 0;
    };

    lib.MediaPage = function () {
        var self = this;

        self.hash_manager = new hash.HashManager();

        self.media_items = ko.observableArray();
        self.folder_path = ko.observable('');

        self.setup = function () {
            var $tree = self._setup_tree();

            var params = self.hash_manager.all();
            var keys = [];
            for (var key in params) {
                keys.push(key);
            }

            keys.sort();

            // reversing so pop()'ing items gives them back in the correct order
            keys.reverse();

            var open = function (deferred) {
                if (deferred == null)
                    deferred = $.Deferred();

                if (keys.length == 0)
                    return deferred.resolve();

                var key = keys.pop();
                var value = params[key];

                var d = {};
                d[key] = value;
                //console.log(d);

                if (value === '0')
                    return open(deferred);

                if (key.indexOf('/') != 0)
                    return open(deferred);

                var node = $tree.tree('getNodeById', key);
                $tree.tree('openNode', node).then(function () {
                    return open(deferred);
                });

                return deferred;
            };

            open().then(function () {
                var selected = self.hash_manager.get('selected');
                if (selected != null)
                    $tree.tree('selectNode', $tree.tree('getNodeById', selected));
            });
        };

        self._setup_tree = function () {
            var $tree = $('#folder-tree').tree({
                                                   dragAndDrop: false,
                                                   useContextMenu: false,
                                                   data: [
                                                       {
                                                           label: 'Media',
                                                           load_on_demand: true,
                                                           href: globs.urls.api + 'media/',
                                                           path: '/',
                                                           id: '/'
                                                       }
                                                   ],
                                                   dataFilter: function (data) {
                                                       var items = [];
                                                       for (var x = 0; x < data.items.length; x++) {
                                                           var item = data.items[x];
                                                           if (item.type == 'folder') {
                                                               item.load_on_demand = true;
                                                               item.url = item.href;
                                                               item.id = item.path;
                                                               items.push(item);
                                                           }
                                                       }

                                                       items.sort(lib.item_cmp);
                                                       return items;
                                                   }
                                               });

            $tree.bind('tree.select', function (event) {
                var node = event.node;
                var all = self.hash_manager.all();
                self.hash_manager.set('selected', node.path);
                $.ajax({
                           url: node.href,
                           contentType: 'application/json'
                       }).done(function (res) {
                    self.update_media_items(node, res.items);
                });
            });

            $tree.bind('tree.open', function (event) {
                var node = event.node;
                self.hash_manager.set(node.path, '1');
            });

            $tree.bind('tree.close', function (event) {
                var node = event.node;
                self.hash_manager.set(node.path, '0');
            });

            return $tree;
        };

        self.update_media_items = function (node, source_items) {
            self.folder_path(node.path);
            var items = [];
            for (var x = 0; x < source_items.length; x++) {
                if (source_items[x].type == 'folder')
                    continue;
                var item = source_items[x];
                item.formatted_size = utils.format_size(item.size);
                item.actions = [
                    new utils.Action({icon: 'download', title: 'Download', href: item.download_url}),
                    new utils.Action({icon: 'play', title: 'Play', href: item.stream_url})
                ];
                items.push(item);
                if (item.type == 'folder')
                    item.icon = 'folder-close';
                else if (item.type == 'video' || item.type.indexOf('video/') == 0)
                    item.icon = 'facetime-video';
            }
            items.sort(lib.item_cmp);
            self.media_items(items);

        };
    };

    return lib;
});
