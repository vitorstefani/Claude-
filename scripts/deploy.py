#!/usr/bin/env python3
"""Deploy de páginas de clientes na HostGator via FTP (modo passivo).

Uso:
    python3 scripts/deploy.py <pasta_local> <slug> [--sem-subdominio]

Exemplo:
    python3 scripts/deploy.py clientes/proposta-cliente proposta-cliente
    -> envia para ~/proposta-cliente.vetordigital.tech/
    -> link: https://proposta-cliente.vetordigital.tech/

Credenciais vêm do arquivo .env na raiz do projeto (fora do git) ou de
variáveis de ambiente: FTP_HOST, FTP_USER, FTP_PASS, FTP_PORT, BASE_DOMAIN,
CPANEL_PORT. Só usa a biblioteca padrão do Python.
"""
import argparse
import base64
import ftplib
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
IGNORAR = {".DS_Store", "Thumbs.db", ".git", "__pycache__"}


def carregar_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for linha in env_file.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    faltando = [k for k in ("FTP_HOST", "FTP_USER", "FTP_PASS") if not os.environ.get(k)]
    if faltando:
        sys.exit(f"Faltam credenciais: {', '.join(faltando)} (configure o .env)")
    return {
        "host": os.environ["FTP_HOST"],
        "user": os.environ["FTP_USER"],
        "password": os.environ["FTP_PASS"],
        "port": int(os.environ.get("FTP_PORT", "21")),
        "base_domain": os.environ.get("BASE_DOMAIN", "vetordigital.tech"),
        "cpanel_port": int(os.environ.get("CPANEL_PORT", "2083")),
    }


def criar_subdominio(cfg, slug):
    """Cria o subdomínio no cPanel (UAPI) apontando para ~/<slug>.<dominio>.
    Se já existir, segue em frente."""
    dir_doc = f"{slug}.{cfg['base_domain']}"
    qs = urllib.parse.urlencode({
        "domain": slug,
        "rootdomain": cfg["base_domain"],
        "dir": dir_doc,
    })
    url = f"https://{cfg['host']}:{cfg['cpanel_port']}/execute/SubDomain/addsubdomain?{qs}"
    token = base64.b64encode(f"{cfg['user']}:{cfg['password']}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            data = json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        print(f"  ! Não consegui criar o subdomínio via cPanel ({e}). "
              f"Se ele ainda não existir, crie em cPanel > Domínios.")
        return
    if data.get("status") == 1:
        print(f"  ✓ Subdomínio {slug}.{cfg['base_domain']} criado")
    else:
        erros = " ".join(data.get("errors") or [])
        if "exist" in erros.lower() or "já" in erros.lower():
            print(f"  · Subdomínio {slug}.{cfg['base_domain']} já existe")
        else:
            print(f"  ! cPanel respondeu: {erros or data}")


def conectar(cfg):
    """Tenta FTPS explícito (mais seguro); se o servidor recusar, usa FTP simples.
    Sempre em modo passivo."""
    try:
        ftp = ftplib.FTP_TLS(timeout=60)
        ftp.connect(cfg["host"], cfg["port"])
        ftp.login(cfg["user"], cfg["password"])
        ftp.prot_p()
        ftp.set_pasv(True)
        print("  ✓ Conectado (FTPS, passivo)")
        return ftp
    except (ftplib.error_perm, ssl.SSLError, OSError) as e:
        if isinstance(e, ftplib.error_perm) and str(e).startswith("530"):
            sys.exit(f"Login recusado: {e}")
        print(f"  · FTPS indisponível ({e}); usando FTP simples")
    ftp = ftplib.FTP(timeout=60)
    ftp.connect(cfg["host"], cfg["port"])
    ftp.login(cfg["user"], cfg["password"])
    ftp.set_pasv(True)
    print("  ✓ Conectado (FTP, passivo)")
    return ftp


def garantir_dir(ftp, caminho):
    """Cria o diretório remoto (e pais) se não existir. Caminho relativo à raiz do FTP."""
    atual = ftp.pwd()
    for parte in [p for p in caminho.split("/") if p]:
        try:
            ftp.cwd(parte)
        except ftplib.error_perm:
            ftp.mkd(parte)
            ftp.cwd(parte)
    ftp.cwd(atual)


def enviar(ftp, pasta_local: Path, destino: str):
    arquivos = 0
    for raiz, dirs, nomes in os.walk(pasta_local):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        rel = Path(raiz).relative_to(pasta_local).as_posix()
        remoto = destino if rel == "." else f"{destino}/{rel}"
        garantir_dir(ftp, remoto)
        for nome in nomes:
            if nome in IGNORAR:
                continue
            with open(Path(raiz) / nome, "rb") as f:
                ftp.storbinary(f"STOR {remoto}/{nome}", f)
            arquivos += 1
            print(f"    ↑ {remoto}/{nome}")
    return arquivos


def main():
    ap = argparse.ArgumentParser(description="Sobe uma pasta de cliente para a HostGator.")
    ap.add_argument("pasta", help="pasta local com o site (deve conter index.html)")
    ap.add_argument("slug", help="slug do cliente, ex.: proposta-cliente")
    ap.add_argument("--sem-subdominio", action="store_true",
                    help="não tenta criar o subdomínio no cPanel")
    args = ap.parse_args()

    slug = args.slug.strip().lower()
    if not SLUG_RE.match(slug):
        sys.exit("Slug inválido: use só letras minúsculas, números e hífen (ex.: proposta-cliente)")
    pasta = Path(args.pasta).resolve()
    if not pasta.is_dir():
        sys.exit(f"Pasta não encontrada: {pasta}")
    if not (pasta / "index.html").exists():
        print("  ! Aviso: a pasta não tem index.html")

    cfg = carregar_env()
    destino = f"{slug}.{cfg['base_domain']}"  # ao lado da public_html
    print(f"→ Deploy de {pasta} para ~/{destino}/")

    if not args.sem_subdominio:
        criar_subdominio(cfg, slug)

    ftp = conectar(cfg)
    try:
        n = enviar(ftp, pasta, destino)
    finally:
        try:
            ftp.quit()
        except Exception:  # noqa: BLE001
            ftp.close()

    print(f"✓ {n} arquivo(s) enviados")
    print(f"🔗 https://{destino}/")


if __name__ == "__main__":
    main()
