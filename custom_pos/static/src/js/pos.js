odoo.define('custom_pos.pos', function(require) {
"use strict";

var models = require('point_of_sale.models');

//add notes in pos receipt
var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    export_for_printing: function() {
        var line = _super_orderline.export_for_printing.apply(this,arguments);
        line.note = this.note;
        return line;
    },
});

var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    get_client_1: function() {
        var order = this.get_order();
        if (order) {
            return order.get_client_1();
        }
        return null;
    }
});

// line 2552
var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function(attr,options) {
        _super_order.initialize.apply(this,arguments);       
        this.set({ client_1: null });
        this.save_to_db();
    },
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this,arguments);
        json.delivery_partner_id = this.get_client_1() ? this.get_client_1().id : false
        console.log('json_delivery',json.delivery_partner_id);
        return json;
    },    
    init_from_JSON: function(json) {
        var client_1;
        _super_order.init_from_JSON.apply(this,arguments);
        if (json.delivery_partner_id) {
            client_1 = this.pos.db.get_partner_by_id(json.delivery_partner_id);
            if (!client_1) {
                console.error('ERROR: trying to load a delivery partner not available in the pos');
            }
        } else {
            client_1 = null;
        }
        this.set_client_1(client_1);
    },
    // export_for_printing: function() {
    //     var line = _super_orderline.export_for_printing.apply(this,arguments);
    //     line.note = this.note;
    //     console.log('custom_noe',this.note);
    //     return line;
    // },
    set_client_1: function(client){
        this.assert_editable();
        
        if (client){  //if delivery partner is selected then customer is set to be null
            // this.set({ client: null });
            this.set({ client: client }); //here set delivery partner as a customer also
            this.save_to_db();
        }
        this.set('client_1',client);
    }, 

    /* ---- Client / Customer --- */
    // the client related to the current order.
    set_client: function(client){
        this.assert_editable();
        var delivery_partner = this.get_client_1();
        if (delivery_partner){ //if customer is selected then delivery partner is set to be null
            this.set({ client_1: null });
            this.save_to_db();
        }
        this.set('client',client);
    },

    get_client_1: function(){
        return this.get('client_1');
    },
    get_client_name_1: function(){
        var client = this.get('client_1');
        return client ? client.name : "";
    }
    
});


});