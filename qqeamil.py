from email.mime.text import MIMEText
from email.header import Header
import smtplib

def send_mail(receiver, subject, content):

    # 邮件配置
    smtp_server = "smtp.qq.com"  # SMTP服务器地址（如：smtp.qq.com）
    port = 587  # 端口（QQ邮箱587，163邮箱465/994）
    sender = "3506322440@qq.com"
    password = "acyrgwjltldpdbjg"  # 邮箱密码/授权码
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = sender
    msg["To"] = receiver
    server =None
    try:
        # 连接SMTP服务器
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # 启用TLS加密（部分邮箱需要）
        server.login(sender, password)

        # 发送邮件
        server.sendmail(sender, [receiver], msg.as_string())
        return True
    except Exception as e:
        return False
    finally:
        server.quit()  # 关闭连接

