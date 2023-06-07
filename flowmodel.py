# -*- coding: utf-8 -*-

import json, math, sys

import calfem.core as cfc
import calfem.geometry as cfg
import calfem.mesh as cfm
import calfem.vis_mpl as cfv
import calfem.utils as cfu

import numpy as np
import tabulate as tbl
import pandas as pd

import pyvtk as vtk


class ModelParams:
    """Class to define our inputdata/model parameters."""

    def __init__(self):
        """InputData class constructor."""
        self.version = 3

        self.w = 100.0
        self.h = 10.0
        self.d = 5.0
        self.t = 0.5

        self.param_d = True
        self.d_start = self.d
        self.d_end = self.d + 2.0

        self.param_t = False
        self.t_start = self.t
        self.t_end = self.t + 1.0

        self.param_filename = "param"
        self.param_steps = 10

        self.kx = 20
        self.ky = 20
        self.th = 1.0

        self.ep = [self.th, 1]         #thickness/ir
        self.el_size_factor = 2
        self.el_type = 2

        # --- Boundary conditions
        self.bcs = [
            [10, 10.0],
            [20, 0.0],
        ]


    def geometry(self):
        """Skapa en geometri instans baserat på definierade parametrar"""

        g = cfg.Geometry()

        w = self.w
        h = self.h
        d = self.d
        t = self.t

        #Points
        g.point([0., 0.])     # 0
        g.point([w, 0.])      # 1
        g.point([w, h])       # 2
        g.point([(w+t)/2, h])        # 3
        g.point([(w+t)/2, (h-d)])    # 4
        g.point([(w-t)/2, (h-d)])    # 5
        g.point([(w-t)/2, h])        # 6
        g.point([0., h])             # 7

        
        #Splines
        g.spline([0, 1])             # 0
        g.spline([1, 2])             # 1
        g.spline([2, 3], marker=20)  # 2
        g.spline([3, 4])             # 3
        g.spline([4, 5])             # 4
        g.spline([5, 6])             # 5
        g.spline([6, 7], marker=10)  # 6
        g.spline([7, 0])             # 7


        #Surface
        g.surface([0, 1, 2, 3, 4, 5, 6, 7])

        return g

    def save(self, filename):
        """Spara indata till fil."""
        input_data = {}
        input_data["version"] = self.version
        input_data["w"] = self.w
        input_data["h"] = self.h
        input_data["d"] = self.d
        input_data["t"] = self.t

        input_data["ep"] = self.ep
        input_data["kx"] = self.kx
        input_data["ky"] = self.ky
        input_data["th"] = self.th

        input_data["bcs"] = self.bcs

        input_data["el_size_factor"] = self.el_size_factor
        input_data["el_type"] = self.el_type

        ofile = open(filename, "w")
        json.dump(input_data, ofile, sort_keys=True, indent=4)
        ofile.close()

    def load(self, filename):
        """Läs indata från fil."""

        ifile = open(filename, "r")
        input_data = json.load(ifile)
        ifile.close()

        self.version = input_data["version"]
        self.w = input_data["w"]
        self.a = input_data["t"]
        self.h = input_data["h"]
        self.b = input_data["d"]

        self.ep = input_data["ep"]
        self.kx = input_data["kx"]
        self.ky = input_data["ky"]
        self.v = input_data["th"]

        self.bcs = input_data["bcs"]

        self.el_size_factor = input_data["el_size_factor"]
        self.el_type = input_data["el_type"]

class ModelResults:
    """Klass för att lagra resultaten från körningen."""

    def __init__(self):
        self.geometry = None
        self.coords = None
        self.edof = None
        self.dofs = None
        self.dofs_per_node = None

        self.a = None
        self.r = None
        self.ex = None
        self.ey = None
        self.ed = None
        self.es = None
        self.et = None
        self.evm = None


