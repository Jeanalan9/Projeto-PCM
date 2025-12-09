"""
Callbacks do módulo de Atendimento Preventivo
"""

import dash
from dash import Input, Output, State, ctx, dcc, html, ALL
from dash.exceptions import PreventUpdate
from datetime import datetime
import dash_leaflet as dl
from constants.colors import CORES, FONTES
from funcoes.telas_atendimento_prev.atendimento_preventiva_funcao import (
    optimize_route_order, calculate_schedule, calculate_strategy_preview, 
    decimal_to_hhmm, hhmm_to_decimal
)
from funcoes.telas_atendimento_prev.pdf_generator import (
    generate_pdf, generate_pdf_protected, generate_all_activity_pdfs
)
from funcoes.telas_atendimento_prev.email_service import (
    EmailService, EmailConfig, EmailMessage, EmailAttachment,
    create_email_body_html, create_email_body_text
)
import re


def registrar_atendimento_preventivo_callbacks(app):

    @app.callback(
        Output('input-busca-equipamento', 'value'),
        Input('btn-limpar-selecao', 'n_clicks'),
        prevent_initial_call=True
    )
    def limpar_campo_busca(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return ''

    @app.callback(
        [
            Output('store-selected-equipment', 'data'),
            Output('contador-selecionados', 'children'),
            Output('config-equipamento', 'children'),
            Output('config-horas-manutencao', 'children'),
            Output({'type': 'equipment-item', 'index': ALL}, 'style'),
            Output({'type': 'equipment-checkbox', 'index': ALL}, 'children'),
            Output('btn-selecionar-todos', 'children'),
            Output('btn-selecionar-hor', 'children'),
            Output('btn-selecionar-km', 'children')
        ],
        [
            Input({'type': 'equipment-item', 'index': ALL}, 'n_clicks'),
            Input('btn-selecionar-todos', 'n_clicks'),
            Input('btn-selecionar-hor', 'n_clicks'),
            Input('btn-selecionar-km', 'n_clicks')
        ],
        [
            State('store-selected-equipment', 'data'),
            State('store-equipment', 'data'),
            State('store-visible-equipment', 'data'),
            State({'type': 'equipment-item', 'index': ALL}, 'id')
        ],
        prevent_initial_call=True
    )
    def toggle_equipment_selection(n_clicks_items, n_clicks_todos, n_clicks_hor, 
                                   n_clicks_km, selected, all_equipment, 
                                   visible_equipment, ids):
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered_id
        selected = selected or []
        visible_ids = visible_equipment or [eq['id'] for eq in all_equipment]

        btn_todos_text = 'Selecionar Todos'
        btn_hor_text = 'Selecionar HOR'
        btn_km_text = 'Selecionar KM'

        if triggered_id == 'btn-selecionar-todos':
            all_visible_selected = all(vid in selected for vid in visible_ids)
            if all_visible_selected:
                for visible_id in visible_ids:
                    if visible_id in selected:
                        selected.remove(visible_id)
                btn_todos_text = 'Selecionar Todos'
            else:
                for visible_id in visible_ids:
                    if visible_id not in selected:
                        selected.append(visible_id)
                btn_todos_text = 'Desselecionar Todos'
                    
        elif triggered_id == 'btn-selecionar-hor':
            hor_equipment = [
                eq['id'] for eq in all_equipment 
                if eq['id'] in visible_ids and eq.get('tipo') == 'HOR'
            ]
            all_hor_selected = all(eq_id in selected for eq_id in hor_equipment)
            if all_hor_selected:
                for eq_id in hor_equipment:
                    if eq_id in selected:
                        selected.remove(eq_id)
                btn_hor_text = 'Selecionar HOR'
            else:
                for eq_id in hor_equipment:
                    if eq_id not in selected:
                        selected.append(eq_id)
                btn_hor_text = 'Desselecionar HOR'
                    
        elif triggered_id == 'btn-selecionar-km':
            km_equipment = [
                eq['id'] for eq in all_equipment 
                if eq['id'] in visible_ids and eq.get('tipo') == 'KM'
            ]
            all_km_selected = all(eq_id in selected for eq_id in km_equipment)
            if all_km_selected:
                for eq_id in km_equipment:
                    if eq_id in selected:
                        selected.remove(eq_id)
                btn_km_text = 'Selecionar KM'
            else:
                for eq_id in km_equipment:
                    if eq_id not in selected:
                        selected.append(eq_id)
                btn_km_text = 'Desselecionar KM'
                    
        elif triggered_id and isinstance(triggered_id, dict) and \
             triggered_id.get('type') == 'equipment-item':
            eq_id = triggered_id['index']
            if eq_id in selected:
                selected.remove(eq_id)
            else:
                selected.append(eq_id)
        elif not any(n_clicks_items):
            raise PreventUpdate

        if all(vid in selected for vid in visible_ids) and len(visible_ids) > 0:
            btn_todos_text = 'Desselecionar Todos'
        else:
            btn_todos_text = 'Selecionar Todos'

        hor_equipment = [eq['id'] for eq in all_equipment if eq['id'] in visible_ids and eq.get('tipo') == 'HOR']
        if all(eq_id in selected for eq_id in hor_equipment) and len(hor_equipment) > 0:
            btn_hor_text = 'Desselecionar HOR'
        else:
            btn_hor_text = 'Selecionar HOR'

        km_equipment = [eq['id'] for eq in all_equipment if eq['id'] in visible_ids and eq.get('tipo') == 'KM']
        if all(eq_id in selected for eq_id in km_equipment) and len(km_equipment) > 0:
            btn_km_text = 'Desselecionar KM'
        else:
            btn_km_text = 'Selecionar KM'

        qtd_equipamentos = len(selected)
        total_hours = sum(eq['hours'] for eq in all_equipment if eq['id'] in selected)
        horas_formatadas = decimal_to_hhmm(total_hours)

        estilos = []
        checkboxes = []
        for item_id in ids:
            is_selected = item_id['index'] in selected
            estilo = {
                'padding': '14px 16px',
                'marginBottom': '10px',
                'border': f'2px solid {"#10b981" if is_selected else CORES.CINZA_MEDIO}',
                'borderRadius': '12px',
                'cursor': 'pointer',
                'background': '#ecfdf5' if is_selected else 'white',
                'transition': 'all 0.2s ease'
            }
            estilos.append(estilo)
            checkboxes.append('☑' if is_selected else '☐')

        return (selected, str(qtd_equipamentos), str(qtd_equipamentos), 
                horas_formatadas, estilos, checkboxes, btn_todos_text, btn_hor_text, btn_km_text)

    @app.callback(
        Output('store-visible-equipment', 'data'),
        Input('input-busca-equipamento', 'value'),
        State('store-equipment', 'data'),
        prevent_initial_call=True
    )
    def atualizar_equipamentos_visiveis(termo_busca, all_equipment):
        if not termo_busca or termo_busca.strip() == '':
            return [eq['id'] for eq in all_equipment]

        termo = termo_busca.lower().strip()
        visible_ids = []

        for eq in all_equipment:
            campos = [
                eq.get('patrimonio', ''),
                eq.get('name', ''),
                eq.get('farmName', ''),
                eq.get('regional', ''),
                eq.get('status', ''),
                eq.get('atividade', ''),
                eq.get('tipo', '')
            ]
            
            if any(termo in str(campo).lower() for campo in campos):
                visible_ids.append(eq['id'])

        return visible_ids

    @app.callback(
        [
            Output('config-horas-programadas', 'children'),
            Output('config-horas-disponiveis', 'children')
        ],
        [
            Input('store-selected-dates', 'data'),
            Input('store-selected-equipment', 'data')
        ],
        State('store-equipment', 'data'),
        prevent_initial_call=True
    )
    def atualizar_horas_programadas(selected_dates, selected_equip, all_equipment):
        selected_dates = selected_dates or []
        selected_equip = selected_equip or []

        num_dias = len(selected_dates)
        horas_programadas_decimal = num_dias * 9.0

        total_hours_manutencao = sum(
            eq['hours'] for eq in all_equipment if eq['id'] in selected_equip
        )
        horas_disponiveis_decimal = horas_programadas_decimal - total_hours_manutencao

        return (decimal_to_hhmm(horas_programadas_decimal), 
                decimal_to_hhmm(horas_disponiveis_decimal))

    @app.callback(
        [
            Output('modal-calendario', 'style'),
            Output('store-current-month', 'data'),
            Output('calendario-dias', 'children'),
            Output('nome-mes-atual', 'children')
        ],
        [
            Input('config-quantidade-dias', 'n_clicks'),
            Input('btn-fechar-calendario', 'n_clicks'),
            Input('btn-confirmar-datas', 'n_clicks'),
            Input('backdrop-calendario', 'n_clicks'),
            Input('btn-mes-anterior', 'n_clicks'),
            Input('btn-mes-proximo', 'n_clicks')
        ],
        [
            State('store-current-month', 'data'),
            State('store-selected-dates', 'data')
        ],
        prevent_initial_call=True
    )
    def toggle_modal_calendario(n_abrir, n_fechar, n_confirmar, n_backdrop,
                                n_anterior, n_proximo, current_month_data, 
                                selected_dates):
        from layouts.telas_atendimento_prev.atendimento_preventiva_layout import (
            criar_dias_do_mes, obter_nome_mes
        )
        from datetime import date

        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered_id
        current_year = current_month_data.get('year', date.today().year)
        current_month = current_month_data.get('month', date.today().month)
        
        selected_dates = selected_dates or []

        if triggered_id == 'btn-mes-anterior':
            if current_month == 1:
                current_month = 12
                current_year -= 1
            else:
                current_month -= 1

            new_month_data = {'year': current_year, 'month': current_month}
            dias_html = criar_dias_do_mes(current_year, current_month, selected_dates)
            nome_mes = f'{obter_nome_mes(current_month)} {current_year}'
            return {'display': 'block'}, new_month_data, dias_html, nome_mes

        elif triggered_id == 'btn-mes-proximo':
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1

            new_month_data = {'year': current_year, 'month': current_month}
            dias_html = criar_dias_do_mes(current_year, current_month, selected_dates)
            nome_mes = f'{obter_nome_mes(current_month)} {current_year}'
            return {'display': 'block'}, new_month_data, dias_html, nome_mes

        elif triggered_id == 'config-quantidade-dias':
            dias_html = criar_dias_do_mes(current_year, current_month, selected_dates)
            nome_mes = f'{obter_nome_mes(current_month)} {current_year}'
            return {'display': 'block'}, current_month_data, dias_html, nome_mes

        else:
            dias_html = criar_dias_do_mes(current_year, current_month, selected_dates)
            nome_mes = f'{obter_nome_mes(current_month)} {current_year}'
            return {'display': 'none'}, current_month_data, dias_html, nome_mes


    @app.callback(
        [
            Output('store-selected-dates', 'data'),
            Output('config-quantidade-dias', 'children'),
            Output('info-dias-calendario', 'children'),
            Output({'type': 'day-btn', 'index': ALL}, 'style')
        ],
        [
            Input({'type': 'day-btn', 'index': ALL}, 'n_clicks'),
            Input('btn-confirmar-datas', 'n_clicks')
        ],
        [
            State('store-selected-dates', 'data'),
            State({'type': 'day-btn', 'index': ALL}, 'id'),
            State('store-current-month', 'data')
        ],
        prevent_initial_call=True
    )
    def gerenciar_selecao_dias(n_clicks_dias, n_confirmar, selected_dates, ids, current_month_data):
        from datetime import date
        
        if not ctx.triggered:
            raise PreventUpdate

        selected_dates = selected_dates or []
        triggered_id = ctx.triggered_id

        if triggered_id and isinstance(triggered_id, dict) and \
        triggered_id.get('type') == 'day-btn':
            date_str = triggered_id['index']
            if date_str in selected_dates:
                selected_dates.remove(date_str)
            else:
                selected_dates.append(date_str)

        num_dias = len(selected_dates)
        info_text = f"{num_dias} dia{'s' if num_dias != 1 else ''} selecionado{'s' if num_dias != 1 else ''}"

        hoje = date.today()
        estilos = []
        for item_id in ids:
            date_str = item_id['index']
            try:
                data_btn = date.fromisoformat(date_str)
                is_passado = data_btn < hoje
                is_selected = date_str in selected_dates
            except:
                is_passado = False
                is_selected = False
            
            if is_passado:
                estilo = {
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
                estilo = {
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
                estilo = {
                    'width': '40px',
                    'height': '40px',
                    'border': f'1px solid {CORES.CINZA_MEDIO}',
                    'borderRadius': '8px',
                    'background': 'white',
                    'color': CORES.PRETO,
                    'cursor': 'pointer',
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'fontFamily': FONTES.TITULO,
                    'transition': 'all 0.2s ease'
                }
            estilos.append(estilo)

        return selected_dates, str(num_dias), info_text, estilos

    @app.callback(
        [
            Output('modal-estrategia', 'style'),
            Output('modal-alertas', 'style'),
            Output('modal-configuracao', 'style'),
            Output('loading-overlay-estrategia', 'style'),
            Output('loading-text-estrategia', 'children'),
            Output({'type': 'strategy-preview-km', 'index': ALL}, 'children'),
            Output({'type': 'strategy-preview-hours', 'index': ALL}, 'children'),
            Output('modal-validacao', 'style'),
            Output('mensagem-validacao', 'children'),
            Output('route-layer', 'children'),
            Output('store-selected-strategy', 'data', allow_duplicate=True),
            Output({'type': 'strategy-card', 'index': ALL}, 'style', allow_duplicate=True)
        ],
        Input('btn-planejar', 'n_clicks'),
        [
            State('store-selected-equipment', 'data'),
            State('store-selected-dates', 'data'),
            State('store-equipment', 'data'),
            State('store-farms', 'data'),
            State('store-start-position', 'data'),
            State('store-end-position', 'data'),
            State({'type': 'strategy-preview-km', 'index': ALL}, 'id'),
            State({'type': 'strategy-preview-hours', 'index': ALL}, 'id'),
            State('config-horas-disponiveis', 'children'),
            State('config-horas-programadas', 'children'),
            State('config-horas-manutencao', 'children'),
            State({'type': 'strategy-card', 'index': ALL}, 'id')
        ],
        prevent_initial_call=True
    )
    def mostrar_modal_estrategia_com_preview(n_clicks, selected, selected_dates, 
                                            all_equip, all_farms, start_pos, end_pos, 
                                            km_ids, hours_ids, horas_disponiveis, 
                                            horas_programadas, horas_manutencao, strategy_ids):
        if not n_clicks:
            raise PreventUpdate

        modal_alertas_style = {
            'position': 'fixed',
            'top': '80px',
            'right': '20px',
            'width': '450px',
            'maxHeight': '650px',
            'background': 'white',
            'borderRadius': '16px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
            'zIndex': 100,
            'overflow': 'hidden'
        }
        
        modal_config_style = {
            'position': 'fixed',
            'bottom': '40px',
            'left': '50%',
            'transform': 'translateX(-50%)',
            'background': 'white',
            'borderRadius': '16px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
            'padding': '20px 28px',
            'zIndex': 100
        }
        
        default_strategy_styles = [
            {
                'padding': '10px',
                'border': f'2px solid {CORES.CINZA_MEDIO}',
                'borderRadius': '10px',
                'cursor': 'pointer',
                'display': 'flex',
                'alignItems': 'center',
                'gap': '14px',
                'background': 'white',
                'transition': 'all 0.2s ease'
            }
            for _ in strategy_ids
        ]
        
        loading_style_show = {
            'display': 'flex',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3001,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        }
        
        loading_style_hide = {'display': 'none'}
        
        if not selected or len(selected) == 0:
            if not selected_dates or len(selected_dates) == 0:
                mensagem = '⚠️ Selecione pelo menos 1 equipamento e 1 dia para planejar!'
            else:
                mensagem = '⚠️ Selecione pelo menos 1 equipamento para planejar!'
            
            return (
                {'display': 'none'},
                modal_alertas_style,
                modal_config_style,
                loading_style_hide,
                'Calculando estratégias...',
                ['-- km'] * len(km_ids),
                ['--:--'] * len(hours_ids),
                {'display': 'block'},
                mensagem,
                [],
                'otimizado',
                default_strategy_styles
            )
        
        if not selected_dates or len(selected_dates) == 0:
            return (
                {'display': 'none'},
                modal_alertas_style,
                modal_config_style,
                loading_style_hide,
                'Calculando estratégias...',
                ['-- km'] * len(km_ids),
                ['--:--'] * len(hours_ids),
                {'display': 'block'},
                '⚠️ Selecione pelo menos 1 dia para planejar!',
                [],
                'otimizado',
                default_strategy_styles
            )

        try:
            selected_equipment = [eq for eq in all_equip if eq['id'] in selected]
            
            if not selected_equipment:
                return (
                    {'display': 'none'},
                    modal_alertas_style,
                    modal_config_style,
                    loading_style_hide,
                    'Calculando estratégias...',
                    ['-- km'] * len(km_ids),
                    ['--:--'] * len(hours_ids),
                    {'display': 'block'},
                    '⚠️ Nenhum equipamento válido encontrado!',
                    [],
                    'otimizado',
                    default_strategy_styles
                )
            
            horas_prog_decimal = hhmm_to_decimal(horas_programadas)
            horas_manut_decimal = hhmm_to_decimal(horas_manutencao)
            
            estrategias = ['otimizado', 'criticos']
            previews_km = []
            previews_hours = []
            estrategias_validas = []

            for estrategia in estrategias:
                preview = calculate_strategy_preview(start_pos, selected_equipment, 
                                                     all_farms, estrategia)
                
                total_horas_previsto = hhmm_to_decimal(preview['hours'])
                
                if total_horas_previsto <= horas_prog_decimal:
                    estrategias_validas.append(estrategia)
                
                previews_km.append(f"{preview['km']} km")
                previews_hours.append(preview['hours'])

            if not estrategias_validas:
                return (
                    {'display': 'none'},
                    modal_alertas_style,
                    modal_config_style,
                    loading_style_hide,
                    'Calculando estratégias...',
                    previews_km,
                    previews_hours,
                    {'display': 'block'},
                    f'⚠️ Nenhuma estratégia é compatível com o tempo disponível!\n\n'
                    f'Horas de Manutenção: {horas_manutencao}\n'
                    f'Horas Programadas: {horas_programadas}\n'
                    f'Tempo Total Necessário: {previews_hours[0]}\n\n'
                    f'Por favor, selecione mais dias ou remova alguns equipamentos.',
                    [],
                    'otimizado',
                    default_strategy_styles
                )
            
            destinations = optimize_route_order(start_pos, selected_equipment, 
                                               all_farms, 'otimizado')
            
            if not destinations:
                return (
                    {'display': 'none'},
                    modal_alertas_style,
                    modal_config_style,
                    loading_style_hide,
                    'Calculando estratégias...',
                    previews_km,
                    previews_hours,
                    {'display': 'block'},
                    '⚠️ Não foi possível otimizar a rota com os equipamentos selecionados!',
                    [],
                    'otimizado',
                    default_strategy_styles
                )
            
            days = calculate_schedule(destinations, start_pos, end_pos, selected_dates)

            cores_dias = ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6']
            rotas_mapa = []

            for idx, dia in enumerate(days):
                cor = cores_dias[idx % len(cores_dias)]
                route_geoms = dia.get('routeGeometries', [])

                for geom in route_geoms:
                    if geom and geom.get('coordinates'):
                        coords = [[c[1], c[0]] for c in geom['coordinates']]
                        rotas_mapa.append(
                            dl.Polyline(positions=coords, color=cor, weight=4, opacity=0.8)
                        )

            modal_alertas_style_opacity = modal_alertas_style.copy()
            modal_alertas_style_opacity.update({'opacity': '0.3', 'pointerEvents': 'none'})
            
            modal_config_style_opacity = modal_config_style.copy()
            modal_config_style_opacity.update({'opacity': '0.3', 'pointerEvents': 'none'})

            selected_strategy_styles = []
            for idx, card_id in enumerate(strategy_ids):
                is_selected = card_id['index'] == 'otimizado'
                estilo = {
                    'padding': '10px',
                    'border': f'2px solid {"#10b981" if is_selected else CORES.CINZA_MEDIO}',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '14px',
                    'background': '#ecfdf5' if is_selected else 'white',
                    'transition': 'all 0.2s ease'
                }
                selected_strategy_styles.append(estilo)

            return (
                {'display': 'block'},
                modal_alertas_style_opacity,
                modal_config_style_opacity,
                loading_style_hide,
                'Calculando estratégias...',
                previews_km,
                previews_hours,
                {'display': 'none'},
                '',
                rotas_mapa,
                'otimizado',
                selected_strategy_styles
            )
        except Exception as e:
            print(f"Erro no callback mostrar_modal_estrategia: {e}")
            import traceback
            traceback.print_exc()
            return (
                {'display': 'none'},
                modal_alertas_style,
                modal_config_style,
                loading_style_hide,
                'Calculando estratégias...',
                ['-- km'] * len(km_ids),
                ['--:--'] * len(hours_ids),
                {'display': 'block'},
                f'❌ Erro ao calcular rotas: {str(e)}',
                [],
                'otimizado',
                default_strategy_styles
            )

    @app.callback(
        Output('modal-validacao', 'style', allow_duplicate=True),
        Input('btn-fechar-validacao', 'n_clicks'),
        prevent_initial_call=True
    )
    def fechar_validacao(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return {'display': 'none'}

    @app.callback(
        [
            Output('store-selected-strategy', 'data', allow_duplicate=True),
            Output({'type': 'strategy-card', 'index': ALL}, 'style', allow_duplicate=True),
            Output('route-layer', 'children', allow_duplicate=True),
            Output('loading-overlay-rota', 'style'),
            Output('loading-text-rota', 'children'),
            Output('modal-validacao', 'style', allow_duplicate=True),
            Output('mensagem-validacao', 'children', allow_duplicate=True)
        ],
        Input({'type': 'strategy-card', 'index': ALL}, 'n_clicks'),
        [
            State({'type': 'strategy-card', 'index': ALL}, 'id'),
            State('store-selected-equipment', 'data'),
            State('store-equipment', 'data'),
            State('store-farms', 'data'),
            State('store-start-position', 'data'),
            State('store-end-position', 'data'),
            State('store-selected-dates', 'data'),
            State('config-horas-programadas', 'children')
        ],
        prevent_initial_call=True
    )
    def selecionar_estrategia_e_mostrar_rota(n_clicks, ids, selected_ids, all_equip,
                                            all_farms, start_pos, end_pos, selected_dates,
                                            horas_programadas):
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered_id
        
        if not triggered_id or not isinstance(triggered_id, dict) or \
           triggered_id.get('type') != 'strategy-card':
            raise PreventUpdate
            
        selected_strategy = triggered_id['index']

        estilos = []
        for card_id in ids:
            is_selected = card_id['index'] == selected_strategy
            estilo = {
                'padding': '10px',
                'border': f'2px solid {"#10b981" if is_selected else CORES.CINZA_MEDIO}',
                'borderRadius': '10px',
                'cursor': 'pointer',
                'display': 'flex',
                'alignItems': 'center',
                'gap': '14px',
                'background': '#ecfdf5' if is_selected else 'white',
                'transition': 'all 0.2s ease'
            }
            estilos.append(estilo)

        if not selected_ids or not selected_dates:
            return (selected_strategy, estilos, [], {'display': 'none'}, 
                   'Calculando rota...', {'display': 'none'}, '')

        try:
            selected_equipment = [eq for eq in all_equip if eq['id'] in selected_ids]
            
            preview = calculate_strategy_preview(start_pos, selected_equipment, 
                                                 all_farms, selected_strategy)
            
            total_horas_previsto = hhmm_to_decimal(preview['hours'])
            horas_prog_decimal = hhmm_to_decimal(horas_programadas)
            
            if total_horas_previsto > horas_prog_decimal:
                return (
                    selected_strategy,
                    estilos,
                    [],
                    {'display': 'none'},
                    'Estratégia incompatível',
                    {'display': 'block'},
                    f'⚠️ A estratégia "{selected_strategy}" não é compatível com o tempo disponível!\n\n'
                    f'Tempo Total Necessário: {preview["hours"]}\n'
                    f'Horas Programadas: {horas_programadas}\n\n'
                    f'Selecione outra estratégia ou ajuste o planejamento.'
                )
            
            destinations = optimize_route_order(start_pos, selected_equipment, 
                                               all_farms, selected_strategy)
            days = calculate_schedule(destinations, start_pos, end_pos, selected_dates)

            cores_dias = ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6']
            rotas_mapa = []

            for idx, dia in enumerate(days):
                cor = cores_dias[idx % len(cores_dias)]
                route_geoms = dia.get('routeGeometries', [])

                for geom in route_geoms:
                    if geom and geom.get('coordinates'):
                        coords = [[c[1], c[0]] for c in geom['coordinates']]
                        rotas_mapa.append(
                            dl.Polyline(positions=coords, color=cor, weight=4, opacity=0.8)
                        )

            return (selected_strategy, estilos, rotas_mapa, {'display': 'none'}, 
                   'Rota calculada', {'display': 'none'}, '')

        except Exception as e:
            print(f"Erro ao calcular rota: {e}")
            return (selected_strategy, estilos, [], {'display': 'none'}, 
                   'Erro ao calcular', {'display': 'none'}, '')

    @app.callback(
        [
            Output('store-planned-route', 'data'),
            Output('modal-estrategia', 'style', allow_duplicate=True),
            Output('modal-roteiro-ativo', 'style'),
            Output('modal-alertas', 'style', allow_duplicate=True),
            Output('modal-configuracao', 'style', allow_duplicate=True),
            Output('route-layer', 'children', allow_duplicate=True),
            Output('resumo-km', 'children'),
            Output('resumo-horas', 'children'),
            Output('timeline-dias', 'children'),
            Output('loading-overlay-atendimento', 'style')
        ],
        Input('btn-iniciar-rota', 'n_clicks'),
        [
            State('store-selected-equipment', 'data'),
            State('store-equipment', 'data'),
            State('store-farms', 'data'),
            State('store-start-position', 'data'),
            State('store-end-position', 'data'),
            State('store-selected-dates', 'data'),
            State('store-selected-strategy', 'data')
        ],
        prevent_initial_call=True
    )
    def iniciar_rota(n_clicks, selected_ids, all_equip, all_farms, start_pos,
                     end_pos, selected_dates, strategy):
        if not n_clicks or not selected_ids or not selected_dates:
            raise PreventUpdate

        loading_style_show = {
            'display': 'flex',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3003,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        }

        try:
            selected_equipment = [eq for eq in all_equip if eq['id'] in selected_ids]
            destinations = optimize_route_order(start_pos, selected_equipment, 
                                               all_farms, strategy)
            days = calculate_schedule(destinations, start_pos, end_pos, selected_dates)

            cores_dias = ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6']
            rotas_mapa = []

            for idx, dia in enumerate(days):
                cor = cores_dias[idx % len(cores_dias)]
                route_geoms = dia.get('routeGeometries', [])

                for geom in route_geoms:
                    if geom and geom.get('coordinates'):
                        coords = [[c[1], c[0]] for c in geom['coordinates']]
                        rotas_mapa.append(
                            dl.Polyline(positions=coords, color=cor, weight=4, opacity=0.8)
                        )

            total_km = sum(d.get('totalKm', 0) for d in days)
            total_hours = sum(
                d.get('totalWorkHours', 0) + d.get('totalTravelHours', 0)
                for d in days
            )
            total_hours_formatted = decimal_to_hhmm(total_hours)

            timeline = criar_timeline_dias(days, cores_dias)
            route_data = {'days': days}
            
            return (
                route_data,
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                rotas_mapa,
                f"{total_km:.0f}",
                total_hours_formatted,
                timeline,
                {'display': 'none'}
            )

        except Exception as e:
            print(f"Erro ao iniciar rota: {e}")
            raise PreventUpdate

    @app.callback(
        [
            Output('modal-estrategia', 'style', allow_duplicate=True),
            Output('modal-alertas', 'style', allow_duplicate=True),
            Output('modal-configuracao', 'style', allow_duplicate=True),
            Output('route-layer', 'children', allow_duplicate=True)
        ],
        Input('btn-cancelar-estrategia', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancelar_estrategia(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        return (
            {'display': 'none'},
            {
                'position': 'fixed',
                'top': '80px',
                'right': '20px',
                'width': '450px',
                'maxHeight': '650px',
                'background': 'white',
                'borderRadius': '16px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                'zIndex': 100,
                'overflow': 'hidden'
            },
            {
                'position': 'fixed',
                'bottom': '40px',
                'left': '50%',
                'transform': 'translateX(-50%)',
                'background': 'white',
                'borderRadius': '16px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                'padding': '20px 28px',
                'zIndex': 100
            },
            []
        )

    @app.callback(
        [
            Output('modal-roteiro-ativo', 'style', allow_duplicate=True),
            Output('modal-alertas', 'style', allow_duplicate=True),
            Output('modal-configuracao', 'style', allow_duplicate=True),
            Output('route-layer', 'children', allow_duplicate=True),
            Output('store-planned-route', 'data', allow_duplicate=True)
        ],
        Input('btn-fechar-roteiro', 'n_clicks'),
        prevent_initial_call=True
    )
    def fechar_roteiro(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        return (
            {'display': 'none'},
            {
                'position': 'fixed',
                'top': '80px',
                'right': '20px',
                'width': '450px',
                'maxHeight': '650px',
                'background': 'white',
                'borderRadius': '16px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                'zIndex': 100,
                'overflow': 'hidden'
            },
            {
                'position': 'fixed',
                'bottom': '40px',
                'left': '50%',
                'transform': 'translateX(-50%)',
                'background': 'white',
                'borderRadius': '16px',
                'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                'padding': '20px 28px',
                'zIndex': 100
            },
            [],
            None
        )

    @app.callback(
        Output('download-pdf-atendimento', 'data'),
        Input('btn-baixar-pdf', 'n_clicks'),
        [
            State('store-planned-route', 'data'),
            State('session-store', 'data')
        ],
        prevent_initial_call=True
    )
    def gerar_pdf_callback(n_clicks, route_data, session_data):
        if not n_clicks or not route_data:
            raise PreventUpdate

        try:
            days = route_data.get('days', [])
            user_name = session_data.get('nome', 'Usuário') if session_data else 'Usuário'
            pdf_bytes = generate_pdf(days, user_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"Roteiro Atendimento {timestamp}.pdf"

            return dcc.send_bytes(pdf_bytes.getvalue(), filename)
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            raise PreventUpdate

    @app.callback(
        Output('modal-email', 'style'),
        [
            Input('btn-enviar-email', 'n_clicks'),
            Input('btn-fechar-email', 'n_clicks'),
            Input('btn-cancelar-email', 'n_clicks')
        ],
        State('modal-email', 'style'),
        prevent_initial_call=True
    )
    def toggle_modal_email(n_abrir, n_fechar, n_cancelar, current_style):
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered_id
        
        if triggered_id == 'btn-enviar-email':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        [
            Output('store-email-recipients', 'data'),
            Output('email-chips-container', 'children'),
            Output('input-novo-email', 'value')
        ],
        [
            Input('btn-adicionar-email', 'n_clicks'),
            Input('input-novo-email', 'n_submit'),
            Input({'type': 'remove-email-chip', 'index': ALL}, 'n_clicks')
        ],
        [
            State('input-novo-email', 'value'),
            State('store-email-recipients', 'data'),
            State({'type': 'remove-email-chip', 'index': ALL}, 'id')
        ],
        prevent_initial_call=True
    )
    def gerenciar_lista_emails(n_add, n_submit, n_removes, novo_email, 
                               recipients, chip_ids):
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered_id
        recipients = recipients or []
        
        if triggered_id == 'btn-adicionar-email' or triggered_id == 'input-novo-email':
            if novo_email and novo_email.strip():
                email_clean = novo_email.strip()
                
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(pattern, email_clean):
                    if email_clean not in recipients:
                        recipients.append(email_clean)
                    novo_email = ''
                else:
                    chips = criar_chips_email(recipients)
                    return recipients, chips, novo_email
        
        elif triggered_id and isinstance(triggered_id, dict) and \
             triggered_id.get('type') == 'remove-email-chip':
            email_to_remove = triggered_id['index']
            if email_to_remove in recipients:
                recipients.remove(email_to_remove)
        
        chips = criar_chips_email(recipients)
        return recipients, chips, ''

    @app.callback(
        [
            Output('input-email-assunto', 'value')
        ],
        Input('modal-email', 'style'),
        [
            State('store-selected-dates', 'data')
        ],
        prevent_initial_call=True
    )
    def preencher_campos_email_inicial(modal_style, selected_dates):
        if not modal_style or modal_style.get('display') != 'block':
            raise PreventUpdate
        
        dates_str = ''
        if selected_dates:
            dates_formatted = []
            for d in sorted(selected_dates):
                try:
                    dt = datetime.fromisoformat(d)
                    dates_formatted.append(dt.strftime('%d/%m'))
                except Exception:
                    pass
            dates_str = ', '.join(dates_formatted)
        
        assunto = f"PROGRAMAÇÃO ATENDIMENTO DE PREVENTIVA - ({dates_str})"
        
        return [assunto]

    @app.callback(
        [
            Output('email-status-message', 'children'),
            Output('email-status-message', 'style'),
            Output('loading-overlay-email', 'style')
        ],
        Input('btn-confirmar-email', 'n_clicks'),
        [
            State('store-email-recipients', 'data'),
            State('input-email-assunto', 'value'),
            State('store-planned-route', 'data'),
            State('session-store', 'data')
        ],
        prevent_initial_call=True
    )
    def enviar_email_programacao(n_clicks, recipients, assunto, 
                                  route_data, session_data):
        if not n_clicks:
            raise PreventUpdate
        
        style_erro = {
            'color': '#dc2626',
            'background': '#fef2f2',
            'padding': '12px',
            'borderRadius': '8px',
            'marginTop': '10px',
            'fontSize': '13px',
            'display': 'block',
            'fontFamily': FONTES.TITULO
        }
        
        style_sucesso = {
            'color': '#16a34a',
            'background': '#f0fdf4',
            'padding': '12px',
            'borderRadius': '8px',
            'marginTop': '10px',
            'fontSize': '13px',
            'display': 'block',
            'fontFamily': FONTES.TITULO,
            'whiteSpace': 'pre-line'
        }
        
        loading_style_show = {
            'display': 'flex',
            'position': 'fixed',
            'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
            'background': 'rgba(255,255,255,0.85)',
            'backdropFilter': 'blur(4px)',
            'zIndex': 3004,
            'justifyContent': 'center',
            'alignItems': 'center',
            'flexDirection': 'column'
        }
        
        loading_style_hide = {'display': 'none'}
        
        remetente = "jeanalan104@gmail.com"
        
        if not recipients or len(recipients) == 0:
            return ("❌ Adicione pelo menos um destinatário operacional", style_erro, 
                   loading_style_hide)
        
        if not route_data or 'days' not in route_data:
            return ("❌ Nenhum roteiro disponível para enviar", style_erro, 
                   loading_style_hide)
        
        try:
            days = route_data.get('days', [])
            user_name = session_data.get('nome', 'Usuário') if session_data else 'Usuário'
            
            email_manutencao = 'auxiliaradmmanutencao@floral.ind.br'
            
            all_recipients = list(set(recipients + [email_manutencao]))
            
            attachments = []
            
            pdf_principal = generate_pdf_protected(days, user_name, password="15963")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            attachments.append(EmailAttachment(
                filename=f"Atendimento Completo {timestamp}.pdf",
                content=pdf_principal.getvalue(),
                content_type="application/pdf"
            ))
            
            activity_pdfs = generate_all_activity_pdfs(days, user_name)
            for atividade, pdf_buffer in activity_pdfs.items():
                attachments.append(EmailAttachment(
                    filename=f"Atendimento {atividade.replace(' ', '_')} {timestamp}.pdf",
                    content=pdf_buffer.getvalue(),
                    content_type="application/pdf"
                ))
            
            body_html = create_email_body_html(days, user_name)
            body_text = create_email_body_text(days, user_name)
            
            message = EmailMessage(
                sender=remetente,
                recipients=all_recipients,
                subject=assunto,
                body_html=body_html,
                body_text=body_text,
                attachments=attachments
            )
            
            config = EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                use_tls=True,
                username="jeanalan104@gmail.com",
                password="menidycvvjtmvzqj"
            )
            
            email_service = EmailService(config)
            success, msg = email_service.send_email(message)
            
            if success:
                return msg, style_sucesso, loading_style_hide
            else:
                return msg, style_erro, loading_style_hide
                
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return (f"❌ Erro inesperado: {str(e)}", style_erro, 
                   loading_style_hide)

    @app.callback(
        Output('lista-equipamentos', 'children'),
        [
            Input('store-visible-equipment', 'data')
        ],
        [
            State('store-equipment', 'data'),
            State('store-selected-equipment', 'data')
        ],
        prevent_initial_call=True
    )
    def filtrar_equipamentos(visible_ids, all_equipment, selected_ids):
        from layouts.telas_atendimento_prev.atendimento_preventiva_layout import (
            criar_item_equipamento
        )
        from consultas.telas_atendimento_prev.atendimento_preventiva_consulta import (
            Equipment
        )

        if not visible_ids:
            visible_ids = [eq['id'] for eq in all_equipment]

        items = []
        for eq_dict in all_equipment:
            if eq_dict['id'] not in visible_ids:
                continue
                
            eq = Equipment(
                id=eq_dict['id'],
                patrimonio=eq_dict['patrimonio'],
                name=eq_dict['name'],
                status=eq_dict['status'],
                hours=eq_dict['hours'],
                horimetro=eq_dict.get('horimetro', 0),
                data_lancamento=eq_dict.get('dataLancamento', ''),
                a_fazer=eq_dict.get('aFazer', ''),
                faltando=eq_dict.get('faltando', 0),
                farm_id=eq_dict.get('farmId'),
                farm_name=eq_dict.get('farmName', ''),
                regional=eq_dict.get('regional', ''),
                abbr=eq_dict.get('abbr', ''),
                atividade=eq_dict.get('atividade', ''),
                tipo=eq_dict.get('tipo', '')
            )
            items.append(criar_item_equipamento(eq, selected_ids))

        return items


def criar_chips_email(recipients):
    if not recipients:
        return html.Div('Nenhum destinatário adicionado', style={
            'fontSize': '13px',
            'color': CORES.CINZA_ESCURO,
            'fontFamily': FONTES.TITULO,
            'fontStyle': 'italic',
            'padding': '8px'
        })
    
    chips = []
    for email in recipients:
        chip = html.Div([
            html.Span(email, style={
                'fontSize': '13px',
                'color': CORES.PRETO,
                'fontFamily': FONTES.TITULO,
                'marginRight': '8px'
            }),
            html.Button('×', 
                id={'type': 'remove-email-chip', 'index': email},
                n_clicks=0,
                style={
                    'background': 'transparent',
                    'border': 'none',
                    'color': '#dc2626',
                    'fontSize': '18px',
                    'cursor': 'pointer',
                    'padding': '0 4px',
                    'lineHeight': '1',
                    'fontWeight': 'bold'
                }
            )
        ], style={
            'display': 'inline-flex',
            'alignItems': 'center',
            'background': '#e0f2fe',
            'border': '1px solid #0ea5e9',
            'borderRadius': '20px',
            'padding': '6px 12px',
            'fontSize': '13px',
            'fontFamily': FONTES.TITULO,
            'transition': 'all 0.2s ease',
            'maxWidth': '100%'
        }, title=email)
        chips.append(chip)
    
    return chips


def criar_timeline_dias(days, cores_dias):
    timeline_items = []

    for idx, day in enumerate(days):
        cor = cores_dias[idx % len(cores_dias)]

        day_card = html.Div([
            html.Div([
                html.Div([
                    html.Span(f'Dia {idx + 1}', style={
                        'fontSize': '14px',
                        'fontWeight': 'bold',
                        'color': CORES.PRETO,
                        'fontFamily': FONTES.TITULO
                    }),
                    html.Span(day.get('dateFormatted', ''), style={
                        'fontSize': '12px',
                        'color': CORES.CINZA_ESCURO,
                        'marginLeft': '8px',
                        'fontFamily': FONTES.TITULO
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '8px'
                }),
                html.Div([
                    html.Div([
                        html.Span('📏 ', style={'fontSize': '12px'}),
                        html.Span(f"{day.get('totalKm', 0):.1f} km", style={
                            'fontSize': '11px',
                            'color': '#3b82f6',
                            'fontWeight': '600',
                            'fontFamily': FONTES.TITULO
                        })
                    ], style={'marginRight': '12px'}),
                    html.Div([
                        html.Span('⏱️ ', style={'fontSize': '12px'}),
                        html.Span(
                            decimal_to_hhmm(
                                day.get('totalWorkHours', 0) + day.get('totalTravelHours', 0)
                            ),
                            style={
                                'fontSize': '11px',
                                'color': '#10b981',
                                'fontWeight': '600',
                                'fontFamily': FONTES.TITULO
                            }
                        )
                    ])
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ], style={
                'padding': '12px',
                'background': '#f8fafc',
                'borderRadius': '10px',
                'marginBottom': '10px',
                'borderLeft': f'4px solid {cor}'
            }),
            html.Div([criar_evento_timeline(ev) for ev in day.get('events', [])])
        ], style={'marginBottom': '20px'})

        timeline_items.append(day_card)

    return timeline_items


def criar_evento_timeline(evento):
    tipo = evento.get('type', '')
    desc = evento.get('desc', '')
    start = evento.get('startTime', '')
    end = evento.get('endTime', '')
    status = evento.get('status', '')
    duration = evento.get('duration', 0)
    farm_name = evento.get('farmName', '')

    icone_map = {
        'START': '📍',
        'TRAVEL': '🚗',
        'WORK': '🔧',
        'LUNCH': '☕',
        'END': '🏁'
    }

    cor_map = {
        'START': '#10b981',
        'TRAVEL': '#3b82f6',
        'WORK': '#f59e0b',
        'LUNCH': '#f97316',
        'END': '#1e293b'
    }

    icone = icone_map.get(tipo, '⚪')
    cor = cor_map.get(tipo, CORES.CINZA_MEDIO)

    cor_status = '#dc2626' if status == 'VERMELHO' else (
        '#f59e0b' if status == 'AMARELO' else '#10b981'
    )

    return html.Div([
        html.Div([
            html.Div([
                html.Span(start, style={
                    'fontSize': '11px',
                    'fontWeight': '600',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                }),
                html.Span(' → ', style={
                    'fontSize': '10px',
                    'color': CORES.CINZA_MEDIO,
                    'margin': '0 4px'
                }),
                html.Span(end, style={
                    'fontSize': '11px',
                    'fontWeight': '600',
                    'color': CORES.CINZA_ESCURO,
                    'fontFamily': FONTES.TITULO
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'marginBottom': '4px'
            }),
            html.Div([
                html.Span(icone, style={'fontSize': '14px', 'marginRight': '6px'}),
                html.Div([
                    html.Span(desc, style={
                        'fontSize': '12px',
                        'color': CORES.PRETO,
                        'fontFamily': FONTES.TITULO,
                        'flex': '1',
                        'marginBottom': '2px'
                    }),
                    html.Span(farm_name, style={
                        'fontSize': '11px',
                        'color': '#3b82f6',
                        'fontFamily': FONTES.TITULO,
                        'fontWeight': '500'
                    }) if farm_name and tipo == 'WORK' else None
                ], style={'flex': '1'}),
                html.Div([
                    html.Span(status, style={
                        'fontSize': '9px',
                        'padding': '2px 8px',
                        'borderRadius': '4px',
                        'background': cor_status,
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontFamily': FONTES.TITULO,
                        'marginRight': '8px',
                        'display': 'none' if not status else 'inline-block'
                    }) if tipo == 'WORK' else None,
                    html.Span(decimal_to_hhmm(duration), style={
                        'fontSize': '11px',
                        'color': '#64748b',
                        'fontFamily': FONTES.TITULO,
                        'fontWeight': '500'
                    }) if duration > 0 else None
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'gap': '8px'
            })
        ], style={
            'padding': '10px 12px',
            'background': 'white',
            'borderRadius': '8px',
            'marginBottom': '8px',
            'borderLeft': f'3px solid {cor}',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.05)'
        })
    ])