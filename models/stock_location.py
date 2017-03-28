# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.tools.yaml_tag import record_constructor
#from numpy.distutils.fcompiler import none

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class stockLocation(models.Model):
    _name = 'stock.location'
    _inherit = 'stock.location'

    kanban_color = fields.Integer(
        string="Color",
        compute='_compute_qty_stock',
        store=True
        )

    current_owner  = fields.Many2one(
        comodel_name='res.partner',
        string='Owner',
        compute='_compute_qty_stock',
        help="Default Owner",
        store=True
        )    
    
    current_rules = fields.Selection([
        ('HS', 'From Outside'),
        ('QC', 'From Québec')],
        help="Product Origin. ",
        compute='_compute_qty_stock',
        store=True
        )    
        
    maxItem = fields.Integer(
        string="Maximum capacity",
        help="The maximum count of product that can be put in that location. ")
    
    spaceLeft = fields.Integer(
        string="Product Space Left",
        help="The empty product space in that location. ")
    
    purchase_lines = fields.One2many(           
        comodel_name='purchase.order.line', 
        inverse_name='location_id',
        string="Purchases",
        help='Stock purchase planed for that location. ')
    
    qty_purchased  = fields.Float(
        string='Quantity Purchased',
        compute='_compute_qty_purchase',
        store=True
        )
    
    stock_lines = fields.One2many(           
        comodel_name='stock.quant', 
        inverse_name='location_id',
        string="Stock",
        help='Stock for that location. ')
    
    qty_stock  = fields.Float(
        string='Quantity Stock',
        compute='_compute_qty_stock',
        store=True
        )
      
    @api.depends('purchase_lines')
    def _compute_qty_purchase(self):
        for record in self:
            qty = 0 
            for line in record.purchase_lines:
                if line.product_id.type == 'product':
                    qty += line.product_qty          
            record.qty_purchased = qty
            
    @api.depends('stock_lines','stock_lines.owner_id','stock_lines.qty')
    def _compute_qty_stock(self):
        for record in self:
            qty = 0
            owner = []
            origin = []
            for line in record.stock_lines:
                if line.product_id.type == 'product':
                    if line.owner_id not in owner:
                        owner.append(line.owner_id)
                    qty += line.qty
            if owner :                                      
                if len(owner) == 1:
                    #un seul proprio
                    record.current_owner = owner [0]
                else:
                    # pas juste une
                    record.kanban_color = 4 
            else:
                #vide
                record.kanban_color = 3 
            record.qty_stock = qty
            
