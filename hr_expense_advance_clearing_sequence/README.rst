====================================
HR Expense Advance Clearing Sequence
====================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:bfb44e1f94dd5b3f2274755eae3238cdc9d7b44059d4ee5165ee90f38a2e1256
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fhr--expense-lightgray.png?logo=github
    :target: https://github.com/OCA/hr-expense/tree/16.0/hr_expense_advance_clearing_sequence
    :alt: OCA/hr-expense
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/hr-expense-16-0/hr-expense-16-0-hr_expense_advance_clearing_sequence
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/hr-expense&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module adds the possibility to define a sequence for the expense report's reference that Employee advance.
This reference is then set as default when you create a new expense report, using the defined sequence.

**Table of contents**

.. contents::
   :local:

Configuration
=============

You can change the default sequence (EXAV0001) by the one of your choice
going to *Settings > Technical > Sequences & Identifiers > Sequences*, and
editing the record `Expense report sequence (Advance)`.

You will only have access to that section if your section has `Technical features`
permission check marked.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-expense/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/hr-expense/issues/new?body=module:%20hr_expense_advance_clearing_sequence%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Ecosoft

Contributors
~~~~~~~~~~~~

* Pimolnat Suntian <pimolnats@ecosoft.co.th>
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

This module is part of the `OCA/hr-expense <https://github.com/OCA/hr-expense/tree/16.0/hr_expense_advance_clearing_sequence>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
