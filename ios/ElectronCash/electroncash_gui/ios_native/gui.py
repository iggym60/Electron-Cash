#!/usr/bin/env python3
#
# Electron Cash - lightweight Bitcoin Cash client
# Copyright (C) 2012 thomasv@gitorious
# Copyright (C) 2018 calin.culianu@gmail.com
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import signal
import sys
import traceback
import bz2
import base64
import time
from datetime import datetime
from . import heartbeat
from . import utils
from . import history
from . import addresses
from . import send
from . import receive

try:
    from .uikit_bindings import *
except Exception as e:
    sys.exit("Error: Could not import iOS libs: %s"%str(e))

from electroncash.i18n import _, set_language, languages
#from electroncash.plugins import run_hook
from electroncash import WalletStorage, Wallet
from electroncash.address import Address
# from electroncash.synchronizer import Synchronizer
# from electroncash.verifier import SPV
# from electroncash.util import DebugMem
from electroncash.util import UserCancelled, print_error, format_satoshis, PrintError, timestamp_to_datetime

# from electroncash.wallet import Abstract_Wallet

# a dummy hard coded wallet with a few tx's in its history for testing
# encrypted with password 'bchbch'
hardcoded_testing_wallet = bz2.decompress(base64.b64decode(b'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'))

TAG_PASSWD = 2
TAG_CASHADDR = 3
TAG_PREFS = 4
TAG_SEED = 5
TAG_NETWORK = 6

def check_imports():
    # pure-python dependencies need to be imported here for pyinstaller
    try:
        import dns
        import pyaes
        import ecdsa
        import requests
        import qrcode
        import pbkdf2
        import google.protobuf
        import jsonrpclib
        # the following imports are for pyinstaller
        from google.protobuf import descriptor
        from google.protobuf import message
        from google.protobuf import reflection
        from google.protobuf import descriptor_pb2
        from jsonrpclib import SimpleJSONRPCServer
        import electroncash
        import electroncash.bitcoin
    # make sure that certificates are here
    except ImportError as e:
        return "Error: %s"%str(e)

    try:
        thekey = "5Hwpw2vSB66RMzf74b8isUYZFfQ23yrrmotVrxmJVcnjBDwWZ76"
        return thekey + " decodes to: " + electroncash.bitcoin.address_from_private_key(str.encode(thekey,'utf8'))
    except Exception as e:
        print("Error: %s"%str(e))
        return str(e)

class GuiHelper(NSObject):
    updateNeeded = objc_property()
    butsStatus = objc_property()
    butsStatusLabel = objc_property()
    butsPasswd = objc_property() # array of buttons, one per tab
    butsCashaddr = objc_property()
    butsSeed = objc_property()
    butsPrefs = objc_property()
    butsSend = objc_property()
    
    @objc_method
    def init(self):
        self = ObjCInstance(send_super(self, 'init'))
        self.updateNeeded = False
        self.butsStatus = []
        self.butsStatusLabel = []
        self.butsPasswd = []
        self.butsCashaddr = []
        self.butsSeed = []
        self.butsPrefs = []
        self.butsSend = []
        heartbeat.Add(self, 'doUpdateIfNeeded')
        return self
    
    @objc_method
    def dealloc(self) -> None:
        heartbeat.Remove(self, 'doUpdateIfNeeded')
        self.updateNeeded = None
        self.butsStatus = None
        self.butsStatusLabel = None
        self.butsPasswd = None
        self.butsCashaddr = None
        self.butsSeed = None
        self.butsPrefs = None
        self.butsSend = None
        send_super(self, 'dealloc')
    
    @objc_method
    def onTimer_(self, ignored):
        pass
    
    @objc_method
    def doUpdateIfNeeded(self):
        if self.updateNeeded and ElectrumGui.gui is not None:
            ElectrumGui.gui.on_status_update()
            self.updateNeeded = False

    @objc_method
    def needUpdate(self):
        self.updateNeeded = True
        
    @objc_method
    def onToolButton_(self,but) -> None:
        print("onToolButton: called with button tag {}".format(str(but.tag)))
        if ElectrumGui.gui is not None:
            ElectrumGui.gui.on_tool_button(but)
        
    @objc_method
    def navigationController_willShowViewController_animated_(self, nav, vc, anim : bool) -> None:
        is_hidden = True if len(nav.viewControllers) and vc.ptr.value != nav.viewControllers[0].ptr.value else False
        #print("SetToolBarHidden=%s"%str(is_hidden))
        nav.setToolbarHidden_animated_(is_hidden, True)
    

