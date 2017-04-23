# -*- coding: utf-8 -*-
from openerp import models, fields, api

class MaplePackOperation(models.Model):
    _inherit = "stock.pack.operation"
    
    maple_weight = fields.Float(
        string = 'Maple Weight', 
        digits = 0,
        compute = '_compute_pack_ops_weight'
        )
        
    @api.one
    @api.depends('pack_lot_ids')
    def _compute_pack_ops_weight(self):
        
        weight = 0.
        if self.product_id.maple_container:
            for lot in self.pack_lot_ids:
                for quant in lot.lot_id.quant_ids:
                    weight += quant.maple_net_weight * lot.qty
#             if self.picking_id:
#                 related_op = self.picking_id.pack_operation_ids.filtered(lambda r: r.product_id.default_code == self.product_id.default_code[1:] )
#                 if not related_op:
#                     related_product = self.env['product.product'].search([('default_code','=',self.product_id.default_code[1:])])
#                     # faut créée un pack ops
#                     op_vals = {
#                         'date' : self.date,
#                         'product_id' : related_product.id,
#                         'location_dest_id' : self.location_dest_id.id,
#                         'picking_id' : self.picking_id.id,
#                         'qty_done' : weight
#                         }
#                     related_op = self.env['stock.pack.operation'].create(op_vals)
#                 else :
#                     related_op.write({
#                         'qty_done' : weight
#                     })

        self.maple_weight= weight



class MapleMove(models.Model):
    _inherit = "stock.move"
    
    maple_weight = fields.Float(
        string = 'Maple Weight', 
        digits = 0,
        compute = '_compute_move_weight'
        )
    
    @api.one
    @api.depends('active_move_lot_ids')
    def _compute_move_weight(self):
        weight = 0
        for lot in self.active_move_lot_ids:
            for quant in lot.lot_id.quant_ids:
                weight += quant.maple_net_weight * lot.quantity_done
        self.maple_weight= weight      
        
        
        
                
class MaplePackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    
    maple_weight = fields.Float(
        string = 'Maple Weight', 
        digits = 0,
        compute = '_compute_pack_ops_lot_weight'
        )
    
    @api.one
    @api.depends('lot_id')
    def _compute_pack_ops_lot_weight(self):
        weight = 0
        for quant in self.lot_id.quant_ids:
                weight += quant.maple_net_weight 
        self.maple_weight= weight        





class MaplePicking(models.Model):
    _inherit = "stock.picking"
    
    maple_weight = fields.Float(
        string = 'Maple Weight', 
        digits = 0,
        compute = '_compute_picking_weight'
        )
    
    @api.one
    @api.depends('pack_operation_product_ids')
    def _compute_picking_weight(self):
        weight = 0
        for pack in self.pack_operation_product_ids:
            for lot in pack.pack_lot_ids:
                for quant in lot.lot_id.quant_ids:
                    weight += quant.maple_net_weight * lot.qty
        self.maple_weight= weight