from odoo import models, fields, api


class ProductPresentTemp(models.Model):

    _inherit = "product.template"

    uom_ids = fields.One2many("product.uom", "product_id", string="Unit of measure")
    pos_custom_price = fields.Float("POS Custom Price",copy=False)

    def get_uom_prices(self,pricelist):
        records = []
        visitor = self.env['website.visitor']._get_visitor_from_request()
        uom_selected = self.env['price.uom.user'].search(
            [('visitor_id', '=', visitor.id), ('product_tmpl_id', '=', self.id)], limit=1)
        other_uom = self.env['uom.uom'].sudo().search([('category_id','=',self.uom_id.category_id.id)])
        
        for uom in other_uom:
            price = self.list_price
            current_uom = self.uom_id
            if uom_selected:
                current_uom = uom_selected.uom_id_selected
            if pricelist:
                price = pricelist.sudo().with_context(uom=uom.id).get_product_price(self,1,False,False,uom.id)
            records.append((uom.id, uom.id, uom.name, price,
                            "selected" if uom.id == current_uom.id else False))

        return records
        
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        res = super(ProductPresentTemp,self)._get_combination_info(combination=combination,product_id=product_id,add_qty=add_qty,pricelist=pricelist,parent_combination=parent_combination,only_template=only_template)
        
        if not pricelist and self.env.context and self.env.context.get('website_id',False):
            website_id = self.env['website'].sudo().browse(self.env.context.get('website_id',False))
            
            if website_id and website_id.pricelist_id:
                pricelist = website_id.pricelist_id

        visitor = self.env['website.visitor']._get_visitor_from_request()
        uom_selected = self.env['price.uom.user'].search(
            [('visitor_id', '=', visitor.id), ('product_tmpl_id', '=', self.id)], limit=1)
        
        if res.get('product_id',False) and pricelist:
            product = self.env['product.product'].browse(res.get('product_id',False))
            uom_id = product.uom_id
            if uom_selected.uom_id_selected:
                uom_id = uom_selected.uom_id_selected
            price = pricelist.with_context(uom=uom_id.id).get_product_price(product,1,False,False,uom_id.id)   
            res.update({'price':price,'list_price':price})
                     
        elif res.get('product_template_id',False) and pricelist:
            product_template_id = self.env['product.template'].browse(res.get('product_template_id',False))
            uom_id = product_template_id.uom_id
            if uom_selected.uom_id_selected and not only_template:
                uom_id = uom_selected.uom_id_selected
            
            price = pricelist.with_context(uom=uom_id.id).get_product_price(product_template_id,1,False,False,uom_id.id)   
            res.update({'price':price,'list_price':price})         
        
        return res
    
class ProductUom(models.Model):

    _name = "product.uom"
    _description = "Product Unit of measure"

    product_id = fields.Many2one("product.template", string="product")
    uom_id = fields.Many2one("uom.uom", string="Units of measure")
    bar_code = fields.Char(string="Barcode")


class PricelistItemtemp(models.Model):

    _inherit = "product.pricelist.item"

    uom_id = fields.Many2one("uom.uom", string="Pricelist UOM")


class PricelistUom(models.Model):

    _inherit = "product.pricelist"

    uom_id = fields.Many2one("uom.uom", string="Pricelist UOM")

    def get_product_price_for_pos_uom(self, product, quantity, partner, date=False, uom_id=False):
        product = self.env['product.product'].browse(product)
        price = self.with_context(uom=uom_id).get_product_price(product,quantity,partner,date,uom_id)
        if product:
            product.pos_custom_price = price
        return price
    
    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        item_ids = []
        if uom_id:
            self.ensure_one()
            # Load all rules
            self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)
                    AND (item.uom_id=%s)
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date,uom_id))
            # NOTE: if you change `order by` on that query, make sure it matches
            # _order from model to avoid inconstencies and undeterministic issues.
    
            item_ids = [x[0] for x in self.env.cr.fetchall()]
            #return self.env['product.pricelist.item'].browse(item_ids)
            
        else:

            self.ensure_one()
            # Load all rules
            self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
            # NOTE: if you change `order by` on that query, make sure it matches
            # _order from model to avoid inconstencies and undeterministic issues.
    
            item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)

        
    