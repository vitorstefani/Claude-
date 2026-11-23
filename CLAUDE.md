# Vetor Digital — páginas de clientes

## Regra permanente: deploy automático
Sempre que o Vitor enviar uma pasta/página de cliente:
1. Coloque-a em `clientes/<slug>/` (slug: minúsculas, números e hífen, ex.: `proposta-cliente`; precisa ter `index.html`).
2. Suba:
   - **Se a rede permitir FTP** (máquina local): `python3 scripts/deploy.py clientes/<slug> <slug>`
   - **Sessão na nuvem** (FTP bloqueado): faça commit e push da pasta — o workflow
     `.github/workflows/deploy-clientes.yml` publica via FTP. Confira o resultado da execução.
3. Devolva o link: `https://<slug>.vetordigital.tech/`

## Hospedagem
- HostGator, cPanel. Site principal em `~/public_html`.
- Cada cliente em `~/<slug>.vetordigital.tech/` (ao lado da `public_html`).
- Home do cPanel: `/home2/vito1304/`.
- Deploy usa a conta FTP dedicada `deploy@vetordigital.tech` (raiz = home), FTPS passivo.
- Conta só de FTP não cria subdomínio: cada `<slug>.vetordigital.tech` precisa ser criado em
  cPanel > Domínios (raiz `/home2/vito1304/<slug>.vetordigital.tech`). Avise o Vitor ao subir
  um cliente novo. O workflow testa o link público e registra o HTTP no log.

## Credenciais
- Local: `.env` (no `.gitignore`; modelo em `.env.example`). Nunca commitar.
- GitHub Actions: secrets `FTP_HOST`, `FTP_USER` (`deploy@vetordigital.tech`), `FTP_PASS`.
