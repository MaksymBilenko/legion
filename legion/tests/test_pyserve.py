#
#    Copyright 2017 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
from __future__ import print_function

import unittest2
import json
import argparse

try:
    from .legion_test_utils import patch_environ, ModelServeTestBuild
    from .legion_test_models import create_simple_summation_model_by_df
except ImportError:
    from legion_test_utils import patch_environ, ModelServeTestBuild
    from legion_test_models import create_simple_summation_model_by_df

import legion.serving.pyserve as pyserve


class TestModelApiEndpoints(unittest2.TestCase):
    MODEL_ID = 'temp'
    MODEL_VERSION = '1.8'

    @staticmethod
    def _load_response_text(response):
        data = response.data

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return data

    def _parse_json_response(self, response):
        self.assertEqual(response.mimetype, 'application/json', 'Invalid response mimetype')

        data = self._load_response_text(response)
        return json.loads(data)

    def test_health_check(self):
        with ModelServeTestBuild(self.MODEL_ID, self.MODEL_VERSION,
                                 create_simple_summation_model_by_df) as model:
            response = model.client.get(pyserve.SERVE_HEALTH_CHECK)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(self._load_response_text(response), 'OK')

    def test_model_info(self):
        with ModelServeTestBuild(self.MODEL_ID, self.MODEL_VERSION,
                                 create_simple_summation_model_by_df) as model:
            response = model.client.get(pyserve.SERVE_INFO.format(model_id=self.MODEL_ID))
            data = self._parse_json_response(response)

            self.assertIsInstance(data, dict, 'Data is not a dictionary')
            self.assertTrue('version' in data, 'Cannot find version field')
            self.assertTrue('use_df' in data, 'Cannot find use_df field')
            self.assertTrue('input_params' in data, 'Cannot find input_params field')

            self.assertEqual(data['version'], self.MODEL_VERSION, 'Incorrect model version')
            self.assertEqual(data['use_df'], False, 'Incorrect model use_df field')
            self.assertDictEqual(data['input_params'],
                                 {'b': {'numpy_type': 'int64', 'type': 'Integer'},
                                  'a': {'numpy_type': 'int64', 'type': 'Integer'}},
                                 'Incorrect model input_params')

    def test_model_invoke(self):
        with ModelServeTestBuild(self.MODEL_ID, self.MODEL_VERSION,
                                 create_simple_summation_model_by_df) as model:
            a = 10
            b = 20

            response = model.client.get(pyserve.SERVE_INVOKE.format(model_id=self.MODEL_ID) + '?a={}&b={}'.format(a, b))
            result = self._parse_json_response(response)

            self.assertIsInstance(result, dict, 'Result not a dict')
            self.assertDictEqual(result, {'x': a + b})


if __name__ == '__main__':
    unittest2.main()
