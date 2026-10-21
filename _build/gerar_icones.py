"""Gera os icones do PWA (sem dependencias externas).

Uso: python _build/gerar_icones.py
Saida: icon-192.png, icon-512.png, apple-touch-icon.png na raiz do projeto.
"""
import os
import struct
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paleta do app (nao alterar: sao as cores oficiais)
ROXO_CLARO = (139, 92, 246)   # --accent #8b5cf6
ROXO_ESCURO = (109, 40, 217)  # tom mais fechado para o degrade
BRANCO = (250, 250, 250)
FUNDO_PORTA = (24, 24, 27)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _dentro_rounded(x, y, r, margem):
    """Quadrado de cantos arredondados em coordenadas 0..1."""
    if x < margem or x > 1 - margem or y < margem or y > 1 - margem:
        return False
    cx = min(max(x, margem + r), 1 - margem - r)
    cy = min(max(y, margem + r), 1 - margem - r)
    dx, dy = x - cx, y - cy
    return dx * dx + dy * dy <= r * r


def cor_do_pixel(x, y):
    """Retorna (r,g,b,a) para coordenadas normalizadas 0..1."""
    if not _dentro_rounded(x, y, 0.22, 0.03):
        return (0, 0, 0, 0)

    # Degrade diagonal do roxo
    t = min(1.0, max(0.0, (x + y) / 2))
    cor = _mix(ROXO_CLARO, ROXO_ESCURO, t)

    # Telhado: triangulo de (0.5,0.20) a (0.14,0.50) a (0.86,0.50)
    if 0.20 <= y <= 0.50:
        meia = (y - 0.20) / 0.30 * 0.36
        if abs(x - 0.5) <= meia:
            cor = BRANCO

    # Corpo da casa: retangulo 0.24..0.76 x 0.50..0.80
    if 0.24 <= x <= 0.76 and 0.50 <= y <= 0.80:
        cor = BRANCO

    # Porta
    if 0.43 <= x <= 0.57 and 0.60 <= y <= 0.80:
        cor = FUNDO_PORTA

    # Janela
    if 0.31 <= x <= 0.40 and 0.56 <= y <= 0.65:
        cor = FUNDO_PORTA
    if 0.60 <= x <= 0.69 and 0.56 <= y <= 0.65:
        cor = FUNDO_PORTA

    return (cor[0], cor[1], cor[2], 255)


def escrever_png(caminho, largura, altura, linhas):
    cru = b"".join(b"\x00" + b"".join(bytes(p) for p in linha) for linha in linhas)

    def bloco(tipo, dados):
        return (
            struct.pack(">I", len(dados))
            + tipo
            + dados
            + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", largura, altura, 8, 6, 0, 0, 0)
    with open(caminho, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(bloco(b"IHDR", ihdr))
        f.write(bloco(b"IDAT", zlib.compress(cru, 9)))
        f.write(bloco(b"IEND", b""))


def gerar(tamanho, amostras=4, destino=None):
    """Renderiza com supersampling e reduz, para as bordas ficarem suaves."""
    forca = tamanho * amostras
    # Renderiza em forca x forca e depois tira a media de cada bloco amostras x amostras
    buffer = [[(0, 0, 0, 0)] * forca for _ in range(forca)]
    for py in range(forca):
        y = (py + 0.5) / forca
        linha = buffer[py]
        for px in range(forca):
            linha[px] = cor_do_pixel((px + 0.5) / forca, y)

    linhas = []
    for oy in range(tamanho):
        linha = []
        for ox in range(tamanho):
            r = g = b = a = 0
            for dy in range(amostras):
                sr = buffer[oy * amostras + dy]
                for dx in range(amostras):
                    p = sr[ox * amostras + dx]
                    # pre-multiplica para o alpha nao escurecer a borda
                    r += p[0] * p[3]
                    g += p[1] * p[3]
                    b += p[2] * p[3]
                    a += p[3]
            if a:
                linha.append((r // a, g // a, b // a, a // (amostras * amostras)))
            else:
                linha.append((0, 0, 0, 0))
        linhas.append(linha)

    escrever_png(destino, tamanho, tamanho, linhas)
    return destino


if __name__ == "__main__":
    alvos = [
        (192, "icon-192.png"),
        (512, "icon-512.png"),
        (180, "apple-touch-icon.png"),
    ]
    for tam, nome in alvos:
        caminho = os.path.join(RAIZ, nome)
        gerar(tam, 4, caminho)
        print("gerado:", nome, tam, "x", tam, os.path.getsize(caminho), "bytes")
