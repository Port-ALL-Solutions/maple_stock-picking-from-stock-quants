# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Stock Picking from stock quant',
    'category': '',
    'version': '1.0',
    'author': "Benoit Vézina & Pierre Dalpé pour Portall",
    'website': "portall.ca",
    'summary': 'Adding and action to create picking from stock_quant',
    'description':
        """
This module add the actions "create picking" and "Add to picking".
================================================================================================

Add action create_picking.
Add action add_to_picking.
        """,
    'depends': [
        'maple',
    ],
    'data': [
        "wizard/stock_picking_from_stock_quants.xml"
    ],
    'qweb': [
#        "static/src/xml/*.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

