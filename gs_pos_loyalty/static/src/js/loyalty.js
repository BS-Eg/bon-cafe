odoo.define('gs_pos_loyalty.pos_loyalty', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');
var ajax = require('web.ajax');

var round_pr = utils.round_precision;

var _t = core._t;

models.load_fields('res.partner','loyalty');
models.load_fields('res.partner','loyalty_id');
models.load_fields('res.partner','delivery_partner');

models.load_models([
    {
        model: 'loyalty.rule',
        condition: function(self){ return self.loyalty; },
        domain: function(self){ return [['loyalty_program_id','=',self.config.loyalty_id[0]]]; },
        fields: ['name','valid_product_ids','points_quantity','points_currency','loyalty_program_id', 'max_amount', 'min_amount'],
        loaded: function(self,rules){
            self.loyalty.rules = [];
            rules.forEach(function(rule) {
                self.loyalty.rules.push(rule);
            });
        },
    },
]);

var _super =  models.Order;

models.Order = models.Order.extend({


    after_load_server_data: function(){
        this.load_orders();
        this.set_start_order();
        if(this.config.use_proxy){
            if (this.config.iface_customer_facing_display) {
                this.on('change:selectedOrder', this.send_current_order_to_customer_facing_display, this);
            }

            return this.connect_to_proxy();
        }
        return Promise.resolve();
    },

    get_rules: function(){
        var rules = [];
        var line_points = 0;
        var self = this;

        this.get_new_loyalty();
        for (var line of this.get_orderlines()){
            if (line.get_reward()) {  // Reward products are ignored
                continue;
            }
        if (!this.pos.loyalty || !this.pos.loyalty.rules){
            return [];
        }
        this.pos.loyalty.rules.forEach(function(rule) {
            var rule_points = 0
            if(rule && rule.valid_product_ids && rule.valid_product_ids.find(function(product_id) {return product_id === line.get_product().id})) {
                rule_points += rule.points_quantity * line.get_quantity();
                rule_points += rule.points_currency * line.get_price_with_tax();
            }
            if(rule_points > line_points)
                line_points = rule_points;
                rules = [rule]

        });
        }
        return rules;
    },

    get_new_loyalty: function(){
        var self = this

        if (this.get_client() && !this.get_client().loyalty){
            this.pos.loyalty = [];
           // this.pos.loyalty.rules = [];
           // this.pos.loyalty.rewards = [];
        }
        if (this.get_client() && this.get_client().loyalty_id && this.get_client().loyalty_id[0] == this.pos.loyalty.id){
            return
        }
        ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'loyalty.program',
                method: 'search_read',
                args:[],
                kwargs: {
                    domain: [],
                    fields: ['name', 'points']
                }
            }).then(function (res) {
                self.pos.loyalties = res;
            })
        if (this.get_client() && this.get_client().loyalty_id &&  this.get_client().loyalty_id.length > 0 && this.get_client().loyalty) {
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'loyalty.program',
                method: 'read',
                args:[self.get_client().loyalty_id[0], ['name', 'points']],
                kwargs: {}
            }).then(function (res) {
                self.pos.loyalty = res[0];
            })
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'loyalty.rule',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['loyalty_program_id', '=', self.get_client().loyalty_id[0]]],
                    fields: ['name','valid_product_ids','points_quantity','points_currency','loyalty_program_id', 'min_amount', 'max_amount']
                }
            }).then(function (res) {
                if(self.pos.loyalty){
                    self.pos.loyalty.rules = res;
                }
            });
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'loyalty.reward',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['loyalty_program_id', '=', self.get_client().loyalty_id[0]]],
                    fields: ['name','reward_type','minimum_points','gift_product_id','point_cost','discount_product_id',
                'discount_percentage', 'discount_fixed_amount', 'discount_apply_on', 'discount_type', 'discount_apply_on',
                'discount_specific_product_ids', 'discount_max_amount', 'minimum_amount', 'loyalty_program_id']
                }
            }).then(function (res) {
                self.pos.loyalty.rewards = res;
            })
            this.pos.loyalty = self.pos.loyalty;
            if(this.pos.loyalty){
                this.pos.loyalty.rules = self.pos.loyalty.rules;
                this.pos.loyalty.rewards = self.pos.loyalty.rewards;
            }
        }
    },

    get_won_points: function(){
        var self = this;
      //  this.get_new_loyalty();
        if (!this.pos.loyalty || ! this.pos.loyalty.rules || !this.get_client() || this.get_client() && !this.get_client().loyalty ) {
            return 0;
        }
        var total_points = 0;
        for (var line of this.get_orderlines()){
            if (line.get_reward()) {
                continue;
            }
            var line_points = 0;
            if (this.pos.loyalty && this.pos.loyalty.rules) {
                this.pos.loyalty.rules.forEach(function(rule) {
                     var rule_points = 0
                    if(rule && rule.valid_product_ids && rule.valid_product_ids.find(function(product_id) {return product_id === line.get_product().id})) {
                        rule_points += rule.points_quantity * line.get_quantity();
                        rule_points += rule.points_currency * line.get_price_with_tax();
                    }
                    if(rule_points > line_points)
                        line_points = rule_points;
                });
            }

            total_points += line_points;
        }
        total_points += this.get_total_with_tax() * this.pos.loyalty.points;
        return round_pr(total_points, 1);
    },

    /* The total number of points spent on rewards */
    get_spent_points: function() {
        var self = this;
       // this.get_new_loyalty();

       var rules = this.get_rules();
       if (rules && rules.length == 0){
        return 0;
       }
        if (!this.pos.loyalty || !this.get_client() || this.get_client() && !this.get_client().loyalty) {
            return 0;
        } else {
            var points   = 0;
            for (var line of this.get_orderlines()){
                var reward = line.get_reward();
                if(reward) {
                    points += round_pr(rules[0].points_currency * (-line.get_price_with_tax()), 1);
                }
            }
            return points;
        }
    },

    /* The total number of points lost or won after the order is validated */
    get_new_points: function() {
        var self = this;
       // this.get_new_loyalty();
        if (!this.pos.loyalty || !this.get_client() || this.get_client() && !this.get_client().loyalty) {
            return 0;
        } else {
            return round_pr(this.get_won_points() - this.get_spent_points(), 1);
        }
    },

    /* The total number of points that the customer will have after this order is validated */
    get_new_total_points: function() {
        var self = this;
       // this.get_new_loyalty();
        if (!this.pos.loyalty || !this.get_client() || this.get_client() && !this.get_client().loyalty) {
            return 0;
        } else {
            if(this.state != 'paid'){
                return round_pr(this.get_client().loyalty_points + this.get_new_points(), 1);
            }
            else{
                return round_pr(this.get_client().loyalty_points, 1);
            }
        }
    },

    /* The number of loyalty points currently owned by the customer */
    get_current_points: function(){
        var self = this;
        //this.get_new_loyalty();
        if (this.get_client() && !this.get_client().loyalty){
            return 0;
        }
        return this.get_client() ? this.get_client().loyalty_points : 0;
    },

    /* The total number of points spendable on rewards */
    get_spendable_points: function(){
        var self = this
        //this.get_new_loyalty();
        if (!this.pos.loyalty || !this.get_client() || this.get_client() && !this.get_client().loyalty) {
            return 0;
        } else {
            return round_pr(this.get_client().loyalty_points - this.get_spent_points(), 1);
        }
    },

    /* The list of rewards that the current customer can get */
    get_available_rewards: function(){
        var self = this
       // this.get_new_loyalty();
        var client = this.get_client();
        if (!client || client && !client.loyalty || !this.pos.loyalty || !this.pos.loyalty.rewards) {
            return [];
        }

        var self = this;
        var rewards = [];
        for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
            var reward = this.pos.loyalty.rewards[i];
            if (reward.minimum_points > self.get_spendable_points()) {
                continue;
            } else if(reward.reward_type === 'discount' && reward.point_cost > self.get_spendable_points()) {
                continue;
            } else if(reward.reward_type === 'gift' && reward.point_cost > self.get_spendable_points()) {
                continue;
            } else if(reward.reward_type === 'discount' && reward.discount_apply_on === 'specific_products' ) {
                var found = false;
                self.get_orderlines().forEach(function(line) {
                    found |= reward.discount_specific_product_ids.find(function(product_id){return product_id === line.get_product().id;});
                });
                if(!found)
                    continue;
            } else if(reward.reward_type === 'discount' && reward.discount_type === 'fixed_amount' && self.get_total_with_tax() < reward.minimum_amount) {
                continue;
            }
            rewards.push(reward);
        }
        if (this.pos.loyalty.rewards)
            return this.pos.loyalty.rewards[0];
        return []
    },

    apply_reward: function(reward, discount_entered, max_amount, min_amount){
        var self = this
       // this.get_new_loyalty();
        var client = this.get_client();
        var product, product_price, order_total, spendable;
        var crounding;

        if (!client || client && !client.loyalty) {
            return;
        } else if (reward.reward_type === 'gift') {
            product = this.pos.db.get_product_by_id(reward.gift_product_id[0]);

            if (!product) {
                return;
            }
            if (discount_entered >= order_total){
                this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be less than Total amount.'),
                });
                return;
            }
            else if (discount_entered > max_amount){
                this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be less than or equal the the Max amount.'),
                });
                return;
            }
            else if (discount_entered < min_amount){
                this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be greater than or equal to the Min amount.'),
                });
                return;
            }
            if (reward){
                this.add_product(product, {
                    price: discount_entered,
                    quantity: 1,
                    merge: false,
                    extras: { reward_id: reward.id },
                });
            }

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
            if (reward) {
                this.add_product(product, {
                    price: - discount_entered, //(reward.discount_type === "percentage")? -discount: -reward.discount_fixed_amount,
                    quantity: 1,
                    merge: false,
                    extras: { reward_id: reward.id },
                });
            }
        }
    },

    finalize: function(){
        var client = this.get_client();
        var self = this;
       // this.get_new_loyalty();
        if ( client && client.loyalty) {
            client.loyalty_points = this.get_new_total_points();
        }
        _super.prototype.finalize.apply(this,arguments);
    },

    export_for_printing: function(){
        var self = this
      //  this.get_new_loyalty();
        var json = _super.prototype.export_for_printing.apply(this,arguments);

        if (this.pos.loyalty && this.get_client()) {
            json.loyalty = {
                name:         this.pos.loyalty.name,
                client:       this.get_client().name,
                points_won  : this.get_won_points(),
                points_spent: this.get_spent_points(),
                points_total: this.get_new_total_points(),
            };
        }
        return json;
    },

    export_as_JSON: function(){
        var self = this
        this.get_new_loyalty();
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.loyalty_points = this.get_new_points();
        return json;
    },




});

models.Orderline = models.Orderline.extend({
    get_reward: function(){
        var reward_id = this.reward_id;
        if (!this.pos.loyalty || !this.pos.loyalty.rewards){
            return []
        }
        if(this.pos.loyalty.rewards && this.pos.loyalty.rewards.length){
            return this.pos.loyalty.rewards.find(function(reward){return reward.id === reward_id;});
        } else {
            return []
        }
    },

});

})