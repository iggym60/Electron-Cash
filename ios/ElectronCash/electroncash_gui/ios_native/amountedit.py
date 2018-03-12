from electroncash.i18n import _
from .custom_objc import *
from .uikit_bindings import *
from . import utils
from . import gui

from decimal import Decimal
from electroncash.util import format_satoshis_plain

def parent():
    return gui.ElectrumGui.gui

def config():
    return parent().config

def base_unit():
    return parent().base_unit()

def decimal_point():
    return parent().get_decimal_point()

# can use utils.register_callback() for this object.
# callbacks:
#   'textChanged' == func(amountEdit : BTCAmountEdit) -> None
#   'shortcut'    == func() -> None
#   'frozen'      == func() -> None
#   'edited'      == func(amountEdit : BTCAmountEdit) -> None

class BTCAmountEdit(UITextField):
    #frozen = pyqtSignal()
    #shortcut = pyqtSignal()
    isInt = objc_property()
    isShortcut = objc_property()
    modified = objc_property()

    @objc_method
    def init(self) -> ObjCInstance:
        self = ObjCInstance(send_super(__class__, self, 'init'))
        if self is not None:
            self.commonInit()
        return self

    @objc_method
    def initWithCoder_(self, coder : ObjCInstance) -> ObjCInstance:
        self = ObjCInstance(send_super(__class__, self, 'initWithCoder:', coder.ptr, argtypes=[c_void_p]))
        if self is not None:
            self.commonInit()
        return self

    @objc_method
    def dealloc(self) -> None:
        # cleanup code here...
        self.isInt = None
        self.isShortcut = None
        self.modified = None
        utils.remove_all_callbacks(self)
        send_super(__class__, self, 'dealloc')

    @objc_method
    def commonInit(self):
        # This seems sufficient for hundred-BTC amounts with 8 decimals
        #self.setFixedWidth(140)
        #self.base_unit = base_unit
        #self.textChanged.connect(self.numbify)
        self.addTarget_action_forControlEvents_(self, SEL(b'numbify'), UIControlEventEditingDidEnd)
        self.addTarget_action_forControlEvents_(self, SEL(b'edited'), UIControlEventEditingChanged)        
        self.isInt = False
        self.isShortcut = False
        self.modified = False
        #self.help_palette = QPalette()

    @objc_method
    def setFrozen_(self, b : bool) -> None:
        #self.setReadOnly(b)
        self.userInteractionEnabled = not b
        #self.setFrame(not b)
        self.alpha = 1.0 if b else 0.75
        utils.get_callback(self, 'frozen')()
        #self.frozen.emit()
        
    @objc_method
    def isFrozen(self) -> bool:
        return not self.userInteractionEnabled

    @objc_method
    def numbify(self):
        text = str(self.text).strip()
        #if text == '!':
        #    #self.shortcut.emit()
        #    utils.get_callback(self, 'shortcut')()
        #    return
        #pos = self.cursorPosition()
        chars = '0123456789'
        if not self.isInt: chars +='.'
        s = ''.join([i for i in text if i in chars])
        if not self.isInt:
            if '.' in s:
                p = s.find('.')
                s = s.replace('.','')
                s = s[:p] + '.' + s[p:p+decimal_point()]
        self.text = s
        utils.get_callback(self, 'textChanged')(self)
        # setText sets Modified to False.  Instead we want to remember
        # if updates were because of user modification.
        #self.setModified(self.hasFocus())
        #self.setCursorPosition(pos)

        
    @objc_method
    def isModified(self) -> bool:
        return self.modified

    @objc_method
    def edited(self) -> None:
        self.modified = True
        utils.get_callback(self, 'edited')(self)

    '''
    def paintEvent(self, event):
        QLineEdit.paintEvent(self, event)
        if self.base_unit:
            panel = QStyleOptionFrame()
            self.initStyleOption(panel)
            textRect = self.style().subElementRect(QStyle.SE_LineEditContents, panel, self)
            textRect.adjust(2, 0, -10, 0)
            painter = QPainter(self)
            painter.setPen(self.help_palette.brush(QPalette.Disabled, QPalette.Text).color())
            painter.drawText(textRect, Qt.AlignRight | Qt.AlignVCenter, self.base_unit())
    '''
    @objc_method
    def getAmount(self) -> ObjCInstance:
        try:
            x = Decimal(str(self.text))
        except:
            return None
        p = pow(10, decimal_point())
        return ns_from_py( int( p * x ) ) if x > 0 else None

    @objc_method
    def setAmount_(self, amount : ObjCInstance) -> None:
        self.modified = False
        if amount is None:
            self.text = ""  # Text(" ") # Space forces repaint in case units changed
        else:
            self.text = format_satoshis_plain(py_from_ns(amount), decimal_point())
        self.numbify()

'''
class BTCAmountEdit(AmountEdit):

    def __init__(self, decimal_point, is_int = False, parent=None):
        AmountEdit.__init__(self, self._base_unit, is_int, parent)
        self.decimal_point = decimal_point

    def _base_unit(self):
        p = self.decimal_point()
        assert p in [2, 5, 8]
        if p == 8:
            return 'BCH'
        if p == 5:
            return 'mBCH'
        if p == 2:
            return 'bits'
        raise Exception('Unknown base unit')


class BTCkBEdit(BTCAmountEdit):
    def _base_unit(self):
        return BTCAmountEdit._base_unit(self) + '/kB'
'''