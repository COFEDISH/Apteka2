import sys

from Data import Get_data
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QDialog, QLabel, \
    QListWidget, QListWidgetItem, QComboBox, QMessageBox, QHBoxLayout, QFrame, QFileDialog, QInputDialog
import json

from googletrans import Translator

from Auth import LoginWindow
from Admin import start

from geopy.geocoders import Nominatim

class StartPage(QWidget):
    def __init__(self, city, data, pharmacies):
        super().__init__()
        self.authenticated = False
        layout = QVBoxLayout()
        self.data = json.loads(data)
        self.pharmacies = json.loads(pharmacies)
        self.filtered_data = []
        self.cart = {}
        available_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(int(available_geometry.width() * 0.9), int(available_geometry.height() * 0.9))
        self.showFullScreen()

        # Установка стилей для улучшения внешнего вида
        self.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border: none;
                color: white;
                padding: 8px 12px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #58D68D;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #E8DDB5;
                padding: 4px;
            }
        """)

        # Кнопка "Корзина"
        cart_button = QPushButton()
        cart_button.setIcon(QIcon(r"icons/list.png"))
        cart_button.clicked.connect(self.show_cart)

        # Кнопка для входа в аккаунт
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.show_login_window)

        # Кнопка для административного режима
        self.admin_button = QPushButton("Администратор")
        self.admin_button.setVisible(False)
        self.admin_button.clicked.connect(self.admin_mode)

        # Добавление кнопок в основной layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cart_button)
        buttons_layout.addWidget(self.admin_button)
        layout.addLayout(buttons_layout)

        # Добавление поля поиска и кнопки поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название лекарства или производителя")
        search_layout.addWidget(self.search_input)
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_medicine)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Отдельный layout для фильтров (сверху)
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы вокруг layout
        filter_layout.setSpacing(2)

        self.min_price_input = QLineEdit()
        self.min_price_input.setPlaceholderText("Минимальная цена")
        filter_layout.addWidget(self.min_price_input)

        self.max_price_input = QLineEdit()
        self.max_price_input.setPlaceholderText("Максимальная цена")
        filter_layout.addWidget(self.max_price_input)

        self.manufacturer_input = QLineEdit()
        self.manufacturer_input.setPlaceholderText("Производитель")
        filter_layout.addWidget(self.manufacturer_input)

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("Действие")
        filter_layout.addWidget(self.action_input)

        apply_filter_button = QPushButton("Применить фильтр")
        apply_filter_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_filter_button)

        # Добавляем фильтры в отдельный layout
        layout.addLayout(filter_layout)

        # Создание красивого текста
        beautiful_text = QLabel(
            "<h1 style='color: #2E86C1; font-family: Arial, sans-serif;'>Добро пожаловать в приложение Apteka!</h1>"
            "<p style='font-size: 18px; color: #34495E; font-family: Arial, sans-serif;'>"
            "Введите название лекарства или производителя. Для удобства поиска предусмотрены фильтры выше."
            "</p>"
        )
        beautiful_text.setAlignment(Qt.AlignCenter)  # Выравнивание по центру

        layout.addWidget(beautiful_text)
        layout.addStretch()  # Растягиваем, чтобы элементы заполнили доступное пространство

        # Табличка с лекарствами (ниже)
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        # Устанавливаем основной layout для окна
        self.setLayout(layout)

        # Изменяем размеры для главной таблицы (QListWidget)
        self.list_widget.setStyleSheet("QListWidget { border: 0px; }")  # Убираем границу у таблицы
        self.list_widget.setFixedSize(1600, 900)  # Устанавливаем желаемые размеры таблицы

        # Изменение размера шрифта в таблице
        font = self.list_widget.font()
        font.setPointSize(14)  # Установите размер шрифта, который хотите использовать
        self.list_widget.setFont(font)

        # Установка стилей для фильтров
        self.min_price_input.setStyleSheet("QLineEdit { padding: 10px; }")
        self.max_price_input.setStyleSheet("QLineEdit { padding: 10px; }")
        self.manufacturer_input.setStyleSheet("QLineEdit { padding: 10px; }")
        self.action_input.setStyleSheet("QLineEdit { padding: 10px; }")
        apply_filter_button.setStyleSheet("QPushButton { padding: 6px 10px; }")

        self.setLayout(layout)
        self.show_filtered_medicines()
        self.login_window = None

    def show_login_window(self):
        if not self.authenticated:  # Если пользователь не аутентифицирован
            login_window = LoginWindow(self)  # Создать окно входа
            if login_window.exec() == QDialog.Accepted:
                self.authenticated = True
                self.login_button.setVisible(False)  # Скрыть кнопку Войти при успешной аутентификации
                # Показать кнопку Администратор при успешной аутентификации
                self.admin_button.setVisible(True)
            else:
                self.authenticated = False

    def search_medicine(self):
        search_text = self.search_input.text().lower()

        self.list_widget.clear()

        for medicine in self.data:
            # Проверяем условия поиска по названию лекарства или производителю
            if (search_text in medicine["Лекарство"].lower()) or (search_text in medicine["Производитель"].lower()):
                item_text = f"{medicine['Лекарство']} - {medicine['Производитель']} {medicine["Стоимость"]}р"
                item = QListWidgetItem(item_text)
                item.setData(100, medicine)  # Используем UserType 100 для хранения данных лекарства
                self.list_widget.addItem(item)

                # Устанавливаем всплывающую подсказку (описание лекарства)
                tooltip_text = medicine.get("Описание", "")
                item.setToolTip(tooltip_text)

    def admin_mode(self):
        start(city)

    def apply_filters(self):
        try:
            min_price = float(self.min_price_input.text() or 0)
            max_price = float(self.max_price_input.text() or float('inf'))
            manufacturer = self.manufacturer_input.text().lower()
            action = self.action_input.text().lower()

            self.filtered_data = []

            for medicine in self.data:
                cost = float(medicine["Cost"])
                if min_price <= cost <= max_price and (manufacturer in medicine["Производитель"].lower()) and (
                        action in medicine["Категория по действию"].lower()):
                    self.filtered_data.append(medicine)

            self.show_filtered_medicines()
        except ValueError:
            print("Введите корректные значения для фильтрации")

    def show_filtered_medicines(self):
        self.list_widget.clear()

        for medicine in self.filtered_data:
            item_text = f"{medicine['Лекраство']} - {medicine['Производитель']}"
            item = QListWidgetItem(item_text)
            item.setData(100, medicine)
            self.list_widget.addItem(item)

            # Добавление описания в качестве данных элемента списка
            description = medicine.get('Описание', 'No description available')  # Получение описания лекарства
            item.setData(Qt.ToolTipRole, description)  # Установка описания в элемент списка

    def on_item_clicked(self, item):
        # Получение данных лекарства по клику на элемент списка
        medicine = item.data(100)
        if medicine:
            self.show_pharmacies(medicine)

    def extract_numbers_from_string(self, text):
        return [int(s) for s in text.split() if s.isdigit()]

    def show_pharmacies(self, medicine):

        # Установка стилей для улучшения внешнего вида
        self.setStyleSheet("""
                           QPushButton {
                               background-color: #2ECC71;
                               border: none;
                               color: white;
                               padding: 8px 12px;
                               text-align: center;
                               text-decoration: none;
                               display: inline-block;
                               font-size: 14px;
                               margin: 4px 2px;
                               transition-duration: 0.4s;
                               cursor: pointer;
                               border-radius: 4px;
                           }
                           QPushButton:hover {
                               background-color: #58D68D;
                               color: white;
                           }
                           QLineEdit {
                               padding: 8px;
                               border: 1px solid #ccc;
                               border-radius: 4px;
                           }
                           QTableWidget {
                               border: 1px solid #ccc;
                               border-radius: 4px;
                               font-size: 12px;
                           }
                           QHeaderView::section {
                               background-color: #E8DDB5;
                               padding: 4px;
                           }
                       """)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Информация о лекарстве {medicine['Лекарство']}")
        layout = QVBoxLayout()

        details_info = f"""
            <p style='font-size: 14px; color: #34495E; font-family: Arial, sans-serif;'>
                <b>Категория по действию:</b> {medicine["Категория по действию"]}<br>
                <b>Категория по системе:</b> {medicine["Категория по системе"]}<br>
                <b>Производитель:</b> {medicine["Производитель"]}<br>
                <b>Дата производства:</b> {medicine["Дата производства"]}<br>
                <b>Стоимость:</b> {medicine["Стоимость"]}<br>
                <b>Количество:</b> {medicine["Количество"]}<br>
                <b>Описание:</b> {medicine["Описание"]}
            </p>
        """

        details_label = QLabel(details_info)
        layout.addWidget(details_label)

        pharmacy_ids = self.extract_numbers_from_string(medicine.get('Наличие в аптеках', ''))
        available_pharmacies = []
        for pharmacy in self.pharmacies:
            if int(pharmacy["Id"]) in pharmacy_ids:
                available_pharmacies.append(pharmacy)

        if available_pharmacies:
            pharmacy_combo = QComboBox()
            pharmacy_combo.addItem("Выберите аптеку")
            for pharmacy in available_pharmacies:
                combined_text = f"{pharmacy['Название']} - {pharmacy['Адрес']}"  # Комбинируем имя и адрес
                pharmacy_combo.addItem(combined_text)
            layout.addWidget(pharmacy_combo)

            # Кнопка для добавления в список
            add_to_cart_button = QPushButton("Добавить в корзину")
            add_to_cart_button.clicked.connect(lambda: self.add_to_cart(medicine, available_pharmacies[
                pharmacy_combo.currentIndex() - 1] if pharmacy_combo.currentIndex() > 0 else None))
            layout.addWidget(add_to_cart_button)
        else:
            no_pharmacy_label = QLabel("Доступность в аптеках отсутствует")
            layout.addWidget(no_pharmacy_label)
        dialog.setLayout(layout)
        dialog.exec()

    def add_to_cart(self, medicine, selected_pharmacy):
        if selected_pharmacy:
            total_cost = int(medicine["Стоимость"])
            medicine_info = {
                "Medicine": medicine["Лекарство"],
                "Manufacturer": medicine["Производитель"],
                "Quantity": 1,  # Установим начальное количество в 1
                "Total Cost": total_cost,
                "PharmacyAddress": selected_pharmacy["Адрес"]
            }

            pharmacy_key = selected_pharmacy["Название"]
            if pharmacy_key in self.cart:
                medicines_list = self.cart[pharmacy_key]
                medicine_found = False

                for item in medicines_list:
                    if item["Medicine"] == medicine_info["Medicine"]:
                        item["Quantity"] += 1
                        item["Total Cost"] += medicine_info["Total Cost"]
                        medicine_found = True
                        break

                if not medicine_found:
                    medicines_list.append(medicine_info)
            else:
                self.cart[pharmacy_key] = [medicine_info]

            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(r'icons\plus_icon.ico'))  # Замените путь на путь к вашей иконке
            msg_box.setWindowTitle("Успех!")
            msg_box.setText(f"Лекарство {medicine['Лекарство']} добавлено в корзину. Количество: 1, Общая стоимость: {total_cost}")
            msg_box.exec()
        else:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(r'icons\plus_icon.ico'))  # Замените путь на путь к вашей иконке
            msg_box.setWindowTitle("Предупреждение")
            msg_box.setText("Пожалуйста, выберите доступную аптеку для лекарства.")
            msg_box.exec()

    def confirm_add_to_cart(self, medicine, quantity, selected_pharmacy):
        try:
            quantity = int(quantity)
            total_cost = int(medicine["Стоимость"]) * quantity
            medicine_info = {
                "Medicine": medicine["Лекарство"],
                "Manufacturer": medicine["Производитель"],
                "Quantity": quantity,
                "Total Cost": total_cost,
                "PharmacyAddress": selected_pharmacy["Адрес"]
            }

            pharmacy_key = selected_pharmacy["Name"]
            if pharmacy_key in self.cart:
                medicines_list = self.cart[pharmacy_key]
                medicine_found = False

                for item in medicines_list:
                    if item["Medicine"] == medicine_info["Medicine"]:
                        item["Quantity"] += medicine_info["Quantity"]
                        item["Total Cost"] += medicine_info["Total Cost"]
                        medicine_found = True
                        break

                if not medicine_found:
                    medicines_list.append(medicine_info)
            else:
                self.cart[pharmacy_key] = [medicine_info]

            print(f"Лекарство {medicine['Лекарство']} добавлено в корзину. Количество: {quantity}, Общая стоимость: {total_cost}")
        except ValueError:
            print("Пожалуйста, введите корректное количество (целое число)")

    def show_cart(self):
        if hasattr(self, 'cart_dialog'):
            self.cart_dialog.close()

        self.cart_dialog = QDialog()
        self.cart_dialog.setWindowIcon(QIcon(r'icons\plus_icon.ico'))  # Замените путь на путь к вашей иконке
        self.cart_dialog.setWindowTitle("Корзина")

        main_layout = QVBoxLayout()

        cart_layout = QVBoxLayout()  # Виджет с содержимым корзины

        # Виджет для итоговой стоимости
        total_cost_frame = QFrame()
        total_cost_layout = QHBoxLayout()  # Размещение для итоговой стоимости

        total_cost_label = QLabel("<h3 style='color: #2980B9;'>Итоговая стоимость:</h3>")

        total_cost = sum(item['Total Cost'] for pharmacy, medicines in self.cart.items() for item in medicines)
        total_cost_value = QLabel(
            f"<p style='font-size: 16px; color: #C0392B;'>{total_cost} Руб.</p>")  # Виджет для отображения стоимости

        total_cost_layout.addWidget(total_cost_label)
        total_cost_layout.addWidget(total_cost_value)

        total_cost_frame.setLayout(total_cost_layout)

        save_button = QPushButton("Сохранить корзину")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border: none;
                color: white;
                padding: 8px 12px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
                color: white;
            }
        """)
        save_button.clicked.connect(self.save_cart_to_file)

        total_cost_layout.addWidget(save_button)

        cart_layout.addWidget(total_cost_frame)

        # Добавляем содержимое корзины в основной виджет
        if not self.cart:
            cart_layout.addWidget(QLabel("<h2 style='color: #8E44AD;'>Корзина пуста :(</h2>"))
        else:
            for pharmacy, medicines in self.cart.items():
                pharmacy_label = QLabel(
                    f"<h3 style='color: #2980B9;'>Аптека: {pharmacy} ({medicines[0]['PharmacyAddress']})</h3>")
                cart_layout.addWidget(pharmacy_label)

                for item in medicines:
                    layout = QHBoxLayout()

                    cart_info = f"<p style='font-size: 14px; color: #2C3E50;'>{item['Medicine']} - {item['Manufacturer']}, Количество: {item['Quantity']}, Общая стоимость: {item['Total Cost']} Руб.</p>"
                    info_label = QLabel(cart_info)

                    minus_button = QPushButton("-")
                    minus_button.setStyleSheet("""
                        QPushButton {
                            background-color: #2ECC71;
                            border: none;
                            color: white;
                            padding: 6px 10px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 14px;
                            margin: 2px 4px;
                            transition-duration: 0.4s;
                            cursor: pointer;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #2ECC71;
                            color: white;
                        }
                    """)
                    minus_button.clicked.connect(lambda med=item, pharm=pharmacy: self.update_quantity(med, pharm, -1))

                    plus_button = QPushButton("+")
                    plus_button.setStyleSheet("""
                        QPushButton {
                            background-color: #2ECC71;
                            border: none;
                            color: white;
                            padding: 6px 10px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 14px;
                            margin: 2px 4px;
                            transition-duration: 0.4s;
                            cursor: pointer;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #2ECC71;
                            color: white;
                        }
                    """)
                    plus_button.clicked.connect(lambda med=item, pharm=pharmacy: self.update_quantity(med, pharm, 1))

                    quantity_layout = QHBoxLayout()
                    quantity_label = QLabel(f"<p style='font-size: 14px; color: #27AE60;'>{item['Quantity']}</p>")

                    delete_item_button = QPushButton("x")
                    delete_item_button.setStyleSheet("""
                        QPushButton {
                            background-color: #E74C3C;
                            border: none;
                            color: white;
                            padding: 6px 10px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 14px;
                            margin: 2px 4px;
                            transition-duration: 0.4s;
                            cursor: pointer;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #C0392B;
                            color: white;
                        }
                    """)
                    delete_item_button.clicked.connect(
                        lambda med=item, pharm=pharmacy: self.remove_item_from_cart(pharm, med))

                    layout.addWidget(info_label)
                    layout.addWidget(minus_button)
                    layout.addWidget(plus_button)
                    layout.addWidget(delete_item_button)
                    layout.addWidget(quantity_label)
                    cart_layout.addLayout(layout)

        main_layout.addLayout(cart_layout)
        self.cart_dialog.setLayout(main_layout)
        self.cart_dialog.exec()

    def remove_item_from_cart(self, pharmacy, medicine):
        if pharmacy in self.cart and medicine in self.cart[pharmacy]:
            self.cart[pharmacy].remove(medicine)
            print(f"Удалено из корзины: {medicine['Medicine']} из {pharmacy}")
            if not self.cart[pharmacy]:  # Если категория пуста после удаления лекарства
                del self.cart[pharmacy]  # Удалить категорию из корзины
                print(f"Категория {pharmacy} удалена из корзины")
            self.show_cart()

    def remove_category_from_cart_button_clicked(self):
        pharmacy = self.sender().pharmacy
        self.remove_category_from_cart(pharmacy)

    def remove_category_from_cart(self, pharmacy):
        if pharmacy in self.cart:
            del self.cart[pharmacy]
            print(f"Удалена категория {pharmacy} из корзины")
            self.show_cart()

    def update_quantity(self, medicine, pharmacy, change):
        new_quantity = medicine["Quantity"] + change
        if new_quantity > 0:
            old_quantity = medicine["Quantity"]
            medicine["Quantity"] = new_quantity
            medicine["Total Cost"] = int(medicine["Total Cost"]) * new_quantity // old_quantity

            print(
                f"Количество {medicine['Medicine']} обновлено в корзине. Новое количество: {new_quantity}, Новая стоимость: {medicine['Total Cost']}")
            self.show_cart()
        else:
            self.remove_item_from_cart(pharmacy, medicine)

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            file.write("Итоговая корзина:\n\n")
            total_cost = 0
            for pharmacy, medicines in self.cart.items():
                file.write(f"Аптека: {pharmacy}\n")
                for item in medicines:
                    file.write(f"Лекарство: {item['Medicine']} - {item['Manufacturer']}\n")
                    file.write(f"Количество: {item['Quantity']}, Общая стоимость: {item['Total Cost']}\n")
                    total_cost += item['Total Cost']
                file.write("\n")
            file.write(f"Итоговая стоимость всей корзины: {total_cost}\n")
        print(f"Итоговый список сохранен в файл: {file_path}")

    def save_cart_to_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.save_to_file(file_path)


