from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import ethernet, ether_types, ipv4, tcp, udp

class QosController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QosController, self).__init__(*args, **kwargs)

        # Define queues
        self.queues = {
            's6': {
                'q0': {'min': 2000000, 'max': 5000000},
                'q1': {'min': 2000000, 'max': 5000000},
                'q2': {'min': 5000000, 'max': 10000000},
                'q3': {'min': 10000000, 'max': 15000000},
                'q4': {'min': 20000000, 'max': 25000000},
                'q5': {'min': 30000000, 'max': 40000000}
            },
            's7': {
                'q0': {'min': 2000000, 'max': 5000000},
                'q1': {'min': 2000000, 'max': 5000000},
                'q2': {'min': 5000000, 'max': 10000000},
                'q3': {'min': 10000000, 'max': 15000000},
                'q4': {'min': 20000000, 'max': 25000000},
                'q5': {'min': 30000000, 'max': 40000000}
            },
            's8': {
                'q0': {'min': 2000000, 'max': 5000000},
                'q1': {'min': 2000000, 'max': 5000000},
                'q2': {'min': 5000000, 'max': 10000000},
                'q3': {'min': 10000000, 'max': 15000000},
                'q4': {'min': 20000000, 'max': 25000000},
                'q5': {'min': 30000000, 'max': 40000000}
            }
        }

        # Define host IPs
        self.host_ips = {
            'h1': '10.0.0.1',
            'h2': '10.0.0.2',
            'h3': '10.0.0.3',
            'h4': '10.0.0.4',
            'h5': '10.0.0.5'
        }

        # Define expected delays for hosts
        self.expected_delays = {
            'h1': float('inf'),
            'h2': 100,
            'h3': 50,
            'h4': 30,
            'h5': float('inf')
        }

        # Define current queues for hosts
        self.host_queues = {
            'h1': 'q0',
            'h2': 'q2',
            'h3': 'q3',
            'h4': 'q4',
            'h5

##########Cutted here#########3

# Define the queue mapping for each host
queue_mapping = {
    "10.0.1.1": 1,   # h1 => q1
    "10.0.2.1": 2,   # h2 => q2
    "10.0.3.1": 3,   # h3 => q3
    "10.0.4.1": 4,   # h4 => q4
    "10.0.5.1": 5,   # h5 => q5
}

# Define the minimum and maximum bandwidth for each queue
queue_bandwidth = {
    0: (0, 2),    # q0 => 0-2 Mbps
    1: (2, 5),    # q1 => 2-5 Mbps
    2: (5, 10),   # q2 => 5-10 Mbps
    3: (10, 15),  # q3 => 10-15 Mbps
    4: (20, 25),  # q4 => 20-25 Mbps
    5: (30, 40),  # q5 => 30-40 Mbps
}

# Define the expected maximum delay for each host
expected_delays = {
    "10.0.2.1": 100,  # h2 => 100 ms
    "10.0.3.1": 50,   # h3 => 50 ms
    "10.0.4.1": 30,   # h4 => 30 ms
}

# Define the current queue allocation for each host
current_queues = {
    "10.0.1.1": 1,   # h1 => q1
    "10.0.2.1": 2,   # h2 => q2
    "10.0.3.1": 3,   # h3 => q3
    "10.0.4.1": 4,   # h4 => q4
    "10.0.5.1": 5,   # h5 => q5
}

# Define a function to update the queue allocation based on the current delay
def update_queues(delay_stats):
    # Check if any host is experiencing delay greater than expected
    delayed_hosts = [host for host, delay in delay_stats.items() if delay > expected_delays.get(host, 0)]
    if not delayed_hosts:
        # All hosts are within expected delay, revert to the initial queue allocation
        for host, queue in current_queues.items():
            add_flow_to_switch(dpid=middle_switches[0], in_port=host_to_port[host], queue_id=queue)
        return
    
    # Sort the delayed hosts by the severity of the delay (highest delay first)
    delayed_hosts = sorted(delayed_hosts, key=lambda host: delay_stats[host], reverse=True)
    
    # Determine the new queue allocation based on the number of delayed hosts
    if len(delayed_hosts) == 1:
        # One host is delayed, move its traffic to a higher priority queue
        host = delayed_hosts[0]
        old_queue = current_queues[host]
        new_queue = old_queue + 1
        if new_queue > 5:
            new_queue = 5
        current_queues[host] = new_queue
        add_flow_to_switch(dpid=middle_switches[0], in_port=host_to_port[host], queue_id=new_queue)
    else:
        # Multiple hosts are delayed, move their traffic to higher priority

#######Cutted here#########

def update_queues(delay_stats, queues, max_bandwidth):
    """
    Update queues according to delay_stats.
    """
    for host, delay in delay_stats.items():
        if delay > expected_delays[host]:
            # Traffic from this host needs to be moved to a higher queue
            queue_index = queue_mapping[host] + 1
            if queue_index == len(queues):
                # Traffic from this host needs to be dropped
                print(f"Traffic from {host} is being dropped due to excessive delay")
            else:
                # Traffic from this host needs to be moved to the next queue
                queues[queue_index].add_traffic(queues[queue_mapping[host]].remove_traffic(delay), max_bandwidth[queue_index])
                queue_mapping[host] = queue_index

########Cutted here########

def load_balancing(event):
    """
    Monitor the load on the middle switches and inject appropriate flows to balance the traffic.
    """
    for switch in middle_switches:
        # Get the switch stats from the event
        stats = event.msg.body[0]
        if switch.dp.id == stats.node_id:
            # Calculate the load on the switch
            load = stats.tx_bytes / stats.tx_time * 8 / 1000 / 1000
            # Calculate the average load on the other middle switches
            avg_load = (total_load - load) / (len(middle_switches) - 1)
            # Calculate the difference between the load on this switch and the average load
            diff = load - avg_load
            if diff > 0:
                # This switch is overloaded, inject a flow to balance the traffic
                in_port = 1
                out_port = 2
                if switch.dp.id == s7.dp.id:
                    in_port = 2
                    out_port = 1
                match = switch.dp.ofproto_parser.OFPMatch()
                actions = [switch.dp.ofproto_parser.OFPActionOutput(out_port)]
                inst = [switch.dp.ofproto_parser.OFPInstructionActions(switch.dp.ofproto.OFPIT_APPLY_ACTIONS, actions)]
                mod = switch.dp.ofproto_parser.OFPFlowMod(
                    datapath=switch.dp, match=match, cookie=0, command=switch.dp.ofproto.OFPFC_ADD,
                    idle_timeout=0, hard_timeout=0, priority=1, flags=0, instructions=inst, buffer_id=None, out_port=in_port,
                    out_group=switch.dp.ofproto.OFPG_ANY
                )
                switch.dp.send_msg(mod)
