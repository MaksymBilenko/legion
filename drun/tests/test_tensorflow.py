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
import os
import time

import drun.io
from drun.utils import TemporaryFolder

import pandas as pd
import tensorflow as tf


class TestTensorFlow(unittest2.TestCase):
    MODEL_ID = 'temp'
    MODEL_VERSION = '1.8'

    def setUp(self):
        pass

    def _build_demo_tensor_flow(self, session):
        X = tf.placeholder("float", [None, 1], name='X')
        Y = tf.placeholder("float", [None, 1], name='Y')
        Z = X + Y
        init = tf.global_variables_initializer()

        session.run(init)

        return X, Y, Z, init

    def test_demo_tensor_flow_calculation(self):
        with tf.Session() as session:
            X, Y, Z, init = self._build_demo_tensor_flow(session)
            data = session.run(Z, feed_dict={X: [[1]], Y: [[2]]})

        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]), 1)
        self.assertEqual(data[0][0], 3.0)

    def test_demo_tensor_build(self):
        with TemporaryFolder('test_demo') as folder:
            with tf.Graph().as_default():
                with tf.Session() as session:
                    X, Y, Z, init = self._build_demo_tensor_flow(session)
                    model_file = os.path.join(folder.path, 'tf.model')

                    data_frame = pd.DataFrame([{'a': 1.0, 'b': 1.5}])

                    drun.io.export_tf(model_file, session,
                                      lambda x: x,
                                      {'a': X, 'b': Y},
                                      {'result': Z},
                                      input_data_frame=data_frame)

                    self.assertTrue(os.path.exists(model_file), 'Model not existed')

    def test_demo_tensor_serving(self):
        with TemporaryFolder('test_demo') as folder:
            with tf.Graph().as_default():
                with tf.Session() as session:
                    X, Y, Z, init = self._build_demo_tensor_flow(session)
                    model_file = os.path.join(folder.path, 'tf.model')

                    data_frame = pd.DataFrame([{'a': float(1.0), 'b': float(1.5)}])

                    drun.io.export_tf(model_file, session,
                                      lambda x: x,
                                      {'a': X, 'b': Y},
                                      {'sum': Z},
                                      input_data_frame=data_frame)

            with TemporaryFolder('test_demo_serving') as serving_folder:
                with drun.io.ModelContainer(model_file, target_path=serving_folder.path) as container:
                    model = container.model

                try:
                    model.startup(serving_folder.path)
                    time.sleep(3)

                    result = model.apply({'a': '2.0', 'b': '3.5'})
                    self.assertEqual(len(result), 1)
                    self.assertTrue('sum' in result)
                    self.assertEqual(result['sum'], 5.5)
                finally:
                    model.shutdown(folder.path)


if __name__ == '__main__':
    unittest2.main()
