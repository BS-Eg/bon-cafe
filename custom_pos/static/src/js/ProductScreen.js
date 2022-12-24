odoo.define('custom_pos.custon_ProductScreen', function(require) {
    'use strict';

    const { Gui } = require('point_of_sale.Gui');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosRewardProductScreen = ProductScreen =>
        class extends ProductScreen {
            _onClickPay() {
                var spent_points = this.env.pos.get_order().get_spent_points()
                if((spent_points > 100) || (spent_points < 15 && spent_points > 0)) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Empty Order'),
                        body: this.env._t(
                            'The Loyalty point should be greater than 15 and less than 100.'
                        ),
                    });
                    return false;
                };
                this.showScreen('PaymentScreen');
            }
        };

    Registries.Component.extend(ProductScreen, PosRewardProductScreen);

    return ProductScreen;
});
