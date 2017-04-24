# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime

class MapleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        super_return = super(MapleOrder,self).action_invoice_create(grouped=False, final=False)
        # faut mettre auter chose, genre un filtre, mais ca va marcher
        invoice = self.invoice_ids[0]
        for picking in self.picking_ids.filtered(lambda p: p.picking_type_id.id == 4):
            for pack_ops in picking.pack_operation_ids:
                invoice_line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == pack_ops.product_id)
                if not invoice_line:
                    account = pack_ops.product_id.property_account_income_id or pack_ops.product_id.categ_id.property_account_income_categ_id
                    if not account:
                        raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                            (pack_ops.product_id.name, pack_ops.product_id.id, pack_ops.product_id.categ_id.name))
            
                    fpos = self.fiscal_position_id or self.partner_id.property_account_position_id
                    if fpos:
                        account = fpos.map_account(account)
                    taxes = pack_ops.product_id.taxes_id.filtered(lambda r: r.company_id == pack_ops.picking_id.company_id)
                    tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

                    vals = {
                        'name': pack_ops.product_id.name_get()[0][1],
                        'invoice_id':invoice.id,
#                        'sequence': self.sequence,
                        'origin': self.name,
                        'account_id': account.id,
                        'price_unit': pack_ops.product_id.with_context(pricelist=self.pricelist_id.id).price,
                        'quantity': pack_ops.qty_done,
#                        'discount': self.discount,
                        'uom_id': pack_ops.product_id.uom_id.id,
                        'product_id': pack_ops.product_id.id,
#                        'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
#                        'product_id': self.product_id.id or False,
                        'invoice_line_tax_ids': [(6, 0, tax_id.ids)],
#                        'account_analytic_id': self.order_id.project_id.id,
#                        'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                        }
                    self.env['account.invoice.line'].create(vals)
                for lot in pack_ops.pack_lot_ids:
                    vals = {
                        'name': pack_ops.product_id.name_get()[0][1] + " " + lot.lot_id.name,
                        'invoice_id':invoice.id,
#                        'sequence': self.sequence,
                        'origin': self.name,
                        'account_id': account.id,
                        'price_unit': 0,
#                        'price_unit': pack_ops.product_id.with_context(pricelist=self.pricelist_id.id).price,
                        'quantity': pack_ops.qty_done,
#                        'discount': self.discount,
#                        'uom_id': pack_ops.product_id.uom_id.id,
#                        'product_id': pack_ops.product_id.id,
#                        'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
#                        'product_id': self.product_id.id or False,
#                        'invoice_line_tax_ids': [(6, 0, tax_id.ids)],
#                        'account_analytic_id': self.order_id.project_id.id,
#                        'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                        }
                    self.env['account.invoice.line'].create(vals)

                     
                
            
        return super_return