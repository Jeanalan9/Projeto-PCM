import dash_leaflet as dl
from dash import dcc, html, Dash, Input, Output, callback
import base64
from datetime import date, timedelta
import calendar
from constants.colors import CORES, FONTES
from utils.icon_gerenciador import carregar_icone_svg
from consultas.telas_atendimento_prev.atendimento_preventiva_consulta import generate_farms, get_all_equipment

def decimal_para_hhmm(valor_decimal: float) -> str:
    horas = int(valor_decimal)
    minutos = int(round((valor_decimal - horas) * 60))
    return f"{horas:02d}:{minutos:02d}"

def criar_layout_atendimento_preventivo():
    try:
        farms = generate_farms()
        equipment = get_all_equipment()
        marcadores = criar_marcadores_fazendas(farms)

        return html.Div([
            criar_stores(equipment, farms),
            criar_mapa(marcadores),
            criar_modal_alertas(equipment),
            criar_modal_configuracao(),
            criar_modal_calendario(),
            criar_modal_estrategia(),
            criar_modal_roteiro_ativo(),
            criar_modal_email(),
            criar_loading_overlay_geral(),
            criar_loading_overlay_estrategia(),
            criar_loading_overlay_rota(),
            criar_loading_overlay_atendimento(),
            criar_loading_overlay_email(),
            criar_modal_validacao(),
            criar_modal_erro()
        ], style={
            'width': '100%',
            'height': '100vh',
            'overflow': 'hidden',
            'position': 'relative'
        })

    except Exception as e:
        return html.Div(
            f"Erro ao carregar layout: {str(e)}",
            style={'padding': '20px', 'color': 'red'}
        )
    
def criar_stores(equipment, farms):
    return html.Div([
        dcc.Store(id='store-equipment', data=[eq.to_dict() for eq in equipment]),
        dcc.Store(id='store-farms', data=[f.to_dict() for f in farms]),
        dcc.Store(id='store-selected-equipment', data=[]),
        dcc.Store(id='store-selected-dates', data=[]),
        dcc.Store(id='store-current-month', data={'year': date.today().year, 'month': date.today().month}),
        dcc.Store(id='store-start-position', data={
            'lat': -19.233086,
            'lng': -44.997034,
            'name': 'Oficina Pompéu'
        }),
        dcc.Store(id='store-end-position', data={
            'lat': -19.233086,
            'lng': -44.997034,
            'name': 'Oficina Pompéu'
        }),
        dcc.Store(id='store-planned-route', data=None),
        dcc.Store(id='store-selected-strategy', data='otimizado'),
        dcc.Store(id='store-search-term', data=''),
        dcc.Store(id='store-visible-farms', data=[f.to_dict()['id'] for f in farms]),
        dcc.Store(id='store-visible-equipment', data=[eq.to_dict()['id'] for eq in equipment]),
        dcc.Store(id='store-loading-state', data=None),
        dcc.Download(id='download-pdf-atendimento'),
    ])

def criar_marcadores_fazendas(farms):
    marcadores = []

    for farm in farms:
        cor = '#94a3b8'
        if farm.equipment:
            if any(eq.status == 'VERMELHO' for eq in farm.equipment):
                cor = '#dc2626'
            elif any(eq.status == 'AMARELO' for eq in farm.equipment):
                cor = '#f59e0b'
            else:
                cor = '#10b981'

        svg_content = f'''<svg width="40" height="40" xmlns="http://www.w3.org/2000/svg">
<circle cx="20" cy="20" r="18" fill="{cor}" stroke="white" stroke-width="3"/>
<text x="20" y="26" font-family="Arial, sans-serif" font-size="13" fill="white" text-anchor="middle" font-weight="bold">{farm.abbr}</text>
</svg>'''

        svg_encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

        marcadores.append(
            dl.Marker(
                position=[farm.lat, farm.lng],
                id={'type': 'farm-marker', 'index': farm.id},
                bubblingMouseEvents=True,
                icon={
                    "iconUrl": f"data:image/svg+xml;base64,{svg_encoded}",
                    "iconSize": [40, 40],
                    "iconAnchor": [20, 20]
                },
                children=[
                    dl.Tooltip(
                        html.Div([
                            html.Div(farm.name, style={
                                'fontWeight': 'bold',
                                'fontSize': '11px'
                            }),
                            html.Div(f"{len(farm.equipment)} equipamento(s)", style={
                                'fontSize': '9px',
                                'color': '#64748b'
                            })
                        ]),
                        permanent=False
                    )
                ]
            )
        )

    return marcadores

def criar_mapa(marcadores):
    marcador_base = dl.Marker(
        position=[-19.233086, -44.997034],
        icon={
            "iconUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjIiIGZpbGw9IiMxMGI5ODEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iNCIvPjx0ZXh0IHg9IjI1IiB5PSIzMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE4IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC13ZWlnaHQ9ImJvbGQiPkI8L3RleHQ+PC9zdmc+",
            "iconSize": [50, 50],
            "iconAnchor": [25, 25]
        },
        children=dl.Tooltip(
            "Base: Oficina Pompéu (Partida e Retorno)",
            permanent=False,
            direction="top"
        )
    )

    return dl.Map(
        id='map-atendimento',
        center=[-18.9, -45.0],
        zoom=9,
        style={
            'width': '100%',
            'height': '100vh',
            'position': 'fixed',
            'top': '60px',
            'left': '70px',
            'right': '0',
            'bottom': '25px',
            'zIndex': 1
        },
        children=[
            dl.TileLayer(
                url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            ),
            dl.TileLayer(
                url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
                attribution='&copy; OpenStreetMap &copy; CARTO',
                maxZoom=20
            ),
            dl.LayerGroup(id='markers-layer', children=marcadores),
            marcador_base,
            dl.LayerGroup(id='route-layer'),
        ]
    )


