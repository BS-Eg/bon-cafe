odoo.define('hr_attendance_geo_html.my_attendances', function (require) {
    "use strict";

    var core = require('web.core');
    var Attendances = require('hr_attendance.my_attendances');
    var QWeb = core.qweb;
    var _t = core._t;


    var MyAttendances = Attendances.include({
        // parse data setting from server
        parse_data_geo: function () {
            var self = this;

            self.state_read.then(function (data) {
                var data = self.data;
                self.geo_enable = data.geo_enable;
                self.state_save.resolve();
            });
        },

        // get geolocation position
        geolocation: function () {
            var self = this;

            if (navigator.geolocation) {
                //self.geo_access = true;
                navigator.geolocation.getCurrentPosition(geo_success, geo_error, self.geo_options);
            } else {
                self.$("#geo-info").text("Geolocation is not supported by this browser");
                self.geo_access = false;
            }
            function geo_success(position) {
                self.geo_success(position);
            }
            function geo_error(err) {
                self.geo_error(err)
                self.geo_coords = $.Deferred();
            }
        },

        start: function () {
            var self = this;
            this.geo_coords = $.Deferred();
            self.geo_options = {
                //a boolean by default false, requires a position with the highest level 
                // of accuracy possible (which might take more time and more power)
                enableHighAccuracy: true,
                // to set the maximum “age” of the position cached by the browser.
                // We don’t accept one older than the set amount of milliseconds
                maximumAge: 30000,
                // to set the number of milliseconds before the request errors out 
                timeout: 27000
            };
            self.geo_access = false;
            self.parse_data_geo();
            self.geolocation();
            self.state_render.then(function (data) {
                self.$("#geo-icon").on("click", function () {
                    if (self.$("#geo-icon").hasClass('fa-angle-double-down')) {
                        self.$("#geo-icon").removeClass('fa-angle-double-down');
                        self.$("#geo-icon").addClass('fa-angle-double-up');
                    }
                    else {
                        self.$("#geo-icon").removeClass('fa-angle-double-up');
                        self.$("#geo-icon").addClass('fa-angle-double-down');
                    }
                    self.$("#geo-info").fadeToggle();
                    self.$('#mapid').toggle('show');
                    setTimeout(function () { self.mymap.invalidateSize() }, 400);
                });
            });
            /*function geo_ip(ip) {
                //when parent start is end, display map
                parentDef.then(function(value) {
                    // display map with current marker user from https://freegeoip.net/json/
                    self.point = L.GeoIP.getPosition(ip);
                    self.geo_access = true;
                    // set size map
                    var wh = window.innerHeight;
                    $('#mapid').css('height', wh/3);
                    // test on container Leaflet duplicate or already display
                    var container = L.DomUtil.get('mapid');
                    if (container != null){
                        container._leaflet_id = null;
                    }
                    
                    var mymap = new L.map('mapid').setView(self.point, 13);
                    L.GeoIP.centerMapOnPosition(mymap,13);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                    }).addTo(mymap);
                    var marker = L.marker(self.point).addTo(mymap);
                });
            }*/
            return $.when(this._super.apply(this, arguments))
        },

        geo_success: function (position) {
            var self = this;
            // get coords
            self.latitude = position.coords.latitude;
            self.longitude = position.coords.longitude;
            self.geo_coords.resolve();

            // display coords in view
            self.$el.find('#latitude').html(self.latitude);
            self.$el.find('#longitude').html(self.longitude);

            //when parent start is end, display map
            self.state_render.then(function (data) {
                if (self.$('#mapid').length && self.latitude && self.longitude) {
                    var wh = window.innerHeight;
                    self.$('#openDiv').on('click', function (event) {
                        self.$('#mapid').toggle('show');
                        setTimeout(function () { mymap.invalidateSize() }, 400);
                    });
                    self.geo_access = true;
                    self.color_geo_success();
                    // set size map
                    self.$('#mapid').css('height', wh / 3);
                    // test on container Leaflet duplicate or already display
                    var container = L.DomUtil.get('mapid');
                    if (container != null) {
                        container._leaflet_id = null;
                    }
                    // display map with current marker user
                    self.point = new L.LatLng(self.latitude, self.longitude);
                    self.mymap = L.map(self.$('#mapid')[0]).setView(self.point, 13);
                    self.mymap.addControl(new L.Control.Fullscreen());
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                    }).addTo(self.mymap);
                    var marker = L.marker(self.point).addTo(self.mymap);
                }
            });
        },

        color_geo_error: function () {
            // dynamic change color to denied mode geolocation
            var self = this;
            if (self.$("#icon-geo").hasClass('fa-check')) {
                self.$("#icon-geo").removeClass('fa-check');
                self.$("#icon-geo").addClass('fa-times');
            }
            if (self.geo_enable) {
                self.$("#geo-access").addClass("hr-attendance-base-denied");
                self.$('#state-geo').css("border", "2px solid #f27474");
                self.$("#icon-geo").addClass("hr-attendance-base-denied");
            }
        },

        color_geo_success: function () {
            // dynamic change color to success mode geolocation
            var self = this;
            //self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));
            if (self.$("#icon-geo").hasClass('fa-times')) {
                self.$("#icon-geo").removeClass('fa-times');
                self.$("#icon-geo").addClass('fa-check');
            }
            if (self.geo_enable) {
                self.$("#geo-access").removeClass("hr-attendance-base-denied");
                self.$("#geo-access").css("color", "green");
                self.$('#state-geo').css("border", "2px solid green");
                self.$("#icon-geo").removeClass("hr-attendance-base-denied");
                self.$("#icon-geo").css("color", "green");
            }
        },

        geo_error: function (error) {
            var self = this;
            self.color_geo_error();
            self.geo_access = false;
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    self.$("#geo-info").text("User denied the request for Geolocation.HINT: enable and refresh page");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "User denied the request for Geolocation.HINT: enable and refresh page",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.POSITION_UNAVAILABLE:
                    self.$("#geo-info").text("Location information is unavailable.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "Location information is unavailable.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.TIMEOUT:
                    self.$("#geo-info").text("The request to get user location timed out.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "The request to get user location timed out.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.UNKNOWN_ERROR:
                    self.$("#geo-info").text("An unknown error occurred.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "An unknown error occurred.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
            }
        },
    });

});
