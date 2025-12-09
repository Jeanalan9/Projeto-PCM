"""
Gerador de PDF do módulo de Atendimento Preventivo
"""

import io
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

MAPEAMENTO_PATRIMONIO_ATIVIDADE = {
    'FEL': 'COLHEITA',
    'GAR': 'COLHEITA',
    'GRU': 'COLHEITA',
    'SKD': 'COLHEITA',
    'PAC': 'SILVICULTURA',
    'TRA': 'SILVICULTURA',
    'CMK': 'CARVOARIA',
    'CTC': 'CARVOARIA',
    'CTL': 'CARVOARIA',
    'CTQ': 'CARVOARIA',
    'CPP': 'CARVOARIA',
    'ONB': 'AGRICULTURA',
    'VCL': 'AGRICULTURA',
    'VPG': 'AGRICULTURA',
    'VPL': 'AGRICULTURA',
}

ATIVIDADES_DISPONIVEIS = [
    'SILVICULTURA',
    'COLHEITA',
    'CARVOARIA',
    'OBRAS CIVIS',
    'AGRICULTURA',
    'PECUARIA'
]

EMERALD_600 = colors.HexColor('#000000')
EMERALD_100 = colors.HexColor('#d1fae5')
SLATE_800 = colors.HexColor('#1e293b')
SLATE_600 = colors.HexColor('#475569')
SLATE_100 = colors.HexColor('#f1f5f9')
SLATE_50 = colors.HexColor('#f8fafc')
RED_600 = colors.HexColor('#dc2626')
AMBER_600 = colors.HexColor('#d97706')
ORANGE_50 = colors.HexColor('#fff7ed')
BLUE_600 = colors.HexColor('#2563eb')
BLUE_50 = colors.HexColor('#eff6ff')

PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
MARGIN = 1 * cm
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)


def decimal_to_hhmm(decimal_hours):
    if decimal_hours is None:
        return "00:00"
    
    is_negative = decimal_hours < 0
    abs_hours = abs(decimal_hours)
    
    hours = int(abs_hours)
    minutes = int((abs_hours - hours) * 60)
    
    result = f"{hours:02d}:{minutes:02d}"
    return f"-{result}" if is_negative else result


def get_atividade_from_patrimonio(patrimonio: str) -> str:
    if not patrimonio:
        return 'SILVICULTURA'
    prefixo = patrimonio[:3].upper()
    return MAPEAMENTO_PATRIMONIO_ATIVIDADE.get(prefixo, 'SILVICULTURA')


def extract_patrimonio_from_desc(desc: str) -> str:
    if not desc:
        return ''
    parts = desc.split(' - ')
    if len(parts) >= 2:
        return parts[0].strip()
    words = desc.split()
    if words:
        return words[0].strip()
    return ''


def generate_qr_code(url: str) -> io.BytesIO:
    if not QRCODE_AVAILABLE:
        return None

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def build_google_maps_url_from_locations(locations: List) -> str:
    if not locations or len(locations) < 2:
        return "https://www.google.com/maps"

    origin = locations[0]
    destination = locations[-1]
    mid_points = locations[1:-1] if len(locations) > 2 else []

    unique_points = []
    for i, p in enumerate(mid_points):
        if i == 0 or (p[0] != mid_points[i - 1][0] or p[1] != mid_points[i - 1][1]):
            unique_points.append(p)

    if len(unique_points) > 8:
        step = len(unique_points) // 8
        unique_points = unique_points[::step][:8]

    waypoints_str = '|'.join([f"{p[0]},{p[1]}" for p in unique_points])

    url = (f"https://www.google.com/maps/dir/?api=1"
           f"&origin={origin[0]},{origin[1]}"
           f"&destination={destination[0]},{destination[1]}")

    if waypoints_str:
        url += f"&waypoints={waypoints_str}"

    url += "&travelmode=driving"

    return url


def build_google_maps_url_from_events(events: List[Dict], start_pos: tuple = None) -> str:
    if start_pos is None:
        start_pos = (-19.233086, -44.997034)

    locations = [start_pos]

    for event in events:
        lat = event.get('lat')
        lng = event.get('lng')
        if lat is not None and lng is not None:
            coord = (lat, lng)
            if not locations or coord != locations[-1]:
                locations.append(coord)

    locations.append(start_pos)

    if len(locations) < 2:
        return "https://www.google.com/maps"

    origin = locations[0]
    destination = locations[-1]

    mid_points = []
    for i, loc in enumerate(locations[1:-1]):
        if i == 0 or loc != locations[i]:
            mid_points.append(loc)

    if len(mid_points) > 10:
        step = len(mid_points) // 10
        mid_points = mid_points[::step][:10]

    url = f"https://www.google.com/maps/dir/?api=1"
    url += f"&origin={origin[0]},{origin[1]}"
    url += f"&destination={destination[0]},{destination[1]}"

    if mid_points:
        waypoints_str = '|'.join([f"{p[0]},{p[1]}" for p in mid_points])
        url += f"&waypoints={waypoints_str}"

    url += "&travelmode=driving"

    return url


