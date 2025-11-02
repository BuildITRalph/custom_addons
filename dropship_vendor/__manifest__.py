{
    'name': "PREFERRED VENDOR DROPSHIP",

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
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

