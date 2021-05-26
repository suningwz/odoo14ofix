    # -*- coding: utf-8 -*-
{
    "name": "POS Promotions Coupons",
    "version": "1.0.1",
    "price": "200",
    "live_test_url": "http://posodoo.com",
    "category": "Point of Sale",
    "author": "TL Technology",
    "sequence": 0,
    "summary": """
    POS Promotions and Sale Promotion/Coupon \n
    Your Business can reuse Promotion/Coupon Program of Odoo Original and use on POS like sale module
    """,
    "description": """
    POS Promotions and Sale Promotion/Coupon \n
    Your Business can reuse Promotion/Coupon Program of Odoo Original and use on POS like sale module
    """,
    "depends": ["point_of_sale", "sale_coupon", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "import/template.xml",
        "views/PosConfig.xml",
        "views/PosOrder.xml",
        "views/Coupon.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "website": "http://posodoo.com",
    'live_test_url': "http://posodoo.com/saas/public/1",
    "application": True,
    "images": ["static/description/icon.png"],
    "support": "thanhchatvn@gmail.com",
    "currency": "EUR",
    "license": "OPL-1"
}
