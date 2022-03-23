#!/bin/env python3

#import argparse
import configparser
import pkg_resources
import shutil
import npyscreen
import requests
import re

from os import path
from time import time
from cli.sentinel import get_nodes, get_subscriptions,connect, disconnect
from cli.sentinel import subscribe as SentinelSubscribe
from datetime import datetime

from curses import KEY_F2, KEY_F3, KEY_F5, KEY_F6, COLOR_CYAN


BASEDIR = path.join(path.expanduser('~'), '.meile')
CONFFILE = path.join(BASEDIR, 'config.ini')
CONFIG = configparser.ConfigParser()
MEILEVERSION = "MEILE v0.1.0"
#KEYNAME="Bernoulli Numbers (dVPN)"
ICANHAZURL = "https://icanhazip.com"
KEY_C = 67
KEY_D = 68
KEY_H = 72
KEY_S = 83

def read_configuration(confpath):
    """Read the configuration file at given path."""
    # copy our default config file
    if not path.isfile(confpath):
        defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
        shutil.copyfile(defaultconf, CONFFILE)

    CONFIG.read(confpath)
    return CONFIG


    
class BoxTitle(npyscreen.BoxTitle):
    _contained_widget = npyscreen.SelectOne


class MeileApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        global CONFIG
        #CONFIG = read_configuration(CONFFILE)
        
        #self.coin_pair = CONFIG['pair'].get('order_book','').split(',')
        #self.hcoin_pair = CONFIG['pair'].get('trade_history', '').split(',')
        #self.tcoin_pair = CONFIG['pair'].get('ticker', '').split(',')
        self.addForm('MAIN', MainApp, name=MEILEVERSION, color="STANDOUT")
        '''
        self.addForm("PAIR", EditPair, name="Trading Pair Books", color="IMPORTANT")
        self.addForm("HISTORY", EditHistoryPair, name="Trading Pair History", color="IMPORTANT")
        self.addForm("TICKER", EditTickerPair, name="Ticker Pair", color="IMPORTANT")
        self.addForm("BUY",  BuyPair, name="Buy Pair", color="IMPORTANT")
        self.addForm("SELL", SellPair, name="Sell Pair", color="IMPORTANT")
        self.addForm("CANCEL", CancelOrder, name="Cancel Order", color="IMPORTANT")
        self.addForm("DEPOSIT", GetCoinDepositAddress, name="Add Deposit Address", color="IMPORTANT")
        self.addForm("WITHDRAW", WithdrawCoin, name="Withdraw", color="IMPORTANT")
        self.addForm("DHISTORY", GetDepositHistory, name="Deposit History", color="IMPORTANT")
        self.addForm("WHISTORY", GetWithdrawHistory, name="Withdraw History", color="IMPORTANT")
        self.addForm("THISTORY", GetTradeHistory, name="Trades History", color="IMPORTANT")
        '''
        #self.change_form("MAIN")
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
    ip = ""
    old_ip = ""
    CONNECTED = False
    price = deposit = dataGB = None
        
    def create(self):
        global CONFIG
        
        ADDRESS = CONFIG['wallet'].get('address', '')
        WALLET  = CONFIG['wallet'].get('keyname', '')
        
        self.keypress_timeout = 30

        
        self.y,self.x = self.curses_pad.getmaxyx()

        self.timeWidget = self.add(npyscreen.Textfield, name=" ",
                                    value=self.getTimeDate(),
                                    editable = None, 
                                    relx = int((self.x - len(self.getTimeDate().split('\n')[-1])-7) / 2))
        
        #self.getBalances()
            
        #self.add_handlers({"^O": self.cancel_order})
        
        req = requests.get(ICANHAZURL)
        self.ip = req.text
        self.old_ip = self.ip
        
        IPDATA = ["NEW IP: " + self.ip, "OLD IP: " + self.old_ip]  

        with open('logo.uni', 'r') as logo:
            data = logo.readlines()
            
        columns = shutil.get_terminal_size().columns
        rows = int(int(shutil.get_terminal_size().lines) / 2)
        newline = "\n"
        print(rows*newline,"Loading....".center(columns), end=' ')
        linlen=len(data[2])
        self.logo = self.add(npyscreen.BoxTitle, values=data, rely=4, relx= int((self.x - linlen) / 2),
               max_width=linlen+7,max_height=len(data)+2)
        self.logo.editable = False 
        
        
        self.ipBox = self.add(npyscreen.BoxTitle, values = IPDATA, rely=5, relx = 3, max_height=4, max_width = 30, editable = None )
        
        
        
        self.add(npyscreen.FixedText,rely=4, relx= self.x - 40, value="Press, H, for help", editable = None)
        self.add(npyscreen.FixedText,rely=9, relx= self.x - 48, value="Wallet: %s" % WALLET, editable = None)
        self.add(npyscreen.FixedText,rely=10, relx= self.x - 48, value="Address: %s" % ADDRESS, editable = None)
        
                 
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

        '''
        self.dVPNs = self.add(npyscreen.BoxTitle, name="Sentinel Nodes", values=NodeData,
                                    max_height=self.y - 30, width = self.x - 6, rely = 11,
                                    scroll_exit = True, editable = True,
                                    contained_widget_arguments={
                                        'color': "CAUTION", 
                                        'widgets_inherit_color': False,}
                                    )
        '''
        self.subs = self.add(BoxTitle, name="Active Subscriptions", values=self.SubsData,
                                    max_height=10, width = self.x - 10, rely = self.y - 18,
                                    scroll_exit = True, editable = True,
                                    contained_widget_arguments={
                                        'color': "CAUTION", 
                                        'widgets_inherit_color': False,}
                                    )
        self.add(npyscreen.FixedText, rely = self.y -7, value="Selected Node")
        self.node = self.add(npyscreen.TitleText, name = "Node: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 6, editable = None)
        self.id = self.add(npyscreen.TitleText, name = "ID: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 5, editable = None)
        self.address = self.add(npyscreen.TitleText, name = "Address: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 4, editable = None)
        self.deposit = self.add(npyscreen.TitleText, name = "Deposit: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 6, relx = 72, editable = None )
        self.price = self.add(npyscreen.TitleText, name = "Price: ", value=None, use_two_lines = False, begin_entry_at = 10, rely = self.y - 5, relx = 72, editable = None )
        self.dataGB = self.add(npyscreen.TitleSlider, max_width = 80, label=True, name="GB", value=19, out_of = 1000, step = 2, block_color = COLOR_CYAN, rely = self.y - 4, relx = 72)
        self.add(npyscreen.FixedText, rely = self.y - 3, value="Use the menu to Connect/Subscribe (CTRL+X)", editable = None)
        self.add_handlers({KEY_F2: self.display_boxy})
        self.add_handlers({KEY_F3: self.display_boxy2})
        self.add_handlers({KEY_F5: self.reloadsubs})
        self.add_handlers({KEY_F6: self.reloadnodes})
        self.add_handlers({KEY_H: self.helpme})
        self.add_handlers({KEY_C: self.connect_subscription})
        self.add_handlers({KEY_D: self.part_subscription})
        self.add_handlers({KEY_S: self.subscribe})
        

    def while_waiting(self):
        if self.price.value:
            mu_amt = re.findall(r'[0-9]+', self.price.value)[0]
            mu_coin = re.findall(r'\D+', self.price.value)[0]
            self.deposit.value = str(int(int(self.dataGB.value) * int(mu_amt))) + mu_coin 
            self.deposit.display()
    
    def helpme(self, *args, **keywords):
        
        message='''
                HELP SCREEN (Meile v0.1.0) (MathNodes)
                
                Commands:
                F2           - Load Subscription Data to Connect to Node
                F3           - Load Node Info to Subscribe to Node
                F5           - Refresh Subscription data (Useful after subscribing)
                F6           - Refresh Node Data
                PGDN         - Scroll the data downwards
                PGUP         - Scroll the data upwards
                Enter/Space  - Select a node
                CTRL+X       - Display the Menu
                l            - Search with data box (Nodes, Subscriptions)
                n            - go to next entry of search results
                H            - This help screen
                S            - Subscribe to loaded node data (from F3)
                D            - Disconnect from connectd node
                C            - Connect to loaded subscription (From F2)
                '''
        npyscreen.notify_confirm(message, title="Meile HELP v0.1.0 (MathNodes)", form_color = "STANDOUT" , wide=True)
                
        
    def reloadsubs(self, *args, **keywords):
        global CONFIG
        ADDRESS = CONFIG['wallet'].get('address','')
        self.SubsData = get_subscriptions(self.result,ADDRESS)
        self.subs.values = self.SubsData
        self.subs.display()
         
    def reloadnodes(self, *args, **keywords):
        self.NodeData = get_nodes()
        self.dVPNs.values = self.NodeData
        self.dVPNs.display()
    
    def get_ip_address(self):
        if not self.CONNECTED:
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
        try: 
            if self.id.value is not None and self.address.value is not None:
                returncode = connect(self.id.value, self.address.value, KEYNAME)
            if returncode == 0:
                npyscreen.notify_confirm("Connection Successful!", title="Sentinel dVPN")
                self.CONNECTED = True
                self.get_ip_address()
            else:
                npyscreen.notify_confirm("ERROR: Something went wrong", title="Sentinel dVPN")
            
        except:
            npyscreen.notify_confirm("ERROR: Something went wrong", title="Sentinel dVPN")
            
            
                
                
    def part_subscription(self, *args, **keywords):
        try:
            returncode = disconnect()
            if returncode == 0:
                npyscreen.notify_confirm("Disconnected Successfully!", title='Sentinel dVPN')
                self.CONNECTED = False
                self.get_ip_address()
            else:
                npyscreen.notify_confirm("ERROR: Something went wrong", title='Sentinel dVPN')
        except:
            npyscreen.notify_confirm("ERROR: Something went wrong", title='Sentinel dVPN')
            
    def subscribe(self, *args, **keywords):
        global CONFIG
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
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
                    else:
                        npyscreen.notify_confirm("ERROR: Something went wrong with sentinelcli", title="ERROR")
                else:
                    npyscreen.notify_confirm("ERROR: Something went wrong with if statement", title="ERROR")
            else:
                return
        except:
            npyscreen.notify_confirm("ERROR: Something went wrong.RETCODE=%s" % returncode, title="ERROR")
                
                
            
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

             
        
def main():
    global CONFIG
    CONFIG = read_configuration(CONFFILE)
    
    if not CONFIG['wallet'].get('keyname'):
        CONFIG.set('wallet', 'keyname', input("Please enter the keyname of the wallet you would like to use: "))
    if not CONFIG['wallet'].get('address'):
        CONFIG.set('wallet', 'address',input("Please enter the wallet address: ") )

    FILE = open(CONFFILE,'w')
    CONFIG.write(FILE)
    
    App = MeileApplication()
    App.run() 
    
if __name__ == '__main__':
    main()
