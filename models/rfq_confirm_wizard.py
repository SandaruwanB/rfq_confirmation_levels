from odoo import models, fields, api


class RfqConfirmWizard(models.TransientModel):
    _name = 'rfq.confirm.wizard'
    _description = 'RFQ Confirmation Wizard'

    sales_order_id = fields.Many2one('sale.order', string='Sales Order', required=True)
    
    def pass_to_approval_level(self):
        print(self.sales_order_id.name)

        return {'type': 'ir.actions.act_window_close'}