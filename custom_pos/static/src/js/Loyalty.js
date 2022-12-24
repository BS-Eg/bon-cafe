odoo.define('custom_pos.pos_loyalty', function (require) {
"use strict";

var models = require('point_of_sale.models');
var pos_loyalty = require('pos_loyalty.pos_loyalty');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;

var _super = models.Order;
models.Order = models.Order.extend({

    apply_reward: function(reward){
        var client = this.get_client();
        var product, product_price, order_total, spendable;
        var crounding;

        if (!client) {
            return;
        } else if (reward.reward_type === 'gift') {
            product = this.pos.db.get_product_by_id(reward.gift_product_id[0]);

            if (!product) {
                return;
            }

            this.add_product(product, {
                price: 0,
                quantity: 1,
                merge: false,
                extras: { reward_id: reward.id },
            });

        } else if (reward.reward_type === 'discount') {

            crounding = this.pos.currency.rounding;
            spendable = this.get_spendable_points();
            order_total = this.get_total_with_tax();
            var discount = 0;

            product = this.pos.db.get_product_by_id(reward.discount_product_id[0]);

            if (!product) {
                return;
            }

            if(reward.discount_type === "percentage") {
                if(reward.discount_apply_on === "on_order"){
                    discount += round_pr(order_total * (reward.discount_percentage / 100), crounding);
                }

                if(reward.discount_apply_on === "specific_products") {
                    for (var prod of reward.discount_specific_product_ids){
                        var specific_products = this.pos.db.get_product_by_id(prod);

                        if (!specific_products)
                            return;

                        for (var line of this.get_orderlines()){
                            if(line.product.id === specific_products.id)
                                discount += round_pr(line.get_price_with_tax() * (reward.discount_percentage / 100), crounding);
                        }
                    }
                }

                if(reward.discount_apply_on === "cheapest_product") {
                    var price;
                    for (var line of this.get_orderlines()){
                        if((!price || price > line.get_unit_price()) && line.product.id !== product.id) {
                            discount = round_pr(line.get_price_with_tax() * (reward.discount_percentage / 100), crounding);
                            price = line.get_unit_price();
                        }
                    }
                }
                }

            if(reward.discount_max_amount !== 0 && discount > reward.discount_max_amount)
                discount = reward.discount_max_amount;

            var custom_qty = this.get_client().loyalty_points;
            const diff_totalorder_loyalty = (this.get_total_with_tax() - this.get_client().loyalty_points);
            if (diff_totalorder_loyalty < 0){
                custom_qty = this.get_total_with_tax();               
            }
            this.add_product(product, {
                price: (reward.discount_type === "percentage")? -discount: -reward.discount_fixed_amount,
                // quantity: 1,
                quantity: custom_qty,
                merge: false,
                extras: { reward_id: reward.id },
            });
        }
    },  
    get_redeem_amount: function() {
         var redeem_amount = 0;
         for(var i = 0; i < this.orderlines.models.length; i++){
            if(this.orderlines.models[i].price < 0){
                redeem_amount = this.orderlines.models[i].price * this.orderlines.models[i].quantity
            }
         }
         return redeem_amount;
    },
    get_total_payment_amount: function() {
         var payment_amount = 0;
         for(var i = 0; i < this.paymentlines.models.length; i++){
              payment_amount = this.paymentlines.models[i].amount
            }
             return payment_amount;
         },
    export_for_printing: function(){
        var orderlines = [];
        var self = this;

        this.orderlines.each(function(orderline){
            orderlines.push(orderline.export_for_printing());
        });

        // If order is locked (paid), the 'change' is saved as negative payment,
        // and is flagged with is_change = true. A receipt that is printed first
        // time doesn't show this negative payment so we filter it out.
        var paymentlines = this.paymentlines.models
            .filter(function (paymentline) {
                return !paymentline.is_change;
            })
            .map(function (paymentline) {
                return paymentline.export_for_printing();
            });
        var client  = this.get('client');
        var cashier = this.pos.get_cashier();
        var company = this.pos.company;
        var date    = new Date();

        function is_html(subreceipt){
            return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
        }

        function render_html(subreceipt){
            if (!is_html(subreceipt)) {
                return subreceipt;
            } else {
                subreceipt = subreceipt.split('\n').slice(1).join('\n');
                var qweb = new QWeb2.Engine();
                    qweb.debug = config.isDebug();
                    qweb.default_dict = _.clone(QWeb.default_dict);
                    qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');

                return qweb.render('subreceipt',{'pos':self.pos,'order':self, 'receipt': receipt}) ;
            }
        }
        var receipt = {
            redeem_amt:this.get_redeem_amount(),
            payment_amt:this.get_total_payment_amount(),
            orderlines: orderlines,
            paymentlines: paymentlines,
            subtotal: this.get_subtotal(),
            total_with_tax: this.get_total_with_tax() - this.get_redeem_amount(),
            total_rounded: this.get_total_with_tax() + this.get_rounding_applied(),
            total_without_tax: this.get_total_without_tax(),
            total_tax: this.get_total_tax(),
            total_paid: this.get_total_paid(),
            total_discount: this.get_total_discount(),
            rounding_applied: this.get_rounding_applied(),
            tax_details: this.get_tax_details(),
            change: this.locked ? this.amount_return : this.get_change(),
            name : this.get_name(),
            client: client ? client : null ,
            invoice_id: null,   //TODO
            cashier: cashier ? cashier.name : null,
            precision: {
                price: 2,
                money: 2,
                quantity: 3,
            },
            date: {
                year: date.getFullYear(),
                month: date.getMonth(),
                date: date.getDate(),       // day of the month
                day: date.getDay(),         // day of the week
                hour: date.getHours(),
                minute: date.getMinutes() ,
                isostring: date.toISOString(),
                localestring: this.formatted_validation_date,
            },
            company:{
                email: company.email,
                website: company.website,
                company_registry: company.company_registry,
                contact_address: company.partner_id[1],
                vat: company.vat,
                vat_label: company.country && company.country.vat_label || _t('Tax ID'),
                name: company.name,
                phone: company.phone,
                logo:  this.pos.company_logo_base64,
            },
            currency: this.pos.currency,
        };

        if (is_html(this.pos.config.receipt_header)){
            receipt.header = '';
            receipt.header_html = render_html(this.pos.config.receipt_header);
        } else {
            receipt.header = this.pos.config.receipt_header || '';
        }
        if (this.pos.loyalty && this.get_client()) {
            receipt.loyalty = {
                name:         this.pos.loyalty.name,
                client:       this.get_client().name,
                points_won  : this.get_won_points(),
                points_spent: this.get_spent_points(),
                points_total: this.get_new_total_points(),
            };
            }

        if (is_html(this.pos.config.receipt_footer)){
            receipt.footer = '';
            receipt.footer_html = render_html(this.pos.config.receipt_footer);
        } else {
            receipt.footer = this.pos.config.receipt_footer || '';
        }
        return receipt;
    },
     export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.redeem_amt = this.get_redeem_amount();
        return json;
    },
});

});
