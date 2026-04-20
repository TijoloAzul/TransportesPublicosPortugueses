#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

import utils.logger as logger
import argparse
import argcomplete
import configparser
import pandas as pd
from utils.db.db import db_manager
import utils.db.db_operators as db_operators
import utils.db.db_routes as db_routes
import utils.db.db_stops as db_stops
import utils.db.db_shapes as db_shapes
import utils.db.db_trips as db_trips
import utils.geo as geo

import operators.carris.colors as carris_colors

properties_file_path = '../../conf/global.properties'

## Connecting to DB
def db_connect():
    global db
    db = db_manager(conf['db'])
    db.open()

def db_disconnect():
    db.close()

## Options & configurations
def load_properties():
    global conf
    conf = configparser.ConfigParser()

    path = os.path.dirname(os.path.realpath(__file__))
    properties_file = os.path.join(path, properties_file_path)
    
    if os.path.exists(properties_file):
        conf.read(properties_file)
    else:
        logger.error("No properties file found, please configure the conf/global.properties")
        raise Exception('Missing properties file: ' + properties_file)

def parse_options():
    parser = argparse.ArgumentParser('Prepara os dados para o meu mapa de transportes públicos.\n'+
                                     'Inicialmente só prepara ficheiros com os trajetos.')

    global operators
    operators = db_operators.get_operator_map(db)
    operators_codes = list(operators.keys())

    parser.add_argument('--operators', '-operadoras', '-o', nargs='*', choices=operators_codes, help='Operadores a preparar')
    parser.add_argument('--routes', '--rotas', '-r', action='store_true', help='Buscar rotas (routes). Rotas disponíveis, por exemplo: 720 da Carris ou Linha Vermelha do metro')
    parser.add_argument('--shapes', '--linhas', '-l', action='store_true', help='Buscar linhas (shapes). Isto corresponde ao traçado em cordenadas geográficas.')
    parser.add_argument('--stops', '--paragens', '-p', action='store_true', help='Buscar paragens. Lista de todas as paragens acessíveis.')
    parser.add_argument('--trips', '--viagens', '-v', action='store_true', help='Buscar viagens. Lista de todas as possíveis viagens. De notar que uma rota vai ter várias viagens ao dia.')
    parser.add_argument('--schedule', '--horario', '--tempos', '-t', action='store_true', help='Buscar horário. Horário das viagens, isto é a que horas é que o meio de transporte passa em cada paragem.')
    parser.add_argument('--calendar', '--calendario', '-c', action='store_true', help='Buscar calendário. Calendário das várias viagens.')
    #parser.add_argument('--start', '--de', '-d', type=datetime.fromisoformat, default=datetime.now(), help='Data de início para a construção do calendário.')
    #parser.add_argument('--end', '--até', '-a', type=datetime.fromisoformat, help='Data de fim para a construção do calendário.')

    argcomplete.autocomplete(parser)
    
    options = parser.parse_args()
    #if_nothing_do_all(options)
    #create_end_date_if_needed(options)
    
    return options

## Data input/output
def read_csv(filename, **options):
    with open(filename, 'r', newline='') as f:
        return pd.read_csv(f, **options)

def get_header(csv):
    header = csv[0]
    if not header[0][0].isascii():
        header[0] = header[0][1:]
    return header

def get_data_path(op):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data/source/' + op['code'])

## Colors
def is_color(color):
    return (not pd.isna(color) and len(color) > 0)

def get_color(op, route):
    if is_color(route['color']):
        return route['color']

    if op['code'] == 'carris':
        return carris_colors.get_color(db, route['code'])

    #if op == operador.barreiro:
    #    return barreiro_colors.get_color(get_code(op, route))
   # 
    #if op == operador.ml:
    #    return ml_helper.get_color(route['name'])
    #
    #if op == operador.fertagus:
    #    return '015389'
    #
    #if op == operador.transtejo:
    #    return tt_helper.get_color(route['name'])

    #if op == operador.cplisboa:
    #    return cpl_helper.get_color(route['name'])
    
    logger.warn(f'Falta a cor da carreira {route['code']} - {route['name']} do operador {op['name']}')
    return '000000'

