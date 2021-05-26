# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class ProductTemplateInhe(models.Model):
    _inherit = "product.template"

    cost_cofig_ids = fields.One2many("cost.configuration", "product_id", string="Cost")
    pro_lst_price = fields.Float('List Price')
    application = fields.Date(string='Date', default=fields.Date.today())

    price_config_ids = fields.One2many("price.configuration", "product_id", string="Price")
    price_cost_of_sale = fields.Float("Net cost of sales")
    price_application_date = fields.Date("Date", default=fields.Date.today())
    MAP_price = fields.Float("Price MAP")
    public_ref_price = fields.Float("Public Reference Price")
    presentation_uom_id = fields.Many2one('uom.uom','Presentation')
    
    def cal_discount(self, discount_price, D1, D2, D3, D4, D5):
        discount = 0
        list_price = discount_price
        if D1:
            discount += (list_price * D1) / 100
            list_price -= discount
        if D2:
            discount += (list_price * D2) / 100
            list_price -= discount
        if D3:
            discount += (list_price * D3) / 100
            list_price -= discount
        if D4:
            discount += (list_price * D4) / 100
            list_price -= discount
        if D5:
            discount += (list_price * D5) / 100
            list_price -= discount

        return discount

    def cal_product_list_cost(self):
        if self.cost_cofig_ids and self.pro_lst_price:
            discount_price = self.pro_lst_price
            for discount in self.cost_cofig_ids:
                if discount.distcount_type == 'sale':
                    discount_price = discount.cost = discount_price - self.cal_discount(self.pro_lst_price, discount.D1, discount.D2, discount.D3, discount.D4, discount.D5)
                    self.price_cost_of_sale = float(discount_price)
                elif discount.distcount_type == 'purchase':
                    discount_price = discount.cost = discount_price - self.cal_discount(discount_price, discount.D1, discount.D2, discount.D3, discount.D4, discount.D5)
#                     if self.seller_ids:
#                         for seller in self.seller_ids:
#                             seller.price = discount.cost
                            #seller.date = self.application
                elif discount.distcount_type == 'confidential':
                    discount_price = discount.cost = discount_price - self.cal_discount(discount_price, discount.D1, discount.D2, discount.D3, discount.D4, discount.D5)

    def set_purchase_vendor_price(self,product,date_update):
        cost_line_id = self.env['cost.history'].search([('product_id','=',product.id),('distcount_type','=','purchase'),('update','<=',date_update)],order='update desc',limit=1)
        if cost_line_id and self.seller_ids:
            for seller in self.seller_ids:
                seller.price = cost_line_id.cost
        
    def update_cost(self):
        if self.cost_cofig_ids and self.pro_lst_price:
            cost_history_obj = self.env['cost.history']
            for discount in self.cost_cofig_ids:
                cost_line_id = self.env['cost.history'].search([('product_id','=',self.id),('distcount_type','=',discount.distcount_type),('update','=',self.application)],limit=1) 
                data = {
                    'update': self.application,
                    'user_id': self.env.user.id,
                    'product_id': self.id,
                    'distcount_type': discount.distcount_type,
                    'D1': discount.D1,
                    'D2': discount.D2,
                    'D3': discount.D3,
                    'D4': discount.D4,
                    'D5': discount.D5,
                    'cost': discount.cost,
                }
                if cost_line_id:
                    cost_line_id.write(data)
                else:
                    cost_history_obj.create(data)
        today_date = datetime.today().date()
        self.set_purchase_vendor_price(self,today_date)
        
    def cal_product_list_price(self):
        if self.price_cost_of_sale and self.price_config_ids:
            sale_price = self.price_cost_of_sale
            first_scale_price = False
            for price in self.price_config_ids:
                if price.price_including_VAT:
                    if self.taxes_id:
                        tax_value = self.taxes_id.compute_all(price.price_including_VAT,handle_price_include=True)
                        total_included_price = tax_value.get("total_included", 0)
                        per = (total_included_price*100)/price.price_including_VAT
                        per = per - 100
                        tax_excluded_price  = price.price_including_VAT / ((per /100) + 1 )
                        price.price_before_VAT = tax_excluded_price
                        about_net = 0
                        if sale_price:
                            about_net = (price.price_before_VAT*100)/sale_price
                            about_net = about_net - 100
                        price.about_net = about_net  
                elif price.about_net:
                    amount = (sale_price * price.about_net) / 100
                    price.price_before_VAT = sale_price + amount
                    price_after_VAT = price.price_before_VAT
                    if self.taxes_id:
                        tax_value = self.taxes_id.compute_all(price_after_VAT)
                        price_after_VAT = tax_value.get("total_included", 0)
                    price.price_including_VAT = price_after_VAT



    def set_sale_price_pricelist(self,product,update_date):
        pricelist_item_obj = self.env['product.pricelist.item']
        for price in self.price_config_ids:
            price_line_ids = self.env['price.history'].search([('product_id','=',product.id),('scale_type','=',price.scale_type.id),('update','=',update_date)],order='update desc')
            for line in price_line_ids:
                pricelist_item_id = pricelist_item_obj.search([('uom_id','=',line.uom_id.id),('pricelist_id','=',price.scale_type.id),('applied_on','=','1_product'),('product_tmpl_id','=',product.id)],limit=1)
                if pricelist_item_id:
                    pricelist_item_id.fixed_price = line.price_before_VAT
        
        public_pricelist_id = self.env.ref('product.list0')
        if public_pricelist_id:
            price = public_pricelist_id.get_product_price(product,1,False,False,product.uom_id.id)
            product.list_price = price
            
    def update_price(self):
        if self.price_cost_of_sale and self.price_config_ids:
            price_history_obj = self.env['price.history']
            pricelist_item_obj = self.env['product.pricelist.item'] 
            for price in self.price_config_ids:
                presentation_uom_id = self.presentation_uom_id and self.presentation_uom_id.id or False
                
                price_line_id = self.env['price.history'].search([('uom_id','=',presentation_uom_id),('product_id','=',self.id),('scale_type','=',price.scale_type.id),('update','=',self.price_application_date)],limit=1)
                
                data = {
                    'update': self.price_application_date,
                    'user_id': self.env.user.id,
                    'product_id': self.id,
                    'scale_type': price.scale_type.id,
                    'about_net': price.about_net,
                    'price_before_VAT': price.price_before_VAT,
                    'price_including_VAT': price.price_including_VAT,
                    'uom_id':self.presentation_uom_id and self.presentation_uom_id.id or False,
                }
                if price_line_id:
                    price_line_id.write(data)
                else:
                    price_history_obj.create(data)

                #==== Create or Update Prices List Line
                pricelist_item_id = pricelist_item_obj.search([('uom_id','=',presentation_uom_id),('pricelist_id','=',price.scale_type.id),('applied_on','=','1_product'),('product_tmpl_id','=',self.id)],limit=1)
