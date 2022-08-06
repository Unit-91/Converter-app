import sys
from my_lib.printf import *
from converter_ui import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class Converter_app(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Converter_ui()
        self.ui.setupUi(self)

        self.inputs_dict = {
            self.ui.USD_input: "BASE_CUR",
            self.ui.RUB_input: "USD_RUB",
            self.ui.KZT_input: "USD_KZT"
        }

        reg = QRegularExpression('^[0-9]+[.,]?[0-9]+')
        reg_validator = QtGui.QRegularExpressionValidator(reg)

        for input in self.inputs_dict.keys():
            input.setValidator(reg_validator)
            input.textEdited.connect(self.convert_currencies)

        self.rates = self.get_exchange_rates()

    def get_exchange_rates(self):
        self.conv = Converter('currency_data.json')

        self.conv.add_currencies('USD_RUB', 'USD_KZT')

        url = 'https://free.currconv.com/api/v7/convert'
        currencies = ','.join(self.conv.get_currencies())
        params = {
            'q': currencies,
            'compact': 'ultra',
            'apiKey': 'dd561cebd6f8203e6f0c'
        }

        self.new_date = self.conv.get_date()
        self.old_date = self.conv.get_old_date()

        if not self.new_date == self.old_date:
            try:
                self.rates = self.conv.get_rates(url, params)
                self.conv.save_date(self.new_date)
                self.conv.save_rates(self.rates)

            except HTTPError as error:
                self.rates = self.conv.get_old_rates()
                info = f"Неполучилось достать текущий курс валют, приложение будет использовать курс за {self.old_date}"
                QMessageBox.information(self.ui.centralwidget, 'Старый курс!', info)
        else:
            self.rates = self.conv.get_old_rates()

        return self.rates

    def convert_currencies(self):
        sender = self.sender()
        sender_currency = self.inputs_dict[sender]

        if not sender.text() == '':
            amount = float(sender.text().replace(',', '.'))

            result = self.conv.convert(self.rates, sender_currency, amount)

            for input, currencies in self.inputs_dict.items():
                if not input == sender:
                    rounded_result = int(result[currencies] * 100) / 100
                    input.setText(str(rounded_result).replace('.', ','))
        else:
            for input in self.inputs_dict.keys():
                input.setText('')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        window = Converter_app()
        window.show()
    except Exception as error:
        printf('Ошибка!: ', error, col=160)

    sys.exit(app.exec())
