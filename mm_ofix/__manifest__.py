# -*- coding: utf-8 -*-
{
    'name': "mm_ofix",

    'summary': """
        Módulo Mit-Mut para personalizaciones Ofix""",

    'description': """
       Módulo Mit-Mut para personalizaciones Ofix
    """,

    'author': "Mit-Mut",
    'website': "https://www.mit-mut.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Mit-Mut',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','sale_management', 'stock', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/invoice.xml',
        'views/view_pos.xml',
        'views/inherit_view_purchase.xml',
        'views/inherit_view_partner.xml',
        'views/inherit_view_invoice.xml',
        'data/automated_actions.xml',
    ],
}
