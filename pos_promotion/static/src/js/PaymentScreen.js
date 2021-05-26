odoo.define('PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const RetailPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }

            mounted() {
                super.mounted();
                this.env.pos.automaticSetCoupon();
            }

        }
    Registries.Component.extend(PaymentScreen, RetailPaymentScreen);

    return RetailPaymentScreen;
});
