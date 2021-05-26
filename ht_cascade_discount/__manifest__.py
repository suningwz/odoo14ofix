# -*- coding: utf-8 -*-

##############################################################################
#
#    Harhu Technologies Pvt. Ltd.
#    Copyright (C) 2019-Today Harhu Technologies Pvt. Ltd.(<http://www.harhu.com>).
#    Author: Harhu Technologies Pvt. Ltd. (<http://www.harhu.com>) Contact: <hello@harhu.com>
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Sale Purchase cascade discount',
    'summary': 'Sale & Purchase cascade discount',
    'version': '14.0.0.1.0',
    'category': 'Tools',
    'author': 'Harhu Technologies Pvt. Ltd.',
    'maintainer': 'Harhu Technologies Pvt. Ltd.',
    'contributors': ['Anil Kesariya <anil.r.kesariya@gmail.com>'],
    'website': 'http://www.harhu.com',
    'depends': ['sale_management', 'purchase','sale_purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/cost_configuration.xml',
    ],
    'installable': True,
    'auto_install': False,
}
