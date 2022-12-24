odoo.define('pizza_modifiers.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosPizzaModifierScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                await super._clickProduct(...arguments);
                var self = this;
                const CurrOrder = this.currentOrder;
                const product = this.currentOrder.get_last_orderline().product;
                const product_template = self.env.pos.db.template_by_id[product.product_tmpl_id];
                const item_name = this.currentOrder.get_last_orderline().get_full_product_name();

                if (product.is_modifier && product_template.modifier_ids.length > 0) {
                    let allow_portion = product_template.allow_portion;

                    var modifier_products = [];
                    $.each(product_template.modifier_ids, function(idx, modifier_id) {
                        var modifier = self.env.pos.db.modifiers_by_id[modifier_id];
                        var modifier_product = self.env.pos.db.get_product_by_id(modifier.name[0]);

                        modifier_product.image_url = window.location.origin + '/web/image?model=product.product&field=image_128&id=' + modifier_product.id;

                        var attributes = _.map(modifier_product.attribute_line_ids, (id) => self.env.pos.attributes_by_ptal_id[id]).filter((attr) => attr !== undefined);
                        // let attributes = [];
                        // if (_.some(product.attribute_line_ids, (id) => id in self.env.pos.attributes_by_ptal_id)) {
                        //     attributes = _.map(product.attribute_line_ids, (id) => self.env.pos.attributes_by_ptal_id[id])
                        //           .filter((attr) => attr !== undefined);
                        // }

                        modifier_products.push({
                            'product': modifier_product,
                            'attributes': attributes
                        });
                    });

                    var sub_products = [];
                    const { confirmed, payload } = await this.showPopup('ModifierProductPopup', {
                        title: this.env._t(item_name),
                        products: modifier_products,
                        product: product
                    });

                    if (confirmed) {
                        sub_products = payload;
                    }

                    var slice_products = [];
                    if (product_template.slice_product_ids.length > 0) {
                        $.each(product_template.slice_product_ids, function(idx, slice_template_id) {
                            const slice_template = self.env.pos.db.template_by_id[slice_template_id];
                            if (slice_template) {
                                $.each(slice_template.product_variant_ids, function(idx, slice_product_id) {
                                var slice_product = self.env.pos.db.get_product_by_id(slice_product_id);

                                slice_product.image_url = window.location.origin + '/web/image?model=product.product&field=image_128&id=' + slice_product.id;

                                var attributes = _.map(slice_product.attribute_line_ids, (id) => self.env.pos.attributes_by_ptal_id[id]).filter((attr) => attr !== undefined);
                                // let attributes = [];
                                // if (_.some(product.attribute_line_ids, (id) => id in self.env.pos.attributes_by_ptal_id)) {
                                //     attributes = _.map(slice_product.attribute_line_ids, (id) => self.env.pos.attributes_by_ptal_id[id]).filter((attr) => attr !== undefined);
                                // }

                                slice_products.push({
                                    'product': slice_product,
                                    'attributes': attributes
                                });
                            });
                            }
                            
                        });

                        const { confirmed, payload } = await this.showPopup('SliceProductPopup', {
                            title: this.env._t('Add Slice'),
                            products: slice_products,
                        });
    
                        if (confirmed) {
                            sub_products = sub_products.concat(payload);
                        }                    
                    }
                    var last_orderline = this.currentOrder.get_last_orderline();
                    if (last_orderline) {
                    }

                    $.each(sub_products, function(idx, product) {
                        let extra_product = self.env.pos.db.get_product_by_id(product.product);
                        var extras = $.extend(product.extras ? product.extras : {}, {'parent_line_id': last_orderline && last_orderline.id});
                        CurrOrder.add_product(extra_product, {
                            description: product.attribute_value,
                            price_extra: product.price_extra,
                            merge: false,
                            extras: extras,
                        });
                    });
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosPizzaModifierScreen);

    return ProductScreen;
});