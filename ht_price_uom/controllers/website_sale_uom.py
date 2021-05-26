from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherited(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        pricelist = False
        if not pricelist and request.env.context and request.env.context.get('website_id',False):
            website_id = request.env['website'].sudo().browse(request.env.context.get('website_id',False))
            
            if website_id and website_id.pricelist_id:
                pricelist = website_id.pricelist_id
                        
        values = super(WebsiteSaleInherited, self)._prepare_product_values(product, category, search, **kwargs)
        
        values['uom_attributes'] = product.sudo().get_uom_prices(pricelist)
        return values

    @http.route(['/product/uom/update'], type='json', auth="public", methods=['POST'], website=True)
    def uom_update(self, product_id, uom_id, **kw):
        visitor = request.env['website.visitor']._get_visitor_from_request()
        record = request.env['price.uom.user'].search([('product_tmpl_id', '=', int(product_id)), ('visitor_id', '=', visitor.id)])
        if record:
            record.write({'uom_id_selected': uom_id})
        else:
            request.env['price.uom.user'].create({
                'product_tmpl_id': product_id,
                'uom_id_selected': uom_id,
                'visitor_id': visitor.id,
            })
