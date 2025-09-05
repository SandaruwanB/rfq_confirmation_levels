from odoo import models, fields



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    level_one_limit = fields.Float(string="Approval Level 1 Limit")
    level_two_limit = fields.Float(string="Approval Level 2 Limit")
    level_three_limit = fields.Float(string="Approval Level 3 Limit")