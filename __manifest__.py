{
    'name': 'RFQ Confirmation Levels',
    'version': '1.0',
    'description': 'RFQ confirmation levels (L1, L2, L3 and L4) based on total amount.',
    'author': 'SandaruwanB',
    'website': 'https://sandaruwanb.github.io/',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/rfq_confirm_wizard.xml',
        'views/res_config_settings_inherit.xml',
        'views/sale_order_form_inherit.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}