class ModelSolver:
    """Klass för att hantera lösningen av vår beräkningsmodell."""

    def __init__(self, model_params, model_results):
        self.model_params = model_params
        self.model_results = model_results

        self.el_func_qe_e = cfc.flw2i4e
        self.el_func_qe_s = cfc.flw2i4s
        
        self.el_func_te_e = cfc.flw2te
        self.el_func_te_s = cfc.flw2ts

    def execute(self):
        """Metod för att utföra finita element beräkningen."""

        # --- Loacal references of model parameters
        ep = self.model_params.ep
        kx = self.model_params.kx
        ky = self.model_params.ky
        bcs = self.model_params.bcs
        el_size_factor = self.model_params.el_size_factor
        el_type = self.model_params.el_type

        # --- Create mesh
        dofs_per_node = 1
        geometry = self.model_params.geometry()
        mesh = cfm.GmshMeshGenerator(geometry)

        mesh.el_size_factor = el_size_factor
        mesh.el_type = el_type
        mesh.dofs_per_node = dofs_per_node
        mesh.return_boundary_elements = True

        coords, edof, dofs, bdofs, elementmarkers, boundaryElements = mesh.create()

        # --- Beräkna element koordinater
        ex, ey = cfc.coordxtr(edof, coords, dofs)
        n_dofs = edof.max()
        nEl = edof.shape[0]

        # --- Beräkna D-matris

        D = np.array([[kx, 0],
                      [0, ky]])

        # --- Assemblera systemmatris


        K = np.zeros([n_dofs, n_dofs])

        for etopo, eex, eey in zip(edof, ex, ey):
            if el_type == 3:
                Ke = self.el_func_qe_e(eex, eey, ep, D)
            elif el_type == 2:
                Ke = self.el_func_te_e(eex, eey, [ep[0]], D)

            cfc.assem(etopo, K, Ke)

        # --- Lösning av ekvationssystem

        f = np.zeros([n_dofs, 1])
        bc_prescr = np.array([], int)
        bc_val = np.array([], float)

        for bc in bcs:
            bc_prescr, bc_val = cfu.applybc(
                bdofs, bc_prescr, bc_val, bc[0], bc[1]
            )

        a, r = cfc.solveq(K, f, bc_prescr, bc_val)

        # --- Beräkna elementkrafter

        ed = cfc.extract_eldisp(edof, a)

        es = np.zeros([nEl,2])
        et = np.zeros([nEl,2])
        evm = np.zeros([nEl,1])

        for eex, eey, eed, ees, eet, eevm in zip(ex, ey, ed, es, et, evm):
            if el_type == 3:
                ies, iet, eci = self.el_func_qe_s(eex, eey, ep, D, eed)
                ees[:] = ies[:]
                eet[:] = iet[:]
                eevm[:] = math.sqrt(ies[0,1]**2 + ies[0,1]**2)
            elif el_type == 2:
                ies, iet = self.el_func_te_s(eex, eey, D, eed)
                ees[:] = ies[0,:]
                eet[:] = iet[0,:]
                eevm[:] = math.sqrt(ies[0,0]**2 + ies[0,1]**2)
            

        self.model_results.geometry = geometry
        self.model_results.coords = coords
        self.model_results.edof = edof
        self.model_results.dofs = dofs
        self.model_results.bdofs = bdofs
        self.model_results.dofs_per_node = dofs_per_node
        self.model_results.el_type = el_type

        self.model_results.a = a
        self.model_results.r = r
        self.model_results.ex = ex
        self.model_results.ey = ey
        self.model_results.ed = ed
        self.model_results.es = es
        self.model_results.et = et
        self.model_results.evm = evm

    def execute_param_study(self):
        """Kör parameter studie"""

        old_d = self.model_params.d
        old_t = self.model_params.t

        i = 1

        if self.model_params.param_d:
            d_range = np.linspace(
                self.model_params.d,
                self.model_params.d_end,
                self.model_params.param_steps
            )
            for d in d_range:
                print("Executing for d = %g..." % d)
                self.model_params.d = d
                self.execute()
                self.export_vtk(
                    "%s_%02d.vtk" % (self.model_params.param_filename, i)
                )
                i += 1
        elif self.model_params.param_t:
            t_range = np.linspace(
                self.model_params.t,
                self.model_params.t_end,
                self.model_params.param_steps
            )

            for t in t_range:
                print("Executing for t = %g..." % t)
                self.model_params.t = t
                self.execute()
                self.export_vtk(
                    "%s_%02d.vtk" % (self.model_params.param_filename, i)
                )
                i += 1

        self.model_params.d = old_d
        self.model_params.t = old_t

    def export_vtk(self, filename):
        """Export results to VTK"""

        print("Exporting results to %s." % filename)

        # --- Extract points and polygons

        points = self.model_results.coords.tolist()
        polygons = (self.model_results.edof-1).tolist()

        # --- Create point data from a

        point_data = vtk.PointData(
            vtk.Scalars(self.model_results.a.tolist(), name="pressure")
        )

        # --- Create cell data from max_flow and flow

        cell_data = vtk.CellData(
            vtk.Scalars(self.model_results.max_flow, name="max_flow"),
            vtk.Vectors(self.model_results.flow, "flow")
        )

        # --- Create structure

        structure = vtk.PolyData(points=points, polygons=polygons)

        # --- Export to vtk

        vtk_data = vtk.VtkData(structure, point_data, cell_data)
        vtk_data.tofile(filename, "ascii")

