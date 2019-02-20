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

	def connectionSqlite(self):
		"""
        @summary: Class Constructor
    	"""
		path = "{}/qtranus.db".format(self.tranus_folder)
		
		try:
			conn = sqlite3.connect(path)
		except (OperationalError):
			print("Connection Failed")
			return False

		return sqlite3.connect(path)


	def dataBaseStructure(self, conn):
		"""
		@summary: Validates invalid characters
		@param input: Input string
		@type input: String object
		"""
		cursor = conn.cursor()
		tabla = ["""
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
				key			 			   INTEGER PRIMARY KEY AUTOINCREMENT,
				id           			   INTEGER,
				name         			   TEXT NOT NULL,
				description    			   TEXT NOT NULL,
				transportable 			   INTEGER NOT NULL,
				location_choice_elasticity REAL,
				atractor_factor   		   REAL NOT NULL,
				price_factor  		       REAL NOT NULL,
				sustitute   		       REAL NOT NULL
			);
			"""]

		try:
			for value in tabla:
				cursor.execute(value)
		except:
			return False
		conn.close()
		return True

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
				(id, name, description, transportable, atractor_factor, price_factor) \
				values ('{}','{}','{}','{}','{}','{}');".format(
					ident, name, description, transportable, atractor_factor, price_factor
				)
		else:
			sql = "insert into sector \
				(id, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor) \
				values ('{}','{}','{}','{}','{}','{}', '{}');".format(
					ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor
				)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def updateSector(self, ident, name, description, transportable, location_choice_elasticity, atractor_factor, price_factor, sustitute, key):
		location_choice_elasticity_value =  location_choice_elasticity  if transportable > 0 else 'null'
		sql = "update sector set  \
			 id={}, name='{}', description='{}', transportable={}, location_choice_elasticity={}, atractor_factor={}, price_factor={}, sustitute={}  \
			 where key = {};".format(
				ident, name, description, transportable, location_choice_elasticity_value, atractor_factor, price_factor, sustitute, key
			)
		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def removeSector(self, key):
		sql = "delete from sector where key = {}".format(key)

		conn = self.connectionSqlite()
		cursor = conn.cursor()
		cursor.execute(sql)
		conn.commit()
		conn.close()
		return True

	def selectAll(self, table, where=''):
		sql = "select * from {} {}".format(table, where)
		conn = self.connectionSqlite()
		try:
			data = conn.execute(sql)
			result = data.fetchall()
			conn.close()
			return result
		except Exception as e:
			return False
