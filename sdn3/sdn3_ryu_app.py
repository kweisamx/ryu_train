from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import ether_types,lldp,packet,ethernet


class MySwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    link = []

    def __init__(self, *args,**kwargs):
        super(MySwitch,self).__init__(*args,**kwargs)
        self.mac_to_port = {} # Mac address is defined
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures,CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #set if packet is lldp, send to controller
        actions = [parser.OFPActionOutput(port=ofproto.OFPP_CONTROLLER,
                                          max_len=ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(type_=ofproto.OFPIT_APPLY_ACTIONS,actions=actions)]
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_LLDP)
        
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=1,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)

        self.send_port_desc_stats_request(datapath)# send the request


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]

        mod = parser.OFPFlowMod(datapath=datapath,priority=priority,match=match,instructions=inst)
        datapath.send_msg(mod)


    def send_port_desc_stats_request(self, datapath):
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
    
        req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)


    # Send the lldp packet
    def send_lldp_packet(self, datapath, port, hw_addr, ttl):
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=ether_types.ETH_TYPE_LLDP,src=hw_addr ,dst=lldp.LLDP_MAC_NEAREST_BRIDGE))

        chassis_id = lldp.ChassisID(subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED, chassis_id=str(datapath.id))
        port_id = lldp.PortID(subtype=lldp.PortID.SUB_LOCALLY_ASSIGNED, port_id=str(port))
        ttl = lldp.TTL(ttl=30)
        end = lldp.End()
        tlvs = (chassis_id,port_id,ttl,end)
        pkt.add_protocol(lldp.lldp(tlvs))
        pkt.serialize()
        self.logger.info("packet-out %s" % pkt)
        data = pkt.data
        actions = [ofp_parser.OFPActionOutput(port=port)]
        out = ofp_parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)


    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        ports = []
        for stat in ev.msg.body:
            if stat.port_no <=ofproto.OFPP_MAX: 
                ports.append({'port_no':stat.port_no,'hw_addr':stat.hw_addr})
        for no in ports:
            in_port = no['port_no']
            match = ofp_parser.OFPMatch(in_port = in_port)
            for other_no in ports:
                if other_no['port_no'] != in_port:
                    out_port = other_no['port_no']
            self.send_lldp_packet(datapath,no['port_no'],no['hw_addr'],10)
            actions = [ofp_parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser


        pkt = packet.Packet(data=msg.data)
        dpid = datapath.id # switch id which send the packetin
        in_port  = msg.match['in_port']

        pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
        pkt_lldp = pkt.get_protocol(lldp.lldp)
        if not pkt_ethernet:
            return 
        #print(pkt_lldp)
        if pkt_lldp:
            self.handle_lldp(dpid,in_port,pkt_lldp.tlvs[0].chassis_id,pkt_lldp.tlvs[1].port_id)


        #self.logger.info("packet-in %s" % (pkt,))

    # Link two switch
    def switch_link(self,s_a,s_b):
        return s_a + '<--->' + s_b
            
    def handle_lldp(self,dpid,in_port,lldp_dpid,lldp_in_port):
        switch_a = 'switch'+str(dpid)+', port'+str(in_port)
        switch_b = 'switch'+lldp_dpid+', port'+lldp_in_port
        link = self.switch_link(switch_a,switch_b)

        # Check the switch link is existed
        if not any(self.switch_link(switch_b,switch_a) == search for search in self.link):
            self.link.append(link)


        print(self.link)
