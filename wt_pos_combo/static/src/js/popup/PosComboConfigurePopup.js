odoo.define('wt_pos_combo.PosComboConfigurePopup', function(require) {
    'use strict';

    const { useState, useSubEnv } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class PosComboConfigurePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useListener('updateComboCart', this._updateComboCart);
            this.product = this.props.product || false;
            this.pos_combo_id = this.props.pos_combo_id || false;
            this.is_editable_pp = this.props.selected_lines ? true : false;
            this.selected_lines = this.props.selected_lines || [];
            this.total_combo_items = 0;
            this.state = useState({
                selected_lines: this.selected_lines
            });
            this._updateComboCart();
        }
        get combo_info(){
            return this.env.pos.db.get_pos_combos_by_id(this.pos_combo_id);
        }
        get combo_lines(){
            return this.selected_lines;
        }
        get combo_items_totals(){
            return this.env.pos.format_currency(this.total_combo_items);
        }
        get digit_combo_items_totals(){
            return this.total_combo_items;
        }
        get combo_cat_items(){
            var self = this;
            var combo_items = [];
            _.each(this.combo_info.pos_combo_items_ids, function(el){
                combo_items.push(self.env.pos.db.get_pos_combos_items_by_id(el));
            });
            return combo_items;
        }
        get pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }
        price(product, qty) {
            const formattedUnitPrice = this.env.pos.format_currency(
                product.get_price(this.pricelist, qty),
                'Product Price'
            );
            if (product.to_weight) {
                return `${formattedUnitPrice}/${
                    this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                }`;
            } else {
                return formattedUnitPrice;
            }
        }
        render_selected_products(){
            var self = this;
            var items = $(this.el).find('.product.selected');
            this.selected_lines = [];
            this.total_combo_items = 0;
            var products = [];
            _.each(items, function(el){
                var data = $(el).data()
                var category = self.env.pos.db.get_category_by_id(data.category_id);
                var product = self.env.pos.db.get_product_by_id(data.product_id);
                var price = self.price(product, data.qty);
                var total_price = product.get_price(self.pricelist, data.qty) * data.qty;
                var unit_price = product.get_price(self.pricelist, data.qty);
                products.push({
                    'category_id': data.category_id,
                    'product_id': data.product_id,
                    'product': product,
                    'product_name': product.display_name,
                    'category': category,
                    'qty': data.qty,
                    'price': price,
                    'total_price': self.env.pos.format_currency(total_price),
                    'unit_price': unit_price,
                    'decimal_total_price': total_price
                });
                self.total_combo_items = self.total_combo_items + total_price;
            });
            if(products.length){
                this.selected_lines = _.groupBy(products, 'category_id');
            }
            this.render();
        }
        render_editable_value(){
            var self = this;
            if(this.selected_lines != undefined){
                var products = [];
                _.each(this.selected_lines, function(val, key){
                    _.each(val, function(item){
                        var product = self.env.pos.db.get_product_by_id(item.product_id);
                        products.push({
                            'category_id': item.category_id,
                            'product_id': item.product_id,
                            'product': product,
                            'product_name': item.display_name,
                            'category': item.category,
                            'qty': item.qty,
                            'price': item.price,
                            'total_price': item.total_price,
                            'unit_price': item.unit_price,
                            'decimal_total_price': item.decimal_total_price
                        });
                        self.total_combo_items = self.total_combo_items + item.decimal_total_price;
                    });
                });
                if(products.length){
                    this.selected_lines = _.groupBy(products, 'category_id');
                }
            }
            this.is_editable_pp = false;
            this.render();
        }
        _updateComboCart(){
            if(!this.is_editable_pp){
                this.render_selected_products();
            }else{
                this.render_editable_value();
            }
        }
        get check_is_max(){
            var self = this;
            var category_data = {};
            _.each(this.combo_cat_items, function(el){
                var qtys = _.map(self.combo_lines, function(num, key){
                    if(key == el.category_id[0]){
                        var sum = _.map(num, 'qty').reduce((a, b) => a + b, 0)
                        return sum;
                    }
                    return 0;
                });
                var qtys_total = qtys.reduce((a, b) => a + b, 0);
                category_data[el.category_id[0]] = qtys_total;
            });
            return category_data;
        }
        check_is_valid_or_not(){
            var self = this;
            var flag = true;
            var error = '';
            _.each(this.combo_cat_items, function(el){
                var qtys = _.map(self.combo_lines, function(num, key){
                    if(key == el.category_id[0]){
                        var sum = _.map(num, 'qty').reduce((a, b) => a + b, 0)
                        return sum;
                    }
                    return 0;

                });
                var qtys_total = qtys.reduce((a, b) => a + b, 0);
                if(el.is_min_max_config && el.min_qty && qtys_total < el.min_qty){
                    error = "You must have to select " + el.min_qty +" item from "+ el.category_id[1];
                    flag = false;
                    return false;
                }
            });
            if(error){
                alert(error);
            }
            return flag;
        }
        async confirm() {
            var s_orderline = this.env.pos.get_order().get_selected_orderline();
            var is_valid = this.check_is_valid_or_not();
            if(is_valid){
                s_orderline.set_combo_lines(this.combo_lines);
                this.trigger('close-popup');
            }
        }
    };
    PosComboConfigurePopup.template = 'PosComboConfigurePopup';
    Registries.Component.add(PosComboConfigurePopup);

    return {
        PosComboConfigurePopup,
    };

});