class ModelExport:
    def __init__(self, model_params, model_results):
        self.model_params = model_params
        self.model_results = model_results

    @property
    def parameters(self):

        parameters = ["w [m]","h [m]", "d [m]","t [m]","thickness [m]","kx [m/day]","ky [m/day]"]
        values = [
            self.model_params.w, 
            self.model_params.h, 
            self.model_params.d,
            self.model_params.t,
            self.model_params.th,
            self.model_params.kx,
            self.model_params.ky
            ]

        return pd.DataFrame({"Parameter": parameters, "Values": values})
   
    @property
    def bounday_conds(self):

        markers = []
        values = []

        for marker, value in self.model_params.bcs:
            markers.append(marker)
            values.append(value)


        return pd.DataFrame({"Marker":markers, "Piezometric head":values})
    
    @property
    def result_summary(self):

        descriptions = [
            "Max piezometric head:",
            "Min piezometric head:",
            "Max boundary flow:",
            "Min boundary flow:",
            "Sum boundary flow:",
            "Max resulting gw flow:",
            "Min resulting gw flow:"
        ]

        values = [
            np.max(self.model_results.a),
            np.min(self.model_results.a),
            np.max(self.model_results.r),
            np.min(self.model_results.r),
            np.sum(self.model_results.r),
            np.max(self.model_results.evm),
            np.min(self.model_results.evm)
        ]

        units = [
            "[m]",
            "[m]",
            "[m/day]",
            "[m/day]",
            "[m/day]",
            "[m/day]",
            "[m/day]"
        ]

        return pd.DataFrame({"Description": descriptions, "Value":values, "Unit":units})
        
    
    @property
    def node_results(self):

        a = self.model_results.a
        r = self.model_results.r

        node_info = np.asarray(
            np.hstack( 
                (self.model_results.dofs, self.model_results.coords, a, r)
                )
            )
        
        df = pd.DataFrame(node_info, columns=["dof", "x_coord [m]"," y_coord [m]", "P.h. [m]","q BC [m/day]"])

        df["dof"] = df["dof"].astype(int)
        return df
    
    @property
    def element_results(self):

        edof = self.model_results.edof
        dofs = self.model_results.dofs
        coords = self.model_results.coords
        a = self.model_results.a
        r = self.model_results.r
        n_dofs = edof.max()
        nNodes = coords.shape[0]
        nEl = edof.shape[0]

        el_info = np.asarray(np.hstack( 
                (edof, self.model_results.es, self.model_results.evm,self.model_results.et)
                ))
        
        h2 = ["N1", "N2", "N3","N4",'qx [m/day]','qy [m/day]','q_res [m/day]','grad [-]','grad [-]']
        
        if self.model_params.el_type == 2:
            h2 = ["N1", "N2", "N3",'qx [m/day]','qy [m/day]','q_res [m/day]','grad [-]','grad [-]']

        df = pd.DataFrame(el_info, columns = h2)
        df["N1"] = df["N1"].astype(int)
        df["N2"] = df["N2"].astype(int)
        df["N3"] = df["N3"].astype(int)
        if self.model_params.el_type != 2:
            df["N4"] = df["N4"].astype(int)

        return df



