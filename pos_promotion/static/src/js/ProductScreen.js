odoo.define('ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const core = require('web.core');

    const RetailProductScreen = (ProductScreen) =>
        class extends ProductScreen {

            async _barcodeErrorAction(code) {
                const selectedOrder = this.env.pos.get_order()
                if (selectedOrder) {
                    const appliedCoupon = this.env.pos.getInformationCouponPromotionOfCode(code.code);
                    if (!appliedCoupon) {
                        super._barcodeErrorAction(code)
                    }
                } else {
                    super._barcodeErrorAction(code)
                }

            }

        }
    Registries.Component.extend(ProductScreen, RetailProductScreen);

    return ProductScreen;
});
