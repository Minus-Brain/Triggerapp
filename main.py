import sys
import os
import sqlite3
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QListWidget, QDialog


class TriggerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить триггер")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        
        layout = QVBoxLayout()

        self.input_phrase = QLineEdit(self)
        self.input_phrase.setPlaceholderText('Введите фразу триггера')
        layout.addWidget(self.input_phrase)

        self.select_app_btn = QPushButton('Выбрать приложение', self)
        self.select_app_btn.clicked.connect(self.select_app)
        layout.addWidget(self.select_app_btn)

        self.add_trigger_btn = QPushButton('Добавить триггер', self)
        self.add_trigger_btn.clicked.connect(self.add_trigger)
        layout.addWidget(self.add_trigger_btn)

        self.setLayout(layout)

    def select_app(self):
        self.app_path, _ = QFileDialog.getOpenFileName(self, 'Выберите приложение')
        if self.app_path:
            self.select_app_btn.setText(f'Выбрано: {os.path.basename(self.app_path)}')

    def add_trigger(self):
        phrase = self.input_phrase.text()
        app_path = getattr(self, 'app_path', None)
        if not phrase or not app_path:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        self.accept()
        self.trigger_data = (phrase, app_path)


class VoiceControlApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_name = 'triggers.db'  
        self.create_table()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Управление Триггерами')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #3b3b3b; }
            QLabel { font-size: 18px; color: #ffffff; }
            QPushButton { font-size: 16px; background-color: #6a5acd; color: #ffffff; border-radius: 10px; padding: 10px; }
            QPushButton:hover { background-color: #836fff; }
            QLineEdit { font-size: 16px; background-color: #2e2e2e; color: #ffffff; border: 2px solid #6a5acd; border-radius: 5px; padding: 5px; }
        """)

        main_layout = QtWidgets.QHBoxLayout()

    
        left_layout = QVBoxLayout()

        self.label = QLabel('Голосовое управление и добавление триггеров')
        left_layout.addWidget(self.label)

        self.start_listen_btn = QPushButton('Начать распознавание голоса', self)
        self.start_listen_btn.clicked.connect(self.start_listening)
        left_layout.addWidget(self.start_listen_btn)

        main_layout.addLayout(left_layout, 2)


        self.trigger_list = QListWidget(self)
        self.trigger_list.setStyleSheet("background-color: #444444; color: #ffffff; font-size: 16px; padding: 5px;")
        main_layout.addWidget(self.trigger_list, 3)

        self.add_trigger_btn = QPushButton('+', self)
        self.add_trigger_btn.setMaximumSize(50, 50)
        self.add_trigger_btn.setStyleSheet("font-size: 24px; background-color: #6a5acd; color: #ffffff; border-radius: 25px;")
        self.add_trigger_btn.clicked.connect(self.open_add_trigger_dialog)
        main_layout.addWidget(self.add_trigger_btn, alignment=QtCore.Qt.AlignTop)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.refresh_trigger_list()

    def open_add_trigger_dialog(self):
        dialog = TriggerDialog()
        if dialog.exec_():
            self.save_trigger(dialog.trigger_data)
            self.refresh_trigger_list()

    def save_trigger(self, trigger_data):
        phrase, app_path = trigger_data
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO triggers (phrase, app_path) VALUES (?, ?)", (phrase, app_path))
            conn.commit()

    def refresh_trigger_list(self):
        self.trigger_list.clear()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT phrase, app_path FROM triggers")
            triggers = cursor.fetchall()

        for phrase, app_path in triggers:
            self.trigger_list.addItem(f"{phrase}\n  {app_path}")

    def start_listening(self):
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.label.setText('Говорите...')
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio, language='ru-RU')
            self.label.setText(f'Распознано: {command}')
            self.execute_command(command)
        except sr.UnknownValueError:
            self.label.setText('Не удалось распознать речь')
        except sr.RequestError:
            self.label.setText('Ошибка сервиса распознавания речи')

    def execute_command(self, command):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT app_path FROM triggers WHERE phrase=?", (command,))
            result = cursor.fetchone()

        if result:
            app_path = result[0]
            os.startfile(app_path)
            self.label.setText(f"Запускаю: {app_path}")
        else:
            self.label.setText('Команда не найдена')

    def create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phrase TEXT NOT NULL,
                    app_path TEXT NOT NULL
                )
            """)
            conn.commit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = VoiceControlApp()
    main_window.show()
    sys.exit(app.exec_())
