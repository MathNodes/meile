# CHANGELOG

## Version 0.5.0 (06/06/2022)
* NEW: Support for dVPN node IBC multi-coin listings
* NEW: Single checkbox for subscribing with IBC coins on Sentinel
* NEW: Parsing of multi-coin IBC for accurate transaction in specific coin
* NEW: Selecting a node in the table and pressing 'I' will display additional information about the selected node. This uses an API call to get status of specific node
* CHANGE: reduced wait_time for updated deposit amount from 35 to 5, instant display
* FIX: Specified max_width in node subscription listings for UI clarity
* ADD: New function for parsing IBC tokens in node listings. 
* REMOVED: Version and Handshake details from main node listing. They can now be found under the Info ('I') dialog. See help in Meile for more info.
* CHANGED: Minimum screen display is now 221x67

## Version 0.4.6 (19/05/2022)
* FIX: Wallet Box max_height

## Version 0.4.5 (19/05/2022)
* NEW: Box Display of Wallet and Token Values
* NEW: API Call in sentinel module, get_balance
* FIX: Display partial start,end of wallet address

## Version 0.4.4 (01/05/2022)
* NEW: Column for node software version. Replaces "STATUS"

## Version 0.4.3 (17/04/2022)
### OFFICIAL RELEASE
* NEW: pip install
* IMPROVEMENT: method for ensuring connection to active node will result in success or failure. Should be fail-proof. 
* FIX: old/new IP address dialog
* FIX: config file processing error

## Version 0.4.0-0.4.2
* YANKED: Due to pip install issues

## Version 0.3.1-BETA (08/04/2022)
* FIX: BadgerBite Testserver listen errors


## Version 0.3.0-BETA (30/03/2022)
* FIX: Remove Multiple Subscriptions when fully consumed
* FIX: IBC Token listing bug
* ENHANCEMENT: Remove null nodes
* ENHANCEMENT: A-Z Sort of Nodes
* ADD: Support for new IBC token

## Version 0.2.1-BETA (27/03/2022)
* ADD: Added logo.uni
* FIX: config.ini
* REPO UPDATED

## Version 0.2.0-BETA (24/03/2022)
* FIX: F7 to reload node data as F6 is npyscreen command
* FIX: Return values of get_nodes() upon refresh
* FIX: Code reduction
* FIX: Connection issues after stopping/restarting
* ENHANCEMENT: Show Connection info and verify user wants to connect
* ENHANCEMENT: Wait screens for background processes
* FEATURE: F7 now reloads all node info from RPC
* FEATURE: Check terminal size and exit if not large enough


## Version 0.1.0-BETA (23/03/2022)
INITIAL RELEASE (BETA)
