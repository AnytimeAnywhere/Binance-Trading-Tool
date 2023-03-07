from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QDialogButtonBox, QLabel
import sys
import mainwindow
import json
import os
from trading_limit import *
from trading_limit_close import *
from trading_market_close import *

def update_config(symbol,leverage,order_quantity_pct,take_profit_price,stop_loss_price,limit_price):
    with open('config.json') as json_file:
        config = json.load(json_file)

    config["trading_params"]["symbol"] = symbol
    config["trading_params"]["leverage"] = leverage
    config["trading_params"]["order_quantity_pct"] = order_quantity_pct
    config["trading_params"]["take_profit_price"] = take_profit_price
    config["trading_params"]["stop_loss_price"] = stop_loss_price
    config["trading_params"]["limit_price"] = limit_price

    with open('config.json', 'w') as data_file:
        data = json.dump(config, data_file,indent=4)
class CustomDialog_Confirm(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Are you really sure to click this button?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
class CustomDialog_buy(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel("TP must be greater than SL in Buying")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
class CustomDialog_sell(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel("TP must be less than SL in Selling")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindowApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindowApp, self).__init__(parent)
        self.setupUi(self)
        
        self.Nx_spin.valueChanged.connect(self.Nx_spin_changed)
        self.Nx_slider.valueChanged.connect(self.Nx_slider_changed)
        self.percent_spin.valueChanged.connect(self.Percent_spin_changed)
        self.percent_slider.valueChanged.connect(self.Percent_slider_changed)
        self.buyBtn.clicked.connect(self.buy_stock)
        self.sellBtn.clicked.connect(self.sell_stock)
        self.closeLimitBtn.clicked.connect(self.close_limit)
        self.closeMarketBtn.clicked.connect(self.close_market)
        

    def Percent_spin_changed(self):
        self.percent_slider.setValue(self.percent_spin.value())

    def Percent_slider_changed(self):
        self.percent_spin.setValue(self.percent_slider.value())

    def Nx_spin_changed(self):
        self.Nx_slider.setValue(self.Nx_spin.value())

    def Nx_slider_changed(self):
        self.Nx_spin.setValue(self.Nx_slider.value())

    def buy_stock(self):
        print(self.sizeCurrency.currentText())
        symbol = self.sizeCurrency.currentText()
        leverage = str(self.Nx_spin.value())
        order_quantity_pct = str(self.percent_spin.value())
        take_profit_price = str(self.tpEdit.text())
        stop_loss_price = str(self.slEdit.text())
        limit_price = str(self.priceEdit.text())

        dialog = CustomDialog_Confirm()
        if dialog.exec_() == QDialog.Accepted:
            print("OK clicked")
        else:
            print("Cancel clicked")
            return
        
        if take_profit_price and stop_loss_price:
            if float(take_profit_price) < float(stop_loss_price):
                dlg = CustomDialog_buy()
                dlg.exec()
                return
        update_config(symbol,leverage,order_quantity_pct,take_profit_price,stop_loss_price,limit_price)
        setOdersList()

    def sell_stock(self):
        symbol = self.sizeCurrency.currentText()
        leverage = str(self.Nx_spin.value())
        order_quantity_pct = str(self.percent_spin.value())
        take_profit_price = str(self.tpEdit.text())
        stop_loss_price = str(self.slEdit.text())
        limit_price = str(self.priceEdit.text())
        dialog = CustomDialog_Confirm()
        if dialog.exec_() == QDialog.Accepted:
            print("OK clicked")
        else:
            print("Cancel clicked")
            return
        if take_profit_price and stop_loss_price:
            if float(take_profit_price) >= float(stop_loss_price):
                dlg = CustomDialog_sell()
                dlg.exec()
                return
        update_config(symbol,leverage,order_quantity_pct,take_profit_price,stop_loss_price,limit_price)
        setOdersList()
    def close_limit(self):
        dialog = CustomDialog_Confirm()
        if dialog.exec_() == QDialog.Accepted:
            print("OK clicked")
        else:
            print("Cancel clicked")
            return
        symbol = self.sizeCurrency.currentText()
        # os.system(f"python trading_limit_close.py {symbol}")
        traing_limit_close(symbol)
        # os.system('py trading_limit_close.py')
    def close_market(self):
        dialog = CustomDialog_Confirm()
        if dialog.exec_() == QDialog.Accepted:
            print("OK clicked")
        else:
            print("Cancel clicked")
            return
        symbol = self.sizeCurrency.currentText()
        # os.system(f"python trading_market_close.py {symbol}")
        # os.system(f"py trading_market_close.py {symbol}")
        trading_market_close(symbol)

def main():
    
    app = QApplication(sys.argv)
    form = MainWindowApp()
    form.show()
    app.exec_()
if __name__ == '__main__':
    main()