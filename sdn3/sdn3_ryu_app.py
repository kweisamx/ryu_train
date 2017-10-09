from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER



class MySwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]


    def __init__(self, *args,**kwargs):
        super(MySwitch,self).__init__(*args,**kwargs)
        self.mac_to_port = {} # Mac address is defined

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures,CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print("send request")
        self.send_port_stats_request(datapath)# send the request

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]

        mod = parser.OFPFlowMod(datapath=datapath,priority=priority,match=match,instructions=inst)
        datapath.send_msg(mod)


    def send_port_stats_request(self, datapath):
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
    
        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        ports = []
        for stat in ev.msg.body:
            if stat.port_no <=ofproto.OFPP_MAX: 
                ports.append(stat.port_no)
        print ports
        for no in ports:
            in_port = no
            match = ofp_parser.OFPMatch(in_port = in_port)
            for other_no in ports:
                if other_no != in_port:
                    out_port = other_no
            actions = [ofp_parser.OFPActionOutput(out_port)]
            print in_port, out_port
            self.add_flow(datapath, 1, match, actions)
