from PyQt5.QtCore import Qt, QRegExp, QTimer, QThread, pyqtSignal
from StartButton import start_button


class StartButtonThread(QThread):
    finished = pyqtSignal()

    def __init__(self, demand_file, product_file, distance_file, machine_file, machine_file2, vehicle_file, output_file):
        super().__init__()
        self.demand_file = demand_file
        self.product_file = product_file
        self.distance_file = distance_file
        self.machine_file = machine_file
        self.machine_file2 = machine_file2
        self.vehicle_file = vehicle_file
        self.output_file = output_file

    def run(self):
        start_button(self.demand_file, self.product_file, self.distance_file, self.machine_file, self.machine_file2, self.vehicle_file, self.output_file)
        self.finished.emit()
