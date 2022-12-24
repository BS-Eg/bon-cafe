# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Amazon S3 cloud Storage",
  "summary"              :  """Store your Odoo attachment to Amazon S3 cloud Storage""",
  "category"             :  "Website",
  "version"              :  "1.2.6",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Deepak Singh Gusain",
  "website"              :  "https://store.webkul.com/Odoo-Amazon-S3-Cloud-Storage.html",
  "description"          :  """Store your Odoo attachment to Amazon S3 cloud Storage""",
  "depends"              :  [
                             'base',
                             'base_setup',
                             'bus',
                            #  'web_tour',
                            #  'website',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/default_data.xml',
                             'views/base_config_view.xml',
                            ],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "USD",
  "external_dependencies":  {'python': ['boto3', 'botocore']},
}