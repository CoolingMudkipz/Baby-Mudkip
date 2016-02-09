import ast
import random
import re
import sys

import discord
from PyQt5 import QtWidgets, Qt, QtCore


def calc_random(dice, dice_type):
    sum_var = 0
    arr = []
    for i in range(0, dice):
        roll = random.SystemRandom().randrange(0, dice_type) + 1
        arr.append(roll)
        sum_var += roll
    return sum_var, dice, dice_type, arr


class DiscordClient(discord.Client):
    def __init__(self, **kwargs):
        super(DiscordClient, self).__init__(**kwargs)

    def handle_message(self, message):
        for mention in message.mentions:
            if mention.id == self.user.id:
                matches = re.findall('(\d+)d(\d+)', message.content)
                out = re.sub('<@\w+>', '', message.content)
                results = ''
                for match in matches:
                    dsum, dice, d_type, res = calc_random(int(match[0]), int(match[1]))
                    results += str(dice) + 'd' + str(d_type) + ' -> ' + str(res) + '\n'
                    out = out.replace(str(dice) + 'd' + str(d_type), str(dsum), 1)
                out = re.sub('^\s+', '', out)
                out2 = ''
                try:
                    out2 = results + out + ' = ' + str(ast.literal_eval(out))
                except:
                    out2 = results + out

                self.send_message(message.channel, out2)
                return

client = DiscordClient()
app = None


class CloseApp(QtWidgets.QWidget):
    def __init__(self):
        super(CloseApp, self).__init__()
        self.setWindowTitle('Discord Bot')
        self.setVisible(False)
        self.quit = QtWidgets.QPushButton()
        self.quit.setText('Exit')
        self.quit.clicked.connect(app.quit)
        self.l = QtWidgets.QVBoxLayout()
        self.l.addWidget(self.quit)
        self.setLayout(self.l)

    def logged_in(self):
        self.setVisible(True)
        self.show()


class LoginWindow(QtWidgets.QWidget):
    started = QtCore.pyqtSignal()
    failure = QtCore.pyqtSignal()

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setWindowTitle('Discord Bot')
        self.l = QtWidgets.QFormLayout()
        self.username = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login = QtWidgets.QPushButton('Login')
        self.l.addRow('Email:', self.username)
        self.l.addRow('Password:', self.password)
        self.l.addRow('', self.login)
        self.setLayout(self.l)
        self.password.returnPressed.connect(self.login.click)
        self.login.clicked.connect(self.do_login)
        self.failure.connect(self.reset_and_show)

    def reset_and_show(self):
        self.password.setText('')
        self.show()

    def do_login(self):
        try:
            self.close()
            client.login(self.username.text(), self.password.text())
            discordRunner.start()
            self.started.emit()
        except discord.LoginFailure as e:
            msg = QtWidgets.QMessageBox()
            msg.setModal(True)
            msg.setText('Cannot Login. Are username and password correct?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            print(e)
            self.failure.emit()


class DiscordRunner(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        if client.is_logged_in:
            client.logout()
        self.wait()

    def run(self):
        client.run()


discordRunner = DiscordRunner()
trayIcon = None

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    trayIcon = CloseApp()
    ui = LoginWindow()
    ui.started.connect(trayIcon.logged_in)
    ui.show()
    app.setQuitOnLastWindowClosed(False)
    app.exec_()
