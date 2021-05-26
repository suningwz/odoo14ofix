# -*- coding: utf-8 -*-
# from odoo import http


# class MmOfix(http.Controller):
#     @http.route('/mm_ofix/mm_ofix/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mm_ofix/mm_ofix/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mm_ofix.listing', {
#             'root': '/mm_ofix/mm_ofix',
#             'objects': http.request.env['mm_ofix.mm_ofix'].search([]),
#         })

#     @http.route('/mm_ofix/mm_ofix/objects/<model("mm_ofix.mm_ofix"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mm_ofix.object', {
#             'object': obj
#         })
