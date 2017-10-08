from mininet.log import setLogLevel,info
from mininet.net import Mininet
from mininet.cli import CLI

# it need match with mininet CLI
'''
class Sdn1(Topo):
    def __init__(self):
        "Create sdn1 topo"
        Topo.__init__(self)

        # Add hosts and switch
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1',failMode='standalone')
        # Add links
        self.addLink(s1,h1)
        self.addLink(s1,h2)
topos = {'sdn1':(lambda: Sdn1())}
'''

def MininetTopo():
    net = Mininet()
    info("Create host nodes.\n")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    


    info("Create switch node.\n")
    #s1 = net.addSwitch("s1",failMode = 'standalone')
    s1 = net.addSwitch("s1",failMode = 'secure')

    info("Create Links. \n")
    net.addLink(h1,s1)
    net.addLink(h2,s1)

    info("Build and start network.\n")
    net.build()
    net.start()
    info("Run the mininet CLI")
    CLI(net)


if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()
