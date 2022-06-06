#!/bin/env python3

import configparser
import pkg_resources
import shutil
import npyscreen
import requests
import re
from sys import exit
from os import path
import os
from time import time
from cli.sentinel import get_nodes, get_subscriptions,connect, disconnect, get_balance
from cli.sentinel import subscribe as SentinelSubscribe
from datetime import datetime
from prettytable import PrettyTable
from urllib3.exceptions import InsecureRequestWarning

from curses import KEY_F2, KEY_F3, KEY_F5, KEY_F6, KEY_F7, COLOR_CYAN


BASEDIR = path.join(path.expanduser('~'), '.meile')
CONFFILE = path.join(BASEDIR, 'config.ini')
CONFIG = configparser.ConfigParser()
LOGOFILE = os.path.join(BASEDIR, 'logo.uni')
MEILEVERSION = "MEILE v0.5.0"
ICANHAZURL = "https://icanhazip.com"
NODEAPIURL = 'https://api.sentinel.mathnodes.com/nodes/'

KEY_C = 67
KEY_D = 68
KEY_H = 72
KEY_I = 73
KEY_S = 83

def read_configuration(confpath):
    """Read the configuration file at given path."""
    # copy our default config file
    
    if os.path.isdir(BASEDIR):
        if not os.path.isfile(confpath):
            defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
            defaultlogo = pkg_resources.resource_filename(__name__, 'logo.uni')
            shutil.copyfile(defaultconf, CONFFILE)
            shutil.copyfile(defaultlogo, LOGOFILE)

    else:
        os.mkdir(BASEDIR)
        defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
        defaultlogo = pkg_resources.resource_filename(__name__, 'logo.uni')
        shutil.copyfile(defaultconf, CONFFILE)
        shutil.copyfile(defaultlogo, LOGOFILE)
        
    CONFIG.read(confpath)
    return CONFIG

    
class BoxTitle(npyscreen.BoxTitle):
    _contained_widget = npyscreen.SelectOne

class IBCCoinCheckBox(npyscreen.SelectOne):
    _contained_widgets = npyscreen.CheckBox
    _contained_widget_height = 1
    
    def display_value(self, vl):
        return vl

class MeileApplication(npyscreen.NPSAppManaged):
    def onStart(self):

        self.addForm('MAIN', MainApp, name=MEILEVERSION, color="STANDOUT")

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def change_form(self, name):
        # Switch forms.  NB. Do *not* call the .edit() method directly (which 
        # would lead to a memory leak and ultimately a recursion error).
        # Instead, use the method .switchForm to change forms.
        self.switchForm(name)
        
        # By default the application keeps track of every form visited.
        # There's no harm in this, but we don't need it so:        
        self.resetHistory()


