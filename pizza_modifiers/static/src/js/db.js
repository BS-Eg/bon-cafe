odoo.define('pizza_modifiers.db', function (require) {
"use strict";

var PosDB = require('point_of_sale.DB');

PosDB.include({
    init: function(options){
        this.template_by_id = {};
        this.product_attribute_by_id = {};
        this.product_attribute_value_by_id = {};
        this.modifiers_by_id = {};
        this._super(options);
    },
    add_templates: function(templates){
        var self = this;
        for(var i=0 ; i < templates.length; i++){
            var attribute_value_ids = [];
            // store Templates
            this.template_by_id[templates[i].id] = templates[i];
        }
    },
    add_modifiers: function(modifiers){
        for(var i=0 ; i < modifiers.length; i++){
            this.modifiers_by_id[modifiers[i].id] = modifiers[i];
        }
    },
});

});
