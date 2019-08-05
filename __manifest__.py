# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'TENDER',
    'version': '1.1',
    'summary': 'TENDER',
    'description': "TENDER",
    'website': '',
    'depends': ['project','product','mail','base'],
    'category': 'sale',
    'sequence': 200,
    'data': [
       'views/tender.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}