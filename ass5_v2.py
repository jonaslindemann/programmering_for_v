# -*- coding: utf-8 -*-
"""Main module for the groundwater flow application"""

import sys

from qtpy.QtCore import QThread, Qt
from qtpy.QtWidgets import QApplication, QMainWindow, QFileDialog
from qtpy import uic

import gw_resources

import flowmodel as fm


class SolverThread(QThread):
    """Klass för att hantera beräkning i bakgrunden"""

    def __init__(self, solver, param_study=False):
        """Klasskonstruktor"""
        QThread.__init__(self)
        self.param_study = param_study
        self.solver = solver

    def __del__(self):
        self.wait()

    def run(self):
        """Thread method for running simulation."""
        if self.param_study:
            self.solver.execute_param_study()
        else:
            self.solver.execute()


class MainWindow(QMainWindow):
    """MainWindow-klass som hanterar vårt huvudfönster"""

    def __init__(self, app):
        """Class constructor"""

        super().__init__()

        # --- Lagra en referens till applikationsinstansen i klassen

        self.app = app

        # --- Läs in gränssnitt från fil

        uic.loadUi("mainwindow_v2.ui", self)

        # --- Koppla kontroller till händelsemetoder

        self.new_action.triggered.connect(self.on_new_action)
        self.open_action.triggered.connect(self.on_open_action)
        self.save_action.triggered.connect(self.on_save_action)
        self.save_as_action.triggered.connect(self.on_save_as_action)
        self.execute_action.triggered.connect(self.on_execute_action)
        self.exit_action.triggered.connect(self.on_exit_action)
        self.exec_param_study_action.triggered.connect(
            self.on_execute_param_study_action
        )

        self.el_size_slider.valueChanged.connect(self.on_el_size_changed)

        # --- Se till att visa fönstret

        self.show()
        self.raise_()

        # --- Se till att vi har en initierad modell

        self.vis = None

        self.init_model()

        self.update_controls()
        self.update_status()

    def init_model(self):
        """Initiera modellen"""

        self.filename = ""
        self.calc_done = False

        if self.vis is not None:
            self.vis.close_all()

        self.model_params = fm.ModelParams()
        self.model_results = fm.ModelResults()
        self.solver = fm.ModelSolver(self.model_params, self.model_results)

        self.report = None

        self.report_edit.clear()

        self.vis = fm.ModelVisualisation(self.model_params, self.model_results)

    def update_controls(self):
        """Fyll kontrollerna med värden från modellen"""

        self.w_edit.setText(str(self.model_params.w))
        self.h_edit.setText(str(self.model_params.h))
        self.d_edit.setText(str(self.model_params.d))
        self.t_edit.setText(str(self.model_params.t))
        self.kx_edit.setText(str(self.model_params.kx))
        self.ky_edit.setText(str(self.model_params.ky))
        self.el_size_slider.setValue(int(self.model_params.el_size_factor*100))
        self.el_size_value_label.setText(str(self.model_params.el_size_factor))
        self.d_end_edit.setText(str(self.model_params.t_end))
        self.t_end_edit.setText(str(self.model_params.d_end))

    def update_model(self):
        """Hämta värden från kontroller och uppdatera modellen"""

        self.model_params.w = float(self.w_edit.text())
        self.model_params.h = float(self.h_edit.text())
        self.model_params.d = float(self.d_edit.text())
        self.model_params.t = float(self.t_edit.text())
        self.model_params.kx = float(self.kx_edit.text())
        self.model_params.ky = float(self.ky_edit.text())
        self.model_params.d_end = float(self.d_end_edit.text())
        self.model_params.t_end = float(self.t_end_edit.text())

        self.update_controls()

    def update_status(self):
        """Sätt filnamn och uppdatera statusrad"""

        if self.filename == "":
            self.statusbar.showMessage("Modell: Ny modell")
        else:
            self.statusbar.showMessage("Modell: %s" % self.filename)

    def create_result_tabs(self):
        """Skapa result tabbar"""

        self.main_tabs.addTab(
            self.vis.show_geometry(no_show=True), "Geometry"
        )
        self.main_tabs.addTab(
            self.vis.show_mesh(no_show=True), "Mesh"
        )
        self.main_tabs.addTab(
            self.vis.show_nodal_values(no_show=True), "Nodal values"
        )
        self.main_tabs.addTab(
            self.vis.show_element_values(no_show=True), "Element values"
        )

    def remove_result_tabs(self):
        """Ta bort resultat tabbar"""

        if self.main_tabs.count() > 1:
            for i in range(4):
                self.main_tabs.removeTab(i+1)

    def on_new_action(self):
        """Skapa en ny modell"""

        self.init_model()
        self.update_controls()
        self.update_status()
        self.remove_result_tabs()

    def on_open_action(self):
        """Öppna in indata fil"""

        self.filename, _ = QFileDialog.getOpenFileName(
            self, "Öppna modell", "", "Modell filer (*.json *.jpg *.bmp)")

        if self.filename != "":
            self.init_model()
            self.model_params.load(self.filename)
            self.update_controls()
            self.update_status()
            self.remove_result_tabs()

    def on_save_action(self):
        """Spara modell"""

        self.update_model()

        if self.filename == "":
            self.filename, _ = QFileDialog.getSaveFileName(
                self, "Spara modell", "", "Modell filer (*.json)")

        if self.filename != "":
            self.model_params.save(self.filename)

        self.update_status()

    def on_save_as_action(self):
        """Spara modell med specifikt filnamn"""

        self.update_model()

        new_filename, _ = QFileDialog.getSaveFileName(
            self, "Spara modell", "", "Modell filer (*.json)")

        if new_filename != "":
            self.filename = new_filename
            self.model_params.save(self.filename)
            self.update_status()

    def on_execute_action(self):
        """Kör beräkningen"""

        # --- Stäng alla visualiseringsfönster

        self.vis.close_all()
        self.remove_result_tabs()

        # --- Avaktivera gränssnitt under beräkningen.

        self.setEnabled(False)

        # --- Uppdatera värden från kontroller

        self.update_model()

        # --- Skapa en lösare

        self.solver = fm.ModelSolver(self.model_params, self.model_results)

        # --- Starta en tråd för att köra beräkningen, så att
        #     gränssnittet inte fryser.

        solver_thread = SolverThread(self.solver)
        solver_thread.finished.connect(self.on_solver_finished)
        solver_thread.start()

    def on_solver_finished(self):
        """Anropas när beräkningstråden avslutas"""

        # --- Aktivera gränssnitt igen

        self.setEnabled(True)

        # --- Generera resulatrapport.

        self.report = fm.ModelReport(self.model_params, self.model_results)
        self.report_edit.setPlainText(str(self.report))

        self.calc_done = True

        # --- Skapa tabbar för resultatdiagram

        self.create_result_tabs()

    def on_exit_action(self):
        """Avsluta programmetin"""

        # --- Stäng alla visualiseringsfönster

        self.vis.close_all()

        # --- Stäng programfönster

        self.close()

    def on_el_size_changed(self, value):
        """Händelsemetod som anropas när skjutreglaget ändras"""

        self.model_params.el_size_factor = value/100.0
        self.el_size_value_label.setText(str(self.model_params.el_size_factor))

    def on_execute_param_study_action(self):
        """Exekvera parameterstudie"""

        print("onExecuteparam_study")

        self.model_params.param_d = self.param_vary_d_radio.isChecked()
        self.model_params.param_t = self.param_vary_t_radio.isChecked()

        if self.model_params.param_d:
            self.model_params.d_start = float(self.d_edit.text())
            self.model_params.d_end = float(self.d_end_edit.text())
        elif self.model_params.param_t:
            self.model_params.t_start = float(self.t_edit.text())
            self.model_params.t_end = float(self.t_end_edit.text())

        self.model_params.param_filename = "param_study"
        self.model_params.param_steps = int(self.param_step.value())

        # --- Stäng alla visualiseringsfönster

        self.vis.close_all()

        # --- Avaktivera gränssnitt under beräkningen.

        self.setEnabled(False)

        # --- Uppdatera värden från kontroller

        self.update_model()

        # --- Starta en tråd för att köra beräkningen, så att
        #     gränssnittet inte fryser.

        solver_thread = SolverThread(self.solver, param_study=True)
        solver_thread.finished.connect(self.on_solver_finished)
        solver_thread.start()


if __name__ == '__main__':

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    window = MainWindow(app)

    sys.exit(app.exec_())
