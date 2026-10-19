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
import speech
import textInfos
import treeInterceptorHandler
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

# Conjuntos de sons: (pasta, nome mostrado na caixa combinada).
# O primeiro, "profetico", usa os arquivos que ficam direto na pasta sons.
# Os outros usam sons/<pasta>. Para criar um tema novo, crie a pasta com os mesmos nomes de arquivo.
TEMAS = [
    ("profetico", "Profético: piano e pads com eco (padrão)"),
    ("pads", "Somente pads"),
    ("piano_reverb", "Piano com reverb intenso"),
    ("celular_classico", "Celular clássico: bipes eletrônicos"),
    ("smartphone", "Smartphone moderno: toques suaves"),
]
TEMA_PADRAO = "profetico"

# Tipo de elemento -> arquivo de som.
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

# Prioridade quando um trecho da pagina tem varios elementos (ex.: titulo com link dentro).
_PRIORIDADE = ["caixa", "botao", "link", "edicao", "controle", "aba", "menu", "titulo", "lista"]

# Elementos "recipiente": nao tocam o som generico ao receber o foco.
_CONTAINERS = set()
for _nome in ("WINDOW", "PANE", "FRAME", "DIALOG", "APPLICATION", "DOCUMENT", "SECTION", "GROUPING",
              "FORM", "TOOLBAR", "STATUSBAR", "MENUBAR", "POPUPMENU", "TREEVIEW", "LIST", "TABCONTROL",
              "LANDMARK", "EMBEDDEDOBJECT", "INTERNALFRAME", "BORDER", "UNKNOWN", "TABLE", "TERMINAL"):
    _papel = getattr(controlTypes.Role, _nome, None)
    if _papel is not None:
        _CONTAINERS.add(_papel)

# Motivos de fala que indicam navegacao com setas ou teclas de navegacao rapida.
_RAZOES_NAVEGACAO = tuple(
    getattr(controlTypes.OutputReason, _n) for _n in ("CARET", "QUICKNAV")
    if hasattr(controlTypes.OutputReason, _n)
)
# -------------------------------

config.conf.spec[SECAO] = {
    "ligado": "boolean(default=True)",
    "volume": "integer(default=80, min=0, max=100)",
    "abertura": "boolean(default=True)",
    "carregamento": "boolean(default=True)",
    "digitacao": "boolean(default=True)",
    "enter": "boolean(default=True)",
    "foco": "boolean(default=True)",
    "navegacao": "boolean(default=True)",
    "generico": "boolean(default=True)",
    "tema": 'string(default="profetico")',
}

# Mudancas temporarias feitas pelos atalhos (voltam ao normal ao reiniciar o NVDA)
_sessao = {"mudo": False, "semDigitar": False}


def _conf():
    return config.conf[SECAO]


def _temaValido(tema):
    return tema if tema in dict(TEMAS) else TEMA_PADRAO


def _pastaTema(tema):
    tema = _temaValido(tema)
    return _PASTA if tema == TEMA_PADRAO else os.path.join(_PASTA, tema)


def aplicarVolume(volume=None, tema=None):
    """Cria copias dos sons do tema com o volume escolhido (o NVDA toca arquivos prontos)."""
    if _CACHE is None:
        return
    try:
        tema = _temaValido(_conf()["tema"] if tema is None else tema)
        fator = (_conf()["volume"] if volume is None else volume) / 100.0
        origem = _pastaTema(tema)
        destino = os.path.join(_CACHE, tema)
        os.makedirs(destino, exist_ok=True)
        for nome in os.listdir(origem):
            if not nome.lower().endswith(".wav"):
                continue
            with wave.open(os.path.join(origem, nome), "rb") as w:
                params = w.getparams()
                dados = w.readframes(w.getnframes())
            amostras = array.array("h")
            amostras.frombytes(dados)
            escalado = array.array("h", (int(a * fator) for a in amostras))
            with wave.open(os.path.join(destino, nome), "wb") as w:
                w.setparams(params)
                w.writeframes(escalado.tobytes())
    except Exception:
        log.error("Alessa Effects: erro ao aplicar o volume", exc_info=True)


