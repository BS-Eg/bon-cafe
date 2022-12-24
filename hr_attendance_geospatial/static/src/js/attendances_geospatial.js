odoo.define('hr_attendance_geospatial.geospatial_attendances', function(require) {
    "use strict";

    var core = require('web.core');
    //var Attendances = require('hr_attendance_base.base_attendances');
    var Attendances = require('hr_attendance.my_attendances');
    var QWeb = core.qweb;
    var _t = core._t;


    var MyAttendances = Attendances.include({
        // parse data setting from server
        parse_data_geospatial: function () {
            var self = this;

            self.state_read.then(function(data) {
                var data = self.data;
                self.geospatial = data.geospatial;
                self.geospatial_access = data.geospatial_access;
                self.geospatial_enable = data.geospatial_enable;

                if (data.geospatial_access) {
                    self.geospatial_description = data.geospatial_description;
                    self.geospatial_name = data.geospatial_name;
                    self.geospatial_id = data.geospatial_id;
                }
                self.state_save.resolve();
            });
        },

        start: function() {
            var self = this;
            self.parse_data_geospatial();

            self.state_render.then(function(data) {
/*                self.$( "#ip-icon" ).on( "click", function() {
                    if (self.$( "#ip-icon" ).hasClass('fa-angle-double-down')){
                        self.$( "#ip-icon" ).removeClass('fa-angle-double-down');
                        self.$( "#ip-icon" ).addClass('fa-angle-double-up');
                    }
                    else{
                        self.$( "#ip-icon" ).removeClass('fa-angle-double-up');
                        self.$( "#ip-icon" ).addClass('fa-angle-double-down');
                    }
                    self.$( "#ip-info" ).fadeToggle();
                });*/
            });
            return $.when(this._super.apply(this, arguments));
        },

    });

});