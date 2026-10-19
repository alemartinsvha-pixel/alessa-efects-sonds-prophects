# Gera os temas de som novos (pads, piano_reverb, celular_classico, smartphone).
# O tema "profetico" e o original e fica direto na pasta sons (veja gerar_sons.py).
import numpy as np, wave, os
SR = 44100
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
rng = np.random.default_rng(23)
NOMES = ["abrir", "carregou", "enter", "letra1", "letra2", "letra3", "letra4", "espaco", "apagar",
         "botao", "link", "edicao", "caixa_marcada", "caixa_desmarcada", "menu", "lista",
         "titulo", "aba", "controle"]

def t(d): return np.arange(int(SR*d))/SR
def somar(*cs):
    s = np.zeros(max(len(c) for c in cs))
    for c in cs: s[:len(c)] += c
    return s
def deslocar(x, seg): return np.pad(x, (int(seg*SR), 0))
def suavizar(x, n): return np.convolve(x, np.ones(n)/n, "same")

def reverb(x, cauda=2.2, mistura=0.5, tau=0.7):
    n = int(cauda*SR)
    ir = rng.standard_normal(n)*np.exp(-np.arange(n)/SR/tau)
    ir = suavizar(ir, 10); ir /= np.sqrt(np.sum(ir**2))
    tam = len(x)+n
    molhado = np.fft.irfft(np.fft.rfft(x, tam)*np.fft.rfft(ir, tam), tam)
    seco = np.pad(x, (0, n))
    molhado *= np.max(np.abs(seco))/(np.max(np.abs(molhado))+1e-9)
    return seco*(1-mistura)+molhado*mistura

def nota_piano(f, d=1.2):
    tt = t(d); x = np.zeros_like(tt)
    for n in range(1, 8):
        x += (1/n**1.3)*np.sin(2*np.pi*f*n*np.sqrt(1+0.0003*n*n)*tt)*np.exp(-tt*(1.6+1.4*n))
    return x*np.minimum(1, tt/0.012)

def pad(f, d=1.5, ataque=0.3):
    tt = t(d); x = np.zeros_like(tt)
    for desv in (-0.006, -0.002, 0.002, 0.006):
        for n in range(1, 6):
            x += (1/n**1.5)*np.sin(2*np.pi*f*(1+desv)*n*tt+n*1.7)
    return x*np.minimum(1, tt/ataque)*np.exp(-np.maximum(0, tt-ataque)*1.8)

def pad_toque(f, d=0.14):
    tt = t(d); x = np.zeros_like(tt)
    for desv in (-0.005, 0.005):
        for n in range(1, 4): x += (1/n)*np.sin(2*np.pi*f*(1+desv)*n*tt)
    return x*np.minimum(1, tt/0.008)*np.exp(-tt*18)

def sino(f, d=0.5, decay=7):
    tt = t(d); x = np.zeros_like(tt)
    for r, a, dc in ((1, 1, decay), (2.76, 0.5, decay*1.6), (5.4, 0.25, decay*2.5)):
        x += a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*dc)
    return x*np.minimum(1, tt/0.002)

def bip(f, d=0.08, forma="sin", decay=25):
    tt = t(d); fase = 2*np.pi*f*tt
    w = {"sin": np.sin(fase), "quad": np.tanh(3*np.sin(fase))*0.7,
         "tri": 2/np.pi*np.arcsin(np.sin(fase))}[forma]
    return w*np.minimum(1, tt/0.002)*np.exp(-tt*decay)

def clique(d=0.02, f=2500):
    tt = t(d); r = np.diff(rng.standard_normal(len(tt)), prepend=0)
    return r*np.exp(-tt*200)+0.5*np.sin(2*np.pi*f*tt)*np.exp(-tt*250)

def toque(f=180, d=0.06):
    tt = t(d); ruido = suavizar(rng.standard_normal(len(tt)), 12)
    return np.sin(2*np.pi*f*tt)*np.exp(-tt*70)+0.6*ruido*np.exp(-tt*150)

def pop(f0, f1, d=0.08):
    tt = t(d); freq = f0+(f1-f0)*(1-np.exp(-tt*60))
    return np.sin(2*np.pi*np.cumsum(freq)/SR)*np.minimum(1, tt/0.003)*np.exp(-tt*35)

def T(x, pico, dur=None, fade=0.004): return (x, pico, dur, fade)

