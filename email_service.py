"""
Serviço de envio de e-mail para o módulo de Atendimento Preventivo
Suporta anexos múltiplos e corpo HTML com envio direto para múltiplos destinatários
"""

import smtplib
import ssl
import re
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Tuple, Optional
from datetime import datetime


@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    username: str = ""
    password: str = ""


@dataclass
class EmailAttachment:
    filename: str
    content: bytes
    content_type: str = "application/pdf"


@dataclass
class EmailMessage:
    sender: str
    recipients: List[str]
    subject: str
    body_html: str = ""
    body_text: str = ""
    attachments: List[EmailAttachment] = field(default_factory=list)


def validar_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


class EmailService:

    def __init__(self, config: EmailConfig):
        self.config = config

    def create_mime_message(self, message: EmailMessage) -> MIMEMultipart:
        msg = MIMEMultipart('mixed')
        msg['From'] = message.sender
        msg['To'] = ', '.join(message.recipients)
        msg['Subject'] = message.subject

        body_part = MIMEMultipart('alternative')

        if message.body_text:
            text_part = MIMEText(message.body_text, 'plain', 'utf-8')
            body_part.attach(text_part)

        if message.body_html:
            html_part = MIMEText(message.body_html, 'html', 'utf-8')
            body_part.attach(html_part)

        msg.attach(body_part)

        for attachment in message.attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{attachment.filename}"'
            )
            msg.attach(part)

        return msg

    def send_email(self, message: EmailMessage) -> Tuple[bool, str]:
        try:
            recipients_validos = []
            recipients_invalidos = []
            
            for recipient in message.recipients:
                recipient_clean = recipient.strip()
                if not validar_email(recipient_clean):
                    recipients_invalidos.append(f"{recipient_clean} (formato inválido)")
                    continue
                recipients_validos.append(recipient_clean)
            
            if not recipients_validos:
                msg_erro = "Nenhum destinatário com formato válido encontrado."
                if recipients_invalidos:
                    msg_erro += f"\n\nE-mails rejeitados:\n- " + "\n- ".join(recipients_invalidos)
                return False, msg_erro
            
            message.recipients = recipients_validos
            mime_msg = self.create_mime_message(message)

            if self.config.use_tls:
                context = ssl.create_default_context()

                with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=60) as server:
                    server.set_debuglevel(0)
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()

                    if self.config.username and self.config.password:
                        server.login(self.config.username, self.config.password)

                    refused = server.sendmail(
                        message.sender,
                        recipients_validos,
                        mime_msg.as_string()
                    )
                    
                    if refused:
                        emails_rejeitados = [f"{email} (recusado pelo servidor)" for email in refused.keys()]
                        emails_enviados = [email for email in recipients_validos if email not in refused]
                    else:
                        emails_rejeitados = []
                        emails_enviados = recipients_validos
            else:
                with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=60) as server:
                    server.set_debuglevel(0)
                    
                    if self.config.username and self.config.password:
                        server.login(self.config.username, self.config.password)

                    refused = server.sendmail(
                        message.sender,
                        recipients_validos,
                        mime_msg.as_string()
                    )
                    
                    if refused:
                        emails_rejeitados = [f"{email} (recusado pelo servidor)" for email in refused.keys()]
                        emails_enviados = [email for email in recipients_validos if email not in refused]
                    else:
                        emails_rejeitados = []
                        emails_enviados = recipients_validos

            if emails_enviados:
                msg_sucesso = f"✅ E-mail enviado DIRETAMENTE para {len(emails_enviados)} destinatário(s):\n"
                msg_sucesso += "\n".join([f"  ✉️ {email}" for email in emails_enviados])
                
                if emails_rejeitados:
                    msg_sucesso += f"\n\n⚠️ AVISOS - Os seguintes e-mails foram rejeitados pelo servidor:\n"
                    msg_sucesso += "\n".join([f"  ❌ {email}" for email in emails_rejeitados])
                    msg_sucesso += "\n\nVerifique se os endereços de e-mail estão corretos."
                
                return True, msg_sucesso
            else:
                msg_erro = "❌ Nenhum e-mail foi enviado com sucesso.\n\nTodos os destinatários foram rejeitados."
                return False, msg_erro

        except smtplib.SMTPAuthenticationError:
            return False, "❌ Erro de autenticação SMTP. Verifique usuário e senha."
        except smtplib.SMTPConnectError:
            return False, "❌ Não foi possível conectar ao servidor SMTP."
        except smtplib.SMTPException as e:
            return False, f"❌ Erro SMTP: {str(e)}"
        except Exception as e:
            return False, f"❌ Erro inesperado: {str(e)}"


def extract_farm_name_from_event(event: dict) -> str:
    farm_name = event.get('farmName', '')
    if farm_name:
        if farm_name.startswith('FAZENDA '):
            return farm_name[8:]
        elif farm_name.startswith('OFICINA '):
            return farm_name[8:]
        elif farm_name.startswith('ESCRITORIO '):
            return farm_name[11:]
        return farm_name
    return '-'