#                 if pricelist_item_id:
#                     pricelist_item_id.fixed_price = price.price_before_VAT
                if not pricelist_item_id:
                    price_data = {
                            'pricelist_id': price.scale_type.id,
                            'name': "Product: "+str(self.display_name),
                            'min_quantity': 1,
                            'fixed_price': price.price_before_VAT,
                            'applied_on' : '1_product',
                            'product_tmpl_id' : self.id,
                            'uom_id':self.presentation_uom_id and self.presentation_uom_id.id or False,
                        }
                    pricelist_item_obj.create(price_data)
        today_date = datetime.today().date()
        self.set_sale_price_pricelist(self,today_date)
    
    #==== Cron For Set the Price =======#
    def update_product_sale_purchase_price(self):
        tmp_ids = self.env['product.template'].search([])
        next_day_date = datetime.today().date()+timedelta(days=1)
        
        for tmp in tmp_ids:
            tmp.set_sale_price_pricelist(tmp,next_day_date)
            tmp.set_purchase_vendor_price(tmp,next_day_date)
                        
class CostConfiguration(models.Model):
    _name = "cost.configuration"
    _description = "Cost Configuration"
    _rec_name = "distcount_type"

    product_id = fields.Many2one('product.template', string="product")

    distcount_type = fields.Selection([('sale', 'Discount Sale'),
                                       ('purchase', 'Discount Purhcase'),
                                       ("confidential", "Discount Confidential")], string="Discount Type")
    D1 = fields.Float("D1")
    D2 = fields.Float("D2")
    D3 = fields.Float("D3")
    D4 = fields.Float("D4")
    D5 = fields.Float("D5")
    cost = fields.Float("Cost")


class PriceConfiguration(models.Model):
    _name = "price.configuration"
    _description = "Price Configuration"

    product_id = fields.Many2one('product.template', string="Product")
    scale_type = fields.Many2one("product.pricelist", string="Scale Type")
    about_net = fields.Float("About Net")
    price_before_VAT = fields.Float("Price Before VAT")
    price_including_VAT = fields.Float("Price Including VAT")

    @api.onchange('price_including_VAT')
    def onchange_price_including_VAT(self):
        price = self
        sale_price = price.product_id.price_cost_of_sale
        if price.price_including_VAT:
            if price.product_id.taxes_id:
                tax_value = price.product_id.taxes_id.compute_all(price.price_including_VAT,handle_price_include=True)
                total_included_price = tax_value.get("total_included", 0)
                per = (total_included_price*100)/price.price_including_VAT
                per = per - 100
                tax_excluded_price  = price.price_including_VAT / ((per /100) + 1 )
                price.price_before_VAT = tax_excluded_price
                about_net = 0
                if sale_price:
                    about_net = (price.price_before_VAT*100)/sale_price
                    about_net = about_net - 100
                price.about_net = about_net  

    @api.onchange('about_net')
    def onchange_about_net(self):
        price = self
        sale_price = price.product_id.price_cost_of_sale
        if price.about_net:
            amount = (sale_price * price.about_net) / 100
            price.price_before_VAT = sale_price + amount
            price_after_VAT = price.price_before_VAT
            if price.product_id.taxes_id:
                tax_value = price.product_id.taxes_id.compute_all(price_after_VAT)
                price_after_VAT = tax_value.get("total_included", 0)
            price.price_including_VAT = price_after_VAT
            
class CostHistory(models.Model):
    _inherit = "cost.configuration"
    _name = "cost.history"
    _description = "Cost History"
    _order = 'update'
    
    update = fields.Date("Date")
    user_id = fields.Many2one('res.users')

    def unlink(self):
        for rec in self:
            today_date = datetime.today().date()
            if rec.update and rec.update <= today_date:
                raise UserError(_('You can delete an entry which has only future dates'))
        return super(CostHistory, self).unlink()
    
class PriceHistory(models.Model):
    _inherit = "price.configuration"
    _name = "price.history"
    _description = "Price History"
    _order = 'update'
    
    update = fields.Date("Date")
    user_id = fields.Many2one('res.users')
    uom_id = fields.Many2one('uom.uom','Presentation')
    def unlink(self):
        for rec in self:
            today_date = datetime.today().date()
            if rec.update and rec.update <= today_date:
                raise UserError(_('You can delete an entry which has only future dates'))
        return super(PriceHistory, self).unlink()
