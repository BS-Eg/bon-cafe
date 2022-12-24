odoo.define('custom_pos.DB', function (require) {
"use strict";

var PosDB = require('point_of_sale.DB');
var models = require('point_of_sale.models');

//load delivery_partner field in js to add filter in customer in pos
models.load_fields('res.partner', ['delivery_partner']);
models.load_fields('res.partner', ['customer_rank']);
models.load_fields('res.partner', ['image_1920']);//used in ClientLine.js
models.load_fields('pos.payment.method', ['custom_image_1920']);//used in PaymentMethodButton.js

// add filter to custom in pos
var DB = PosDB.include({

    

    get_partners_sorted: function(max_count){
                
        max_count = max_count ? Math.min(this.partner_sorted.length, max_count) : this.partner_sorted.length;
        var partners = [];
        for (var i = 0; i < max_count; i++) {          

            if((this.partner_by_id[this.partner_sorted[i]].delivery_partner == false) && (this.partner_by_id[this.partner_sorted[i]].customer_rank > 0)){
                partners.push(this.partner_by_id[this.partner_sorted[i]]);
            }
        }
        return partners;
    },

    get_delivery_partners_sorted: function(max_count){
                
        max_count = max_count ? Math.min(this.partner_sorted.length, max_count) : this.partner_sorted.length;
        var partners = [];
        for (var i = 0; i < max_count; i++) {          
            if((this.partner_by_id[this.partner_sorted[i]].delivery_partner == true)){
                partners.push(this.partner_by_id[this.partner_sorted[i]]);
            }
        }
        return partners;
    },
    // filter while searching
    search_partner: function (query,delivery_partner_b) {
        var res = this._super.apply(this, arguments)

        // if(res[0]['delivery_partner']== false && res[0]['customer_rank']>0){
        //     return res;
        // }
        // else{
        //     return [];
        // }  

        // delivery_partner_b for delivery_partner_button
        if(delivery_partner_b==true && res[0]['delivery_partner']== true){
            return res;            
        }
        else if(delivery_partner_b==true && res[0]['delivery_partner']== false){
                return [];            
        }

        else if(res[0]['delivery_partner']== false && res[0]['customer_rank']>0){
            return res;
        }
        else{
            return [];
        }        
      

    }

});
return DB;
});

// odoo.define('custom_pos.inherit_DB', function (require) {
//     "use strict";

// var PosDB = require('point_of_sale.DB');

// var search_db = PosDB.include({
//     search_partner: function (query) {
//         var res = this._super.apply(this, arguments)
//         if(!(res[0]['delivery_partner'])){
//             return res;
//         }
//         else{
//             return [];
//         }

        

//     },
// });
// return search_db;

// });

