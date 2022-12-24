odoo.define('gs_notification.tree_header_extend', function (require){
    "use strict";
    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");
    var rpc = require('web.rpc');

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName == 'gs.notification') {
                var your_btn = this.$buttons.find('button.get_data_in_notification_form');
                your_btn.on('click', this.proxy('get_data_in_notification_form'));
            }
        },
        get_data_in_notification_form: function(){

//        #$#$# TO OPEN A WIZARD #$#$#
         this.do_action({
                name: "Compute",
                type: 'ir.actions.act_window',
                res_model: 'get.data.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
            });

        }
    };

    ListController.include(includeDict);
});