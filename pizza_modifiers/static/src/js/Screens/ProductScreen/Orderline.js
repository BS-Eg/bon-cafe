odoo.define('pizza_modifiers.Orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PizzaModifiersOrderline = Orderline =>
        class extends Orderline {
            /**
             * @override
             */
            get addedClasses() {
                const res = super.addedClasses;
                Object.assign(res, {
                    modifier: this.props.line.parent_line_id,
                });
                return res;
            }
        };

    Registries.Component.extend(Orderline, PizzaModifiersOrderline);

    return Orderline;
});
