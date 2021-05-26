odoo.define('ht_price_uom.multi_uom', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var _super_orderline = models.Orderline.prototype;

/*==============================================*/

	models.load_fields("product.product", ["pos_custom_price"]);
	models.Product = models.Product.extend({

	get_price: function(pricelist, quantity, price_extra){
		var self = this;
		var date = moment().startOf('day');

		// In case of nested pricelists, it is necessary that all pricelists are made available in
		// the POS. Display a basic alert to the user in this case.
		if (pricelist === undefined) {
		    alert(_t(
		        'An error occurred when loading product prices. ' +
		        'Make sure all pricelists are available in the POS.'
		    ));
		}

		
		var def;
		def= rpc.query({
					'model': 'product.pricelist',
					'method': 'get_product_price_for_pos_uom',
					'args': [pricelist.id,self.id,quantity,false,false,self.uom_id[0]],
					'kwargs': {context: {}},
			    	}).then(function(result) {
					 return result;
	  		});
		       
		var price = self.pos_custom_price;

		def= rpc.query({
					'model': 'product.pricelist',
					'method': 'get_product_price_for_pos_uom',
					'args': [pricelist.id,self.id,quantity,false,false,self.uom_id[0]],
					'kwargs': {context: {}},
			    	}).then(function(result) {
					 return result;
	  		});
		return price;
	    },
		
	});
/*=============================================*/
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.uom_id = this.product.get_unit();
        },

        export_as_JSON: function() {
            var result = _super_orderline.export_as_JSON.call(this);
            result.uom_id = this.uom_id;
            return result;
        },
        get_custom_unit: function(){
            return this.uom_id;
        },
        find_reference_unit_price: function(product, product_uom){
            if(product_uom.uom_type == 'reference'){
                return product.lst_price;
            }
            else if(product_uom.uom_type == 'smaller'){
               return (product.lst_price * product_uom.factor);
            }
            else if(product_uom.uom_type == 'bigger'){
               return (product.lst_price / product_uom.factor_inv);
            }
        },
        get_latest_price: function(uom, product, ref_price, product_uom, uom_list){
            var ref_unit = null;
            for (var i in uom_list){
                if(uom_list[i].item.uom_type == 'reference'){
                    ref_unit = uom_list[i];
                    break;
                }
            }
            if(ref_unit){
                if(uom.uom_type == 'bigger'){
                    return (ref_price * uom.factor_inv);
                }
                else if(uom.uom_type == 'smaller'){
                    return (ref_price / uom.factor);
                }
                else if(uom.uom_type == 'reference'){
                    return ref_price;
                }
            }
            return product.lst_price;
        },
        export_for_printing: function() {
            var line = _super_orderline.export_for_printing.apply(this,arguments);
            line.unit_name = this.get_custom_unit().name;
            return line;
        },
    });

    class PosCustomUomButton extends PosComponent {
        async onClick() {
            const order = this.env.pos.get_order();
            if (order) {
                if (order.selected_orderline) {
                    const PosUomList = []
                    const order_line = order.selected_orderline
                    const product = order_line.get_product()
                    for (let unit of this.env.pos.units) {
                        if (order_line.uom_id.category_id[0] == unit.category_id[0]){
                            PosUomList.push({
                                id: unit.id,
                                label: unit.name,
                                item: unit,
                            });
                        }
                    }
                    const { confirmed, payload: selectedUomId } = await this.showPopup(
                        'SelectionPopup',
                        {
                            title: 'Select UOM',
                            list: PosUomList,
                        }
                    );
                    if (confirmed) {

                        const product_uom = order_line.get_unit();
			var uom_price = 0;
                        //const ref_price = order_line.find_reference_unit_price(product, product_uom);
		    	uom_price= rpc.query({
				'model': 'product.pricelist',
				'method': 'get_product_price_for_pos_uom',
				'args': [order_line.order.pricelist.id,product.id,1,false,false,selectedUomId.id],
				'kwargs': {context: {}},
		    	}).then(function(result) {
				//uom_price =  result;
				const latest_price = result
				//const latest_price = order_line.get_latest_price(selectedUomId, product, result, product_uom, PosUomList)		

                        	order_line.uom_id = selectedUomId;
                       	 	order_line.set_unit_price(latest_price);
                        	order_line.price = latest_price;

				//return result;
  			});
			//var ref_price = 100;
			
			//const latest_price = order_line.get_latest_price(selectedUomId, product, ref_price, product_uom, PosUomList)		

                        //order_line.uom_id = selectedUomId;
                        //order_line.set_unit_price(latest_price);
                        //order_line.price = latest_price;
                    }
                }
            }

        }
    }
/*
    PosCustomUomButton.template = 'PosCustomUomButton';
    ProductScreen.addControlButton({
        component: PosCustomUomButton,
        condition: function () {
            return this.env.pos.config.is_multi_uom_shown;
        },
    });
    Registries.Component.add(PosCustomUomButton);

    return PosCustomUomButton;
*/

    PosCustomUomButton.template = 'PosCustomUomButton';
    ProductScreen.addControlButton({
		component: PosCustomUomButton,
		condition: function () {
		    return true;
		},
		position: ['before', 'SetFiscalPositionButton'],

	    });

    Registries.Component.add(PosCustomUomButton);
    return PosCustomUomButton;

});
