# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        sale_order_line = self.env['sale.order.line'].search([('id', '=', values['line_id'])])
        visitor = self.env['website.visitor']._get_visitor_from_request()
        if sale_order_line:
            uom_selected = self.env['price.uom.user'].search(
                [('visitor_id', '=', visitor.id),
                 ('product_tmpl_id', '=', sale_order_line.product_id.product_tmpl_id.id)], limit=1)
            
            if uom_selected.uom_id_selected :
                sale_order_line.write({'product_uom': uom_selected.uom_id_selected.id})
                
                if sale_order_line.order_id and sale_order_line.order_id.pricelist_id:
                     price = sale_order_line.order_id.pricelist_id.sudo().with_context(uom=uom_selected.uom_id_selected.id).get_product_price(sale_order_line.product_id,1,False,False,uom_selected.uom_id_selected.id)
                     sale_order_line.write({'price_unit': price})
        return values
