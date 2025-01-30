import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-akretion-ak-multi-company-incubator",
    description="Meta package for akretion-ak-multi-company-incubator Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_invoicing_multicompany',
        'odoo8-addon-intercompany_partner',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