## Route names
def get_code(op, route):
    #if op == operador.barreiro:
    #    return route['name'].split('-')[0].strip()
    #
    #if op == operador.ml:
    #    return route['name'].split('-')[0].strip()
    # 
    #if op == operador.fertagus:
    #    return 'Fertagus'
    #
    #if op == operador.transtejo:
    #    return tt_helper.get_code(route['name'])
    #
    #if op == operador.cplisboa:
    #    return cpl_helper.get_code(route['name'])
    
    return route['code']

def get_name(op, route):
    #if op == operador.barreiro:
    #    return '-'.join(route['name'].split('-')[1:]).strip()

    #if op == operador.ml:
    #    return '-'.join(route['name'].split('-')[1:]).strip()

    #if op == operador.mp:
    #    return mp_helper.get_name(route['code'])
    
    #if op == operador.cplisboa:
    #    return cpl_helper.get_name(route['name'])
    
    return route['name']

## Shapes
def read_shapes(op):
    logger.info(f'A ler linhas de {op['name']}')
    filename = os.path.join(get_data_path(op), "shapes.txt")
    dataframe = read_csv(filename)

    columns = {
        'shape_id': 'id', 
        'shape_pt_lat': 'lat', 
        'shape_pt_lon': 'lon', 
        'shape_pt_sequence': 'idx'}

    dataframe = dataframe[columns.keys()].rename(columns = columns).set_index('id')
    dataframe = dataframe.sort_values(['id', 'idx'])
    
    grouped = dataframe.groupby('id')['idx'].agg(list).apply(is_continous_list)
    errors = grouped[grouped].reset_index()['id'].to_list()
    if len(errors) > 0:
        logger.warn('Pontos errados nas linhas: ' + str(errors))

    return dataframe

def is_continous_list(l):
    if len(l) != len(set(l)):
        return False
    return (max(l) != min(l) + len(l) - 1)

def complete_shapes(op, shape_to_route, routes):
    logger.info(f'A completar linhas de {op['name']}')
    
    shape_to_route['route'] = shape_to_route['route'].apply(lambda r: next(iter(r), None))
    return pd.merge(shape_to_route, routes, left_on='route', right_index=True).drop(columns=['route'])
   
def complete_shape_points(op, shape_points):
    logger.info(f'A calcular distâncias para as linhas de {op['name']}.')
   
    return geo.compute_distance_in_path(shape_points)
    
def get_route(shape, shape_to_route, routes):
    if shape not in shape_to_route.index:
        logger.warn(f'Linha {shape} não encontrada')
        return None
    if not shape_to_route.loc[shape, 'route']:
        logger.error(f'Esta linha {shape} é muito estranha')
        return None
    route = next(iter(shape_to_route.loc[shape, 'route']), None)
    if route not in routes.index:
        logger.warn(f'Rota {route} não encontrada')
        return None
    return route

def save_shapes(op, shapes, shape_points):
    logger.info(f'A guardar {str(len(shapes))} linhas com {str(len(shape_points))} pontos de {op['name']}')
    db_shapes.save_shapes(db, op['id'], shapes, shape_points)

## Trips
def link_shape_to_routes(trips):

    shape_to_route = trips.groupby(['shape'])['route'].agg(set).reset_index().set_index('shape')

    for shape in shape_to_route[shape_to_route['route'].map(len) > 1].itertuples():
        logger.warn("Too many routes in the same shape: " + str(shape.Index) + " => " + str(shape.route))

    return shape_to_route

def read_trips(op, routes):
    logger.info(f"A ler viagens de {op['name']}.")
    filename = os.path.join(get_data_path(op), "trips.txt")
    dataframe = read_csv(filename, dtype = {'trip_headsign': 'string'})

    columns = {
        'trip_id': 'id',
        'shape_id': 'shape',
        'service_id': 'service', 
        'trip_headsign': 'headsign', 
        'route_id': 'route'}

    dataframe = dataframe[columns.keys()].rename(columns = columns).set_index('id')       
    dataframe = dataframe.merge(
        routes[['code', 'name', 'color']].add_suffix('_route'),
        how = 'left',
        left_on = 'route',
        right_index = True)

    return dataframe