class ModelReport:
    """Class to present model parameters and model result"""

    def __init__(self, model_params, model_results):
        self.model_params = model_params
        self.model_results = model_results
        self.table_format = "psql"
        self.report = ""

    def clear(self):
        self.report = ""

    def add_text(self, text=""):
        self.report += str(text)+"\n"

    def __str__(self):

        edof = self.model_results.edof
        dofs = self.model_results.dofs
        coords = self.model_results.coords
        a = self.model_results.a
        r = self.model_results.r
        n_dofs = edof.max()
        nNodes = coords.shape[0]
        nEl = edof.shape[0]

        np.set_printoptions(
            formatter={'float': '{: 10.3f}'.format}, threshold=sys.maxsize
        )

        self.clear()
        self.add_text()
        self.add_text(
            "-------------------------------------------------------------")
        self.add_text(
            "-------------- Model input ----------------------------------")
        self.add_text(
            "-------------------------------------------------------------")
        self.add_text()
        self.add_text("Model parameters:")
        self.add_text()

        parameters = [
            ["w [m]", self.model_params.w],
            ["h [m]", self.model_params.h],
            ["d [m]", self.model_params.d],
            ["t [m]", self.model_params.t],
            ["thickness [m]", self.model_params.th],
            ["kx [m/day]", self.model_params.kx],
            ["ky [m/day]", self.model_params.ky],
        ]

        self.add_text(
            tbl.tabulate(
                parameters,
                headers=["Parameter", "Value"],
                numalign="right",
                floatfmt=".4g",
                tablefmt=self.table_format,
            )
        )

        # --- Boundary conditions

        self.add_text()
        self.add_text("Model boundary conditions:")
        self.add_text()
        self.add_text(
            tbl.tabulate(
                self.model_params.bcs,
                headers=["Marker", "Piezometric head"],
                numalign="right",
                tablefmt=self.table_format,
            )
        )


        self.add_text()
        self.add_text(
            "-------------------------------------------------------------")
        self.add_text(
            "-------------- Results --------------------------------------")
        self.add_text(
            "-------------------------------------------------------------")
        
        #----------Model info:---------------------------------------------------

        mod_info = [
            ["Max element size:", self.model_params.el_size_factor],
            ["Dofs per node:", self.model_results.dofs_per_node],
            ["Element type:", self.model_params.el_type],
            ["Number of dofs:", n_dofs],
            ["Number of elements:", nEl],
            ["Number of nodes:", nNodes],
        ]

        self.add_text()
        self.add_text("Model info:")
        self.add_text()
        self.add_text(
            tbl.tabulate(
                mod_info,
                numalign="right",
                tablefmt=self.table_format,
            )
        ) 

        
        #------- SUmmary results--------------------------------------------------------------------------------

        short_res = [
        ["Max piezometric head:",np.max(self.model_results.a),"[m]"],
        ["Min piezometric head:",np.min(self.model_results.a),"[m]"],
        ["Max boundary flow:",np.max(self.model_results.r),"[m/day]"],
        ["Min boundary flow:",np.min(self.model_results.r),"[m/day]"],
        ["Sum boundary flow:",np.sum(self.model_results.r),"[m/day]"],
        ["Max resulting gw flow:",np.max(self.model_results.evm),"[m/day]"],
        ["Min resulting gw flow:",np.min(self.model_results.evm),"[m/day]"],
        
        ]

        self.add_text()
        self.add_text("Summary of results:")
        self.add_text()
        self.add_text(
            tbl.tabulate(
                short_res,
                numalign="right",
                tablefmt=self.table_format,
                floatfmt=".3f"
            )
        ) 
        
        #------- Per node--------------------------------------------------------------------------------
        self.add_text()
        self.add_text("Results per node:")
        self.add_text()

        node_info = np.asarray(np.hstack( 
                (self.model_results.dofs, self.model_results.coords, a, r)
                ))

        self.add_text(
            tbl.tabulate(
                node_info,
                headers=["N", "dof", "x_coord\n[m]"," y_coord\n[m]", "P.h.\n[m]","q BC\n[m/day]"],
                numalign="right",
                floatfmt= (".0f", ".0f",".1f",".1f",".3f",".3f"),
                tablefmt=self.table_format,
                showindex=range(1, len(node_info) + 1)
            )
        )

        #------- Per element-------------------------------------------------------

        el_info = np.asarray(np.hstack( 
                (edof, self.model_results.es, self.model_results.evm,self.model_results.et)
                ))
        
        h2 = ["El\nNb", "N\n1", "N\n2", "N\n3","N\n4",'qx\n[m/day]','qy\n[m/day]','q_res\n[m/day]','grad\n[-]','grad\n[-]']
        fm2 =  [".0f", ".0f",".0f",".0f",".0f",".3f",".3f",".3f",".3f",".3f"]
        
        if self.model_params.el_type == 2:
            h2 = ["El\nNb", "N\n1", "N\n2", "N\n3",'qx\n[]','qy\n[m/day]','q_res\n[m/day]','grad_x\n[-]','grad_y\n[-]']
            fm2 = [".0f", ".0f",".0f",".0f",".3f",".3f",".3f",".3f",".3f"]


        self.add_text()
        self.add_text("Results per element:")
        self.add_text()
        self.add_text(
            tbl.tabulate(
                el_info,
                headers=h2,
                numalign="right",
                floatfmt= fm2,
                tablefmt=self.table_format,
                showindex=range(1, len(el_info) + 1)
            )
        )

        return self.report


