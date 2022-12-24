odoo.define('pizza_modifiers.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const PizzaModifiersOrderReceipt = OrderReceipt =>
        class extends OrderReceipt {
            constructor() {
                super(...arguments);
            }

        };

    Registries.Component.extend(OrderReceipt, PizzaModifiersOrderReceipt);

    return OrderReceipt;
});