def save_trips(op, trips):
    logger.info(f'A guardar {str(len(trips))} viagens de {op['name']}')
    db_trips.save_trips(db, op['id'], trips)

## Routes
def read_routes(op):
    logger.info(f'A ler rotas de {op['name']}')
    filename = os.path.join(get_data_path(op), "routes.txt")
    dataframe = read_csv(filename, dtype = {'route_color': 'string'})
    
    columns = {
        'route_id': 'id', 
        'route_short_name': 'code', 
        'route_long_name': 'name', 
        'route_color': 'color'}

    dataframe = dataframe[columns.keys()].rename(columns = columns).set_index('id')   
    dataframe = dataframe.apply(lambda route: fix_route(op, route), axis=1)

    return dataframe

def fix_route(op, route):
    route['color'] = get_color(op, route)
    route['code'] = get_code(op, route)
    route['name'] = get_name(op, route)
    return route

def save_routes(op, routes):
    logger.info(f'A guardar {str(len(routes))} rotas de {op['name']}')
    db_routes.save_routes(db, op['id'], routes)

## Stops
def read_stops(op):
    logger.info(f'A ler paragens de {op['name']}')
    filename = os.path.join(get_data_path(op), "stops.txt")
    dataframe = read_csv(filename)

    columns = {
        'stop_id': 'id', 
        'stop_name': 'name', 
        'stop_lat': 'lat', 
        'stop_lon': 'lon'}

    dataframe = dataframe[columns.keys()].rename(columns = columns).set_index('id') 

    return dataframe

def save_stops(op, stops):
    logger.info(f'A guardar {str(len(stops))} paragens de {op['name']}')
    db_stops.save_stops(db, op['id'], stops)

## Schedule
def read_schedule(op):
    logger.info(f'A ler horário de {op['name']}')
    filename = os.path.join(get_data_path(op), "stop_times.txt")
    dataframe = read_csv(filename)

    columns = {
        'trip_id': 'trip',
        'arrival_time': 'arrival',
        'departure_time': 'departure',
        'stop_id': 'stop',
        'stop_sequence': 'idx'}
    
    dataframe = dataframe[columns.keys()].rename(columns = columns)
    dataframe = dataframe.sort_values(['trip', 'idx'])
    
    return dataframe

## Main
def get_operators(options):
    global operators
    if options.operators is None:
        return operators.values()
    return [operators[code] for code in options.operators]

def main():
    load_properties()
    db_connect()
    options = parse_options()
    ops = get_operators(options)

    for op in ops:
        if options.routes or options.trips or options.shapes or options.calendar or options.schedule:
            routes = read_routes(op)
        if options.trips or options.shapes or options.calendar or options.schedule: 
            trips = read_trips(op, routes)
        if options.stops or options.shapes or options.schedule:
            stops = read_stops(op)
        if options.shapes or options.schedule:
            shape_to_route = link_shape_to_routes(trips)
            shape_points = read_shapes(op)
        if options.shapes or options.schedule or options.calendar:
            schedule = read_schedule(op)
        #if options.calendar:
        #    calendar = read_calendar(op, options.start, options.end)
        #    calendar = cal_helper.fill_calendar(op, calendar, trips, schedule)
        if options.shapes or options.schedule:
            shapes = complete_shapes(op, shape_to_route, routes)
        #    if op in (operador.cplisboa, operador.ml, operador.mp, operador.fertagus, operador.transtejo):
        #        shapes = compute_alternative_shapes(op, schedule, trips, stops)
            shape_points = complete_shape_points(op, shape_points)
        if options.routes:
            save_routes(op, routes)
        if options.shapes:
            save_shapes(op, shapes, shape_points)
        if options.trips:
            save_trips(op, trips)
        if options.stops:
            save_stops(op, stops)
        #if options.schedule:
        #    schedule = complete_shedule_with_info(op, schedule, stops, shapes, trips)
        #    save_schedule(op, schedule)
        #if options.calendar:
        #    save_calendar(op, calendar)

    logger.info('Chegou ao fim')
    db_disconnect()

main()