def criar_modal_alertas(equipment):
    return html.Div(
        id='modal-alertas',
        style={
            'position': 'fixed',
            'top': '80px',
            'right': '20px',
            'width': '450px',
            'maxHeight': '650px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
            'zIndex': 100,
            'overflow': 'hidden'
        },
        children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(' Alertas de Manutenção', style={
                            'fontSize': '15px',
                            'fontWeight': '600',
                            'fontFamily': FONTES.TITULO,
                            'textAlign': 'center',
                            'marginLeft': '8px',
                            'color': CORES.PRETO
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Div([
                        html.Span(
                            id='contador-selecionados',
                            children='0',
                            style={
                                'fontSize': '13px',
                                'color':CORES.BRANCO,
                                'fontFamily': FONTES.TITULO,
                                'fontWeight': 'bold'
                            }
                        ),
                        html.Span(' selecionados', style={
                            'fontSize': '13px',
                            'color':CORES.BRANCO,
                            'fontFamily': FONTES.TITULO
                        })
                    ])
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginBottom': '10px'
                }),
                html.Div([
                    html.Div([
                        html.Div([
                            carregar_icone_svg("Buscar - Pesquisa.svg", size=16)], 
                            style={'fontSize': '14px', 'marginRight': '8px', 'color': CORES.CINZA_ESCURO}),
                        dcc.Input(
                            id='input-busca-equipamento',
                            type='text',
                            placeholder='Buscar patrimônio, alerta, status, fazenda, tipo (HOR/KM)...',
                            style={
                                'flex': '1',
                                'border': 'none',
                                'outline': 'none',
                                'fontSize': '13px',
                                'fontFamily': FONTES.TITULO,
                                'background': 'transparent'
                            }
                        )
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'flex': '1',
                        'padding': '10px 14px',
                        'border': f'1px solid {CORES.CINZA_MEDIO}',
                        'borderRadius': '10px',
                        'background': 'white'
                    }),
                    html.Button('Limpar Busca', id='btn-limpar-selecao', n_clicks=0, style={
                        'background': 'white',
                        'color': '#dc2626',
                        'border': f'1px solid #dc2626',
                        'padding': '10px 16px',
                        'borderRadius': '10px',
                        'fontSize': '13px',
                        'fontWeight': '500',
                        'cursor': 'pointer',
                        'marginLeft': '10px',
                        'fontFamily': FONTES.TITULO,
                        'whiteSpace': 'nowrap'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                }),
                html.Div([
                    html.Button('Selecionar Todos', id='btn-selecionar-todos', n_clicks=0, style={
                        'flex': '1',
                        'background': '#f3f4f6',
                        'color': CORES.PRETO,
                        'border': f'1px solid {CORES.CINZA_MEDIO}',
                        'padding': '8px 12px',
                        'borderRadius': '8px',
                        'fontSize': '12px',
                        'fontWeight': '500',
                        'cursor': 'pointer',
                        'fontFamily': FONTES.TITULO,
                        'transition': 'all 0.2s ease'
                    }),
                    html.Button('Selecionar HOR', id='btn-selecionar-hor', n_clicks=0, style={
                        'flex': '1',
                        'background': '#f3f4f6',
                        'color': '#3b82f6',
                        'border': f'1px solid #93c5fd',
                        'padding': '8px 12px',
                        'borderRadius': '8px',
                        'fontSize': '12px',
                        'fontWeight': '500',
                        'cursor': 'pointer',
                        'marginLeft': '8px',
                        'fontFamily': FONTES.TITULO,
                        'transition': 'all 0.2s ease'
                    }),
                    html.Button('Selecionar KM', id='btn-selecionar-km', n_clicks=0, style={
                        'flex': '1',
                        'background': '#f3f4f6',
                        'color': '#10b981',
                        'border': f'1px solid #a7f3d0',
                        'padding': '8px 12px',
                        'borderRadius': '8px',
                        'fontSize': '12px',
                        'fontWeight': '500',
                        'cursor': 'pointer',
                        'marginLeft': '8px',
                        'fontFamily': FONTES.TITULO,
                        'transition': 'all 0.2s ease'
                    })
                ], style={
                    'display': 'flex',
                    'marginTop': '12px',
                    'gap': '8px'
                })
            ], style={
                'padding': '10px',
                'borderBottom': f'1px solid {CORES.CINZA_MEDIO}',
                'background': 'white'
            }),
            html.Div(
                id='lista-equipamentos',
                style={
                    'maxHeight': '480px',
                    'overflowY': 'auto',
                    'padding': '5px'
                },
                children=[criar_item_equipamento(eq, []) for eq in equipment]
            )
        ]
    )


