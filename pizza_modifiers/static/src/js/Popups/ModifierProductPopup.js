odoo.define('pizza_modifiers.ModifierProductPopup', function(require) {
    'use strict';

    const { useState, useSubEnv } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    var core = require('web.core');
    var QWeb = core.qweb;
    class ModifierProductPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.modifiers_list = []
        }
        mounted() {
            var self = this;
            $('map').imageMapResize();
        }
        SelectPizzaPortionArea(event) {
            var self = this;
            var total_portion = $(event.currentTarget).attr('data-total_portion');
            var portion_no = $(event.currentTarget).attr('data-portion_no');
            var partion_label = $(event.currentTarget).attr('data-label');
            $('.portion-modifier').attr({
                'data-total_portion': total_portion,
                'data-portion_no': portion_no,
                'data-label': partion_label
            });
            $(event.currentTarget).closest('.portion-modifier').find('article.selected').removeClass('selected');
            if (self.modifiers_list) {
                _.each(self.modifiers_list, function(modifier) {
                    if (portion_no == modifier.portion_no && total_portion == modifier.total_portion) {
                        $(event.currentTarget).closest('.portion-modifier').find('article[data-product-id="' + modifier.product + '"][data-attribure-value-name="' + modifier.attribute_value + '"]').addClass('selected');
                    }
                });
            }
        }
        _AddModfierCartView() {
            var self = this;
            $('.modifer_cart_lines').empty();
            var new_modifiers_list = [];
            _.each(this.modifiers_list, function(modifier) {
                var product = posmodel.db.get_product_by_id(modifier.product);
                new_modifiers_list.push({
                    'product': product,
                    'attribute_value': modifier.attribute_value,
                    'portion_name': modifier.extras.portion,
                    'qty': 1,
                    'price_extra': modifier.price_extra
                })
            });
            var rendered_modifer_lines = QWeb.render('ModfierDisplayCartOrderLines', {
                'modifierslines': new_modifiers_list,
                'pos': self,
            });
            $('.modifer_cart_lines').html(rendered_modifer_lines);
        }
        SelectExtraModifier(event) {
            $(event.currentTarget.parentElement).find('article.selected').removeClass('selected');
            $(event.currentTarget).addClass('selected');
            var $item = $(event.currentTarget);
            var portion_modifier = $(event.currentTarget).closest('.portion-modifier');
            var extras_dict = {};
            var quantity = 1;
            var portion_no = false;
            var total_portion = false;
            if (portion_modifier && portion_modifier.length) {
                if (portion_modifier.attr('data-portion_no')) {
                    portion_no = portion_modifier.attr('data-portion_no')
                    extras_dict['portion'] = portion_modifier.attr('data-label');
                }
                var total_portion_str = portion_modifier.attr('data-total_portion');
                total_portion = total_portion_str
                if (total_portion_str && portion_modifier.attr('data-portion_no') != "full") {
                    quantity = 1 / parseInt(total_portion_str);
                }
            }
            var product_id = $item.attr('data-product-id');
            var attribute_value = $item.attr('data-attribure-value-name');
            if (this.modifiers_list.length) {
                var already_exisit = false;
                _.each(this.modifiers_list, function(modifier) {
                    if (modifier.product == product_id && portion_no == modifier.portion_no && total_portion == modifier.total_portion) {
                        already_exisit = true;
                        modifier['product'] = product_id;
                        modifier['attribute_value'] = attribute_value;
                        modifier['price_extra'] = parseFloat($item.attr('data-attribure-price-extra'));
                        modifier['quantity'] = quantity;
                        modifier['portion_no'] = portion_no;
                        modifier['extras'] = extras_dict;
                        modifier['total_portion'] = total_portion;
                    }
                });
                if (!already_exisit) {
                    this.modifiers_list.push({
                        'product': product_id,
                        'attribute_value': attribute_value,
                        'price_extra': parseFloat($item.attr('data-attribure-price-extra')),
                        'quantity': quantity,
                        'portion_no': portion_no,
                        'extras': extras_dict,
                        'total_portion': total_portion,
                    });
                }
            } else {
                this.modifiers_list.push({
                    'product': product_id,
                    'attribute_value': attribute_value,
                    'price_extra': parseFloat($item.attr('data-attribure-price-extra')),
                    'quantity': quantity,
                    'portion_no': portion_no,
                    'extras': extras_dict,
                    'total_portion': total_portion,
                });
            }
            this._AddModfierCartView();
        }
        SelectModifiedPizzaPoration() {
            var $el = $(event.currentTarget).parents('.modifier-product-popup');
            $el.find('.modifiers-by-portion').toggleClass('oe_hidden');
            $(event.currentTarget).find('i').toggleClass('fa-plus-circle fa-minus-circle')
        }
        getPayload() {
            var $el = $(event.currentTarget).parents('.modifier-product-popup');

            var modifiers = [];
            $.each($el.find('.product-list'), function() {
                if ($(this).find('article.selected').length > 0) {
                    var $item = $(this).find('article.selected');
                    modifiers.push({
                        'product': $item.attr('data-product-id'),
                        'attribute_value': $item.attr('data-attribure-value-name'),
                        'price_extra': parseFloat($item.attr('data-attribure-price-extra'))
                    });
                }
            });
            modifiers = this.modifiers_list;
            return modifiers;
        }
    }
    ModifierProductPopup.template = 'ModifierProductPopup';
    Registries.Component.add(ModifierProductPopup);

    return {
        ModifierProductPopup,
    };
});