def get_user_location():
    city_mappings = {
        "Москва": "msk",
        "Санкт-Петербург": "spb",
        "Новосибирск": "nsk",
        "Екатеринбург": "ekb",
        "Нижний Новгород": "nn",
        "Казань": "kzn",
        "Челябинск": "chlb",
        "Омск": "omsk",
        "Самара": "smr",
        "Ростов-на-Дону": "rnd"
    }

    cities = list(city_mappings.keys())

    dialog = QInputDialog()
    dialog.setWindowTitle("Выберите город")
    dialog.setWindowIcon(QIcon(r'icons\plus_icon.ico'))  # Замените путь на путь к вашей иконке

    # Получаем кнопку в диалоговом окне
    button = dialog.findChild(QPushButton)
    if button:
        # Применяем стили к кнопке
        button.setStyleSheet("background-color: #6495ED; color: white; font-weight: bold;")

    city, ok_pressed = dialog.getItem(None, "Выберите город", "Список городов", cities, 0, False)

    if ok_pressed and city:
        print(f"Выбран город: {city}")
        print(city_mappings.get(city))
        return city_mappings.get(city)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    city = get_user_location()
    data = Get_data(city)
    # Ваши JSON данные о лекарствах и аптеках
    medicine_data = data.get_data_Medicine()
    pharmacy_data = data.get_data_Pharmacy()

    main_window = QMainWindow()
    main_window.setWindowTitle("Apteka")
    main_window.setWindowIcon(QIcon(r'icons\plus_icon.ico'))  # Установка иконки окна
    main_window.setGeometry(100, 100, 800, 600)

    start_page = StartPage(city, medicine_data, pharmacy_data)
    main_window.setCentralWidget(start_page)

    main_window.show()
    sys.exit(app.exec())