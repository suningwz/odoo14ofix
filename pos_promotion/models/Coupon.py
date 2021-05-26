# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import ast


class CouponProgram(models.Model):
    _inherit = "coupon.program"

    pos_order_count = fields.Integer(compute='_compute_pos_order_count')

    def _compute_pos_order_count(self):
        for program in self:
            program.pos_order_count = len(self.env['pos.order.line'].search(
                ['|', ('coupon_program_id', '=', program.id), ('coupon_id.program_id', '=', program.id)]))

    def action_view_pos_orders(self):
        self.ensure_one()
        orders = self.env['pos.order.line'].search(['|', ('coupon_program_id', '=', self.id), ('coupon_id.program_id', '=', self.id)]).mapped(
            'order_id')
        return {
            'name': _('POS Orders'),
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', orders.ids)],
            'context': dict(self._context, create=False)
        }


class Coupon(models.Model):
    _inherit = 'coupon.coupon'

    pos_order_id = fields.Many2one('pos.order', 'Pos Order', readonly=1)


class CouponRule(models.Model):
    _inherit = 'coupon.rule'

    applied_partner_ids = fields.Many2many('res.partner', compute='_getAppliedPartnerIds')
    applied_product_ids = fields.Many2many('product.product', compute='_getAppliedProductIds')

    def _getAppliedPartnerIds(self):
        for rule in self:
            if rule.rule_partners_domain:
                rule.applied_partner_ids = [
                    [6, 0, [p.id for p in
                            self.env['res.partner'].sudo().search(ast.literal_eval(rule.rule_partners_domain))]]]
            else:
                rule.applied_partner_ids = [
                    [6, 0, [p.id for p in self.env['res.partner'].sudo().search([])]]]

    def _getAppliedProductIds(self):
        for rule in self:
            if rule.rule_products_domain:
                rule.applied_product_ids = [
                    [6, 0, [p.id for p in
                            self.env['product.product'].sudo().search(ast.literal_eval(rule.rule_products_domain))]]]
            else:
                rule.applied_product_ids = [
                    [6, 0, [p.id for p in self.env['product.product'].sudo().search([])]]]
