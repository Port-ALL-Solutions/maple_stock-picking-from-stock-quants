# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError

class PickingFromQuantsWizardLines(models.TransientModel):
    _name = 'stock.picking_from_quants.lines'

    quant_id = fields.Many2one(
        'stock.quant', 
        'Product selected',
        )

    quant_serial = fields.Char(
        string='Serial',
        related='quant_id.lot_id.name'
        )
    
    picking_from_quant_id = fields.Many2one('stock.picking_from_quants', string='Quants')
          
class PickingFromQuantsWizard(models.TransientModel):
    _name = 'stock.picking_from_quants'

    quants_line = fields.One2many('stock.picking_from_quants.lines', 'picking_from_quant_id', string='Quants Lines')

    picking_type_id = fields.Many2one(
        'stock.picking.type', 
        'Picking Type',
#        required=True,
#        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
        )

    fixed_destination = fields.Boolean(
        string='Fixed destination',
        related='picking_type_id.fixed_destination',
        )
    
    location_dest_id = fields.Many2one(
        'stock.location', 
        "Destination Location Zone",
 #       required=True,        
#        states={'draft': [('readonly', False)]}
        )
        
    location_source_id = fields.Many2one(
        'stock.location', 
        "Source Location Zone",
 #       required=True,        
#        states={'draft': [('readonly', False)]}
        )
        
    maple_producer = fields.Many2one(
        comodel_name='res.partner',
        compute='_compute_producer',
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

    @api.onchange('related_ids')
    def _compute_producer(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.maple_producer = self.env['stock.quant'].browse(active_ids[0]).owner_id


    @api.onchange('picking_type_id')
    def _compute_related_destination(self):
        self.location_dest_id = self.picking_type_id.default_location_dest_id

    @api.onchange('maple_producer')
    def _compute_related(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        quants = self.env['stock.quant'].browse(active_ids)
        
        for q in quants:
            self.env['stock.picking_from_quants.lines'].create({'quant_id':q.id})
        
        self.related_ids =  ''.join(str(e) for e in active_ids)

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

        
        quantity = 0.
        quants = self.env['stock.quant'].browse(active_ids)
        
        partners = quants.mapped('producer')
        locations = quants.mapped('location_id')
        products = quants.mapped('product_id')

#         prod_list = []        
#         
#         partners = []
#         locations = []
#         products = []        # generic error checking
#         prod_list = []
#         
#         for record in quants:
#             quantity += record.qty
#             if record.producer.id not in partners:
#                 partners.append(record.producer.id)
#             if record.location_id.id not in locations:
#                 locations.append(record.location_id.id)
#             if len(products):
#                 found_product = False
#                 for p in products:
#                     if p['product_id'] == record.product_id.id:
#                         p['qty'] += record.qty
#                         found_product = True
#                 if not found_product:
#                     products.append({'product_id':record.product_id.id,'qty':record.qty})
#                     prod_list.append(record.product_id.id)
#             else:
#                 products.append({'product_id':record.product_id.id,'qty':record.qty})
#                 prod_list.append(record.product_id.id)
                
        if not len(products):
             raise UserError(_("No product."))

        if picking_type_obj.single_product and len (products) > 1: 
             raise UserError(_("More than one product."))
        
        if not partners:
             raise UserError(_("No producer."))

        if picking_type_obj.single_origin and len (partners) > 1:
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
            'location_id': locations[0].id,
            'location_dest_id': self.location_dest_id.id,
            }
         
        picking = picking_obj.create(picking_vals)
        
#        moved_products = product_obj.browse(prod_list)
  
        for product in products:
            quants_product = quants.filtered(lambda r: r.product_id == product)
            move_vals= {
                    'picking_id': picking.id,
                    'product_id': product.id,
                    'name': "Manually created",
                    'product_uom_qty' : len(quants_product),
                    'product_uom' : product.uom_id.id,
                    'location_id': locations[0].id,
                    'location_dest_id': self.location_dest_id.id,
                    }                
            move = move_obj.create(move_vals)

        
#         for product in moved_products:        
# #            product = product_obj.browse(products)
#             
#             move_vals= {
#                 'picking_id': picking.id,
#                 'product_id': product.id,
#                 'name': "Manually created",
#                 'product_uom_qty' : quantity,
#                 'product_uom' : product.uom_id.id,
#                 'location_id': locations[0],
#                 'location_dest_id': picking_type_obj.default_location_dest_id.id,
#                 }                
#             move = move_obj.create(move_vals)

        picking.action_confirm()
        picking.action_assign()

#         selected_lots = quant_obj.browse(active_ids)
#         
#         for move in picking.move_lines:  
#             autopick_lots = move.reserved_quant_ids
#             for lot in autopick_lots:
#                 if lot not in selected_lots:
#                     lot.write({'reservation_id': False})
#             for lot in selected_lots:
#                 if not lot.reservation_id:
#                     quants = quant_obj.quants_get_preferred_domain(lot.qty, move, lot_id=lot.lot_id.id)
#     #                quants = quant_obj.quants_get_preferred_domain(lot.qty, move, ops=ops, lot_id=lot.lot_id, domain=domain, preferred_domain_list=[])
#                     lot.quants_reserve(quants, move)
# 
#         for ops in picking.pack_operation_product_ids:            
#             ops.write({'owner_id': partners[0].id})
#             ops_lots = ops.pack_lot_ids
#             x = 0
#             for lot in ops_lots:
#                 lot.write({'lot_id': selected_lots[x].lot_id.id})
#                 x += 1
            
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_add_quants_to_picking(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        return {'type': 'ir.actions.act_window_close'}
    
    def action_create_classification(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        partners = []
        locations = []
        products = []        # generic error checking

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

#        if len (products) > 1:
#             raise UserError(_("More than one product."))
        
        if not partners:
             raise UserError(_("No producer."))

#        if len (partners) > 1:
#             raise UserError(_("More than one producer."))
        
        if not locations:
             raise UserError(_("No locations."))

        if len (locations) > 1:
             raise UserError(_("More than one locations."))

        classification_obj = self.env['maple.classification']
        classification = classifiaciton_obj.create()
        classification_line_obj = self.env['maple.classification.line']

        for record in self.env['stock.quant'].browse(active_ids):
            classification_line_vals = {
                'classification_id': classification.id,
                'quant_id': record.id}
            classification_line = classification_line_obj.create(classification_line_vals)
            
        return {'type': 'ir.actions.act_window_close'}

    