# Manages the GUI. Part of the ElectronCash API so you can't rename this class easily.
class ElectrumGui(PrintError):

    gui = None

    def __init__(self, config, daemon, plugins):
        ElectrumGui.gui = self
        self.appName = 'Electron-Cash'
        self.appDomain = 'com.c3-soft.ElectronCash'
        self.set_language()

        #todo: support multiple wallets in 1 UI?
        self.config = config
        self.daemon = daemon
        self.plugins = plugins
        self.wallet = None
        self.window = None
        self.tabController = None
        self.historyNav = None
        self.historyVC = None
        self.sendVC = None
        self.sendNav = None
        self.receiveVC = None
        self.receiveNav = None
        self.addressesNav = None
        self.addressesVC = None
        
        self.decimal_point = config.get('decimal_point', 5)
        self.fee_unit = config.get('fee_unit', 0)
        self.num_zeros     = int(config.get('num_zeros',3))
        
        Address.show_cashaddr(config.get('show_cashaddr', True))

        self.history = []
        self.helper = None
        self.helperTimer = None

    def createAndShowUI(self):
        self.helper = GuiHelper.alloc().init()

        self.window = UIWindow.alloc().initWithFrame_(UIScreen.mainScreen.bounds)
        self.tabController = UITabBarController.alloc().init().autorelease()

        self.window.backgroundColor = UIColor.whiteColor
        self.historyVC = tbl = history.HistoryTableVC.alloc().initWithStyle_(UITableViewStylePlain).autorelease()

        self.sendVC = snd = send.SendVC.alloc().init().autorelease()
        
        self.receiveVC = rcv = receive.ReceiveVC.alloc().init().autorelease()
        
        self.addressesVC = adr = addresses.AddressesTableVC.alloc().initWithStyle_(UITableViewStylePlain).autorelease()
        
        self.historyNav = nav = UINavigationController.alloc().initWithRootViewController_(tbl).autorelease()

        self.sendNav = nav2 = UINavigationController.alloc().initWithRootViewController_(snd).autorelease()
        self.receiveNav = nav3 = UINavigationController.alloc().initWithRootViewController_(rcv).autorelease()
        self.addressesNav = nav4 = UINavigationController.alloc().initWithRootViewController_(adr).autorelease()

        self.tabController.viewControllers = [nav, nav2, nav3, nav4]
        tabitems = self.tabController.tabBar.items
        tabitems[0].image = UIImage.imageNamed_("tab_history.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)
        tabitems[1].image = UIImage.imageNamed_("tab_send.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)
        tabitems[2].image = UIImage.imageNamed_("tab_receive.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)
        tabitems[3].image = UIImage.imageNamed_("tab_addresses.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)

        self.window.rootViewController = self.tabController

        self.setup_toolbar()
        
        self.window.makeKeyAndVisible()
                 
        # network callbacks
        if self.daemon.network:
            self.daemon.network.register_callback(self.on_history, ['on_history'])
            self.daemon.network.register_callback(self.on_quotes, ['on_quotes'])
            interests = ['updated', 'new_transaction', 'status',
                         'banner', 'verified', 'fee']
            # To avoid leaking references to "self" that prevent the
            # window from being GC-ed when closed, callbacks should be
            # methods of this class only, and specifically not be
            # partials, lambdas or methods of subobjects.  Hence...
            self.daemon.network.register_callback(self.on_network, interests)
            print ("REGISTERED NETWORK CALLBACKS")

        tbl.refresh()
        
        self.helper.needUpdate()
                
        print("UI Created Ok")
        
        return True
    
    def setup_toolbar(self):
        butsStatusLabel = []
        butsStatus = []
        butsPasswd = []
        butsSeed = []
        butsCashaddr = []
        butsPrefs = []
        for nav in self.tabController.viewControllers:
            itemsThisNav = []
            # status label
            l = UILabel.alloc().initWithFrame_(CGRectMake(0,0,UIScreen.mainScreen.bounds.size.width-100,50)).autorelease()
            l.text = "Electron Cash..."
            l.adjustsFontSizeToFitWidth = True
            l.numberOfLines=0
            l.sizeToFit()
            b = UIBarButtonItem.alloc().initWithCustomView_(l).autorelease()
            b.tag = 0

            butsStatusLabel.append(b)
            itemsThisNav.append(b)
            
            # spacer
            b = UIBarButtonItem.alloc().initWithBarButtonSystemItem_target_action_(UIBarButtonSystemItemFlexibleSpace, None, None)
            b.tag = 1
            itemsThisNav.append(b)

            # Locked/Unlocked icon
            b = UIBarButtonItem.alloc().initWithImage_style_target_action_(UIImage.imageNamed_("unlock.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal),
                                                                           UIBarButtonItemStylePlain,
                                                                           self.helper,
                                                                           SEL(b'onToolButton:'))
            b.tag = TAG_PASSWD
            butsPasswd.append(b)
            itemsThisNav.append(b)

            # Cashaddr icon
            b = UIBarButtonItem.alloc().initWithImage_style_target_action_(self.cashaddr_icon(),
                                                                           UIBarButtonItemStylePlain,
                                                                           self.helper,
                                                                           SEL(b'onToolButton:'))
            b.tag = TAG_CASHADDR
            butsCashaddr.append(b)
            itemsThisNav.append(b)


            # Seed icon
            b = UIBarButtonItem.alloc().initWithImage_style_target_action_(UIImage.imageNamed_("seed.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal),
                                                                           UIBarButtonItemStylePlain,
                                                                           self.helper,
                                                                           SEL(b'onToolButton:'))
            b.tag = TAG_SEED
            butsSeed.append(b)
            itemsThisNav.append(b)

            # Prefs icon
            b = UIBarButtonItem.alloc().initWithImage_style_target_action_(UIImage.imageNamed_("preferences.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal),
                                                                           UIBarButtonItemStylePlain,
                                                                           self.helper,
                                                                           SEL(b'onToolButton:'))
            b.tag = TAG_PREFS
            butsPrefs.append(b)
            itemsThisNav.append(b)
            
            # status/network icon
            b = UIBarButtonItem.alloc().initWithImage_style_target_action_(UIImage.imageNamed_("status_disconnected.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal),
                                                                           UIBarButtonItemStylePlain,
                                                                           self.helper,
                                                                           SEL(b'onToolButton:'))
            b.tag = TAG_NETWORK
            butsStatus.append(b)
            itemsThisNav.append(b)
            
            root = nav.viewControllers[0] # get root viewcontroller
            itemsThisNav.sort(key=lambda x: x.tag)
            root.setToolbarItems_animated_(itemsThisNav, True)
            nav.setToolbarHidden_animated_(False, True)
            # below two cause problems because of our 'persistent toolbar', so disable
            #nav.hidesBarsWhenKeyboardAppears = True
            #nav.hidesBarsWhenVerticallyCompact = True
            nav.delegate = self.helper
        self.helper.butsStatusLabel = butsStatusLabel
        self.helper.butsStatus = butsStatus
        self.helper.butsPasswd = butsPasswd
        self.helper.butsSeed = butsSeed
        self.helper.butsCashaddr = butsCashaddr
        self.helper.butsPrefs = butsPrefs
    
    def destroyUI(self):
        if self.window is None:
            return
        self.daemon.network.unregister_callback(self.on_history)
        self.daemon.network.unregister_callback(self.on_network)
        if self.helperTimer is not None:
            self.helperTimer.invalidate()
        self.tabController.viewControllers = None
        self.historyNav = None
        self.historyVC = None
        self.sendNav = None
        self.sendVC = None
        self.receiveVC = None
        self.receiveNav = None
        self.addressesNav = None
        self.addressesVC = None
        self.window.rootViewController = None
        self.tabController = None
        self.window.release()
        self.window = None
        self.helperTimer = None
        self.helper.release()
        self.helper = None        
    
    def on_rotated(self): # called by PythonAppDelegate after screen rotation
        #update status bar label width
        size = UIScreen.mainScreen.bounds.size
        buts = self.helper.butsStatusLabel
        for b in buts:
            f = b.customView.frame
            if size.width < size.height:
                f.size.width = size.width/2 - 30
            else:
                f.size.width = size.width / 2
            b.customView.frame = f
            #b.customView.sizeToFit()


    
    def init_network(self):
        # Show network dialog if config does not exist
        if self.daemon.network:
            if self.config.get('auto_connect') is None:
                #wizard = InstallWizard(self.config, self.app, self.plugins, None)
                #wizard.init_network(self.daemon.network)
                #wizard.terminate()
                print("NEED TO SHOW WIZARD HERE")
                pass
            
    def on_history(self, b):
        print("ON HISTORY (IsMainThread: %s)"%(str(NSThread.currentThread.isMainThread)))
        assert self.historyVC is not None
        self.historyVC.needUpdate()
        self.helper.needUpdate()
        
    def on_quotes(self, event, *args):
        print("ON QUOTES (IsMainThread: %s)"%(str(NSThread.currentThread.isMainThread)))        
        self.historyVC.needUpdate()
        self.addressesVC.needUpdate()
        self.helper.needUpdate()
            
    def on_network(self, event, *args):
        print ("ON NETWORK: %s (IsMainThread: %s)"%(event,str(NSThread.currentThread.isMainThread)))
        assert self.historyVC is not None
        if event == 'updated':
            self.helper.needUpdate()
        elif event == 'new_transaction':
            self.historyVC.needUpdate() #enqueue update to main thread
            self.addressesVC.needUpdate() #enqueue update to main thread
            self.helper.needUpdate()
        elif event == 'banner':
            #todo: handle console stuff here
            pass
        elif event == 'status':
            #todo: handle status update here
            self.helper.needUpdate()
        elif event in ['verified']:
            self.historyVC.needUpdate() #enqueue update to main thread
            self.addressesVC.needUpdate()
            self.helper.needUpdate()
        elif event == 'fee':
            # todo: handle fee stuff here
            pass
        else:
            self.print_error("unexpected network message:", event, args)
            
    def on_status_update(self):
        print ("ON STATUS UPDATE (IsMainThread: %s)"%(str(NSThread.currentThread.isMainThread)))
        if not self.wallet:
            return

        if self.daemon.network is None or not self.daemon.network.is_running():
            text = _("Offline")
            icon = "status_disconnected.png"

        elif self.daemon.network.is_connected():
            server_height = self.daemon.network.get_server_height()
            server_lag = self.daemon.network.get_local_height() - server_height
            # Server height can be 0 after switching to a new server
            # until we get a headers subscription request response.
            # Display the synchronizing message in that case.
            if not self.wallet.up_to_date or server_height == 0:
                text = _("Synchronizing...")
                icon = "status_waiting.png"
            elif server_lag > 1:
                text = _("Server is lagging ({} blocks)").format(server_lag)
                icon = "status_lagging.png"
            else:
                c, u, x = self.wallet.get_balance()
                text =  _("Balance" ) + ": %s "%(self.format_amount_and_units(c))
                if u:
                    text +=  " [%s unconfirmed]"%(self.format_amount(u, True).strip())
                if x:
                    text +=  " [%s unmatured]"%(self.format_amount(x, True).strip())

                # append fiat balance and price
                if self.daemon.fx.is_enabled():
                    text += self.daemon.fx.get_fiat_status_text(c + u + x,
                        self.base_unit(), self.get_decimal_point()) or ''
                if not self.daemon.network.proxy:
                    icon = "status_connected.png"
                else:
                    icon = "status_connected_proxy.png"
        else:
            text = _("Not connected")
            icon = "status_disconnected.png"

        #self.tray.setToolTip("%s (%s)" % (text, self.wallet.basename()))
        #self.balance_label.setText(text)
        #self.status_button.setIcon( icon )
        lbls = self.helper.butsStatusLabel
        buts = self.helper.butsStatus
        for l in lbls:
            l.customView.text = text
        img = UIImage.imageNamed_(icon).imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)
        for b in buts:
            b.setImage_(img)
            
        self.update_lock_icon()
        self.update_buttons_on_seed()
        
    def update_lock_icon(self):
        img = UIImage.imageNamed_("lock.png" if self.wallet.has_password() else "unlock.png").imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal)
        buts = self.helper.butsPasswd
        for b in buts:
            b.setImage_(img)
        

    def update_buttons_on_seed(self):
        def removeBut(but,vcidx):
            nav = self.tabController.viewControllers[vcidx]
            root = nav.viewControllers[0]
            itemsThisNav = root.toolbarItems
            itemsThisNav = [x for x in itemsThisNav if x.tag != but.tag]
            root.setToolbarItems_animated_(itemsThisNav, True)
        def addBut(but,vcidx):
            nav = self.tabController.viewControllers[vcidx]
            root = nav.viewControllers[0]
            itemsThisNav = root.toolbarItems
            if but not in itemsThisNav:
                itemsThisNav.insert(but.tag,but)
                root.setToolbarItems_animated_(itemsThisNav, True)

        buts = self.helper.butsSeed
        for i,b in enumerate(buts):
            b.enabled = self.wallet.has_seed()
            if not b.isEnabled():
                removeBut(b,i)
            else:
                addBut(b,i)
        buts = self.helper.butsPasswd
        for i,b in enumerate(buts):
            b.enabled = self.wallet.can_change_password()
            if not b.isEnabled():
                removeBut(b,i)
            else:
                addBut(b,i)
        buts = self.helper.butsSend
        for i,b in enumerate(buts): # todo: implement send button tracking?
            b.enabled = not self.wallet.is_warching_only()
            if not b.isEnabled():
                removeBut(b,i)
            else:
                addBut(b,i)
        #self.seed_button.setVisible(self.wallet.has_seed())
        #self.password_button.setVisible(self.wallet.can_change_password())
        #self.send_button.setVisible(not self.wallet.is_watching_only())

    def on_tool_button(self, but : ObjCInstance) -> None:
        if but.tag == TAG_NETWORK: # status button
            print("Network status button pushed.. TODO, implement...")
        elif but.tag == TAG_PASSWD:
            print("Password lock button pushed.. TODO, implement...")
        elif but.tag == TAG_SEED:
            print("Seed button pushed.. TODO, implement...")
        elif but.tag == TAG_PREFS:
            print("Prefs button pushed.. TODO, implement...")
        elif but.tag == TAG_CASHADDR:
            print("CashAddr button pushed.. TODO, implement...")
            self.toggle_cashaddr_status_bar()
        else:
            print("Unknown button pushed, tag=%d"%int(but.tag))
  
    def cashaddr_icon(self):
        imgname = "addr_converter_bw.png"
        if self.config.get('show_cashaddr', True):
            imgname = "addr_converter.png"
        return UIImage.imageNamed_(imgname).imageWithRenderingMode_(UIImageRenderingModeAlwaysOriginal) 

    def update_cashaddr_icon(self):
        buts = self.helper.butsCashaddr
        img = self.cashaddr_icon()
        for b in buts:
            b.setImage_(img)

    def toggle_cashaddr_status_bar(self):
        self.toggle_cashaddr(not self.config.get('show_cashaddr', True))

    def toggle_cashaddr(self, on):
        self.config.set_key('show_cashaddr', on)
        self.update_cashaddr_icon()
        Address.show_cashaddr(on)
        self.historyVC.needUpdate()
        self.addressesVC.needUpdate()
        #for window in self.gui_object.windows:
        #    window.cashaddr_toggled_signal.emit()
      
    @staticmethod
    def prompt_password(prmpt, dummy=0):
        print("prompt_password(%s,%s) thread=%s mainThread?=%s"%(prmpt,str(dummy),NSThread.currentThread.description,str(NSThread.currentThread.isMainThread)))
        return "bchbch"

    def generate_wallet(self, path):
        with open(path, "wb") as fdesc:
            fdesc.write(hardcoded_testing_wallet)
            fdesc.close()
            print("Generated hard-coded wallet -- wrote %d bytes"%len(hardcoded_testing_wallet))
        storage = WalletStorage(path, manual_upgrades=True)
        if not storage.file_exists():
            return
        if storage.is_encrypted():
            password = ElectrumGui.prompt_password("EnterPasswd",0)
            if not password:
                return
            storage.decrypt(password)
        if storage.requires_split():
            return
        if storage.requires_upgrade():
            return
        if storage.get_action():
            return
        wallet = Wallet(storage)
        return wallet

    def do_wallet_stuff(self, path, uri):
        try:
            wallet = self.daemon.load_wallet(path, ElectrumGui.prompt_password("PassPrompt1"))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return
        if not wallet:
            storage = WalletStorage(path, manual_upgrades=True)
            try:
                wallet = self.generate_wallet(path)
            except Exception as e:
                print_error('[do_wallet_stuff] Exception caught', e)
            if not wallet:
                print("NO WALLET!!!")
                return
            wallet.start_threads(self.daemon.network)
            self.daemon.add_wallet(wallet)
        print("WALLET=%s synchronizer=%s"%(str(wallet),str(wallet.synchronizer)))
        return wallet
    
    def format_amount(self, x, is_diff=False, whitespaces=False):
        return format_satoshis(x, is_diff, self.num_zeros, self.decimal_point, whitespaces)

    def format_amount_and_units(self, amount, usenl=False):
        text = self.format_amount(amount) + ' '+ self.base_unit()
        x = self.daemon.fx.format_amount_and_units(amount)
        if text and x:
            text += "\n" if usenl else ''
            text += ' (%s)'%x
        return text

    def format_fee_rate(self, fee_rate):
        if self.fee_unit == 0:
            return '{:.2f} sats/byte'.format(fee_rate/1000)
        else:
            return self.format_amount(fee_rate) + ' ' + self.base_unit() + '/kB'

    def base_unit(self):
        assert self.decimal_point in [2, 5, 8]
        if self.decimal_point == 2:
            return 'bits'
        if self.decimal_point == 5:
            return 'mBCH'
        if self.decimal_point == 8:
            return 'BCH'
        raise Exception('Unknown base unit')

    def get_decimal_point(self):
        return self.decimal_point
   
    def on_label_edited(self, key, newvalue):
        self.wallet.set_label(key, newvalue)
        self.wallet.storage.write()
        self.historyVC.needUpdate()
        self.addressesVC.needUpdate()


    def set_language(self):
        langs = NSLocale.preferredLanguages
        if langs:
            l = langs[0].replace('-','_')
            if not languages.get(l):
                # iOS sometimes returns a mixed language_REGION code, so try and match it to what we have 
                pre1 = l.split('_')[0]
                for k in languages.keys():
                    pre2 = k.split('_')[0]
                    if pre1 == pre2:
                        print("OS language is '%s', but we are guessing this matches our language code '%s'"%(l, k))
                        l = k
                        break
            print ("Setting language to {}".format(l))
            set_language(l)


    # this method is called by Electron Cash libs to start the GUI
    def main(self):       
        print("Test Decode result: %s"%check_imports())
        import hashlib
        print("HashLib algorithms available: " + str(hashlib.algorithms_available))
        import platform
        print ("Platform %s uname: %s"%(platform.platform(),platform.uname()))
        print ("Bundle Identifier %s"% utils.bundle_identifier)

        try:
            self.init_network()
        except:
            traceback.print_exc(file=sys.stdout)
            return
        self.config.open_last_wallet()
        path = self.config.get_wallet_path()


        # hard code some stuff for testing
        self.daemon.network.auto_connect = True
        self.config.set_key('auto_connect', self.daemon.network.auto_connect, True)
        print("WALLET PATH: %s"%path)
        print ("NETWORK: %s"%str(self.daemon.network))
        w = self.do_wallet_stuff(path, self.config.get('url'))
        assert w
        # TODO: put this stuff in the UI
        self.wallet = w
        self.createAndShowUI()
