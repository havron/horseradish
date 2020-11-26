"""
.. module: horseradish.plugins.bases.metric
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from horseradish.plugins.base import Plugin


class MetricPlugin(Plugin):
    type = "metric"

    def submit(
        self, metric_name, metric_type, metric_value, metric_tags=None, options=None
    ):
        raise NotImplementedError
