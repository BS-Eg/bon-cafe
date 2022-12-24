odoo.define('portal_attendance_pro.GeofenceDrawing', function (require) {
    'use strict';


    var AbstractField = require('web.AbstractField');
    var GeofenceCommon = require('portal_attendance_pro.GeofenceCommon');
    var registry = require('web.field_registry');

    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    var GeofenceDrawing = AbstractField.extend(GeofenceCommon.GeofenceCommon, {
        template: 'GeofenceDrawingView',
        class: 'ol_map_widget',
        supportedFieldTypes: ['text'],
        tagName: 'div',
        xmlDependencies: ['/portal_attendance_pro/static/src/xml/geofence_template.xml'],

        init: function () {
            var _super = this._super.apply(this, arguments);
            this.olmap = null;
            this.isDrawingEnabled = false;
            return _super;
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            if (!this.value) {
                this.value = 'Empty';
            }
            this._init_olmap();
            return def
        },

        _init_olmap: function () {
            var self = this;
            var olmap_div = this.$(".olmap_widget").get(0);
            $(olmap_div).css({
                width: '100%',
                height: '100%'
            });
            var map = this._load_olmap();
            if (this.olmap) {
                map.setTarget(olmap_div);
                this._ol_add_layer_vector();
                if (self.mode === 'edit' && !this.get('effective_readonly')) {
                    self._ol_drawing_polygon_addcontrol();
                    self._ol_clear_polygon_addcontrol();
                }
            }
        },

        _load_olmap: function (lat, lon) {
            if (!lat) {
                lat = 0;
            }
            if (!lon) {
                lon = 0;
            }
            if (!this.olmap) {
                this.olmap = new ol.Map({
                    layers: [
                        new ol.layer.Tile({
                            source: new ol.source.OSM(),
                        })],
                    view: new ol.View({
                        center: ol.proj.fromLonLat([lat, lon]),
                        zoom: 0,
                    }),

                });
                this.olmap.updateSize();
            }
            return this.olmap;
        },

        _ol_drawing_polygon_addcontrol: function () {
            var buttonElement = document.createElement('button');
            buttonElement.innerHTML = '<i class="fa fa-pencil" style="cursor: pointer !important;"></i>';
            buttonElement.id = 'ol-draw';
            buttonElement.addEventListener('click', this._ol_drawing_polygon.bind(this));

            var divElement = document.createElement('div');
            divElement.className = 'ol-draw ol-unselectable ol-control';
            divElement.appendChild(buttonElement);

            this._OnStartPolygonDrawControl = new ol.control.Control({
                element: divElement
            });
            this.olmap.addControl(this._OnStartPolygonDrawControl);
        },

        _ol_clear_polygon_addcontrol: function () {
            var buttonElement = document.createElement('button');
            buttonElement.innerHTML = '<i class="fa fa-trash" style="cursor: pointer !important;"></i>';
            buttonElement.id = 'ol-clear';
            buttonElement.addEventListener('click', this._ol_clear_polygon.bind(this));

            var divElement = document.createElement('div');
            divElement.className = 'ol-clear ol-unselectable ol-control';
            divElement.appendChild(buttonElement);

            this._OnDeletePolygonDrawControl = new ol.control.Control({
                element: divElement
            });
            this.olmap.addControl(this._OnDeletePolygonDrawControl);
        },

        _ol_drawing_polygon: function (e) {
            if (this.isDrawingEnabled) {
                console.log("you can't edit or draw features");
                return null;
            }
            var self = this;
            this.olmap.removeInteraction(this.draw);
            this.isDrawingEnabled = !this.isDrawingEnabled;
            var geometryFunction = null;
            if (this.isDrawingEnabled) {
                this.$("#btn-olmap-edit").html("<i class='fa fa-play'></i>");
                this.isDrawingEnabled = false;

                this.draw = new ol.interaction.Draw({
                    source: self.vectorSource,
                    type: 'Polygon',
                    geometryFunction: geometryFunction,
                    name: 'draw',
                });

                this.olmap.addInteraction(this.draw);
                this.draw.on('drawend', this._ol_polygon_draw_end.bind(this));
                this.draw.on('drawstart', function (e) {
                    self.vectorSource.clear();
                });

                this.modify = new ol.interaction.Modify({
                    source: this.vectorSource,
                    name: 'modify',
                });
                this.olmap.addInteraction(this.modify);
                this.modify.on('modifyend', this._ol_polygon_draw_end.bind(this));

                this.snap = new ol.interaction.Snap({
                    source: this.vectorSource,
                    name: 'snap',
                });
                this.olmap.addInteraction(this.snap);
            } else {
                this.$("#btn-olmap-edit").html("<i class='fa fa-pencil'></i>");
                ol.Observable.unByKey(this.key);
            }
        },

        _ol_clear_polygon: function () {
            var self = this;
            this.isDrawingEnabled = false;
            if (this.draw) {
                this.olmap.removeInteraction(this.draw);
            }
            if (this.snap) {
                this.olmap.removeInteraction(this.snap);
            }
            if (this.modify) {
                this.olmap.removeInteraction(this.modify);
            }
            self.vectorSource.clear();
            self._ol_field_changed();
        },

        _ol_field_changed: function () {
            var changes = {};
            var getFeatures = this.vectorSource.getFeatures();
            var _newValue = new ol.format.GeoJSON().writeFeatures(getFeatures);
            changes[this.attrs.name] = _newValue;
            this.trigger_up("field_changed", {
                dataPointID: this.dataPointID,
                changes: changes,
                viewType: this.viewType
            });
            this.value = _newValue;
        },

        _ol_add_layer_vector: function () {
            if (!this.vectorSource) {
                this.vectorSource = new ol.source.Vector();
            }
            if (!this.vectorLayer) {
                this.vectorLayer = new ol.layer.Vector({
                    source: this.vectorSource,
                    name: 'vectorSource',
                    style: new ol.style.Style({
                        fill: new ol.style.Fill({
                            color: 'rgb(255 235 59 / 62%)',
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#ffc107',
                            width: 2,
                        }),
                        image: new ol.style.Circle({
                            radius: 7,
                            fill: new ol.style.Fill({
                                color: '#ffc107',
                            }),
                        }),
                    }),
                });
                this.olmap.addLayer(this.vectorLayer);
            }
            if (this.value && this.value != 'Empty') {                
                var readFeatures = new ol.format.GeoJSON().readFeatures(this.value);
                this.vectorSource.addFeatures(readFeatures);
                _.each(this.vectorSource.getFeatures(), function (feature) {
                    feature.setStyle(
                        new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgb(255 235 59 / 62%)',
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#ffc107',
                                width: 2,
                            }),
                            image: new ol.style.Circle({
                                radius: 7,
                                fill: new ol.style.Fill({
                                    color: '#ffc107',
                                }),
                            }),
                        })
                    );
                });
            }
        },

        _ol_polygon_draw_end: function (e) {
            var self = this;
            if (!this.isDrawingEnabled){
                this.isDrawingEnabled = false;
                if (this.draw) {
                    this.olmap.removeInteraction(this.draw);
                }
                if (this.snap) {
                    this.olmap.removeInteraction(this.snap);
                }
                if (this.modify) {
                    this.olmap.removeInteraction(this.modify);
                }
                this.$("#btn-olmap-edit").html("<i class='fa fa-pencil'></i>");
                setTimeout(function () {
                    self._ol_field_changed();
                }, 100);
            }
        },

        _render: function () {
            if (this.olmap) {
                var self = this;
                setTimeout(function () {
                    self.olmap.updateSize();
                    self._updateTabListener();
                }, 250);
            } else {
                this._init_olmap();
            }
            return $.when();
        },
        _updateTimeOutSize: function(){
            var self = this;
            setTimeout(function () {
                self.olmap.updateSize();
            }, 250);
        },        

        _updateTabListener: function () {
            var self = this;
            if (this.tabListenerInstalled) {
                return;
            }
            
            var tab = this.$el.closest('div.tab-pane');
            if (!tab.length) {
                return;
            }

            var tab_link = $('a[href="#' + tab[0].id + '"]');
            if (!tab_link.length) {
                return;
            }

            tab_link.on('click', function (e) {
                self._updateTimeOutSize();
            }.bind(this));

            this.tabListenerInstalled = true;
        },
    });

    registry.add('geofence_drawing', GeofenceDrawing);
    return GeofenceDrawing;
});