# -*- coding: utf-8 -*-
import sys, os

import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError
from typing import Tuple
from ..general.Helpers import Helpers

class DataBaseSqlite():
	"""
        @summary: Class Constructor
    """
	def __init__(self, tranus_folder):
		self.tranus_folder = tranus_folder
		self.conn = self.connectionSqlite()

	def __del__(self):
		try:
			if self.conn:
				self.conn.close()
		except:
			print("There is no Connection")

	def connectionSqlite(self):
		"""
        @summary: Class Constructor
    	"""
		self.tranus_folder = self.tranus_folder if self.tranus_folder[-3:]=='.db' else f"{self.tranus_folder}.db"
		path = f"{self.tranus_folder}"
		try:
			conn = sqlite3.connect(path)
		except (OperationalError):
			print("Connection to Database Failed")
			return False
		return conn


	def dataBaseStructure(self, conn):
		"""
		@summary: Validates invalid characters
		@param input: Input string
		@type input: String object
		"""
		cursor = conn.cursor()
		tables = [
		    """
			CREATE TABLE IF NOT EXISTS project_files (
				zone_shape_file      TEXT,
				zone_shape_file_id   TEXT,
				zone_shape_file_name   TEXT,
				link_shape_file      TEXT,
				link_shape_file_codscenario   TEXT,
				link_shape_file_origin   TEXT,
				link_shape_file_destination   TEXT,
				link_shape_file_id   TEXT,
				link_shape_file_name   TEXT,
				link_shape_file_type   TEXT,
				link_shape_file_length   TEXT,
				link_shape_file_direction   TEXT,
				link_shape_file_capacity   TEXT,
				node_shape_file      TEXT,
				node_shape_file_id   TEXT,
				node_shape_file_name   TEXT,
				node_shape_file_type   TEXT,
				node_shape_file_x   TEXT,
				node_shape_file_y   TEXT
			);""",
			"""
			CREATE TABLE IF NOT EXISTS scenario (
				id 			 INTEGER PRIMARY KEY AUTOINCREMENT,
				code         CHAR(20) NOT NULL,
				name         TEXT NOT NULL,
				cod_previous CHAR(20)
			);""",
			"""
			CREATE TABLE IF NOT EXISTS project (
				id 			 INTEGER PRIMARY KEY AUTOINCREMENT,
				name         TEXT NOT NULL,
				description  TEXT NOT NULL,
				author       TEXT NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS config_model (
				id 			 			 INTEGER PRIMARY KEY AUTOINCREMENT,
				type         			 TEXT NOT NULL,
				iterations  		     INTEGER NOT NULL,
				convergence  			 REAL NOT NULL,
				smoothing_factor  		 REAL NOT NULL,
				route_similarity_factor  TEXT, 
				def_internal_cost_factor REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS sector (
				id           			   INTEGER,
				id_scenario                INTEGER NOT NULL,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL,
				transportable 			   INTEGER NOT NULL,
				location_choice_elasticity REAL,
				atractor_factor   		   REAL NOT NULL,
				price_factor  		       REAL NOT NULL,
				substitute   		       REAL NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS mode (
				id           			   INTEGER,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL,
				path_overlapping_factor    INTEGER NOT NULL,
				maximum_number_paths       INTEGER NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS administrator (
				id           			   INTEGER,
				id_scenario 			   INTEGER,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS category (
				id           			   INTEGER,
				id_scenario                INTEGER,
				id_mode           		   INTEGER,
				name         			   TEXT NOT NULL,
				description    			   TEXT,
				volumen_travel_time        REAL, 
				value_of_waiting_time      REAL, 
			    min_trip_gener             REAL,
			    max_trip_gener             REAL, 
			    elasticity_trip_gener      REAL, 
			    choice_elasticity          REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS inter_sector_inputs (
				id		        INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario     INTEGER NOT NULL,
				id_sector       INTEGER NOT NULL,
				id_input_sector INTEGER NOT NULL,
				min_demand      REAL,
				max_demand    	REAL,
				elasticity      REAL,
				substitute      REAL,
				exog_prod_attractors REAL,
				ind_prod_attractors REAL,
				CONSTRAINT fk_inter_sector_inputs_scenarios
    			FOREIGN KEY (id_scenario)
    			REFERENCES scenario(id)
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS inter_sector_transport_cat (
				id		        INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario     INTEGER NOT NULL,
				id_sector       INTEGER NOT NULL,
				id_category     INTEGER NOT NULL,
				type            REAL,
				time_factor    	REAL,
				volume_factor   REAL,
				flow_to_product REAL,
				flow_to_consumer REAL,
				CONSTRAINT fk_inter_sector_transport_cat_scenarios
    			FOREIGN KEY (id_scenario)
    			REFERENCES scenario(id)
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS zone (
				id		   			INTEGER NOT NULL,
				name       			TEXT NOT NULL,
				external   			BLOB,
				internal_cost_factor REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS zonal_data (
				id		             INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario          INTEGER NOT NULL,
				id_sector            INTEGER NOT NULL,
				id_zone              INTEGER NOT NULL,
				exogenous_production REAL,
				induced_production   REAL,
				min_production       REAL,
				max_production       REAL,
				exogenous_demand     REAL,
				base_price    	     REAL,
				value_added          REAL,
				attractor            REAL,
				max_imports          REAL,
				min_imports          REAL,
				exports              REAL,
				attractor_import     REAL,
				CONSTRAINT fk_zonal_data_scenarios
    			FOREIGN KEY (id_scenario)
    			REFERENCES scenario(id)
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS operator (
				id           			   INTEGER,
				id_scenario                INTEGER,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL,
				id_mode    			       INTEGER NOT NULL,
				type        			   INTEGER NOT NULL,
				basics_modal_constant       REAL NOT NULL,
				basics_occupency    		REAL NOT NULL,
				basics_time_factor    		REAL NOT NULL,
				basics_fixed_wating_factor  REAL NOT NULL,
				basics_boarding_tariff    	REAL NOT NULL,
				basics_distance_tariff    	REAL NOT NULL,
				basics_time_tariff    	    REAL NOT NULL,
				energy_min    	            REAL NOT NULL,
				energy_max    	            REAL NOT NULL,
				energy_slope    	        REAL NOT NULL,
				energy_cost    	            REAL NOT NULL,
				cost_time_operation    	    REAL NOT NULL,
				cost_porc_paid_by_user    	REAL NOT NULL,
				stops_min_stop_time    	    REAL NOT NULL,
				stops_unit_boarding_time    REAL NOT NULL,
				stops_unit_alight_time    	REAL NOT NULL,
				color 					    INT  NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS operator_category (
				id		      INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario   INTEGER,
				id_operator   INTEGER,
				id_category   INTEGER,
				tariff_factor REAL,
				penal_factor  REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS transfer_operator_cost (
				id		          INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario       INTEGER,
				id_operator_from  INTEGER,
				id_operator_to    INTEGER,
				cost REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS route (
				id	        INTEGER,
				id_scenario INTEGER,
				name        TEXT,
				description TEXT,
				id_operator    INTEGER,
				frequency_from REAL,
				frequency_to   REAL,
				target_occ     REAL,
				max_fleet      REAL,
				used 		   BLOB,
				follows_schedule BLOB,
				color          INTEGER	
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link_type (
				id	        INTEGER,
				id_scenario INTEGER,
				name        TEXT NOT NULL,
				description TEXT NOT NULL,
				id_administrator   		INTEGER,
				capacity_factor 		REAL,
				min_maintenance_cost   	REAL,
				perc_speed_reduction_vc REAL,
				perc_max_speed_reduction REAL,
				vc_max_reduction         REAL, 
				symbology                TEXT
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link_type_operator (
				id	              INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario       INTEGER,
				id_linktype       INTEGER NOT NULL,
				id_operator       INTEGER,
				speed   		  REAL,
				charges 		  REAL,
				penaliz   	      REAL,
				distance_cost     REAL,
				equiv_vahicules   REAL,
				overlap_factor    REAL,
				margin_maint_cost REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link (
				id	            INTEGER PRIMARY KEY AUTOINCREMENT,
				linkid          TEXT NOT NULL, 
				id_scenario     INTEGER,
				id_linktype     INTEGER,
				two_way         INTEGER,
				used_in_scenario INTEGER,
				node_from       INTEGER,
				node_to         INTEGER,
				name            TEXT,
				description     TEXT,
				length   		REAL,
				capacity   	    REAL,
				delay           REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link_route (
				id	            INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario     INTEGER,
				id_link         TEXT,
				id_route        INTEGER, 
				type_route      INTEGER
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS intersection_delay (
				id	            INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario     INTEGER,
				id_link         TEXT,
				id_node         INTEGER, 
				delay           REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS node (
				id	            INTEGER,
				id_scenario     INTEGER,
				id_type         INTEGER, 
				name            TEXT, 
				description     TEXT, 
				x               REAL,
				y               REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS exogenous_trips (
				id	          INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario   INTEGER, 
				id_zone_from  INTEGER, 
				id_zone_to    INTEGER,
				id_mode       INTEGER, 
				id_category   INTEGER,
				trip      	  REAL,
				factor        REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS results_zones (
				id     TEXT,
				name   TEXT,
				sectors_expression   TEXT,
				scenario      TEXT,
				field   TEXT
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS results_network (
				id     TEXT,
				name   TEXT,
				color   TEXT,
				scenario      TEXT,
				field   TEXT,
				id_field_name TEXT,
				level TEXT,
				method TEXT,
				sectors_expression TEXT
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS results_matrix (
				id     TEXT,
				name   TEXT,
				color   TEXT,
				origin_zones  TEXT,
				destination_zones  TEXT,
				scenario  TEXT,
				field   TEXT,
				id_field_name TEXT,
				method TEXT,
				sectors_expression TEXT
			);
			"""]
	
		indexes = ["""CREATE UNIQUE INDEX if NOT EXISTS idx_zone_id 
					ON zone (id);""",
					"""CREATE UNIQUE INDEX if NOT EXISTS idx_link_linkid_id_scenario 
					ON link (id_scenario, linkid);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_node_id_id_scenario 
					ON node (id_scenario, id);""",
				   """CREATE UNIQUE INDEX IF NOT EXISTS idx_route_id_id_scenario 
				    ON route (id_scenario, id);""",
				   """CREATE UNIQUE INDEX IF NOT EXISTS idx_link_route_linkid_id_route_id_scenario 
				    ON link_route (id_link, id_route, id_scenario);""",
				   """CREATE UNIQUE INDEX IF NOT EXISTS idx_link_intersectiodelay_linkid_id_node_id_scenario 
				    ON intersection_delay (id_link, id_node, id_scenario);""",
			       """CREATE UNIQUE INDEX IF NOT EXISTS idx_administrator_id_id_scenario 
					ON administrator (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_category_id_id_scenario 
				   ON category (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_operator_id_id_scenario 
				   ON operator (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_transfer_operator_cost_id_id_scenario_id_from_id_to
				   ON transfer_operator_cost (id_scenario, id_operator_from, id_operator_to);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_route_id_id_scenario
				   ON route (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_node_id_id_scenario
				   ON node (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_linktype_id_id_scenario
				   ON link_type (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_link_linkid_id_scenario
				   ON link (linkid, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_exogenoustrip_id_from_to_id_scenario_id_category
				   ON exogenous_trips (id_scenario, id_zone_from, id_zone_to, id_category);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_sector_id_id_scenario
				   ON sector (id, id_scenario);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_intersector_id_scenario_id_sector_id_input_sector
				   ON inter_sector_inputs (id_scenario, id_sector, id_input_sector);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_inter_sector_transport_cat_id_scenario_id_sector_id_category
				   ON inter_sector_transport_cat (id_scenario, id_sector, id_category);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_zonal_data_id_scenario_id_sector_id_zone
				   ON zonal_data (id_scenario, id_sector, id_zone);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_operator_category_id_scenario_id_operator_id_category
				   ON operator_category (id_scenario, id_operator, id_category);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_link_type_operator_id_scenario_id_linktype_id_operator
				   ON link_type_operator (id_scenario, id_linktype, id_operator);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_results_zones_id 
					ON results_zones (id);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_results_network_id 
					ON results_network (id);""",
				   """CREATE UNIQUE INDEX if NOT EXISTS idx_results_matrix_id 
					ON results_matrix (id);"""]

		# Types of routes: 1 Passes and Stops (passes_stops); 2 Passes Only (passes_only), 3 Can not Pass (cannot_pass)
		# Types of Nodes: 1 Zone Centroid, 2 External, 0 Node
		try:

			for value in tables:
				cursor.execute(value)

			for value in indexes:
				cursor.execute(value)

			conn.commit()

			result = self.executeSql(" select count(*) from scenario ")
		
			if int(result[0][0]) == 0:
				sql = """insert into scenario (code, name, cod_previous) values ('00A', 'Base Scenario', '')"""
				cursor.execute(sql)
				conn.commit()
			conn.close()
		except:
			return False
		conn.close()
		return True


	def insertBaseParameters(self, dataList):
		conn = self.connectionSqlite()
		sql = f"""select count(*) from project_files"""

		data = conn.execute(sql)
		result = data.fetchall()
		if result[0][0]>0:
			sql = f""" update project_files set zone_shape_file = '{dataList['zone_shape_file']}', zone_shape_file_id =  '{dataList['zone_shape_file_id']}', zone_shape_file_name = '{dataList['zone_shape_file_name']}',
				link_shape_file = '{dataList['link_shape_file']}', link_shape_file_origin = '{dataList['link_shape_file_origin']}', link_shape_file_destination = '{dataList['link_shape_file_destination']}', 
				link_shape_file_codscenario = '{dataList['link_shape_file_codscenario']}', link_shape_file_id = '{dataList['link_shape_file_id']}', link_shape_file_name = '{dataList['link_shape_file_name']}',
				link_shape_file_type = '{dataList['link_shape_file_type']}', link_shape_file_length = '{dataList['link_shape_file_length']}', link_shape_file_direction = '{dataList['link_shape_file_direction']}',
				link_shape_file_capacity = '{dataList['link_shape_file_capacity']}',
				node_shape_file = '{dataList['node_shape_file']}', node_shape_file_id = '{dataList['node_shape_file_id']}', 
				node_shape_file_name = '{dataList['node_shape_file_name']}', node_shape_file_type = '{dataList['node_shape_file_type']}', 
				node_shape_file_x = '{dataList['node_shape_file_x']}', node_shape_file_y = '{dataList['node_shape_file_y']}'"""
		else:
			sql = f""" insert into project_files (zone_shape_file, zone_shape_file_id, zone_shape_file_name, link_shape_file, 
				link_shape_file_codscenario, link_shape_file_origin, link_shape_file_destination, link_shape_file_id, link_shape_file_name, link_shape_file_type, link_shape_file_length, link_shape_file_direction, 
				link_shape_file_capacity, node_shape_file, node_shape_file_id, node_shape_file_name, node_shape_file_type,
				node_shape_file_x, node_shape_file_y) values (
				'{dataList['zone_shape_file']}','{dataList['zone_shape_file_id']}','{dataList['zone_shape_file_name']}',
				'{dataList['link_shape_file']}','{dataList['link_shape_file_codscenario']}','{dataList['link_shape_file_origin']}','{dataList['link_shape_file_destination']}','{dataList['link_shape_file_id']}',
				'{dataList['link_shape_file_name']}','{dataList['link_shape_file_type']}','{dataList['link_shape_file_length']}','{dataList['link_shape_file_direction']}',
				'{dataList['link_shape_file_capacity']}','{dataList['node_shape_file']}','{dataList['node_shape_file_id']}',
				'{dataList['node_shape_file_name']}','{dataList['node_shape_file_type']}','{dataList['node_shape_file_x']}', 
				'{dataList['node_shape_file_y']}')"""

		conn.execute(sql)
		conn.commit()
		conn.close()
		return True

	def findDemandSubsXSect(self, id_scenario, id_sector):
		conn = self.connectionSqlite()
		sql = f"""select id_input_sector, substitute 
					from inter_sector_inputs 
					where id_scenario = {id_scenario} and id_sector = {id_sector}
					and substitute != '' and substitute is not null
				"""
		
		data = conn.execute(sql)
		result = data.fetchall()
		resultString = ''
		for value in result:
			resultString += "  "+str(value[0])+"  "+Helpers.decimalFormat(str(value[1]))

		conn.close()
		return resultString


	def findRoutesRestrictedTurns(self, id_link, id_scenario):
		conn = self.connectionSqlite()
		sql = """select id_route from link_route
				where id_link = '{}' and id_scenario = {} and type_route = 2
				""".format(id_link, id_scenario)
		
		data = conn.execute(sql)
		result = data.fetchall()
		
		sql_restricted = f"""select 
					id_node
					from intersection_delay 
					where id_link = '{id_link}' and id_scenario = {id_scenario} and delay = -1"""
		data_res = conn.execute(sql_restricted)
		result_res = data_res.fetchall()
		conn.close()

		restricted_turn = "     ".join([str(val[0]) for val in result_res])+' /' if result_res else ' /'
		routes = "     ".join([str(value[0]) for value in result])+" 0  "+restricted_turn if result else "0  "+restricted_turn
		
		return routes
		
		

	def selectAllScenarios(self, codeScenario, columns='*', orderby='1 asc'):
		
		sql = """WITH RECURSIVE
		hierarchy_scenario(n) AS (
				VALUES('%s')
			UNION
				SELECT code FROM scenario, hierarchy_scenario
			 		WHERE scenario.cod_previous=hierarchy_scenario.n
		)
		SELECT * FROM scenario
		WHERE scenario.code IN hierarchy_scenario
		ORDER BY %s;""" % (codeScenario, orderby)

		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchall()
			conn.close()
			return result
		except Exception as e:
			return False


	def getScenarioId(self, codeScenario):
		"""Return the ID of a scenario given its code."""
		conn = self.connectionSqlite()
		try:
			cursor = conn.cursor()
			cursor.execute("select id from scenario where code = ?", (codeScenario,))
			row = cursor.fetchone()
			conn.close()
			return row[0] if row else None
		except Exception:
			conn.close()
			return None

	
	def deleteExtraLinks(self, dataArray):
		""" Delete extra links not in the shape file from the database."""
		conn = self.connectionSqlite()

		sql_delete = """ delete from link where id_scenario = ? and linkid = ? """

		try:
			cursor = conn.cursor()
			cursor.executemany(sql_delete, dataArray)
			print(f"Rows affected (executemany): {cursor.rowcount}")
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Error deleting extra links: {e}")
			conn.close()
			return False


	def replaceScenarioCode(self, data_array):
		""" Replace scenario code with scenario ID in the given data array."""
		data_array_new = []
		for data in data_array:
			data_new = list(data)
			data_new[0] = self.getScenarioId(data_new[0])
			data_array_new.append(tuple(data_new))
		return data_array_new


	def validateConnection(self):
		try:
			self.dataBaseStructure(self.conn)
			return True
		except:
			return False


	def previousScenario(self,id_scenario):
		conn = self.connectionSqlite()
		sql = """with base as (
			select cod_previous
			from scenario where id = %s
			)
			select id 
			from scenario 
			where code = (select base.cod_previous from base)""" % (id_scenario)

		data = conn.execute(sql)
		result = data.fetchall()
		conn.close()
		return result


	def findTransfer(self, id_operator_from, id_operator_to, id_scenario):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		qry = """select cost 
				  from transfer_operator_cost 
				  where id_operator_from = {0} 
				  and id_operator_to = {1} 
				  and id_scenario = {2}""".format(id_operator_from, id_operator_to, id_scenario)

		data = cursor.execute(qry)
		result = data.fetchall()
		conn.commit()
		conn.close()
		return result


	def findLinkTypeOperator(self, id_scenario, id_linktype, id_operator):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		
		qry = """
			select id_operator, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost
			from link_type_operator
			where id_scenario = {0} and id_linktype = {1} and id_operator = {2}
			""".format(id_scenario, id_linktype, id_operator)

		data = cursor.execute(qry)
		result = data.fetchall()
		conn.commit()
		conn.close()
		return result
			
	def syncTransfers(self, scenarios):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		data_arr = []
		for id_scenario in scenarios:
			sql = """with id_from as (
					select 
					id_scenario, id
					from 
					operator
					where id_scenario = {0}
				),
				id_to as (
					select 
					id, basics_boarding_tariff tariff_to
					from 
					operator
					where id_scenario = {0}
				)
				select a.id_scenario, a.id id_from, b.id id_to, b.tariff_to 
				from id_from a, id_to b
				where id_scenario = {0}""".format(id_scenario[0])
				
			result_data = self.executeSql(sql)

			for values in result_data:
				data_arr.append((values[0], values[1], values[2], values[3]))

		sql = f"""INSERT OR REPLACE INTO  transfer_operator_cost (id_scenario, id_operator_from, id_operator_to, cost) 
			VALUES (?, ?, ?, ?)"""

		# cursor.executemany(sql, data_arr)
		# conn.commit()			
		conn.close()

		return True


	def syncScenariosDB(self, id_scenario, cod_previous):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []
		sql_arr_cat = []
		sql_arr_ope = []
		sql_arr_ope_cat = []
		sql_arr_cost = []
		sql_arr_route = []
		sql_arr_node = []
		sql_arr_linktype = []
		sql_arr_linktype_ope = []
		sql_arr_link = []
		sql_arr_exotrip = []
		sql_arr_sector = []
		sql_arr_intersector = []
		sql_arr_intersector_cat = []
		sql_arr_zonal_data = []

		result = self.selectAll(" scenario ", where=" where code = '{}'".format(cod_previous))
		if result:
			data_list = self.selectAll(" administrator ", where=f" where id_scenario = {result[0][0]}")
			data_cat = self.selectAll(" category ", where=f" where id_scenario = {result[0][0]}")
			data_ope = self.selectAll(" operator ", where=f" where id_scenario = {result[0][0]}")
			data_ope_cat = self.selectAll(" operator_category ", columns=" id_scenario, id_operator, id_category, tariff_factor, penal_factor ", where=f" where id_scenario = {result[0][0]}")
			data_cost = self.selectAll(" transfer_operator_cost ", columns=" id_scenario, id_operator_from, id_operator_to, cost ", where=f" where id_scenario = {result[0][0]}")
			data_route = self.selectAll(" route ", columns="id, id_scenario, name, description, id_operator, frequency_from, frequency_to, target_occ, max_fleet, used, follows_schedule",  where=f" where id_scenario = {result[0][0]}")
			data_node = self.selectAll(" node ", where=f" where id_scenario = {result[0][0]}")
			data_linktype = self.selectAll(" link_type ", where=f" where id_scenario = {result[0][0]}")
			data_linktype_ope = self.selectAll(" link_type_operator ", columns=" id_scenario, id_linktype, id_operator, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost ", where=f" where id_scenario = {result[0][0]}")
			data_link = self.selectAll(" link ", columns=" linkid,  id_scenario, id_linktype, two_way, used_in_scenario, node_from, node_to, name, description, length, capacity, delay ", where=f" where id_scenario = {result[0][0]}")
			data_exotrip = self.selectAll(" exogenous_trips ", columns="id_scenario,  id_zone_from,  id_zone_to, id_mode,  id_category, trip, factor ", where=f" where id_scenario = {result[0][0]}")
			data_sector = self.selectAll(" sector ", where=f" where id_scenario = {result[0][0]}")
			data_intersector = self.selectAll(" inter_sector_inputs ", columns=" id_scenario, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors ", where=f" where id_scenario = {result[0][0]}")
			data_intersector_cat = self.selectAll(" inter_sector_transport_cat ", columns=" id_scenario, id_sector, id_category, type, time_factor, volume_factor, flow_to_product, flow_to_consumer ", where=f" where id_scenario = {result[0][0]}")
			data_zonal_data = self.selectAll(" zonal_data ", columns=" id_scenario, id_sector, id_zone, exogenous_production, induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor, max_imports, min_imports, exports ", where=f" where id_scenario = {result[0][0]}")
		else:
			result_scenario = self.executeSql("select min(id) from scenario")
			data_list = self.selectAll(" administrator ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_ope = self.selectAll(" operator ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_ope_cat = self.selectAll(" operator_category ", columns=" id_scenario, id_operator, id_category, tariff_factor, penal_factor ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_cat = self.selectAll(" category ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_cost = self.selectAll(" transfer_operator_cost ", columns=" id_scenario, id_operator_from, id_operator_to, cost ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_route = self.selectAll(" route ", columns="id, id_scenario, name, description, id_operator, frequency_from, frequency_to, target_occ, max_fleet, used, follows_schedule", where=f" where id_scenario = {result_scenario[0][0]}")
			data_node = self.selectAll(" node ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_linktype = self.selectAll(" link_type ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_linktype_ope = self.selectAll(" link_type_operator ", columns=" id_scenario, id_linktype, id_operator, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_link = self.selectAll(" link ", columns=" linkid,  id_scenario, id_linktype, two_way, used_in_scenario, node_from, node_to, name, description, length, capacity, delay ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_exotrip = self.selectAll(" exogenous_trips ", columns=" id_scenario,  id_zone_from,  id_zone_to, id_mode,  id_category, trip, factor ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_sector = self.selectAll(" sector ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_intersector = self.selectAll(" inter_sector_inputs ", columns=" id_scenario, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_intersector_cat = self.selectAll(" inter_sector_transport_cat ", columns=" id_scenario, id_sector, id_category, type, time_factor, volume_factor, flow_to_product, flow_to_consumer ", where=f" where id_scenario = {result_scenario[0][0]}")
			data_zonal_data = self.selectAll(" zonal_data ", columns=" id_scenario, id_sector, id_zone, exogenous_production, induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor, max_imports, min_imports, exports ", where=f" where id_scenario = {result_scenario[0][0]}")

		sql = f"""INSERT OR REPLACE INTO  administrator (id, id_scenario, name, description) 
			VALUES (?, ?, ?, ?)"""

		sql_cat = f"""INSERT OR REPLACE INTO  category (id, id_scenario, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_ope = f"""INSERT OR REPLACE INTO  operator (id, id_scenario, name, description, id_mode, type, basics_modal_constant, basics_occupency, basics_time_factor, basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, energy_min, energy_max, energy_slope, energy_cost, cost_time_operation, cost_porc_paid_by_user, stops_min_stop_time, stops_unit_boarding_time, stops_unit_alight_time, color) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_ope_cat = f"""INSERT OR REPLACE INTO  operator_category ( id_scenario, id_operator, id_category, tariff_factor, penal_factor ) 
			VALUES (?, ?, ?, ?, ?)"""
		
		sql_cost = f"""INSERT OR REPLACE INTO  transfer_operator_cost (id_scenario, id_operator_from, id_operator_to, cost) 
			VALUES (?, ?, ?, ?)"""

		sql_route = f"""INSERT OR REPLACE INTO  route (id, id_scenario, name, description, id_operator, frequency_from, frequency_to, target_occ, max_fleet, used, follows_schedule) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_node = f"""INSERT OR REPLACE INTO  node (id, id_scenario, id_type,  name,  description,  x, y) 
			VALUES (?, ?, ?, ?, ?, ?, ?)"""

		sql_linktype = f"""INSERT OR REPLACE INTO  link_type (id, id_scenario, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_linktype_ope = f"""INSERT OR REPLACE INTO  link_type_operator ( id_scenario, id_linktype, id_operator, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_link = f"""INSERT OR REPLACE INTO  link ( linkid,  id_scenario, id_linktype, two_way, used_in_scenario, node_from, node_to, name, description, length, capacity, delay ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_exotrip = f"""INSERT OR REPLACE INTO  exogenous_trips ( id_scenario,  id_zone_from,  id_zone_to, id_mode,  id_category, trip, factor ) 
			VALUES (?, ?, ?, ?, ?, ?, ?)"""

		sql_sector = f"""INSERT OR REPLACE INTO  sector ( id, id_scenario, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, substitute ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_intersector = f"""INSERT OR REPLACE INTO  inter_sector_inputs ( id_scenario, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_intersector_cat = f"""INSERT OR REPLACE INTO  inter_sector_transport_cat ( id_scenario, id_sector, id_category, type, time_factor, volume_factor, flow_to_product, flow_to_consumer ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_zonal_data = f"""INSERT OR REPLACE INTO  zonal_data ( id_scenario, id_sector, id_zone, exogenous_production, induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor, max_imports, min_imports, exports ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		for row in data_list:
			sql_arr.append((row[0], id_scenario, row[2], row[3]))

		for row in data_cat:
			sql_arr_cat.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

		for row in data_ope:
			sql_arr_ope.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[15], row[17], row[18], row[19], row[20], row[21], row[22]))
		
		for row in data_ope_cat:
			sql_arr_ope_cat.append((id_scenario, row[1], row[2], row[3], row[4]))
		
		for row in data_cost:
			sql_arr_cost.append((id_scenario, row[1], row[2], row[3]))

		for row in data_route:
			sql_arr_route.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
		
		for row in data_node:
			sql_arr_node.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6]))

		for row in data_linktype:
			sql_arr_linktype.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
		
		for row in data_linktype_ope:
			sql_arr_linktype_ope.append((id_scenario, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
		
		for row in data_link:
			sql_arr_link.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))

		for row in data_exotrip:
			sql_arr_exotrip.append((id_scenario, row[1], row[2], row[3], row[4], row[5], row[6]))

		for row in data_sector:
			sql_arr_sector.append((row[0], id_scenario, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
		
		for row in data_intersector:
			sql_arr_intersector.append((id_scenario, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
	
		for row in data_intersector_cat:
			sql_arr_intersector_cat.append((id_scenario, row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
		
		for row in data_zonal_data:
			sql_arr_zonal_data.append((id_scenario, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
		try:
			cursor.executemany(sql, sql_arr)
			cursor.executemany(sql_cat, sql_arr_cat)
			cursor.executemany(sql_ope, sql_arr_ope)
			cursor.executemany(sql_ope_cat, sql_arr_ope_cat)
			cursor.executemany(sql_cost, sql_arr_cost)
			cursor.executemany(sql_route, sql_arr_route)
			cursor.executemany(sql_node, sql_arr_node)
			cursor.executemany(sql_linktype, sql_arr_linktype)
			cursor.executemany(sql_linktype_ope, sql_arr_linktype_ope)
			cursor.executemany(sql_link, sql_arr_link)
			cursor.executemany(sql_exotrip, sql_arr_exotrip)
			cursor.executemany(sql_sector, sql_arr_sector)
			cursor.executemany(sql_intersector, sql_arr_intersector)
			cursor.executemany(sql_intersector_cat, sql_arr_intersector_cat)
			cursor.executemany(sql_zonal_data, sql_arr_zonal_data)
			conn.commit()			
			conn.close()
			return True
		except Exception as e:
			print(e)
			conn.commit()			
			conn.close()
			return False


	def ifExist(self, table, field, code):
		sql = """select * from {} where {} = '{}'""".format(table, field, code)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		data = cursor.execute(sql)
		result = data.fetchall()
		conn.commit()
		conn.close()
		if len(result) > 0:
			return True
		else: 
			return False

	def addExogenousData(self, scenarios, id_zone_from, id_zone_to, id_category, column=None, value=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for valor in scenarios:
			sql = "insert into exogenous_trips \
				(id_scenario, id_zone_from, id_zone_to, id_category, {4}) \
				values ({0},{1},{2},{3},{5});".format(valor[0], id_zone_from, id_zone_to, id_category, column, value)
		
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True

	
	def add_route_link(self, scenarios, links_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = """INSERT OR REPLACE INTO  link_route (id_scenario, id_link, id_route, type_route) 
			VALUES (?, ?, ?, ?)"""
		sql_arr = []

		for id_scenario in scenarios:		
			for link in links_list:
				sql_arr.append((id_scenario[0], link[0], link[1], link[2]))

		cursor.executemany(sql, sql_arr)
		conn.commit()			
		conn.close()
		return True


	def add_linktype_link(self, scenarios, linktypes_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = """ update link set id_linktype = ?
				where id_scenario = ? and linkid = ? """
		sql_arr = []
		
		for id_scenario in scenarios:		
			for link in linktypes_list:
				sql_arr.append((int(link[1]), id_scenario[0], link[0]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()			
		conn.close()
		return True
	
	def remove_route_link(self, scenarios, links_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for scenario in scenarios:
			for link in links_list:
				sql = f"""delete from link_route 
					where id_scenario = {scenario[0]} and id_route = {link[1]} and id_link = '{link[0]}'"""
				cursor.execute(sql)
				conn.commit()
		
		conn.close()
		return True
		

	def addLinkFDialog(self, scenarios, id_origin, id_destination, id_linktype, name, description, two_way, used_in_scenario, length, capacity, delay, id_routes_arr_selected, turns_delays_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		two_way = 1 if two_way else 'null'
		used_in_scenario = 1 if used_in_scenario else 'null'
		columns = ''
		values = ''
		if name:
			columns += ", name"
			values +=  f", '{name}'"
		if description:
			columns += ", description"
			values +=  f", '{description}'"
		if delay:
			columns += ", delay"
			values +=  f", {delay}"

		for id_scenario in scenarios:
			if two_way:
				sql = f"""insert into link (id_scenario, linkid, id_linktype,
			        	two_way, used_in_scenario, node_from, node_to, length, capacity {columns}) 
			        	values ({id_scenario[0]}, '{id_origin}-{id_destination}', {id_linktype}, {two_way}, {used_in_scenario},
			        	{id_origin}, {id_destination}, {length}, {capacity} {values})"""
				cursor.execute(sql)
				conn.commit()    

				result = self.selectAll(' link ', where= f" where linkid='{id_destination}-{id_origin}' and id_scenario = {id_scenario[0]}" )

				if not result:
					sql = f"""insert into link (id_scenario, linkid, id_linktype,
				        	two_way, used_in_scenario, node_from, node_to, length, capacity {columns}) 
				        	values ({id_scenario[0]}, '{id_destination}-{id_origin}', {id_linktype}, {two_way}, {used_in_scenario},
				        	{id_destination}, {id_origin}, {length}, {capacity} {values})"""
					cursor.execute(sql)
					conn.commit()    
			else:
				sql = f"""insert into link (id_scenario, linkid, id_linktype,
			        	two_way, used_in_scenario, node_from, node_to, length, capacity {columns}) 
			        	values ({id_scenario[0]}, '{id_origin}-{id_destination}', {id_linktype}, {two_way}, {used_in_scenario},
			        	{id_origin}, {id_destination}, {length}, {capacity} {values})"""

				cursor.execute(sql)
				conn.commit()

		for id_scenario in scenarios:
			for id_route in id_routes_arr_selected:
				sql = f"""insert into  link_route (id_scenario, id_link, id_route, type_route) 
					values ({id_scenario[0]}, '{id_origin}-{id_destination}', {int(id_route[0])}, {int(id_route[1])})"""
				cursor.execute(sql)
				conn.commit()	

			for turn in turns_delays_arr:
				if turn[1]:
					sql = f"""insert into intersection_delay (id_scenario, id_link, id_node, delay) 
						values ({id_scenario[0]}, '{id_origin}-{id_destination}', {turn[0]}, {turn[1]})"""
					
					cursor.execute(sql)
					conn.commit()
		
		conn.close()
		return True


	def addLinkRouteFFile(self, scenarios, data_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr = []
		sql = f"""INSERT OR REPLACE INTO  link_route (id_scenario, id_link, id_route, type_route) 
			VALUES (?,?,?,?)"""
		for row in data_list:
			for id_scenario in scenarios:
				sql_arr.append((id_scenario[0], row[0], row[1], row[2]))
		cursor.executemany(sql, sql_arr)
		conn.commit()			
		conn.close()
		return True


	def addLinkIntersectioDelayFFile(self, scenarios, data_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr = []
		sql = f"""INSERT OR REPLACE INTO  intersection_delay (id_scenario, id_link, id_node, delay) 
			VALUES (?,?,?,?)"""
		for row in data_list:
			for id_scenario in scenarios:
				sql_arr.append((id_scenario[0], row[0], row[1], row[2]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()			
		conn.close()
		return True


	def updateLinkFDialog(self, scenarios, id_origin, id_destination, id_linktype, name, description, two_way, used_in_scenario, length, capacity, delay, id_routes_arr_selected, turns_delays_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns_values = ''
		used_in_scenario = 1 if used_in_scenario else 'null'
		two_way = 1 if two_way else 'null'

		if name:
			columns_values += f", name = '{name}'"
		if description:
			columns_values += f", description = '{description}'"
		if delay:
			columns_values += f', delay = {delay}'

		for id_scenario in scenarios:
			sql = f"""update link set id_linktype = {id_linktype}, two_way = {two_way}, 
					 used_in_scenario = {used_in_scenario}, length = {length}, capacity = {capacity} {columns_values}
					 where linkid = '{id_origin}-{id_destination}' and id_scenario = {id_scenario[0]}"""
			cursor.execute(sql)
			conn.commit()
			
			if two_way:
				result = self.selectAll(" link ", where = f" where linkid = '{id_destination}-{id_origin}' ")
				if not result:
					self.addLinkFDialog(scenarios, id_destination, id_origin, id_linktype, name, description, two_way, used_in_scenario, length, capacity, delay, id_routes_arr_selected, turns_delays_arr)

				sql = f"""update link  set id_linktype = {id_linktype}, two_way = {two_way}, 
					length = {length}, capacity = {capacity}, used_in_scenario = {used_in_scenario}
					where linkid = '{id_destination}-{id_origin}' and id_scenario = {id_scenario[0]}"""
				cursor.execute(sql)
				conn.commit()
				
			elif two_way == 'null':
				sql = f"""update link  set two_way = null
					where linkid = '{id_destination}-{id_origin}' and id_scenario = {id_scenario[0]}"""
				
				cursor.execute(sql)
				conn.commit()

		if id_routes_arr_selected:
			for id_scenario in scenarios:
				# Update or Insert Routes
				for id_route in id_routes_arr_selected:
					result = self.selectAll(' link_route ', 
						where=f""" where id_scenario={id_scenario[0]} and id_link='{id_origin}-{id_destination}' and id_route={int(id_route[0])}""")

					if result:
						sql = f"""update link_route set type_route = {int(id_route[1])} where id_scenario = {id_scenario[0]} and id_link = '{id_origin}-{id_destination}' and id_route = {int(id_route[0])}"""
					else:
						sql = f"""insert into link_route (id_scenario, id_link, id_route, type_route) values ({id_scenario[0]}, '{id_origin}-{id_destination}', {int(id_route[0])}, {int(id_route[1])})"""
					
					cursor.execute(sql)
					conn.commit()


		if turns_delays_arr:
			for id_scenario in scenarios:
				for turn in turns_delays_arr:
					if turn[1]:
						result = self.selectAll(' intersection_delay ', 
							where=f""" where id_scenario={id_scenario[0]} and id_link='{id_origin}-{id_destination}' and id_node={int(turn[0])}""")
						if result:
							sql = f""" update intersection_delay set delay = {turn[1]} where id_scenario={id_scenario[0]} and id_link='{id_origin}-{id_destination}' and id_node={turn[0]} """
							cursor.execute(sql)
							conn.commit()
						else:
							sql = f""" insert into intersection_delay (id_scenario, id_link, id_node, delay) values ({id_scenario[0]}, '{id_origin}-{id_destination}', {turn[0]},  {turn[1]}) """
							cursor.execute(sql)
							conn.commit()

		return True
						

	def updateLinkFShape(self, scenarios, linkId, column, value):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns_values = ''

		for id_scenario in scenarios:
			sql = f"""update link set {column}='{value}'
					 where linkid = '{linkId}' and id_scenario = {id_scenario[0]}"""

			cursor.execute(sql)
			conn.commit()


	def removeLink(self, scenarios, linkid):

		linkid_b = f'{linkid.split("-")[1]}-{linkid.split("-")[0]}'
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		for scenario in scenarios:
			sql = f""" delete from link where linkid in ('{linkid}', '{linkid_b}') and id_scenario = {scenario[0]}"""
			cursor.execute(sql)
			conn.commit()

		for scenario in scenarios:
			sql = f""" delete from link_route where id_link in ('{linkid}', '{linkid_b}') and id_scenario = {scenario[0]}"""
			cursor.execute(sql)
			conn.commit()

		for scenario in scenarios:
			sql = f""" delete from intersection_delay where id_link in ('{linkid}', '{linkid_b}') and id_scenario = {scenario[0]}"""
			cursor.execute(sql)
			conn.commit()
		return True


	def deleteRouteFLink(self, scenarios, id_link, route):
		conn = self.connectionSqlite()
		cursor = conn.cursor()


		for scenario in scenarios:
			sql = """delete from link_route where id_link = '{0}'
				and id_scenario = {1} and id_route = {2};""".format(id_link, scenario[0], route)
			
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True


	def updateExogenousData(self, id_scenario, id_zone_from, id_zone_to, id_category, column=None, value=None):
		
		if value !='':
			sql = """
				update exogenous_trips set {4}={5}
				where id_scenario={0} and id_zone_from={1} and id_zone_to={2} and id_category={3} ;
				""".format(id_scenario, id_zone_from, id_zone_to, id_category, column, value)
		else: 
			sql = """
				delete from exogenous_trips
				where id_scenario={0} and id_zone_from={1} and id_zone_to={2} and id_category={3} ;
				""".format(id_scenario, id_zone_from, id_zone_to, id_category)	

		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False


	def bulkLoadExogenousTrips(self, scenarios, data_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr_trips = []

		sql_exogenous = f"""INSERT OR REPLACE INTO exogenous_trips ( id_scenario, id_zone_from, id_zone_to, id_category, trip) 
			VALUES (?, ?, ?, ?, ?)"""
		
		for id_scenario in scenarios:
			for row in data_arr:
				sql_arr_trips.append((id_scenario[0], row[0], row[1], row[2], row[3]))

		cursor.executemany(sql_exogenous, sql_arr_trips)
		conn.commit()			
		conn.close()



	def addScenario(self, code, name, cod_previous=''):
		if self.ifExist('scenario', 'code', code):
			return False
		else:
			sql = "insert into scenario (code, name, cod_previous) values ('{}','{}','{}');".format(code, name, cod_previous)
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True


	def addLinkType(self, scenarios, id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = """insert into link_type (id_scenario, id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology)
			 values ({}, {},'{}','{}',{},{},{},{},{},{},"{}");""".format(id_scenario[0], id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology)
			cursor.execute(sql)
			conn.commit()
		conn.close()
		
		return True


	def updateLinkType(self, scenarios, id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = """update link_type set name='{}', description='{}', id_administrator={}, capacity_factor={}, min_maintenance_cost={}, perc_speed_reduction_vc={}, perc_max_speed_reduction={}, vc_max_reduction={}, symbology="{}"
		 	where id = {} and id_scenario = {};""".format(name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, symbology, id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()
		conn.close()
		
		return True


	def updateLinkTypeOperator(self, scenarios, id_linktype, id_operator, column=None, value=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for scenarios in id_scenario:
			sql = """update link_type_operator set {0} = {1} where id_linktype = {2} and id_operator = {3} and id_scenario = {4};""".format(column, value, id_linktype, id_operator, id_scenario);
			
			cursor.execute(sql)
			conn.commit()

		conn.close()
		
		return True


	def addLinkTypeOperatorInsertUpdate(self, scenarios,  operator_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr_operator = []

		sql_linktype_ope = f"""INSERT OR REPLACE INTO  link_type_operator ( id_scenario, id_linktype, id_operator, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost ) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
 		
		for id_scenario in scenarios:
			for row in operator_arr:
				sql_arr_operator.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

		cursor.executemany(sql_linktype_ope, sql_arr_operator)

		conn.commit()			
		conn.close()
		return True


	def removeLinkType(self, scenarios, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = """delete from link_type where id_scenario = {} and  id = {};""".format(id_scenario[0], id)
			cursor.execute(sql)
			conn.commit()

			sql = """delete from link_type_operator where id_scenario = {} and id_linktype = {};""".format(id_scenario[0], id)
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True


	def addRoute(self, scenarios, id, name, description, id_operator, frequency_from, frequency_to, max_fleet, color, used=None, follows_schedule=None):
		#try:
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		try:
			for id_scenario in scenarios:
				sql = """insert into route (id, id_scenario, name, description, id_operator, frequency_from, frequency_to, max_fleet, used, follows_schedule, color)
			 	values ({},{},'{}','{}',{},{},{},{},{},{},{});""".format(id, id_scenario[0], name, description, id_operator, frequency_from, frequency_to, max_fleet, used, follows_schedule, color)
				
				cursor.execute(sql)
				conn.commit()

			conn.close()
			return True
		except:
			return False


	def addFFileRoute(self, scenarios, data_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr = []
		for row in data_list:
			for id_scenario in scenarios:
				sql = """INSERT OR REPLACE INTO route (id_scenario, id, name, description, id_operator, frequency_from, frequency_to, target_occ, max_fleet, follows_schedule)
		 		VALUES (?,?,?,?,?,?,?,?,?,?);"""
				sql_arr.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
		
		cursor.executemany(sql, sql_arr)

		conn.commit()
		conn.close()
		return True
		

	def updateRoute(self, scenarios, id, name, description, id_operator, frequency_from, frequency_to, max_fleet, color, used=None, follows_schedule=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = """update route set name='{}', description='{}', id_operator={}, frequency_from={}, frequency_to={}, max_fleet={},  used={}, follows_schedule={}, color={}
				where id={} and id_scenario = {}""".format(name, description, id_operator, frequency_from, frequency_to, max_fleet, used, follows_schedule, color, id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True


	def removeRoute(self, scenarios, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:

			sql = """delete from route where id = {} and id_scenario = {};""".format(id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True


	def addZone(self, id, name, external=None, internal_cost_factor=None):
		if external is None and internal_cost_factor is None:
			sql = "insert into zone (id, name) values ({},'{}');".format(id, name)
		elif external==0:
			sql = "insert into zone (id, name, external, internal_cost_factor) values ({},'{}',{},{});".format(id, name, external, internal_cost_factor)
		else:
			sql = "insert into zone (id, name, external) values ({},'{}',{});".format(id, name, 1)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True	


	def addZoneFFShape(self, data_list, typeSql='IGNORE'):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []
		sql = """INSERT OR """+str(typeSql)+""" INTO zone (id, name) 
			values (?, ?);"""
		for row in data_list:
			sql_arr.append((row[0], row[1]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True


	def addLink(self, scenarios, linkid, node_from, node_to):
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		for id_scenario in scenarios:
			sql = "insert into link (id_scenario, linkid, node_from, node_to) values ({},'{}',{},{});".format(id_scenario[0], linkid, node_from, node_to)
		
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True


	def addFFileLink(self, scenarios, data_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []
		sql = """INSERT OR REPLACE INTO link (id_scenario, linkid, node_from, node_to, id_linktype, length, capacity, name, description) 
			values (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

		for row in data_list:
			for id_scenario in scenarios:
				sql_arr.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True


	def addLinkFFShape(self, scenarios, data_list, typeSql='IGNORE'):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []

		sql = """INSERT OR """+str(typeSql)+""" INTO link (id_scenario, linkid, node_from, node_to, id_linktype, length, two_way, capacity, name) 
			values (?, ?, ?, ?, ?, ?, ?, ?, ?);"""


		if typeSql=='REPLACE':
			sql = """INSERT OR """+str(typeSql)+""" INTO link (id_scenario, linkid, node_from, node_to, id_linktype, length, two_way, capacity, name, used_in_scenario) 
				values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

		for row in data_list:
			scenarios = self.selectAllScenarios(row[0], columns='id')
			
			for id_scenario in scenarios:
				if typeSql=='REPLACE':
					sql_arr.append((int(id_scenario[0]), str(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], row[8], 1))
				else:
					sql_arr.append((int(id_scenario[0]), str(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], str(row[8])))
		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True

	
	def addLinkFShapeFile(self, scenarios, data_list, typeSql='IGNORE'):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []

		sql = """INSERT OR """+str(typeSql)+""" INTO link (id_scenario, linkid, node_from, node_to, id_linktype, length, two_way, capacity, name) 
			values (?, ?, ?, ?, ?, ?, ?, ?, ?);"""


		if typeSql=='REPLACE':
			sql = """INSERT OR """+str(typeSql)+""" INTO link (id_scenario, linkid, node_from, node_to, id_linktype, length, two_way, capacity, name, used_in_scenario) 
				values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

		for row in data_list:
			if typeSql=='REPLACE':
				sql_arr.append((int(row[0]), str(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], row[8], 1))
			else:
				sql_arr.append((int(row[0]), str(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], str(row[8])))


		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True


	def truncateLinkTable(self):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "delete from link;"

		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def addNode(self, scenarios, _id, id_type, name, description, x, y):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()

			column = 'id'
			value = "%s " % _id
			
			if id_type:
				column += ", id_type"
				value += ", %s" % id_type
			if name:
				column += ", name"
				value += ", '%s'" % name
			if description:
				column += ", description"
				value += ", '%s'" % description
			if x:
				column += ", x"
				value += ", %s" % x
			if y:
				column += ", y"
				value += ", %s" % y

			for id_scenario in scenarios:
				sql = "insert into node ({}, id_scenario) values ({}, {});".format(column, value, id_scenario[0])
				cursor.execute(sql)
				conn.commit()

			conn.close()
			return True
		except Exception as e:
			return False
		


	def addNodeFShape(self, scenarios, data_list, typeSql="IGNORE"):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []

		sql = """INSERT OR """+str(typeSql)+""" INTO node (id_scenario, id, x, y, name, description, id_type) 
			values (?, ?, ?, ?, ?, ?, ?);"""
		
		for row in data_list:
			for id_scenario in scenarios:
				sql_arr.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True
		

	def addFFileNode(self, scenarios, data_list):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr = []

		sql = """INSERT OR REPLACE INTO node (id_scenario, id, x, y, id_type, name, description) 
			values (?, ?, ?, ?, ?, ?, ?);"""

		for row in data_list:
			for id_scenario in scenarios:
				sql_arr.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5]))
		
		cursor.executemany(sql, sql_arr)
		conn.commit()
		conn.close()
		return True

	def updateNode(self, scenarios, _id, id_type, name, description, x, y):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		column = 'id'
		value = "%s " % _id
		update = '' 

		update += ", name = '%s'" % name if name != '' else ", name = null"
		update += ", description = '%s'" % description if description != '' else ", description = null"

		if id_type:
			update += ', id_type = %s' % (id_type if id_type != '0' else 'null')
		if x:
			update += ', x = %s' % (x if x != '0' else 'null')
		if y:
			update += ', y = %s' % (y if y != '0' else 'null')

		for id_scenario in scenarios:
			sql = """update node set id = {0} {1}
					where id = {0} and id_scenario = {2}
					""".format(_id, update, id_scenario[0])
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True


	def removeNode(self, scenarios, _id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		
		for id_scenario in scenarios:
			sql = "delete from node where id={} and id_scenario = {};".format(_id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True


	def updateZone(self, id, name, external, internal_cost_factor):
		if external==1:
			sql = "update zone set name='{1}', external={2}, internal_cost_factor=NULL where id={0}; ".format(id, name, external)
		else:
			sql = "update zone set name='{1}', external={2}, internal_cost_factor={3} where id={0}; ".format(id, name, external, internal_cost_factor)
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True	


	def removeZone(self, id):
		
		sql = "delete from zone where id = '{}';".format(id)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()

		sql = "delete from zone where id = '{}';".format(id)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()

		sql = f"""delete from exogenous_trips where id_zone_from = '{id}' or id_zone_to = '{id}';"""
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()

		conn.close()
		return True	

	def addOperator(self, data):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		scenarios = data['scenarios']

		_id = int(data['id'])
		_name = data['name']
		_description = data['description']
		_id_mode = int(data['id_mode'])
		_type = data['type']
		basics_modal_constant = float(data['basics_modal_constant'])
		basics_occupency = float(data['basics_occupency'])
		basics_time_factor = float(data['basics_time_factor'])
		basics_fixed_wating_factor = float(data['basics_fixed_wating_factor'])
		basics_boarding_tariff = float(data['basics_boarding_tariff'])
		basics_distance_tariff = float(data['basics_distance_tariff'])
		basics_time_tariff = float(data['basics_time_tariff'])
		energy_min =   float(data['energy_min']    )
		energy_max = float(data['energy_max'] )
		energy_slope = float(data['energy_slope'])
		energy_cost = float(data['energy_cost'])
		cost_time_operation = float(data['cost_time_operation'])
		cost_porc_paid_by_user = float(data['cost_porc_paid_by_user'])
		stops_min_stop_time = float(data['stops_min_stop_time'])
		stops_unit_boarding_time = float(data['stops_unit_boarding_time'])
		stops_unit_alight_time = float(data['stops_unit_alight_time'])
		color = int(data['color'])

		for id_scenario in scenarios:
			sql = "insert into operator (id_scenario, id, name, description, id_mode, type, \
				   basics_modal_constant, basics_time_factor, basics_occupency, \
				   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, \
				   energy_min, energy_max, energy_slope, energy_cost, \
				   cost_time_operation, cost_porc_paid_by_user,\
				   stops_min_stop_time, stops_unit_boarding_time, \
				   stops_unit_alight_time, color) values ({},{},'{}','{}',{},'{}',\
				   {},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{});".format(id_scenario[0], _id, _name, _description, _id_mode, _type,
				   basics_modal_constant, basics_time_factor, basics_occupency,
				   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, 
				   energy_min, energy_max, energy_slope, energy_cost, 
				   cost_time_operation, cost_porc_paid_by_user, stops_min_stop_time, 
				   stops_unit_boarding_time, stops_unit_alight_time, color)

			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True


	def updateOperator(self, data):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		scenarios = data['scenarios']

		_id = int(data['id'])
		_name = data['name']
		_description = data['description']
		_id_mode = data['id_mode']
		_type = data['type']
		basics_modal_constant = float(data['basics_modal_constant'])
		basics_occupency = float(data['basics_occupency'])
		basics_time_factor = float(data['basics_time_factor'])
		basics_fixed_wating_factor = float(data['basics_fixed_wating_factor'])
		basics_boarding_tariff = float(data['basics_boarding_tariff'])
		basics_distance_tariff = float(data['basics_distance_tariff'])
		basics_time_tariff = float(data['basics_time_tariff'])
		energy_min =   float(data['energy_min']    )
		energy_max = float(data['energy_max'] )
		energy_slope = float(data['energy_slope'])
		energy_cost = float(data['energy_cost'])
		cost_time_operation = float(data['cost_time_operation'])
		cost_porc_paid_by_user = float(data['cost_porc_paid_by_user'])
		stops_min_stop_time = float(data['stops_min_stop_time'])
		stops_unit_boarding_time = float(data['stops_unit_boarding_time'])
		stops_unit_alight_time = float(data['stops_unit_alight_time'])
		color = float(data['color'])

		for id_scenario in scenarios:
			sql = """update operator set name='{}', description='{}', id_mode={}, type='{}', 
				   basics_modal_constant={}, basics_time_factor={}, basics_occupency={}, 
				   basics_fixed_wating_factor={}, basics_boarding_tariff={}, basics_distance_tariff={}, basics_time_tariff={}, 
				   energy_min={}, energy_max={}, energy_slope={}, energy_cost={}, 
				   cost_time_operation={}, cost_porc_paid_by_user={},
				   stops_min_stop_time={}, stops_unit_boarding_time={}, 
				   stops_unit_alight_time={}, color={} where id = {} and id_scenario = {};""".format(_name, _description, _id_mode, _type,
				   basics_modal_constant, basics_time_factor, basics_occupency,
				   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, 
				   energy_min, energy_max, energy_slope, energy_cost, 
				   cost_time_operation, cost_porc_paid_by_user, stops_min_stop_time, 
				   stops_unit_boarding_time, stops_unit_alight_time, color, _id, id_scenario[0])
			
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True

			
	def addOperatorCategory(self, scenarios, id_operator, id_category, tariff_factor, penal_factor):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		if (tariff_factor != '' or penal_factor != ''):
			for id_scenario in scenarios:
				sql = """insert into operator_category 
					(id_scenario, id_operator, id_category, tariff_factor, penal_factor ) 
					values ({0},{1},{2},{3},{4});""".format(id_scenario[0], id_operator, id_category, tariff_factor, penal_factor)
				cursor.execute(sql)
				conn.commit()

		conn.close()
		return True
		

	def operatorCategoryInsertUpdate(self, scenarios, operator_category_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr_ope_cat = []

		sql_ope_cat  = """INSERT OR REPLACE INTO operator_category (id_scenario, id_operator, id_category, tariff_factor, penal_factor )
			values (?, ?, ?, ?, ?);"""

		for id_scenario in scenarios:
			for row in operator_category_arr:
				sql_arr_ope_cat.append((id_scenario[0], row[0], row[1], row[2], row[3]))

		cursor.executemany(sql_ope_cat, sql_arr_ope_cat)
		conn.commit()
		conn.close()
		return True
		

	def updateOperatorCategory(self, scenarios, id_operator, id_category, tariff_factor, penal_factor):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		try:
			for id_scenario in scenarios:
				sql = """update operator_category set tariff_factor = {0}, penal_factor={1} 
					where id_operator = {2} and id_category = {3} and id_scenario = {4}""".format(tariff_factor, penal_factor, id_operator, id_category, id_scenario[0])
			
				cursor.execute(sql)
				conn.commit()
			conn.close()
			return True
		except:
			return False

	def addTransferOperator(self, scenarios, id_from, id_to, cost):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		try:
			for valor in scenarios:
				result = self.selectAll(' transfer_operator_cost ', where=' where id_scenario = %s and id_operator_from = %s and id_operator_to = %s' % (valor[0], id_from, id_to))
				if len(result) > 0:
					qry = """update transfer_operator_cost set cost={3}
						where id_scenario = {0} and id_operator_from = {1} and id_operator_to ={2};""".format(valor[0], id_from, id_to, cost)
				else:
					qry = """insert into transfer_operator_cost 
						(id_scenario, id_operator_from, id_operator_to, cost) 
						values ({0},{1},{2},{3});""".format(valor[0], id_from, id_to, cost)
				
				cursor.execute(qry)
				conn.commit()	
			conn.close()
			return True
		except:
			return False


	def updateTransferOperator(self, scenarios, id_from, id_to, cost):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			if cost!='':
				qry = """update  transfer_operator_cost set cost = {2} where id_operator_from = {0} and id_operator_to = {1} and id_scenario={3};""".format(id_from, id_to, cost, id_scenario[0])
			else:
				qry = """delete from transfer_operator_cost where id_operator_from={0} and id_operator_to={1} and id_scenario={2}""".format(id_from, id_to, id_scenario[0])
		
			cursor.execute(qry)
			conn.commit()
		conn.close()
		return True
		


	def removeOperator(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		qry = """delete from operator where id = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()

		qry = """delete from operator_category where id_operator = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()

		qry = """delete from transfer_operator_cost where id_operator_from = %s or id_operator_to = %s;""" % (id, id)
		cursor.execute(qry)
		conn.commit()

		qry = """delete from link_type_operator where id_operator = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()
		
		conn.close()
		return True		   		

	def updateScenario(self, code, name, cod_previous='', old_code=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "update scenario set code='{}', name='{}', cod_previous='{}' where code = '{}';".format(code, name, cod_previous, old_code)
		cursor.execute(sql)
		conn.commit()
		
		if code != old_code:
			sql = "update scenario set cod_previous='{}' where cod_previous = '{}';".format(code, old_code)
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True
	

	def removeScenario(self, code, scenarios):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "delete from scenario where code in (\
		WITH RECURSIVE \
  			antecesores(n) AS (\
	    		VALUES('{}')\
	    		UNION\
	    			SELECT code\
					FROM scenario, antecesores\
					WHERE scenario.cod_previous=antecesores.n\
	  			)\
		SELECT code FROM scenario\
		WHERE scenario.code IN antecesores);".format(code)
		cursor.execute(sql)
		conn.commit()

		for id_scenario in scenarios:
			sql = f" delete from administrator where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from category where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from operator where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from operator_category where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from transfer_operator_cost where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from route where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from node where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from link_type where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from link_type_operator where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from link where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from exogenous_trips where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from sector where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from inter_sector_inputs where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from inter_sector_transport_cat where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			sql = f" delete from zonal_data where id_scenario = {id_scenario[0]};"
			cursor.execute(sql)
			conn.commit()
			
		conn.close()
		return True

	def addProjectConfig(self, name, description, author, config_model):
		sql_a = " insert into project (name, description, author) values ('{}','{}','{}');".format(name, description, author)
		sql_b = " insert into config_model (type, iterations, convergence, smoothing_factor, route_similarity_factor) values ('{}','{}','{}','{}','{}' );".format(config_model[0]['type'], config_model[0]['iterations'], config_model[0]['convergence'], config_model[0]['smoothing_factor'], config_model[0]['route_similarity_factor'])
		sql_c = " insert into config_model (type, iterations, convergence, smoothing_factor, def_internal_cost_factor) values ('{}','{}','{}','{}', {} );".format(config_model[1]['type'], config_model[1]['iterations'], config_model[1]['convergence'], config_model[1]['smoothing_factor'], config_model[1]['internal_cost_factor'])

		qrys = [sql_a, sql_b, sql_c]
		try:
			for value in qrys:
				conn = self.connectionSqlite()
				cursor = conn.cursor()
				cursor.execute(value)
				conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False

	def updateProjectConfig(self, name, description, author, config_model):
		sql_a = "update project set name='{}', description='{}', author='{}'".format(name, description, author)
		sql_b = "update config_model set type='{0}', iterations='{1}', convergence='{2}', smoothing_factor='{3}', route_similarity_factor='{4}' where type='{0}'".format(config_model[0]['type'], config_model[0]['iterations'], config_model[0]['convergence'], config_model[0]['smoothing_factor'], config_model[0]['route_similarity_factor'])
		sql_c = "update config_model set type='{0}', iterations='{1}', convergence='{2}', smoothing_factor='{3}', def_internal_cost_factor={4} where type='{0}'".format(config_model[1]['type'], config_model[1]['iterations'], config_model[1]['convergence'], config_model[1]['smoothing_factor'], config_model[1]['internal_cost_factor'])

		qrys = [sql_a, sql_b, sql_c]
		try:
			for value in qrys:
				conn = self.connectionSqlite()
				cursor = conn.cursor()
				cursor.execute(value)
				conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False

	def addSector(self, scenarios, ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			if transportable == '0':
				sql = "insert into sector \
					(id_scenario, id, name, description, transportable, atractor_factor, price_factor, substitute) \
					values ({},'{}','{}','{}','{}','{}','{}','{}');".format(
						id_scenario[0], ident, name, description, transportable, atractor_factor, price_factor, sustitute
					)
			else:
				sql = "insert into sector \
					(id_scenario, id, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, substitute) \
					values ({}, '{}','{}','{}','{}','{}','{}','{}','{}');".format(
						id_scenario[0], ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute
					)

			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True

	def updateSector(self, scenarios, ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		location_choice_elasticity_value =  location_choice_elasticity  if transportable > 0 else 'null'
		for id_scenario in scenarios:
			sql = "update sector set  \
				 id={}, name='{}', description='{}', transportable={}, location_choice_elasticity={}, atractor_factor={}, price_factor={}, substitute={}  \
				 where id = {} and id_scenario = {};".format(
					ident, name, description, transportable, location_choice_elasticity_value, atractor_factor, price_factor, sustitute, ident, id_scenario[0]
				)
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True

	def addMode(self, id, name, description, path_overlapping_factor, maximum_number_paths):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "insert into mode \
			(id, name, description, path_overlapping_factor, maximum_number_paths) \
			values ({},'{}','{}','{}','{}');".format(
				id, name, description, path_overlapping_factor, maximum_number_paths
			)
		
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def updateMode(self, id, name, description, path_overlapping_factor, maximum_number_paths, key):
		
		sql = "update mode set  \
			 id={}, name='{}', description='{}', path_overlapping_factor={}, maximum_number_paths={}  \
			 where id = {};".format(
				id, name, description, path_overlapping_factor, maximum_number_paths, id
			)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def validateRemoveMode(self, id_mode):

		sql = f"""select  b.code scenario, a.name category
			from category a 
			join scenario b on (a.id_scenario = b.id) 
			where id_mode = {id_mode}"""
		categories = self.executeSql(sql)

		sql = f"""select  b.code scenario, a.name operator, a.id id_operator
				from operator a 
				join scenario b on (a.id_scenario = b.id) 
				where id_mode = {id_mode}"""
		operators = self.executeSql(sql)

		sql = f"""select distinct b.code, c.name origin, d.name destination, a.trip
				from exogenous_trips a
				join scenario b on (a.id_scenario = b.id)
				join zone c on (a.id_zone_from = c.id)
				join zone d on (a.id_zone_from = d.id)
				where id_mode = {id_mode}"""
		exogenous_trips = self.executeSql(sql)

		if categories or operators:
			return False, categories, operators, exogenous_trips
		else:
			return True, categories, operators, exogenous_trips


	def validateRemoveCategory(self, id_category, scenarios):
		
		sql = f"""select 
				distinct c.code, a.name operator
				from 
				operator a 
				join operator_category b on (a.id = b.id_operator) 
				join scenario c on (b.id_scenario = c.id)
				where b.id_category = {id_category} and b.id_scenario in ({scenarios})"""

		operators = self.executeSql(sql)

		sql = f"""select b.code, c.name origin, d.name destination, a.trip
				from exogenous_trips a
				join scenario b on (a.id_scenario = b.id)
				join zone c on (a.id_zone_from = c.id)
				join zone d on (a.id_zone_from = d.id)
				where id_category = {id_category} and id_scenario in ({scenarios})"""
		exogenous_trips = self.executeSql(sql)

		if operators or exogenous_trips:
			return False, operators, exogenous_trips
		else:
			return True, operators, exogenous_trips


	def validateRemoveOperator(self, id_operator, scenarios):
		
		sql = f"""select distinct b.code scenario, 
			c.name origin_ope, d.name destination_ope, cost
			from transfer_operator_cost a
			join scenario b on (a.id_scenario = b.id)
			join operator c on (a.id_operator_from = c.id)
			join operator d on (a.id_operator_to = d.id)
			where a.id_scenario in ({scenarios}) 
			and (id_operator_from = {id_operator} or id_operator_to = {id_operator})"""

		transfers = self.executeSql(sql)

		sql = f"""select distinct b.code, a.name
				from route a
				join scenario b on (a.id_scenario = b.id)
				where a.id_scenario in ({scenarios}) 
				and a.id_operator = {id_operator}"""
		routes = self.executeSql(sql)

		sql = f"""select distinct c.code, a.name link_type 
			from link_type a
			join link_type_operator b on (a.id = b.id_linktype)
			join scenario c on (b.id_scenario = c.id)
			where b.id_scenario in ({scenarios}) and id_operator = {id_operator} and speed != '' and speed is not null and speed != 0;"""
			
		link_types = self.executeSql(sql)

		if transfers or routes or link_types:
			return False, transfers, routes, link_types
		else:
			return True, transfers, routes, link_types


	def validateRemoveAdministrator(self, id_administrator, scenarios):
		
		sql = f"""select distinct c.code, b.name adm
			from link_type a
			join administrator b on (a.id_administrator = b.id)
			join scenario c on (b.id_scenario = c.id)
			where b.id_scenario in ({scenarios}) and b.id = {id_administrator}"""

		link_types = self.executeSql(sql)

		if link_types:
			return False, link_types
		else:
			return True, link_types
	

	def validateRemoveLinkType(self, id_linktype, scenarios):
		
		sql = f"""select distinct c.code, a.linkid
			from link a
			join link_type b on (a.id_linktype = b.id) 
			join scenario c on (a.id_scenario = c.id)
			where c.id in ({scenarios}) and b.id = {id_linktype} """
			
		links = self.executeSql(sql)

		if links:
			return False, links
		else:
			return True, links


	def validateRemoveRoutes(self, id_route, scenarios):
		
		sql = f"""select distinct c.code, id_link
			from link_route a 
			join route b on a.id_route = b.id
			join scenario c on b.id_scenario = c.id
			where a.id_scenario in ({scenarios}) and a.id_route = {id_route}"""
			
		links = self.executeSql(sql)

		if links:
			return False, links
		else:
			return True, links


	def validateRemoveNodes(self, id_node, scenarios):
		
		sql = f"""select distinct b.code, linkid
			from link a
			join scenario b on (a.id_scenario = b.id)
			where (node_from = {id_node} or node_to = {id_node}) 
			and id_scenario in ({scenarios})"""
			
		links = self.executeSql(sql)

		if links:
			return False, links
		else:
			return True, links


	def validateRemoveSector(self, id_sector, scenarios):
		
		sql = f"""select distinct  c.code scenario, b.name sector
			from inter_sector_transport_cat a
			join sector b on (a.id_sector = b.id) 
			join scenario c on (a.id_scenario = c.id) 
			where time_factor != 0 or 
			a.volume_factor != 0.0 or a.flow_to_product != 0.0 or flow_to_consumer != 0
			and a.id_scenario in ({scenarios}) and a.id_sector = {id_sector}"""
			
		sector = self.executeSql(sql)


		sql = f"""select distinct c.code, b.name sector
			from zonal_data a
			join scenario c on (a.id_scenario = c.id)
			join sector b on (a.id_sector = b.id) 
			where b.id = {id_sector} and a.id_scenario in ({scenarios}) and (induced_production != 0.0 )"""
			
		zonal_data = self.executeSql(sql)

		if sector or zonal_data:
			return False, sector, zonal_data 
		else:
			return True, sector, zonal_data


	def validateRemoveZones(self, id_zone, scenarios):
		
		sql = f"""select distinct b.code, c.name origin, d.name destination, a.trip
				from exogenous_trips a
				join scenario b on (a.id_scenario = b.id)
				join zone c on (a.id_zone_from = c.id)
				join zone d on (a.id_zone_from = d.id)
				where b.id in ({scenarios}) and (c.id = {id_zone} or d.id = {id_zone})"""
			
		exogenous_trips = self.executeSql(sql)

		sql = f"""select distinct c.code, b.name zone, d.name sector
			from zonal_data a
			join zone b on (a.id_zone = b.id)
			join scenario c on (a.id_scenario = c.id)
			join sector d on (a.id_zone = d.id) 
			where b.id = {id_zone} and a.id_scenario in ({scenarios}) and (induced_production != 0.0 )"""
			
		zonal_data = self.executeSql(sql)

		if exogenous_trips or zonal_data:
			return False, exogenous_trips, zonal_data
		else:
			return True, exogenous_trips, zonal_data


	def removeMode(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "delete from mode where id = {}".format(id)
		cursor.execute(sql)
		conn.commit()

		return True


	def addAdministrator(self, scenarios, id, name, description):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		for id_scenario in scenarios:
			sql = "insert into administrator \
				(id_scenario, id, name, description) \
				values ({}, {}, '{}','{}');".format(
					id_scenario[0], id, name, description
				)
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True


	def updateAdministrator(self, scenarios, id, name, description):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = "update administrator set  \
				 name='{}', description='{}' \
				 where id = {} and id_scenario = {};".format(name, description, id, id_scenario[0])
			
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True


	def removeAdministrator(self, scenarios, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = "delete from administrator where id = {} and id_scenario = {} ".format(id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True

	
	def addCategory(self, scenarios, ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = "insert into category \
				(id_scenario, id, id_mode, name, description, volumen_travel_time, value_of_waiting_time, \
				min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity) \
				values ({},'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(
					id_scenario[0], ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity
				)
		
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True


	def updateCategory(self, scenarios, ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:		
			sql = "update category set  \
				 id={}, id_mode={}, name='{}', description='{}', volumen_travel_time={},  value_of_waiting_time={}, \
				 min_trip_gener={}, max_trip_gener={}, elasticity_trip_gener={}, choice_elasticity={}\
				 where id = {} and id_scenario = {};".format(
					 ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity, ident, id_scenario[0]
				)
			
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True

	def removeCategory(self, scenarios,  id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for id_scenario in scenarios:
			sql = "delete from category where id = {} and id_scenario = {}; ".format(id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()
		
		for id_scenario in scenarios:
			sql = "delete from operator_category where id_category = {} and id_scenario = {}; ".format(id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()

		for id_scenario in scenarios:
			sql = "delete from exogenous_trips where id_category = {} and id_scenario = {}; ".format(id, id_scenario[0])
			cursor.execute(sql)
			conn.commit()
			
		conn.close()
		return True

	def addIntersectorSectorInput(self, scenarios, id_sector, id_input_sector,  min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns = ''
		values = ''
		update = ''

		if min_demand!='':
			columns += ', min_demand'
			values += ', '+str(min_demand)
			update += ', min_demand = %s' % min_demand 

		if max_demand!='':
			columns += ', max_demand'
			values += ', '+str(max_demand)
			update += ', max_demand = %s' % max_demand 

		if elasticity!='':
			columns += ', elasticity'
			values += ', '+str(elasticity)
			update += ', elasticity = %s' % elasticity 

		if substitute!='':
			columns += ', substitute'
			values += ', '+str(substitute)
			update += ', substitute = %s' % substitute 
			
		if exog_prod_attractors!='':
			columns += ', exog_prod_attractors'
			values += ', '+str(exog_prod_attractors)
			update += ', exog_prod_attractors = %s' % exog_prod_attractors 

		if ind_prod_attractors!='':
			columns += ', ind_prod_attractors'
			values += ', '+str(ind_prod_attractors)
			update += ', ind_prod_attractors = %s' % ind_prod_attractors 
		
		for scenario in scenarios:
			where_sql = " where id_scenario = %s and id_sector = %s and id_input_sector = %s" % (scenario[0], id_sector, id_input_sector)
			result = self.selectAll(" inter_sector_inputs ", where=where_sql)
			
			if result and len(result)>0:
				sql = """update inter_sector_inputs set id_scenario = {0} {3}
					where id_scenario = {0} and id_sector = {1} and id_input_sector = {2} 
					""".format(scenario[0], id_sector, id_input_sector, update)
			else:
				sql = """insert into inter_sector_inputs (id_scenario, id_sector, id_input_sector {3}) 
				values ( {0}, {1}, {2} {4})""".format(scenario[0], id_sector, id_input_sector, columns, values)
			
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True
	

	def addIntersectorSectorInputTestInsertUpdate(self, scenarios, inputs_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_arr_intersector = []

		sql_intersector = f"""INSERT OR REPLACE INTO  inter_sector_inputs ( id_scenario, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors) 
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		for id_scenario in scenarios:
			for row in inputs_arr:
				sql_arr_intersector.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

		cursor.executemany(sql_intersector, sql_arr_intersector)

		conn.commit()			
		conn.close()
		return True


	def addIntersectorTransInsertUpdate(self, scenarios, trans_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		sql_arr_intersector_cat = []
		
		sql_intersector_cat = f"""INSERT OR REPLACE INTO  inter_sector_transport_cat ( id_scenario, id_sector, id_category, type, time_factor, volume_factor, flow_to_product, flow_to_consumer ) 
					VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""


		for id_scenario in scenarios:
			for row in trans_arr:
				sql_arr_intersector_cat.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

		cursor.executemany(sql_intersector_cat, sql_arr_intersector_cat)

		conn.commit()			
		conn.close()


	def addIntersectorTrans(self, scenarios, id_sector, id_category, _type, time_factor, volume_factor, flow_to_product, flow_to_consumer):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns = ''
		values = ''
		update = ''

		if _type!='':
			columns += ', type'
			values += ', '+str(_type)
			update += ', type = %s' % _type 

		if time_factor!='':
			columns += ', time_factor'
			values += ', '+str(time_factor)
			update += ', time_factor = %s' % time_factor 

		if volume_factor!='':
			columns += ', volume_factor'
			values += ', '+str(volume_factor)
			update += ', volume_factor = %s' % volume_factor 

		if flow_to_product!='':
			columns += ', flow_to_product'
			values += ', '+str(flow_to_product)
			update += ', flow_to_product = %s' % flow_to_product 
			
		if flow_to_consumer!='':
			columns += ', flow_to_consumer'
			values += ', '+str(flow_to_consumer)
			update += ', flow_to_consumer = %s' % flow_to_consumer 
		
		for scenario in scenarios:
			where_sql = " where id_scenario = %s and id_sector = %s and id_category = %s" % (scenario[0], id_sector, id_category)
			result = self.selectAll(" inter_sector_transport_cat ", where=where_sql)
			
			if result and len(result)>0:
				sql = """update inter_sector_transport_cat set id_scenario = {0} {3}
					where id_scenario = {0} and id_sector = {1} and id_category = {2} 
					""".format(scenario[0], id_sector, id_category, update)
			else:
				sql = """insert into inter_sector_transport_cat (id_scenario, id_sector, id_category {3}) 
				values ( {0}, {1}, {2} {4})""".format(scenario[0], id_sector, id_category, columns, values)
			
			cursor.execute(sql)
			conn.commit()

		return True

	def updateIntersectorSectorInput(self, scenarios, id_sector, id_input_sector, column=None, value=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for valor in scenarios:
			sql = "update inter_sector_inputs set {0} = {1} where id_sector = {2} and id_input_sector = {3} and id_scenario = {4}".format(column, value, id_sector, id_input_sector, valor[0])
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True


	def addZonalData(self, scenarios, id_sector, id_zone, exogenous_production, induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns = ''
		values = ''
		update = ''

		if exogenous_production!='':
			columns += ', exogenous_production'
			values += ', '+str(exogenous_production)
			update += ', exogenous_production = %s' % exogenous_production 

		if induced_production!='':
			columns += ', induced_production'
			values += ', '+str(induced_production)
			update += ', induced_production = %s' % induced_production 

		if min_production!='':
			columns += ', min_production'
			values += ', '+str(min_production)
			update += ', min_production = %s' % min_production 

		if max_production!='':
			columns += ', max_production'
			values += ', '+str(max_production)
			update += ', max_production = %s' % max_production 
			
		if exogenous_demand!='':
			columns += ', exogenous_demand'
			values += ', '+str(exogenous_demand)
			update += ', exogenous_demand = %s' % exogenous_demand 

		if base_price!='':
			columns += ', base_price'
			values += ', '+str(base_price)
			update += ', base_price = %s' % base_price

		if value_added!='':
			columns += ', value_added'
			values += ', '+str(value_added)
			update += ', value_added = %s' % value_added 

		if attractor!='':
			columns += ', attractor'
			values += ', '+str(attractor)
			update += ', attractor = %s' % attractor 

		for scenario in scenarios:
			where_sql = " where id_scenario = %s and id_sector = %s and id_zone = %s" % (scenario[0], id_sector, id_zone)
			result = self.selectAll(" zonal_data ", where=where_sql)
			
			if result and len(result)>0:
				sql = """update zonal_data set id_scenario = {0} {3}
					where id_scenario = {0} and id_sector = {1} and id_zone = {2} 
					""".format(scenario[0], id_sector, id_zone, update)
			else:
				sql = """insert into zonal_data (id_scenario, id_sector, id_zone {3}) 
				values ( {0}, {1}, {2} {4})""".format(scenario[0], id_sector, id_zone, columns, values)
			
			cursor.execute(sql)
			conn.commit()

		return True


	def addZonalDataInsertUpdate(self, scenarios, data_zonal_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_zonal_data = f"""INSERT OR REPLACE INTO  zonal_data ( id_scenario, id_sector, id_zone, exogenous_production, 
			induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		sql_arr_zonal_data = []
		for id_scenario in scenarios:
			for row in data_zonal_arr:
				sql_arr_zonal_data.append((id_scenario[0], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

		cursor.executemany(sql_zonal_data, sql_arr_zonal_data)
		conn.commit()			
		conn.close()

		return True


	def addZonalDataImportInsertUpdate(self, scenarios, data_zonal_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()		
		sql_imports_arr = []
		sql_imports = """INSERT INTO zonal_data(id_scenario, id_sector, id_zone, min_imports, max_imports, base_price, attractor_import) 
					VALUES(?, ?, ?, ?, ?, ?, ?)
  					ON CONFLICT(id_scenario, id_sector, id_zone) 
  					DO UPDATE SET min_imports=?, max_imports=?,  base_price=?, attractor_import=?;"""
		for id_scenario in scenarios:
			for row in data_zonal_arr:
				sql_imports_arr.append((id_scenario[0], row[0], row[1], 
					row[2], row[3], row[4], row[5], row[2],  row[3],  row[4], row[5]))
				
		cursor.executemany(sql_imports, sql_imports_arr)
		conn.commit()
		conn.close()
		return True


	def addZonalDataExportsInsertUpdate(self, scenarios, data_zonal_arr):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql_zonal_exports_data = """INSERT INTO zonal_data(id_scenario, id_sector, id_zone, exports) 
					VALUES(?, ?, ?, ?)
  					ON CONFLICT(id_scenario, id_sector, id_zone) 
  					DO UPDATE SET exports=?;"""

		sql_zonal_exports_arr = []

		for id_scenario in scenarios:
			for row in data_zonal_arr:
				sql_zonal_exports_arr.append((id_scenario[0], row[0], row[1], row[2], row[2]))

		cursor.executemany(sql_zonal_exports_data, sql_zonal_exports_arr)
		conn.commit()			
		conn.close()

		return True


	def addZonalDataImports(self, scenarios, id_sector, id_zone, max_imports, min_imports, base_price, attractor):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns = ''
		values = ''
		update = ''

		if max_imports!='':
			columns += ', max_imports'
			values += ', '+str(max_imports)
			update += ', max_imports = %s' % max_imports 

		if min_imports!='':
			columns += ', min_imports'
			values += ', '+str(min_imports)
			update += ', min_imports = %s' % min_imports 

		if base_price!='':
			columns += ', base_price'
			values += ', '+str(base_price)
			update += ', base_price = %s' % base_price 

		if attractor!='':
			columns += ', attractor'
			values += ', '+str(attractor)
			update += ', attractor = %s' % attractor 

		for scenario in scenarios:
			where_sql = " where id_scenario = %s and id_sector = %s and id_zone = %s" % (scenario[0], id_sector, id_zone)
			result = self.selectAll(" zonal_data ", where=where_sql)
			
			if result and len(result)>0:
				sql = """update zonal_data set id_scenario = {0} {3}
					where id_scenario = {0} and id_sector = {1} and id_zone = {2} 
					""".format(scenario[0], id_sector, id_zone, update)
			else:
				sql = """insert into zonal_data (id_scenario, id_sector, id_zone {3}) 
				values ( {0}, {1}, {2} {4})""".format(scenario[0], id_sector, id_zone, columns, values)
			
			cursor.execute(sql)
			conn.commit()

		return True

	def addZonalDataExports(self, scenarios, id_sector, id_zone, exports):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		columns = ''
		values = ''
		update = ''

		if exports!='':
			columns += ', exports'
			values += ', '+str(exports)
			update += ', exports = %s' % exports 

		for scenario in scenarios:
			where_sql = " where id_scenario = %s and id_sector = %s and id_zone = %s" % (scenario[0], id_sector, id_zone)
			result = self.selectAll(" zonal_data ", where=where_sql)
			
			if result and len(result)>0:
				sql = """update zonal_data set id_scenario = {0} {3}
					where id_scenario = {0} and id_sector = {1} and id_zone = {2} 
					""".format(scenario[0], id_sector, id_zone, update)
			else:
				sql = """insert into zonal_data (id_scenario, id_sector, id_zone {3}) 
				values ( {0}, {1}, {2} {4})""".format(scenario[0], id_sector, id_zone, columns, values)
			
			cursor.execute(sql)
			conn.commit()

		return True
	
		

	def updateIntersectorTrans(self, scenarios, id_sector, id_category, column=None, value=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		for scenario in scenarios:
			sql = "update inter_sector_transport_cat set {0} = {1} where id_sector = {2} and id_category = {3} and id_scenario = {4}".format(column, value, id_sector, id_category, scenario[0])
		
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def removeSector(self, id):
		sql = "delete from sector where id = {}".format(id)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def selectAll(self, table, where='', columns='*', orderby=''):
		sql = "select {} from {} {} {}".format(columns,table, where, orderby)
		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchall()
			conn.close()
			return result
		except Exception as e:
			return False

	def executeSql(self,sql):
		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchall()
			conn.close()
			return result
		except Exception as e:
			return False


	def executeDML(self,sql):
		try:
			data = conn.execute(sql)
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return result
		except Exception as e:
			return False


	def maxIdTable(self, table, field='id'):
		sql = f"select max({field}) from {table}"
		
		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchone()
			conn.close()
			return result[0]+1 if result[0] else 1
		except Exception as e:
			return False


	def validateId(self, table, id, field='id'):

		sql = "select * from {0} where {2} = {1}".format(table, id, field)

		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchall()
			conn.close()
			if len(result) > 0:
				return False
			else: 
				return True
		except Exception as e:
			return False
	
	def upSertResultsZones(self, id, name, sectors_expression, scenario, field):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""INSERT OR REPLACE INTO  results_zones ( id, name, sectors_expression, scenario, field)  VALUES ("{id}", "{name}", "{sectors_expression}", "{scenario}", "{field}");"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False
	

	def deleteResultsZone(self, id):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""delete from results_zones where id = '{id}';"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False


	def upSertResultsNetwork(self, id, name, color, scenario, field, id_field_name, level, method, sectors_expression):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""INSERT OR REPLACE INTO  results_network ( id, name, color, scenario, field, id_field_name, level, method, sectors_expression )  
			        VALUES ("{id}", "{name}", "{color}", "{scenario}", "{field}", "{id_field_name}", "{level}", "{method}", "{sectors_expression}");"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False
	

	def deleteResultsNetwork(self, id):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""delete from results_network where id = '{id}';"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False

	
	def upSertResultsMatrix(self, id, name, color, origin_zones, destination_zones, scenario, field, id_field_name, method, sectors_expression ):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""INSERT OR REPLACE INTO  results_matrix ( id, name, color, origin_zones, destination_zones, scenario, field, id_field_name, method, sectors_expression )  
					VALUES ( "{id}", "{name}", "{color}", "{origin_zones}", "{destination_zones}", "{scenario}", "{field}", "{id_field_name}", "{method}", "{sectors_expression}");"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False
	

	def deleteResultsMatrix(self, id):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			
			sql =  f"""delete from results_matrix where id = '{id}';"""
			
			cursor.execute(sql)
			conn.commit()

			return True
		except Exception as e:
			return False