def tocar(nome, tema=None):
    try:
        tema = _temaValido(_conf()["tema"] if tema is None else tema)
        arquivo = nome + ".wav"
        caminho = os.path.join(_CACHE, tema, arquivo) if _CACHE else ""
        if not (caminho and os.path.isfile(caminho)):
            caminho = os.path.join(_pastaTema(tema), arquivo)
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
        self.escolhaTema = ajuda.addLabeledControl(
            "Conjunto de sons:", wx.Choice, choices=[nome for _, nome in TEMAS]
        )
        ids = [i for i, _ in TEMAS]
        self.escolhaTema.SetSelection(ids.index(_temaValido(c["tema"])))
        self.spinVolume = ajuda.addLabeledControl(
            "Volume dos efeitos (0 a 100):", wx.SpinCtrl, min=0, max=100, initial=c["volume"]
        )
        self.cbAbertura = ajuda.addItem(wx.CheckBox(self, label="Som ao abrir programas e janelas"))
        self.cbAbertura.SetValue(c["abertura"])
        self.cbCarregamento = ajuda.addItem(wx.CheckBox(self, label="Som ao terminar de carregar páginas"))
        self.cbCarregamento.SetValue(c["carregamento"])
        self.cbDigitacao = ajuda.addItem(wx.CheckBox(self, label="Sons ao digitar"))
        self.cbDigitacao.SetValue(c["digitacao"])
        self.cbEnter = ajuda.addItem(wx.CheckBox(self, label="Som ao apertar Enter"))
        self.cbEnter.SetValue(c["enter"])
        self.cbFoco = ajuda.addItem(wx.CheckBox(
            self, label="Sons ao mover o foco (Tab e setas): botão, link, caixa de texto, lista, título..."))
        self.cbFoco.SetValue(c["foco"])
        self.cbNavegacao = ajuda.addItem(wx.CheckBox(
            self, label="Sons ao navegar com as setas e teclas de navegação rápida em páginas web"))
        self.cbNavegacao.SetValue(c["navegacao"])
        self.cbGenerico = ajuda.addItem(wx.CheckBox(
            self, label="Som genérico para outros elementos que recebem o foco"))
        self.cbGenerico.SetValue(c["generico"])
        self.btnTestar = ajuda.addItem(wx.Button(self, label="Ouvir exemplo do conjunto escolhido"))
        self.btnTestar.Bind(wx.EVT_BUTTON, self.onTestar)

    def _temaEscolhido(self):
        return TEMAS[self.escolhaTema.GetSelection()][0]

    def onTestar(self, evento):
        tema = self._temaEscolhido()
        aplicarVolume(self.spinVolume.GetValue(), tema)
        tocar("abrir", tema)
        wx.CallLater(1400, tocar, "botao", tema)
        wx.CallLater(2000, tocar, "caixa_marcada", tema)
        wx.CallLater(2700, tocar, "enter", tema)

    def onSave(self):
        c = _conf()
        c["ligado"] = self.cbLigado.GetValue()
        c["tema"] = self._temaEscolhido()
        c["volume"] = self.spinVolume.GetValue()
        c["abertura"] = self.cbAbertura.GetValue()
        c["carregamento"] = self.cbCarregamento.GetValue()
        c["digitacao"] = self.cbDigitacao.GetValue()
        c["enter"] = self.cbEnter.GetValue()
        c["foco"] = self.cbFoco.GetValue()
        c["navegacao"] = self.cbNavegacao.GetValue()
        c["generico"] = self.cbGenerico.GetValue()
        aplicarVolume()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        self._ultimo = 0.0
        self._ultimoFoco = 0.0
        self._ultimoAbrir = 0.0
        self._originais = []
        aplicarVolume()
        NVDASettingsDialog.categoryClasses.append(PainelAlessa)
        self._instalarGancho()

    def terminate(self):
        self._removerGancho()
        try:
            NVDASettingsDialog.categoryClasses.remove(PainelAlessa)
        except Exception:
            pass
        super().terminate()

    # ---- Navegacao com setas em paginas web (modo de navegacao) ----
    def _instalarGancho(self):
        """Acompanha a fala do NVDA ao mover o cursor em paginas web, onde o foco nao muda."""
        try:
            for modulo in (speech, getattr(speech, "speech", None)):
                if modulo is None or not hasattr(modulo, "speakTextInfo"):
                    continue
                original = modulo.speakTextInfo
                if getattr(original, "_alessa", False):
                    continue

                def novo(info, *args, _orig=original, **kwargs):
                    try:
                        self._aoFalarTexto(info, kwargs)
                    except Exception:
                        log.debugWarning("Alessa Effects: erro no gancho de navegacao", exc_info=True)
                    return _orig(info, *args, **kwargs)

                novo._alessa = True
                modulo.speakTextInfo = novo
                self._originais.append((modulo, original))
        except Exception:
            log.error("Alessa Effects: nao foi possivel instalar o gancho de navegacao", exc_info=True)

    def _removerGancho(self):
        for modulo, original in self._originais:
            try:
                modulo.speakTextInfo = original
            except Exception:
                pass
        self._originais = []

    def _aoFalarTexto(self, info, kwargs):
        if kwargs.get("reason") not in _RAZOES_NAVEGACAO:
            return
        if not self._ativo("navegacao"):
            return
        if not isinstance(getattr(info, "obj", None), treeInterceptorHandler.TreeInterceptor):
            return
        agora = time.monotonic()
        if agora - self._ultimoFoco < INTERVALO_FOCO:
            return
        som = self._somDoTrecho(info)
        if som:
            self._ultimoFoco = agora
            tocar(som)

    @staticmethod
    def _somDoTrecho(info):
        encontrados = {}
        for item in info.getTextWithFields():
            if isinstance(item, textInfos.FieldCommand) and item.command == "controlStart":
                campo = item.field
                base = MAPA_SONS.get(campo.get("role"))
                if not base:
                    continue
                final = base
                if base == "caixa":
                    estados = campo.get("states") or ()
                    marcada = controlTypes.State.CHECKED in estados
                    final = "caixa_marcada" if marcada else "caixa_desmarcada"
                encontrados[base] = final
        for base in _PRIORIDADE:
            if base in encontrados:
                return encontrados[base]
        return None

    @staticmethod
    def _eFocalizavel(obj):
        return controlTypes.State.FOCUSABLE in obj.states and obj.role not in _CONTAINERS

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
                elif som is None and _conf()["generico"] and self._eFocalizavel(obj):
                    som = "controle"
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
