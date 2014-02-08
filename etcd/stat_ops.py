import requests
import re

from urlparse import parse_qsl
from collections import namedtuple
from datetime import timedelta, datetime

from etcd.common_ops import CommonOps
from etcd.response import ResponseV2 


class StatOps(CommonOps):
    """Functions that query the server for statistics information."""

    def get_leader_stats(self):
        """Returns leader and follower information.

        :returns: Tuple of leader name and follower dictionary
        :rtype: namedtuple
        """
        
        r = self.client.send(2, 'get', '/stats/leader', return_raw=True)
        data = r.json()

        F = namedtuple('LStatFollower', ['counts', 'latency'])
        C = namedtuple('LStatCounts', ['fail', 'success'])
        L = namedtuple('LStatLatency', 
                       ['average', 'current', 'maximum', 'minimum', 
                        'standard_deviation'])

        followers = {}
        for name, block in data['followers'].iteritems():
            counts_raw = block['counts']
            counts = C(fail=counts_raw['fail'], 
                       success=counts_raw['success'])

            latency_raw = block['latency']
            latency = L(average=latency_raw['average'],
                        current=latency_raw['current'],
                        maximum=latency_raw['maximum'],
                        minimum=latency_raw['minimum'],
                        standard_deviation=latency_raw['standardDeviation'])

            followers[name] = F(counts=counts, latency=latency)

        return (data['leader'], followers)

    def get_self_stats(self):
        """Returns stats regarding the current node.

        :returns: Statistics data for host
        :rtype: namedtuple
        """
        
        r = self.client.send(2, 'get', '/stats/self', return_raw=True)
        data = r.json()

        S = namedtuple('SStat', ['leader_info', 'name', 
                                 'recv_append_request_cnt', 
                                 'send_append_request_cnt', 
                                 'send_bandwidth_rate', 
                                 'send_pkg_rate', 'start_time', 'state'])

        L = namedtuple('SStatLeader', ['leader', 'uptime'])

        leader_info_raw = data['leaderInfo']

        hours = 0
        minutes = 0
        seconds = 0
        
        match = re.match('([0-9]+)h([0-9]+)m([0-9]+\.[0-9]+)s', 
                         leader_info_raw['uptime'])

        if match is not None:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
        else:
            match = re.match('([0-9]+)m([0-9]+\.[0-9]+)s', 
                             leader_info_raw['uptime'])
            
            if match is not None:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
            else:
                match = re.match('([0-9]+\.[0-9]+)s', 
                                 leader_info_raw['uptime'])
                
                if match is None:
                    raise ValueError("Could not understand leader-uptime value: %s" % 
                                     (leader_info_raw['uptime']))

                seconds = float(match.group(1))

        uptime = hours * 3600 + minutes * 60 + seconds
        leader_info = L(leader=leader_info_raw['leader'], 
                        uptime=timedelta(seconds=uptime))

        start_time_raw = data['startTime']
        pivot = start_time_raw.rfind('.')

# TODO(dustin): At this time, we won't worry about the timezone component, and
#               will assume that the client is operating in the same zone as
#               the cluster.        
        start_time = datetime.strptime(start_time_raw[:pivot], 
                                       '%Y-%m-%dT%H:%M:%S')

        return S(leader_info=leader_info, name=data['name'], 
                 recv_append_request_cnt=data['recvAppendRequestCnt'],
                 send_append_request_cnt=data['sendAppendRequestCnt'],
                 send_bandwidth_rate=data['sendBandwidthRate'],
                 send_pkg_rate=data['sendPkgRate'], 
                 start_time=start_time, state=data['state'])

