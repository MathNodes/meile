from subprocess import Popen, PIPE, STDOUT
import collections
from prettytable import PrettyTable
from os import path

IBCSCRT = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
BASEDIR = path.join(path.expanduser('~'), '.sentinelcli')

NodesInfoKeys = ["Moniker","Address","Provider","Price","Country","Speed","Latency","Peers","Handshake","Version","Status"]

dash = "-"


def get_nodes():
    AllNodesInfo = []
    nodeCMD = ["sentinelcli", "query", "nodes", "--node", "https://rpc.mathnodes.com:4444", "--limit", "20000"]

    NodeTable = PrettyTable()    
    proc = Popen(nodeCMD, stdout=PIPE)
    
    k=1
    
    print()
    for line in proc.stdout.readlines():
        #print(line)
        if k < 4:  
            k += 1 
            continue
        if k >=4 and '+-------+' in str(line.decode('utf-8')):
            break
        elif "freak12techno" in str(line.decode('utf-8')):
            ninfos = []
            ninfos.append(str(line.decode('utf-8')).split('|')[1])
            for ninf in str(line.decode('utf-8')).split('|')[3:-1]:
                ninfos.append(ninf)
            AllNodesInfo.append(dict(zip(NodesInfoKeys, ninfos)))
                          
        else: 
            ninfos = str(line.decode('utf-8')).split('|')[1:-1]
            AllNodesInfo.append(dict(zip(NodesInfoKeys, ninfos)))
            #print(ninfos, end='\n')
    
    #get = input("Blah: ")
    AllNodesInfoSorted = sorted(AllNodesInfo, key=lambda d: d[NodesInfoKeys[4]], reverse=True)
    result = collections.defaultdict(list)
    
    for d in AllNodesInfoSorted:
        for k, v in d.items():
            if IBCSCRT in v:
                v = v.replace(IBCSCRT,'uscrt')
            result[k].append(v.lstrip().rstrip())
            
    
    
    #country = input("Country: ")
    
    #pos = [i for i,val in enumerate(result[NodesInfoKeys[4]]) if val.upper() == country.upper()]
            
    #pos = list(locate(result[NodesInfoKeys[4]], lambda x: x.upper() == country.upper()))
    
    
    pos = len(result[NodesInfoKeys[4]])
    
    NodeTable.field_names = [NodesInfoKeys[0],NodesInfoKeys[1], NodesInfoKeys[3],NodesInfoKeys[4],
                                                                                NodesInfoKeys[5],
                                                                                NodesInfoKeys[6],
                                                                                NodesInfoKeys[7],
                                                                                "HS",
                                                                                NodesInfoKeys[10]]
   
    #NodeData.append(173*dash)
    for e in range(pos):
        NodeTable.add_row([result[NodesInfoKeys[0]][e],result[NodesInfoKeys[1]][e],result[NodesInfoKeys[3]][e],
                                                                                result[NodesInfoKeys[4]][e],
                                                                                result[NodesInfoKeys[5]][e],
                                                                                result[NodesInfoKeys[6]][e],
                                                                                result[NodesInfoKeys[7]][e],
                                                                                result[NodesInfoKeys[8]][e],
                                                                                result[NodesInfoKeys[10]][e]])
                           
 
    NodeTableString = NodeTable.get_string()
    
    NodeData = NodeTableString.split('\n')
    
    return NodeData,result

