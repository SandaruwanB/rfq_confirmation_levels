from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # override exiting confirm button method
    def action_confirm(self):
        if self._check_approval():
            return self._open_approval_wizard()

        return super(SaleOrder, self).action_confirm()        


    # open the wizard to inform user and send request to next approval level
    def _open_approval_wizard(self):
        wizard = self.env['rfq.confirm.wizard'].create({
            'sales_order_id': self.id,
        })
        
        return {
            'name': _('RFQ Approval'),
            'type': 'ir.actions.act_window',
            'res_model': 'rfq.confirm.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
    

    # approval leves and amount limitations check before confirm the order (This hapens when confirm button is bugged and visible)
    def _check_approval(self):
        user_approval_level = self._get_user_approval_level()
        limits = self._get_value_limits()
        current_order_amount = self.amount_total

        if user_approval_level is None:
            message = _("You don't have permissions. Please contact the administrator.")
            return self._show_toast_message(message, 'warning')
            
        elif user_approval_level == 1:
            if current_order_amount > limits['level_one_limit']:
                return True
                
        elif user_approval_level == 2:
            if current_order_amount > limits['level_two_limit']:
                return True

        elif user_approval_level == 3:
            if current_order_amount > limits['level_three_limit']:
                return True
        
        return False


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
    
    def approve_and_confirm_order(self):
        user_approval_level = self._get_user_approval_level()
        limits = self._get_value_limits()
        current_order_amount = self.amount_total
        
        # Check if user has sufficient approval level
        can_approve = False
        if user_approval_level == 1 and current_order_amount <= limits['level_one_limit']:
            can_approve = True
        elif user_approval_level == 2 and current_order_amount <= limits['level_two_limit']:
            can_approve = True
        elif user_approval_level == 3 and current_order_amount <= limits['level_three_limit']:
            can_approve = True
        elif user_approval_level == 4:
            can_approve = True
        
        if can_approve:
            # Post approval message in chatter
            self.message_post(
                body=_("Order approved and confirmed by %s (Level %s Approver)") % (self.env.user.name, user_approval_level),
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
            
            # Mark related activities as done
            activities = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('res_model', '=', 'sale.order'),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id.name', '=', 'RFQ Approval')
            ])
            activities.action_feedback(feedback=_("Order approved and confirmed"))
            
            # Confirm the order
            return super(SaleOrder, self).action_confirm()
        else:
            return self._show_toast_message(
                _("You don't have sufficient approval level for this order amount."), 
                'warning'
            )