# -*- coding: utf-8 -*-
from openerp import models, fields, api

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class stockPickingType(models.Model):
    _name = 'stock.picking.type'
    _inherit = 'stock.picking.type'

    single_origin = fields.Boolean(
        string='One origin',
        help='If check, this type of picking allow only from same origin (partner). ',
        default=False
        )    

    single_product = fields.Boolean(
        string='One Product',
        help='If check, this type of picking will not allow mixed product. ',
        default=False
        )    

    fixed_origin = fields.Boolean(
        string='Fixed origin',
        help='If check, this type of picking will not allow you to change the origin. ',
        default=False
        )    

    fixed_destination = fields.Boolean(
        string='Fixed destination',
        help='If check, this type of picking will not allow you to change the destination. ',
        default=False
        )    
