from odoo import models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    # override exiting confirm button method
    def action_confirm(self):
        approval_result = self._check_approval()

        if isinstance(approval_result, dict) and approval_result.get('type') == 'ir.actions.client':
            return approval_result

        if not approval_result:
            return False

        return super(SaleOrder, self).action_confirm()
    

    # approval leves and amount limitations check
    def _check_approval(self):
        user_approval_level = self._get_user_approval_level()
        limits = self._get_value_limits()
        current_order_amount = self.amount_total

        if user_approval_level is None:
            message = _("You don't have permissions. Please contact the administrator.")
            return self._show_toast_message(message, 'warning')
            
        elif user_approval_level == 1:
            if current_order_amount > limits['level_one_limit']:
                message = _("Order amount (%.2f) exceeds your approval limit (%.2f).") % (current_order_amount, limits['level_one_limit'])
                return self._show_toast_message(message, 'warning')
                
        elif user_approval_level == 2:
            if current_order_amount > limits['level_two_limit']:
                message = _("Order amount (%.2f) exceeds your approval limit (%.2f).") % (current_order_amount, limits['level_two_limit'])
                return self._show_toast_message(message, 'warning')
                
        elif user_approval_level == 3:
            if current_order_amount > limits['level_three_limit']:
                message = _("Order amount (%.2f) exceeds your approval limit (%.2f).") % (current_order_amount, limits['level_three_limit'])
                return self._show_toast_message(message, 'warning')
        
        return True


    # get value limit from the settings
    def _get_value_limits(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        
        limits = {
            'level_one_limit': float(ir_config.get_param('rfq_confirmation_levels.level_one_limit', 0.0)),
            'level_two_limit': float(ir_config.get_param('rfq_confirmation_levels.level_two_limit', 0.0)),
            'level_three_limit': float(ir_config.get_param('rfq_confirmation_levels.level_three_limit', 0.0)),
        }
        
        return limits


    # get current user approval level
    def _get_user_approval_level(self):
        current_user = self.env.user
        approval_groups = [
            ('rfq_confirmation_levels.group_sales_quotation_level_four_approver', 4),
            ('rfq_confirmation_levels.group_sales_quotation_level_three_approver', 3),
            ('rfq_confirmation_levels.group_sales_quotation_level_two_approver', 2),
            ('rfq_confirmation_levels.group_sales_quotation_level_one_approver', 1),
        ]

        for group_xml_id, level in approval_groups:
            if current_user.has_group(group_xml_id):
                return level
        return None
        

    # Toast notification to user
    def _show_toast_message(self, message, message_type='info'):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Confirmation Denied'),
                'message': message,
                'type': message_type,
                'sticky': False,
            }
        }