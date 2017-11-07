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
"""
TensorFlow serving utils
"""

import os
import subprocess

import tensorflow as tf
from grpc.beta import implementations
from tensorflow_serving_client.protos import prediction_service_pb2, predict_pb2
from tensorflow_serving_client.proto_util import copy_message


class TensorFlowServer:
    """
    TensorFlow server (binary runner)
    """

    def __init__(self, *arguments, kwargs=None, server_binary=None):
        """
        Create server

        :param arguments: binary arguments
        :type arguments: list[str]
        :param kwargs: binary kv arguments
        :type kwargs: dict[str, str]
        :param server_binary: custom path to binary
        :type server_binary: str or None
        """
        self._process = None
        self._kwargs = kwargs
        self._arguments = arguments

        self._binary = server_binary
        if not self._binary:
            self._binary = os.getenv('TF_SERVER', 'tensorflow_model_server')

    @property
    def is_started(self):
        """
        Get information is server started

        :return: bool -- is server started
        """
        if not self._process:
            return False
        return self._process.returncode is None

    def start(self):
        """
        Start server

        :return: None
        """
        if self.is_started:
            return

        full_arguments = []

        if self._kwargs:
            for key, value in self._kwargs.items():
                full_arguments.append('--%s=%s' % (key, value))
        if self._arguments:
            full_arguments.extend(self._arguments)

        self._process = subprocess.Popen([self._binary, *full_arguments])

    def stop(self):
        """
        Stop server

        :return:
        """
        if self.is_started:
            self._process.kill()


class TensorFlowServingClient:
    """
    TensorFlow client
    """

    def __init__(self, host, port):
        """
        Create client

        :param host: host address
        :type host: str
        :param port: port
        :type port: int
        """
        self.host = host
        self.port = port
        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)

    def execute(self, request, timeout):
        """
        Execute request on server

        :param request: request
        :type request: :py:class:`predict_pb2.PredictRequest`
        :param timeout: request timeout (seconds)
        :type timeout: float
        :return: result of prediction
        """
        return self.stub.Predict(request, timeout)

    def make_prediction(self, input_df, column_types, model_name, timeout=10.0):
        """
        Build and execute request

        :param input_df: input pandas DataFrame
        :type input_df: :py:class:`pandas.DataFrame`
        :param column_types: dict of column name => type
        :type column_types: dict[str, :py:class:`drun.types.ColumnInformation`]
        :param model_name: name of model
        :type model_name: str
        :param timeout: request timeout (seconds)
        :type timeout: float
        :return: dict[str, object] -- result of request
        """
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name

        columns = input_df.columns.values

        if set(columns) != set(column_types.keys()):
            raise Exception('Invalid data frame columns: %s' % set(columns))

        for column in columns:
            data = input_df.iloc[0][column]
            data = data.item()  # Convert to native
            copy_message(tf.contrib.util.make_tensor_proto(data), request.inputs[column])

        response = self.execute(request, timeout)

        results = {}
        for key in response.outputs:
            tensor_proto = response.outputs[key]
            nd_array = tf.contrib.util.make_ndarray(tensor_proto)
            results[key] = nd_array.item()

        return results
