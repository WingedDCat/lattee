import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
import sqlite3
from UI.main import Ui_MainWindow
from UI.addEditCoffeeForm import Ui_MainWindow as ui_addCoffeeWindow

class Add_modal(QMainWindow, ui_addCoffeeWindow):
    sortSaved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #uic.loadUi('./UI/addEditCoffeeForm.ui', self)
        self.setWindowTitle('Добавление нового сорта')
        self.btn_save.clicked.connect(self.on_btn_save_click)
        self.action = 'add'

    def open_for_add(self):
        self.action = 'add'
        self.txt_sort.setText('')
        self.cmb_grains.setCurrentIndex(0)
        self.txt_taste.setText('')
        self.txt_price.setText('')
        self.txt_volume.setText('')
        self.txt_supplier.setText('')
        self.cmb_roast.setCurrentIndex(0)
        self.show()

    def open_for_edit(self, data):
        self.action = 'edit'
        self.current_id = int(data[0])
        self.txt_sort.setText(data[1])
        self.cmb_roast.setCurrentText(data[2])
        self.cmb_grains.setCurrentText(data[3])
        self.txt_taste.setText(data[4])
        self.txt_price.setText(data[5])
        self.txt_volume.setText(data[6])
        self.txt_supplier.setText(data[7])
        self.show()

    def on_btn_save_click(self):
        sort = self.txt_sort.toPlainText()
        grains = self.cmb_grains.currentText()
        taste = self.txt_taste.toPlainText()
        price = self.txt_price.toPlainText()
        volume = self.txt_volume.toPlainText()
        supplier = self.txt_supplier.toPlainText()
        roast = self.cmb_roast.currentText()

        try:
            with sqlite3.connect('./data/coffe.sqlite') as connection:
                cursor = connection.cursor()
                if self.action == 'add':
                    cursor.execute('''
                                INSERT INTO coffe (sort, roast, grains, taste, price, volume,supplier)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (sort, roast, grains, taste, price, volume,supplier))
                elif self.action == 'edit':
                    cursor.execute('''
                                        UPDATE coffe
                                        SET sort=?, roast=?, grains=?, taste=?, price=?, volume=?, supplier=?
                                        WHERE id=?
                                    ''', (sort, roast, grains, taste, price, volume, supplier, self.current_id))

                connection.commit()
                self.sortSaved.emit()
                self.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при работе с базой данных: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {e}')



class Shaobicoffee(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #uic.loadUi('./UI/main.ui', self)
        self.setWindowTitle('Кофейная коллекция')
        self.load_database()
        self.btn_add.clicked.connect(self.on_btn_add_click)
        self.window1 = Add_modal()
        self.window1.sortSaved.connect(self.on_sort_saved)
        self.btn_edit.clicked.connect(self.on_btn_edit_click)
        self.btn_remove.clicked.connect(self.on_btn_remove_click)

    def on_sort_saved(self):
        self.load_database()

    def on_btn_add_click(self):
        self.window1.open_for_add()

    def load_database(self):
        try:
            with sqlite3.connect('./data/coffe.sqlite') as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM coffe")
                coffe_data = cursor.fetchall()

                self.tableWidget.setRowCount(len(coffe_data))
                self.tableWidget.setColumnCount(len(coffe_data[0]) if coffe_data else 0)
                self.tableWidget.setHorizontalHeaderLabels(
                    ['ID', 'Название', 'Степень обжарки', 'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем упаковки', 'Поставщик']
                )

                for row_num, row_data in enumerate(coffe_data):
                    for col_num, col_data in enumerate(row_data):
                        item = QTableWidgetItem(str(col_data))
                        self.tableWidget.setItem(row_num, col_num, item)

        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при работе с базой данных: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {e}')

    def on_btn_edit_click(self):
        #self.window1.show()
        selected_row = self.tableWidget.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return

        data = []
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(selected_row, col)
            data.append(item.text() if item else '')

        self.window1.open_for_edit(data)

        def on_btn_delete_click(self):
            selected_row = self.tableWidget.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
                return

            # Получаем ID из первого столбца выбранной строки
            item = self.tableWidget.item(selected_row, 0)
            if not item:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось получить ID записи')
                return

            record_id = int(item.text())

            # Подтверждение действия
            reply = QMessageBox.question(
                self,
                'Подтверждение',
                'Вы действительно хотите удалить эту запись?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    with sqlite3.connect('./data/coffe.sqlite') as conn:
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM coffe WHERE id = ?', (record_id,))
                        conn.commit()

                    # Обновляем таблицу
                    self.load_database()
                    QMessageBox.information(self, 'Успех', 'Запись успешно удалена')

                except sqlite3.Error as e:
                    QMessageBox.critical(self, 'Ошибка', f'Ошибка базы данных: {str(e)}')
                except Exception as e:
                    QMessageBox.critical(self, 'Ошибка', f'Непредвиденная ошибка: {str(e)}')

    def on_btn_remove_click(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
            return

        item = self.tableWidget.item(selected_row, 0)
        if not item:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось получить ID записи')
            return

        record_id = int(item.text())

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы действительно хотите удалить эту запись?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with sqlite3.connect('./data/coffe.sqlite') as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM coffe WHERE id = ?', (record_id,))
                    conn.commit()

                self.load_database()
                QMessageBox.information(self, 'Выполнение операции', 'Запись успешно удалена')

            except sqlite3.Error as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка базы данных: {str(e)}')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Непредвиденная ошибка: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Shaobicoffee()
    window.show()
    sys.exit(app.exec())