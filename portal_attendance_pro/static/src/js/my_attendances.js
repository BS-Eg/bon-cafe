odoo.define('portal_attendance_pro.my_attendances', function (require) {
    "use strict";

    var MyAttendances = require('hr_attendance.my_attendances');
    var session = require("web.session");
    var Dialog = require('web.Dialog');

    var core = require('web.core');
    var _t = core._t;

    var MyAttendances = MyAttendances.include({
        cssLibs: [
            '/portal_attendance_pro/static/src/lib/ol-6.12.0/ol.css',
            '/portal_attendance_pro/static/src/lib/ol-ext/ol-ext.css',
        ],
        jsLibs: [
            '/portal_attendance_pro/static/src/lib/ol-6.12.0/ol.js',
            '/portal_attendance_pro/static/src/lib/ol-ext/ol-ext.js',
        ],
        events: _.extend({}, MyAttendances.prototype.events, {
            'click .b_gmap_kisok_toggle': '_toggle_gmap',
            'click .b_glocation_kisok_toggle': '_toggle_glocation',
        }),
        willStart: function () {
            var self = this;
            var superDef = this._super.apply(this, arguments);                   
            return Promise.all([superDef]);
        },
        start: function () {
            var self = this;
            this.olmap = null;
            this.ip = null;            
            return this._super.apply(this, arguments).then(function () {
                if (window.location.protocol == 'https:') {
                    self.$('.fa-sign-in').css('pointer-events','none');
                    self.$('.fa-sign-out').css('pointer-events','none');
                    
                    self.def_geofence = $.Deferred();
                    if (session.portal_attendance_geofence) {
                        self._initMap();
                    } else {
                        self.$('.b_gmap_kisok_container').css('display','none');
                        self.def_geofence.resolve();
                    }

                    self.def_geolocation = $.Deferred();
                    if (session.portal_attendance_geolocation) {
                        self._getGeolocation();
                    }else{
                        self.$('.b_glocation_kisok_container').css('display','none');
                        self.def_geolocation.resolve();
                    }

                    $.when(self.def_geofence, self.def_geolocation).then(function(){
                        self.$('.fa-sign-in').css('pointer-events','');
                        self.$('.fa-sign-out').css('pointer-events','');
                    })
                }

            });
        },
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            if (this.olmap) {
                this.olmap.updateSize();
            }
        },
        _toggle_gmap: function () {
            var self = this;
            if (self.$(".b_gmap_kisok_toggle").hasClass('fa-angle-double-down')) {
                self.$('.b_gmap_kisok_view').toggle('show');
                self.$("i.b_gmap_kisok_toggle", self).toggleClass("fa-angle-double-down fa-angle-double-up");
                self.$(".o_hr_attendance_kiosk_backdrop")[0].setAttribute('style', 'height: calc(100vh + 197px);');
                setTimeout(function () {
                    self.olmap.updateSize()
                }, 400);
            } else {
                self.$('.b_gmap_kisok_view').toggle('hide');
                self.$("i.b_gmap_kisok_toggle", self).toggleClass("fa-angle-double-up fa-angle-double-down");
                self.$(".o_hr_attendance_kiosk_backdrop")[0].setAttribute('style', 'height: calc(100vh);');
                setTimeout(function () {
                    self.olmap.updateSize()
                }, 400);
            }
        },
        _toggle_glocation: function () {
            var self = this;
            if (self.$(".b_glocation_kisok_toggle").hasClass('fa-angle-double-down')) {
                self.$('.b_glocation_kisok_view').toggle('show');
                self.$("i.b_glocation_kisok_toggle", self).toggleClass("fa-angle-double-down fa-angle-double-up");
                if (self.latitude && self.longitude){
                    self.$('.b_glocation_kisok_view span')[0].innerText =  "Lattitude:" + self.latitude + ", Longitude:" + self.longitude ;
                }
            } else {
                self.$('.b_glocation_kisok_view').toggle('hide');
                self.$("i.b_glocation_kisok_toggle", self).toggleClass("fa-angle-double-up fa-angle-double-down");                
            }
        },
        _initMap: function () {
            var self = this;
            if (window.location.protocol == 'https:') {
                var options = {
                    enableHighAccuracy: true,
                    maximumAge: 30000,
                    timeout: 27000
                };
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(successCallback, errorCallback, options);
                } else {
                    self.geolocation = false;
                }

                function successCallback(position) {
                    self.latitude = position.coords.latitude;
                    self.longitude = position.coords.longitude;
                    if (!self.olmap) {
                        var olmap_div = self.$('.b_gmap_kisok_view').get(0);
                        $(olmap_div).css({
                            width: '425px !important',
                            height: '200px !important'
                        });
                        var vectorSource = new ol.source.Vector({});
                        self.olmap = new ol.Map({
                            layers: [
                                new ol.layer.Tile({
                                    source: new ol.source.OSM(),
                                }),
                                new ol.layer.Vector({
                                    source: vectorSource
                                })
                            ],

                            loadTilesWhileInteracting: true,
                            target: olmap_div,
                            view: new ol.View({
                                center: [self.latitude, self.longitude],
                                zoom: 2,
                            }),
                        });
                        const coords = [position.coords.longitude, position.coords.latitude];
                        const accuracy = ol.geom.Polygon.circular(coords, position.coords.accuracy);
                        vectorSource.clear(true);
                        vectorSource.addFeatures([
                            new ol.Feature(accuracy.transform('EPSG:4326', self.olmap.getView().getProjection())),
                            new ol.Feature(new ol.geom.Point(ol.proj.fromLonLat(coords)))
                        ]);
                        self.olmap.getView().fit(vectorSource.getExtent(), { duration: 100, maxZoom: 6 });
                        self.olmap.updateSize();
                    }
                    self.$('.b_gmap_kisok_container').css('display', '');
                    self.def_geofence.resolve();
                }

                function errorCallback(err) {                    
                    switch (err.code) {
                        case err.PERMISSION_DENIED:
                            console.log("The request for geolocation was refused by the user.");
                            break;
                        case err.POSITION_UNAVAILABLE:
                            console.log("There is no information about the location available.");
                            break;
                        case err.TIMEOUT:
                            console.log("The request for the user's location was unsuccessful.");
                            break;
                        case err.UNKNOWN_ERROR:
                            console.log("An unidentified error has occurred.");
                            break;
                    }
                    self.def_geofence.resolve();
                }
            }
            else {
                self.$('.b_gmap_kisok_container').addClass('d-none');
                self.do_notify(false, _t("GEOLOCATION API MAY ONLY WORKS WITH HTTPS CONNECTIONS."));
            }
        },
        _getGeolocation: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                maximumAge: 30000,
                timeout: 27000
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(successCallback, errorCallback, options);
            } else {
                self.geolocation = false;
                self.def_geolocation.resolve();
            }

            function successCallback(position) {
                self.latitude = position.coords.latitude;
                self.longitude = position.coords.longitude;
                self.$('.b_glocation_kisok_container').css('display','');
                self.def_geolocation.resolve();
            }

            function errorCallback(err) {
                switch (err.code) {
                    case err.PERMISSION_DENIED:
                        console.log("The request for geolocation was refused by the user.");
                        break;
                    case err.POSITION_UNAVAILABLE:
                        console.log("There is no information about the location available.");
                        break;
                    case err.TIMEOUT:
                        console.log("The request for the user's location was unsuccessful.");
                        break;
                    case err.UNKNOWN_ERROR:
                        console.log("An unidentified error has occurred.");
                        break;
                }
                self.def_geolocation.reject();
            }            
        },
        update_attendance: function () {
            var self = this;
            if (window.location.protocol == 'https:') {
                self._validate_attendances();
            }else {
                this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                })
                .then(function(result) {
                    if (result.action) {
                        var action = result.action;
                        self.do_action(action); 
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
            }
        },
        _validate_attendances: function(){
            var self = this;

            self.data_ip_address = null;
            self.data_latitude = null;
            self.data_longitude = null;
            self.data_is_inside = false;
            self.data_geofence_ids = null;          
            self.data_photo = false;          

            self.def_geolocation_data = new $.Deferred();
            if (session.portal_attendance_geolocation) {                
                if (window.location.protocol == 'https:') {
                self._validate_Geolocation();
            }else{
                self.def_geolocation_data.resolve();
            }
            }else{
                self.def_geolocation_data.resolve();
            }

            self.def_geofence_data = new $.Deferred();
            if (session.portal_attendance_geofence) {                
                if (window.location.protocol == 'https:') {
                self._validate_Geofence();
            }else{
                self.def_geofence_data.resolve();
            }
            }else{
                self.def_geofence_data.resolve();
            }
            
            self.def_photo_data = new $.Deferred();
            if (session.portal_attendance_photo) {                
                if (window.location.protocol == 'https:') {
                self._validate_Photo();
            }else{
                self.def_photo_data.resolve();
            }
            }else{
                self.def_photo_data.resolve();
            }

            $.when(self.def_geolocation_data, self.def_geofence_data, self.def_photo_data).then(function(){
                self._manual_attendance(self.data_ip_address, self.data_latitude, self.data_longitude, self.data_is_inside, self.data_geofence_ids, self.data_photo);
            })
        },
        _validate_Photo: function () {
            var self = this;
            this.dialogPhoto = new Dialog(this, {
                size: 'medium',
                title: _t("Capture Snapshot"),
                $content: `
                <div class="container-fluid">
                    <div class="col-12 controls">
                        <fieldset class="reader-config-group">
                            <div class="row">
                                <div class="col-3">
                                    <label>
                                        <span>Select Camera</span>
                                    </label>
                                </div>
                                <div class="col-6">
                                    <select name="video_source" class="videoSource" id="videoSource">                                       
                                    </select>
                                </div>
                                <div class="col-3">
                                </div>
                            </div>
                        </fieldset>
                    </div>
                    <div class="row">                                
                        <div class="col-12" id="videoContainer">
                            <video autoplay muted playsinline id="video" style="width: 100%; max-height: 100%; box-sizing: border-box;" autoplay="1"/>
                            <canvas id="image" style="display: none;"/>
                        </div>
                    </div>
                </div>`,
                buttons: [
                    {
                        text: _t("Capture Snapshot"), classes: 'btn-primary captureSnapshot',
                    },
                    {
                        text: _t("Close"), classes: 'btn-secondary captureClose', close: true,
                    }
                ]
            }).open();

            this.dialogPhoto.opened().then(async function () {
                var videoElement = self.dialogPhoto.$('#video').get(0);
                var videoSelect = self.dialogPhoto.$('select#videoSource').get(0);
                videoSelect.onchange = getStream;

                getStream().then(getDevices).then(gotDevices);

                function getStream() {
                    if (window.stream) {
                        window.stream.getTracks().forEach(track => {
                            track.stop();
                        });
                    }
                    const videoSource = videoSelect.value;
                    const constraints = {
                        video: { deviceId: videoSource ? { exact: videoSource } : undefined }
                    };
                    return navigator.mediaDevices.getUserMedia(constraints).then(gotStream).catch(handleError);
                }

                function getDevices() {
                    return navigator.mediaDevices.enumerateDevices();
                }

                function gotDevices(deviceInfos) {
                    window.deviceInfos = deviceInfos;
                    for (const deviceInfo of deviceInfos) {
                        const option = document.createElement('option');
                        option.value = deviceInfo.deviceId;
                        if (deviceInfo.kind === 'videoinput') {
                            option.text = deviceInfo.label || "Camera" + (videoSelect.length + 1) + "";
                            videoSelect.appendChild(option);
                        }
                    }
                }

                function gotStream(stream) {
                    window.stream = stream;
                    videoSelect.selectedIndex = [...videoSelect.options].
                        findIndex(option => option.text === stream.getVideoTracks()[0].label);
                    videoElement.srcObject = stream;
                }

                function handleError(error) {
                    console.error('Error: ', error);
                }

                var $captureSnapshot = self.dialogPhoto.$footer.find('.captureSnapshot');
                var $closeBtn = self.dialogPhoto.$footer.find('.captureClose');

                $captureSnapshot.on('click', function (event) {
                    var img64 = "";
                    var image = self.dialogPhoto.$('#image').get(0);
                    image.width = $(video).width();
                    image.height = $(video).height();
                    image.getContext('2d').drawImage(video, 0, 0, image.width, image.height);
                    var img64 = image.toDataURL("image/jpeg");
                    img64 = img64.replace(/^data:image\/(png|jpg|jpeg|webp);base64,/, "");
                    if (img64) {
                        self.data_photo = img64;
                        self.def_photo_data.resolve();
                        $closeBtn.click();
                    }else{
                        self.def_photo_data.reject();
                    }
                    $captureSnapshot.text("uploading....").addClass('disabled');
                });

            });
        },
        _validate_Geolocation: function(){
            var self = this;
            if (self.latitude && self.longitude){
                self.data_latitude = self.latitude || null;
                self.data_longitude = self.longitude || null;
                self.def_geolocation_data.resolve();
            }else{
                self.def_geolocation_data.reject();
            }     
        },
        _validate_Geofence: async function(){
            var self = this;
            var insidePolygon = false;
            var insideGeofences = []              
            
            await self._rpc({
                model: 'hr.attendance.geofence',
                method: 'search_read',
                args: [[['company_id', '=', self.getSession().company_id], ['employee_ids', 'in', self.employee.id]], ['id', 'name', 'overlay_paths']],
            }).then(function (res) {                    
                self.geofence_data = res.length && res;                
                if (!res.length) {
                    self.def_geofence_data.reject();
                }
                
                var options = {
                    enableHighAccuracy: true,
                    maximumAge: 30000,
                    timeout: 27000
                };
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(successCallback, errorCallback, options);
                }
                    
                function successCallback(position) {
                    self.latitude = position.coords.latitude;
                    self.longitude = position.coords.longitude;
                    if (self.olmap) {
                        for (let i = 0; i < self.geofence_data.length; i++) {
                            var path = self.geofence_data[i].overlay_paths;
                            var value = JSON.parse(path);                                
                            if (Object.keys(value).length > 0) {
                                let coords = ol.proj.fromLonLat([self.longitude, self.latitude]);
                                var features = new ol.format.GeoJSON().readFeatures(value);
                                var geometry = features[0].getGeometry();
                                insidePolygon = geometry.intersectsCoordinate(coords);
                                if (insidePolygon === true) {
                                    insideGeofences.push(self.geofence_data[i].id);
                                }
                            }
                        }
                        
                        if (insideGeofences.length > 0) {
                            self.data_is_inside = true;
                            self.data_geofence_ids = insideGeofences;
                            self.def_geofence_data.resolve();
                        } else {
                            Swal.fire({
                                title: 'Access Denied',
                                text: "You haven't entered any of the geofence zones.",
                                icon: 'error',
                                confirmButtonColor: '#3085d6',
                                confirmButtonText: 'Ok'
                            }).then(function(){
                                if(self.dialogPhoto && self.dialogPhoto != undefined){
                                    var $closeBtn = self.dialogPhoto.$footer.find('.captureClose');
                                    $closeBtn.click();
                                }
                            });
                            self.def_geofence_data.reject();
                        }
                    }
                }
                function errorCallback(err) {
                    console.log(err);
                }
            })
        },
        
        _manual_attendance: function (data_latitude, data_longitude, data_geofence_ids, data_photo) {
            var self = this;
            var data_latitude = self.data_latitude || null;
            var data_longitude = self.data_longitude || null;
            var data_geofence_ids = self.data_geofence_ids || null;
            var data_photo = self.data_photo || null;

            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances', null, [data_latitude, data_longitude], data_geofence_ids, [data_photo]],
            }).then(function (result) {
                if (result.action) {
                    var action = result.action;
                    self.do_action(action); 
                    if (window.stream) {
                        window.stream.getTracks().forEach(track => {
                            track.stop();
                        });
                    }
                } else if (result.warning) {
                    self.do_warn(result.warning);
                    if (window.stream) {
                        window.stream.getTracks().forEach(track => {
                            track.stop();
                        });
                    }
                }
            });
        },
    });
});
