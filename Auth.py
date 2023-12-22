import socket

from Data import Get_data
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        # Проверка логина и пароля
        username = self.username_input.text()
        password = self.password_input.text()
        print(password)
        check_password = Get_data.get_password(self, username)

        if password == check_password:
            self.accept()  # Вход выполнен успешно
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")