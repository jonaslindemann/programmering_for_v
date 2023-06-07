# -*- coding: utf-8 -*-

import flowmodel as fm

import calfem.vis_mpl as cfv
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import cm

import win32com.client as win32

def export_to_excel(filename, max_flow):
    """Exportera max_flow array till Excel"""

    try:
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True

        workbook = excel.Workbooks.Add()

        worksheet = workbook.Sheets(1)

        num_rows = max_flow.shape[0]
        num_cols = max_flow.shape[1]

        for i in range(num_rows):
            for j in range(num_cols):
                worksheet.Cells(i + 1, j + 1).Value = max_flow[i][j]

        workbook.SaveAs(filename)
        workbook.Close(False)

    finally:
        excel.Quit()

def plot_param_surface(d, t, max_flow):
    """Plotta maxflow med Matplotlib"""
    
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    surf = ax.plot_surface(d, t, max_flow, cmap=cm.coolwarm,
                       linewidth=0, antialiased=True)

    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()



if __name__ == "__main__":

    # --- Skapa objekt för parametrar och resultat.

    model_params = fm.ModelParams()
    model_results = fm.ModelResults()

    # --- Skapa en lösare för vårt problem och koppla
    #     parametrar och resultat till objektet.

    model_solver = fm.ModelSolver(model_params, model_results)

    # --- Definiera arrayer för våra parametrar

    d_range = np.linspace(0.2, 8.0, 2)
    t_range = np.linspace(0.2, 10.0, 2)

    d, t = np.meshgrid(d_range, t_range)

    max_flow = np.zeros((len(d_range),len(t_range)))

    # --- Använd lösaren för att beräkna alla kombinationer
    #     av parametrarna d och t.

    for i in range(len(d_range)):
        for j in range(len(t_range)):

            model_params.t = t[i, j]
            model_params.d = d[i, j]

            model_solver.execute()

            max_flow[i, j] = np.max(model_results.evm)

    # --- Plotta maxflöden i ett ytdiagram.

    plot_param_surface()

    # --- Överföra värden till Excel.

    export_to_excel(r"D:\Users\Jonas\Development\vsmn20_solutions\param_example\test.xlsx", max_flow)