def criar_item_equipamento(eq, selected_ids=None):
    if selected_ids is None:
        selected_ids = []
    
    is_selected = eq.id in selected_ids
    cor_status = '#dc2626' if eq.status == 'VERMELHO' else (
        '#f59e0b' if eq.status == 'AMARELO' else '#10b981'
    )
    
    bg_status = '#FEE2E2' if eq.status == 'VERMELHO' else (
        '#FEF3C7' if eq.status == 'AMARELO' else '#D1FAE5'
    )
    
    txt_status = '#991B1B' if eq.status == 'VERMELHO' else (
        '#92400E' if eq.status == 'AMARELO' else '#065F46'
    )
    
    cor_tipo = '#3b82f6' if eq.tipo == 'HOR' else '#10b981' if eq.tipo == 'KM' else '#64748b'
    bg_tipo = '#eff6ff' if eq.tipo == 'HOR' else '#f0fdf4' if eq.tipo == 'KM' else '#f1f5f9'

    horas_formatadas = decimal_para_hhmm(eq.hours)
    
    faltando_cor = '#dc2626' if eq.faltando < 0 else '#10b981'
    faltando_texto = f"{eq.faltando:.1f}" if eq.faltando != int(eq.faltando) else f"{int(eq.faltando)}"

    return html.Div(
        id={'type': 'equipment-item', 'index': eq.id},
        n_clicks=0,
        style={
            'padding': '14px 16px',
            'marginBottom': '5px',
            'border': f'2px solid {"#10b981" if is_selected else CORES.CINZA_MEDIO}',
            'borderRadius': '10px',
            'cursor': 'pointer',
            'background': '#ecfdf5' if is_selected else 'white',
            'transition': 'all 0.2s ease'
        },
        children=[
            html.Div([
                html.Div(
                    '☑' if is_selected else '☐',
                    id={'type': 'equipment-checkbox', 'index': eq.id},
                    style={
                        'fontSize': '20px',
                        'marginRight': '12px',
                        'color': '#10b981' if is_selected else CORES.CINZA_ESCURO
                    }
                ),
                html.Div([
                    html.Div([
                        html.Span(eq.patrimonio, style={
                            'fontSize': '14px',
                            'marginRight': '20px',
                            'fontWeight': 'bold',
                            'fontFamily': FONTES.TITULO,
                            'color': CORES.PRETO
                        }),
                        html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 6px'}),
                        html.Span(f"{eq.horimetro:.0f}", style={
                            'fontSize': '14px',
                            'marginRight': '20px',
                            'fontFamily': FONTES.TITULO,
                            'color': CORES.CINZA_ESCURO
                        }),
                        html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 6px'}),
                        html.Span(eq.data_lancamento, style={
                            'fontSize': '14px',
                            'marginRight': '20px',
                            'fontFamily': FONTES.TITULO,
                            'color': CORES.CINZA_ESCURO
                        }),
                        html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 6px'}),
                        html.Span(eq.tipo if hasattr(eq, 'tipo') and eq.tipo else 'N/A', style={
                            'fontSize': '12px',
                            'padding': '2px 8px',
                            'borderRadius': '4px',
                            'background': bg_tipo,
                            'color': cor_tipo,
                            'fontWeight': 'bold',
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'marginBottom': '5px'}),
                    html.Div(
                        eq.name[:50] + ('...' if len(eq.name) > 50 else ''),
                        style={
                            'fontSize': '13px',
                            'fontFamily': FONTES.TITULO,
                            'color': CORES.PRETO,
                            'marginBottom': '6px'
                        }
                    ),
                    html.Div([
                        html.Span('A Fazer: ', style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        }),
                        html.Span(eq.a_fazer, style={
                            'fontSize': '12px',
                            'color': '#3b82f6',
                            'fontFamily': FONTES.TITULO,
                            'fontWeight': '500'
                        }),
                        html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 6px'}),
                        html.Span('Faltando: ', style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        }),
                        html.Span(faltando_texto, style={
                            'fontSize': '12px',
                            'color': faltando_cor,
                            'fontFamily': FONTES.TITULO,
                            'fontWeight': '600'
                        })
                    ], style={'marginBottom': '6px'}),
                    html.Div([
                        html.Span(eq.farm_name, style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        }),
                        html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 6px'}),
                        html.Span(eq.regional, style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'marginBottom': '8px'}),
                    html.Div([
                        html.Span(eq.status, style={
                            'fontSize': '11px',
                            'marginRight': '20px',
                            'padding': '4px 12px',
                            'borderRadius': '6px',
                            'background': bg_status,
                            'color': txt_status,
                            'fontWeight': 'bold',
                            'fontFamily': FONTES.TITULO
                        }),
                        html.Span('Horas Manut.: ', style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        }),
                        html.Span(horas_formatadas, style={
                            'fontSize': '13px',
                            'color': CORES.CINZA_ESCURO,
                            'marginLeft': '12px',
                            'fontFamily': FONTES.TITULO,
                            'fontWeight': '500'
                        })
                    ])
                ], style={'flex': '1'})
            ], style={
                'display': 'flex',
                'alignItems': 'flex-start'
            })
        ]
    )


