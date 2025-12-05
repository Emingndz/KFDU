import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_password_reset_email(to_email: str, code: str) -> bool:
    """
    Send password reset code via email.
    Returns True if successful, False otherwise.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[EMAIL] SMTP not configured. Code for {to_email}: {code}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'KFDU - Şifre Sıfırlama Kodu'
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.SMTP_USER}>"
        msg['To'] = to_email
        
        # Plain text version
        text = f"""
Merhaba,

Şifre sıfırlama talebiniz alındı.

Şifre sıfırlama kodunuz: {code}

Bu kodu şifre sıfırlama sayfasına girerek yeni şifrenizi belirleyebilirsiniz.

Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.

KFDU Platform
        """
        
        # HTML version
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .code {{ background: #667eea; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; letter-spacing: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬📚 KFDU Platform</h1>
        </div>
        <div class="content">
            <h2>Şifre Sıfırlama</h2>
            <p>Merhaba,</p>
            <p>Şifre sıfırlama talebiniz alındı. Aşağıdaki kodu kullanarak yeni şifrenizi belirleyebilirsiniz:</p>
            <div class="code">{code}</div>
            <p>Bu kod 10 dakika boyunca geçerlidir.</p>
            <p>Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
        </div>
        <div class="footer">
            <p>KFDU - Kitap ve Film Değerlendirme Uygulaması</p>
        </div>
    </div>
</body>
</html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        
        print(f"[EMAIL] Password reset code sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")
        return False
