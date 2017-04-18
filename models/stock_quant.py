# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class stockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant']
    
    def action_create_picking_from_quants(self, cr, uid, ids, context=None):
        if context is None: context = {}
        # generic error checking
        if not ids: return False

        if not isinstance(ids, list): ids = [ids]
                
        quants = self.env['stock.quant'].browse(ids)
        
        quants_locations = quants.mapped('location_id')
        quants_owner = quants.mapped('owner_id')
        quants_origin = quants.mapped('owner_id.state_id')
        quants_buyer = quants.mapped('buyer')
        
#         quants_locations = []
#         quants_owner = []
#         quants_origin= []
#         quants_buyer = []
#         
#         for quant in quants:
#             if quant.location_id not in quants_locations:
#                 quants_locations.append(quant.location_id)
#             if quant.owner_id not in quants_owner:                
#                 quants_owner.append(quant.owner_id)
#                 if quant.owner_id.state_id.code not in quants_origin:
#                     quants_origin.append(quant.owner_id.state_id.code)
#             if quant.buyer not in quants_buyer:
#                 quants_buyer.append(quant.buyer)   

        wizard_obj = self.env['stock.picking_from_quants']
           
        vals = { 'location_source_id': quants_locations[0].id }        
           
        wizard_id = wizard_obj.create(vals)

        wizard_line_obj = self.env['stock.picking_from_quants.lines']
    
        for quant in quants:
            if not quant.reservation_id:
                vals_line = {
                    'picking_from_quant_id': wizard_id.id,
                    'quant_id': quant.id,
                    }
                wizard_line_id = wizard_line_obj.create(vals_line)
            else:
                logger.warn("Record #" + str(quant.id) + " as allready reserved")       
                
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


    def action_create_classification(self, cr, uid, ids, context=None):
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


    #NEEDED TO COUNTER THE LAST CHECK
    @api.model
    def quants_move(self, quants, move, location_to, location_from=False, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, entire_pack=False):
        """Moves all given stock.quant in the given destination location.  Unreserve from current move.
        :param quants: list of tuple(browse record(stock.quant) or None, quantity to move)
        :param move: browse record (stock.move)
        :param location_to: browse record (stock.location) depicting where the quants have to be moved
        :param location_from: optional browse record (stock.location) explaining where the quant has to be taken
                              (may differ from the move source location in case a removal strategy applied).
                              This parameter is only used to pass to _quant_create_from_move if a negative quant must be created
        :param lot_id: ID of the lot that must be set on the quants to move
        :param owner_id: ID of the partner that must own the quants to move
        :param src_package_id: ID of the package that contains the quants to move
        :param dest_package_id: ID of the package that must be set on the moved quant
        """
        # TDE CLEANME: use ids + quantities dict
        if location_to.usage == 'view':
            raise UserError(_('You cannot move to a location of type view %s.') % (location_to.name))

        quants_reconcile_sudo = self.env['stock.quant'].sudo()
        quants_move_sudo = self.env['stock.quant'].sudo()
        check_lot = False
        for quant, qty in quants:
            if not quant:
                #If quant is None, we will create a quant to move (and potentially a negative counterpart too)
                quant = self._quant_create_from_move(
                    qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=location_from, force_location_to=location_to)
                check_lot = True
            else:
                quant._quant_split(qty)
                quants_move_sudo |= quant
            quants_reconcile_sudo |= quant

        if quants_move_sudo:
            moves_recompute = quants_move_sudo.filtered(lambda self: self.reservation_id != move).mapped('reservation_id')
            quants_move_sudo._quant_update_from_move(move, location_to, dest_package_id, lot_id=lot_id, entire_pack=entire_pack)
            moves_recompute.recalculate_move_state()

        if location_to.usage == 'internal':
            # Do manual search for quant to avoid full table scan (order by id)
            self._cr.execute("""
                SELECT 0 FROM stock_quant, stock_location WHERE product_id = %s AND stock_location.id = stock_quant.location_id AND
                ((stock_location.parent_left >= %s AND stock_location.parent_left < %s) OR stock_location.id = %s) AND qty < 0.0 LIMIT 1
            """, (move.product_id.id, location_to.parent_left, location_to.parent_right, location_to.id))
            if self._cr.fetchone():
                quants_reconcile_sudo._quant_reconcile_negative(move)

        # In case of serial tracking, check if the product does not exist somewhere internally already
        # Checking that a positive quant already exists in an internal location is too restrictive.
        # Indeed, if a warehouse is configured with several steps (e.g. "Pick + Pack + Ship") and
        # one step is forced (creates a quant of qty = -1.0), it is not possible afterwards to
        # correct the inventory unless the product leaves the stock.
        picking_type = move.picking_id and move.picking_id.picking_type_id or False
#        if check_lot and lot_id and move.product_id.tracking == 'serial' and (not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
#            other_quants = self.search([('product_id', '=', move.product_id.id), ('lot_id', '=', lot_id),
#                                        ('qty', '>', 0.0), ('location_id.usage', '=', 'internal')])
#            if other_quants:
                # We raise an error if:
                # - the total quantity is strictly larger than 1.0
                # - there are more than one negative quant, to avoid situations where the user would
                #   force the quantity at several steps of the process
#                if sum(other_quants.mapped('qty')) > 1.0 or len([q for q in other_quants.mapped('qty') if q < 0]) > 1:
#                    lot_name = self.env['stock.production.lot'].browse(lot_id).name
#                    raise UserError(_('The serial number %s is already in stock.') % lot_name + _("Otherwise make sure the right stock/owner is set."))   
    
