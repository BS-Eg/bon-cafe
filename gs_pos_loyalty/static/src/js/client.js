odoo.define('gs_pos_loyalty.ClientDetailsEdit', function(require) {
    'use strict';

    const { _t } = require('web.core');
    const { getDataURLFromFile } = require('web.utils');
    const PosComponent = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');


    class ClientDetailsEdit extends PosComponent {
        constructor() {
            super(...arguments);
            this.checkboxField = ['loyalty'];
            this.intFields.push('loyalty_id');
            this.changes['loyalty_id'] = this.props.partner.loyalty_id && this.props.partner.loyalty_id[0];
        }
        changeValue(){
            $('input.eligible_loyalty').change(function(){
                if($(this).is(":checked")) {
                    $(".client-loyalty").parent().show();
                } else {
                    $(".client-loyalty").parent().hide();
                }
            });
        }
        saveChanges() {
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else if (this.checkboxField.includes(key)) {
                    processedChanges[key] = $(".eligible_loyalty").is(":checked")

                } else {
                    processedChanges[key] = value;
                }
            }
            if ((!this.props.partner.name && !processedChanges.name) ||
                processedChanges.name === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _t('A Customer Name Is Required'),
                });
            }
            processedChanges.id = this.props.partner.id || false;
            this.trigger('save-changes', { processedChanges });
        }


    }

    ClientDetailsEdit.template = 'ClientDetailsEdit';

    Registries.Component.add(ClientDetailsEdit);

    return ClientDetailsEdit;
});


