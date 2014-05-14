define([], function ($, ko) {
    "use strict";

    return {
        format_size: function (size_in_b) {
            var i = -1;
            var byte_units = ['kB', 'MB', 'GB', 'TB', 'PB'];
            do {
                size_in_b = size_in_b / 1024;
                i++;
            } while (size_in_b > 1024);
            return (Math.round(size_in_b * 10) / 10).toFixed(1) + byte_units[i];
        },

        format_progress: function (progress) {
            return (Math.round(progress * 1000) / 10).toFixed(1);
        },

        Action: function (kwargs) {
            var self = this;

            self.icon = ko.observable(kwargs.icon);
            self.title = ko.observable(kwargs.title);
            self.callback = kwargs.callback;
            self.href = kwargs.href;
        }
    };
});
