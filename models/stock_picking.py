# -*- coding: utf-8 -*-
from openerp import models, fields, api

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class MaplePicking(models.Model):
    _inherit = 'stock.picking'

#    @api.multi
#    def do_new_transfer(self):
#        super(MaplePicking,self).do_new_transfer()
        
#        if self.state == 'done':
#            print 'hello'
        