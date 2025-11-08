{
    'name': "DROPSHIP PREFERRED VENDOR",

    'summary': "Setup the Preferred Vendor in Dropship Orders",

    'description': """
    This module allows users to set a preferred vendor for products. When creating dropship orders,
    the system will automatically select the preferred vendor if one is set for the product.
    """,

    'author': "BUILDITRALPH Co.",
    # 'website': "https://builditralph.github.io/My-Portfolio/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Supply Chain',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','sale_stock','stock','stock_dropshipping'],

    # always loaded
    'data': [
        'security/preferred_vendor_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}

