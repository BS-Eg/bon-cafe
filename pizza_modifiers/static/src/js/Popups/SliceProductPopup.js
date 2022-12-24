odoo.define('pizza_modifiers.SliceProductPopup', function(require) {
    'use strict';

    const { useState, useSubEnv } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class SliceProductPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

        AddRemoveSlices(event) {
            $(event.currentTarget).toggleClass('selected');
        }

        getPayload() {
            var $el = $(event.currentTarget).parents('.slice-product-popup');

            var slide_products = [];
            $.each($el.find('.product-list article.selected'), function() {
                var $item = $(this).find('article.selected');
                slide_products.push({
                    'product': $(this).attr('data-product-id'),
                    'attribute_value': $(this).attr('data-attribure-value-name'),
                    'price_extra': parseFloat($(this).attr('data-attribure-price-extra'))
                });
            });
            return slide_products;
        }
    }
    SliceProductPopup.template = 'SliceProductPopup';
    Registries.Component.add(SliceProductPopup);
    return {
        SliceProductPopup,
    };
});