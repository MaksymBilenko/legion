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

import legion.utils as utils
import unittest2


class TestUtilsDefaultDockerRegistry(unittest2.TestCase):
    def test_full_source_empty_registry(self):
        source = 'localhost:31100/repo/image:tag'
        registry = None

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'localhost:31100/repo/image:tag')

    def test_2_source_empty_registry(self):
        source = 'repo/image:tag'
        registry = None

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'repo/image:tag')

    def test_1_source_empty_registry(self):
        source = 'image:tag'
        registry = None

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'image:tag')

    def test_full_source_full_registry(self):
        source = 'localhost:31100/repo/image:tag'
        registry = 'external:6666/other'

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'localhost:31100/repo/image:tag')

    def test_2_source_full_registry(self):
        source = 'repo/image:tag'
        registry = 'external:6666/other'

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'external:6666/repo/image:tag')

    def test_1_source_full_registry(self):
        source = 'image:tag'
        registry = 'external:6666/other'

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'external:6666/other/image:tag')

    def test_2_source_1_registry(self):
        source = 'repo/image:tag'
        registry = 'external:6666'

        self.assertEqual(utils.add_default_docker_registry(source, registry), 'external:6666/repo/image:tag')

    def test_1_source_1_registry(self):
        source = 'image:tag'
        registry = 'external:6666'

        with self.assertRaises(Exception):
            self.assertEqual(utils.add_default_docker_registry(source, registry), 'external:6666/repo/image:tag')


if __name__ == '__main__':
    unittest2.main()
