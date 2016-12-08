# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Intercompany Partners',
 'summary': "Filter partners of the ERP companies",
 'version': '8.0.0.1.0',
 'category': 'Base',
 'description': """
Allow to filter partners defined as partner_id in 'res.company'
in the partner view.

|


.. figure:: intercompany_partner/static/description/company_partners.png
   :alt: Partners of the companies
   :width: 800 px

 """,
 'license': 'AGPL-3',
 'author': 'Akretion',
 'website': 'http://www.akretion.com',
 'depends': [
     'base',
 ],
 'data': [
     'partner_view.xml',
 ],
 'installable': True,
 }
