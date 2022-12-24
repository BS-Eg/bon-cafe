odoo.define('custom_pos.CustomPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    const CustomPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                useListener('selectclient-1', this.selectClient_1);
            }

            async selectClient_1() {
                // IMPROVEMENT: This code snippet is repeated multiple times.
                // Maybe it's better to create a function for it.
                const currentClient = this.currentOrder.get_client_1();
                // const currentClient = null
                console.log('new_custom_select_client_1',this.currentOrder.get_client_1());
                const { confirmed, payload: newClient } = await this.showTempScreen(
                    'ClientListScreen',
                    { client: currentClient,'delivery_partner_button':'true'}
                    
                );
                if (confirmed) {
                    this.currentOrder.set_client_1(newClient);                
                    //auto selection of invoice button(toggleIsToInvoice())
                    this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice()); 
                    this.render();                
                    // this.currentOrder.updatePricelist(newClient);
                }
            }
    

            async _isOrderValid(isForceValidate) {
                if (this.currentOrder.get_orderlines().length === 0) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Empty Order'),
                        body: this.env._t(
                            'There must be at least one product in your order before it can be validated'
                        ),
                    });
                    return false;
                }
                // pop error for no delivery partner if payment_method is "Food App"
                if (!this.currentOrder.get_client_1()) {                
                    for (var i = 0; i < this.paymentLines.length; i++) {
                        var payment_method_name =  this.paymentLines[i].payment_method.name;
                        if (payment_method_name.includes("Food App")) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Empty Order'),
                                body: this.env._t(
                                    'There must be one delivery partner in your order before it can be validated.'
                                ),
                            });
                            return false;
                        }
                    }                 
                }
    
                // pop error if delivery partner is selected even payment_method is non "Food App"
                // problem will be occured when two payment methods will be used at a time
                if (this.currentOrder.get_client_1()) {                
                    for (var i = 0; i < this.paymentLines.length; i++) {
                        var payment_method_name =  this.paymentLines[i].payment_method.name;
                        if (!payment_method_name.includes("Food App")) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Please select the Customer'),
                                body: this.env._t(
                                    'Selected payment method is non Food App'
                                ),
                            });
                            return false;
                        }
                    }                 
                }
    
    
                if (this.currentOrder.is_to_invoice() && !this.currentOrder.get_client()) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select the Customer'),
                        body: this.env._t(
                            'You need to select the customer before you can invoice an order.'
                        ),
                    });
                    if (confirmed) {
                        this.selectClient();
                    }
                    return false;
                }
    
                if (!this.currentOrder.is_paid() || this.invoicing) {
                    return false;
                }
    
                if (this.currentOrder.has_not_valid_rounding()) {
                    var line = this.currentOrder.has_not_valid_rounding();
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Incorrect rounding'),
                        body: this.env._t(
                            'You have to round your payments lines.' + line.amount + ' is not rounded.'
                        ),
                    });
                    return false;
                }
    
                // The exact amount must be paid if there is no cash payment method defined.
                if (
                    Math.abs(
                        this.currentOrder.get_total_with_tax() - this.currentOrder.get_total_paid()  + this.currentOrder.get_rounding_applied()
                    ) > 0.00001
                ) {
                    var cash = false;
                    for (var i = 0; i < this.env.pos.payment_methods.length; i++) {
                        cash = cash || this.env.pos.payment_methods[i].is_cash_count;
                    }
                    if (!cash) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Cannot return change without a cash payment method'),
                            body: this.env._t(
                                'There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'
                            ),
                        });
                        return false;
                    }
                }
    
                // if the change is too large, it's probably an input error, make the user confirm.
                if (
                    !isForceValidate &&
                    this.currentOrder.get_total_with_tax() > 0 &&
                    this.currentOrder.get_total_with_tax() * 1000 < this.currentOrder.get_total_paid()
                ) {
                    this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please Confirm Large Amount'),
                        body:
                            this.env._t('Are you sure that the customer wants to  pay') +
                            ' ' +
                            this.env.pos.format_currency(this.currentOrder.get_total_paid()) +
                            ' ' +
                            this.env._t('for an order of') +
                            ' ' +
                            this.env.pos.format_currency(this.currentOrder.get_total_with_tax()) +
                            ' ' +
                            this.env._t('? Clicking "Confirm" will validate the payment.'),
                    }).then(({ confirmed }) => {
                        if (confirmed) this.validateOrder(true);
                    });
                    return false;
                }
    
                return true;
            }
    
        };

    Registries.Component.extend(PaymentScreen, CustomPaymentScreen);

    return CustomPaymentScreen;
});
