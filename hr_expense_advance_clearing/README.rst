=============================
Employee Advance and Clearing
=============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:34f402d1730612641c154dce7b2412a1fb8576942a70fa44f685a8505e4ce1d7
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fhr--expense-lightgray.png?logo=github
    :target: https://github.com/OCA/hr-expense/tree/16.0/hr_expense_advance_clearing
    :alt: OCA/hr-expense
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/hr-expense-16-0/hr-expense-16-0-hr_expense_advance_clearing
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/hr-expense&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

Standard Expenses module allow employee to do the expense reimbursement only after the expense has been made.
In other world, employee will need to pay first and reimburse later.

This module, allow company to advance an amount to the employee.
Employee can then use that advance amount to purchase product/service first, then back to company and do the clearing.

There can be 3 scenarios for advance and clearing

* When clearing amount = advance amount, no other operation is required.
* When clearing amount > advance amount, company will pay the extra to employee.
* When clearing amount < advance amount, employee will return the remain to company.

**Table of contents**

.. contents::
   :local:

Configuration
=============

This module will create a new product "Employee Advance" automatically.
You will need to setup the Expense Account of this product to your Employee Advance account manually.

* Open Product window and search for "Employee Advance"
* On Accounting tab, select appropriate employee advance account from your chart of account

Note:

* You will need the "Show Full Accounting Features" to see accounting data
* Employee Advance account code, if not already exists, you can create one. Use type = Current Asset and check Allow Reconciliation.

Usage
=====

To use this module, you must configure product "Employee Advance" with account type = Current Asset and check Allow Reconciliation.
After that, you can step following:

**Create an Employee Advance**

#. Go to Expenses > My Expenses > Advances
#. Create sheet and add a line with advance
#. As an option, the user can also set the "Clearing Product". If this is set, on the clear advance step, the clearing product will create a default product line.
#. Set the unit price to advance amount > Save
#. As normal, do Submit to Manager > Approve > Post Journal Entries > Register Payment.
#. As this is Advance, you will see a new field "Amount to clear".

**Clear Advance**

you can do 2 ways,

#. Create clearing from advance document
    #. Go to Expenses > My Expenses > Advances
    #. Search for the Advance you want to clear, or use filter "Advance (not cleared)" to see all uncleared advance.
    #. Open an Advance which is now in paid status with some Amount to be cleared.
    #. Click button "Clear Advance", system will create new Expense Report with reference to the previous step Advance.
    #. Create name clearing and Save (must save first)
    #. Edit > Add or create Expense line(s) as normal.
    #. As normal, do Approve > Post Journal Entries
#. Create clearing from new expense
    #. Go to Expenses > My Expenses > Expenses
    #. Create sheet and reference advance with field "Clear Advance" > Save (must save first)
    #. Edit > Add or create Expense line(s) as normal.
    #. As normal, do Approve > Post Journal Entries

Note:

* If the total expense amount less than or equal to the advance amount, the status will be set to Paid right after post journal entries.
* If the total expense amount more than the advance amount, Register Payment will pay the extra amount then set state to Paid.

**Return Advance**

#. Go to Expenses > My Expenses > Advances
#. Search for the Advance you want to clear, or use filter "Advance (not cleared)" to see all uncleared advance.
#. Open an Advance which is now in paid status with some Amount to be cleared.
#. Click button "Return Advance" will open Register Payment wizard with Amount to clear.
#. Click button "Create Payment" to return that amount back
#. All returned, Amount to clear is now equal to 0.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-expense/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/hr-expense/issues/new?body=module:%20hr_expense_advance_clearing%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Ecosoft

Contributors
~~~~~~~~~~~~

* Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
* Tharathip Chaweewongphan <tharathipc@ecosoft.co.th>
* Saran Lim. <saranl@ecosoft.co.th>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-kittiu| image:: https://github.com/kittiu.png?size=40px
    :target: https://github.com/kittiu
    :alt: kittiu

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-kittiu| 

This module is part of the `OCA/hr-expense <https://github.com/OCA/hr-expense/tree/16.0/hr_expense_advance_clearing>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