class MainApp(npyscreen.FormWithMenus):
    

    SubsData = []
    NodeData = []
    result   = []
    ibc_coins = ["udvpn","uscrt","uatom","udec","uosmo"]
    ip = ""
    old_ip = ""
    CONNECTED = False
    price = deposit = dataGB = None
        
    def create(self):
        global CONFIG
        
        ADDRESS = CONFIG['wallet'].get('address', '')
        WALLET  = CONFIG['wallet'].get('keyname', '')
        
        self.keypress_timeout = 5

        
        self.y,self.x = self.curses_pad.getmaxyx()

        self.timeWidget = self.add(npyscreen.Textfield, name=" ",
                                    value=self.getTimeDate(),
                                    editable = None, 
                                    relx = int((self.x - len(self.getTimeDate().split('\n')[-1])-7) / 2))
        

        req = requests.get(ICANHAZURL)
        self.ip = req.text
        self.old_ip = self.ip
        
        IPDATA = ["NEW IP: " + self.ip, "OLD IP: " + self.old_ip]  

        with open(LOGOFILE, 'r') as logo:
            data = logo.readlines()
            
        columns = shutil.get_terminal_size().columns
        rows = int(int(shutil.get_terminal_size().lines) / 2)
        newline = "\n"
        if not rows*2 >= 67 or not columns >= 221:
            exit("Terminal not big enough. Please make sure your terminal is at least 66x240 (rows x col). Use 'stty size' to determine and adjust appropriately.")
        print(rows*newline,"Loading.... (%s x %s)".center(columns) % (rows*2, columns), end=' ')
        linlen=len(data[2])
        self.logo = self.add(npyscreen.BoxTitle, values=data, rely=4, relx= int((self.x - linlen) / 2),
               max_width=linlen+7,max_height=len(data)+2)
        self.logo.editable = False 
        
        
        CoinData = self.get_wallet_balances(WALLET, ADDRESS)
            
        

        self.ipBox = self.add(npyscreen.BoxTitle, values = IPDATA, rely=5, relx = 3, max_height=4, max_width = 30, editable = None )
        self.coinBox = self.add(npyscreen.BoxTitle, values = CoinData, rely = 3,relx = self.x - 50, max_height = 9, max_width = 40, editable = None)
        
        
        self.add(npyscreen.FixedText,rely=2, relx= self.x - 50, value="Press, H, for help / CTRL+x, for menu", editable = None)
        #self.add(npyscreen.FixedText,rely=9, relx= self.x - 58, value="Wallet: %s" % WALLET, editable = None)
        #self.add(npyscreen.FixedText,rely=10, relx= self.x - 58, value="Address: %s" % ADDRESS, editable = None)
        
                 
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItem(text="1.) Connect",onSelect=self.connect_subscription,shortcut="C")
        self.m1.addItem(text="2.) Disconnect",onSelect=self.part_subscription,shortcut="D")
        self.m1.addItem(text="3.) Subscribe",onSelect=self.subscribe,shortcut="S")
        
        self.NodeData,self.result = get_nodes()
        self.SubsData = get_subscriptions(self.result, ADDRESS)
        self.dVPNs = self.add(BoxTitle, name="Sentinel Nodes", values=self.NodeData,
                                    max_height=self.y - 30, width = self.x - 6, rely = 11,
                                    scroll_exit = True, editable = True,
                                    contained_widget_arguments={
                                        'color': "CAUTION", 
                                        'widgets_inherit_color': False,}
                                    )


        self.subs = self.add(BoxTitle, name="Active Subscriptions", values=self.SubsData,
                                    max_height=10, width = self.x - 10, rely = self.y - 18,
                                    scroll_exit = True, editable = True,
                                    contained_widget_arguments={
                                        'color': "CAUTION", 
                                        'widgets_inherit_color': False,}
                                    )
        self.add(npyscreen.FixedText, rely = self.y -7, value="Selected Node", max_width = 13)
        self.ibc_check_box = self.add(IBCCoinCheckBox, max_height=5, name="Testing", values=self.ibc_coins, slow_scroll=False, relx = 72 + 82, rely = self.y -7)

        self.node = self.add(npyscreen.TitleText, name = "Node: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 6, editable = None, max_width = 60)
        self.id = self.add(npyscreen.TitleText, name = "ID: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 5, editable = None, max_width = 30)
        self.address = self.add(npyscreen.TitleText, name = "Address: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 4, editable = None, max_width = 54)
        self.deposit = self.add(npyscreen.TitleText, name = "Deposit: ", max_width = 57, value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 6, relx = 72, editable = None )
        self.price = self.add(npyscreen.TitleText, name = "Price: ", value=None, max_width = 70, use_two_lines = False, begin_entry_at = 10, rely = self.y - 5, relx = 72, editable = None )
        self.dataGB = self.add(npyscreen.TitleSlider, max_width = 80, label=True, name="GB", value=19, out_of = 1000, step = 2, block_color = COLOR_CYAN, rely = self.y - 3, relx = 72)
        #self.add(npyscreen.FixedText, rely = self.y - 3, value="Use the menu to Connect/Subscribe (CTRL+X)", editable = None)
        self.add_handlers({KEY_F2: self.display_boxy})
        self.add_handlers({KEY_F3: self.display_boxy2})
        self.add_handlers({KEY_F5: self.reloadsubs})
        self.add_handlers({KEY_F7: self.reloadnodes})
        self.add_handlers({KEY_H: self.helpme})
        self.add_handlers({KEY_C: self.connect_subscription})
        self.add_handlers({KEY_D: self.part_subscription})
        self.add_handlers({KEY_S: self.subscribe})
        self.add_handlers({KEY_I: self.expand_node_info})

    def while_waiting(self):
        if self.price.value:
            #mu_coin = re.findall(r'\D+', self.price.value)[0]
            if self.ibc_check_box.value:
                mu_coin = self.ibc_coins[self.ibc_check_box.value[0]]
                mu_amt_coin = re.findall(r'[0-9]+' + mu_coin, self.price.value)[0]
                mu_amt = re.findall(r'[0-9]+', mu_amt_coin)[0]
                self.deposit.value = str(int(int(self.dataGB.value) * int(mu_amt))) + mu_coin 
                self.deposit.display()
    
    def helpme(self, *args, **keywords):
        
        message='''
                HELP SCREEN (%s) (MathNodes)
                
                Commands:
                F2           - Load Subscription Data to Connect to Node
                F3           - Load Node Info to Subscribe to Node
                F5           - Refresh Subscription data (Useful after subscribing)
                F7           - Refresh Node Data
                PGDN         - Scroll the data downwards
                PGUP         - Scroll the data upwards
                Enter/Space  - Select a node
                CTRL+X       - Display the Menu
                l            - Search with data box (Nodes, Subscriptions)
                L            - Reset filter and go to top
                n            - go to next entry of search results
                H            - This help screen
                S            - Subscribe to loaded node data (from F3)
                D            - Disconnect from connectd node
                C            - Connect to loaded subscription (From F2)
                I            - Select Node and Get Additional Information
                ''' % MEILEVERSION
        npyscreen.notify_confirm(message, title="Meile HELP v0.2.0 (MathNodes)", form_color = "STANDOUT" , wide=True)
                
        
    def reloadsubs(self, *args, **keywords):
        global CONFIG
        ADDRESS = CONFIG['wallet'].get('address','')
        npyscreen.notify("Relading Subscriptions... Please wait...", title="Meile Subscriptions")
        self.SubsData = get_subscriptions(self.result,ADDRESS)
        self.subs.values = self.SubsData
        self.subs.display()
         
    def reloadnodes(self, *args, **keywords):
        npyscreen.notify("Reloading Nodes... Please wait...", title="Sentinel dVPN nodes")
        self.NodeData,self.result = get_nodes()
        self.dVPNs.values = self.NodeData
        self.dVPNs.display()
    
    def get_ip_address(self):
        self.old_ip = self.ip
        req = requests.get(ICANHAZURL)
        self.ip = req.text
    
        IPDATA = ["NEW IP: " + self.ip, "OLD IP: " + self.old_ip]
        self.ipBox.values = IPDATA
        self.ipBox.display()

    def getTimeDate(self):
        epoch_time = time()
        now = datetime.fromtimestamp(int(epoch_time))
        now_date = now.strftime("%a, %b %d %Y")
        now_time = now.strftime("%I:%M:%S %p")
        
        return now_date + '\n' +  now_time
    
    def connect_subscription(self, *args, **keywords):
        global CONFIG
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        message='''
Connection Info:
Node: %s
Node Address: %s
Keyname: %s
''' % (self.node.value, self.address.value, KEYNAME)
        ret = npyscreen.notify_ok_cancel(message, title="Meile Connection (Sentinel Network)")
        if ret:
            npyscreen.notify_wait("Connecting... Please wait...", title="Sentinel Network")
            try: 
                if self.id.value is not None and self.address.value is not None:
                    returncode, self.CONNECTED = connect(self.id.value, self.address.value, KEYNAME)
                if returncode == 0 and self.CONNECTED:
                    npyscreen.notify_confirm("Connection Successful!", title="Sentinel dVPN")
                    self.get_ip_address()
                else:
                    npyscreen.notify_confirm("ERROR: Something went wrong", title="Sentinel dVPN")
                
            except:
                npyscreen.notify_confirm("ERROR: Something went wrong", title="Sentinel dVPN")
        else:
            npyscreen.notify_wait("Ok. We won't connect to the selected node.", title="Sentinel Network")
            
                
                
    def part_subscription(self, *args, **keywords):
        npyscreen.notify_wait("Disconnecting.... Please wait...", title="Sentinel Network")
        try:
            returncode, self.CONNECTED = disconnect()
            if returncode == 0 and not self.CONNECTED:
                npyscreen.notify_confirm("Disconnected Successfully!", title='Sentinel dVPN')
                self.get_ip_address()
            else:
                npyscreen.notify_confirm("ERROR: Something went wrong", title='Sentinel dVPN')
        except:
            npyscreen.notify_confirm("ERROR: Something went wrong", title='Sentinel dVPN')
            
    def subscribe(self, *args, **keywords):
        global CONFIG
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        ADDRESS = CONFIG['wallet'].get('address', '')

        
        try:
            message='''
Subscription Info:
Node: %s
Node Address: %s
Deposit: %s
Keyname: %s
''' % (self.node.value, self.address.value, self.deposit.value, KEYNAME)
            ret = npyscreen.notify_ok_cancel(message, title="Meile Subscription (Sentinel Network)")
            if ret:
                if self.address.value and self.deposit.value != "N/A" and self.deposit.value:
                    returncode = SentinelSubscribe(KEYNAME, self.address.value, self.deposit.value)
                    if returncode == 0:
                        npyscreen.notify_confirm("Successfully Subscribe. Please reload your subscriptions. Remember it may take 1-5 minutes to show up.",
                                                 title="Meile Subscription")
                        self.coinBox.values = self.get_wallet_balances(KEYNAME, ADDRESS)
                        self.coinBox.display()
                    else:
                        npyscreen.notify_confirm("ERROR: Something went wrong with sentinelcli", title="ERROR")
                else:
                    npyscreen.notify_confirm("ERROR: Something went wrong with if statement", title="ERROR")
            else:
                return
        except:
            npyscreen.notify_confirm("ERROR: Something went wrong.RETCODE=%s" % returncode, title="ERROR")
                
    def get_wallet_balances(self, WALLET, ADDRESS):
        
        CoinData = []
        CoinData.append("Wallet: " + WALLET)
        CoinData.append("Address: " + ADDRESS[0:10] + "..." + ADDRESS[::-1][0:6][::-1])
        CoinData.append(" ")
        
        
        for key,val in get_balance(ADDRESS).items():
            CoinData.append("{0:<4}{1:>15}".format(key,val))
        
        return CoinData            
            
    def display_boxy(self, *args, **keywords):
        try: 
            selected_node_data = self.SubsData[self.subs.value[0]].split('|')[1:4]
            self.node.value    = selected_node_data[1].lstrip().rstrip()
            self.id.value      = selected_node_data[0].lstrip().rstrip()
            self.address.value = selected_node_data[2].lstrip().rstrip()
            self.deposit.value = "N/A"
            self.price.value   = ""
            
            self.node.display()
            self.id.display()
            self.address.display()
            self.deposit.display()
            self.price.display()
        except:
            pass
        
    def display_boxy2(self, *args, **keywords):
        try:
            selected_node_data = self.NodeData[self.dVPNs.value[0]].split('|')[1:4]
            self.node.value    = selected_node_data[0].lstrip().rstrip()
            self.address.value = selected_node_data[1].lstrip().rstrip()
            
            # This needs to change along with CheckBox 
            self.price.value   = selected_node_data[2].lstrip().rstrip()
            self.id.value      = "N/A"
            #self.deposit.value =  "Enter Amt..."
            self.node.display()
            self.id.display()
            self.address.display()
            self.deposit.display()
            self.price.display()
        except:
            pass
        
    def expand_node_info(self, *args, **keywords): 
 
        selected_node_data = self.NodeData[self.dVPNs.value[0]].split('|')[1:4]
        NADDRESS = selected_node_data[1].lstrip().rstrip()

        NodeTable = self.get_node_infos(NADDRESS)
        npyscreen.notify_confirm(NodeTable, title="Node Info", form_color = "STANDOUT" , wide=True)
 

                    


    def get_node_infos(self, naddress):
        APIURL   = "https://api.sentinel.mathnodes.com"

        endpoint = "/nodes/" + naddress
        
        NodeInfoDict = {}
        NodeTable = PrettyTable()    
    
        r = requests.get(APIURL + endpoint)
        
        remote_url = r.json()['result']['node']['remote_url']
        print(remote_url)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    
        r = requests.get(remote_url + "/status", verify=False)
        
        NodeInfoJSON = r.json()
        
        NodeInfoDict['Moniker']         = NodeInfoJSON['result']['moniker']
        NodeInfoDict['city']            = NodeInfoJSON['result']['location']['city']
        NodeInfoDict['country']         = NodeInfoJSON['result']['location']['country']
        NodeInfoDict['bandwidth']       = str(int(int(NodeInfoJSON['result']['bandwidth']['download']) / (1024*1024))) + "MB/s down, " + str(int(int(NodeInfoJSON['result']['bandwidth']['upload']) / (1024*1024))) + "MB/s up"
        NodeInfoDict['connected_peers'] = NodeInfoJSON['result']['peers']
        NodeInfoDict['max_peers']       = NodeInfoJSON['result']['qos']['max_peers']
        NodeInfoDict['price']           = NodeInfoJSON['result']['price']
        NodeInfoDict['version']         = NodeInfoJSON['result']['version']
        
        NodeTable.field_names = ['Moniker', 'City', 'Country', 'Bandwith', 'Connected Peers', 'Maximum Peers', 'Price', 'Version' ]
        NodeTable.add_row([NodeInfoDict['Moniker'],
                           NodeInfoDict['city'],
                           NodeInfoDict['country'],
                           NodeInfoDict['bandwidth'],
                           NodeInfoDict['connected_peers'],
                           NodeInfoDict['max_peers'],
                           NodeInfoDict['price'],
                           NodeInfoDict['version']
                           ])
        
        return '___\nExpanded Node Data\n_____________________\n' + NodeTable.get_string()
        
            
        
def main():
    global CONFIG
    CONFIG = read_configuration(CONFFILE)
    FILE = open(CONFFILE,'w')

    if not CONFIG['wallet'].get('keyname'):
        CONFIG.set('wallet', 'keyname', input("Please enter the keyname of the wallet you would like to use: "))
    if not CONFIG['wallet'].get('address'):
        CONFIG.set('wallet', 'address',input("Please enter the wallet address: ") )
    
    CONFIG.write(FILE)

    FILE.close()
    
    App = MeileApplication()
    App.run() 
    
if __name__ == '__main__':
    main()
