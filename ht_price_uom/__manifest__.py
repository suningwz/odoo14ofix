{
    'name': 'Price Units of Measure',
    'summary': 'Price Units of Measure Details',
    'version': '14.0.0.1',
    'depends': ['sale_management', 'website_sale', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_detail_page_template.xml',
        'views/product_presentations_view.xml',
        'views/pricelist_uom_view.xml',
        'views/assets.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
    ],
    'qweb': [
            'static/src/xml/multi_uom.xml',
            ],
}
