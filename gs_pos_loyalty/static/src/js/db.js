odoo.define('gs_pos_loyalty.DB', function (require) {

var posdb = require('point_of_sale.DB');

posdb.include({
    _partner_search_string: function(partner){
        str =  this._super.apply(this, arguments);
        if(partner.phone){
            str += '|' + partner.phone.split(' ').join('');
        }
        return str;
    }
});

})