def create_email_body_html(days: List[dict], user_name: str) -> str:
    total_km = sum(d.get('totalKm', 0) for d in days)
    total_equip = sum(
        len([e for e in d.get('events', []) if e.get('type') == 'WORK'])
        for d in days
    )
    total_hours = sum(
        d.get('totalWorkHours', 0) + d.get('totalTravelHours', 0)
        for d in days
    )

    dates_list = [d.get('dateFormatted', '') for d in days]
    dates_range = f"{dates_list[0]} a {dates_list[-1]}" if len(dates_list) > 1 else dates_list[0] if dates_list else ''

    hora_atual = datetime.now().hour
    if 6 <= hora_atual < 12:
        saudacao = "Bom dia a todos"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde a todos"
    else:
        saudacao = "Boa noite a todos"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #334155;
                max-width: 700px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }}
            .header {{
                background: #000000;
                color: white;
                padding: 30px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 700;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 14px;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 12px 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .day-section {{
                margin: 25px 0;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden;
            }}
            .day-header {{
                background: #334155;
                color: white;
                padding: 12px 16px;
                font-weight: 600;
            }}
            .day-content {{
                padding: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            th {{
                background: #f1f5f9;
                padding: 10px 8px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #e2e8f0;
            }}
            td {{
                padding: 10px 8px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .status-vermelho {{
                color: #dc2626;
                font-weight: 600;
            }}
            .status-amarelo {{
                color: #d97706;
                font-weight: 600;
            }}
            .status-verde {{
                color: #000000;
                font-weight: 600;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
                font-size: 12px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PROGRAMAÇÃO ATENDIMENTO DE PREVENTIVA</h1>
            <p>Período: {dates_range}</p>
        </div>
        <div class="content">
            <p>{saudacao}!</p>
            <p>Segue abaixo e em anexo a programação de atendimento de preventiva criado por: <strong>{user_name}</strong>.</p>
    """

    for idx, day in enumerate(days):
        date_formatted = day.get('dateFormatted', f'Dia {idx + 1}')
        events = day.get('events', [])
        work_events = [e for e in events if e.get('type') == 'WORK']

        html += f"""
            <div class="day-section">
                <div class="day-header">
                    📅 DIA {idx + 1} - {date_formatted} ({len(work_events)} equipamentos)
                </div>
                <div class="day-content">
                    <table>
                        <tr>
                            <th>Horário</th>
                            <th>Equipamento</th>
                            <th>Local / Regional</th>
                            <th>Status</th>
                            <th>Duração</th>
                        </tr>
        """

        for event in work_events[:10]:
            start = event.get('startTime', '--:--')
            end = event.get('endTime', '--:--')
            desc = event.get('desc', '')[:50]
            patrimonio = event.get('patrimonio', '')
            status = event.get('status', '')
            status_class = f"status-{status.lower()}" if status else ""
            farm_name = event.get('farmName', '-')
            regional = event.get('regional', '-')
            duration = event.get('duration', 0)
            duration_text = f"{duration:.1f}h" if duration else '-'

            equipamento_completo = f"{patrimonio} - {desc}" if patrimonio else desc
            local_completo = f"{farm_name} / {regional}" if regional else farm_name

            html += f"""
                        <tr>
                            <td>{start} - {end}</td>
                            <td>{equipamento_completo}</td>
                            <td>{local_completo}</td>
                            <td><span class="{status_class}">{status}</span></td>
                            <td>{duration_text}</td>
                        </tr>
            """

        if len(work_events) > 10:
            html += f"""
                        <tr>
                            <td colspan="5" style="text-align: center; font-style: italic; color: #64748b;">
                                ... e mais {len(work_events) - 10} equipamentos (ver PDF anexo)
                            </td>
                        </tr>
            """

        html += """
                    </table>
                </div>
            </div>
        """

    html += """
            <div class="footer">
                <p>Este e-mail foi gerado automaticamente pelo Sistema de Gestão de Manutenção.</p>
                <p>PCM Oficina Pompéu - MG</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def create_email_body_text(days: List[dict], user_name: str) -> str:
    total_km = sum(d.get('totalKm', 0) for d in days)
    total_equip = sum(
        len([e for e in d.get('events', []) if e.get('type') == 'WORK'])
        for d in days
    )

    dates_list = [d.get('dateFormatted', '') for d in days]
    dates_range = f"{dates_list[0]} a {dates_list[-1]}" if len(dates_list) > 1 else dates_list[0] if dates_list else ''

    hora_atual = datetime.now().hour
    if 6 <= hora_atual < 12:
        saudacao = "Bom dia a todos"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde a todos"
    else:
        saudacao = "Boa noite a todos"

    text = f"""
PROGRAMAÇÃO DE ATENDIMENTO PREVENTIVO
=====================================

Período: {dates_range}
Gerado por: {user_name}
Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

{saudacao}!

RESUMO:
- Dias: {len(days)}
- Equipamentos: {total_equip}
- Distância: {total_km:.0f} km

"""

    for idx, day in enumerate(days):
        date_formatted = day.get('dateFormatted', f'Dia {idx + 1}')
        events = day.get('events', [])
        work_events = [e for e in events if e.get('type') == 'WORK']

        text += f"""
DIA {idx + 1} - {date_formatted}
---------------------------------
"""

        for event in work_events:
            start = event.get('startTime', '--:--')
            end = event.get('endTime', '--:--')
            desc = event.get('desc', '')
            patrimonio = event.get('patrimonio', '')
            status = event.get('status', '')
            farm_name = event.get('farmName', '-')
            regional = event.get('regional', '-')
            duration = event.get('duration', 0)
            duration_text = f"{duration:.1f}h" if duration else '-'

            equipamento_completo = f"{patrimonio} - {desc}" if patrimonio else desc
            local_completo = f"{farm_name} / {regional}" if regional else farm_name

            text += f"  {start}-{end} | {equipamento_completo[:25]}... | {local_completo[:20]}... | {status} | {duration_text}\n"

    text += """

---
PCM Oficina Pompéu - MG
"""

    return text