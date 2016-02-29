#!/usr/bin/env python
# Copyright 2015 CenturyLink
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import clc_ansible_module.clc_aa_policy as clc_aa_policy
from clc_ansible_module.clc_aa_policy import ClcAntiAffinityPolicy
import clc as clc_sdk
from clc import CLCException
import mock
from mock import patch, create_autospec
import os
import unittest

def FakeAnsibleModule():
    module = mock.MagicMock()
    module.check_mode = False
    module.params = {}
    return module

class TestClcAntiAffinityPolicy(unittest.TestCase):

    def setUp(self):
        self.clc = mock.MagicMock()
        self.module = FakeAnsibleModule()
        self.policy = ClcAntiAffinityPolicy(self.module)
        self.policy.module.exit_json = mock.MagicMock()
        self.policy_dict = {}

    def testArgumentSpecContract(self):
        args = ClcAntiAffinityPolicy._define_module_argument_spec()
        self.assertEqual(args, dict(
            name=dict(required=True),
            location=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
            wait=dict(default=True)
        ))

    def testCreateNoChange(self):
        mock_policy = mock.MagicMock(spec=clc_sdk.v2.AntiAffinity)
        mock_policy.name = 'TestMaster3000'
        mock_policy.data = {}
        self.policy.module.params = {
            'location': 'beer',
            'state': 'present',
            'name': 'TestMaster3000'
        }

        self.policy.clc.v2.AntiAffinity.GetAll = mock.MagicMock(return_value=[mock_policy])
        self.policy.process_request()
        self.policy.module.exit_json.assert_called_once_with(changed=False,policy={})


    def testCreateWithChange(self):
        mock_policy = mock.MagicMock(spec=clc_sdk.v2.AntiAffinity)
        mock_policy.name = 'TestMaster3000'
        mock_policy.data = {'a_thing': 'happened'}
        self.policy.module.params = {
            'location': 'beer',
            'state': 'present',
            'name': 'TestMaster3000'
        }

        self.policy.clc.v2.AntiAffinity.GetAll = mock.MagicMock(return_value=[])
        self.policy.clc.v2.AntiAffinity.Create = mock.MagicMock(return_value=mock_policy)
        self.policy.process_request()
        self.policy.module.exit_json.assert_called_once_with(changed=True,policy=mock_policy.data)

    def testDeleteNoChange(self):
        mock_policy = mock.MagicMock(spec=clc_sdk.v2.AntiAffinity)
        mock_policy.name = 'TestMaster3000'
        mock_policy.data = {}
        self.policy.module.params = {
            'location': 'beer',
            'state': 'absent',
            'name': 'TestMaster3000'
        }

        self.policy.clc.v2.AntiAffinity.GetAll = mock.MagicMock(return_value=[])
        self.policy.process_request()
        self.policy.module.exit_json.assert_called_once_with(changed=False,policy=None)

    def testDeleteWithChange(self):
        mock_policy = mock.MagicMock(spec=clc_sdk.v2.AntiAffinity)
        mock_policy.name = 'TestMaster3000'
        mock_policy.data = {'a_thing': 'happened'}
        self.policy.module.params = {
            'location': 'beer',
            'state': 'absent',
            'name': 'TestMaster3000'
        }

        self.policy.clc.v2.AntiAffinity.GetAll = mock.MagicMock(return_value=[mock_policy])
        self.policy.clc.v2.AntiAffinity.Delete = mock.MagicMock(return_value=None)
        self.policy.process_request()
        self.policy.module.exit_json.assert_called_once_with(changed=True,policy=None)

    @patch.object(clc_aa_policy, 'AnsibleModule')
    @patch.object(clc_aa_policy, 'ClcAntiAffinityPolicy')
    def test_main(self, mock_ClcAAPolicy, mock_AnsibleModule):
        mock_ClcAAPolicy_instance       = mock.MagicMock()
        mock_AnsibleModule_instance     = mock.MagicMock()
        mock_ClcAAPolicy.return_value   = mock_ClcAAPolicy_instance
        mock_AnsibleModule.return_value = mock_AnsibleModule_instance

        clc_aa_policy.main()

        mock_ClcAAPolicy.assert_called_once_with(mock_AnsibleModule_instance)
        assert mock_ClcAAPolicy_instance.process_request.call_count ==1

    @patch.object(clc_aa_policy, 'clc_sdk')
    def test_create_aa_policy_error(self, mock_clc_sdk):
        under_test = ClcAntiAffinityPolicy(self.module)
        policy = {
            'name': 'dummyname',
            'location': 'dummylocation'
        }
        error = CLCException('Failed')
        error.response_text = 'I am failed'
        mock_clc_sdk.v2.AntiAffinity.Create.side_effect = error
        under_test.clc = mock_clc_sdk
        ret = under_test._create_policy(policy)
        self.module.fail_json.assert_called_with(msg='Failed to create anti affinity policy : dummyname. I am failed')

    @patch.object(clc_aa_policy, 'clc_sdk')
    def test_delete_aa_policy_error(self, mock_clc_sdk):
        under_test = ClcAntiAffinityPolicy(self.module)
        error = CLCException('Failed')
        error.response_text = 'I am failed'
        policy_mock = mock.MagicMock()
        policy_mock.Delete.side_effect = error
        under_test.policy_dict['dummyname'] = policy_mock
        under_test.clc = mock_clc_sdk
        policy = {
            'name': 'dummyname',
            'location': 'dummylocation'
        }
        ret = under_test._delete_policy(policy)
        self.module.fail_json.assert_called_with(msg='Failed to delete anti affinity policy : dummyname. I am failed')



if __name__ == '__main__':
    unittest.main()
