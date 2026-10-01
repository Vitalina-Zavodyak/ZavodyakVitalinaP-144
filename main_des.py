import sys
import json
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
# ВАЖЛИВО: Змініть назву файлу імпорту на той, який згенерував Qt Designer
# Якщо у вас файл називається design.py, то буде: from design import Ui_MainWindow
from design import Ui_MainWindow


class GardenAuthApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Змінні для захисту від брутфорсу
        self.failed_attempts = 0
        self.lockout_time = 0

        # Підключення кнопок до функцій
        self.btnLogin.clicked.connect(self.handle_login)
        self.btnRegister.clicked.connect(self.handle_registration)

        # Початкове завантаження бази даних
        self.users = self.load_users()

    def load_users(self):
        """Завантаження користувачів з файлу users.json"""
        try:
            with open('users.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_users(self):
        """Збереження користувачів у файл users.json"""
        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump(self.users, file, indent=4, ensure_ascii=False)

    def handle_login(self):
        """Логіка входу (Студент 1 + Студент 2)"""
        # 1. Перевірка на блокування (Захист від брутфорсу - Студент 2)
        current_time = time.time()
        if current_time < self.lockout_time:
            remaining = int(self.lockout_time - current_time)
            QMessageBox.warning(self, "Блокування", f"Занадто багато спроб. Зачекайте {remaining} сек.")
            return

        email = self.txtLoginEmail.text().strip()
        password = self.txtPassword.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть всі поля!")
            return

        user_found = None
        for user in self.users:
            if user['email'] == email and user['password'] == password:
                user_found = user
                break

        if user_found:
            # Скидання лічильника невдач при успішному вході
            self.failed_attempts = 0

            # Логіка для Адміна (Студент 2)
            if user_found['role'] == 'admin':
                total_users = len(self.users)
                QMessageBox.information(self, "Адмін-панель",
                                        f"Вітаємо, Адміне!\nЗагальна кількість користувачів: {total_users}")

            # Логіка для Покупця (Студент 1)
            else:
                QMessageBox.information(self, "Успіх", "Вітаємо у нашому саду!")

                # Обробка чекбоксу "Запам'ятати мене"
                if self.chkRemember.isChecked():
                    with open('session.txt', 'w', encoding='utf-8') as f:
                        f.write(email)
                else:
                    # Якщо чекбокс не натиснуто, видаляємо стару сесію, якщо вона є
                    import os
                    if os.path.exists('session.txt'):
                        os.remove('session.txt')
        else:
            # Невдала спроба
            self.failed_attempts += 1
            QMessageBox.warning(self, "Помилка", "Невірний email або пароль!")

            # Перевірка на 3 невдалі спроби (Студент 2)
            if self.failed_attempts >= 3:
                self.lockout_time = time.time() + 10  # Блокування на 10 секунд
                self.failed_attempts = 0
                QMessageBox.critical(self, "Блокування", "3 невдалі спроби! Кнопку входу заблоковано на 10 секунд.")

    def handle_registration(self):
        """Логіка реєстрації (Студент 1)"""
        email = self.txtLoginEmail_2.text().strip()
        password = self.txtPassword_2.text().strip()
        confirm_password = self.txtConfirmPassword.text().strip()

        if not email or not password or not confirm_password:
            QMessageBox.warning(self, "Помилка", "Заповніть всі поля для реєстрації!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Помилка", "Паролі не збігаються!")
            return

        # Перевірка, чи не зайнятий email
        for user in self.users:
            if user['email'] == email:
                QMessageBox.warning(self, "Помилка", "Користувач з таким email вже існує!")
                return

        # Додавання нового користувача
        new_user = {
            "email": email,
            "password": password,
            "role": "customer"
        }
        self.users.append(new_user)
        self.save_users()

        QMessageBox.information(self, "Успіх", "Реєстрація успішна! Тепер ви можете увійти.")

        # Очищення полів реєстрації
        self.txtLoginEmail_2.clear()
        self.txtPassword_2.clear()
        self.txtConfirmPassword.clear()

        # Перемикання на вкладку входу (індекс 0)
        self.tabWidget.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GardenAuthApp()
    window.show()
    sys.exit(app.exec_())