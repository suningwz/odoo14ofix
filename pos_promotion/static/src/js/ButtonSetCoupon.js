odoo.define('ButtonSetCoupon', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class ButtonSetCoupon extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            const selectedOrder = this.env.pos.get_order()
            if (selectedOrder.orderlines.length == 0) {
                return this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Your cart is blank. Please finish order products and use Promotion/Coupon Code')
                })
            }
            let {confirmed, payload: code} = await this.showPopup('TextInputPopup', {
                title: this.env._t('Promotion/Coupon Code ?'),
            })
            if (confirmed) {
                this.env.pos.getInformationCouponPromotionOfCode(code)
            }
        }
    }

    ButtonSetCoupon.template = 'ButtonSetCoupon';

    ProductScreen.addControlButton({
        component: ButtonSetCoupon,
        condition: function () {
            return this.env.pos.couponPrograms && this.env.pos.couponPrograms.length > 0;
        },
    });

    Registries.Component.add(ButtonSetCoupon);

    return ButtonSetCoupon;
});
