# -*- coding: UTF-8 -*-
# Alessa Effects Sounds Prophetic - efeitos sonoros para o NVDA.
# Copyright (C) 2026 Alessandra Acessibilidade Já.
# Licenciado sob a GNU General Public License, versão 2 (GPL v2).
import array
import os
import random
import time
import wave

import config
import controlTypes
import globalPluginHandler
import globalVars
import gui
import nvwave
import scriptHandler
import ui
import wx
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log

NOME = "Alessa Effects Sounds Prophetic"
SECAO = "alessaEffects"

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PASTA = os.path.join(_RAIZ, "sons")
try:
    _CACHE = os.path.join(globalVars.appArgs.configPath, "alessaEffects", "cache")
except Exception:
    _CACHE = None

# ---- CONFIGURACAO AVANCADA ----
LETRAS = ["letra1", "letra2", "letra3", "letra4"]  # sons sorteados ao digitar letras
INTERVALO_MINIMO = 0.02  # segundos entre dois sons de digitacao
INTERVALO_FOCO = 0.05    # segundos minimos entre dois sons de foco

# Tipo de elemento -> arquivo de som. Para mudar o som de um tipo, troque o nome do arquivo.
_ROLES = [
    ("BUTTON", "botao"), ("TOGGLEBUTTON", "botao"), ("SPLITBUTTON", "botao"), ("MENUBUTTON", "botao"),
    ("LINK", "link"),
    ("EDITABLETEXT", "edicao"), ("PASSWORDEDIT", "edicao"), ("TERMINAL", "edicao"),
    ("CHECKBOX", "caixa"), ("RADIOBUTTON", "caixa"), ("CHECKMENUITEM", "caixa"), ("RADIOMENUITEM", "caixa"),
    ("MENUITEM", "menu"),
    ("LISTITEM", "lista"), ("COMBOBOX", "lista"), ("TREEVIEWITEM", "lista"),
    ("HEADING", "titulo"),
    ("TAB", "aba"),
    ("SLIDER", "controle"), ("SPINBUTTON", "controle"),
]
MAPA_SONS = {}
for _nome, _som in _ROLES:
    _papel = getattr(controlTypes.Role, _nome, None)
    if _papel is not None:
        MAPA_SONS[_papel] = _som
# -------------------------------

config.conf.spec[SECAO] = {
    "ligado": "boolean(default=True)",
    "volume": "integer(default=80, min=0, max=100)",
    "abertura": "boolean(default=True)",
    "carregamento": "boolean(default=True)",
    "digitacao": "boolean(default=True)",
    "enter": "boolean(default=True)",
    "foco": "boolean(default=True)",
}

# Mudancas temporarias feitas pelos atalhos (voltam ao normal ao reiniciar o NVDA)
_sessao = {"mudo": False, "semDigitar": False}


def _conf():
    return config.conf[SECAO]


def aplicarVolume(volume=None):
    """Cria copias dos sons com o volume escolhido (o NVDA toca arquivos prontos)."""
    if _CACHE is None:
        return
    try:
        fator = (_conf()["volume"] if volume is None else volume) / 100.0
        os.makedirs(_CACHE, exist_ok=True)
        for nome in os.listdir(_PASTA):
            if not nome.lower().endswith(".wav"):
                continue
            with wave.open(os.path.join(_PASTA, nome), "rb") as w:
                params = w.getparams()
                dados = w.readframes(w.getnframes())
            amostras = array.array("h")
            amostras.frombytes(dados)
            escalado = array.array("h", (int(a * fator) for a in amostras))
            with wave.open(os.path.join(_CACHE, nome), "wb") as w:
                w.setparams(params)
                w.writeframes(escalado.tobytes())
    except Exception:
        log.error("Alessa Effects: erro ao aplicar o volume", exc_info=True)


def tocar(nome):
    try:
        arquivo = nome + ".wav"
        caminho = os.path.join(_CACHE, arquivo) if _CACHE else ""
        if not (caminho and os.path.isfile(caminho)):
            caminho = os.path.join(_PASTA, arquivo)
        nvwave.playWaveFile(caminho, asynchronous=True)
    except Exception:
        log.debugWarning("Alessa Effects: nao foi possivel tocar %s" % nome, exc_info=True)


