odoo.define('gs_pos_loyalty.AbstractReceiptScreen', function (require) {
    'use strict';

    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const GSAbstractReceiptScreen = GSAbstractReceiptScreen =>
        class  extends AbstractReceiptScreen {
        constructor() {
            super(...arguments);
        }

        async _printWeb() {
            console.log('*****')
            try {
                 setTimeout(function() {
                    window.print();
                   // newWindow.close();
                }, 500);
               // window.print();
                return true;
            } catch (err) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Printing is not supported on some browsers'),
                    body: this.env._t(
                        'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                    ),
                });
                return false;
            }
        }
    }

    Registries.Component.extend(AbstractReceiptScreen, GSAbstractReceiptScreen);

    return GSAbstractReceiptScreen;
});
