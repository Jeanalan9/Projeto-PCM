"""
Funções para cálculo e otimização de rotas de atendimento preventivo
Integrado com Google Gemini AI para otimização inteligente
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union
import openai

from openai import OpenAI


OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

INICIO_JORNADA = "07:00"
FIM_PREFERENCIAL = "17:00"
FIM_MAXIMO = "18:00"
ALMOCO_INICIO_IDEAL = "11:00"
ALMOCO_FIM_IDEAL = "12:00"
ALMOCO_LIMITE_MAXIMO = "13:00"
DURACAO_ALMOCO = 1.0

REGRAS_PERNOITE = {
    'Pompéu': {
        'destino_padrao': 'FAZENDA OFICINA POMPEU',
        'excecoes': {}
    },
    'Felixlândia': {
        'destino_padrao': 'FAZENDA GRAVATA',
        'excecoes': {
            'FAZENDA CARAIBAS': 'FAZENDA CARAIBAS'
        }
    },
    'Morada Nova': {
        'destino_padrao': 'FAZENDA SANTA HELENA',
        'excecoes': {
            'FAZENDA PONTAL': 'FAZENDA PONTAL'
        }
    }
}


def decimal_to_hhmm(decimal_hours):
    if decimal_hours is None:
        return "00:00"
    
    is_negative = decimal_hours < 0
    abs_hours = abs(decimal_hours)
    
    hours = int(abs_hours)
    minutes = int((abs_hours - hours) * 60)
    
    result = f"{hours:02d}:{minutes:02d}"
    return f"-{result}" if is_negative else result


def hhmm_to_decimal(time_str):
    if not time_str or time_str == "00:00":
        return 0.0
    
    is_negative = time_str.startswith('-')
    time_str = time_str.lstrip('-')
    
    try:
        hours, minutes = map(int, time_str.split(':'))
        decimal = hours + (minutes / 60.0)
        return -decimal if is_negative else decimal
    except:
        return 0.0


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def add_time(time_str, hours_to_add):
    minutes = time_to_minutes(time_str)
    minutes_to_add = int(hours_to_add * 60)
    new_minutes = minutes + minutes_to_add
    
    if new_minutes > 24 * 60:
        new_minutes = 24 * 60
    
    return minutes_to_time(new_minutes)


def time_difference(start_time, end_time):
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    return (end_minutes - start_minutes) / 60.0


def normalize_coords(coords: Union[Dict, List, Tuple]) -> Tuple[float, float]:
    if isinstance(coords, dict):
        return (coords.get('lat', 0), coords.get('lng', 0))
    elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
        return (coords[0], coords[1])
    else:
        return (0, 0)


def get_route_osrm(start, end, profile='driving'):
    try:
        start_lat, start_lng = normalize_coords(start)
        end_lat, end_lng = normalize_coords(end)
        
        url = f"http://router.project-osrm.org/route/v1/{profile}/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'false'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                return {
                    'distance': route['distance'] / 1000,
                    'duration': route['duration'] / 3600,
                    'geometry': route['geometry']
                }
    except requests.exceptions.Timeout:
        print(f"Timeout ao calcular rota OSRM")
    except Exception as e:
        print(f"Erro ao calcular rota OSRM: {e}")
    
    return None


def calculate_travel_time(start_coords, end_coords):
    start_lat, start_lng = normalize_coords(start_coords)
    end_lat, end_lng = normalize_coords(end_coords)
    
    route = get_route_osrm((start_lat, start_lng), (end_lat, end_lng))
    if route:
        return route['duration'], route['distance'], route['geometry']
    
    import math
    lat_diff = end_lat - start_lat
    lon_diff = end_lng - start_lng
    distance = math.sqrt(lat_diff**2 + lon_diff**2) * 111
    travel_time = distance / 50
    
    return travel_time, distance, None


def determinar_destino_pernoite(ultima_fazenda_nome, regional, all_farms):
    if regional not in REGRAS_PERNOITE:
        return None
    
    regras = REGRAS_PERNOITE[regional]
    
    if ultima_fazenda_nome in regras['excecoes']:
        destino_nome = regras['excecoes'][ultima_fazenda_nome]
    else:
        destino_nome = regras['destino_padrao']
    
    for farm in all_farms:
        farm_name = farm.get('name', '')
        if farm_name == destino_nome:
            return {
                'name': destino_nome,
                'coords': (farm.get('lat', 0), farm.get('lng', 0)),
                'regional': farm.get('regional', '')
            }
    
    return None


def pode_adicionar_atividade(hora_atual, duracao_atividade, tempo_deslocamento, 
                             almoco_realizado, eh_ultima_atividade=False):
    minutos_atual = time_to_minutes(hora_atual)
    minutos_fim_maximo = time_to_minutes(FIM_MAXIMO)
    minutos_fim_preferencial = time_to_minutes(FIM_PREFERENCIAL)
    minutos_limite_almoco = time_to_minutes(ALMOCO_LIMITE_MAXIMO)
    
    duracao_total_horas = tempo_deslocamento + duracao_atividade
    duracao_total_minutos = int(duracao_total_horas * 60)
    
    if not almoco_realizado:
        if minutos_atual >= time_to_minutes(ALMOCO_INICIO_IDEAL):
            duracao_total_minutos += 60
    
    minutos_fim_previsto = minutos_atual + duracao_total_minutos
    
    if minutos_fim_previsto > minutos_fim_maximo:
        if eh_ultima_atividade and tempo_deslocamento > 0:
            if minutos_fim_previsto <= minutos_fim_maximo + 30:
                return True, "Deslocamento final permitido após 18:00", {}
        
        return False, "Atividade ultrapassaria 18:00", {
            'hora_prevista_fim': minutes_to_time(minutos_fim_previsto),
            'sugestao': 'Reagendar para próximo dia'
        }
    
    if not almoco_realizado:
        if minutos_atual >= time_to_minutes("10:30"):
            minutos_fim_atividade_sem_almoco = minutos_atual + int((tempo_deslocamento + duracao_atividade) * 60)
            
            if minutos_fim_atividade_sem_almoco > time_to_minutes(ALMOCO_FIM_IDEAL):
                if minutos_fim_atividade_sem_almoco > minutos_limite_almoco:
                    return False, "Almoço ficaria depois de 13:00", {
                        'sugestao': 'Fazer almoço antes desta atividade'
                    }
    
    if minutos_fim_previsto > minutos_fim_preferencial:
        return True, "Atividade ultrapassa 17:00 mas está dentro do limite", {
            'aviso': f'Término previsto: {minutes_to_time(minutos_fim_previsto)}'
        }
    
    return True, "Atividade pode ser adicionada", {}


def inserir_almoco_dinamico(eventos, hora_atual, almoco_realizado):
    if almoco_realizado:
        return hora_atual, True
    
    minutos_atual = time_to_minutes(hora_atual)
    minutos_almoco_ideal = time_to_minutes(ALMOCO_INICIO_IDEAL)
    minutos_limite = time_to_minutes(ALMOCO_LIMITE_MAXIMO)
    
    if minutos_atual >= minutos_limite:
        eventos.append({
            'type': 'LUNCH',
            'desc': 'Almoço (atrasado)',
            'startTime': hora_atual,
            'endTime': add_time(hora_atual, DURACAO_ALMOCO),
            'duration': DURACAO_ALMOCO,
            'status': '',
            'farmName': '',
            'lat': 0,
            'lng': 0
        })
        return add_time(hora_atual, DURACAO_ALMOCO), True
    
    if minutos_atual >= minutos_almoco_ideal:
        eventos.append({
            'type': 'LUNCH',
            'desc': 'Almoço',
            'startTime': hora_atual,
            'endTime': add_time(hora_atual, DURACAO_ALMOCO),
            'duration': DURACAO_ALMOCO,
            'status': '',
            'farmName': '',
            'lat': 0,
            'lng': 0
        })
        return add_time(hora_atual, DURACAO_ALMOCO), True
    
    return hora_atual, False


def fallback_optimize(start_pos, selected_equipment, all_farms, strategy='otimizado'):
    destinations = []
    
    for equipment in selected_equipment:
        farm = None
        for f in all_farms:
            if f.get('id') == equipment.get('farmId'):
                farm = f
                break
        
        if farm:
            destinations.append({
                'id': equipment.get('id'),
                'name': equipment.get('name'),
                'patrimonio': equipment.get('patrimonio'),
                'hours': equipment.get('hours', 0),
                'status': equipment.get('status', ''),
                'aFazer': equipment.get('aFazer', ''),
                'farm': farm,
                'regional': farm.get('regional', ''),
                'prioridade': 1 if equipment.get('status') == 'VERMELHO' else (
                    2 if equipment.get('status') == 'AMARELO' else 3
                ),
                'coords': (farm.get('lat', 0), farm.get('lng', 0))
            })
    
    if strategy == 'criticos':
        destinations.sort(key=lambda x: (x['prioridade'], x['regional'], x['farm'].get('name', '')))
    else:
        destinations.sort(key=lambda x: (x['regional'], x['farm'].get('name', ''), x['prioridade']))
    
    return destinations


def optimize_with_openai(start_pos, selected_equipment, all_farms, strategy='otimizado'):
    try:
        destinations = []
        
        for equipment in selected_equipment:
            farm = None
            for f in all_farms:
                if f.get('id') == equipment.get('farmId'):
                    farm = f
                    break
            
            if farm:
                destinations.append({
                    'id': equipment.get('id'),
                    'name': equipment.get('name'),
                    'patrimonio': equipment.get('patrimonio'),
                    'hours': equipment.get('hours', 0),
                    'status': equipment.get('status', ''),
                    'aFazer': equipment.get('aFazer', ''),
                    'farm': farm,
                    'regional': farm.get('regional', ''),
                    'prioridade': 1 if equipment.get('status') == 'VERMELHO' else (
                        2 if equipment.get('status') == 'AMARELO' else 3
                    ),
                    'coords': (farm.get('lat', 0), farm.get('lng', 0))
                })
        
        # Preparar dados para prompt
        equipment_list = []
        for dest in destinations:
            equipment_list.append({
                'patrimonio': dest['patrimonio'],
                'regional': dest['regional'],
                'farm_name': dest['farm']['name'],
                'prioridade': dest['prioridade'],
                'hours': dest['hours'],
                'coords': dest['coords']
            })
        
        start_lat, start_lng = normalize_coords(start_pos)
        start_info = f"Start position: lat {start_lat}, lng {start_lng}"
        
        prompt = f"""
        Otimize a ordem de atendimento para os seguintes equipamentos, considerando:
        - Horário inicia às 07:00, preferencial 17:00 fim, máximo 18:00.
        - 1 hora almoço obrigatório por dia, ideal 11-12h, máximo até 13h, dinâmico.
        - Não ultrapassar 18h para manutenções, deslocamentos podem ligeiramente.
        - Primeiro dia inicia no ponto de partida, último termina no ponto de partida.
        - Pernoites: Pompéu -> Oficina Pompéu; Felixlândia -> Gravatá (exceto Caraíbas); Morada Nova -> Santa Helena (exceto Pontal).
        - Minimizar deslocamentos.
        - Priorizar status VERMELHO (prioridade 1), AMARELO (2), outros (3).
        - Estratégia: {strategy}
    
        Equipamentos: {equipment_list}
    
        {start_info}
    
        Retorne EXCLUSIVAMENTE um JSON no formato:
        {
        "ordem": ["PAT1", "PAT2", "PAT3"]
        }
        Não escreva mais nada além do JSON.

        """
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um otimizador de rotas para manutenções."},
                {"role": "user", "content": prompt}
            ]
        )
        
        optimized_order_str = response.choices[0].message.content.strip()

        import json

        try:
            data = json.loads(optimized_order_str)
            optimized_patrimonios = data["ordem"]
        except:
            print("IA retornou formato inválido. Usando fallback.")
            return fallback_optimize(start_pos, selected_equipment, all_farms, strategy)


        
        # Reordenar destinations baseado na ordem da IA
        optimized_destinations = []
        for pat in optimized_patrimonios:
            for dest in destinations:
                if dest['patrimonio'] == pat:
                    optimized_destinations.append(dest)
                    break
        
        if len(optimized_destinations) != len(destinations):
            print("IA retornou ordem incompleta. Usando fallback.")
            return fallback_optimize(start_pos, selected_equipment, all_farms, strategy)
        
        return optimized_destinations
    
    except Exception as e:
        print(f"Erro na otimização com OpenAI: {str(e)}. Usando fallback.")
        return fallback_optimize(start_pos, selected_equipment, all_farms, strategy)


def optimize_route_order(start_pos, selected_equipment, all_farms, strategy='otimizado'):
    # Usar OpenAI para otimizar
    return optimize_with_openai(start_pos, selected_equipment, all_farms, strategy)


def calculate_schedule(start_pos, end_pos, selected_dates, destinations, all_farms, strategy='otimizado'):
    if not selected_dates or not destinations:
        return None
    
    selected_dates.sort()
    
    days_schedule = []
    equipamentos_pendentes = destinations.copy()
    
    start_coords = normalize_coords(start_pos)
    end_coords = normalize_coords(end_pos)
    
    current_position = start_coords
    current_date = datetime.strptime(selected_dates[0], '%Y-%m-%d')
    
    for day_idx in range(len(selected_dates)):
        eh_ultimo_dia = day_idx == len(selected_dates) - 1
        
        day = {
            'date': selected_dates[day_idx],
            'dateFormatted': current_date.strftime('%d/%m/%Y'),
            'events': [],
            'totalKm': 0.0,
            'totalTravelHours': 0.0,
            'totalWorkHours': 0.0,
            'conformidade': {
                'almoco_ok': False,
                'termino_ok': True,
                'observacoes': []
            },
            'routeGeometries': [],
            'equipamentos_atendidos': []
        }
        
        hora_atual = INICIO_JORNADA
        almoco_realizado = False
        equipamentos_dia = []
        ultima_fazenda_nome = None
        ultima_regional = None
        
        day['events'].append({
            'type': 'START',
            'desc': start_pos.get('name', 'Ponto de Partida') if isinstance(start_pos, dict) else "Ponto de Partida",
            'startTime': hora_atual,
            'endTime': hora_atual,
            'duration': 0,
            'status': '',
            'farmName': '',
            'lat': start_coords[0],
            'lng': start_coords[1]
        })
        
        while equipamentos_pendentes:
            equipamento = equipamentos_pendentes[0]
            farm = equipamento.get('farm', {})
            equip_coords = normalize_coords({
                'lat': farm.get('lat', 0),
                'lng': farm.get('lng', 0)
            })
            
            duracao_manutencao = equipamento.get('hours', 0)
            
            travel_time, travel_km, geometry = calculate_travel_time(
                current_position, equip_coords
            )
            
            pode_adicionar, motivo, info = pode_adicionar_atividade(
                hora_atual, duracao_manutencao, travel_time, 
                almoco_realizado, eh_ultima_atividade=(len(equipamentos_pendentes) == 1 and eh_ultimo_dia)
            )
            
            if not pode_adicionar:
                day['conformidade']['observacoes'].append(f"{motivo} - {equipamento.get('patrimonio')}")
                break
            
            hora_fim_viagem = add_time(hora_atual, travel_time)
            
            day['events'].append({
                'type': 'TRAVEL',
                'desc': f"Deslocamento para {farm.get('name', '')}",
                'startTime': hora_atual,
                'endTime': hora_fim_viagem,
                'duration': travel_time,
                'status': '',
                'farmName': farm.get('name', ''),
                'regional': farm.get('regional', ''),
                'lat': equip_coords[0],
                'lng': equip_coords[1]
            })
            
            day['totalKm'] += travel_km
            day['totalTravelHours'] += travel_time
            
            if geometry:
                day['routeGeometries'].append(geometry)
            
            hora_atual = hora_fim_viagem
            current_position = equip_coords
        
            if not almoco_realizado:
                minutos_antes_manutencao = time_to_minutes(hora_atual)
                if minutos_antes_manutencao >= time_to_minutes(ALMOCO_INICIO_IDEAL):
                    hora_atual, almoco_realizado = inserir_almoco_dinamico(
                        day['events'], hora_atual, almoco_realizado
                    )
                    if almoco_realizado:
                        day['conformidade']['almoco_ok'] = True
            
            hora_fim_manutencao = add_time(hora_atual, duracao_manutencao)
            day['events'].append({
                'type': 'WORK',
                'desc': f'{equipamento.get("name", "Equipamento")} - {equipamento.get("aFazer", "Manutenção")}',
                'startTime': hora_atual,
                'endTime': hora_fim_manutencao,
                'duration': duracao_manutencao,
                'status': equipamento.get('status', ''),
                'farmName': farm.get('name', ''),
                'regional': farm.get('regional', ''),
                'patrimonio': equipamento.get('patrimonio', ''),
                'equipamento_id': equipamento.get('id', ''),
                'lat': equip_coords[0],
                'lng': equip_coords[1]
            })
            
            day['totalWorkHours'] += duracao_manutencao
            hora_atual = hora_fim_manutencao
            
            equipamentos_pendentes.pop(0)
            equipamentos_dia.append(equipamento.get('id'))
            day['equipamentos_atendidos'].append(equipamento.get('patrimonio', ''))
            
            ultima_fazenda_nome = farm.get('name', '')
            ultima_regional = farm.get('regional', '')
        
        if not almoco_realizado:
            hora_atual, almoco_realizado = inserir_almoco_dinamico(
                day['events'], hora_atual, almoco_realizado
            )
            day['conformidade']['almoco_ok'] = almoco_realizado
        
        if eh_ultimo_dia:
            destino_final_coords = end_coords
            destino_final_nome = end_pos.get('name', 'Retorno ao Ponto de Partida') if isinstance(end_pos, dict) else "Retorno ao Ponto de Partida"
        else:
            if ultima_fazenda_nome and ultima_regional:
                destino_pernoite = determinar_destino_pernoite(
                    ultima_fazenda_nome, ultima_regional, all_farms
                )
                if destino_pernoite:
                    destino_final_coords = destino_pernoite['coords']
                    destino_final_nome = f"Pernoite - {destino_pernoite['name']}"
                else:
                    destino_final_coords = current_position
                    destino_final_nome = f"Permanência - {ultima_fazenda_nome}"
            else:
                destino_final_coords = start_coords
                destino_final_nome = "Retorno ao Ponto de Partida"
        
        if destino_final_coords != current_position:
            travel_time_final, travel_km_final, geometry_final = calculate_travel_time(
                current_position, destino_final_coords
            )
            
            hora_fim_dia = add_time(hora_atual, travel_time_final)
            
            if time_to_minutes(hora_fim_dia) > time_to_minutes(FIM_MAXIMO):
                day['conformidade']['termino_ok'] = False
                day['conformidade']['observacoes'].append(
                    f"Deslocamento final ultrapassa 18:00 (término: {hora_fim_dia})"
                )
            
            day['events'].append({
                'type': 'END',
                'desc': destino_final_nome,
                'startTime': hora_atual,
                'endTime': hora_fim_dia,
                'duration': travel_time_final,
                'status': '',
                'farmName': '',
                'lat': destino_final_coords[0],
                'lng': destino_final_coords[1]
            })
            
            day['totalKm'] += travel_km_final
            day['totalTravelHours'] += travel_time_final
            
            if geometry_final:
                day['routeGeometries'].append(geometry_final)
            
            hora_atual = hora_fim_dia
        
        day['destino_pernoite_nome'] = destino_final_nome
        day['destino_pernoite_coords'] = destino_final_coords
        day['hora_termino'] = hora_atual
        
        days_schedule.append(day)
    
    return days_schedule


def calculate_strategy_preview(start_pos, selected_equipment, all_farms, strategy):
    destinations = optimize_route_order(start_pos, selected_equipment, all_farms, strategy)
    
    if not destinations:
        return {
            'km': '0.0',
            'hours': '00:00'
        }
    
    total_km = 0.0
    total_hours = 0.0
    current_pos = normalize_coords(start_pos)
    
    for dest in destinations:
        farm = dest.get('farm', {})
        farm_coords = normalize_coords({
            'lat': farm.get('lat', 0),
            'lng': farm.get('lng', 0)
        })
        
        if farm_coords != (0, 0):
            travel_time, travel_km, _ = calculate_travel_time(current_pos, farm_coords)
            total_km += travel_km
            total_hours += travel_time + dest.get('hours', 0)
            current_pos = farm_coords
    
    end_coords = normalize_coords(start_pos)
    travel_time, travel_km, _ = calculate_travel_time(current_pos, end_coords)
    total_km += travel_km
    total_hours += travel_time
    
    return {
        'km': f"{total_km:.1f}",
        'hours': decimal_to_hhmm(total_hours)
    }