def criar_modal_configuracao():
    return html.Div(
        id='modal-configuracao',
        style={
            'position': 'fixed',
            'bottom': '10px',
            'left': '50%',
            'transform': 'translateX(-50%)',
            'background': CORES.CINZA_CLARO,
            'borderRadius': '10px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
            'padding': '15px',
            'zIndex': 100,
        },
        children=[
            html.Div([
                criar_card_config('QTD Equip.', 'config-equipamento', '0', '#DBEAFE', '#1E3A8A'),
                criar_divisor(),
                criar_card_config('Horas Manut.', 'config-horas-manutencao', '00:00', '#FEE2E2', '#991B1B'),
                criar_divisor(),
                criar_card_config('Horas Prog.', 'config-horas-programadas', '00:00', '#F3E8FF', '#581C87'),
                criar_divisor(),
                criar_card_config('Horas Disp.', 'config-horas-disponiveis', '00:00', '#FEF3C7', '#78350F'),
                criar_divisor(),
                html.Div([
                    html.Label('Ponto de Partida / Retorno', style={
                        'fontSize': '11px',
                        'color': CORES.CINZA_ESCURO,
                        'marginBottom': '8px',
                        'display': 'block',
                        'textAlign': 'center',
                        'fontFamily': FONTES.TITULO
                    }),
                    html.Div(id='config-ponto-retorno', children='Oficina Pompéu', style={
                        'minWidth': '160px',
                        'padding': '12px 16px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'background': '#F3F4F6',
                        'borderRadius': '8px',
                        'fontSize': '12px',
                        'color': CORES.PRETO,
                        'textAlign': 'center',
                        'fontFamily': FONTES.TITULO,
                        'height': '56px',
                        'boxSizing': 'border-box'
                    })
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                criar_divisor(),
                html.Div([
                    html.Label('QTD de Dias', style={
                        'fontSize': '11px',
                        'color': CORES.CINZA_ESCURO,
                        'marginBottom': '8px',
                        'display': 'block',
                        'textAlign': 'center',
                        'fontFamily': FONTES.TITULO
                    }),
                    html.Div(id='config-quantidade-dias', children='0', n_clicks=0, style={
                        'width': '56px',
                        'height': '56px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'background': '#D1FAE5',
                        'borderRadius': '8px',
                        'fontSize': '14px',
                        'fontWeight': 'bold',
                        'color': '#065F46',
                        'fontFamily': FONTES.TITULO,
                        'cursor': 'pointer',
                        'transition': 'all 0.2s ease'
                    })
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                criar_divisor(),
                html.Button('Planejar', id='btn-planejar', n_clicks=0, style={
                    'background': '#10b981',
                    'color': 'white',
                    'border': 'none',
                    'padding': '0 32px',
                    'borderRadius': '8px',
                    'fontSize': '14px',
                    'fontWeight': '600',
                    'cursor': 'pointer',
                    'height': '56px',
                    'boxShadow': '0 4px 14px rgba(16, 185, 129, 0.3)',
                    'transition': 'all 0.2s',
                    'fontFamily': FONTES.TITULO,
                    'marginTop': '19px'
                })
            ], style={
                'display': 'flex',
                'gap': '20px',
                'alignItems': 'flex-start'
            })
        ]
    )

def criar_card_config(label, id_valor, valor_inicial, bg_color, text_color):
    return html.Div([
        html.Label(label, style={
            'fontSize': '11px',
            'color': CORES.CINZA_ESCURO,
            'marginBottom': '8px',
            'display': 'block',
            'textAlign': 'center',
            'fontFamily': FONTES.TITULO
        }),
        html.Div(id=id_valor, children=valor_inicial, style={
            'minWidth': '70px',
            'height': '56px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'background': bg_color,
            'borderRadius': '10px',
            'fontSize': '14px',
            'fontWeight': 'bold',
            'color': text_color,
            'fontFamily': FONTES.TITULO,
            'padding': '0 10px'
        })
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})

def criar_divisor():
    return html.Div(style={
        'width': '1px',
        'height': '60px',
        'background': '#E5E7EB',
        'marginTop': '19px'
    })

def obter_nome_mes(mes: int) -> str:
    nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    return nomes[mes]

def criar_dias_do_mes(ano: int, mes: int, selected_dates=None):
    if selected_dates is None:
        selected_dates = []
        
    hoje = date.today()
    primeiro_dia = date(ano, mes, 1)
    
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)
    
    dias_no_mes = ultimo_dia.day
    dia_semana_inicio = primeiro_dia.weekday()
    
    semanas = []
    semana_atual = []
    
    for _ in range(dia_semana_inicio):
        semana_atual.append(html.Div(style={'width': '40px', 'height': '40px'}))
    
    for dia in range(1, dias_no_mes + 1):
        data_atual = date(ano, mes, dia)
        is_passado = data_atual < hoje
        is_selected = data_atual.isoformat() in selected_dates
        
        if data_atual.weekday() == 0 and semana_atual:
            semanas.append(html.Div(semana_atual, style={
                'display': 'flex',
                'gap': '4px',
                'marginBottom': '4px'
            }))
            semana_atual = []
        
        if is_passado:
            estilo_base = {
                'width': '40px',
                'height': '40px',
                'border': f'1px solid {CORES.CINZA_MEDIO}',
                'borderRadius': '8px',
                'background': '#e5e7eb',
                'cursor': 'not-allowed',
                'fontSize': '13px',
                'fontWeight': '500',
                'fontFamily': FONTES.TITULO,
                'color': '#9ca3af',
                'opacity': '0.5'
            }
        elif is_selected:
            estilo_base = {
                'width': '40px',
                'height': '40px',
                'border': '2px solid #10b981',
                'borderRadius': '8px',
                'background': '#10b981',
                'color': 'white',
                'cursor': 'pointer',
                'fontSize': '13px',
                'fontWeight': '600',
                'fontFamily': FONTES.TITULO,
                'transition': 'all 0.2s ease'
            }
        else:
            estilo_base = {
                'width': '40px',
                'height': '40px',
                'border': f'1px solid {CORES.CINZA_MEDIO}',
                'borderRadius': '8px',
                'background': 'white',
                'cursor': 'pointer',
                'fontSize': '13px',
                'fontWeight': '500',
                'fontFamily': FONTES.TITULO,
                'color': CORES.PRETO,
                'transition': 'all 0.2s ease'
            }
        
        semana_atual.append(
            html.Button(
                str(dia),
                id={'type': 'day-btn', 'index': data_atual.isoformat()},
                n_clicks=0,
                disabled=is_passado,
                style=estilo_base
            )
        )
    
    while len(semana_atual) < 7:
        semana_atual.append(html.Div(style={'width': '40px', 'height': '40px'}))
    
    if semana_atual:
        semanas.append(html.Div(semana_atual, style={
            'display': 'flex',
            'gap': '4px',
            'marginBottom': '4px'
        }))
    
    return semanas



def criar_modal_calendario():
    hoje = date.today()
    
    return html.Div(
        id='modal-calendario',
        style={'display': 'none'},
        children=[
            html.Div(style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'right': '0',
                'bottom': '0',
                'background': 'rgba(0,0,0,0.3)',
                'zIndex': 149
            }, id='backdrop-calendario'),
            html.Div([
                html.Div([
                    html.Button('◀', id='btn-mes-anterior', n_clicks=0, style={
                        'background': 'transparent',
                        'border': 'none',
                        'fontSize': '18px',
                        'cursor': 'pointer',
                        'color': CORES.CINZA_ESCURO,
                        'padding': '4px 12px',
                        'borderRadius': '6px',
                        'transition': 'all 0.2s ease'
                    }),
                    html.Span(id='nome-mes-atual', children=f'{obter_nome_mes(hoje.month)} {hoje.year}', style={
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'fontFamily': FONTES.TITULO,
                        'color': CORES.PRETO,
                        'minWidth': '150px',
                        'textAlign': 'center'
                    }),
                    html.Button('▶', id='btn-mes-proximo', n_clicks=0, style={
                        'background': 'transparent',
                        'border': 'none',
                        'fontSize': '18px',
                        'cursor': 'pointer',
                        'color': CORES.CINZA_ESCURO,
                        'padding': '4px 12px',
                        'borderRadius': '6px',
                        'transition': 'all 0.2s ease'
                    }),
                    html.Button('✕', id='btn-fechar-calendario', n_clicks=0, style={
                        'background': 'transparent',
                        'border': 'none',
                        'fontSize': '18px',
                        'cursor': 'pointer',
                        'color': CORES.CINZA_ESCURO,
                        'marginLeft': 'auto',
                        'padding': '4px 8px'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '16px',
                    'paddingBottom': '12px',
                    'borderBottom': f'1px solid {CORES.CINZA_MEDIO}'
                }),
                html.Div([
                    html.Span('Seg', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Ter', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Qua', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Qui', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Sex', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Sáb', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                    html.Span('Dom', style={'width': '40px', 'textAlign': 'center', 'fontSize': '11px', 'color': CORES.CINZA_ESCURO, 'fontWeight': '600'}),
                ], style={'display': 'flex', 'gap': '4px', 'marginBottom': '10px'}),
                html.Div(id='calendario-dias', children=criar_dias_do_mes(hoje.year, hoje.month), style={
                    'maxHeight': '280px',
                    'overflowY': 'auto'
                }),
                html.Div([
                    html.Span(id='info-dias-calendario', children='0 dias selecionados', style={
                        'fontSize': '13px',
                        'color': '#FFFFFF',
                        'fontWeight': '600',
                        'fontFamily': FONTES.TITULO
                    }),
                    html.Button('Confirmar', id='btn-confirmar-datas', n_clicks=0, style={
                        'background': '#10b981',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'borderRadius': '8px',
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'cursor': 'pointer',
                        'fontFamily': FONTES.TITULO
                    })
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginTop': '16px',
                    'paddingTop': '12px',
                    'borderTop': f'1px solid {CORES.CINZA_MEDIO}'
                })
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'background': 'white',
                'borderRadius': '16px',
                'padding': '20px',
                'boxShadow': '0 20px 60px rgba(0,0,0,0.2)',
                'zIndex': 200,
                'minWidth': '340px'
            })
        ]
    )



def criar_modal_estrategia():
    return html.Div(
        id='modal-estrategia',
        style={'display': 'none'},
        children=[
            html.Div([
                html.Div([
                    html.Span(' Estratégia de Atendimento', style={
                        'fontSize': '16px',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'color': CORES.PRETO,
                        'marginLeft': '8px'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '6px'
                }),
                html.Div('Selecione a melhor estratégia de atendimento', style={
                    'fontSize': '12px',
                    'color': CORES.CINZA_ESCURO,
                    'marginBottom': '10px',
                    'fontFamily': FONTES.TITULO
                }),
                html.Div([
                    criar_card_estrategia('otimizado', carregar_icone_svg("Icon - Otimizado.svg", size=30), 'Otimizado', 'Menor distância e tempo de deslocamento', 0),
                    criar_card_estrategia('criticos', carregar_icone_svg("Icon Cartao - Alerta Cinza.svg", size=30,), 'Criticidade', 'Prioriza os equipamentos críticos', 1),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '10px',
                    'marginBottom': '10px'
                }),
                html.Div([
                    html.Button([
                        html.Span('Visualizar Atendimento', style={'marginRight': '8px'}),
                        html.Span('→', style={'fontSize': '14px'})
                    ], id='btn-iniciar-rota', n_clicks=0, style={
                        'flex': '1',
                        'background': 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '14px 20px',
                        'borderRadius': '10px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'fontSize': '12px',
                        'boxShadow': '0 4px 12px rgba(30, 41, 59, 0.3)',
                        'transition': 'all 0.2s ease'
                    }),
                    html.Button('Cancelar', id='btn-cancelar-estrategia', n_clicks=0, style={
                        'background': 'transparent',
                        'color': CORES.CINZA_ESCURO,
                        'border': f'2px solid {CORES.CINZA_MEDIO}',
                        'padding': '14px 20px',
                        'borderRadius': '10px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontFamily': FONTES.TITULO,
                        'transition': 'all 0.2s ease'
                    })
                ], style={
                    'display': 'flex',
                    'gap': '10px'
                })
            ], style={
                'position': 'fixed',
                'top': '80px',
                'left': '90px',
                'background': 'white',
                'borderRadius': '16px',
                'padding': '10px',
                'zIndex': 150,
                'width': '340px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.15)'
            })
        ]
    )

def criar_card_estrategia(id_val, icone, titulo, desc, index):
    return html.Div(
        id={'type': 'strategy-card', 'index': id_val},
        n_clicks=0,
        style={
            'padding': '10px',
            'border': f'2px solid {CORES.CINZA_MEDIO}',
            'borderRadius': '10px',
            'cursor': 'pointer',
            'display': 'flex',
            'alignItems': 'center',
            'gap': '14px',
            'background': 'white',
            'transition': 'all 0.2s ease'
        },
        children=[
            html.Div(icone, style={
                'fontSize': '24px',
                'width': '48px',
                'height': '48px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'background': '#FFFFFF',
                'borderRadius': '10px',
                'flexShrink': '0'
            }),
            html.Div([
                html.Div(titulo, style={
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'fontFamily': FONTES.TITULO,
                    'color': CORES.PRETO
                }),
                html.Div(desc, style={
                    'fontSize': '12px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO,
                    'marginTop': '2px'
                }),
                html.Div([
                    html.Span(carregar_icone_svg("Icon - Distancia.svg", size=16), style={'marginRight': '10px'}),
                    html.Span(id={'type': 'strategy-preview-km', 'index': index}, children='-- km', style={
                        'fontSize': '11px',
                        'fontWeight': '600',
                        'color': '#3b82f6',
                        'fontFamily': FONTES.TITULO
                    }),
                    html.Span(' • ', style={'color': CORES.CINZA_MEDIO, 'margin': '0 4px'}),
                    html.Span(carregar_icone_svg("Icon - Tempo AT.svg", size=16), style={'marginRight': '10px'}),
                    html.Span(id={'type': 'strategy-preview-hours', 'index': index}, children='--:--', style={
                        'fontSize': '11px',
                        'fontWeight': '600',
                        'color': '#10b981',
                        'fontFamily': FONTES.TITULO
                    })
                ], style={'marginTop': '6px'})
            ], style={'flex': '1'})
        ]
    )



def criar_modal_roteiro_ativo():
    return html.Div(
        id='modal-roteiro-ativo',
        style={'display': 'none'},
        children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(' Atendimento Ativo', style={
                                'fontSize': '18px',
                                'fontWeight': 'bold',
                                'fontFamily': FONTES.TITULO,
                                'marginLeft': '8px',
                                'color': 'white'
                            })
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        html.Button('✕', id='btn-fechar-roteiro', n_clicks=0, style={
                            'background': CORES.PRETO,
                            'border': 'none',
                            'color': 'white',
                            'cursor': 'pointer',
                            'fontSize': '16px',
                            'borderRadius': '8px',
                            'padding': '6px 10px',
                            'transition': 'all 0.2s ease'
                        })
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'alignItems': 'center',
                        'marginBottom': '16px'
                    }),
                    html.Div([
                        html.Div([
                            html.Div('DISTÂNCIA', style={
                                'fontSize': '10px',
                                'color': 'rgba(255,255,255,0.7)',
                                'fontFamily': FONTES.TITULO,
                                'letterSpacing': '1px'
                            }),
                            html.Div([
                                html.Span(id='resumo-km', children='0', style={
                                    'fontSize': '32px',
                                    'fontWeight': 'bold',
                                    'color': CORES.BRANCO,
                                    'fontFamily': FONTES.TITULO
                                }),
                                html.Span(' km', style={
                                    'fontSize': '14px',
                                    'color': 'rgba(255,255,255,0.8)',
                                    'fontFamily': FONTES.TITULO
                                })
                            ])
                        ], style={
                            'flex': '1',
                            'textAlign': 'center',
                            'padding': '12px',
                            'background': CORES.PRETO,
                            'borderRadius': '12px'
                        }),
                        html.Div([
                            html.Div('TEMPO TOTAL', style={
                                'fontSize': '10px',
                                'color': 'rgba(255,255,255,0.7)',
                                'fontFamily': FONTES.TITULO,
                                'letterSpacing': '1px'
                            }),
                            html.Div([
                                html.Span(id='resumo-horas', children='00:00', style={
                                    'fontSize': '32px',
                                    'fontWeight': 'bold',
                                    'color': CORES.BRANCO,
                                    'fontFamily': FONTES.TITULO
                                })
                            ])
                        ], style={
                            'flex': '1',
                            'textAlign': 'center',
                            'padding': '12px',
                            'background': CORES.PRETO,
                            'borderRadius': '12px'
                        })
                    ], style={'display': 'flex', 'gap': '12px'})
                ], style={
                    'background': CORES.PRETO_ESCURO,
                    'padding': '20px',
                    'borderRadius': '16px 16px 0 0'
                }),
                html.Div([
                    html.Div([
                        html.Span('Mostrar todas fazendas', style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontWeight': '500',
                            'fontFamily': FONTES.TITULO
                        }),
                        dcc.Checklist(
                            id='toggle-todas-fazendas',
                            options=[{'label': '', 'value': 'show'}],
                            value=[],
                            style={'marginLeft': '8px'}
                        )
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'space-between',
                        'padding': '14px 16px',
                        'borderBottom': f'1px solid {CORES.CINZA_MEDIO}',
                        'background': '#fafafa'
                    }),
                    html.Div(
                        id='timeline-dias',
                        style={
                            'maxHeight': '400px',
                            'overflowY': 'auto',
                            'padding': '16px'
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Button([
                                '📄 Baixar PDF do Atendimento'
                            ], id='btn-baixar-pdf', n_clicks=0, style={
                                'flex': '1',
                                'background': CORES.PRETO_ESCURO,
                                'color': 'white',
                                'border': 'none',
                                'padding': '16px',
                                'borderRadius': '12px',
                                'cursor': 'pointer',
                                'fontWeight': 'bold',
                                'fontFamily': FONTES.TITULO,
                                'fontSize': '14px',
                                'boxShadow': '0 4px 12px rgba(30, 41, 59, 0.2)',
                                'transition': 'all 0.2s ease',
                                'marginRight': '10px'
                            }),
                            html.Button([
                                '✉️ Enviar por E-mail'
                            ], id='btn-enviar-email', n_clicks=0, style={
                                'flex': '1',
                                'background': '#3b82f6',
                                'color': 'white',
                                'border': 'none',
                                'padding': '16px',
                                'borderRadius': '12px',
                                'cursor': 'pointer',
                                'fontWeight': 'bold',
                                'fontFamily': FONTES.TITULO,
                                'fontSize': '14px',
                                'boxShadow': '0 4px 12px rgba(59, 130, 246, 0.3)',
                                'transition': 'all 0.2s ease'
                            })
                        ], style={
                            'display': 'flex',
                            'gap': '10px',
                            'marginBottom': '10px'
                        })
                    ], style={'padding': '16px', 'borderTop': f'1px solid {CORES.CINZA_MEDIO}'})
                ], style={'background': 'white'})
            ], style={
                'position': 'fixed',
                'top': '80px',
                'right': '20px',
                'width': '400px',
                'background': 'white',
                'borderRadius': '16px',
                'boxShadow': '0 12px 40px rgba(0,0,0,0.15)',
                'zIndex': 200,
                'overflow': 'hidden'
            })
        ]
    )