class PainelAlessa(SettingsPanel):
    title = NOME

    def makeSettings(self, settingsSizer):
        c = _conf()
        ajuda = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        self.cbLigado = ajuda.addItem(wx.CheckBox(self, label="Ativar efeitos sonoros"))
        self.cbLigado.SetValue(c["ligado"])
        self.spinVolume = ajuda.addLabeledControl(
            "Volume dos efeitos (0 a 100):", wx.SpinCtrl, min=0, max=100, initial=c["volume"]
        )
        self.cbAbertura = ajuda.addItem(wx.CheckBox(self, label="Som ao abrir programas e janelas (piano)"))
        self.cbAbertura.SetValue(c["abertura"])
        self.cbCarregamento = ajuda.addItem(wx.CheckBox(self, label="Som ao terminar de carregar páginas (pad)"))
        self.cbCarregamento.SetValue(c["carregamento"])
        self.cbDigitacao = ajuda.addItem(wx.CheckBox(self, label="Sons de bateria ao digitar"))
        self.cbDigitacao.SetValue(c["digitacao"])
        self.cbEnter = ajuda.addItem(wx.CheckBox(self, label="Som de piano ao apertar Enter"))
        self.cbEnter.SetValue(c["enter"])
        self.cbFoco = ajuda.addItem(wx.CheckBox(
            self, label="Sons ao mover o foco (Tab e setas): botão, link, caixa de texto, lista, título..."))
        self.cbFoco.SetValue(c["foco"])
        self.btnTestar = ajuda.addItem(wx.Button(self, label="Ouvir exemplo"))
        self.btnTestar.Bind(wx.EVT_BUTTON, self.onTestar)

    def onTestar(self, evento):
        aplicarVolume(self.spinVolume.GetValue())
        tocar("abrir")
        wx.CallLater(1400, tocar, "carregou")
        wx.CallLater(3300, tocar, "enter")

    def onSave(self):
        c = _conf()
        c["ligado"] = self.cbLigado.GetValue()
        c["volume"] = self.spinVolume.GetValue()
        c["abertura"] = self.cbAbertura.GetValue()
        c["carregamento"] = self.cbCarregamento.GetValue()
        c["digitacao"] = self.cbDigitacao.GetValue()
        c["enter"] = self.cbEnter.GetValue()
        c["foco"] = self.cbFoco.GetValue()
        aplicarVolume()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        self._ultimo = 0.0
        self._ultimoFoco = 0.0
        self._ultimoAbrir = 0.0
        aplicarVolume()
        NVDASettingsDialog.categoryClasses.append(PainelAlessa)

    def terminate(self):
        try:
            NVDASettingsDialog.categoryClasses.remove(PainelAlessa)
        except Exception:
            pass
        super().terminate()

    @staticmethod
    def _ativo(chave):
        return _conf()["ligado"] and not _sessao["mudo"] and _conf()[chave]

    def event_foreground(self, obj, nextHandler):
        try:
            if self._ativo("abertura"):
                self._ultimoAbrir = time.monotonic()
                tocar("abrir")
        finally:
            nextHandler()

    def event_gainFocus(self, obj, nextHandler):
        try:
            agora = time.monotonic()
            if (self._ativo("foco") and agora - self._ultimoAbrir > 0.4
                    and agora - self._ultimoFoco >= INTERVALO_FOCO):
                som = MAPA_SONS.get(obj.role)
                if som == "caixa":
                    marcada = controlTypes.State.CHECKED in obj.states
                    som = "caixa_marcada" if marcada else "caixa_desmarcada"
                if som:
                    self._ultimoFoco = agora
                    tocar(som)
        except Exception:
            log.debugWarning("Alessa Effects: erro no som de foco", exc_info=True)
        finally:
            nextHandler()

    def event_documentLoadComplete(self, obj, nextHandler):
        try:
            if self._ativo("carregamento"):
                tocar("carregou")
        finally:
            nextHandler()

    def event_typedCharacter(self, obj, nextHandler, ch):
        try:
            agora = time.monotonic()
            if agora - self._ultimo >= INTERVALO_MINIMO:
                if ch in ("\r", "\n"):
                    if self._ativo("enter"):
                        self._ultimo = agora
                        tocar("enter")
                elif self._ativo("digitacao") and not _sessao["semDigitar"]:
                    self._ultimo = agora
                    if ch == " ":
                        tocar("espaco")
                    elif ch == "\b":
                        tocar("apagar")
                    else:
                        tocar(random.choice(LETRAS))
        finally:
            nextHandler()

    @scriptHandler.script(
        description="Liga ou desliga todos os efeitos sonoros",
        gesture="kb:NVDA+shift+e",
        category=NOME,
    )
    def script_alternarSons(self, gesture):
        _sessao["mudo"] = not _sessao["mudo"]
        ui.message("Efeitos sonoros desligados" if _sessao["mudo"] else "Efeitos sonoros ligados")

    @scriptHandler.script(
        description="Liga ou desliga os sons de digitação",
        gesture="kb:NVDA+shift+d",
        category=NOME,
    )
    def script_alternarDigitacao(self, gesture):
        _sessao["semDigitar"] = not _sessao["semDigitar"]
        ui.message("Sons de digitação desligados" if _sessao["semDigitar"] else "Sons de digitação ligados")
