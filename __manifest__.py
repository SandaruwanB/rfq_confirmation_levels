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
        'security/security.xml',
        'views/res_config_settings_inherit.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}