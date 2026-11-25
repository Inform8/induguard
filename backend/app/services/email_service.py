import os
import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

logger = logging.getLogger("induguard.email")


from dotenv import load_dotenv
load_dotenv()

class EmailService:
    """
    Asynchronous Industrial Email Notification Service.
    Dispatches automated email alerts when WARNING or CRITICAL machine conditions occur.
    """

    def __init__(self):
        self.last_sent: Optional[Dict[str, Any]] = None
        self._recipient_override: Optional[str] = None

    @property
    def smtp_server(self) -> str: return os.getenv("SMTP_SERVER", "smtp.gmail.com")
    
    @property
    def smtp_port(self) -> int: return int(os.getenv("SMTP_PORT", "587"))
    
    @property
    def sender_email(self) -> str: return os.getenv("SMTP_USER", "alerts@induguard-iot.com")
    
    @property
    def sender_password(self) -> str: return os.getenv("SMTP_PASSWORD", "")
    
    @property
    def recipient_email(self) -> str: return self._recipient_override or os.getenv("ALERT_EMAIL_RECIPIENT", "operator@induguard.com")
    
    @property
    def github_token(self) -> str: return os.getenv("GITHUB_TOKEN", "")
    
    @property
    def enabled(self) -> bool: return os.getenv("ENABLE_EMAIL_ALERTS", "true").lower() in ["true", "1", "yes"]

    def update_recipient(self, email: str):
        """Update the active recipient email."""
        if email and "@" in email:
            self._recipient_override = email.strip()

    def get_config(self) -> Dict[str, Any]:
        """Return current email configuration (without exposing secrets)."""
        return {
            "recipient_email": self.recipient_email,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "sender_email": self.sender_email,
            "has_password": bool(self.sender_password),
            "enabled": self.enabled,
            "last_sent": self.last_sent,
            "github_token_configured": bool(self.github_token)
        }

    def _build_html_email(self, alert_data: Dict[str, Any]) -> str:
        """Build a clean, high-priority HTML email template."""
        machine_id = alert_data.get("machine_id", "UNKNOWN")
        severity = alert_data.get("severity", "WARNING").upper()
        fault_type = alert_data.get("type", alert_data.get("predicted_fault", "Industrial Anomaly"))
        timestamp = alert_data.get("timestamp", "Just now")
        message = alert_data.get("message", "Anomalous sensor readings detected.")
        reasons = alert_data.get("reasons", ["Sensor parameters deviated from safe operational baseline."])
        action = alert_data.get("recommended_action", "Inspect machinery immediately.")

        sensor_readings = alert_data.get("sensor_readings", {})
        temp = sensor_readings.get("temperature", "N/A")
        vib = sensor_readings.get("vibration", "N/A")
        hum = sensor_readings.get("humidity", "N/A")
        pres = sensor_readings.get("pressure", "N/A")

        if isinstance(temp, float): temp = round(temp, 1)
        if isinstance(vib, float): vib = round(vib, 1)
        if isinstance(hum, float): hum = round(hum, 1)
        if isinstance(pres, float): pres = round(pres, 1)

        is_critical = severity == "CRITICAL"
        header_bg = "#450a0a" if is_critical else "#422006"
        header_text = "🚨 CRITICAL ALERT" if is_critical else "⚠️ WARNING"
        machine_badge_bg = "#ef4444" if is_critical else "#f59e0b"
        
        bg_color = "#1e293b"
        text_color = "#f8fafc"
        border_color = "#334155"
        table_row_even = "#0f172a"
        table_row_odd = "#1e293b"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{header_text}</title>
            <style>
                .tr-even {{ background-color: {table_row_even}; }}
                .tr-odd {{ background-color: {table_row_odd}; }}
            </style>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px;">
            <div style="max-width: 600px; margin: 0 auto; background: {bg_color}; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <!-- Header Banner -->
                <div style="background-color: {header_bg}; color: #ffffff; padding: 20px 24px; text-align: center; border-bottom: 2px solid {machine_badge_bg};">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 1px;">{header_text}</h1>
                </div>

                <!-- Body Details -->
                <div style="padding: 24px; color: {text_color};">
                    <div style="display: inline-block; background-color: {machine_badge_bg}; color: #ffffff; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: bold; margin-bottom: 16px;">
                        Machine {machine_id}
                    </div>
                    
                    <h2 style="margin: 0 0 20px 0; font-size: 20px;">{fault_type} Detected</h2>

                    <!-- Sensor Table -->
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px; border: 1px solid {border_color}; border-radius: 4px; overflow: hidden;">
                        <tr class="tr-even">
                            <td style="padding: 12px 16px; color: #94a3b8; font-size: 14px; border-bottom: 1px solid {border_color};">Temperature</td>
                            <td style="padding: 12px 16px; text-align: right; font-weight: 600; border-bottom: 1px solid {border_color};">{temp} °C</td>
                        </tr>
                        <tr class="tr-odd">
                            <td style="padding: 12px 16px; color: #94a3b8; font-size: 14px; border-bottom: 1px solid {border_color};">Vibration</td>
                            <td style="padding: 12px 16px; text-align: right; font-weight: 600; border-bottom: 1px solid {border_color};">{vib} mm/s</td>
                        </tr>
                        <tr class="tr-even">
                            <td style="padding: 12px 16px; color: #94a3b8; font-size: 14px; border-bottom: 1px solid {border_color};">Humidity</td>
                            <td style="padding: 12px 16px; text-align: right; font-weight: 600; border-bottom: 1px solid {border_color};">{hum} %</td>
                        </tr>
                        <tr class="tr-odd">
                            <td style="padding: 12px 16px; color: #94a3b8; font-size: 14px;">Pressure</td>
                            <td style="padding: 12px 16px; text-align: right; font-weight: 600;">{pres} bar</td>
                        </tr>
                    </table>

                    <!-- Recommended Action -->
                    <div style="border-left: 4px solid #eab308; background: #422006; padding: 16px; margin-bottom: 24px; border-radius: 4px;">
                        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #eab308; margin-bottom: 8px;">RECOMMENDED ACTION</div>
                        <div style="font-size: 14px; color: #f8fafc;">{action}</div>
                    </div>

                    <div style="text-align: center; color: #ef4444; font-weight: 600; font-size: 16px; margin-top: 32px; margin-bottom: 16px;">
                        Action Required Immediately
                    </div>
                </div>

                <!-- Footer -->
                <div style="border-top: 1px solid {border_color}; padding: 16px; text-align: center; color: #94a3b8; font-size: 12px; line-height: 1.6;">
                    © 2026 InduGuard System. All rights reserved.<br>
                    Automated telemetry alert generated by InduGuard.
                </div>
            </div>
        </body>
        </html>
        """

    def _send_email_thread(self, alert_data: Dict[str, Any]):
        """Background thread execution for sending the email."""
        try:
            if not self.enabled:
                logger.info("Email alerts disabled via configuration.")
                return

            recipient = self.recipient_email
            if not recipient:
                return

            subject = f"[{alert_data.get('severity', 'ALERT').upper()}] Machine {alert_data.get('machine_id')} - {alert_data.get('type', 'Fault')}"
            html_body = self._build_html_email(alert_data)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient
            msg.attach(MIMEText(html_body, "html"))

            # If sender password is provided, attempt actual SMTP transport
            if self.sender_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, [recipient], msg.as_string())
                logger.info(f"Successfully dispatched alert email to {recipient}")
            else:
                # Mock / Simulation transport log (cleanly records dispatch)
                logger.info(f"[EMAIL SIMULATION] Alert email prepared for {recipient} | Subject: {subject}")

            self.last_sent = {
                "recipient": recipient,
                "subject": subject,
                "timestamp": alert_data.get("timestamp"),
                "status": "SENT" if self.sender_password else "SIMULATED_DISPATCH"
            }
        except Exception as e:
            logger.error(f"Failed to dispatch alert email: {e}")
            self.last_sent = {
                "recipient": self.recipient_email,
                "status": "FAILED",
                "error": str(e)
            }

    def dispatch_alert_email(self, alert_data: Dict[str, Any]):
        """Asynchronously dispatch email alert in background thread without blocking streaming."""
        t = threading.Thread(target=self._send_email_thread, args=(alert_data,), daemon=True)
        t.start()


# Singleton instance
email_service = EmailService()
