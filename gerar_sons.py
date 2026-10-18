import numpy as np, wave, os
SR = 44100
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
rng = np.random.default_rng(11)

def t(d): return np.arange(int(SR*d))/SR

def salvar(nome, x, pico=0.5, duracao=None, fade=0.004):
    if duracao: x = x[:int(duracao*SR)]
    x = x/(np.max(np.abs(x))+1e-9)*pico
    n = int(fade*SR); x[-n:] *= np.linspace(1, 0, n)
    with wave.open(os.path.join(PASTA, nome+".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x*32767).astype("<i2").tobytes())

def reverb(x, cauda=2.2, mistura=0.5, tau=0.7):
    n = int(cauda*SR)
    ir = rng.standard_normal(n)*np.exp(-np.arange(n)/SR/tau)
    ir = np.convolve(ir, np.ones(10)/10, "same"); ir /= np.sqrt(np.sum(ir**2))
    tam = len(x)+n
    molhado = np.fft.irfft(np.fft.rfft(x, tam)*np.fft.rfft(ir, tam), tam)
    seco = np.pad(x, (0, n))
    molhado *= np.max(np.abs(seco))/(np.max(np.abs(molhado))+1e-9)
    return seco*(1-mistura)+molhado*mistura

def nota_piano(f, d=1.6, suave=True):
    tt = t(d); x = np.zeros_like(tt)
    for n in range(1, 8):
        x += (1/n**1.3)*np.sin(2*np.pi*f*n*np.sqrt(1+0.0003*n*n)*tt)*np.exp(-tt*(1.6+1.4*n))
    ataque = np.minimum(1, tt/(0.012 if suave else 0.004))
    return x*ataque

def pad(f, d=2.0, ataque=0.35):
    tt = t(d); x = np.zeros_like(tt)
    for desv in (-0.006, -0.002, 0.002, 0.006):
        for n in range(1, 6):
            x += (1/n**1.5)*np.sin(2*np.pi*f*(1+desv)*n*tt+n*1.7)
    env = np.minimum(1, tt/ataque)*np.exp(-np.maximum(0, tt-ataque)*1.8)
    return x*env

def somar(*camadas):
    n = max(len(c) for c in camadas); s = np.zeros(n)
    for c in camadas: s[:len(c)] += c
    return s

def deslocar(x, seg):
    return np.pad(x, (int(seg*SR), 0))

# Re maior com nona: D3 A3 D4 F#4 A4 E5
salvar("abrir", reverb(somar(nota_piano(440.0, 1.4), 0.5*nota_piano(880.0, 1.4), 0.35*pad(220.0, 1.4, 0.2))), 0.5, 1.5, 0.12)
salvar("carregou", reverb(somar(pad(146.83, 2.2, 0.4), 0.8*pad(220.0, 2.2, 0.45), 0.6*pad(329.63, 2.2, 0.5)), 2.5, 0.6, 0.9), 0.42, 1.9, 0.25)
salvar("enter", reverb(somar(nota_piano(440.0, 1.2), deslocar(0.8*nota_piano(659.25, 1.0), 0.07), deslocar(0.5*nota_piano(880.0, 0.9), 0.14)), 1.8, 0.45, 0.5), 0.5, 1.1, 0.1)

# ---- bateria de digitacao (mantida) ----
def bumbo(d=0.16):
    tt = t(d); freq = 50+110*np.exp(-tt*35)
    return np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-tt*22)
def caixa(d=0.14):
    tt = t(d); r = rng.standard_normal(len(tt))
    return r*0.8*np.exp(-tt*28)+np.sin(2*np.pi*190*tt)*0.6*np.exp(-tt*35)
def chimbal(d=0.05, brilho=1.0):
    tt = t(d); r = np.diff(rng.standard_normal(len(tt)), prepend=0)
    return r*np.exp(-tt*(90/brilho))
def tom(f0, d=0.12):
    tt = t(d); freq = f0*(0.6+0.4*np.exp(-tt*30))
    return np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-tt*28)
def aro(d=0.04):
    tt = t(d)
    return (np.sin(2*np.pi*1400*tt)+0.5*np.sin(2*np.pi*2300*tt))*np.exp(-tt*120)
salvar("letra1", chimbal(0.05, 1.0), 0.28)
salvar("letra2", chimbal(0.04, 1.4), 0.25)
salvar("letra3", aro(), 0.25)
salvar("letra4", tom(220, 0.10), 0.3)
salvar("espaco", bumbo(0.14), 0.45)
salvar("apagar", caixa(0.11), 0.35)

# ---- sons por tipo de elemento (escala de Re maior, curtos, eco leve) ----
def piano_curto(f, d=0.55): return reverb(nota_piano(f, d), 1.0, 0.28, 0.35)
def duas_notas(f1, f2):
    return reverb(somar(nota_piano(f1, 0.5), deslocar(nota_piano(f2, 0.5), 0.09)), 1.0, 0.28, 0.35)
def pad_curto(*fs):
    return reverb(somar(*[pad(f, 0.7, 0.12) for f in fs]), 1.2, 0.3, 0.4)

salvar("botao", piano_curto(587.33), 0.38, 0.7, 0.08)          # re5
salvar("link", piano_curto(739.99), 0.36, 0.7, 0.08)           # fa# 5
salvar("edicao", pad_curto(146.83, 220.0), 0.34, 0.8, 0.1)     # re3 + la3
salvar("caixa_marcada", duas_notas(659.25, 880.0), 0.38, 0.75, 0.08)     # mi5 -> la5 (sobe)
salvar("caixa_desmarcada", duas_notas(880.0, 659.25), 0.34, 0.75, 0.08)  # la5 -> mi5 (desce)
salvar("menu", piano_curto(329.63), 0.38, 0.7, 0.08)           # mi4
salvar("lista", piano_curto(440.0, 0.4), 0.3, 0.5, 0.06)       # la4, bem curto
salvar("titulo", pad_curto(185.0, 277.18), 0.34, 0.8, 0.1)     # fa#3 + do#4
salvar("aba", piano_curto(493.88), 0.36, 0.7, 0.08)            # si4
salvar("controle", piano_curto(783.99), 0.34, 0.7, 0.08)       # sol5
print(sorted(os.listdir(PASTA)))
