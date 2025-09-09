from odoo import models, fields, api, _
from datetime import datetime, timedelta


class RfqConfirmWizard(models.TransientModel):
    _name = 'rfq.confirm.wizard'
    _description = 'RFQ Confirmation Wizard'

    sales_order_id = fields.Many2one('sale.order', string='Sales Order', required=True)
    
    # button action
    def pass_to_approval_level(self):
        current_user_level = self.sales_order_id._get_user_approval_level()
        next_level = self._get_next_approval_level(current_user_level)
        self._set_chatter_message(current_user_level, next_level)
        self._create_approval_activity(next_level)
        
        return {'type': 'ir.actions.act_window_close'}
    
    
    # Find and get next approval level
    def _get_next_approval_level(self, current_level):
        limits = self.sales_order_id._get_value_limits()
        order_amount = self.sales_order_id.amount_total

        required_level = 4
        
        if order_amount <= limits['level_one_limit']:
            required_level = 1
        elif order_amount <= limits['level_two_limit']:
            required_level = 2
        elif order_amount <= limits['level_three_limit']:
            required_level = 3
        else:
            required_level = 4

        for level in range(required_level, 5):
            users_at_level = self._get_users_in_specific_level_only(level)
            if users_at_level:
                return level
        return 4

    # chatter message send to the log
    def _set_chatter_message(self, current_level, next_level):
        current_user = self.env.user
        order_amount = self.sales_order_id.amount_total
        
        level_names = {
            1: "Level 1",
            2: "Level 2", 
            3: "Level 3",
            4: "Level 4"
        }
        
        message = _(
            "Approval request sent by %(user)s (%(current_level)s Approver). "
            "Order Amount: %(amount)s "
            "Requesting approval from %(next_level)s Approvers."
        ) % {
            'user': current_user.name,
            'current_level': level_names.get(current_level, 'Unknown'),
            'amount': self.sales_order_id.currency_id.symbol + str(order_amount),
            'next_level': level_names.get(next_level, 'Unknown')
        }
        
        self.sales_order_id.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    
    # create activity to target group's user
    def _create_approval_activity(self, next_level):
        next_level_users = self._get_users_in_specific_level_only(next_level)
        
        # if the user level is not found pass to next group users
        if not next_level_users:
            for level in range(next_level + 1, 5):
                next_level_users = self._get_users_in_specific_level_only(level)
                if next_level_users:
                    next_level = level
                    break
        
        if not next_level_users:
            return

        activity_type = self._get_or_create_approval_activity_type()

        for user in next_level_users:
            self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'res_id': self.sales_order_id.id,
                'res_model_id': self.env['ir.model']._get('sale.order').id,
                'user_id': user.id,
                'summary': _('RFQ Approval Required'),
                'note': _(
                    'Please confirm this sales order: %(order_name)s<br/>'
                    'Customer: %(customer)s<br/>'
                    'Amount: %(amount)s<br/>'
                    'Requested by: %(requester)s'
                ) % {
                    'order_name': self.sales_order_id.name,
                    'customer': self.sales_order_id.partner_id.name,
                    'amount': self.sales_order_id.currency_id.symbol + str(self.sales_order_id.amount_total),
                    'requester': self.env.user.name
                },
                'date_deadline': datetime.now() + timedelta(days=1),
            })
    
    # Filter users to get level
    def _get_users_in_specific_level_only(self, level):
        group_mapping = {
            1: 'rfq_confirmation_levels.group_sales_quotation_level_one_approver',
            2: 'rfq_confirmation_levels.group_sales_quotation_level_two_approver',
            3: 'rfq_confirmation_levels.group_sales_quotation_level_three_approver',
            4: 'rfq_confirmation_levels.group_sales_quotation_level_four_approver',
        }
        
        target_group_xml_id = group_mapping.get(level)
        if not target_group_xml_id:
            return self.env['res.users']
        
        try:
            target_group = self.env.ref(target_group_xml_id)
            target_users = target_group.users

            filtered_users = self.env['res.users']
            
            for user in target_users:
                is_higher_level = False
                
                for higher_level in range(level + 1, 5):
                    higher_group_xml_id = group_mapping.get(higher_level)
                    if higher_group_xml_id:
                        try:
                            higher_group = self.env.ref(higher_group_xml_id)
                            if user in higher_group.users:
                                is_higher_level = True
                                break
                        except:
                            continue

                if not is_higher_level:
                    filtered_users |= user
            
            return filtered_users
            
        except:
            return self.env['res.users']
    

    def _get_or_create_approval_activity_type(self):
        activity_type = self.env['mail.activity.type'].search([
            ('name', '=', 'RFQ Approval'),
            ('category', '=', 'default')
        ], limit=1)
        
        if not activity_type:
            activity_type = self.env['mail.activity.type'].create({
                'name': 'RFQ Approval',
                'category': 'default',
                'summary': 'RFQ requires approval',
                'delay_count': 3,
                'delay_unit': 'days',
                'delay_from': 'current_date',
            })
        
        return activity_type