define(['jquery', 'knockout'], function ($, ko) {
    "use strict";

    var lib = {
        init: function () {
            var find_media_page = new lib.FindMediaPage(globs.urls.api + 'media-search/');
            find_media_page.setup();
            ko.applyBindings(find_media_page);
        }
    };

    lib.FindMediaPage = function (url) {
        var self = this;

        self.perform_search_enabled = ko.observable(true);
        self.search_type = ko.observable('movies');
        self.search_text = ko.observable('');

        self.matches = ko.observableArray();

        self.setup = function () {
        };

        self.perform_search = function (evt) {
            var payload = {
                s: self.search_text(),
                t: self.search_type()
            };

            $.ajax({
                url: url,
                contentType: 'application/json',
                data: $.param(payload)
            }).done(function (res) {
                self.matches.removeAll();
                for (var x = 0; x < res.length; x++) {
                    self.matches.push(res[x]);
                }
            });
        };
    };


    return lib;
});
