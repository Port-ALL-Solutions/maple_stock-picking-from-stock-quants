# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError

class PickingFromQuantsWizard(models.TransientModel):
    _name = 'stock.picking_from_quants'
#    _inherit = 'purchase.order'

    
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True,
#        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
        )
    
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
#        states={'draft': [('readonly', False)]}
        )
        
    maple_producer = fields.Many2one(
        comodel_name='res.partner',
        string= 'Producer',
        help="Producer. "
        )

    partner_fpaqCode = fields.Char(
        string='FPAQ',
        related='maple_producer.parent_id.fpaqCode'
        )
    
    partner_street = fields.Char(
        string='Address',
        related='maple_producer.street'
        )
    
    partner_city = fields.Char(
        string='City',
        related='maple_producer.city'
        )
        
    partner_state = fields.Char(
        string='Province / State',
        related='maple_producer.state_id.name'
        )

    partner_region = fields.Char(
        string='Region',
        related='maple_producer.maple_region.name',
        )
    
#    employee_id = fields.Many2one(
#        comodel_name='hr.employee',
#        string= 'Employee',
#        help="Employee. "
#ajouter domaine pour limiter aux inspecteurs
#        )
    
    date_planed = fields.Date(
        string='Date planed',
        required=True,
        index=True,
        default=fields.Date.today,
        help='Date at which weighing is planed to be done. '
        )            

    related_ids = fields.Char(
        string='Related',
        compute='_compute_related',
        )

    quants_selected = fields.Many2one(
        comodel_name='stock.quant',
        string= 'Quants',
        help="Qaunts. "
        )

    note = fields.Text('Internal Notes')


    @api.onchange('maple_producer')
    def _compute_related(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        if active_ids:
            quants_selected = self.env['stock.quant'].browse(active_ids)


    @api.onchange('maple_producer')
    def _compute_related(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        self.related_ids =  ''.join(str(e) for e in active_ids)

    @api.multi
    def action_create_picking_from_quants(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        product_obj = self.env['product.product']

        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type'].browse(self.picking_type_id.id)
        
        quant_obj = self.env['stock.quant']
        move_obj = self.env['stock.move']
        operation_obj = self.env['stock.pack.operation']
        operation_lot_obj = self.env['stock.pack.operation.lot']

        partners = []
        locations = []
        products = []
        quantity = 0.

        for record in self.env['stock.quant'].browse(active_ids):
            quantity += record.qty
            if record.producer.id not in partners:
                partners.append(record.producer.id)
            if record.location_id.id not in locations:
                locations.append(record.location_id.id)
            if record.product_id.id not in products:
                products.append(record.product_id.id)

        if not products:
             raise UserError(_("No product."))

        if len (products) > 1:
             raise UserError(_("More than one product."))
        
        if not partners:
             raise UserError(_("No producer."))

        if len (partners) > 1:
             raise UserError(_("More than one producer."))
        
        if not locations:
             raise UserError(_("No locations."))

        if len (locations) > 1:
             raise UserError(_("More than one locations."))

        picking_vals = {
            'origin': "Manually created",
            'partner_id': False,
            'date_done': self.date_planed,
            'picking_type_id': self.picking_type_id.id,
            'move_type': 'direct',
            'note': self.note or "",
            'location_id': locations[0],
            'location_dest_id': picking_type_obj.default_location_dest_id.id,
            }
         
        picking = picking_obj.create(picking_vals)
        product = product_obj.browse(products)
        
        move_vals= {
            'picking_id': picking.id,
            'product_id': products[0],
            'name': "Manually created",
            'product_uom_qty' : quantity,
            'product_uom' : product.uom_id.id,
            'location_id': locations[0],
            'location_dest_id': picking_type_obj.default_location_dest_id.id,
            }
            
        move = move_obj.create(move_vals)
        picking.action_confirm()
        picking.action_assign()
        
        selected_lots = quant_obj.browse(active_ids)
        autopick_lots = move.reserved_quant_ids
        
        for lot in autopick_lots:
            if lot not in selected_lots:
                lot.write({'reservation_id': False})
                
        for lot in selected_lots:
            if not lot.reservation_id:
                quants = quant_obj.quants_get_preferred_domain(lot.qty, move, lot_id=lot.lot_id.id)
#                quants = quant_obj.quants_get_preferred_domain(lot.qty, move, ops=ops, lot_id=lot.lot_id, domain=domain, preferred_domain_list=[])
                lot.quants_reserve(quants, move)
        
        ops = picking.pack_operation_product_ids
        ops.write({'owner_id': partners[0]})
        ops_lots = ops.pack_lot_ids
        x = 0
        for lot in ops_lots:
            lot.write({'lot_id': selected_lots[x].lot_id.id})
            x += 1

#        move.quants_unreserve()
#        operation = operation__obj.browse(picking.pack_operation_product_ids)
#        operation_lots = operation_lots_obj.browse(opertation.pack_lots_ids)
        
                
#        for record in self.env['stock.quant'].browse(active_ids):
            
#        for record in self.env['stock.quant'].browse(active_ids):
    #            if record.state not in ('draft', 'proforma', 'proforma2'):
    #                raise UserError(_("Selected invoice(s) cannot be confirmed as they are not in 'Draft' or 'Pro-Forma' state."))
              
 #           record.action_change_test()
        return {'type': 'ir.actions.act_window_close'}


    @api.multi
    def action_add_quants_to_picking(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        return {'type': 'ir.actions.act_window_close'}