def protect_pdf_with_password(pdf_buffer: io.BytesIO, password: str) -> io.BytesIO:
    try:
        from PyPDF2 import PdfReader, PdfWriter

        pdf_buffer.seek(0)
        reader = PdfReader(pdf_buffer)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer

    except ImportError:
        print("PyPDF2 não instalado. PDF será gerado sem proteção.")
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        print(f"Erro ao proteger PDF: {e}")
        pdf_buffer.seek(0)
        return pdf_buffer


def generate_pdf(days: List[Dict], user_name: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    title_style = ParagraphStyle(
        'CustomTitle',
        fontSize=16,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        leading=20
    )

    header_info_style = ParagraphStyle(
        'HeaderInfo',
        fontSize=9,
        textColor=colors.white,
        fontName='Helvetica',
        alignment=TA_RIGHT
    )

    summary_title_style = ParagraphStyle(
        'SummaryTitle',
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        textColor=SLATE_800
    )

    elements = []

    generated_at = datetime.now().strftime('%d/%m/%Y às %H:%M')
    header_text = f"Gerado: {generated_at}  •  Por: {user_name}"

    header_data = [[
        Paragraph("ATENDIMENTO PREVENTIVAS", title_style),
        Paragraph(header_text, header_info_style)
    ]]

    header_table = Table(header_data, colWidths=[CONTENT_WIDTH * 0.55, CONTENT_WIDTH * 0.45])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), EMERALD_600),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (1, 0), (1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    for idx, day in enumerate(days):
        if isinstance(day.get('date'), str):
            try:
                date_obj = datetime.fromisoformat(day['date'].replace('Z', '+00:00'))
            except Exception:
                date_obj = datetime.now()
        else:
            date_obj = day.get('date', datetime.now())

        date_str = day.get('dateFormatted', date_obj.strftime('%d/%m/%Y') if date_obj else '')

        total_work = day.get('totalWorkHours', 0)
        total_travel = day.get('totalTravelHours', 0)
        total_h = total_work + total_travel
        km = day.get('totalKm', 0)

        qr_img = None
        if QRCODE_AVAILABLE:
            try:
                locations = day.get('locations', [])
                if locations:
                    maps_url = build_google_maps_url_from_locations(locations)
                else:
                    events = day.get('events', [])
                    maps_url = build_google_maps_url_from_events(events)

                qr_buffer = generate_qr_code(maps_url)
                if qr_buffer:
                    qr_img = Image(qr_buffer, width=18 * mm, height=18 * mm)
            except Exception as e:
                print(f"Erro ao gerar QR Code: {e}")
                qr_img = None

        day_header_style = ParagraphStyle(
            'DayHeader',
            fontSize=12,
            fontName='Helvetica-Bold',
            leading=18
        )

        total_work_fmt = decimal_to_hhmm(total_work)
        total_travel_fmt = decimal_to_hhmm(total_travel)
        total_h_fmt = decimal_to_hhmm(total_h)

        day_info = f"<b>DIA {idx + 1}</b> - {date_str}<br/><font size=9 color='#475569'>⏱ {total_h_fmt} total ({total_work_fmt} manut. + {total_travel_fmt} desloc.)  •  📍 {km:.0f} km</font>"

        day_header_content = [[
            Paragraph(day_info, day_header_style),
            qr_img if qr_img else ""
        ]]

        day_header_table = Table(day_header_content, colWidths=[CONTENT_WIDTH - 25 * mm, 25 * mm])
        day_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SLATE_100),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (0, 0), 12),
            ('RIGHTPADDING', (1, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(day_header_table)
        elements.append(Spacer(1, 8))

        col_widths = [
            CONTENT_WIDTH * 0.10,
            CONTENT_WIDTH * 0.10,
            CONTENT_WIDTH * 0.50,
            CONTENT_WIDTH * 0.15,
            CONTENT_WIDTH * 0.15
        ]

        table_data = [[
            Paragraph('<b>Início</b>', ParagraphStyle('Header', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Fim</b>', ParagraphStyle('Header', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Atividade / Local</b>', ParagraphStyle('Header', fontSize=9, fontName='Helvetica-Bold')),
            Paragraph('<b>Status</b>', ParagraphStyle('Header', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Duração</b>', ParagraphStyle('Header', fontSize=9, fontName='Helvetica-Bold', alignment=TA_RIGHT))
        ]]

        events = day.get('events', [])
        for ev in events:
            event_type = ev.get('type', '')
            status_text = ev.get('status', '-') or '-'
            duration = ev.get('duration')
            duration_text = decimal_to_hhmm(duration) if duration else '-'
            desc = ev.get('desc', '')
            patrimonio = ev.get('patrimonio', '')

            icon = "■"
            if event_type == 'START':
                icon = "■"
            elif event_type == 'TRAVEL':
                icon = "■"
            elif event_type == 'WORK':
                icon = "■"
                if patrimonio:
                    desc = f"{patrimonio} - {desc}"
            elif event_type == 'LUNCH':
                icon = "■■"
            elif event_type == 'RETURN':
                icon = "■"
            elif event_type == 'END':
                icon = "■"

            desc_with_icon = f"{icon} {desc}"

            table_data.append([
                Paragraph(ev.get('startTime', ''), ParagraphStyle('Cell', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold')),
                Paragraph(ev.get('endTime', ''), ParagraphStyle('Cell', fontSize=9, alignment=TA_CENTER)),
                Paragraph(desc_with_icon, ParagraphStyle('Cell', fontSize=9)),
                Paragraph(status_text, ParagraphStyle('Cell', fontSize=9, alignment=TA_CENTER)),
                Paragraph(duration_text, ParagraphStyle('Cell', fontSize=9, alignment=TA_RIGHT))
            ])

        event_table = Table(table_data, colWidths=col_widths)

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), SLATE_50),
            ('TEXTCOLOR', (0, 0), (-1, 0), SLATE_800),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]

        for row_idx, ev in enumerate(events, start=1):
            event_type = ev.get('type', '')
            status = ev.get('status', '')

            if event_type in ['START', 'END']:
                table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), EMERALD_100))
            elif event_type == 'TRAVEL':
                table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), BLUE_50))
            elif event_type == 'LUNCH':
                table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), ORANGE_50))

            if status == 'VERMELHO':
                table_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), RED_600))
                table_style.append(('FONTNAME', (3, row_idx), (3, row_idx), 'Helvetica-Bold'))
            elif status == 'AMARELO':
                table_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), AMBER_600))
                table_style.append(('FONTNAME', (3, row_idx), (3, row_idx), 'Helvetica-Bold'))
            elif status == 'VERDE':
                table_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), EMERALD_600))

        event_table.setStyle(TableStyle(table_style))
        elements.append(event_table)
        elements.append(Spacer(1, 15))

    sum_work = sum(d.get('totalWorkHours', 0) for d in days)
    sum_travel = sum(d.get('totalTravelHours', 0) for d in days)
    sum_km = sum(d.get('totalKm', 0) for d in days)
    total_days = len(days)

    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1')))
    elements.append(Spacer(1, 12))

    summary_data = [[
        Paragraph("<b>RESUMO GERAL</b>", summary_title_style)
    ]]
    summary_table = Table(summary_data, colWidths=[CONTENT_WIDTH])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_50),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8))

    stat_style = ParagraphStyle('Stat', fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=18)

    sum_work_fmt = decimal_to_hhmm(sum_work)
    sum_travel_fmt = decimal_to_hhmm(sum_travel)
    sum_total_fmt = decimal_to_hhmm(sum_work + sum_travel)

    stats_data = [[
        Paragraph(f"<b>{total_days}</b><br/><font size=8 color='#64748b'>Dias</font>", stat_style),
        Paragraph(f"<b>{sum_work_fmt}</b><br/><font size=8 color='#64748b'>Manutenção</font>", stat_style),
        Paragraph(f"<b>{sum_travel_fmt}</b><br/><font size=8 color='#64748b'>Deslocamento</font>", stat_style),
        Paragraph(f"<b>{sum_total_fmt}</b><br/><font size=8 color='#64748b'>Total</font>", stat_style),
        Paragraph(f"<b>{sum_km:.0f} km</b><br/><font size=8 color='#64748b'>Distância</font>", stat_style)
    ]]

    stats_table = Table(stats_data, colWidths=[CONTENT_WIDTH / 5] * 5)
    stats_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEAFTER', (0, 0), (3, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(stats_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_pdf_protected(days: List[Dict], user_name: str = "Usuário",
                           password: str = "15963") -> io.BytesIO:
    pdf_buffer = generate_pdf(days, user_name)
    return protect_pdf_with_password(pdf_buffer, password)


