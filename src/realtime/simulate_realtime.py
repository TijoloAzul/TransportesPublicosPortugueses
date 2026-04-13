#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from flask import Flask
from datetime import datetime
import flask
import utils.logger as logger
import argparse
import configparser
import time
import json
import requests
from utils.db.db import db_manager
import utils.db.db_operators as db_operators
import utils.db.db_trips as db_trips
from google.transit import gtfs_realtime_pb2

global_properties_file_path = "../../conf/global.properties"
generic_map_properties_file_path = "../../conf/map.generic.properties"

## Flask
app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route("/")
def hello_world():
	resp = flask.Response("Benvindo")
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.after_request
def add_header(response):
	response.headers['X-Content-Type-Options'] = 'nosniff'
	return response

@app.route("/realtime/<op_name>")
def realtime(op_name):
	start = time.time()
	logger.info(f'Pedindo posições para {op_name}')
	
	op = operators[op_name]
	if op is None:
		logger.warn("Unkwnon operator " + op_name)
		flask.abort(400, "Unknown operator " + op_name)	
	
	resp = flask.Response(json.dumps(get_realtime_geojson(op)))
	resp.headers['Access-Control-Allow-Origin'] = '*'
	logger.info("Getting " + op['name'] + " vehicle positions took: " + str(time.time() - start) + ' seconds')
	return resp

def get_realtime_geojson(op):
	if op['code'] == 'cm':
		return get_cm_realtime()
	elif op['code'] == 'carris':
		return get_carris_realtime()
	#else:
	#    return requests.get("http://localhost:5001/simulate/" + op.name).json()

## Carris Metropolitana
def get_cm_realtime():
	global trips
	op_trips = trips['cm']
	vehicles = requests.get("https://api.carrismetropolitana.pt/vehicles").json()
	features = list()
	now = datetime.now()
	for vehicle in vehicles:
		if is_vehicle_complete(vehicle):
			id = vehicle['id']
			trip = vehicle['trip_id']
			lat = vehicle['lat']
			lon = vehicle['lon']
			size = map_conf['cm']['vehicle_size']
			time_delta = (now - datetime.fromtimestamp(vehicle['timestamp']))
			if time_delta.total_seconds() < 300:
				if trip in op_trips.index:
					text = str(vehicle['line_id']) + ' : ' + str(op_trips.loc[trip, 'headsign'])
					color = '#' + op_trips.loc[trip, 'color_route']
				else:
					logger.warn('Missing trip for cm: ' + str(vehicle['trip_id']))
					text = str(vehicle['line_id'])
					color = 'gray'
				if map_conf['cm']['vehicle_color'] != 'LINE':
					color = map_conf['cm']['vehicle_color']
			
				features.append({
					"type": "Feature",
					"geometry": {
						"type": "Point",
						"coordinates": [lon, lat]},
					"properties": {
						"id": id,
						"color": color,
						"text": text,
						"size": size}})
    
	return {'type': 'FeatureCollection', 'features': features}

def is_vehicle_complete(vehicle):
    	return 'lat' in vehicle and 'lon' in vehicle and 'id' in vehicle and 'trip_id' in vehicle and 'line_id' in vehicle

# Carris
def ler_gtfs_rt(url):
	feed = gtfs_realtime_pb2.FeedMessage()
	
	try:
		response = requests.get(url)
		binario = response.content
		feed.ParseFromString(binario)
		return feed

	except Exception as e:
		logger.error(f"Erro ao ler o ficheiro: {e}")
		return None

def get_carris_realtime():
	global trips
	op_trips = trips['carris']
	vehicles = ler_gtfs_rt('https://gateway.carris.pt/gateway/gtfs/api/v2.11/GTFS/realtime/vehiclepositions')
	features = list()
	if vehicles is None:
		return {'type': 'FeatureCollection', 'features': features}

	for entity in vehicles.entity:
		if is_vehicle(entity):
			vehicle = entity.vehicle
			id = entity.id
			trip = vehicle.trip.trip_id
			lat = vehicle.position.latitude
			lon = vehicle.position.longitude
			size = map_conf['carris']['vehicle_size']
			if trip in op_trips.index:
				if op_trips.loc[trip, 'headsign'] is None:
					try:
						if '-' in op_trips.loc[trip, 'name_route']:
							headsign = str(op_trips.loc[trip, 'name_route']).split('-')[1-vehicle.trip.direction_id].strip()
						else:
							headsign = str(op_trips.loc[trip, 'name_route'])
					except:
						logger.error(str(op_trips.loc[trip, 'name_route']) + ' -- ' + str(vehicle.trip.direction_id))
						headsign = str(op_trips.loc[trip, 'name_route'])
				else:
					headsign = op_trips.loc[trip, 'headsign']
				text = str(op_trips.loc[trip, 'code_route']) + ' : ' + headsign
				color = op_trips.loc[trip, 'color_route']
			else:
				logger.warn('Missing trip for carris: ' + str(trip))
				text = str(vehicle.trip.route_id)
				color = 'gray'
			if map_conf['carris']['vehicle_color'] != 'LINE':
				color = map_conf['carris']['vehicle_color']
			
			features.append({
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [lon, lat]},
				"properties": {
					"id": id,
					"color": color,
					"text": text,
					"size": size}})
	return {'type': 'FeatureCollection', 'features': features}

def is_vehicle(entity):
    return entity.HasField('vehicle')

## Connecting to DB
def db_connect():
	global db
	db = db_manager(global_conf['db'])
	db.open()

def db_disconnect():
	db.close()
	
## Options & configurations
def load_properties_file(filename):
	conf = configparser.ConfigParser()
	
	path = os.path.dirname(os.path.realpath(__file__))
	properties_file = os.path.join(path, filename)
	
	if os.path.exists(properties_file):
		conf.read(properties_file)
	else:
		logger.error(f"Ficheiro de configurações {properties_file} não encontrado.")
		raise Exception('Missing properties file: ' + properties_file)

	return conf

def load_generic_map_properties():
	global map_conf
	map_conf = load_properties_file(generic_map_properties_file_path)

def load_global_properties():
	global global_conf
	global_conf = load_properties_file(global_properties_file_path)

def parse_options():
	parser = argparse.ArgumentParser('Interface com os dados realtime das várias operadoras.')

	global operators
	operators = db_operators.get_operator_map(db)
	operators_codes = list(operators.keys())

	parser.add_argument('--operators', '-operadoras', '-o', nargs='*', choices=operators_codes, help='Operadores a preparar')

	return parser.parse_args()

# Trips
def read_trips(op):
	logger.info(f"A ler viagens de {op['name']}.")
	trips = db_trips.read_trips(db, op['id']).set_index('code')
	logger.info(f"Importadas {len(trips)} viagens para {op['name']}")
	return trips

# Main
def get_operators(options):
	global operators
	return {op: operators[op] for op in options['operators']}
	
def main():
	load_global_properties()
	load_generic_map_properties()
	db_connect()
	##options = parse_options()
	global operators, trips
	operators = db_operators.get_operator_map(db)
	trips = dict()
	options = {'operators': ['cm', 'carris']}
	ops = get_operators(options)
	for op in ops.values():
		if op['code'] == 'cm' or op['code'] == 'carris':
			trips[op['code']] = read_trips(op)
		else: 
			logger.warn(f'O operador {op['name']} não tem realtime.')
	db_disconnect()
	logger.info('Simulação prontas')

main()    