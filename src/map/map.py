#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

import webbrowser
import folium
import utils.logger as logger
import argparse
import configparser
import json
import pandas as pd
from utils.db.db import db_manager
import utils.db.db_operators as db_operators
import utils.db.db_stops as db_stops
import utils.db.db_shapes as db_shapes

global_properties_file_path = "../../conf/global.properties"
map_properties_file_path = "../../conf/map.{name}.properties"
generic_map_properties_file_path = "../../conf/map.generic.properties"

## Options & configurations
def parse_options():
	parser = argparse.ArgumentParser('Cria um mapa com a posição dos autocarros.\n'+
									 'Inicialmente só desenha os rotas e a posição atual dos autocarros da carris metropolitana.')

	global operators
	operators = db_operators.get_operator_map(db)
	operators_codes = list(operators.keys())
	
	parser.add_argument('--operators', '-o', nargs='*', choices=operators_codes, help='Operadores a preparar')
	parser.add_argument('--shapes', '--linhas', '-l', action='store_true', help='Desenhar linhas')
	parser.add_argument('--stops', '--paragens', '-p', action='store_true', help='Desenhar paragens')
	#parser.add_argument('--vehicles', '--veiculos', '-v', action='store_true', help='Desenhar veículos')
	#parser.add_argument('--simulate', '--simular', '-s', action='store_true', help='Simular veículos')
	parser.add_argument('--config', '-c', help='Nome da configuração')

	options = parser.parse_args()

	if options.operators is None:
		options.operators = operators_codes	

	if options.config is None:
		load_generic_map_properties()
	else:
		load_map_properties(options.config)
		options.operators = list(set(options.operators) & set(map_conf.sections()))		
		
	return options

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

def load_global_properties():
	global global_conf
	global_conf = load_properties_file(global_properties_file_path)

def load_map_properties(name):
	global map_conf
	map_conf = load_properties_file(map_properties_file_path.format(name = name))
 
def load_generic_map_properties():
	global map_conf
	map_conf = load_properties_file(generic_map_properties_file_path)
	
## Connecting to DB
def db_connect():
	global db
	db = db_manager(global_conf['db'])
	db.open()

def db_disconnect():
	db.close()

## Stops
def read_stops(operator):
	logger.info(f"A ler paragens de {operator['name']}.")
	return db_stops.read_stops(db, operator['id'])

def draw_stops(city, op, stops):
	logger.info("A desenhar " + str(len(stops)) + " paragens")
	op_inner_color = map_conf[op]['stops_inner_color']
	op_outer_color = map_conf[op]['stops_outer_color']
	for stop in stops.itertuples():
		folium.Circle(
			[stop.lat, stop.lon], 
			fillColor = op_outer_color,
			stroke=False,
			fillOpacity=0.5,
			tooltip=stop.name,
			radius=float(map_conf[op]['stops_size'])
			).add_to(city)
		folium.Circle(
			[stop.lat, stop.lon], 
			fillColor = op_inner_color,
			stroke=False,
			fillOpacity=1,
			tooltip=stop.name,
			radius=float(map_conf[op]['stops_size']) / 2
			).add_to(city)

## Shapes
def read_shapes(operator):
	logger.info(f"A ler linhas de {operator['name']}.")
	shapes = db_shapes.read_shapes(db, operator['id']).set_index('id')
	points = db_shapes.read_points(db, operator['id'])
	points = points.sort_values(['id_shape', 'idx'])
    
    
	paths = points.groupby('id_shape')[['lat', 'lon']].apply(lambda p: p.values.tolist()).reset_index(name='path')
	paths = paths.set_index('id_shape')
    
	return pd.merge(paths, shapes, left_index=True, right_index=True)

def draw_shapes(city, op, shapes):
    logger.info("A desenhar " + str(len(shapes)) + " linhas")
    op_color = map_conf[op]['shape_color']
    for shape in shapes.itertuples():
        if op_color.upper() == 'LINE':
            line_color = format_color(shape.color)
        else:
            line_color = map_conf[op]['shape_color']
        folium.PolyLine(
			shape.path, 
			color = line_color,
			tooltip=shape.code_route + ' - ' + shape.name,
			weight=map_conf[op]['shape_width']
			).add_to(city)

def format_color(color):
    if color[0] == "#":
        return color
    else:
        return '#' + color 

## Main
def get_operators(options):
	global operators
	return {op: operators[op] for op in options.operators}

def build_path():
	return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data/map'))

def ensure_path(path):
	if not os.path.isdir(path):
		logger.info("A criar pasta para mapas.")
		os.makedirs(path)
		
def save_map(city):
	path = build_path()
	ensure_path(path)
	filename = os.path.join(path, map_conf['map']['filename'])
	logger.info(f'A criar um mapa: {filename}')
	city.save(filename)
	webbrowser.open(f"file://./{filename}")

def main():
	load_global_properties()
	db_connect()
	options = parse_options()
	city = folium.Map(location=(38.7, -9.2), tiles ="cartodb positron", zoom_start = 11)	
	city.get_root().title = map_conf['map']['title']

	ops = get_operators(options)
	for op in ops:
		if options.stops:
			stops = read_stops(ops[op])
			draw_stops(city, op, stops)
		if options.shapes:
			shapes = read_shapes(ops[op])
			draw_shapes(city, op, shapes)
	
	save_map(city)
	db_disconnect()
	logger.info("Mapa criado!")

main()    