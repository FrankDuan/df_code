#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_serialization import jsonutils

from neutron.agent.linux.utils import wait_until_true

from dragonflow.common import utils as df_utils
from dragonflow.db.db_common import DbUpdate, SEND_ALL_TOPIC
from dragonflow.db.pub_sub_api import TableMonitor
from dragonflow.tests.common import utils as test_utils
from dragonflow.tests.fullstack import test_base
from dragonflow.tests.fullstack import test_objects as objects
from dragonflow.tests.common.utils import OvsFlowsParser

class TestTopology(test_base.DFTestBase):

    def setUp(self):
        super(TestTopology, self).setUp()
        self.en_sel_topo_dist = \
            cfg.CONF.df.enable_selective_topology_distribution

    def tearDown(self):
        super(TestTopology, self).tearDown()

    def test_topology_create_vm(self):
        """
        Add a VM. Verify it's ARP flow is there.
        """
        network = self.store(objects.NetworkTestObj(self.neutron, self.nb_api))
        network_id = network.create(network={'name': 'topo_net1'})
        subnet = {'network_id': network_id,
            'cidr': '192.168.101.0/24',
            'gateway_ip': '192.168.101.1',
            'ip_version': 4,
            'name': 'topo_net1',
            'enable_dhcp': True}
        subnet = self.neutron.create_subnet({'subnet': subnet})

        vm = self.store(objects.VMTestObj(self, self.neutron))
        vm.create(network=network)
        ip = vm.get_first_ipv4()

    def _get_arp_table_flows(self):
        ovs_flows_parser = OvsFlowsParser()
        flows = ovs_flows_parser.dump()
        flows = [flow for flow in flows
                if flow['table'] == str(const.ARP_TABLE) + ',']
        return flows
