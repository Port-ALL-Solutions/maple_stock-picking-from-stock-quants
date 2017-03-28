# -*- coding: utf-8 -*-
from openerp import models, fields, api

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class stockPickingType(models.Model):
    _name = 'stock.picking.type'
    _inherit = 'stock.picking.type'

    single_origin = fields.Boolean(
        string='One origin',
        help='If check, this type of picking allow only from same origin. ',
        default=False
        )    
