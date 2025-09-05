from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    level_one_limit = fields.Float(string="Approval Level 1 Limit")
    level_two_limit = fields.Float(string="Approval Level 2 Limit")
    level_three_limit = fields.Float(string="Approval Level 3 Limit")

    # Getter
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        res.update({
            'level_one_limit' : ir_config.get_param('rfq_confirmation_levels.level_one_limit'),
            'level_two_limit' : ir_config.get_param('rfq_confirmation_levels.level_two_limit'),
            'level_three_limit' : ir_config.get_param('rfq_confirmation_levels.level_three_limit'),
        })

        return res

    # Setter
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        ir_config.set_param('rfq_confirmation_levels.level_one_limit', self.level_one_limit)
        ir_config.set_param('rfq_confirmation_levels.level_two_limit', self.level_two_limit)
        ir_config.set_param('rfq_confirmation_levels.level_three_limit', self.level_three_limit)