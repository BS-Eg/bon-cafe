odoo.define('wt_pos_combo.Screen', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { Gui } = require('point_of_sale.Gui');
    const { isConnectionError } = require('point_of_sale.utils');
    const { useState, onMounted } = owl.hooks;
    const { parse } = require('web.field_utils');
    const ProductScreen = require('point_of_sale.ProductScreen');

    const PosComboProductScreen = ProductScreen =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }
            async _clickProduct(event) {
                super._clickProduct(event);
                const product = event.detail;
                if(product && product.is_combo_product && product.pos_combo_id){
                    let { confirmed, payload } = await this.showPopup('PosComboConfigurePopup', {
                        product: product,
                        pos_combo_id: product.pos_combo_id[0],
                        is_combo_product: product.is_combo_product,
                    });
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosComboProductScreen);
    

    class PosComboCartItem extends PosComponent {
        constructor() {
            super(...arguments);
        }
        get pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }
        get product_price(){
            return this.env.pos.format_currency(this.props.product.get_price(this.pricelist, 1));
        }
        get total_main_plus_item(){
            var total = this.props.product.get_price(this.pricelist, 1) + this.props.digit_combo_items_totals;
            return this.env.pos.format_currency(total);
        }
    };
    PosComboCartItem.template = 'PosComboCartItem';
    Registries.Component.add(PosComboCartItem);

    class PosComboItemDetails extends PosComponent {
        constructor() {
            super(...arguments);
        }
        select_categories(event){
            var cat_id = $(event.currentTarget).data('pos_combo_cate_id');
            $(this.el).find(".combo_pack_box li").removeClass('active');
            $(this.el).find(".combo_pack_box li[data-pos_combo_cate_id='"+cat_id+"']").addClass('active');
            $(this.el).find(".product_display_block_combo").removeClass('active');
            $(this.el).find(".product_display_block_combo[data-pos_combo_cate_id='"+cat_id+"']").addClass('active');
        }
    };
    PosComboItemDetails.template = 'PosComboItemDetails';
    Registries.Component.add(PosComboItemDetails);


    class ComboCatProducts extends PosComponent {
        constructor() {
            super(...arguments);
            this.products_ids = this.props.combo_cat_obj.product_ids || false;
        }
        get combo_product_items(){
            var self = this;
            var products = [];
            _.each(this.products_ids, function(product_id){
                products.push(self.env.pos.db.get_product_by_id(product_id));
            })
            return products;
        }
    };
    ComboCatProducts.template = 'ComboCatProducts';
    Registries.Component.add(ComboCatProducts);


        class PosComboProductItem extends PosComponent {
        constructor() {
            super(...arguments);
        }
        /**
         * For accessibility, pressing <space> should be like clicking the product.
         * <enter> is not considered because it conflicts with the barcode.
         *
         * @param {KeyPressEvent} event
         */
        OnSelectComboProduct(event) {
            var cat_id = $(event.currentTarget).data('category_id');
            var is_valid = this.check_max_limit_in_category(cat_id);
            if(is_valid){
                var error = "You can only select "+ this.props.combo_cat_obj.max_qty + " items from " + this.props.combo_cat_obj.category_id[1];
                alert(error);
            }else{
                $(event.currentTarget).addClass('selected');
                var qty = parseInt($(event.currentTarget).find('.qty_text').text(), 10);
                var qty = qty + 1;
                $(event.currentTarget).data('qty', qty);
                $(event.currentTarget).find('.qty_text').text(qty);
                this.trigger('updateComboCart');
            }
        }
        get select_item(){
            var selected = '';
            var self = this;
            var prod_id = this.props.product.id;
            var cate_id = this.props.combo_cat_obj.category_id[0];
            if(this.props.combo_lines != undefined){
                _.each(this.props.combo_lines, function(val, key){
                    _.each(val, function(item){
                        if(item.category_id == cate_id && item.product_id == prod_id){
                            selected = 'selected';
                        }
                    });
                });
            }
            return selected;
        }
        get select_qty(){
            var qty_selected = 0;
            var self = this;
            var prod_id = this.props.product.id;
            var cate_id = this.props.combo_cat_obj.category_id[0];
            if(this.props.combo_lines != undefined){
                _.each(this.props.combo_lines, function(val, key){
                    _.each(val, function(item){
                        if(item.category_id == cate_id && item.product_id == prod_id){
                            qty_selected = item.qty;
                        }
                    });
                });
            }
            return qty_selected;
        }
        get imageUrl() {
            const product = this.props.product;
            return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }
        get pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }
        get price() {
            const formattedUnitPrice = this.env.pos.format_currency(
                this.props.product.get_price(this.pricelist, 1),
                'Product Price'
            );
            if (this.props.product.to_weight) {
                return `${formattedUnitPrice}/${
                    this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                }`;
            } else {
                return formattedUnitPrice;
            }
        }
        check_max_limit_in_category(cate_id){
            var qtys = this.props.check_is_max[cate_id];
            var cat_obj = this.props.combo_cat_obj;
            if(cat_obj.is_min_max_config && cat_obj.max_qty && qtys >= cat_obj.max_qty){
                return true;
            }
            return false;
        }
        onProductRemoveClick(event) {
            $(event.currentTarget).closest('.selected').attr('data-qty', 0);
            $(event.currentTarget).closest('.selected').find('.qty_text').text(0);
            $(event.currentTarget).closest('.selected').removeClass('selected');
            this.trigger('updateComboCart');
        }
    }
    PosComboProductItem.template = 'PosComboProductItem';

    Registries.Component.add(PosComboProductItem);

    class ComboOrderLine extends PosComponent {
        get pos_combo_order_lines(){
            if(!_.isEmpty(this.props.line.combo_lines)){
                return this.props.line.combo_lines;
            }
            return [];
        }
        async edit_combo_product(){
            const product = this.props.line.product;
            if(product && product.is_combo_product && product.pos_combo_id){
                let { confirmed, payload } = await this.showPopup('PosComboConfigurePopup', {
                    product: product,
                    pos_combo_id: product.pos_combo_id[0],
                    is_combo_product: product.is_combo_product,
                    selected_lines: this.props.line.combo_lines
                });
            }
        }
        get is_hide_edit(){
            if(this.props.line.order.get_screen_data().name == 'PaymentScreen'){
                return 'oe_hidden';
            }
            return '';
        }        
    }
    ComboOrderLine.template = 'ComboOrderLine';

    Registries.Component.add(ComboOrderLine);

    class ComboCatName extends PosComponent {
        get pos_combo_category(){
            return this.env.pos.db.get_category_by_id(this.props.com_cat_id);
        }
    }
    ComboCatName.template = 'ComboCatName';

    Registries.Component.add(ComboCatName);

    class ComboProductItems extends PosComponent {
        get combo_product_items(){
            return this.props.pos_combo_order_lines[this.props.com_cat_id];
        }
    }
    ComboProductItems.template = 'ComboProductItems';

    Registries.Component.add(ComboProductItems);


    class ComboLinesReceipt extends PosComponent {
        get p_combo_lines(){
            return this.props.line.combo_lines;
        }
    }
    ComboLinesReceipt.template = 'ComboLinesReceipt';

    Registries.Component.add(ComboLinesReceipt);


    return {
        PosComboProductScreen: PosComboProductScreen,
        PosComboCartItem: PosComboCartItem,
        PosComboItemDetails: PosComboItemDetails,
        PosComboProductItem: PosComboProductItem,
        ComboOrderLine: ComboOrderLine,
        ComboCatName: ComboCatName
    }
}); 