class ModelVisualisation:
    """Klass för visualisering av resulat"""

    def __init__(self, input_data, output_data):
        """Konstruktor"""

        self.model_params = input_data
        self.model_results = output_data

        self.geom_fig = None
        self.mesh_fig = None
        self.el_value_fig = None
        self.node_value_fig = None

        self.geom_widget = None
        self.mesh_widget = None
        self.el_value_widget = None
        self.node_value_widget = None

    def show(self):
        """Visa alla visualiseringsfönster"""
        geometry = self.model_results.geometry
        a = self.model_results.a
        max_flow = self.model_results.max_flow
        coords = self.model_results.coords
        edof = self.model_results.edof
        dofs_per_node = self.model_results.dofs_per_node
        el_type = self.model_results.el_type

        cfv.figure()
        cfv.draw_geometry(geometry, title="Geometry")

        cfv.figure()
        cfv.draw_element_values(max_flow, coords, edof, dofs_per_node, el_type,
                                None, draw_elements=False, title="Max flows")

        cfv.figure()
        cfv.draw_mesh(coords, edof, dofs_per_node, el_type, filled=True,
                      title="Mesh")

        cfv.figure()
        cfv.draw_nodal_values(a, coords, edof, el_type=el_type,
                              draw_elements=False, title="Nodal values")

        cfv.colorbar()

    def close_all(self):
        """Stäng alla visualiseringsfönster"""

        cfv.closeAll()

        self.geom_fig = None
        self.mesh_fig = None
        self.el_value_fig = None
        self.node_value_fig = None

        if self.geom_widget is not None:
            self.geom_widget.close()
        if self.mesh_widget is not None:
            self.mesh_widget.close()
        if self.el_value_widget is not None:
            self.el_value_widget.close()
        if self.node_value_widget is not None:
            self.node_value_widget.close()

    def show_geometry(self, no_show=False):
        """Visa geometri visualisering"""

        geometry = self.model_params.geometry()

        self.geom_fig = cfv.figure(self.geom_fig)

        if self.geom_widget is None:
            self.geom_widget = cfv.figure_widget(self.geom_fig)

        cfv.clf()
        cfv.draw_geometry(geometry, title="Geometry")

        if no_show:
            return self.geom_widget
        
        cfv.show()

        return None

    def show_mesh(self, no_show=False):
        """Visa nät visualisering"""

        coords = self.model_results.coords
        edof = self.model_results.edof
        dofs_per_node = self.model_results.dofs_per_node
        el_type = self.model_results.el_type

        self.mesh_fig = cfv.figure(self.mesh_fig)

        if self.mesh_widget is None:
            self.mesh_widget = cfv.figure_widget(self.mesh_fig)

        cfv.clf()
        cfv.draw_mesh(coords, edof, dofs_per_node, el_type, filled=True,
                      title="Mesh")

        if no_show:
            return self.mesh_widget
        
        cfv.show()

        return None

    def show_nodal_values(self, no_show=False):
        """Visa nodvärden"""

        a = self.model_results.a
        coords = self.model_results.coords
        edof = self.model_results.edof
        dofs_per_node = self.model_results.dofs_per_node
        el_type = self.model_results.el_type

        self.node_value_fig = cfv.figure(self.node_value_fig)

        if self.node_value_widget is None:
            self.node_value_widget = cfv.figure_widget(self.node_value_fig)

        cfv.clf()
        cfv.draw_nodal_values(a, coords, edof, dofs_per_node=dofs_per_node,
                              el_type=el_type, draw_elements=False,
                              title="Nodal values")

        if no_show:
            return self.node_value_widget
        
        cfv.show()

        return None

    def show_element_values(self, no_show=False):
        """Visa elementvärden"""

        evm = self.model_results.evm
        coords = self.model_results.coords
        edof = self.model_results.edof
        dofs_per_node = self.model_results.dofs_per_node
        el_type = self.model_results.el_type

        self.el_value_fig = cfv.figure(self.el_value_fig)

        if self.el_value_widget is None:
            self.el_value_widget = cfv.figure_widget(self.el_value_fig)

        cfv.clf()
        cfv.draw_element_values(np.reshape(evm, (evm.shape[0],)), coords, edof, dofs_per_node,  
                                el_type, None, draw_elements=False, title="Max flows")

        if no_show:
           return self.el_value_widget
        
        cfv.colorbar()
        cfv.show()

        return None

    def show_and_wait(self):
        cfv.show_and_wait()

if __name__ == "__main__":

    model_params = ModelParams()

    model_params.el_size_factor = 2
    model_params.el_type = 2

    model_params.kx = 20
    model_params.ky = 20
    model_params.th = 1

    model_results = ModelResults()
    model_solver = ModelSolver(model_params, model_results)

    model_solver.execute()

    model_report = ModelReport(model_params, model_results)
    model_report.table_format = "psql"
    print(model_report)

    with open('flowmodel_v3.txt','w') as f:
        f.write(str(model_report))

    # model_vis = ModelVisualisation(model_params, model_results)
    # model_vis.show()
    # model_vis.show_and_wait()