def get_subscriptions(result, ADDRESS):
    SubsNodesInfo = []
    SubsInfoKeys = ["ID", "Owner", "Plan", "Expiry", "Denom", "Node", "Price", "Deposit", "Free", "Status"]
    subsCMD = ["sentinelcli", "query", "subscriptions", "--node", "https://rpc.mathnodes.com:4444", "--status", "Active", "--limit", "100", "--address" ,ADDRESS]
    SubsTable = PrettyTable()
    proc = Popen(subsCMD, stdout=PIPE)

    k=1
    for line in proc.stdout.readlines():
        #print(line)
        if k < 4:
            k += 1 
            continue
        else: 
            ninfos = str(line.decode('utf-8')).lstrip().rstrip().split('|')[1:-1]
            SubsNodesInfo.append(dict(zip(SubsInfoKeys, ninfos)))
            
    SubsResult = collections.defaultdict(list)
    
    for d in SubsNodesInfo:
        for k, v in d.items():
            if IBCSCRT in v:
                v = v.replace(IBCSCRT,'uscrt')
            SubsResult[k].append(v.lstrip().rstrip())
            
    SubsAddressSet = set(SubsResult[SubsInfoKeys[5]])
    #NodesAddressSet = set(result[NodesInfoKeys[1]])
    
    # The Index of Subscription Address in All Data
    Nodespos = [i for i,val in enumerate(result[NodesInfoKeys[1]]) if val in SubsAddressSet]
    NodeAddys = [val for i,val in enumerate(result[NodesInfoKeys[1]]) if val in SubsAddressSet]
    
    # Available Subscriptions
    #Subspos = [i for i,val in enumerate(SubsResult[SubsInfoKeys[5]]) if val in NodesAddressSet]
    #SubsAddys = [val for i,val in enumerate(SubsResult[SubsInfoKeys[5]]) if val in NodesAddressSet]
    #print(Subspos)
    #print(SubsResult[SubsInfoKeys[5]])
    
    SubsTable.field_names = [SubsInfoKeys[0],
                            "Moniker",
                            SubsInfoKeys[5],
                            SubsInfoKeys[6],
                            SubsInfoKeys[7],
                            "Country",
                            "Allocated",
                            "Consumed"]

    #SubsData.append(173*dash)
    
    k=0
    j=0
    # This would be the more efficent algorithm. Not a fan of O(n^2)
    #for e1,e2 in zip(Nodespos,Subspos):
    for sub in SubsResult[SubsInfoKeys[5]]:
        for node in NodeAddys:
            if sub == node:
                quotaCMD = ['sentinelcli', 'query', 'quotas', '--node', 'https://rpc.mathnodes.com:4444', '--page', '1', SubsResult[SubsInfoKeys[0]][k]]
        
                proc = Popen(quotaCMD, stdout=PIPE)
                
                h=1
                for line in proc.stdout.readlines():
                    #print(line)
                    if h < 4:
                        h += 1 
                        continue
                    if h >=4 and '+-----------+' in str(line.decode('utf-8')):
                        break
                    else:
                        nodeQuota = str(line.decode('utf-8')).split("|")[2:-1]
                SubsTable.add_row([SubsResult[SubsInfoKeys[0]][k],
                                    result[NodesInfoKeys[0]][Nodespos[j]],
                                    SubsResult[SubsInfoKeys[5]][k],
                                    SubsResult[SubsInfoKeys[6]][k],
                                    SubsResult[SubsInfoKeys[7]][k],
                                    result[NodesInfoKeys[4]][Nodespos[j]],
                                    nodeQuota[0],
                                    nodeQuota[1]])

                break
            else:
                j += 1
                continue
        j=0
        k += 1
    SubsTableString = SubsTable.get_string()
    
    SubsData = SubsTableString.split('\n')
     
    return SubsData

def disconnect():
    ifCMD = ["ifconfig", "-a"]
    ifgrepCMD = ["grep", "-oE", "wg[0-9]+"]
    partCMD = ["sentinelcli", "disconnect"]
    
    ifoutput = Popen(ifCMD,stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    grepoutput = Popen(ifgrepCMD, stdin=ifoutput.stdout, stdout=PIPE, stderr=STDOUT)
    wgif = grepoutput.communicate()[0]
    wgif_file = str(wgif.decode('utf-8')).replace("\n", '') + ".conf"

    CONFFILE = path.join(BASEDIR, wgif_file)
    wg_downCMD = ['wg-quick', 'down', CONFFILE]
        
    proc1 = Popen(partCMD)
    proc1.wait(timeout=10)
    
    proc = Popen(wg_downCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = proc.communicate()
    return proc.returncode

def connect(ID, address, keyname):
    connCMD = ["sentinelcli", "connect", "--keyring-backend", "os", "--chain-id", "sentinelhub-2",
               "--node", "https://rpc.mathnodes.com:4444", "--gas-prices", "0.1udvpn", "--yes", "--from",keyname, ID, address]
    proc = Popen(connCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = proc.communicate()
    return proc.returncode

def subscribe(KEYNAME, NODE, DEPOSIT):

    subscribeCMD = ["sentinelcli", "tx", "subscription", "subscribe-to-node", "--home", BASEDIR,  "--yes",
                    "--keyring-backend", "os", "--gas-prices", "0.1udvpn", "--chain-id", "sentinelhub-2",
                    "--node", "https://rpc.mathnodes.com:4444", "--from", "%s" % KEYNAME, NODE, DEPOSIT]
    
    subproc = Popen(subscribeCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = subproc.communicate()
    #print(proc_out+proc_err)
    return subproc.returncode
    
    
    
    