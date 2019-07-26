# -*- coding: utf-8 -*-
import sys, os

import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError

class DataBaseSqlite():
	"""
        @summary: Class Constructor
    """
	def __init__(self, tranus_folder):
		self.tranus_folder = tranus_folder
		self.conn = self.connectionSqlite()

	def __del__(self):
		self.conn.close()

	def connectionSqlite(self):
		"""
        @summary: Class Constructor
    	"""
		if self.tranus_folder[-13:]=="""\W_TRANUS.CTL""":
			self.tranus_folder = self.tranus_folder.replace('\W_TRANUS.CTL','')
		
		path = "{}/qtranus.db".format(self.tranus_folder)
		
		try:
			conn = sqlite3.connect(path)
		except (OperationalError):
			print("Connection to Database Failed")
			return False

		return sqlite3.connect(path)


	def dataBaseStructure(self, conn):
		"""
		@summary: Validates invalid characters
		@param input: Input string
		@type input: String object
		"""
		cursor = conn.cursor()
		tables = ["""
			CREATE TABLE IF NOT EXISTS scenario (
				id 			 INTEGER PRIMARY KEY AUTOINCREMENT,
				code         CHAR(20) NOT NULL,
				name         TEXT NOT NULL,
				description  TEXT NOT NULL,
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
				route_similarity_factor  TEXT
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS sector (
				id           			   INTEGER,
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
				id           			   INTEGER PRIMARY KEY,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS scenario_administrator (
				id	             INTEGER PRIMARY KEY,
				id_scenario      INTEGER,
				id_administrator INTEGER
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS category (
				id           			   INTEGER,
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
				CONSTRAINT fk_zonal_data_scenarios
    			FOREIGN KEY (id_scenario)
    			REFERENCES scenario(id)
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS operator (
				id           			   INTEGER,
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
				stops_unit_alight_time    	REAL NOT NULL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS operator_category (
				id		      INTEGER PRIMARY KEY AUTOINCREMENT,
				id_operator   INTEGER,
				id_category   INTEGER,
				tariff_factor REAL,
				penal_factor  REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS scenario_operator (
				id	        INTEGER PRIMARY KEY,
				id_scenario INTEGER,
				id_operator INTEGER
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
				id	        INTEGER PRIMARY KEY,
				name        TEXT NOT NULL,
				description TEXT NOT NULL,
				id_operator    INTEGER,
				frequency_from REAL,
				frequency_to   REAL,
				target_occ     REAL,
				max_fleet      REAL,
				used 		   BLOB,
				follows_schedule BLOB	
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS scenario_route (
				id	        INTEGER PRIMARY KEY,
				id_scenario INTEGER,
				id_route    INTEGER
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link_type (
				id	        INTEGER,
				name        TEXT NOT NULL,
				description TEXT NOT NULL,
				id_administrator   		INTEGER,
				capacity_factor 		REAL,
				min_maintenance_cost   	REAL,
				perc_speed_reduction_vc REAL,
				perc_max_speed_reduction REAL,
				vc_max_reduction         REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link_type_operator (
				id	              INTEGER PRIMARY KEY AUTOINCREMENT,
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
			CREATE TABLE IF NOT EXISTS scenario_linktype (
				id	        INTEGER PRIMARY KEY,
				id_scenario INTEGER,
				id_linktype INTEGER
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS link (
				id	            INTEGER PRIMARY KEY AUTOINCREMENT,
				id_scenario     INTEGER,
				linkid          TEXT NOT NULL, 
				id_linktype     INTEGER,
				node_from       INTEGER,
				node_to         INTEGER,
				distance 		REAL,
				capacity   	    REAL,
				delay           REAL
			);
			""",
			"""
			CREATE TABLE IF NOT EXISTS node (
				id	            INTEGER PRIMARY KEY AUTOINCREMENT,
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
			"""
			]

		try:
			for value in tables:
				cursor.execute(value)
		except:
			return False
		conn.close()
		return True


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


	def validateConnection(self):
		try:
			self.dataBaseStructure(self.conn)
			return True
		except:
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

	def addExogenousData(self, scenarios, id_zone_from, id_zone_to, id_mode, id_category, column=None, value=None):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		for valor in scenarios:
			sql = "insert into exogenous_trips \
				(id_scenario, id_zone_from, id_zone_to, id_category, id_mode,  {5}) \
				values ({0},{1},{2},{3},{4},{6});".format(valor[0], id_zone_from, id_zone_to, id_category, id_mode, column, value)
			
			cursor.execute(sql)
			conn.commit()

		conn.close()
		return True
		


	def updateExogenousData(self, id_scenario, id_zone_from, id_zone_to, id_mode, id_category, column=None, value=None):
		
		if value !='':
			sql = """
				update exogenous_trips set {5}={6}
				where id_scenario={0} and id_zone_from={1} and id_zone_to={2} and id_mode={3} and id_category={4} ;
				""".format(id_scenario, id_zone_from, id_zone_to, id_mode, id_category, column, value)
		else: 
			sql = """
				delete from exogenous_trips
				where id_scenario={0} and id_zone_from={1} and id_zone_to={2} and id_mode={3} and id_category={4} ;
				""".format(id_scenario, id_zone_from, id_zone_to, id_mode, id_category)	

		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False


	def addScenario(self, code, name, description, cod_previous=''):
		if self.ifExist('scenario', 'code', code):
			return False
		else:
			sql = "insert into scenario (code, name, description, cod_previous) values ('{}','{}','{}','{}');".format(code, name, description, cod_previous)
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True

	def addLinkType(self, scenarios, id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = """insert into link_type (id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction)
		 values ({},'{}','{}',{},{},{},{},{},{});""".format(id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction)
		
		cursor.execute(sql)
		conn.commit()

		for value in scenarios:
			sql= """insert into scenario_linktype (id_scenario, id_linktype) values (%s, %s);""" % (value[0], id)
			cursor.execute(sql)
			conn.commit()

		conn.close()
		
		return True


	def updateLinkType(self, id, name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction):
		sql = """update link_type set name='{}', description='{}', id_administrator={}, capacity_factor={}, min_maintenance_cost={}, perc_speed_reduction_vc={}, perc_max_speed_reduction={}, vc_max_reduction={}
		 where id = {};""".format(name, description, id_administrator, capacity_factor, min_maintenance_cost, perc_speed_reduction_vc, perc_max_speed_reduction, vc_max_reduction, id)
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		
		return True


	def updateLinkTypeOperator(self, id_linktype, id_operator, column=None, value=None):
		sql = """update link_type_operator set {0} = {1} where id_linktype = {2} and id_operator = {3};""".format(column, value, id_linktype, id_operator);
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		
		return True


	def addLinkTypeOperator(self, id_linktype, id_operator, column=None, value=None):
		
		sql = "insert into link_type_operator \
		(id_linktype, id_operator, {2}) \
		values ({0},{1},{3});".format(id_linktype, id_operator, column, value)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def removeLinkType(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = """delete from link_type where id = {};""".format(id)
		cursor.execute(sql)
		conn.commit()

		sql = """delete from link_type_operator where id_linktype = {};""".format(id)
		cursor.execute(sql)
		conn.commit()

		sql = """delete from scenario_linktype where id_linktype = {};""".format(id)
		cursor.execute(sql)
		conn.commit()
		
		conn.close()
		return True

	def addRoute(self, scenarios, id, name, description, id_operator, frequency_from, frequency_to, max_fleet, target_occ, used=None, follows_schedule=None):
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()

			sql = """insert into route (id, name, description, id_operator, frequency_from, frequency_to, max_fleet,  target_occ, used, follows_schedule)
			 values ({}, '{}','{}',{},{},{},{},{},{},{});""".format(id, name, description, id_operator, frequency_from, frequency_to, max_fleet, target_occ, used, follows_schedule)
			
			cursor.execute(sql)
			conn.commit()

			for value in scenarios:
				sql= """insert into scenario_route (id_scenario, id_route) values (%s, %s);""" % (value[0], id)
				cursor.execute(sql)
				conn.commit()
			conn.close()
			return True
		except:
			return False


	def updateRoute(self, id, name, description, id_operator, frequency_from, frequency_to, max_fleet, target_occ, used=None, follows_schedule=None):
		sql = """update route set name='{}', description='{}', id_operator={}, frequency_from={}, frequency_to={}, max_fleet={}, target_occ={}, used={}, follows_schedule={}
			where id={}""".format(name, description, id_operator, frequency_from, frequency_to, max_fleet, target_occ, used, follows_schedule, id)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def removeRoute(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = """delete from route where id = {};""".format(id)
		cursor.execute(sql)
		conn.commit()

		sql = """delete from scenario_route where id_route = {};""".format(id)
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

	def addLink(self, linkid, node_from, node_to):

		sql = "insert into link (linkid, node_from, node_to) values ('{}',{},{});".format(linkid, node_from, node_to)
		
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def addNode(self, _id, id_type, name, description, x, y):
		
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

		sql = "insert into node ({}) values ({});".format(column, value)
		
		#print(sql)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def removeNode(self, _id):
		
		sql = "delete from node where id={};".format(_id)
		
		#print(sql)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
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
		
		sql = "delete from zone where id = {};".format(id)
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

		sql = "insert into operator (id, name, description, id_mode, type, \
			   basics_modal_constant, basics_time_factor, basics_occupency, \
			   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, \
			   energy_min, energy_max, energy_slope, energy_cost, \
			   cost_time_operation, cost_porc_paid_by_user,\
			   stops_min_stop_time, stops_unit_boarding_time, \
			   stops_unit_alight_time) values ({},'{}','{}',{},'{}',\
			   {},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{});".format(_id, _name, _description, _id_mode, _type,
			   basics_modal_constant, basics_time_factor, basics_occupency,
			   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, 
			   energy_min, energy_max, energy_slope, energy_cost, 
			   cost_time_operation, cost_porc_paid_by_user, stops_min_stop_time, 
			   stops_unit_boarding_time, stops_unit_alight_time)

		cursor.execute(sql)
		conn.commit()

		for value in scenarios:
			sql= """insert into scenario_operator (id_scenario, id_operator) values (%s, %s);""" % (value[0], _id)
			cursor.execute(sql)
			conn.commit()
		
		conn.close()
		return True


	def updateOperator(self, data):
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

		sql = """update operator set name='{}', description='{}', id_mode={}, type='{}', 
			   basics_modal_constant={}, basics_time_factor={}, basics_occupency={}, 
			   basics_fixed_wating_factor={}, basics_boarding_tariff={}, basics_distance_tariff={}, basics_time_tariff={}, 
			   energy_min={}, energy_max={}, energy_slope={}, energy_cost={}, 
			   cost_time_operation={}, cost_porc_paid_by_user={},
			   stops_min_stop_time={}, stops_unit_boarding_time={}, 
			   stops_unit_alight_time={} where id = {};""".format(_name, _description, _id_mode, _type,
			   basics_modal_constant, basics_time_factor, basics_occupency,
			   basics_fixed_wating_factor, basics_boarding_tariff, basics_distance_tariff, basics_time_tariff, 
			   energy_min, energy_max, energy_slope, energy_cost, 
			   cost_time_operation, cost_porc_paid_by_user, stops_min_stop_time, 
			   stops_unit_boarding_time, stops_unit_alight_time, _id)
		#print(sql)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def addOperatorCategory(self, id_operator, id_category, column=None, value=None):
		
		sql = "insert into operator_category \
			(id_operator, id_category, {2}) \
			values ({0},{1},{3});".format(id_operator, id_category, column, value)
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False



	def updateOperatorCategory(self, id_operator, id_category, column=None, value=None):
		sql = "update operator_category set {0} = {1} where id_operator = {2} and id_category = {3}".format(column, value, id_operator, id_category)
		
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False


	def addTransferOperator(self, scenarios, id_from, id_to, cost):
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		
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


	def updateTransferOperator(self, id_scenario, id_from, id_to, cost):
		if cost!='':
			qry = """update  transfer_operator_cost set cost = {2} where id_operator_from = {0} and id_operator_to = {1} and id_scenario={3};""".format(id_from, id_to, cost, id_scenario)
		else:
			qry = """delete from transfer_operator_cost where id_operator_from={0} and id_operator_to={1} and id_scenario={2}""".format(id_from, id_to, id_scenario)
		try:
			conn = self.connectionSqlite()
			cursor = conn.cursor()
			cursor.execute(qry)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False


	def removeOperator(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		qry = """delete from operator where id = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()

		qry = """delete from operator_category where id_operator = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()

		qry = """delete from scenario_operator where id_operator = %s;""" % (id)
		cursor.execute(qry)
		conn.commit()
		conn.close()
		return True		   		

	def updateScenario(self, code, name, description, cod_previous=''):
		sql = "update scenario set name='{}', description='{}', cod_previous='{}' where code = '{}';".format(name, description, cod_previous, code)
		conn = self.connectionSqlite()
		try:
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False

	def removeScenario(self, code):
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

		conn = self.connectionSqlite()
		try:
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			return False

	def addProjectConfig(self, name, description, author, config_model):
		sql_a = " insert into project (name, description, author) values ('{}','{}','{}');".format(name, description, author)
		sql_b = " insert into config_model (type, iterations, convergence, smoothing_factor, route_similarity_factor) values ('{}','{}','{}','{}','{}' );".format(config_model[0]['type'], config_model[0]['iterations'], config_model[0]['convergence'], config_model[0]['smoothing_factor'], config_model[0]['route_similarity_factor'])
		sql_c = " insert into config_model (type, iterations, convergence, smoothing_factor) values ('{}','{}','{}','{}' );".format(config_model[1]['type'], config_model[1]['iterations'], config_model[1]['convergence'], config_model[1]['smoothing_factor'])

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
		sql_c = "update config_model set type='{0}', iterations='{1}', convergence='{2}', smoothing_factor='{3}' where type='{0}'".format(config_model[1]['type'], config_model[1]['iterations'], config_model[1]['convergence'], config_model[1]['smoothing_factor'])

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

	def addSector(self, ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute):
		if transportable == '0':
			sql = "insert into sector \
				(id, name, description, transportable, atractor_factor, price_factor, substitute) \
				values ('{}','{}','{}','{}','{}','{}','{}');".format(
					ident, name, description, transportable, atractor_factor, price_factor, sustitute
				)
		else:
			sql = "insert into sector \
				(id, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, substitute) \
				values ('{}','{}','{}','{}','{}','{}','{}','{}');".format(
					ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute
				)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def updateSector(self, ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute):
		location_choice_elasticity_value =  location_choice_elasticity  if transportable > 0 else 'null'
		sql = "update sector set  \
			 id={}, name='{}', description='{}', transportable={}, location_choice_elasticity={}, atractor_factor={}, price_factor={}, substitute={}  \
			 where id = {};".format(
				ident, name, description, transportable, location_choice_elasticity_value, atractor_factor, price_factor, sustitute, ident
			)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
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

	def removeMode(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "delete from mode where id = {}".format(id)
		cursor.execute(sql)
		conn.commit()

		sql = "delete from scenario_mode where id_mode = {}".format(id)
		cursor.execute(sql)
		conn.commit()	
		conn.close()
		return True


	def addAdministrator(self, scenarios, id, name, description):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "insert into administrator \
			(id, name, description) \
			values ({},'{}','{}');".format(
				id, name, description
			)
		cursor.execute(sql)
		conn.commit()
		for value in scenarios:
			sql= """insert into scenario_administrator (id_scenario, id_administrator) values (%s, %s);""" % (value[0], id)
			cursor.execute(sql)
			conn.commit()
		conn.close()
		return True


	def updateAdministrator(self, id, id_scenario, name, description):
		
		sql = "update administrator set  \
			 id={}, name='{}', description='{}' \
			 where id = {};".format(
				id, name, description, id
			)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True


	def removeAdministrator(self, id):
		conn = self.connectionSqlite()
		cursor = conn.cursor()

		sql = "delete from administrator where id = {}".format(id)
		cursor.execute(sql)
		conn.commit()

		sql = "delete from scenario_administrator where id_administrator = {}".format(id)
		cursor.execute(sql)
		conn.commit()

		conn.close()
		return True

	
	def addCategory(self, ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity):
		sql = "insert into category \
			(id, id_mode, name, description, volumen_travel_time, value_of_waiting_time, \
			min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity) \
			values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(
				ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity
			)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def updateCategory(self, ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity):
		sql = "update category set  \
			 id={}, id_mode={}, name='{}', description='{}', volumen_travel_time={},  value_of_waiting_time={}, \
			 min_trip_gener={}, max_trip_gener={}, elasticity_trip_gener={}, choice_elasticity={}\
			 where id = {};".format(
				ident, id_mode, name, description, volumen_travel_time, value_of_waiting_time, min_trip_gener, max_trip_gener, elasticity_trip_gener, choice_elasticity, ident
			)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def removeCategory(self, id):
		sql = "delete from category where id = {}".format(id)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
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
		