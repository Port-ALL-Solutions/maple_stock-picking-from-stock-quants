<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
    
        <record id="view_picking_form_head" model="ir.ui.view">
              <field name="name">maple.view_picking_form</field>
              <field name="model">stock.picking</field>
              <field name="inherit_id" ref="stock.view_picking_form_head"/>
              <field name="arch" type="xml">
                <xpath expr="//field[@name='min_date']" position="before">
                      <field name="maple_weight"/>
                </xpath>              
              </field>
        </record>    
    
        <record id="view_picking_form_body" model="ir.ui.view">
              <field name="name">maple.view_picking_form</field>
              <field name="model">stock.picking</field>
              <field name="inherit_id" ref="stock.view_picking_form_body"/>
              <field name="arch" type="xml">
                <xpath expr="//button[@name='split_lot']" position="before">
                      <field name="maple_weight"/>
                </xpath>              
              </field>
        </record>    
    
        <record id="view_pack_operation_lot_form" model="ir.ui.view">
              <field name="name">maple.view_pack_operation_lot_form</field>
              <field name="model">stock.pack.operation</field>
              <field name="inherit_id" ref="stock.view_pack_operation_lot_form"/>
              <field name="arch" type="xml">
                <xpath expr="//field[@name='qty']" position="after">
                      <field name="maple_weight"/>
                </xpath>
              </field>
        </record>    
        
    
    </data>
</odoo>