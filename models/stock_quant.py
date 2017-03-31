# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date


class stockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant']
    
    
    def action_create_picking_from_quants2(self, cr, uid, ids, context=None):
        if context is None: context = {}
        # generic error checking
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
                
        quants = self.env['stock.quant'].browse(ids)
        quants_locations = []
        quants_owner = []
        quants_origin= []
        quants_buyer = []
        for quant in quants:
            if quant.location_id not in quants_locations:
                quants_locations.append(quant.location_id)
            if quant.owner_id not in quants_owner:                
                quants_owner.append(quant.owner_id)
                if quant.owner_id.state_id.code not in quants_origin:
                    quants_origin.append(quant.owner_id.state_id.code)
            if quant.buyer not in quants_buyer:
                quants_buyer.append(quant.buyer)   

#        if len(quants_locations) == 1:
            

        wizard_obj = self.env['stock.picking_from_quants']
           
        vals = { 'location_source_id': quants_locations[0].id }        
           
        wizard_id = wizard_obj.create(vals)

        wizard_line_obj = self.env['stock.picking_from_quants.lines']
    
        for quant in quants:
            vals_line = {
                'picking_from_quant_id': wizard_id.id,
                'quant_id': quant.id,
                }
            wizard_line_id = wizard_line_obj.create(vals_line)

        return {
            'name': 'Picking from Quants Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking_from_quants',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
