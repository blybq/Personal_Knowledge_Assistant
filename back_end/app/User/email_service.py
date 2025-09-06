import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        
    def send_verification_code(self, recipient_email: str, verification_code: str) -> bool:
        """
        发送验证码邮件
        
        Args:
            recipient_email: 收件人邮箱
            verification_code: 验证码
            
        Returns:
            bool: 发送是否成功
        """
        if not all([self.sender_email, self.sender_password]):
            print("邮件配置不完整，请设置SENDER_EMAIL和SENDER_PASSWORD环境变量")
            return False
            
        # 创建邮件内容
        subject = "个人知识助手 - 密码重置验证码"
        
        # HTML邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code {{
                    background: #ffffff;
                    border: 2px dashed #667eea;
                    padding: 15px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #6c757d;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>个人知识助手</h1>
            </div>
            <div class="content">
                <h2>密码重置验证码</h2>
                <p>您好！</p>
                <p>您正在尝试重置个人知识助手的密码，请使用以下验证码完成验证：</p>
                
                <div class="code">
                    {verification_code}
                </div>
                
                <div class="warning">
                    <strong>请注意：</strong>
                    <ul>
                        <li>此验证码有效期为10分钟</li>
                        <li>请勿将此验证码分享给他人</li>
                        <li>如果您没有请求重置密码，请忽略此邮件</li>
                    </ul>
                </div>
                
                <p>如果您有任何问题，请联系我们的支持团队。</p>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本内容
        text_content = f"""
        个人知识助手 - 密码重置验证码
        
        您好！
        
        您正在尝试重置个人知识助手的密码，请使用以下验证码完成验证：
        
        验证码：{verification_code}
        
        请注意：
        - 此验证码有效期为10分钟
        - 请勿将此验证码分享给他人
        - 如果您没有请求重置密码，请忽略此邮件
        
        如果您有任何问题，请联系我们的支持团队。
        
        此邮件由系统自动发送，请勿直接回复
        """
        
        try:
            # 创建邮件消息
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # 添加文本和HTML版本
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            
            message.attach(part1)
            message.attach(part2)
            
            # 创建安全连接并发送邮件
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                # server.set_debuglevel(1)  # 观察底层通信
                # server.ehlo()
                # server.starttls(context=context)
                # server.ehlo()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email, recipient_email, message.as_string()
                )

                server.close()
            
            print(f"验证码邮件已成功发送到 {recipient_email}")
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False

# 全局邮件服务实例
email_service = EmailService()
