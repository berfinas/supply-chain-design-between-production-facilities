import json
import os
import random
import sys

from PyQt5.QtCore import Qt, QRegExp, QTimer
from PyQt5.QtGui import QPixmap, QRegExpValidator, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, \
    QLineEdit, QWidget, QScrollArea, QComboBox, QGraphicsTextItem
from StartButtonThread import StartButtonThread
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QAbstractBarSeries
from PyQt5.QtGui import QPainter


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item.widget() is not None:
            item.widget().setParent(None)
        elif item.layout() is not None:
            clear_layout(item.layout())
            layout.removeItem(item)


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.initUI()
        self.finished_flag = False

    def initUI(self):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo2.jpeg')
        bilkent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bilkent2.jpeg')

        self.setWindowTitle("Norm Civata Optimization")
        self.setGeometry(100, 100, 800, 600)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0
        # Ana layout
        main_layout = QHBoxLayout()

        # Sol panel (navbar)
        left_panel = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setFixedWidth(200)
        left_panel_widget.setLayout(left_panel)

        # Logo
        logo = QLabel()
        logo.setFixedWidth(200)
        logo.setFixedHeight(100)
        logo.setPixmap(QPixmap(logo_path).scaled(150, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(logo)

        # Navbar butonları
        self.btn_home = QPushButton("Ana Sayfa")
        self.btn_files = QPushButton("Dosyalar")
        self.btn_results = QPushButton("Sonuçlar")
        self.btn_graphs = QPushButton("Grafikler")
        self.btn_credits = QPushButton("Credits")


        # Buton işlevlerinin bağlantıları
        self.btn_home.clicked.connect(self.home_section)
        self.btn_files.clicked.connect(self.files_section)
        self.btn_results.clicked.connect(self.results_section)
        self.btn_graphs.clicked.connect(self.graphs_section)
        self.btn_credits.clicked.connect(self.credits_section)

        self.navbar_buttons = [
            self.btn_home,
            self.btn_files,
            self.btn_results,
            self.btn_graphs,
            self.btn_credits,
        ]

        for btn in self.navbar_buttons:
            btn.setFixedHeight(50)
            btn.setFixedWidth(200)
            left_panel.addWidget(btn)

        logo2 = QLabel()
        logo2.setFixedWidth(200)
        logo2.setFixedHeight(100)
        logo2.setPixmap(QPixmap(bilkent_path).scaled(150, 100, Qt.KeepAspectRatio))
        logo2.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(logo2)

        main_layout.addWidget(left_panel_widget)

        # Sağ panel (içerik)
        self.right_panel = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_contents = QWidget()
        scroll_area_contents.setLayout(self.right_panel)
        scroll_area.setWidget(scroll_area_contents)
        main_layout.addWidget(scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.home_section()

    def update_timer(self):
        self.time_elapsed += 1
        self.timer_label.setText(f"Time: {self.time_elapsed}s")

    def set_active_button(self, active_button):
        for btn in self.navbar_buttons:
            if btn == active_button:
                btn.setStyleSheet("background-color: #19A7CE;")
            else:
                btn.setStyleSheet("")

    def home_section(self):
        self.clear_right_panel()
        self.set_active_button(self.btn_home)
        label = QLabel("Hoşgeldiniz! Sol taraftaki menu ile işlemlerinizi gerçekleştirebilirsiniz.")
        self.right_panel.addWidget(label)

    def clear_right_panel(self):
        clear_layout(self.right_panel)

    def files_section(self):
        self.clear_right_panel()
        self.set_active_button(self.btn_files)

        label = QLabel("Gerekli excelleri buradan seçiniz:")
        self.right_panel.addWidget(label)

        excel_names = ["Talepler", "Ürünler", "Uzaklıklar", "Makineler", "Makineler2", "Araçlar"]

        self.file_labels = []

        for i, name in enumerate(excel_names):
            hbox = QHBoxLayout()
            label = QLabel(f"{name}:")
            hbox.addWidget(label)
            file_label = QLabel(self.data.get(f"Excel_{i + 1}", ""))
            hbox.addWidget(file_label)
            self.file_labels.append(file_label)
            btn_browse = QPushButton("Browse")
            btn_browse.clicked.connect(
                lambda _, index=i: self.browse_file(f"Excel_{index + 1}", self.file_labels[index]))
            hbox.addWidget(btn_browse)
            self.right_panel.addLayout(hbox)

        self.btn_start = QPushButton("Başlat")
        self.btn_start.setEnabled(False)  # Disable the button initially
        self.btn_start.clicked.connect(self.run_start_button)
        self.right_panel.addWidget(self.btn_start)
        # Timer label
        self.timer_label = QLabel()
        self.timer_label.setText(f"Süre: {self.time_elapsed}s")
        self.right_panel.addWidget(self.timer_label)

    def browse_file(self, key, label):
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)")
        if file_name:
            print(f"Seçilen dosya: {file_name}")
            file_basename = os.path.basename(file_name)
            label.setText(file_basename)
            self.data[key] = file_name
            self.check_files_selected()

    def check_files_selected(self):
        if all(f"Excel_{i + 1}" in self.data for i in range(5)):
            self.btn_start.setEnabled(True)
        else:
            self.btn_start.setEnabled(False)

    def run_start_button(self):
        demand_file_name = self.data.get("Excel_1")
        product_file_name = self.data.get("Excel_2")
        distance_file_name = self.data.get("Excel_3")
        machine_file_name = self.data.get("Excel_4")
        machine_file_name2 = self.data.get("Excel_5")
        vehicle_file_name = self.data.get("Excel_6")


        if demand_file_name and product_file_name and distance_file_name and machine_file_name:
            self.time_elapsed = 0
            self.timer.start(1000)
            self.btn_start.setEnabled(False)
            self.start_button_thread = StartButtonThread(demand_file_name, product_file_name, distance_file_name,
                                                         machine_file_name, machine_file_name2, vehicle_file_name ,'output.txt')
            self.start_button_thread.finished.connect(self.on_start_button_finished)
            self.start_button_thread.start()
        else:
            print("Dosyalar eksik!")

    def on_start_button_finished(self):
        self.timer.stop()
        self.finished_flag = True
        self.results_section()
        self.btn_start.setEnabled(True)

    def results_section(self):
        self.clear_right_panel()
        self.set_active_button(self.btn_results)

        # output.txt dosyasını açıp okuma
        if self.finished_flag:
            try:
                with open("output.txt", "r") as file:
                    content = file.read()
            except FileNotFoundError:
                content = "output.txt dosyası bulunamadı."
        else:
            content = "Hesaplamalar henüz tamamlanmadı."

        # Sonuçları QLabel ile gösterme
        label = QLabel(content)
        self.right_panel.addWidget(label)

    def credits_section(self):
        self.clear_right_panel()
        self.set_active_button(self.btn_credits)

        label = QLabel(" Hazal Albayrak\n Beyza Alkı̧s\n Berfin A̧s \n Hilal Aydın \n Ipek Bayram \n Mustafa Mert Eskicioğlu \n Umut Gubari \n\n Industrial Engineering \n Bilkent University \n 06800 Ankara")
        self.right_panel.addWidget(label)

    def graphs_section(self):
        self.clear_right_panel()
        self.set_active_button(self.btn_graphs)
        if self.finished_flag:
            # ChartView oluşturma
            chart_view = QChartView(self)
            chart_view.setRenderHint(QPainter.Antialiasing)
            # Verileri JSON dosyasından okuma
            with open('graph_data.json') as f:
                data = json.load(f)

            # Kategorileri (x ekseni) ve değerleri (y ekseni) ayırma
            categories = ["Tesis {}".format(i + 1) for i in range(7)]
            x_values = [d[:2] for d in data]
            y_values = [d[2] for d in data]

            # Veri seti oluşturma
            bar_set = QBarSet("Veri Seti")
            bar_set.append(y_values)

            # Veri serisi ve sütun grafiği oluşturma
            bar_series = QBarSeries()
            bar_series.append(bar_set)
            chart = QChart()
            chart.addSeries(bar_series)
            chart.setTitle("Sütun Grafiği")

            # Kategorileri (x ekseni) belirleme
            category_axis = QBarCategoryAxis()
            category_axis.append(categories)
            chart.addAxis(category_axis, Qt.AlignBottom)
            bar_series.attachAxis(category_axis)

            # Sayı değerlerini (y ekseni) belirleme
            value_axis = QValueAxis()
            value_axis.setRange(0, max(y_values))  # y ekseni aralığı
            chart.addAxis(value_axis, Qt.AlignLeft)
            bar_series.attachAxis(value_axis)

            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            chart_view.setChart(chart)

            self.right_panel.addWidget(chart_view)

            # Açılır menü (dropdown) oluşturma
            dropdown = QComboBox()
            dropdown.addItems(categories + ["Genel"])
            dropdown.currentIndexChanged.connect(self.update_graph)
            self.right_panel.addWidget(dropdown)

            # Çizimi güncelleme
            self.update_graph(0)
        else:
            label = QLabel("Hesaplamalar henüz tamamlanmadı.")
            self.right_panel.addWidget(label)

    def update_graph(self, index):
        # Açılır menüdeki (dropdown) seçeneğe göre grafik güncelleme
        selected_value = index + 1  # Seçilen değeri almak için index'e 1 ekliyoruz

        # Verileri JSON dosyasından okuma
        with open('graph_data.json') as f:
            data = json.load(f)

        # Kategorileri (x ekseni) ve değerleri (y ekseni) ayırma
        categories = ["Tesis {}".format(i + 1) for i in range(7)]

        x_values = [d[:2] for d in data]
        y_values = [d[2] for d in data]

        if selected_value == len(categories) + 1:
            # "Genel" seçildiğinde
            izmir_izmir = 0
            izmir_salihli = 0
            salihli_izmir = 0
            salihli_salihli = 0
            for i in (1,2,3,4):
                for j in (1,2,3,4):
                    total = sum([d[2] for d in data if d[0] == i and d[1] == j])
                    izmir_izmir += total

            for i in (1,2,3,4):
                for j in (5,6,7):
                    total = sum([d[2] for d in data if d[0] == i and d[1] == j])
                    izmir_salihli += total

            for i in (5,6,7):
                for j in (1,2,3,4):
                    total = sum([d[2] for d in data if d[0] == i and d[1] == j])
                    salihli_izmir += total

            for i in (5,6,7):
                for j in (5, 6, 7):
                    total = sum([d[2] for d in data if d[0] == i and d[1] == j])
                    salihli_salihli += total

            filtered_data = [izmir_izmir, izmir_salihli, salihli_izmir, salihli_salihli]
            categories = ["izmir-izmir", "izmir-salihli", "salihli-izmir", "salihli-salihli"]
            chart_title = "Genel"
        else:
            # Diğer tesisler için
            filtered_data = [d[2] for d in data if d[0] == selected_value or d[1] == selected_value]
            chart_title = "Tesis {}".format(selected_value)

        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(chart_title)

        # Kategorileri (x ekseni) belirleme
        category_axis = QBarCategoryAxis()
        category_axis.append(categories)
        chart.addAxis(category_axis, Qt.AlignBottom)

        # Sayı değerlerini (y ekseni) belirleme
        value_axis = QValueAxis()
        value_axis.setRange(0, max(filtered_data))  # y ekseni aralığı
        chart.addAxis(value_axis, Qt.AlignLeft)

        bar_set = QBarSet("Veri Seti")
        bar_set.append(filtered_data)

        bar_series = QBarSeries()
        bar_series.append(bar_set)
        bar_series.setLabelsVisible(True)
        bar_series.setLabelsPosition(QAbstractBarSeries.LabelsCenter)
        bar_series.setLabelsAngle(90)
        chart.addSeries(bar_series)

        bar_series.attachAxis(category_axis)
        bar_series.attachAxis(value_axis)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.right_panel.itemAt(0).widget().setChart(chart)
        bar_series.clicked.connect(self.show_details)

    def show_details(self, index, barset):
        if self.right_panel.itemAt(2) is not None:
            self.right_panel.itemAt(2).widget().deleteLater()
        label = QLabel("Değer: " + str(barset.at(index)))
        label.setAlignment(Qt.AlignCenter)
        self.right_panel.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = Ui_MainWindow()
    main_win.show()
    sys.exit(app.exec_())
