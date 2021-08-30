# -*- coding: utf-8 -*-
import os, sys

from .DataBaseSqlite import DataBaseSqlite
from ..libraries.tabulate import tabulate

class ScenariosFiles():
    def __init__(self, project_file, statusBar=None):
        self.project_file = project_file
        self.tranus_folder = self.uri_segmentation(self.project_file)
        self.statusBar = statusBar
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)

    def uri_segmentation(self, project_file):
        project_file_arr = project_file.split("\\")
        return "/".join(project_file_arr[:len(project_file_arr)-1])

    def generate_single_scenario(self, id_scenario):
        self.generate_ctl_file()
        self.generate_l0e_file()
        self.generate_z1e_file()
        
        self.write_f1e_file(id_scenario)
        self.write_l1e_file(id_scenario)
        self.write_l2e_file(id_scenario)
        self.write_l3e_file(id_scenario)
        self.write_p0e_file(id_scenario)
        self.write_p1e_file(id_scenario)
        self.write_t1e_file(id_scenario)


    def generate_ctl_file(self):
        """
            @summary: Set Scenario selected
        """
        tabulate.PRESERVE_WHITESPACE = True
        header = self.dataBaseSqlite.selectAll(" project ")
        #scenarios = self.dataBaseSqlite.selectAll(" scenario ")
        scenarios = self.dataBaseSqlite.executeSql("select code, name, CASE cod_previous WHEN '' then ' ' else cod_previous end cod_previous from scenario")
        scenarios_header = ["'Code'", "'Name'", "'Prev'"]
        scenarios_data = [["'"+str(valor[0])+"'","'"+valor[1]+"'","'"+valor[2]+"'"] for valor in scenarios]

        # Study Area 
        study_header = ["'Code'","'Name'"]
        study_data = [["'"+str(header[0][1])+"'","'"+header[0][2]+"'"]]
        
        filename = "W_TRANUS.CTL"
        fh = None
        
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf-8")
            fh.write("STUDY and SCENARIO DEFINITION -- File W_TRANUS.CTL \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("1.0 STUDY AREA IDENTIFICATION \n")
            fh.write(tabulate(study_data, tablefmt='plain', headers=study_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SCENARIOS \n")
            fh.write(tabulate(scenarios_data, tablefmt='plain', headers=scenarios_header)+"\n")            
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 Model \n")
            fh.write("3.1 TRANS Use Logit model instead of Powit\n")
            fh.write("    1\n")
            fh.write("3.2 LOC Use Logit model instead of Powit \n")
            fh.write("    1\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def generate_z1e_file(self):
        """
            @summary: Set Scenario selected
        """
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}.Z1E".format(header[0][1])
        fh = None
        zones_first = self.dataBaseSqlite.selectAll(" zone ", columns=" id, name ", where=" where id > 0 and (external is null or external = 0) ", orderby=" order by 1 asc ")
        zones_external = self.dataBaseSqlite.selectAll(" zone ", columns=" id, name ", where=" where id > 0 and external = 1", orderby=" order by 1 asc ")
        zones_header = ["Zone", "'Name'"]
        zones_data = [[valor[0],"'"+str(valor[1])+"'"] for valor in zones_first]
        zones_data_ext = [[valor[0],"'"+str(valor[1])+"'"] for valor in zones_external]
        
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf-8")
            fh.write("ZONE DEFINITION - File Z1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 FIRST LEVEL ZONES \n")
            fh.write(tabulate(zones_data, tablefmt='plain', headers=zones_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SECOND LEVEL ZONES \n")
            fh.write("        Zone  SubZone 'Name'           SubZone 'Name'           SubZone 'Name'          ->/\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 EXTERNAL ZONES \n")
            fh.write(tabulate(zones_data_ext, tablefmt='plain', headers=zones_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            #self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def generate_l0e_file(self):
        """
            @summary: Set Scenario selected
        """
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}.L0E".format(header[0][1])
        zone_internal_header = ["Sector","Zone","ExogProd","InducedPro","ExogDemand","Price","ValueAdded","Attractor"]
        zone_export_header = ["Sector","Zone","Exports"]
        zone_import_header = ["Sector","Zone","Min Imp.","Max Imp.","Price","Attractor"]
        zone_prod_header = ["Sector","Zone","Min","Max"]
        fh = None

        qry = """select id from scenario where cod_previous = ''"""
        
        result_base_scenario = self.dataBaseSqlite.executeSql(qry)
        id_base_scenario = result_base_scenario[0][0]
        # 1.1
        qry_internal = f"""select 
                        distinct id_sector, id_zone, coalesce(nullif(exogenous_production, ''),0), coalesce(nullif(induced_production, ''),0), 
                        coalesce(nullif(exogenous_demand, ''),0), coalesce(nullif(base_price, ''),0), coalesce(nullif(value_added, ''),0), coalesce(nullif(attractor, ''),0)
                        from 
                        zonal_data a 
                        join zone b on a.id_zone = b.id
                        where (external is null or external = 0) and b.id > 0 and (exogenous_production > 0 or exogenous_demand > 0 or  base_price > 0  or value_added > 0 or  attractor >  0)
                        and id_scenario =  {id_base_scenario}
                        order by 1, 2""" 

        result_internal = self.dataBaseSqlite.executeSql(qry_internal) 
        internal_data =[[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],valor[7]] for valor in result_internal]

        # 2.1
        qry_exports = f"""select 
                        distinct id_sector, id_zone, coalesce(nullif(exports,''),0)
                        from 
                        zonal_data a 
                        join zone b on a.id_zone = b.id
                        where b.external = 1 and id_zone > 0 and id_scenario = {id_base_scenario} and exports != '' and exports != 0"""

        result_export = self.dataBaseSqlite.executeSql(qry_exports) 
        export_data =[[valor[0],valor[1],valor[2]] for valor in result_export]

        # 2.2
        qry_imports = f"""select 
                    distinct id_sector, id_zone, coalesce(nullif(min_imports,''), 0), coalesce(nullif(max_imports,''), 0), 
                    coalesce(nullif(base_price,''), 0), coalesce(nullif(attractor,''), 0)
                    from 
                    zonal_data a 
                    join zone b on a.id_zone = b.id
                    where b.external = 1 and id_zone > 0 and id_scenario = 1
                    and (min_imports != '' or max_imports != '' or base_price != '' or attractor != '')
                    and (min_imports != 0 or max_imports != 0 or base_price != 0 or attractor != 0) and id_scenario = {id_base_scenario}"""

        result_imports = self.dataBaseSqlite.executeSql(qry_imports) 
        import_data =[[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5]] for valor in result_imports]

        # 3.0
        qry_prod = f"""select 
                distinct id_sector, id_zone, coalesce(nullif(min_production,''), 0), coalesce(nullif(max_production,''), 0), coalesce(nullif(induced_production,''), 0), \
                     coalesce(nullif(exogenous_production,''), 0)
                from 
                    zonal_data a 
                join zone b on a.id_zone = b.id
                where b.external is null and id_zone > 0 
                and min_production = max_production 
                /* and min_production > 0 
                and max_production > 0 */ and id_scenario = {id_base_scenario} """

        result_prod = self.dataBaseSqlite.executeSql(qry_prod) 
        data_result = []
        for value in result_prod:
            if (value[4] + value[5]) > 0  and value[2] > 0 and value[3] > 0:
                data_result.append([value[0],value[1],value[2],value[3]])
            elif (value[4] + value[5]) == 0  and value[2] == 0 and value[3] == 0:
                data_result.append([value[0],value[1],value[2],value[3]])

        # prod_data =[[valor[0],valor[1],valor[2],valor[3]] for valor in result_prod]
        prod_data = data_result
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf-8")
            fh.write("LOCALIZATION DATA - File L0E  (QTRANUS v2019.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1. Base Year Data for Calibration \n")
            fh.write(" 1.1 Observed Data per Internal Zone \n")
            fh.write(tabulate(internal_data, tablefmt='plain', headers=zone_internal_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2. RELATIONSHIPS WITH EXTERNAL ZONES \n")
            fh.write(" 2.1 Exports \n")
            fh.write(tabulate(export_data, tablefmt='plain', headers=zone_export_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write(" 2.2 Imports \n")
            fh.write(tabulate(import_data, tablefmt='plain', headers=zone_import_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3. RESTRICTIONS TO PRODUCTION \n")
            fh.write(tabulate(prod_data, tablefmt='plain', headers=zone_prod_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            #self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()

    def write_f1e_file(self, id_scenario):

        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]

        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.F1E".format(header[0][1], codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        # 1.0 CATEGORY FORMATION FROM SOCIO-ECONOMIC SECTORS
        int_trans_cat =["Cat","Sector","Type","TimeF","VolumeF","Cons>Pro","Pro>Cons"]
        qry_trans_cat = """select distinct coalesce(nullif(id_category,''),0) id_category, coalesce(nullif(id_sector,''),0) id_sector, coalesce(nullif(type,''),0) type, 
                        coalesce(nullif(time_factor,''),0) time_factor, coalesce(nullif(volume_factor,''),0) volume_factor, coalesce(nullif(flow_to_product,''),0) flow_to_product, coalesce(nullif(flow_to_consumer,''),0) flow_to_consumer
                        from inter_sector_transport_cat
                        where id_scenario = 1 and (type != '' or time_factor != '' 
                         or  volume_factor != '' or flow_to_product != '' or  flow_to_consumer != '') order by 2 ASC""".format(id_scenario)
        result_trans_cat = self.dataBaseSqlite.executeSql(qry_trans_cat) 
        trans_cat_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_trans_cat] 
        
        # 2.0  INTRAZONAL COST PARAMETERS (ONLY FOR PROGRAM COST)
        int_zone_cost =["Zone","First Leve","Second Lev"]
        qry_trans_cat = """select 0, def_internal_cost_factor
                            from 
                            config_model
                            where def_internal_cost_factor is not null
                            UNION
                            select id zone, coalesce(nullif(internal_cost_factor,''),0) internal_cost_factor
                            from zone 
                            where internal_cost_factor is not null and internal_cost_factor > 0"""
        result_zone_cost = self.dataBaseSqlite.executeSql(qry_trans_cat) 
        zone_cost_data = [[valor[0],valor[1],"/"] for valor in result_zone_cost] 

        #3.0  EXOGENOUS TRIPS
        #  3.1 Exogenous trips by transport category
        exogenous_trips_cat =["Cat","Orig","Dest","Trips", "Factor"]
        exogenous_cat = """select id_category, id_zone_from, id_zone_to, 
                        coalesce(trip,0) trip, 1 factor 
                        from exogenous_trips
                        where id_scenario = {}""".format(id_scenario)
        result_exogenous_cat = self.dataBaseSqlite.executeSql(exogenous_cat) 
        exogenous_cat_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_exogenous_cat] 
        
        #  3.0 Exogenous trips by transport category
        # exogenous_trips_cat_mode =["Cat","Orig","Dest","Mode","Trips", "Factor"]
        # exogenous_cat_mode = select id_category, id_zone_from, id_zone_to, id_mode, 
        #                    coalesce(trip,0) trip, coalesce(factor,0) factor 
        #                    from exogenous_trips 
        #                    where id_scenario = {}.format(id_scenario)
        # result_exogenous_cat_mode = self.dataBaseSqlite.executeSql(exogenous_cat_mode) 
        # exogenous_cat_mode_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5]] for valor in result_exogenous_cat_mode] """

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("LAND USE - TRANSPORT INTERFACE - File F1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 CATEGORY FORMATION FROM SOCIO-ECONOMIC SECTORS \n")
            fh.write(tabulate(trans_cat_data, tablefmt='plain', headers=int_trans_cat)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0  INTRAZONAL COST PARAMETERS (ONLY FOR PROGRAM COST) \n")
            fh.write(tabulate(zone_cost_data, tablefmt='plain', headers=int_zone_cost)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0  EXOGENOUS TRIPS \n")
            fh.write("     3.1 Exogenous trips by transport category \n")
            fh.write(tabulate(exogenous_cat_data, tablefmt='plain', headers=exogenous_trips_cat)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("     3.2 Exogenous trips by transport category and mode \n")
            fh.write(" Cat    Orig    Dest    Mode    Trips    Factor \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()

    def write_l1e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]

        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L1E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'landuse'")
        
        #2.1
        sector_header = ["\nSector","\nName", "Utility\nLev1","\nLev2","Price\nLev1","\nLev2","Logit\nScale","Atrac\nFactor","Price-Cost\nRatio","Sector\nType","Target\nSector"]
        qry_sectors = f"""select distinct id sector, name, 
                        coalesce(nullif(location_choice_elasticity,''),0) utility_lvl1, 
                        coalesce(nullif(location_choice_elasticity,''),0) utility_lvl2, 
                        1 as price_lvl1, 0  as price_lvl2, 1 as logic_scale , 
                        coalesce(nullif(atractor_factor,''),0), 
                        0 price_cost_ratio, 0 sector_type, '' target_sector 
                        from 
                        sector
                        where id_scenario = {id_scenario}"""

        result_sector = self.dataBaseSqlite.executeSql(qry_sectors) 
        sector_data =[[valor[0],"'"+valor[1]+"'",valor[2],valor[3],valor[4],valor[5],valor[6],valor[7],valor[8],valor[9], "/"] for valor in result_sector]

        #2.2
        demand_func_para = ["Sector","Input","MinCons","MaxCons","Elast"]
        qry_demand_func = f"""select  distinct id_sector sector, id_input_sector input, 
                            coalesce(nullif(min_demand,''),0) mincons, coalesce(nullif(max_demand,''),0) maxcons, 
                            coalesce(nullif(elasticity,''),0) elast
                            from inter_sector_inputs
                            where id_scenario = {id_scenario} and (nullif(min_demand,'') > 0 or nullif(max_demand,'') > 0 )"""
        result_demand_func = self.dataBaseSqlite.executeSql(qry_demand_func) 
        demand_func_data =[[valor[0],valor[1],valor[2],valor[3],str(valor[4])+" /"] for valor in result_demand_func]
 
        #2.3
        demand_subs = ["Sector","SustElast","LogitSc","Subst","Penal .../"]
        qry_demand_subs = f"""
                    select distinct id_sector sector, coalesce(nullif(b.substitute,''),0) subselast, 1 logicsc, id_sector sector, 1 penal 
                    from inter_sector_inputs a
                    join sector b on (a.id_sector = b.id and a.id_scenario = b.id_scenario)
                    where a.id_scenario = {id_scenario} and (a.substitute is not null and a.substitute !='')"""
        result_demand_subs = self.dataBaseSqlite.executeSql(qry_demand_subs) 

        demand_subs_data =[[valor[0],valor[1],valor[2], self.dataBaseSqlite.findDemandSubsXSect(id_scenario, valor[0]), '/'] for valor in result_demand_subs]

        #3.1
        attrac_exog =["Sect","AttracSe","Lev1","Lev2","ProdFac","PriceFac","CapFac"]
        qry_attractors_exog = f"""select distinct id_sector sector, id_input_sector, coalesce(nullif(exog_prod_attractors,''),0) lvl1, 0 lvl2, 
                                1 prodfact, 0 pricefactor, 0 capfact
                                from inter_sector_inputs 
                                where id_scenario = {id_scenario} and nullif(exog_prod_attractors,'') > 0"""
        result_attra_exog = self.dataBaseSqlite.executeSql(qry_attractors_exog) 
        attractors_exog_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_attra_exog]  

        #3.2
        attrac_ind =["Sector","Var","Lev1","Lev2"]
        qry_attra_ind = f"""select distinct id_sector sector, id_input_sector var, 
                            coalesce(nullif(ind_prod_attractors,''),0) lvl1, 0 lvl2
                            from inter_sector_inputs 
                            where id_scenario = {id_scenario} and nullif(ind_prod_attractors,'') > 0"""
        result_attra_ind = self.dataBaseSqlite.executeSql(qry_attra_ind) 
        attractors_ind_data = [[valor[0],valor[1],valor[2],valor[3]] for valor in result_attra_ind] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("ACTIVITY LOCATION PARAMETERS - File L1E  (QTRANUS v2019.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0  GLOBAL PARAMETERS \n")
            fh.write("      Iterations     Convergenc \n")
            fh.write("              {}             {}      {} /\n".format(result[0][2] or 0, result[0][3], float(result[0][4])))
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SOCIOECONOMIC SECTORS \n")
            fh.write("  2.1 Locational Utility Function Parameters \n")
            fh.write(tabulate(sector_data, tablefmt='plain', headers=sector_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("  2.2 Demand Function Parameters \n")
            fh.write(tabulate(demand_func_data, tablefmt='plain', headers=demand_func_para)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("  2.3 Demand Substitutions \n")
            fh.write(tabulate(demand_subs_data, tablefmt='plain', headers=demand_subs)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 ATRACTION VARIABLES AND PARAMETERS \n")
            fh.write("   3.1 Atractors for Increments in Exogenous Variables \n")
            fh.write(tabulate(attractors_exog_data, tablefmt='plain', headers=attrac_exog)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("   3.2 Atractors for Induced Production \n")
            fh.write(tabulate(attractors_ind_data, tablefmt='plain', headers=attrac_ind)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_l3e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L3E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("ALLOCATION OF CHANGES IN EXOGENOUS VARIABLES - File L3E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 INECREMENTS/DECREMENTS IN EXOGENOUS VARIABLES \n")
            fh.write("      Sector 'Variable'      'Func'               Value   Constant [AttracS 'AttracVar'         Param]  .../ \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))


        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_p0e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """

        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.P0E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        # 2.1 TRANSPORT DEMAND CATEGORIES
        trans_mode_head =["No.","'Name'","Paths","Overlapp","ASC"]
        qry_trans_mode = """select a.id, name, coalesce(nullif(maximum_number_paths,''),0), 
                            coalesce(path_overlapping_factor,0), 0 asc
                        from mode a"""
        result_trans_mode = self.dataBaseSqlite.executeSql(qry_trans_mode) 
        trans_mode_data = [[valor[0],"'"+valor[1]+"'",valor[2], valor[3], "%s /" % valor[4]  ] for valor in result_trans_mode] 

        # 2.2
        trans_ope_head =["No","'Name'","Mode","Type","OccRate","Penaliz","MinWait","MaxWait","PathASC"]
        qry_ope = """select a.id, a.name, a.id_mode mode, a.type, coalesce(nullif(a.basics_occupency,''),0) occupency, 
                            coalesce(nullif(a.basics_modal_constant,''),0) penaliz, 
                            coalesce(nullif(a.basics_fixed_wating_factor,''),0)  minwait,  0 maxwait, 0 path_asc 
                            from operator a
                            where id_scenario = {}""".format(id_scenario)
        result_ope = self.dataBaseSqlite.executeSql(qry_ope) 
        ope_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],valor[4],valor[5],valor[6],valor[7],str(valor[8])+" /"] for valor in result_ope] 
        
        # 2.3
        trans_route_head =["No","'Name'","Oper","MinFreq","MaxFreq","Tartet Occ","MaxFleet","Scheduled"]
        qry_route = """select a.id, a.name, a.id_operator, a.frequency_from, 
                    a.frequency_to, 0.70, coalesce(nullif(a.max_fleet,''),0), coalesce(nullif(a.follows_schedule,''),0)
                    from route a
                    where id_scenario = {} and used = 1""".format(id_scenario)
        result_route = self.dataBaseSqlite.executeSql(qry_route) 
        route_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],valor[4],valor[5],valor[6],str(valor[7])+" /"] for valor in result_route] 

        # 2.4
        trans_adm_head =["No","'Name'"]
        qry_adm = """select a.id, name  
                     from administrator a
                     where id_scenario = {} """.format(id_scenario)
        result_adm = self.dataBaseSqlite.executeSql(qry_adm) 
        adm_data = [[valor[0],"'"+str(valor[1])+"'"] for valor in result_adm] 

        # 2.5
        trans_lynkt_head =["No","'Name'","Admin","MinMaintCo"]
        qry_lynkt = """select a.id, name, id_administrator, coalesce(nullif(min_maintenance_cost,''),0)
                        from link_type a
                        where a.id_scenario = {}""".format(id_scenario)
        result_lynkt = self.dataBaseSqlite.executeSql(qry_lynkt) 
        lynkt_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3]] for valor in result_lynkt] 

        # 3.0
        trans_cat_head =["No","'Name'","VofTrTime","VofWtTime", "Available Modes"]
        qry_cat = """select id, name, coalesce(nullif(volumen_travel_time,''),0), coalesce(nullif(value_of_waiting_time,''),0), id_mode 
                    from category
                    where id_scenario = {}""".format(id_scenario)
        result_cat = self.dataBaseSqlite.executeSql(qry_cat) 
        cat_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],str(valor[4])+" /"] for valor in result_cat] 

        # 4.1
        cost_ener_head =["Oper", "MinCons", "MaxCons","Slope","EnerCost","CtOpCost","TimeOpCost"]
        qry_cost_ener = """select a.id, coalesce(nullif(a.energy_min,''),0) energy_min, coalesce(nullif(a.energy_max,''),0) energy_max, 
                        coalesce(nullif(a.energy_slope,''),0) energy_slope, coalesce(nullif(a.energy_cost,''),0) energy_cost,
                        0 cost_time_operation, 
                        coalesce(nullif(cost_time_operation,''), 0) cost_time_operation
                        from operator a
                        where id_scenario = {}""".format(id_scenario)
        result_cost_ener = self.dataBaseSqlite.executeSql(qry_cost_ener) 
        cost_ener_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_cost_ener] 

        # 4.2
        cost_header =["Type", "Oper", "Speed","EqVeh","DistCost","Toll","Maint","Penal"]
        qry_cond = """select 
                        CAST(a.id_linktype as integer) id_linktype, a.id_operator, coalesce(nullif(speed,''),0), coalesce(nullif(equiv_vahicules,''),0), coalesce(nullif(distance_cost,''),0), 
                        coalesce(nullif(charges,''),0) toll, coalesce(nullif(margin_maint_cost,''),0), coalesce(nullif(penaliz,''),0)
                        from link_type_operator a
                        where id_scenario = {} and speed > 0
                        order by 1,2 """.format(id_scenario)
        result_cond = self.dataBaseSqlite.executeSql(qry_cond) 
        cost_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],valor[7]] for valor in result_cond] 
        
        # 4.3
        overlap_head =["Type", "Oper", "Overlap"]
        qry_overlap = """select 
                        CAST(a.id_linktype as integer) id_linktype, a.id_operator, coalesce(nullif(overlap_factor,''),0) overlap_factor
                        from link_type_operator a
                        where id_scenario = {} and overlap_factor > 1
                        order by 1,2 """.format(id_scenario)
        result_overlap = self.dataBaseSqlite.executeSql(qry_overlap) 
        overlap_data = [[valor[0],valor[1],valor[2]] for valor in result_overlap] 

        # 5.1
        tariff_head =["Oper","MinTarf","TimeTarf","DistTarf.","OperCost"]
        qry_tariff = """select distinct a.id, coalesce(nullif(basics_boarding_tariff,''),0), coalesce(nullif(basics_time_tariff,''),0),  
                        coalesce(nullif(basics_distance_tariff,''),0), coalesce(nullif(cost_porc_paid_by_user/100,''),0)  
                        from operator a
                        where id_scenario = {} 
                        and (basics_boarding_tariff > 0 or basics_time_tariff > 0 or cost_porc_paid_by_user > 0)""".format(id_scenario)

        result_tariff = self.dataBaseSqlite.executeSql(qry_tariff) 
        tariff_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_tariff] 

        # 5.2
        transfer_head =["FromOper","ToOper","Tariff"]
        qry_transfer = """select id_operator_from, id_operator_to, coalesce(nullif(cost,''),0)
                        from transfer_operator_cost
                        where id_scenario = {} order by 1,2 """.format(id_scenario)
        result_transfer = self.dataBaseSqlite.executeSql(qry_transfer) 
        transfer_data = [[valor[0],valor[1],valor[2]] for valor in result_transfer]

        # 5.3
        cat_cost_head =["Cat","Oper","Penal F.","Tariff F..","ASC"]
        qry_cat_cost = """select id_category, id_operator, coalesce(nullif(penal_factor,''),0), coalesce(nullif(tariff_factor,''),0), 0 asc
                        from operator_category
                        where id_scenario = {}""".format(id_scenario)
        result_cat_cost = self.dataBaseSqlite.executeSql(qry_cat_cost) 
        cat_cost_data = [[valor[0],valor[1],valor[2],valor[3],str(valor[4])+" /"] for valor in result_cat_cost] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("TRANSPORT PARAMETERS - File P0E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 GLOBAL PARAMETERS \n")
            fh.write("    For TRANUS Internal Use \n")
            fh.write("    60 \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 TRANSPORT DEMAND CATEGORIES\n")
            fh.write("    2.1 Transport Modes \n")
            fh.write(tabulate(trans_mode_data, tablefmt='plain', headers=trans_mode_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Transport Operators (Type: 1=Free 2=Public 3=Routes 4=Walking)\n")
            fh.write(tabulate(ope_data, tablefmt='plain', headers=trans_ope_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.3 Public Transit Routes\n")
            fh.write(tabulate(route_data, tablefmt='plain', headers=trans_route_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.4 Administrators\n")
            fh.write(tabulate(adm_data, tablefmt='plain', headers=trans_adm_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.5 Link Types\n")
            fh.write(tabulate(lynkt_data, tablefmt='plain', headers=trans_lynkt_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 TRANSPORT DEMAND CATEGORIES\n")
            fh.write(tabulate(cat_data, tablefmt='plain', headers=trans_cat_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("4.0 COSTS AND OPERATING CONDITIONS \n")
            fh.write("    4.1 Energy and other operating costs per vehicle \n")
            fh.write(tabulate(cost_ener_data, tablefmt='plain', headers=cost_ener_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    4.2 Operating costs and conditions by link type \n")
            fh.write(tabulate(cost_data, tablefmt='plain', headers=cost_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    4.3 Path overlap factor by Link-Type & Operator \n")
            fh.write(tabulate(overlap_data, tablefmt='plain', headers=overlap_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("5.0 USER TARIFFS \n")
            fh.write("    5.1 Linear tariffs by operator \n")
            fh.write(tabulate(tariff_data, tablefmt='plain', headers=tariff_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    5.2 Integrated tarifs between operators (-1 if no transfers) \n")
            fh.write(tabulate(transfer_data, tablefmt='plain', headers=transfer_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    5.3 Tariff Factors by Category/Operator \n")
            fh.write(tabulate(cat_cost_data, tablefmt='plain', headers=cat_cost_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()

    def write_p1e_file(self,id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.P1E".format(header[0][1],codeScenario)
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        net_head =["Src","Dest","GISId","Type","Dist.","Capac.","Delay","Routes..    0 Restricted Turns..../"]
        qry_net = """select distinct node_from, node_to, id, id_linktype, 
                    coalesce(nullif(length,''),0), 
                    case when capacity = 0 then -1 else coalesce(nullif(capacity,''),0) end capacity, 
                    coalesce(nullif(delay,''),0), 0
                    from link
                    where id_scenario = %s
                    order by 1,2;""" % (id_scenario)
        
        result_net = self.dataBaseSqlite.executeSql(qry_net) 
        result_routes = []

        #[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6], str(valor[7])+" /"]
        net_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5], valor[6], str(self.dataBaseSqlite.findRoutesRestrictedTurns(f"{valor[0]}-{valor[1]}", id_scenario))] for valor in result_net] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("TRANSPORT NETWORK DEFINITION - File P1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("2.0 DELETED LINKS \n")
            fh.write("         Src      Dst    GISId     Type  \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 MODIFIED LINKS \n")
            fh.write("         Src     Dest    GISId     Type      Dist.     Capac.      Delay Routes..  0 Restricted Turns.... / \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 NEW LINKS \n")
            fh.write(tabulate(net_data, tablefmt='plain', headers=net_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("4.0 INTERSECTION DELAYS \n")
            fh.write("         Src      Dst     Node      Delay \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_t1e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.T1E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")

        # 1.0
        global_head =["Iterations","Convergenc",""]
        qry_global = """select iterations, coalesce(nullif(convergence,''),0), smoothing_factor
                        from config_model
                        where type='transport'"""

        result_global = self.dataBaseSqlite.executeSql(qry_global) 
        global_data = [[valor[0],valor[1],float(valor[2])] for valor in result_global]

        # 2.1
        ope_simu_head =["Oper","TimeFactor","ConsolPar"]
        qry_ope_simu = """select a.id, coalesce(nullif(basics_time_factor,''),0), -1 cosolpar
                        from operator a
                        where id_scenario = {}""".format(id_scenario)
                    
        result_ope_simu = self.dataBaseSqlite.executeSql(qry_ope_simu) 
        ope_simu_data = [[valor[0],valor[1],valor[2]] for valor in result_ope_simu]

        # 2.2
        restr_head =["Link\nType","% Reduct\nat V/C=1","% Reduct\nMax", "V/C for\nMin Vel","Capacity\nFactor"]
        qry_restr = """select a.id, coalesce(nullif(perc_speed_reduction_vc,''),0), coalesce(nullif(perc_max_speed_reduction,''),0), 
                        coalesce(nullif(vc_max_reduction,''),0), coalesce(nullif(capacity_factor,''),0) 
                        from link_type a
                        where id_scenario = {}""".format(id_scenario)
        result_restr = self.dataBaseSqlite.executeSql(qry_restr) 
        restr_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_restr]

        # 2.3
        trip_gen_head =["Cat","MinGen","MaxGen", "GenElast","ModeElast","Logit Sc","CarAvail"]
        qry_trip_gen = """select id, coalesce(nullif(min_trip_gener,''),0), coalesce(nullif(max_trip_gener,''),0), 
                    coalesce(nullif(elasticity_trip_gener,''),0), 1 modeelast, 1 logitsc, 1 caravail 
                    from category
                    where id_scenario = {}""".format(id_scenario)
        result_trip_gen = self.dataBaseSqlite.executeSql(qry_trip_gen) 
        trip_gen_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_trip_gen]
        
        # 2.4
        path_head =["Cat","PathChElas","Logit Sc"]
        qry_path = """select id, coalesce(nullif(choice_elasticity,''),0), 1 logitsc 
                        from category
                    where id_scenario = {}""".format(id_scenario)
        result_path = self.dataBaseSqlite.executeSql(qry_path) 
        path_data = [[valor[0],valor[1],valor[2]] for valor in result_path]
        
        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("TRANSPORT ASSIGNMENT PARAMETERS - File T1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 GLOBAL PARAMETERS \n")
            fh.write(tabulate(global_data, tablefmt='plain', headers=global_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 Simulation Parameters \n")
            fh.write("    2.1 Operator Parameters \n")
            fh.write(tabulate(ope_simu_data, tablefmt='plain', headers=ope_simu_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Capacity Restriction Parameters \n")
            fh.write(tabulate(restr_data, tablefmt='plain', headers=restr_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.3 Trip generation and modal split \n")
            fh.write(tabulate(trip_gen_data, tablefmt='plain', headers=trip_gen_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.4 Path Choice Parameters \n")
            fh.write(tabulate(path_data, tablefmt='plain', headers=path_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()



    def write_l2e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L2E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")

        #1.1 
        global_increments_head = ["Sector","Production","Demand","MinRest","MaxRest"]
        qry_global_incre = """select id_sector,  
                            coalesce(nullif(exogenous_production,''),0), 
                            coalesce(nullif(exogenous_demand,''),0), 
                            coalesce(nullif(min_production,''),0), 
                            coalesce(nullif(max_production,''),0)
                            from 
                                zonal_data a
                            where a.id_zone = 0 and id_scenario = {} and 
                            ((exogenous_production !='' and exogenous_production !=0) 
                            or (exogenous_demand !='' and exogenous_demand != 0) 
                            or (min_production!='' and min_production!=0) 
                            or (max_production!='' and max_production!=0)) order by 1 asc""".format(id_scenario)

        result_global_incre = self.dataBaseSqlite.executeSql(qry_global_incre)
        global_data =  [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_global_incre]

        #1.2 
        int_exog_prods_head = ["Sector","Zone","Increment"]
        qry_exog_prod_incre = """select distinct id_sector sector, id_zone zone, 
                            coalesce(nullif(exogenous_production,''),0) exogenous_production
                            from zonal_data a
                            where a.id_zone != 0 and id_scenario = {} and (exogenous_production != 0 and exogenous_production != '') order by 2,1""".format(id_scenario)
        result_int_exog_prod = self.dataBaseSqlite.executeSql(qry_exog_prod_incre)
        int_exog_prod_data =  [[valor[0],valor[1],valor[2]] for valor in result_int_exog_prod]

        #1.3 
        int_exog_demand_head = ["Sector","Zone","Increment"]
        qry_exog_demand_incre = """select distinct id_sector sector, id_zone zone, 
                                coalesce(nullif(exogenous_demand,''),0) exogenous_demand
                                from zonal_data a
                                where a.id_zone != 0 and id_scenario = {} and (exogenous_demand!=0 and exogenous_demand!='')  order by 2,1""".format(id_scenario)
        result_int_demand_prod = self.dataBaseSqlite.executeSql(qry_exog_demand_incre)
        int_exog_demand_data =  [[valor[0],valor[1],valor[2]] for valor in result_int_demand_prod]

        #2.1
        int_ext_zone_exp_head = ["Sector","Zone","Increment"]
        qry_ext_zone_exp = """select distinct
                    id_sector sector, id_zone zone, 
                    coalesce(nullif(exports,''), 0) exports
                    from zonal_data a 
                    join zone b on (a.id_zone = b.id)
                    where a.id_zone != 0 and b.external = 1 and id_scenario = {} and (exports != 0 and exports !='') order by 2,1""".format(id_scenario)
        result_ext_zone_prod = self.dataBaseSqlite.executeSql(qry_ext_zone_exp)
        int_ext_zone_data =  [[valor[0],valor[1],valor[2]] for valor in result_ext_zone_prod]

        #2.2
        int_imp_zone_exp_head = ["Sector","Zone","Min Incr.", "Max Incr.", "Attractor"]
        qry_imp_zone_exp = """select distinct
                                    id_sector sector, id_zone zone, 
                                    coalesce(nullif(min_imports,''), 0) min_imports, 
                                    coalesce(nullif(max_imports,''), 0) max_imports, 
                                    coalesce(nullif(attractor_import,''),0) attractor_import
                                from zonal_data a 
                                join zone b on (a.id_zone = b.id)
                                where b.external = 1 and id_scenario = {} 
                                and (min_imports != 0 and min_imports !='')
                                or (max_imports != 0 and  max_imports != '')
                                or (attractor_import != 0 and attractor_import != '') order by 1""".format(id_scenario)
        result_imp_zone_prod = self.dataBaseSqlite.executeSql(qry_imp_zone_exp)
        int_imp_zone_data =  [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_imp_zone_prod]

        #3.1
        int_endvar_head = ["Sector","Zone","Attractor"]
        qry_endvar = """select distinct
                        id_sector sector, id_zone zone, 
                        coalesce(nullif(attractor,''), 0) attractor
                        from zonal_data a 
                        join zone b on (a.id_zone = b.id) 
                        where a.id_zone != 0 and a.id_scenario = {} and (attractor != 0 and attractor != '') order by 1,2""".format(id_scenario)
        result_endvar = self.dataBaseSqlite.executeSql(qry_endvar)
        int_endvar_data =  [[valor[0],valor[1],valor[2]] for valor in result_endvar]

        #3.2
        int_prod_head = ["Sector","Zone","MinRest", "MaxRest"]
        qry_prod = """select 
                    distinct  id_sector sector, id_zone zone, 
                    coalesce(nullif(min_production,''),0) min_production, 
                    coalesce(nullif(max_production,''),0) max_production
                    from zonal_data 
                    where id_zone != 0 and id_scenario = {} and (min_production != 0 or max_production != 0)  order by 1,2 """.format(id_scenario)
        result_prod = self.dataBaseSqlite.executeSql(qry_prod)
        int_prod_data =  [[valor[0],valor[1],valor[2],valor[3]] for valor in result_prod]

        #3.3
        int_value_add_head = ["Sector","Zone","ValueAdded"]
        qry_value_add = """select distinct 
                                id_sector sector, id_zone zone, 
                                coalesce(nullif(value_added,''),0) value_added
                        from zonal_data
                        where id_zone != 0 and id_scenario = {} and (value_added != 0 and value_added != '') 
                        order by 1,2""".format(id_scenario)
        result_value_add = self.dataBaseSqlite.executeSql(qry_value_add)
        int_value_add_data =  [[valor[0],valor[1],valor[2]] for valor in result_value_add]

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf-8")
            fh.write("LOCALIZATION DATA - File L2E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 INCREMENTS IN EXOGENOUS VARIABLES \n")
            fh.write("    1.1 Global Increments\n")
            fh.write(tabulate(global_data, tablefmt='plain', headers=global_increments_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    1.2 Increments in Exogenous Production per Internal Zone\n")
            fh.write(tabulate(int_exog_prod_data, tablefmt='plain', headers=int_exog_prods_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    1.3 Increments in Exogenous Demand per Internal Zone\n")
            fh.write(tabulate(int_exog_demand_data, tablefmt='plain', headers=int_exog_demand_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 INCREMENTS IN IMPORTS AND EXPORTS \n")
            fh.write("    2.1 Increments in Exports by External Zone\n")
            fh.write(tabulate(int_ext_zone_data, tablefmt='plain', headers=int_ext_zone_exp_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Increments in Imports by External Zone\n")
            fh.write(tabulate(int_imp_zone_data, tablefmt='plain', headers=int_imp_zone_exp_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 INCREMENTS IN ENDOGENOUS VARIABLES \n")
            fh.write("    3.1 Increments in Location Atractors by Sector and Zone (Zone=0 means 'All Zones')\n")
            fh.write(tabulate(int_endvar_data, tablefmt='plain', headers=int_endvar_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    3.2 Increments in Production Restriction per Sector-Zone\n")
            fh.write(tabulate(int_prod_data, tablefmt='plain', headers=int_prod_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    3.3 Increments in Value Added by Sector-Zone \n")
            fh.write("                                                (Zone=0 means All Zones) \n")
            fh.write(tabulate(int_value_add_data, tablefmt='plain', headers=int_value_add_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()
    
    

        
        