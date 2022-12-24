odoo.define('portal_attendance_pro.GeofenceCommon', function () {
    "use strict";
    var GeofenceCommon = {
        cssLibs: [
            '/portal_attendance_pro/static/src/lib/ol-6.12.0/ol.css',
            '/portal_attendance_pro/static/src/lib/ol-ext/ol-ext.css',
        ],
        jsLibs: [
            '/portal_attendance_pro/static/src/lib/ol-6.12.0/ol.js',
            '/portal_attendance_pro/static/src/lib/ol-ext/ol-ext.js',
        ],
    };

    return {
        GeofenceCommon: GeofenceCommon,
    };
});