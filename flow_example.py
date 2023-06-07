# -*- coding: utf-8 -*-

import flowmodel as fm

import numpy as np
import pandas as pd

if __name__ == "__main__":

    model_params = fm.ModelParams()
    model_results = fm.ModelResults()

    model_solver = fm.ModelSolver(model_params, model_results)
    model_solver.execute()

    model_export = fm.ModelExport(model_params, model_results)
    
    parameters = model_export.parameters
    bcs = model_export.bounday_conds
    result_summary = model_export.result_summary
    node_results = model_export.node_results
    element_results = model_export.element_results

    with pd.ExcelWriter('output.xlsx') as writer:  
        parameters.to_excel(writer, sheet_name='Parameters')
        bcs.to_excel(writer, sheet_name='BCs')
        result_summary.to_excel(writer, sheet_name='Summary')
        node_results.to_excel(writer, sheet_name='Nodes')
        element_results.to_excel(writer, sheet_name='Elements')