def criar_modal_email():
    return html.Div(
        id='modal-email',
        style={'display': 'none'},
        children=[
            html.Div(
                style={
                    'position': 'fixed',
                    'top': 0,
                    'left': 0,
                    'right': 0,
                    'bottom': 0,
                    'background': 'rgba(0,0,0,0.6)',
                    'zIndex': 299
                }
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.Span('✉️', style={'fontSize': '24px', 'marginRight': '10px'}),
                        html.Span('Enviar Programação por E-mail', style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Button('✕', id='btn-fechar-email', n_clicks=0, style={
                        'background': 'transparent',
                        'border': 'none',
                        'cursor': 'pointer',
                        'fontSize': '20px',
                        'color': CORES.CINZA_ESCURO
                    })
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginBottom': '24px',
                    'paddingBottom': '16px',
                    'borderBottom': f'1px solid {CORES.CINZA_MEDIO}'
                }),
                
                dcc.Store(id='store-email-recipients', data=[]),
                
                html.Div([
                    html.Label('E-mail do Remetente (Fixo)', style={
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'color': CORES.CINZA_ESCURO,
                        'fontFamily': FONTES.TITULO,
                        'marginBottom': '6px',
                        'display': 'block'
                    }),
                    html.Div([
                        html.Span('jeanalan104@gmail.com', style={
                            'fontSize': '14px',
                            'color': CORES.PRETO,
                            'fontFamily': FONTES.TITULO,
                        }),
                    ], style={
                        'padding': '12px 16px',
                        'border': f'1px solid {CORES.CINZA_MEDIO}',
                        'borderRadius': '10px',
                        'background': '#f9fafb'
                    })
                ], style={'marginBottom': '16px'}),
                
                html.Div([
                    html.Label('Destinatários Operacionais', style={
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'color': CORES.CINZA_ESCURO,
                        'fontFamily': FONTES.TITULO,
                        'marginBottom': '6px',
                        'display': 'block'
                    }),
                    
                    html.Div(
                        id='email-chips-container',
                        style={
                            'minHeight': '50px',
                            'maxHeight': '150px',
                            'overflowY': 'auto',
                            'padding': '8px',
                            'border': f'1px solid {CORES.CINZA_MEDIO}',
                            'borderRadius': '10px',
                            'background': 'white',
                            'display': 'flex',
                            'flexWrap': 'wrap',
                            'gap': '8px',
                            'alignItems': 'flex-start',
                            'marginBottom': '8px'
                        }
                    ),
                    
                    html.Div([
                        dcc.Input(
                            id='input-novo-email',
                            type='email',
                            placeholder='Digite um e-mail operacional e pressione Enter',
                            style={
                                'flex': '1',
                                'padding': '10px 14px',
                                'border': f'1px solid {CORES.CINZA_MEDIO}',
                                'borderRadius': '8px',
                                'fontSize': '13px',
                                'fontFamily': FONTES.TITULO,
                                'boxSizing': 'border-box'
                            }
                        ),
                        html.Button('+ Adicionar', id='btn-adicionar-email', n_clicks=0, style={
                            'background': '#10b981',
                            'color': 'white',
                            'border': 'none',
                            'padding': '10px 16px',
                            'borderRadius': '8px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'marginLeft': '8px',
                            'fontFamily': FONTES.TITULO,
                            'whiteSpace': 'nowrap'
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    
                    html.Span('Pressione Enter ou clique em Adicionar para cada e-mail', style={
                        'fontSize': '11px',
                        'color': CORES.CINZA_ESCURO,
                        'fontFamily': FONTES.TITULO,
                        'marginTop': '4px',
                        'display': 'block'
                    })
                ], style={'marginBottom': '16px'}),
                
                html.Div([
                    html.Label('Destinatários Manutenção (Fixos)', style={
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'color': CORES.CINZA_ESCURO,
                        'fontFamily': FONTES.TITULO,
                        'marginBottom': '6px',
                        'display': 'block'
                    }),
                    
                    html.Div([
                        html.Div([
                            html.Span('auxiliaradmmanutencao@floral.ind.br', style={
                                'fontSize': '13px',
                                'color': CORES.PRETO,
                                'fontFamily': FONTES.TITULO,
                            }),
                        ], style={
                            'display': 'inline-flex',
                            'alignItems': 'center',
                            'background': '#dcfce7',
                            'border': '1px solid #10b981',
                            'borderRadius': '20px',
                            'padding': '6px 12px',
                            'fontSize': '13px',
                            'fontFamily': FONTES.TITULO,
                        })
                    ], style={
                        'minHeight': '50px',
                        'padding': '8px',
                        'border': f'1px solid {CORES.CINZA_MEDIO}',
                        'borderRadius': '10px',
                        'background': '#f9fafb',
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'gap': '8px',
                        'alignItems': 'flex-start',
                    }),
                    
                    html.Span('Este e-mail receberá automaticamente a programação', style={
                        'fontSize': '11px',
                        'color': '#10b981',
                        'fontFamily': FONTES.TITULO,
                        'marginTop': '4px',
                        'display': 'block',
                        'fontWeight': '500'
                    })
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Label('Assunto', style={
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'color': CORES.CINZA_ESCURO,
                        'fontFamily': FONTES.TITULO,
                        'marginBottom': '6px',
                        'display': 'block'
                    }),
                    dcc.Input(
                        id='input-email-assunto',
                        type='text',
                        placeholder='PROGRAMAÇÃO ATENDIMENTO DE PREVENTIVA',
                        style={
                            'width': '100%',
                            'padding': '12px 16px',
                            'border': f'1px solid {CORES.CINZA_MEDIO}',
                            'borderRadius': '10px',
                            'fontSize': '14px',
                            'fontFamily': FONTES.TITULO,
                            'boxSizing': 'border-box'
                        }
                    )
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.Span('📎', style={'fontSize': '16px', 'marginRight': '8px'}),
                        html.Span('Anexos incluídos:', style={
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'color': CORES.PRETO,
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'marginBottom': '10px'}),
                    html.Ul([
                        html.Li([
                            html.Span('🔒 ', style={'marginRight': '4px'}),
                            'Atendimento Completo (PDF protegido - senha: 15963)'
                        ], style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO,
                            'marginBottom': '6px'
                        }),
                        html.Li('PDFs separados por atividade', style={
                            'fontSize': '12px',
                            'color': CORES.CINZA_ESCURO,
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'margin': '0', 'paddingLeft': '20px'})
                ], style={
                    'background': '#f8fafc',
                    'padding': '16px',
                    'borderRadius': '10px',
                    'marginBottom': '20px',
                    'border': f'1px solid {CORES.CINZA_MEDIO}'
                }),
                
                html.Div(
                    id='email-status-message',
                    style={'display': 'none'}
                ),
                
                html.Div([
                    html.Button('Cancelar', id='btn-cancelar-email', n_clicks=0, style={
                        'flex': '1',
                        'background': '#f1f5f9',
                        'color': CORES.CINZA_ESCURO,
                        'border': 'none',
                        'padding': '14px',
                        'borderRadius': '10px',
                        'cursor': 'pointer',
                        'fontWeight': '600',
                        'fontFamily': FONTES.TITULO,
                        'fontSize': '14px'
                    }),
                    html.Button('📤 Enviar E-mail', id='btn-confirmar-email', n_clicks=0, style={
                        'flex': '2',
                        'background': '#3b82f6',
                        'color': 'white',
                        'border': 'none',
                        'padding': '14px',
                        'borderRadius': '10px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'fontSize': '14px',
                        'boxShadow': '0 4px 12px rgba(59, 130, 246, 0.3)'
                    })
                ], style={
                    'display': 'flex',
                    'gap': '12px',
                    'marginTop': '16px'
                })
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'background': 'white',
                'borderRadius': '16px',
                'padding': '28px',
                'zIndex': 300,
                'width': '550px',
                'maxHeight': '90vh',
                'overflowY': 'auto',
                'boxShadow': '0 20px 60px rgba(0,0,0,0.25)'
            })
        ]
    )

def criar_loading_overlay_geral():
    return html.Div(
        id='loading-overlay',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3000,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        },
        children=[
            html.Div(style={
                'width': '60px',
                'height': '60px',
                'border': '4px solid #e2e8f0',
                'borderTop': '4px solid #10b981',
                'borderRadius': '50%',
                'animation': 'spin 1s linear infinite'
            }),
            html.Div(
                'Carregando...',
                id='loading-text',
                style={
                    'marginTop': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': '#1e293b',
                    'fontFamily': FONTES.TITULO
                }
            ),
            html.Div(
                'Por favor, aguarde',
                style={
                    'marginTop': '8px',
                    'fontSize': '14px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }
            )
        ]
    )

def criar_loading_overlay_estrategia():
    return html.Div(
        id='loading-overlay-estrategia',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3001,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        },
        children=[
            html.Div(style={
                'width': '60px',
                'height': '60px',
                'border': '4px solid #e2e8f0',
                'borderTop': '4px solid #3b82f6',
                'borderRadius': '50%',
                'animation': 'spin 1s linear infinite'
            }),
            html.Div(
                'Calculando estratégias...',
                id='loading-text-estrategia',
                style={
                    'marginTop': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': '#1e293b',
                    'fontFamily': FONTES.TITULO
                }
            ),
            html.Div(
                'Analisando as melhores opções',
                style={
                    'marginTop': '8px',
                    'fontSize': '14px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }
            )
        ]
    )

def criar_loading_overlay_rota():
    return html.Div(
        id='loading-overlay-rota',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3002,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        },
        children=[
            html.Div(style={
                'width': '60px',
                'height': '60px',
                'border': '4px solid #e2e8f0',
                'borderTop': '4px solid #f59e0b',
                'borderRadius': '50%',
                'animation': 'spin 1s linear infinite'
            }),
            html.Div(
                'Calculando rota...',
                id='loading-text-rota',
                style={
                    'marginTop': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': '#1e293b',
                    'fontFamily': FONTES.TITULO
                }
            ),
            html.Div(
                'Otimizando o trajeto',
                style={
                    'marginTop': '8px',
                    'fontSize': '14px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }
            )
        ]
    )

def criar_loading_overlay_atendimento():
    return html.Div(
        id='loading-overlay-atendimento',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3003,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        },
        children=[
            html.Div(style={
                'width': '60px',
                'height': '60px',
                'border': '4px solid #e2e8f0',
                'borderTop': '4px solid #10b981',
                'borderRadius': '50%',
                'animation': 'spin 1s linear infinite'
            }),
            html.Div(
                'Iniciando atendimento...',
                id='loading-text-atendimento',
                style={
                    'marginTop': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': '#1e293b',
                    'fontFamily': FONTES.TITULO
                }
            ),
            html.Div(
                'Preparando roteiro',
                style={
                    'marginTop': '8px',
                    'fontSize': '14px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }
            )
        ]
    )

def criar_loading_overlay_email():
    return html.Div(
        id='loading-overlay-email',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3004,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        },
        children=[
            html.Div(style={
                'width': '60px',
                'height': '60px',
                'border': '4px solid #e2e8f0',
                'borderTop': '4px solid #3b82f6',
                'borderRadius': '50%',
                'animation': 'spin 1s linear infinite'
            }),
            html.Div(
                'Enviando e-mail...',
                id='loading-text-email',
                style={
                    'marginTop': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': '#1e293b',
                    'fontFamily': FONTES.TITULO
                }
            ),
            html.Div(
                'Por favor, aguarde',
                style={
                    'marginTop': '8px',
                    'fontSize': '14px',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }
            )
        ]
    )

def criar_modal_validacao():
    return html.Div(
        id='modal-validacao',
        style={'display': 'none'},
        children=[
            html.Div(style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'right': '0',
                'bottom': '0',
                'background': 'rgba(0,0,0,0.5)',
                'zIndex': 2999
            }),
            html.Div([
                html.Div([
                    html.Span('⚠️', style={'fontSize': '28px'}),
                    html.Span('Atenção!', style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'marginLeft': '12px'
                    })
                ], style={'marginBottom': '16px', 'color': '#f59e0b', 'display': 'flex', 'alignItems': 'center'}),
                html.Div(
                    id='mensagem-validacao',
                    children='Por favor, verifique os dados inseridos.',
                    style={
                        'fontSize': '14px',
                        'color': CORES.CINZA_ESCURO,
                        'marginBottom': '20px',
                        'fontFamily': FONTES.TITULO,
                        'lineHeight': '1.5',
                        'whiteSpace': 'pre-line'
                    }
                ),
                html.Button('Entendido', id='btn-fechar-validacao', n_clicks=0, style={
                    'width': '100%',
                    'background': '#fef3c7',
                    'color': '#f59e0b',
                    'border': '2px solid #fde68a',
                    'padding': '14px',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'fontFamily': FONTES.TITULO,
                    'fontSize': '14px',
                    'transition': 'all 0.2s ease'
                })
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'background': 'white',
                'borderRadius': '16px',
                'padding': '28px',
                'zIndex': 3000,
                'maxWidth': '420px',
                'boxShadow': '0 20px 60px rgba(0,0,0,0.25)',
                'borderLeft': '6px solid #f59e0b'
            })
        ]
    )


