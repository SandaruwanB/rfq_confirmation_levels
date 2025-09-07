from odoo import models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Get current user
        current_user = self.env.user
        
        # Define approval level groups to check (in order from highest to lowest)
        approval_groups = [
            ('rfq_confirmation_levels.group_sales_quotation_level_four_approver', 4, 'Level 4 Approver'),
            ('rfq_confirmation_levels.group_sales_quotation_level_three_approver', 3, 'Level 3 Approver'),
            ('rfq_confirmation_levels.group_sales_quotation_level_two_approver', 2, 'Level 2 Approver'),
            ('rfq_confirmation_levels.group_sales_quotation_level_one_approver', 1, 'Level 1 Approver'),
        ]
        
        # Find the user's approval level (should be only one now)
        user_approval_level = None
        user_approval_group_name = None
        
        for group_xml_id, level, group_name in approval_groups:
            if current_user.has_group(group_xml_id):
                user_approval_level = level
                user_approval_group_name = group_name
                break  # Take the first (highest) level found
        
        # Print the results
        print(f"\n=== Sales Quotation Approval Level Check ===")
        print(f"User: {current_user.name} (ID: {current_user.id})")
        print(f"Sale Order: {self.name}")
        print(f"Order Amount: {self.amount_total}")
        
        if user_approval_level:
            print(f"User's Approval Level: {user_approval_group_name} (Level {user_approval_level})")
            _logger.info(f"User {current_user.name} has approval level: {user_approval_level}")
            
            # You can add approval logic here based on amount thresholds
            # Example:
            # if self.amount_total > 10000 and user_approval_level < 3:
            #     raise UserError("This order requires Level 3 or higher approval")
            
        else:
            print("User has NO approval level groups assigned")
            _logger.info(f"User {current_user.name} has no approval level groups assigned")
        
        print("=" * 45)
        
        # Call the original action_confirm method
        # return super(SaleOrder, self).action_confirm()

    def _get_approval_status(self):
        pass

    def _set_approval_status(self):
        pass

    def _check_user_approval_level(self):
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