def build_password_reset_email_html(reset_url: str) -> str:
    """Monta o HTML do email de redefinição de senha, no tema visual
    laranja/preto do BetAnalyzer (consistente com o frontend)."""
    return f"""\
<!DOCTYPE html>
<html lang="pt-BR">
  <body style="margin:0;padding:0;background-color:#080B14;font-family:Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#080B14;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#0F1624;border:1px solid #1E2D4A;border-radius:16px;overflow:hidden;">
            <tr>
              <td style="background:linear-gradient(135deg,#FF6B00,#F0B429);padding:28px 32px;">
                <span style="font-size:20px;font-weight:800;color:#080B14;">Bet<span style="color:#0F1624;">Analyzer</span></span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;color:#F0F4FF;">
                <h1 style="margin:0 0 16px;font-size:20px;color:#F0F4FF;">Redefinição de senha</h1>
                <p style="margin:0 0 24px;font-size:14px;line-height:1.6;color:#8896B3;">
                  Recebemos uma solicitação para redefinir a senha da sua conta BetAnalyzer.
                  Clique no botão abaixo para escolher uma nova senha. Este link expira em 1 hora.
                </p>
                <table role="presentation" cellpadding="0" cellspacing="0">
                  <tr>
                    <td align="center" style="border-radius:10px;background:linear-gradient(135deg,#FF6B00,#F0B429);">
                      <a href="{reset_url}" style="display:inline-block;padding:14px 28px;font-size:14px;font-weight:700;color:#080B14;text-decoration:none;">
                        Redefinir senha
                      </a>
                    </td>
                  </tr>
                </table>
                <p style="margin:24px 0 0;font-size:12px;line-height:1.6;color:#8896B3;">
                  Se você não solicitou isso, pode ignorar este email com segurança — sua senha
                  atual continua válida. Se o botão não funcionar, copie e cole este link no navegador:
                  <br />
                  <a href="{reset_url}" style="color:#FF6B00;word-break:break-all;">{reset_url}</a>
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:20px 32px;border-top:1px solid #1E2D4A;">
                <p style="margin:0;font-size:11px;color:#8896B3;">
                  Apostas envolvem risco. Jogue com responsabilidade. +18
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
