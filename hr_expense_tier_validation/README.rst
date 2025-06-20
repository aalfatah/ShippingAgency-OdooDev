=======================
Expense Tier Validation
=======================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:eabc2b023bb6018a082ca54c02a7e2263cf3432bc58ed08e876472abeab8b392
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fhr--expense-lightgray.png?logo=github
    :target: https://github.com/OCA/hr-expense/tree/16.0/hr_expense_tier_validation
    :alt: OCA/hr-expense
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/hr-expense-16-0/hr-expense-16-0-hr_expense_tier_validation
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/hr-expense&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module extends the functionality of Expense Reports to support a tier validation process.

**Table of contents**

.. contents::
   :local:

Installation
============

This module depends on ``base_tier_validation``.
You can find it at `OCA/server-ux <https://github.com/OCA/server-ux>`

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for hr_expense model.

Usage
=====

To use this module, you need to:

#. Create a Expense Report triggering at least one "Tier Definition".
#. Click on *Request Validation* button.
#. Under the tab *Reviews* have a look to pending reviews and their statuses.
#. Once all reviews are validated click on *Approve*.

Additional features:

* You can filter the Expense Reports requesting your review through the
  filter *Needs my Review*.
* User with rights to confirm the Expense Report (validate all tiers that would
  be generated) can directly do the operation, this is, there is no need for
  her/him to request a validation.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-expense/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/hr-expense/issues/new?body=module:%20hr_expense_tier_validation%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

.. |maintainer-ps-tubtim| image:: https://github.com/ps-tubtim.png?size=40px
    :target: https://github.com/ps-tubtim
    :alt: ps-tubtim

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-ps-tubtim| 

This module is part of the `OCA/hr-expense <https://github.com/OCA/hr-expense/tree/16.0/hr_expense_tier_validation>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
