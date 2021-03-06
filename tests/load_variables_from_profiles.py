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
Variables loader (from profiles/{env.PROFILE}.ansible.yml files)
"""

import os

import yaml

PROFILE_ENVIRON_KEY = 'PROFILE'


def get_variables(arg):
    """
    Gather and return all variables to robot

    :param arg: path to directory with profiles
    :type args: str
    :return: dict[str, Any] -- values for robot
    """
    profile = os.getenv(PROFILE_ENVIRON_KEY)
    if not profile:
        raise Exception('Cannot get profile - {} ENV variable is not set'.format(PROFILE_ENVIRON_KEY))

    if not arg:
        raise Exception('Cannot get profile - script should be run with one argument that '
                        'provides path to profiles dir. Current argument: {}'.format(arg))

    profile = os.path.join(arg, '{}.ansible.yml'.format(profile))
    if not os.path.exists(profile):
        raise Exception('Cannot get profile - file not found {}'.format(profile))

    with open(profile, 'r') as stream:
        data = yaml.load(stream)

    variables = {
        'CLUSTER_NAMESPACE': data['namespace'],
        'DEPLOYMENT': data['deployment'],

        'USE_HTTPS': data['use_https'] == 'yes',
        'USE_HTTPS_FOR_TESTS': data['use_https_for_tests'] == 'yes',

        'HOST_BASE_DOMAIN': data['test_base_domain'],
        'REAL_HOST_BASE_DOMAIN': data['base_domain'],

        'SERVICE_ACCOUNT': data['service_account']['login'],
        'SERVICE_PASSWORD': data['service_account']['password'],

        'SUBDOMAINS': data['subdomains'],
        'JENKINS_JOBS': data['examples_to_test'],
    }

    variables['HOST_PROTOCOL'] = 'https' if variables['USE_HTTPS_FOR_TESTS'] else 'http'

    return variables