def salvar(tema, nome, item):
    x, pico, dur, fade = item
    if dur: x = x[:int(dur*SR)]
    x = x/(np.max(np.abs(x))+1e-9)*pico
    n = max(1, int(fade*SR)); x[-n:] *= np.linspace(1, 0, n)
    pasta = os.path.join(BASE, tema); os.makedirs(pasta, exist_ok=True)
    with wave.open(os.path.join(pasta, nome+".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x*32767).astype("<i2").tobytes())

D5, Fs5, A5, E5, B4, G5, A4, E4, D4, Fs4, Cs5 = 587.33, 739.99, 880.0, 659.25, 493.88, 783.99, 440.0, 329.63, 293.66, 369.99, 554.37
D3, A3, Fs3, Cs4 = 146.83, 220.0, 185.0, 277.18

def pc(*fs, d=0.8, mist=0.3, tau=0.4, atk=0.12):
    return reverb(somar(*[pad(f, d, atk) for f in fs]), 1.2, mist, tau)

# ---------------- Tema: somente pads ----------------
pads = {
 "abrir": T(reverb(somar(pad(D3,1.6,.25), .8*pad(A3,1.6,.3), .6*pad(D4,1.6,.35)), 2.0, .5, .8), .42, 1.5, .12),
 "carregou": T(reverb(somar(pad(D3,2.2,.4), .8*pad(A3,2.2,.45), .6*pad(E4,2.2,.5), .4*pad(B4,2.2,.55)), 2.5, .6, .9), .4, 1.9, .25),
 "enter": T(reverb(somar(pad(A3,1.0,.1), deslocar(.8*pad(E4,.9,.1), .08)), 1.6, .45, .5), .42, 1.0, .1),
 "letra1": T(pad_toque(D4), .2), "letra2": T(pad_toque(Fs4), .2),
 "letra3": T(pad_toque(A4), .2), "letra4": T(pad_toque(E4), .2),
 "espaco": T(pad_toque(D3, .18), .3), "apagar": T(pad_toque(196.0, .12), .24),
 "botao": T(pc(D4, A4), .36, .7, .1), "link": T(pc(Fs4, Cs5), .34, .7, .1),
 "edicao": T(pc(D3, A3), .34, .8, .1), "menu": T(pc(E4, B4), .34, .7, .1),
 "lista": T(pc(A3, E4, d=.4, atk=.06), .28, .5, .06), "titulo": T(pc(Fs3, Cs4), .34, .8, .1),
 "aba": T(pc(B4, Fs4), .34, .7, .1), "controle": T(pc(G5/2, D5/2*1.0), .32, .7, .1),
 "caixa_marcada": T(reverb(somar(pad(E4,.5,.05), deslocar(pad(A4,.5,.05), .09)), 1.0, .3, .35), .36, .8, .08),
 "caixa_desmarcada": T(reverb(somar(pad(A4,.5,.05), deslocar(pad(E4,.5,.05), .09)), 1.0, .3, .35), .32, .8, .08),
}

# ---------------- Tema: piano com reverb intenso ----------------
def rv(x, c=2.5, m=.65, tau=1.0): return reverb(x, c, m, tau)
def pn(f, d=.5): return rv(nota_piano(f, d))
piano = {
 "abrir": T(rv(somar(nota_piano(A4,1.4), .5*nota_piano(A5,1.4)), 4.0, .72, 1.8), .5, 2.4, .2),
 "carregou": T(rv(somar(nota_piano(D4,1.8), deslocar(.8*nota_piano(A4,1.6),.12), deslocar(.7*nota_piano(D5,1.4),.24)), 4.5, .72, 2.0), .45, 2.8, .3),
 "enter": T(rv(somar(nota_piano(A4,1.2), deslocar(.8*nota_piano(E5,1.0),.07), deslocar(.5*nota_piano(A5,.9),.14)), 3.5, .7, 1.5), .5, 1.8, .2),
 "letra1": T(rv(nota_piano(D5,.3), 1.5, .55, .6), .22, .5, .08), "letra2": T(rv(nota_piano(Fs5,.3), 1.5, .55, .6), .2, .5, .08),
 "letra3": T(rv(nota_piano(A5,.3), 1.5, .55, .6), .2, .5, .08), "letra4": T(rv(nota_piano(E5,.3), 1.5, .55, .6), .2, .5, .08),
 "espaco": T(rv(nota_piano(D3,.4), 1.5, .5, .6), .34, .5, .08),
 "apagar": T(rv(somar(nota_piano(A4,.25), deslocar(nota_piano(E4,.25),.06)), 1.5, .5, .6), .24, .4, .08),
 "botao": T(pn(D5), .38, .9, .12), "link": T(pn(Fs5), .36, .9, .12), "edicao": T(pn(D3), .4, .9, .12),
 "menu": T(pn(E4), .38, .9, .12), "lista": T(rv(nota_piano(A4,.3), 1.6, .55, .6), .3, .6, .08),
 "titulo": T(rv(somar(nota_piano(Fs3,.6), .7*nota_piano(Cs4,.6)), 2.5, .65, 1.0), .38, 1.0, .12),
 "aba": T(pn(B4), .36, .9, .12), "controle": T(pn(G5), .34, .9, .12),
 "caixa_marcada": T(rv(somar(nota_piano(E5,.5), deslocar(nota_piano(A5,.5),.09)), 2.5, .65, 1.0), .38, 1.0, .12),
 "caixa_desmarcada": T(rv(somar(nota_piano(A5,.5), deslocar(nota_piano(E5,.5),.09)), 2.5, .65, 1.0), .34, 1.0, .12),
}

# ---------------- Tema: celular classico (bipes eletronicos) ----------------
def dois(f1, f2, forma="sin"): return somar(bip(f1,.07,forma,30), deslocar(bip(f2,.09,forma,28), .07))
classico = {
 "abrir": T(somar(bip(880,.09,"quad",25), deslocar(bip(1320,.12,"quad",22), .09)), .32, .3),
 "carregou": T(somar(bip(784,.09,"tri",22), deslocar(bip(988,.09,"tri",22), .09), deslocar(bip(1318,.16,"tri",18), .18)), .34, .4),
 "enter": T(bip(1568,.25,"sin",14), .36, .3),
 "letra1": T(clique(.02,2200), .24), "letra2": T(clique(.02,2800), .22),
 "letra3": T(clique(.02,3400), .22), "letra4": T(clique(.025,1800), .24),
 "espaco": T(toque(130,.06), .3), "apagar": T(bip(700,.06,"sin",40)*1.0+deslocar(bip(500,.06,"sin",40),.04)[:int(.06*SR)], .26),
 "botao": T(bip(1000,.05,"quad",50), .3), "link": T(somar(bip(1400,.04,"quad",60), deslocar(bip(1400,.04,"quad",60),.06)), .28),
 "edicao": T(bip(500,.08,"tri",30), .32), "menu": T(bip(800,.05,"quad",50), .3),
 "lista": T(bip(1200,.03,"sin",80), .22), "titulo": T(bip(700,.12,"tri",22), .32),
 "aba": T(bip(900,.06,"quad",45), .3), "controle": T(bip(1100,.05,"tri",45), .3),
 "caixa_marcada": T(dois(800,1200,"quad"), .3, .3), "caixa_desmarcada": T(dois(1200,800,"quad"), .28, .3),
}

# ---------------- Tema: smartphone moderno (toques suaves) ----------------
smartphone = {
 "abrir": T(somar(sino(1046.5,.5,9), deslocar(.8*sino(1568,.5,9), .1)), .4, .5, .06),
 "carregou": T(somar(sino(880,.6,8), deslocar(.8*sino(1108.7,.6,8), .11), deslocar(.7*sino(1318.5,.7,7), .22)), .4, .8, .1),
 "enter": T(somar(pop(400,700,.09), deslocar(sino(1760,.35,11), .03)), .38, .4, .05),
 "letra1": T(toque(1400,.035), .24), "letra2": T(toque(1700,.035), .22),
 "letra3": T(toque(1250,.035), .22), "letra4": T(toque(1550,.035), .22),
 "espaco": T(toque(260,.06), .3), "apagar": T(toque(200,.05), .24),
 "botao": T(pop(350,650,.08), .36), "link": T(sino(1760,.25,18), .3, .25, .03),
 "edicao": T(toque(300,.08), .34), "menu": T(toque(520,.06), .32),
 "lista": T(toque(1900,.025), .2), "titulo": T(sino(660,.4,9), .32, .4, .05),
 "aba": T(toque(700,.05), .3), "controle": T(toque(1100,.04), .28),
 "caixa_marcada": T(somar(pop(350,650,.07), deslocar(pop(500,900,.07), .07)), .34, .2),
 "caixa_desmarcada": T(somar(pop(500,900,.07), deslocar(pop(350,550,.07), .07)), .3, .2),
}

for tema, dic in (("pads", pads), ("piano_reverb", piano), ("celular_classico", classico), ("smartphone", smartphone)):
    assert set(dic) == set(NOMES), (tema, set(NOMES) ^ set(dic))
    for nome in NOMES: salvar(tema, nome, dic[nome])
    print(tema, len(os.listdir(os.path.join(BASE, tema))), "sons")
