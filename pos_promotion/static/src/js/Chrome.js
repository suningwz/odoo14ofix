odoo.define('pos_bus.Chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const RetailChrome = (Chrome) =>
        class extends Chrome {
            constructor() {
                super(...arguments);
            }

            async start() {
                await super.start()
                this.env.pos.chrome = this
            }
        }
    Registries.Component.extend(Chrome, RetailChrome);

    return RetailChrome;
});
