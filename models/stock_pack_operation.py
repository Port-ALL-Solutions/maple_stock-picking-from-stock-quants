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
        weight = 0 
        for lot in self.pack_lot_ids:
            for quant in lot.lot_id.quant_ids:
                weight += quant.maple_net_weight * lot.qty
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