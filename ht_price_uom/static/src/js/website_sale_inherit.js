odoo.define("ht_price_uom.WebsiteSale", function(require){

    var publicWidget = require('web.public.widget');
    const wUtils = require('website.utils');

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
            'change select.js_uom_change': '_onChangeUOM',
        }),

        _onChangeUOM: function(event){
            var self = this;
            var option = $(event.currentTarget).children("option:selected");
            var $form = $(event.currentTarget).parents('form');
            var product_id = $form.find('.product_template_id').val();
            var data = option.data();
            var value = option.val();
            $(event.currentTarget).parent().find("input.price_uom_info").val(value);
            if (value) {
                this._rpc({
                    route: '/product/uom/update',
                    params: {
                        'product_id': product_id,
                        'uom_id': parseFloat(value),
                    }
                }).then(function(){
                    var $parent;
                    if ($(event.currentTarget).closest('.oe_optional_products_modal').length > 0){
                        $parent = $(event.currentTarget).closest('.oe_optional_products_modal');
                    } else if ($(event.currentTarget).closest('form').length > 0){
                        $parent = $(event.currentTarget).closest('form');
                    }  else {
                        $parent = $(event.currentTarget).closest('.o_product_configurator');
                    }

                    self.triggerVariantChange($parent);
                });
            }

        },
    });
});
