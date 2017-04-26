# -*- coding: utf-8 -*-
from openerp import models, fields, api

# def adjust_picking(picking, src = None):
#     if not src:
#         src = picking
#     
#     barel_pack_ops = src.pack_operation_ids.filtered(lambda ops: ops.product_id.maple_container)
#     maple_pack_ops = src.pack_operation_ids.filtered(lambda ops: not ops.product_id.maple_container)
#     barel_products = barel_pack_ops.mapped('product_id')      
#      
#     for barel_product in barel_products:
# 
#         barel_prod_ops = barel_pack_ops.filtered(lambda ops: ops.product_id == barel_product)
#         maple_weight = 0 
# 
#         for barel_prod_op in barel_prod_ops:
#             maple_weight += barel_prod_op.maple_weight
#       
#         maple_prod_op = maple_pack_ops.filtered(lambda ops: ops.product_id.default_code == barel_product.default_code[1:])
# 
#         maple_prod = picking.env['product.product'].search([('default_code', '=', barel_product.default_code[1:])])
# 
#         if not maple_prod_op:
#             
#             pack_ops_vals = {   'picking_id':picking.id,
#                                 'product_id':maple_prod.id,
#                                 'date':barel_prod_op.date,
#                                 'location_dest_id':barel_prod_op.location_dest_id.id,
#                                 'location_id':barel_prod_op.location_id.id,
#                                 'product_qty':maple_weight,
#                                 'ordered_qty':maple_weight,
#                                 'qty_done':maple_weight,
#                                 'product_uom_id':maple_prod.uom_id.id,
#                             }
#             
#             picking.env['stock.pack.operation'].create(pack_ops_vals)
#                       
#         else :
#             maple_prod_op.write({   'qty_done':maple_weight,
#                                     'product_qty':maple_weight,
#                                     'ordered_qty':maple_weight
#                                 })
#                              
# #                 pack_ops_vals['location_dest_id']=  picking.location_dest_id.id
# #                 pack_ops_vals['location_id'] = picking.location_id.id
# #                 picking.env['stock.pack.operation'].create(pack_ops_vals)

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class MaplePicking(models.Model):
    _inherit = 'stock.picking'

    def adjust_picking(self):
       
        barel_pack_ops = self.pack_operation_ids.filtered(lambda ops: ops.product_id.maple_container)
        maple_pack_ops = self.pack_operation_ids.filtered(lambda ops: not ops.product_id.maple_container)
        barel_products = barel_pack_ops.mapped('product_id')      
         
        for barel_product in barel_products:
    
            barel_prod_ops = barel_pack_ops.filtered(lambda ops: ops.product_id == barel_product)
            maple_weight = 0 
    
            for barel_prod_op in barel_prod_ops:
                maple_weight += barel_prod_op.maple_weight
          
            maple_prod_op = maple_pack_ops.filtered(lambda ops: ops.product_id.default_code == barel_product.default_code[1:])
    
            maple_prod = self.env['product.product'].search([('default_code', '=', barel_product.default_code[1:])])
    
            if not maple_prod_op:
                
                pack_ops_vals = {   'picking_id':self.id,
                                    'product_id':maple_prod.id,
                                    'date':barel_prod_op.date,
                                    'location_dest_id':barel_prod_op.location_dest_id.id,
                                    'location_id':barel_prod_op.location_id.id,
                                    'product_qty':maple_weight,
                                    'ordered_qty':maple_weight,
                                    'qty_done':maple_weight,
                                    'product_uom_id':maple_prod.uom_id.id,
                                }
                
                self.env['stock.pack.operation'].create(pack_ops_vals)
                          
            else :
                maple_prod_op.write({   'qty_done':maple_weight,
                                        'product_qty':maple_weight,
                                        'ordered_qty':maple_weight
                                    })
                                 
    #                 pack_ops_vals['location_dest_id']=  picking.location_dest_id.id
    #                 pack_ops_vals['location_id'] = picking.location_id.id
    #                 picking.env['stock.pack.operation'].create(pack_ops_vals)


    def adjust_child_picking(self):
        child_picking = self.move_lines[0].move_dest_id.picking_id
        
        for from_pack_op in self.pack_operation_ids:
            to_pack_op = child_picking.pack_operation_ids.filtered(lambda o: o.product_id == from_pack_op.product_id)
            if to_pack_op:
                to_pack_op.write({  'product_qty':from_pack_op.product_qty,
                                    'ordered_qty':from_pack_op.ordered_qty
                    })
            else:
                pack_ops_vals = {   'picking_id':child_picking.id,
                                    'product_id':from_pack_op.product_id.id,
                                    'date':from_pack_op.date,
                                    'location_dest_id':from_pack_op.location_dest_id.id,
                                    'location_id':from_pack_op.location_id.id,
                                    'product_qty':from_pack_op.product_qty,
                                    'ordered_qty':from_pack_op.ordered_qty,
#                                    'qty_done':from_pack_op.qty_done,
                                    'product_uom_id':from_pack_op.product_id.uom_id.id,
                                }
                
                to_pack_op = self.env['stock.pack.operation'].create(pack_ops_vals)
            for from_pack_lot in from_pack_op.pack_lot_ids:
                to_pack_lot = to_pack_op.pack_lot_ids.filtered(lambda pl: pl.lot_id == from_pack_lot.lot_id)
                if not to_pack_lot:
                    pack_ops_lot_vals = {   'operation_id':to_pack_op.id,
#                                            'qty':from_pack_op.product_id.id,
                                            'lot_id':from_pack_lot.lot_id.id,
                                            'qty_todo':from_pack_lot.qty_todo,                                            
                                            #qty_done':from_pack_op.qty_done,
                                        }
                
                    self.env['stock.pack.operation.lot'].create(pack_ops_lot_vals)
                
 
    def adjust_move(self, product, qty):
        prod_move = self.move_lines.filtered(lambda m: m.product_id == product.id)
        if not prod_move:
            prod_move = self.move_lines[0].copy()
            prod_move.write ({  'product_id' : product.id,
                                'product_tmpl_id': product.product_tmpl_id,
                                'product_uom': product.uom_id.id
                            })
            
        prod_move.remaining_qty = qty
        prod_move.product_uom_qty = qty
        prod_move.ordered_qty = qty
        prod_move.save()
            


    def do_invoice(self):
        for pick in self:
            barel_pack_ops = pick.pack_operation_ids.filtered(lambda ops: ops.product_id.maple_container)


    @api.multi
    def do_transfer(self):
        
        # fix picking
        super(MaplePicking,self).do_transfer()
        if self.move_lines[0].move_dest_id.picking_id: #and self.picking_type_id.id in [3,4,9,10,15,16,21,22,27,28]:
            self.adjust_child_picking()
        return

#        self.do_invoice()

    @api.multi
    def do_new_transfer(self):
#        if self.picking_type_id.id in [3,4,9,10,15,16,21,22,27,28]:
        self.adjust_picking()
        return super(MaplePicking,self).do_new_transfer()

    def _create_extra_moves(self):
        extra_move = super(MaplePicking,self)._create_extra_moves()
        for move in extra_move:
            move._push_apply()
        return extra_move


#         