def filter_events_by_activity(events: List[dict], atividade: str) -> List[dict]:
    filtered = []

    for event in events:
        if event.get('type') != 'WORK':
            continue

        desc = event.get('desc', '')
        patrimonio = extract_patrimonio_from_desc(desc)
        event_atividade = get_atividade_from_patrimonio(patrimonio)

        if event_atividade == atividade:
            filtered.append(event)

    return filtered


def generate_pdf_by_activity(days: List[Dict], atividade: str,
                              user_name: str = "Usuário") -> Optional[io.BytesIO]:
    filtered_days = []

    for day in days:
        events = day.get('events', [])
        filtered_events = filter_events_by_activity(events, atividade)

        if filtered_events:
            filtered_day = {
                'dateFormatted': day.get('dateFormatted', ''),
                'date': day.get('date', ''),
                'totalKm': 0,
                'totalWorkHours': sum(e.get('duration', 0) for e in filtered_events),
                'totalTravelHours': 0,
                'events': filtered_events,
                'locations': day.get('locations', [])
            }
            filtered_days.append(filtered_day)

    if not filtered_days:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    title_style = ParagraphStyle(
        'CustomTitle',
        fontSize=16,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        leading=20
    )

    header_info_style = ParagraphStyle(
        'HeaderInfo',
        fontSize=9,
        textColor=colors.white,
        fontName='Helvetica',
        alignment=TA_RIGHT
    )

    summary_title_style = ParagraphStyle(
        'SummaryTitle',
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        textColor=SLATE_800
    )

    elements = []

    generated_at = datetime.now().strftime('%d/%m/%Y às %H:%M')
    header_text = f"Gerado: {generated_at}  •  Por: {user_name}"

    header_data = [[
        Paragraph(f"PREVENTIVA - {atividade}", title_style),
        Paragraph(header_text, header_info_style)
    ]]

    header_table = Table(header_data, colWidths=[CONTENT_WIDTH * 0.55, CONTENT_WIDTH * 0.45])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), EMERALD_600),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (1, 0), (1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    for idx, day in enumerate(filtered_days):
        if isinstance(day.get('date'), str):
            try:
                date_obj = datetime.fromisoformat(day['date'].replace('Z', '+00:00'))
            except Exception:
                date_obj = datetime.now()
        else:
            date_obj = day.get('date', datetime.now())

        date_str = day.get('dateFormatted', date_obj.strftime('%d/%m/%Y') if date_obj else '')
        events = day.get('events', [])
        total_work = day.get('totalWorkHours', 0)

        qr_img = None
        if QRCODE_AVAILABLE:
            try:
                locations = day.get('locations', [])
                if locations:
                    maps_url = build_google_maps_url_from_locations(locations)
                else:
                    maps_url = build_google_maps_url_from_events(events)

                qr_buffer = generate_qr_code(maps_url)
                if qr_buffer:
                    qr_img = Image(qr_buffer, width=18 * mm, height=18 * mm)
            except Exception as e:
                print(f"Erro ao gerar QR Code: {e}")
                qr_img = None

        day_header_style = ParagraphStyle(
            'DayHeader',
            fontSize=12,
            fontName='Helvetica-Bold',
            leading=18
        )

        total_work_fmt = decimal_to_hhmm(total_work)

        day_info = f"<b>DIA {idx + 1}</b> - {date_str}<br/><font size=9 color='#475569'>⏱ {total_work_fmt} manutenção  •  🔧 {len(events)} equipamentos</font>"

        day_header_content = [[
            Paragraph(day_info, day_header_style),
            qr_img if qr_img else ""
        ]]

        day_header_table = Table(day_header_content, colWidths=[CONTENT_WIDTH - 25 * mm, 25 * mm])
        day_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SLATE_100),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (0, 0), 12),
            ('RIGHTPADDING', (1, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(day_header_table)
        elements.append(Spacer(1, 8))

        col_widths = [
            CONTENT_WIDTH * 0.08,
            CONTENT_WIDTH * 0.08,
            CONTENT_WIDTH * 0.32,
            CONTENT_WIDTH * 0.22,
            CONTENT_WIDTH * 0.12,
            CONTENT_WIDTH * 0.10,
            CONTENT_WIDTH * 0.08
        ]

        table_data = [[
            Paragraph('<b>Início</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Fim</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Atividade</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold')),
            Paragraph('<b>Fazenda</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold')),
            Paragraph('<b>Status</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph('<b>Duração</b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold', alignment=TA_RIGHT)),
            Paragraph('<b></b>', ParagraphStyle('Header', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER))
        ]]

        for ev in events:
            status_text = ev.get('status', '-') or '-'
            duration = ev.get('duration')
            duration_text = decimal_to_hhmm(duration) if duration else '-'
            desc = ev.get('desc', '')
            patrimonio = ev.get('patrimonio', '')
            farm_name = ev.get('farmName', '') or ev.get('fazenda', '') or ev.get('farm', '') or '-'

            if patrimonio:
                desc_with_patrimonio = f"■ {patrimonio} - {desc}"
            else:
                desc_with_patrimonio = f"■ {desc}"

            table_data.append([
                Paragraph(ev.get('startTime', ''), ParagraphStyle('Cell', fontSize=8, alignment=TA_CENTER, fontName='Helvetica-Bold')),
                Paragraph(ev.get('endTime', ''), ParagraphStyle('Cell', fontSize=8, alignment=TA_CENTER)),
                Paragraph(desc_with_patrimonio, ParagraphStyle('Cell', fontSize=8)),
                Paragraph(farm_name, ParagraphStyle('Cell', fontSize=7)),
                Paragraph(status_text, ParagraphStyle('Cell', fontSize=8, alignment=TA_CENTER)),
                Paragraph(duration_text, ParagraphStyle('Cell', fontSize=8, alignment=TA_RIGHT)),
                Paragraph('', ParagraphStyle('Cell', fontSize=8))
            ])

        event_table = Table(table_data, colWidths=col_widths)

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), SLATE_50),
            ('TEXTCOLOR', (0, 0), (-1, 0), SLATE_800),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]

        for row_idx, ev in enumerate(events, start=1):
            status = ev.get('status', '')

            if status == 'VERMELHO':
                table_style.append(('TEXTCOLOR', (4, row_idx), (4, row_idx), RED_600))
                table_style.append(('FONTNAME', (4, row_idx), (4, row_idx), 'Helvetica-Bold'))
            elif status == 'AMARELO':
                table_style.append(('TEXTCOLOR', (4, row_idx), (4, row_idx), AMBER_600))
                table_style.append(('FONTNAME', (4, row_idx), (4, row_idx), 'Helvetica-Bold'))
            elif status == 'VERDE':
                table_style.append(('TEXTCOLOR', (4, row_idx), (4, row_idx), EMERALD_600))

        event_table.setStyle(TableStyle(table_style))
        elements.append(event_table)
        elements.append(Spacer(1, 15))

    sum_work = sum(d.get('totalWorkHours', 0) for d in filtered_days)
    total_equipments = sum(len(d.get('events', [])) for d in filtered_days)
    total_days = len(filtered_days)

    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1')))
    elements.append(Spacer(1, 12))

    summary_data = [[
        Paragraph("<b>RESUMO GERAL</b>", summary_title_style)
    ]]
    summary_table = Table(summary_data, colWidths=[CONTENT_WIDTH])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_50),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8))

    stat_style = ParagraphStyle('Stat', fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=18)

    sum_work_fmt = decimal_to_hhmm(sum_work)

    stats_data = [[
        Paragraph(f"<b>{total_days}</b><br/><font size=8 color='#64748b'>Dias</font>", stat_style),
        Paragraph(f"<b>{total_equipments}</b><br/><font size=8 color='#64748b'>Equipamentos</font>", stat_style),
        Paragraph(f"<b>{sum_work_fmt}</b><br/><font size=8 color='#64748b'>Manutenção</font>", stat_style),
    ]]

    stats_table = Table(stats_data, colWidths=[CONTENT_WIDTH / 3] * 3)
    stats_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEAFTER', (0, 0), (1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(stats_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_all_activity_pdfs(days: List[Dict], user_name: str = "Usuário") -> Dict[str, io.BytesIO]:
    result = {}

    for atividade in ATIVIDADES_DISPONIVEIS:
        pdf_buffer = generate_pdf_by_activity(days, atividade, user_name)
        if pdf_buffer:
            result[atividade] = pdf_buffer

    return result