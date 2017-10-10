from mininet.log import setLogLevel,info
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
from optparse import OptionParser
def SetParse():
    parser = OptionParser()
    parser.add_option("-n","--number",type="int",dest="switch_num",help="write the switch number",default=1 )
    return parser.parse_args()
def MininetTopo(switch_num):
    net = Mininet()
    info("Create host nodes.\n")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    


    info("Create switch node.\n")
    #s1 = net.addSwitch("s1",failMode = 'standalone')
    #s1 = net.addSwitch("s1",failMode = 'secure',protocols = 'OpenFlow13')
    for sw in range(1,switch_num+1):
        name = "s"+str(sw)
        name = net.addSwitch(name,failMode = 'secure',protocols = 'OpenFlow13')

    info("Create Links. \n")
    for link in range(0,switch_num+1):
        if link is 0:
            net.addLink(h1,"s"+str(link+1))
        elif link is switch_num:
            net.addLink(h2,"s"+str(link))
        else:
            net.addLink("s"+str(link),"s"+str(link+1))

    info("Create controller ot switch. \n")
    net.addController(controller=RemoteController,ip='140.113.207.84',port=6633)

    info("Build and start network.\n")
    net.build()
    net.start()
    info("Run the mininet CLI")
    CLI(net)


if __name__ == '__main__':
    setLogLevel('info')
    # Set Parse
    (options, args) = SetParse()
    print(options.switch_num)

    MininetTopo(options.switch_num)
