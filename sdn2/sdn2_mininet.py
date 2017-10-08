from mininet.log import setLogLevel,info
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI


def MininetTopo():
    net = Mininet()
    info("Create host nodes.\n")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    


    info("Create switch node.\n")
    #s1 = net.addSwitch("s1",failMode = 'standalone')
    s1 = net.addSwitch("s1",failMode = 'secure',protocols = 'OpenFlow13')

    info("Create Links. \n")
    net.addLink(h1,s1)
    net.addLink(h2,s1)

    info("Create controller ot switch. \n")
    net.addController(controller=RemoteController,ip='140.113.207.84',port=6633)

    info("Build and start network.\n")
    net.build()
    net.start()
    info("Run the mininet CLI")
    CLI(net)


if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()