def criar_modal_erro():
    return html.Div(
        id='modal-erro',
        style={'display': 'none'},
        children=[
            html.Div(style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'right': '0',
                'bottom': '0',
                'background': 'rgba(0,0,0,0.5)',
                'zIndex': 2999
            }),
            html.Div([
                html.Div([
                    html.Span('⚠️', style={'fontSize': '28px'}),
                    html.Span('Limite Excedido!', style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'marginLeft': '12px'
                    })
                ], style={'marginBottom': '16px', 'color': '#dc2626', 'display': 'flex', 'alignItems': 'center'}),
                html.Div(
                    id='mensagem-erro',
                    children='O planejamento ultrapassa 10 horas diárias.',
                    style={
                        'fontSize': '14px',
                        'color': CORES.CINZA_ESCURO,
                        'marginBottom': '20px',
                        'fontFamily': FONTES.TITULO,
                        'lineHeight': '1.5'
                    }
                ),
                html.Button('Entendido, ajustar planejamento', id='btn-fechar-erro', n_clicks=0, style={
                    'width': '100%',
                    'background': '#fee2e2',
                    'color': '#dc2626',
                    'border': '2px solid #fecaca',
                    'padding': '14px',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'fontFamily': FONTES.TITULO,
                    'fontSize': '14px',
                    'transition': 'all 0.2s ease'
                })
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'background': 'white',
                'borderRadius': '16px',
                'padding': '28px',
                'zIndex': 3000,
                'maxWidth': '420px',
                'boxShadow': '0 20px 60px rgba(0,0,0,0.25)',
                'borderLeft': '6px solid #dc2626'
            })
        ]
    )