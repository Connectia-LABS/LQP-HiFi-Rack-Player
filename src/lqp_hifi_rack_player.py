#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Connectia-LABS.
# Licensed under the PolyForm Noncommercial License 1.0.0. See LICENSE.
"""
LQP HiFi Rack Player — 4.0 WORLD EDITION — Windows 11
Un solo archivo .py, auto-instalable, con estética rack hi-fi 80/90.

NOVEDADES 4.0:
- EQ híbrido: las 10 palancas se ajustan manualmente aun después de usar IA.
- AI EQ AUTO: detecta el tema en reproducción, completa artista/título/género y puede
  lanzar la ecualización sin escribir datos manualmente.
- NVIDIA BYOK: cada usuario carga su API key; en Windows se guarda cifrada con DPAPI.
- Playlist con drag & drop desde el Explorador y reordenamiento por arrastre.
- RADIO WORLD por ciudades y reparación de streams mediante Radio-Browser.

NOVEDADES 3.2:
- AI EQ (NVIDIA Nemotron): escribí tu género musical, banda o tema, el modelo de
  tus parlantes y qué equipo tenés en la cadena de sonido, y la IA calcula la
  ecualización perfecta para vos. Se aplica al instante y se puede guardar con
  el nombre que quieras en MEMORY EQ.
- Logo LQP rediseñado: placa metálica retro con franjas 70s y tipografía de época.

NOVEDADES 3.1:
- Presets de ecualización dedicados para JBL 104 (Reference, Bass Boost, Noche, Voz).
- MEMORY EQ: guardá tus propios seteos de ecualización con nombre, borralos,
  e importá/exportá seteos en JSON para compartirlos entre PCs.
- Compatible con empaquetado a .exe (instalador de Windows).

NOVEDADES 3.0:
- Analizador de espectro LED de 20 bandas con peak-hold (estilo Technics/Pioneer).
- Cassette animado: carretes que giran y cinta que avanza con el tema.
- Display fluorescente con marquee, LEDs de REC / SIGNAL / STEREO.
- Vúmetro estéreo LED calibrado en dB reales con peak-hold y aviso de clip.
- ● REC "AIR CHECK": graba la radio en vivo a MP3 (como grabar cassettes en los 90).
- SLEEP TIMER con fade-out de volumen, como los equipos de rack de verdad.
- La configuración ahora guarda TODO: volumen, EQ, playlist, radios, salida, ventana.
- Fixes: barra de progreso que se congelaba, glitches de audio en radio,
  clicks al mover el ecualizador, shuffle que repetía el mismo tema.

BASE (de la 2.0):
- Reproductor local Hi-Fi: FLAC, MP3, WAV, OGG, M4A, AAC, AIFF, WMA, OPUS, APE, etc.
- Radio online argentina por streaming + Radio-Browser + logos con caché.
- Ecualizador gráfico de 10 bandas.
- Playlists y emisoras import/export: M3U, M3U8, JSON.
- Modo POWER STAGE: ganancia perceptual + compresor/limitador/soft-clip.
- Instalación automática de dependencias y descarga automática de FFmpeg portable.

Ejecución recomendada en Windows 11:
    py LQP_HiFi_Rack_Player_v4_WORLD.py

Nota técnica honesta:
El modo POWER STAGE no aumenta la potencia física real del amplificador/parlantes.
Eleva la ganancia digital y controla picos con DSP para más presión sonora percibida
sin clipping destructivo. Usalo progresivamente para cuidar tus JBL.
"""

from __future__ import annotations

import os
import sys
import json
import base64
import ctypes
import difflib
import socket
import webbrowser
import math
import time
import queue
import random
import shutil
import zipfile
import hashlib
import subprocess
import threading
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable, Any

APP_NAME = "LQP HiFi Rack Player"
APP_VERSION = "4.0 WORLD EDITION"
NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
NVIDIA_API_KEY_ENV = "NVIDIA_API_KEY"
NVIDIA_KEY_CONFIG_FIELD = "nvidia_api_key_protected"
NVIDIA_KEYS_URL = "https://build.nvidia.com/settings/api-keys"

AUDIO_EXTENSIONS = {
    ".flac", ".mp3", ".wav", ".ogg", ".oga", ".m4a", ".aac", ".aiff", ".aif",
    ".wma", ".opus", ".alac", ".mp4", ".mka", ".ape", ".wv", ".tta"
}

REQUIRED_PACKAGES = [
    ("numpy", "numpy"),
    ("sounddevice", "sounddevice"),
    ("requests", "requests"),
    ("PIL", "pillow"),
    ("mutagen", "mutagen"),
    ("scipy", "scipy"),
    ("tkinterdnd2", "tkinterdnd2"),
]

# Presets embebidos. La app puede refrescar stream/logo con Radio-Browser.
RADIO_PRESETS: List[Dict[str, str]] = [
    {
        "name": "Aspen 102.3",
        "genre": "Classic Hits / Pop Rock",
        "stream_url": "http://playerservices.streamtheworld.com/api/livestream-redirect/ASPENAAC",
        "homepage": "https://fmaspen.com/",
        "logo_query": "Aspen 102.3 Argentina",
    },
    {
        "name": "Mega 98.3",
        "genre": "Rock Nacional",
        "stream_url": "https://server1.stweb.tv/mega983/live/chunks.m3u8",
        "homepage": "https://mega983.com.ar/",
        "logo_query": "Mega 98.3 Argentina",
    },
    {
        "name": "Rock & Pop 95.9",
        "genre": "Rock / Pop / Actualidad",
        "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/ROCKANDPOPAAC.aac",
        "homepage": "https://fmrockandpop.com/",
        "logo_query": "Rock and Pop 95.9 Argentina",
    },
    {
        "name": "Vorterix",
        "genre": "Rock / Streaming / Cultura",
        "stream_url": "http://147.135.11.82:9904/;",
        "homepage": "https://vorterix.com/",
        "logo_query": "Vorterix Argentina",
    },
    {
        "name": "La 100 99.9",
        "genre": "Pop / Hits / Magazine",
        "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/FM999_56.mp3",
        "homepage": "https://la100.cienradios.com/",
        "logo_query": "La 100 99.9 Argentina",
    },
    {
        "name": "Radio 10 AM 710",
        "genre": "Noticias / Actualidad",
        "stream_url": "https://radio10.stweb.tv/radio10/live/playlist.m3u8",
        "homepage": "https://radio10.com.ar/",
        "logo_query": "Radio 10 Argentina",
    },
    {
        "name": "Pop Radio 101.5",
        "genre": "Pop / Magazine",
        "stream_url": "https://s8.stweb.tv/popradio/live/playlist.m3u8",
        "homepage": "https://popradio1015.com.ar/",
        "logo_query": "Pop Radio 101.5 Argentina",
    },
    {
        "name": "LOS40 Argentina",
        "genre": "Top 40 / Pop",
        "stream_url": "http://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_ARGENTINAAAC",
        "homepage": "https://los40.com.ar/",
        "logo_query": "LOS40 Argentina",
    },
    {
        "name": "Radio Disney Argentina",
        "genre": "Pop / Hits",
        "stream_url": "http://disneyargradio-lh.akamaihd.net/i/ARG_Disney_RADIO@102438/master.m3u8",
        "homepage": "https://radiodisney.disneylatino.com/argentina/",
        "logo_query": "Radio Disney Argentina",
    },
    {
        "name": "Metro 95.1",
        "genre": "Música / Magazine",
        "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/METROAAC.aac",
        "homepage": "https://metro951.com/",
        "logo_query": "Metro 95.1 Argentina",
    },
    {
        "name": "Blue 100.7",
        "genre": "Classic / Adult Contemporary",
        "stream_url": "https://blue.secure2.footprint.net/egress/bhandler/streamroot_lsd2latam/blue/chunklist_b98304.m3u8",
        "homepage": "https://bluefm.com.ar/",
        "logo_query": "Blue 100.7 Argentina",
    },
    {
        "name": "Con Vos FM",
        "genre": "Actualidad / Magazine",
        "stream_url": "https://server1.stweb.tv/rcvos/live/playlist.m3u8",
        "homepage": "https://radioconvos.com.ar/",
        "logo_query": "Con Vos FM Argentina",
    },
    {
        "name": "Vale 97.5",
        "genre": "Latina / Pop",
        "stream_url": "http://vale.stweb.tv:1935/vale/live/playlist.m3u8",
        "homepage": "https://vale975.com/",
        "logo_query": "Vale 97.5 Argentina",
    },
    {
        "name": "Futurock",
        "genre": "Online / Música / Actualidad",
        "stream_url": "http://radio1.us.mediastre.am/futurockargentina.aac",
        "homepage": "https://futurock.fm/",
        "logo_query": "Futurock Argentina",
    },
    {
        "name": "Urbana Play 104.3",
        "genre": "Streaming / Magazine / Música",
        "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/URBANAPLAYAAC.aac",
        "homepage": "https://urbanaplayfm.com/",
        "logo_query": "Urbana Play 104.3 Argentina",
    },
]

WORLD_CITY_PRESETS: Dict[str, Dict[str, Any]] = {
    "Miami": {"country_code":"US","country":"United States","state":"Florida","queries":["Power 96","Y100 Miami","WLRN","Radio Mambi","Revolution 93.5"]},
    "New York": {"country_code":"US","country":"United States","state":"New York","queries":["Z100 New York","WNYC","Hot 97","Q104.3","WBGO"]},
    "Ibiza": {"country_code":"ES","country":"Spain","state":"Balearic Islands","queries":["Ibiza Sonica","Ibiza Global Radio","Pure Ibiza Radio","OpenLab Ibiza"]},
    "Madrid": {"country_code":"ES","country":"Spain","state":"Madrid","queries":["Los 40","Cadena SER Madrid","Radio 3","Europa FM","Cadena 100"]},
    "London": {"country_code":"GB","country":"United Kingdom","state":"England","queries":["BBC Radio 1","BBC Radio 2","Capital London","Jazz FM","NTS Radio"]},
    "Paris": {"country_code":"FR","country":"France","state":"Île-de-France","queries":["FIP","France Inter","NRJ","Radio Nova","TSF Jazz"]},
    "Berlin": {"country_code":"DE","country":"Germany","state":"Berlin","queries":["Radio Eins","FluxFM","Fritz","JazzRadio Berlin","Deutschlandfunk Kultur"]},
    "Tokyo": {"country_code":"JP","country":"Japan","state":"Tokyo","queries":["J-WAVE","Tokyo FM","NHK Radio","InterFM"]},
    "Rio de Janeiro": {"country_code":"BR","country":"Brazil","state":"Rio de Janeiro","queries":["Rádio Globo Rio","JB FM","Mix Rio","Paradiso FM","MEC FM"]},
    "Ciudad de México": {"country_code":"MX","country":"Mexico","state":"Ciudad de México","queries":["Reactor 105.7","W Radio México","Universal 88.1","Alfa 91.3","Ibero 90.9"]},
}



def _no_window_kwargs() -> Dict[str, Any]:
    # En el .exe empaquetado (sin consola) evita que cada FFmpeg abra una
    # ventana negra. En modo consola no cambia nada visible.
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}  # type: ignore[attr-defined]
    return {}


def _run_subprocess(cmd: List[str], timeout: Optional[int] = None) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            **_no_window_kwargs(),
        )
        return proc.returncode, proc.stdout
    except Exception as exc:
        return 999, str(exc)


def ensure_python_packages() -> None:
    if getattr(sys, "frozen", False):
        # Ejecutable empaquetado: las dependencias ya vienen adentro.
        return
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(import_name)
        except Exception:
            missing.append(pip_name)

    if not missing:
        return

    print("\n[LQP HiFi] Faltan dependencias:", ", ".join(missing))
    print("[LQP HiFi] Instalando automáticamente. Primera ejecución: puede tardar.\n")
    _run_subprocess([sys.executable, "-m", "ensurepip", "--upgrade"], timeout=120)
    _run_subprocess([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "--user"], timeout=300)

    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--user"] + missing
    code, out = _run_subprocess(cmd, timeout=1800)
    print(out)
    if code != 0:
        print("[LQP HiFi] Reintentando instalación global. Si Windows pregunta, aceptá permisos de administrador.")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + missing
        code, out = _run_subprocess(cmd, timeout=1800)
        print(out)
        if code != 0:
            raise RuntimeError(
                "No se pudieron instalar dependencias automáticamente.\n"
                "Ejecutá PowerShell como administrador y corré:\n"
                f"{sys.executable} -m pip install " + " ".join(missing)
            )


ensure_python_packages()

import numpy as np
import sounddevice as sd
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont
from mutagen import File as MutagenFile
from scipy import signal

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk, simpledialog
except Exception as exc:
    raise RuntimeError("Tkinter no está disponible. Instalá Python oficial desde python.org con Tcl/Tk habilitado.") from exc

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


def app_cache_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    path = Path(base) / "LQP_HiFi_Rack_Player"
    path.mkdir(parents=True, exist_ok=True)
    return path


def app_config_path() -> Path:
    return app_cache_dir() / "config_radio_power.json"


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _blob_from_bytes(data: bytes) -> Tuple[_DataBlob, Any]:
    buffer = ctypes.create_string_buffer(data)
    return _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))), buffer


def protect_secret_for_current_user(secret: str) -> str:
    if not secret: return ""
    if os.name != "nt": raise RuntimeError("El guardado cifrado de la API key está disponible en Windows.")
    crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined]
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    crypt32.CryptProtectData.argtypes = [ctypes.POINTER(_DataBlob),ctypes.c_wchar_p,ctypes.POINTER(_DataBlob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(_DataBlob)]
    crypt32.CryptProtectData.restype = ctypes.c_bool
    kernel32.LocalFree.argtypes=[ctypes.c_void_p]; kernel32.LocalFree.restype=ctypes.c_void_p
    in_blob,_buf=_blob_from_bytes(secret.encode('utf-8')); out_blob=_DataBlob()
    if not crypt32.CryptProtectData(ctypes.byref(in_blob),APP_NAME,None,None,None,0x01,ctypes.byref(out_blob)):
        raise ctypes.WinError()
    try: encrypted=ctypes.string_at(out_blob.pbData,out_blob.cbData)
    finally: kernel32.LocalFree(out_blob.pbData)
    return base64.urlsafe_b64encode(encrypted).decode('ascii')


def unprotect_secret_for_current_user(value: str) -> str:
    if not value or os.name != "nt": return ""
    try: encrypted=base64.urlsafe_b64decode(value.encode('ascii'))
    except Exception: return ""
    crypt32=ctypes.windll.crypt32  # type: ignore[attr-defined]
    kernel32=ctypes.windll.kernel32  # type: ignore[attr-defined]
    crypt32.CryptUnprotectData.argtypes=[ctypes.POINTER(_DataBlob),ctypes.POINTER(ctypes.c_wchar_p),ctypes.POINTER(_DataBlob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(_DataBlob)]
    crypt32.CryptUnprotectData.restype=ctypes.c_bool
    kernel32.LocalFree.argtypes=[ctypes.c_void_p]; kernel32.LocalFree.restype=ctypes.c_void_p
    in_blob,_buf=_blob_from_bytes(encrypted); out_blob=_DataBlob()
    if not crypt32.CryptUnprotectData(ctypes.byref(in_blob),None,None,None,None,0x01,ctypes.byref(out_blob)): return ""
    try: clear=ctypes.string_at(out_blob.pbData,out_blob.cbData)
    finally: kernel32.LocalFree(out_blob.pbData)
    try: return clear.decode('utf-8')
    except Exception: return ""


def recordings_dir() -> Path:
    path = Path.home() / "Music" / "LQP Grabaciones"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_ffmpeg() -> Optional[Path]:
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)

    cache = app_cache_dir()
    ffmpeg_dir = cache / "ffmpeg"
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
    ffprobe_exe = ffmpeg_dir / "ffprobe.exe"
    if ffmpeg_exe.exists():
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
        return ffmpeg_exe

    if os.name != "nt":
        print("[LQP HiFi] FFmpeg no está instalado. En este sistema no se descarga portable automáticamente.")
        return None

    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache / "ffmpeg-release-essentials.zip"
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    print("[LQP HiFi] FFmpeg no encontrado. Descargando FFmpeg portable para Windows...")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0) or 0)
            downloaded = 0
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 / total
                            print(f"\r[LQP HiFi] Descargando FFmpeg: {pct:5.1f}%", end="")
        print("\n[LQP HiFi] Extrayendo FFmpeg...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.namelist()
            ffmpeg_member = next((m for m in members if m.endswith("/bin/ffmpeg.exe")), None)
            ffprobe_member = next((m for m in members if m.endswith("/bin/ffprobe.exe")), None)
            if not ffmpeg_member:
                raise RuntimeError("El ZIP no contiene ffmpeg.exe")
            with zf.open(ffmpeg_member) as src, open(ffmpeg_exe, "wb") as dst:
                shutil.copyfileobj(src, dst)
            if ffprobe_member:
                with zf.open(ffprobe_member) as src, open(ffprobe_exe, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        try:
            zip_path.unlink(missing_ok=True)
        except Exception:
            pass
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
        return ffmpeg_exe
    except Exception as exc:
        print("[LQP HiFi] No se pudo descargar FFmpeg automáticamente:", exc)
        return None


FFMPEG_PATH = ensure_ffmpeg()


def safe_filename(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in text).strip()
    return cleaned[:80] or "item"


def format_time(seconds: float) -> str:
    if seconds is None or seconds < 0 or math.isnan(seconds):
        seconds = 0
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass
class TrackInfo:
    path: str
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: str = ""
    codec_hint: str = ""
    is_stream: bool = False

    @property
    def display_name(self) -> str:
        if self.artist and self.title:
            return f"{self.artist} — {self.title}"
        if self.title:
            return self.title
        if self.is_stream:
            return self.path
        return Path(self.path).stem


@dataclass
class RadioStation:
    name: str
    genre: str
    stream_url: str
    homepage: str = ""
    logo_url: str = ""
    logo_query: str = ""
    source: str = "preset"
    country: str = "Argentina"
    country_code: str = "AR"
    city: str = ""
    state: str = ""
    station_uuid: str = ""
    language: str = ""
    codec: str = ""
    bitrate: int = 0
    clickcount: int = 0
    lastcheckok: bool = True

    def display_name(self, include_location: bool = False) -> str:
        location = self.city or self.state or self.country
        suffix = f"  ·  {location}" if include_location and location else ""
        return f"{self.name}  ·  {self.genre}{suffix}"


def read_track_info(path: str) -> TrackInfo:
    info = TrackInfo(path=path, codec_hint=Path(path).suffix.upper().replace(".", ""))
    try:
        mf = MutagenFile(path, easy=True)
        if mf:
            info.title = (mf.get("title", [""])[0] or "").strip()
            info.artist = (mf.get("artist", [""])[0] or "").strip()
            info.album = (mf.get("album", [""])[0] or "").strip()
            info.genre = (mf.get("genre", [""])[0] or "").strip()
            if getattr(mf, "info", None):
                info.duration = float(getattr(mf.info, "length", 0) or 0)
                info.sample_rate = int(getattr(mf.info, "sample_rate", 44100) or 44100)
                info.channels = int(getattr(mf.info, "channels", 2) or 2)
                bps = getattr(mf.info, "bits_per_sample", 0) or 0
                info.bit_depth = f"{int(bps)} bit" if bps else ""
    except Exception:
        pass
    return info


def decode_file_to_float32(path: str, sample_rate_hint: int = 0) -> Tuple[np.ndarray, int, TrackInfo]:
    if not FFMPEG_PATH:
        raise RuntimeError("FFmpeg no está disponible. La app lo necesita para FLAC y formatos avanzados.")
    info = read_track_info(path)
    sr = int(info.sample_rate or sample_rate_hint or 44100)
    sr = max(8000, min(sr, 384000))
    cmd = [
        str(FFMPEG_PATH), "-v", "error", "-nostdin", "-i", path,
        "-vn", "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "2", "-ar", str(sr), "pipe:1"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **_no_window_kwargs())
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg no pudo decodificar el archivo:\n{err}")
    arr = np.frombuffer(proc.stdout, dtype=np.float32)
    if arr.size == 0:
        raise RuntimeError("El archivo no produjo audio decodificable.")
    arr = arr[: arr.size - (arr.size % 2)].reshape((-1, 2))
    info.sample_rate = sr
    info.channels = 2
    if not info.duration:
        info.duration = len(arr) / float(sr)
    return arr.copy(), sr, info


class BiquadEQ:
    def __init__(self, sample_rate: int, bands: List[float], gains_db: List[float], q: float = 1.10):
        self.sample_rate = max(8000, int(sample_rate))
        self.bands = bands
        self.q = q
        self.gains_db = list(gains_db)
        self.filters: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._build_filters()

    def _peaking(self, freq: float, gain_db: float) -> Tuple[np.ndarray, np.ndarray]:
        if abs(gain_db) < 0.05:
            return np.array([1.0, 0.0, 0.0], dtype=np.float64), np.array([1.0, 0.0, 0.0], dtype=np.float64)
        nyquist = self.sample_rate / 2.0
        freq = min(max(20.0, freq), nyquist * 0.92)
        a_amp = 10 ** (gain_db / 40.0)
        omega = 2.0 * math.pi * freq / self.sample_rate
        alpha = math.sin(omega) / (2.0 * self.q)
        cosw = math.cos(omega)
        b0 = 1.0 + alpha * a_amp
        b1 = -2.0 * cosw
        b2 = 1.0 - alpha * a_amp
        a0 = 1.0 + alpha / a_amp
        a1 = -2.0 * cosw
        a2 = 1.0 - alpha / a_amp
        b = np.array([b0 / a0, b1 / a0, b2 / a0], dtype=np.float64)
        a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float64)
        return b, a

    def _build_filters(self) -> None:
        self.filters.clear()
        for freq, gain in zip(self.bands, self.gains_db):
            b, a = self._peaking(freq, gain)
            zi = np.zeros((2, 2), dtype=np.float64)
            self.filters.append((b, a, zi))

    def rebuild_for_sample_rate(self, sample_rate: int) -> None:
        self.sample_rate = max(8000, int(sample_rate))
        self._build_filters()

    def set_gains(self, gains_db: List[float]) -> None:
        # Solo recalcula las bandas que cambiaron y conserva el estado (zi) del filtro:
        # evita clicks audibles al mover un slider mientras suena música.
        if len(gains_db) != len(self.bands) or len(self.filters) != len(self.bands):
            self.gains_db = list(gains_db)
            self._build_filters()
            return
        for i, (freq, new_gain) in enumerate(zip(self.bands, gains_db)):
            if abs(new_gain - self.gains_db[i]) < 1e-6:
                continue
            b, a = self._peaking(freq, new_gain)
            _b_old, _a_old, zi = self.filters[i]
            self.filters[i] = (b, a, zi)
        self.gains_db = list(gains_db)

    def process(self, block: np.ndarray) -> np.ndarray:
        if block.size == 0:
            return block
        out = block.astype(np.float64, copy=True)
        if out.ndim == 1:
            out = out.reshape((-1, 1))
        if out.shape[1] == 1:
            out = np.repeat(out, 2, axis=1)
        for idx, (b, a, zi) in enumerate(self.filters):
            if np.allclose(b, [1.0, 0.0, 0.0], atol=1e-8) and np.allclose(a, [1.0, 0.0, 0.0], atol=1e-8):
                continue
            left, z_left = signal.lfilter(b, a, out[:, 0], zi=zi[0])
            right, z_right = signal.lfilter(b, a, out[:, 1], zi=zi[1])
            out[:, 0] = left
            out[:, 1] = right
            self.filters[idx] = (b, a, np.vstack([z_left, z_right]))
        return out.astype(np.float32, copy=False)


class AudioEngine:
    def __init__(self):
        self.lock = threading.RLock()
        self.eq_lock = threading.RLock()
        self.audio: Optional[np.ndarray] = None
        self.sample_rate: int = 44100
        self.position: int = 0
        self.stream: Optional[sd.OutputStream] = None
        self.output_device: Optional[int] = None
        self.playing = False
        self.finished = False
        self.mode = "idle"  # idle/local/radio
        self.volume = 0.85
        self.preamp_db = 0.0
        self.power_enabled = False
        self.power_amount = 0.0  # 0..100
        self.bands = [31.0, 62.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
        self.eq_gains = [0.0 for _ in self.bands]
        self.eq = BiquadEQ(self.sample_rate, self.bands, self.eq_gains)
        # Medidores normalizados 0..1 en escala dB (-48 dBFS .. +3 dBFS).
        self.vu_left = 0.0
        self.vu_right = 0.0
        self.peak_left = 0.0
        self.peak_right = 0.0
        self.clip_warning = False
        # Último bloque mono post-mezcla para el analizador de espectro (lo lee la UI).
        self.monitor_mono: Optional[np.ndarray] = None
        self.loaded_info: Optional[TrackInfo] = None
        self.on_finished: Optional[Callable[[], None]] = None
        self.last_error: Optional[str] = None
        self.radio_url: str = ""
        self.radio_process: Optional[subprocess.Popen] = None
        self.radio_thread: Optional[threading.Thread] = None
        self.radio_queue: queue.Queue = queue.Queue(maxsize=64)
        self.radio_stop = threading.Event()
        self.radio_buffering = False
        # Sobrante del último chunk de radio. Antes se reencolaba al FINAL de la
        # cola y desordenaba el audio (glitches). Ahora se consume primero.
        self.radio_pending: Optional[np.ndarray] = None

    def set_output_device(self, device_index: Optional[int]) -> None:
        with self.lock:
            self.output_device = device_index
        if self.playing:
            self._reopen_stream()

    def set_volume(self, value: float) -> None:
        with self.lock:
            self.volume = clamp(float(value), 0.0, 1.8)

    def set_preamp(self, db: float) -> None:
        with self.lock:
            self.preamp_db = clamp(float(db), -18.0, 18.0)

    def set_power(self, enabled: bool, amount: float) -> None:
        with self.lock:
            self.power_enabled = bool(enabled)
            self.power_amount = clamp(float(amount), 0.0, 100.0)

    def set_eq_gains(self, gains: List[float]) -> None:
        with self.eq_lock:
            self.eq_gains = list(gains)
            self.eq.set_gains(self.eq_gains)

    def load_file(self, path: str) -> TrackInfo:
        self.stop(close_stream=False)
        audio, sr, info = decode_file_to_float32(path)
        with self.lock:
            self.audio = audio
            self.sample_rate = sr
            self.position = 0
            self.mode = "local"
            self.loaded_info = info
            self.finished = False
            self.last_error = None
        with self.eq_lock:
            self.eq.rebuild_for_sample_rate(sr)
            self.eq.set_gains(self.eq_gains)
        return info

    def load_radio(self, station: RadioStation) -> TrackInfo:
        self.stop(close_stream=True)
        info = TrackInfo(
            path=station.name,
            title=station.name,
            artist=f"Radio Online · {station.country or 'World'}",
            album=station.genre,
            duration=0.0,
            sample_rate=44100,
            channels=2,
            codec_hint="STREAM",
            is_stream=True,
        )
        with self.lock:
            self.mode = "radio"
            self.sample_rate = 44100
            self.position = 0
            self.loaded_info = info
            self.radio_url = station.stream_url
            self.finished = False
            self.last_error = None
            self.radio_buffering = True
        with self.eq_lock:
            self.eq.rebuild_for_sample_rate(44100)
            self.eq.set_gains(self.eq_gains)
        return info

    def _open_stream(self) -> None:
        if self.stream:
            return
        self.stream = sd.OutputStream(
            samplerate=int(self.sample_rate),
            channels=2,
            dtype="float32",
            blocksize=2048,
            callback=self._callback,
            device=self.output_device,
            latency="high",
        )
        self.stream.start()

    def _reopen_stream(self) -> None:
        was_playing = self.playing
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except Exception:
            pass
        self.stream = None
        if was_playing:
            self._open_stream()

    def _start_radio_reader(self) -> None:
        if not FFMPEG_PATH:
            raise RuntimeError("FFmpeg no está disponible para streaming.")
        self._stop_radio_process()
        while not self.radio_queue.empty():
            try:
                self.radio_queue.get_nowait()
            except Exception:
                break
        self.radio_pending = None
        self.radio_stop.clear()
        cmd = [
            str(FFMPEG_PATH),
            "-v", "error",
            "-nostdin",
            "-user_agent", f"LQP-HiFi-Rack-Player/{APP_VERSION}",
            "-rw_timeout", "15000000",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "5",
            "-i", self.radio_url,
            "-vn",
            "-f", "f32le",
            "-acodec", "pcm_f32le",
            "-ac", "2",
            "-ar", str(self.sample_rate),
            "pipe:1",
        ]
        kwargs: Dict[str, Any] = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        self.radio_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            **kwargs,
        )
        self.radio_thread = threading.Thread(target=self._radio_read_loop, daemon=True)
        self.radio_thread.start()

    def _radio_read_loop(self) -> None:
        block_frames = 4096
        block_bytes = block_frames * 2 * 4
        try:
            assert self.radio_process is not None and self.radio_process.stdout is not None
            while not self.radio_stop.is_set():
                data = self.radio_process.stdout.read(block_bytes)
                if not data:
                    break
                arr = np.frombuffer(data, dtype=np.float32)
                if arr.size < 2:
                    continue
                arr = arr[: arr.size - (arr.size % 2)].reshape((-1, 2)).copy()
                try:
                    self.radio_queue.put(arr, timeout=0.5)
                    with self.lock:
                        self.radio_buffering = False
                except queue.Full:
                    pass
        except Exception:
            self.last_error = traceback.format_exc()
        finally:
            with self.lock:
                self.radio_buffering = False

    def _stop_radio_process(self) -> None:
        self.radio_stop.set()
        proc = self.radio_process
        self.radio_process = None
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        while not self.radio_queue.empty():
            try:
                self.radio_queue.get_nowait()
            except Exception:
                break
        self.radio_pending = None

    def play(self) -> None:
        with self.lock:
            if self.mode == "idle":
                return
            self.playing = True
            self.finished = False
        if self.mode == "radio":
            self._start_radio_reader()
        self._open_stream()

    def pause(self) -> None:
        with self.lock:
            self.playing = False
        if self.mode == "radio":
            self._stop_radio_process()

    def stop(self, close_stream: bool = False, keep_position: bool = False) -> None:
        with self.lock:
            self.playing = False
            if not keep_position:
                self.position = 0
            self.finished = False
            self.vu_left = self.vu_right = self.peak_left = self.peak_right = 0.0
            self.clip_warning = False
        self._stop_radio_process()
        if close_stream:
            try:
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
            except Exception:
                pass
            self.stream = None

    def close(self) -> None:
        self.stop(close_stream=True)

    def toggle(self) -> None:
        if self.playing:
            self.pause()
        else:
            self.play()

    def seek_seconds(self, seconds: float) -> None:
        with self.lock:
            if self.mode != "local" or self.audio is None:
                return
            seconds = clamp(seconds, 0.0, self.get_duration_seconds())
            self.position = int(seconds * self.sample_rate)
            self.finished = False

    def get_position_seconds(self) -> float:
        with self.lock:
            return self.position / float(self.sample_rate or 44100)

    def get_duration_seconds(self) -> float:
        with self.lock:
            if self.mode == "local" and self.audio is not None:
                return len(self.audio) / float(self.sample_rate or 44100)
            return 0.0

    def _apply_power_stage(self, block: np.ndarray, enabled: bool, amount: float) -> np.ndarray:
        if not enabled or amount <= 0:
            return block
        # 0..100 => hasta +15 dB de ganancia previa. Control independiente del volumen principal.
        boost_db = 15.0 * (amount / 100.0)
        drive = 1.0 + 2.2 * (amount / 100.0)
        x = block * (10 ** (boost_db / 20.0))
        # Compresión simple por muestra para preservar presencia sin destruir tanto los transitorios.
        threshold = 0.55 - 0.12 * (amount / 100.0)
        ratio = 2.5 + 4.0 * (amount / 100.0)
        absx = np.abs(x)
        over = absx > threshold
        if np.any(over):
            compressed = threshold + (absx[over] - threshold) / ratio
            x[over] = np.sign(x[over]) * compressed
        # Limitador/soft clip final. Suena más amable que recortar duro.
        y = np.tanh(x * drive) / np.tanh(drive)
        return y.astype(np.float32, copy=False)

    def _callback(self, outdata, frames, time_info, status):
        try:
            with self.lock:
                playing = self.playing
                mode = self.mode
                vol = self.volume
                preamp_db = self.preamp_db
                power_enabled = self.power_enabled
                power_amount = self.power_amount

            if not playing:
                outdata[:] = 0
                self._decay_meters()
                return

            reached_end = False
            if mode == "local":
                with self.lock:
                    if self.audio is None:
                        outdata[:] = 0
                        return
                    start = self.position
                    end = min(start + frames, len(self.audio))
                    block = self.audio[start:end]
                    self.position = end
                    if end >= len(self.audio):
                        reached_end = True
                if len(block) < frames:
                    pad = np.zeros((frames - len(block), 2), dtype=np.float32)
                    block = np.vstack([block, pad]) if len(block) else pad
            elif mode == "radio":
                chunks = []
                needed = frames
                # Primero el sobrante de la lectura anterior, para mantener el orden.
                if self.radio_pending is not None:
                    pend = self.radio_pending
                    if len(pend) > needed:
                        chunks.append(pend[:needed])
                        self.radio_pending = pend[needed:]
                        needed = 0
                    else:
                        chunks.append(pend)
                        needed -= len(pend)
                        self.radio_pending = None
                while needed > 0:
                    try:
                        chunk = self.radio_queue.get_nowait()
                    except queue.Empty:
                        break
                    if len(chunk) > needed:
                        chunks.append(chunk[:needed])
                        self.radio_pending = chunk[needed:]
                        needed = 0
                    else:
                        chunks.append(chunk)
                        needed -= len(chunk)
                if chunks:
                    block = np.vstack(chunks)
                else:
                    block = np.zeros((0, 2), dtype=np.float32)
                if len(block) < frames:
                    pad = np.zeros((frames - len(block), 2), dtype=np.float32)
                    block = np.vstack([block, pad]) if len(block) else pad
                with self.lock:
                    self.position += frames
                    self.radio_buffering = len(chunks) == 0
            else:
                outdata[:] = 0
                return

            with self.eq_lock:
                block = self.eq.process(block)

            gain = (10 ** (preamp_db / 20.0)) * vol
            block = block * gain
            block = self._apply_power_stage(block, power_enabled, power_amount)
            peak_before_clip = float(np.max(np.abs(block))) if block.size else 0.0
            clipped = peak_before_clip > 0.98
            block = np.clip(block, -0.985, 0.985).astype(np.float32, copy=False)
            outdata[:] = block
            self._update_meters(block, clipped)

            if reached_end:
                with self.lock:
                    if not self.finished:
                        self.playing = False
                        self.finished = True
                        if self.on_finished:
                            threading.Thread(target=self.on_finished, daemon=True).start()
        except Exception:
            self.last_error = traceback.format_exc()
            outdata[:] = 0
            with self.lock:
                self.playing = False

    @staticmethod
    def _norm_db(amplitude: float) -> float:
        # Escala calibrada: -48 dBFS => 0.0 ; +3 dBFS => 1.0
        db = 20.0 * math.log10(amplitude + 1e-9)
        return clamp((db + 48.0) / 51.0, 0.0, 1.0)

    def _decay_meters(self) -> None:
        with self.lock:
            self.vu_left *= 0.86
            self.vu_right *= 0.86
            self.peak_left *= 0.94
            self.peak_right *= 0.94
            self.clip_warning = False
            self.monitor_mono = None

    def _update_meters(self, block: np.ndarray, clipped: bool) -> None:
        if block.size == 0:
            self._decay_meters()
            return
        left = block[:, 0]
        right = block[:, 1]
        rms_l = float(np.sqrt(np.mean(left * left))) if len(left) else 0.0
        rms_r = float(np.sqrt(np.mean(right * right))) if len(right) else 0.0
        peak_l = float(np.max(np.abs(left))) if len(left) else 0.0
        peak_r = float(np.max(np.abs(right))) if len(right) else 0.0
        # RMS -> lectura tipo VU (+3 dB de calibración respecto a seno pleno).
        nl = self._norm_db(rms_l * 1.41)
        nr = self._norm_db(rms_r * 1.41)
        pl = self._norm_db(peak_l)
        pr = self._norm_db(peak_r)
        mono = ((left + right) * 0.5).astype(np.float32)
        with self.lock:
            self.vu_left = nl if nl > self.vu_left else self.vu_left * 0.86
            self.vu_right = nr if nr > self.vu_right else self.vu_right * 0.86
            self.peak_left = pl if pl > self.peak_left else self.peak_left * 0.97
            self.peak_right = pr if pr > self.peak_right else self.peak_right * 0.97
            self.clip_warning = bool(clipped or peak_l > 0.97 or peak_r > 0.97)
            self.monitor_mono = mono


class StreamRecorder:
    """● REC "AIR CHECK": graba el stream de radio a MP3 con un FFmpeg aparte.

    Funciona independiente de la reproducción: podés seguir escuchando (o hasta
    pausar) y la grabación continúa, como cuando dejabas la cinta grabando.
    """

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.path: Optional[Path] = None
        self.station_name: str = ""
        self.started_at: float = 0.0

    @property
    def active(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def elapsed(self) -> float:
        if not self.active:
            return 0.0
        return time.time() - self.started_at

    def start(self, station: RadioStation) -> Path:
        if self.active:
            raise RuntimeError("Ya hay una grabación en curso.")
        if not FFMPEG_PATH:
            raise RuntimeError("FFmpeg no está disponible para grabar.")
        stamp = time.strftime("%Y%m%d_%H%M%S")
        out_path = recordings_dir() / f"{safe_filename(station.name)}_{stamp}.mp3"
        cmd = [
            str(FFMPEG_PATH),
            "-v", "error",
            "-nostdin",
            "-user_agent", f"LQP-HiFi-Rack-Player/{APP_VERSION}",
            "-rw_timeout", "15000000",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "5",
            "-i", station.stream_url,
            "-vn",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            "-y",
            str(out_path),
        ]
        kwargs: Dict[str, Any] = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **kwargs,
        )
        self.path = out_path
        self.station_name = station.name
        self.started_at = time.time()
        return out_path

    def stop(self) -> Optional[Path]:
        proc = self.process
        self.process = None
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        return self.path


class RadioBrowserClient:
    SERVERS=["https://all.api.radio-browser.info","https://de1.api.radio-browser.info","https://nl1.api.radio-browser.info","https://at1.api.radio-browser.info"]
    def __init__(self):
        self.session=requests.Session(); self.session.headers.update({"User-Agent":f"LQP-HiFi-Rack-Player/{APP_VERSION}","Accept":"application/json"}); self._lock=threading.RLock(); self._preferred_server=self.SERVERS[0]
    def _ordered_servers(self): return [self._preferred_server]+[x for x in self.SERVERS if x!=self._preferred_server]
    def _get(self,path:str,params:Dict[str,Any],timeout:int=12)->List[Dict[str,Any]]:
        for base in self._ordered_servers():
            try:
                with self._lock: response=self.session.get(base+path,params=params,timeout=timeout)
                response.raise_for_status(); data=response.json()
                if isinstance(data,list): self._preferred_server=base; return data
            except Exception: continue
        return []
    def search_station(self,query:str="",country_code:str="",state:str="",limit:int=25)->List[RadioStation]:
        params={"hidebroken":"true","limit":str(max(1,min(int(limit),100))),"order":"clickcount","reverse":"true"}
        if query: params["name"]=query
        if country_code: params["countrycode"]=country_code.upper()
        if state: params["state"]=state
        return [self._row_to_station(row,"radio-browser") for row in self._get("/json/stations/search",params) if row.get("url_resolved") or row.get("url")]
    def top_country(self,country_code:str,limit:int=50)->List[RadioStation]:
        params={"hidebroken":"true","limit":str(max(1,min(int(limit),100))),"order":"clickcount","reverse":"true"}
        return [self._row_to_station(row,"radio-browser") for row in self._get(f"/json/stations/bycountrycodeexact/{country_code.upper()}",params) if row.get("url_resolved") or row.get("url")]
    def top_argentina(self,limit:int=50): return self.top_country("AR",limit)
    @staticmethod
    def _station_key(station): return (station.station_uuid or station.stream_url,station.name.casefold())
    def featured_city(self,city:str,limit:int=25)->List[RadioStation]:
        preset=WORLD_CITY_PRESETS.get(city)
        if not preset: return []
        code=str(preset.get("country_code") or ""); state=str(preset.get("state") or ""); selected=[]; seen=set()
        for query in preset.get("queries",[]):
            candidates=self.search_station(str(query),code,state,8) or self.search_station(str(query),code,"",8)
            if not candidates: continue
            q=str(query).casefold(); candidates.sort(key=lambda x:(difflib.SequenceMatcher(None,q,x.name.casefold()).ratio(),x.clickcount,x.bitrate),reverse=True)
            for candidate in candidates:
                key=self._station_key(candidate)
                if key in seen: continue
                candidate.city=city; selected.append(candidate); seen.add(key); break
        fallback=self.search_station("",code,state,max(limit*2,30)) or self.top_country(code,max(limit*2,30))
        for candidate in fallback:
            key=self._station_key(candidate)
            if key in seen: continue
            candidate.city=city; selected.append(candidate); seen.add(key)
            if len(selected)>=limit: break
        return selected[:limit]
    def best_match(self,station:RadioStation,limit:int=20)->Optional[RadioStation]:
        candidates=self.search_station(station.logo_query or station.name,station.country_code,station.state,limit) or self.search_station(station.name,station.country_code,"",limit)
        if not candidates: return None
        target=station.name.casefold().strip(); candidates.sort(key=lambda x:(difflib.SequenceMatcher(None,target,x.name.casefold().strip()).ratio(),x.clickcount,x.bitrate),reverse=True)
        best=candidates[0]; similarity=difflib.SequenceMatcher(None,target,best.name.casefold().strip()).ratio()
        return best if similarity>=0.42 else None
    def _row_to_station(self,row,source):
        try: bitrate=int(row.get("bitrate") or 0)
        except Exception: bitrate=0
        try: clickcount=int(row.get("clickcount") or 0)
        except Exception: clickcount=0
        name=str(row.get("name") or "Radio sin nombre").strip(); tags=str(row.get("tags") or "").replace(","," / ")
        return RadioStation(name=name,genre=tags[:90] if tags else "Radio Online",stream_url=str(row.get("url_resolved") or row.get("url") or "").strip(),homepage=str(row.get("homepage") or "").strip(),logo_url=str(row.get("favicon") or "").strip(),logo_query=name,source=source,country=str(row.get("country") or "Radio World").strip(),country_code=str(row.get("countrycode") or "").upper(),state=str(row.get("state") or "").strip(),station_uuid=str(row.get("stationuuid") or "").strip(),language=str(row.get("language") or "").strip(),codec=str(row.get("codec") or "").strip(),bitrate=bitrate,clickcount=clickcount,lastcheckok=bool(row.get("lastcheckok",1)))


def create_fallback_logo(text: str, size: int = 128) -> Image.Image:
    img = Image.new("RGB", (size, size), "#080b08")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size - 1, size - 1], fill="#070907", outline="#374237", width=3)
    for y in range(10, size, 12):
        draw.line([0, y, size, y], fill="#111811")
    for r, col in [(56, "#0b2d17"), (44, "#104a22"), (34, "#1db954")]:
        draw.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], outline=col, width=2)
    initials = "".join(word[0] for word in text.upper().split() if word and word[0].isalnum())[:3] or "FM"
    try:
        font_big = ImageFont.truetype("arialbd.ttf", 34)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 4), initials, fill="#caffc2", font=font_big)
    label = "ONLINE"
    bbox = draw.textbbox((0, 0), label, font=font_small)
    draw.text(((size - (bbox[2] - bbox[0])) / 2, size - 25), label, fill="#ffb000", font=font_small)
    return img


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extrae el primer objeto JSON de una respuesta de LLM (tolera ```fences``` y texto alrededor)."""
    text = (text or "").strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                text = candidate
                break
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("La IA no devolvió un JSON reconocible.")
    return json.loads(text[start:end + 1])


def nvidia_eq_suggestion(genre: str, band: str, track: str, speakers: str, equipment: str, api_key: str) -> Dict[str, Any]:
    """Pide a NVIDIA Nemotron la EQ ideal para la música y el equipo del usuario.

    Devuelve {"gains": [10 floats], "name": str, "why": str}. Lanza excepción con
    mensaje claro si no hay internet, la API falla o la respuesta no sirve.
    """
    api_key=(api_key or os.environ.get(NVIDIA_API_KEY_ENV,"")).strip()
    if not api_key: raise RuntimeError("Falta tu API key de NVIDIA.")

    system_prompt = (
        "Sos un ingeniero de mastering argentino experto en ecualizadores gráficos de 10 bandas "
        "(31, 62, 125, 250, 500, 1000, 2000, 4000, 8000 y 16000 Hz). "
        "Tu tarea: proponer las ganancias en dB ideales para el material musical y el equipo del usuario. "
        "Rango permitido: -12.0 a +12.0, en pasos de 0.5. Sé criterioso: las correcciones sutiles "
        "(entre -4 y +4 en la mayoría de las bandas) suenan mejor que las curvas extremas. "
        "Tené en cuenta las limitaciones físicas de los parlantes (por ejemplo, monitores chicos "
        "no reproducen 31 Hz: ahí conviene cortar para ganar headroom). "
        "Respondé ÚNICAMENTE con un objeto JSON válido, sin ningún texto adicional, con esta forma exacta: "
        '{"gains": [g31, g62, g125, g250, g500, g1k, g2k, g4k, g8k, g16k], '
        '"name": "nombre corto y atractivo para el seteo (máx 30 caracteres, en español)", '
        '"why": "explicación breve en español de por qué elegiste esta curva (máx 60 palabras)"}'
    )
    user_lines = []
    if genre:
        user_lines.append(f"Género musical: {genre}")
    if band:
        user_lines.append(f"Banda / artista: {band}")
    if track:
        user_lines.append(f"Tema específico: {track}")
    if speakers:
        user_lines.append(f"Parlantes: {speakers}")
    if equipment:
        user_lines.append(f"Equipo en la cadena de sonido: {equipment}")
    user_prompt = "Calculá la ecualización perfecta para esto:\n" + "\n".join(user_lines)

    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 2048,
        "chat_template_kwargs": {"enable_thinking": True},
        "reasoning_budget": 1024,
        "stream": False,
    }
    try:
        r = requests.post(
            NVIDIA_API_BASE + "/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"No se pudo conectar con la IA de NVIDIA (¿hay internet?): {exc}") from exc
    if r.status_code == 401:
        raise RuntimeError("La API key de NVIDIA fue rechazada (401). Revisala o generá una nueva.")
    if r.status_code == 429:
        raise RuntimeError("La IA de NVIDIA está saturada (429). Esperá unos segundos y probá de nuevo.")
    if r.status_code >= 400:
        raise RuntimeError(f"La API de NVIDIA devolvió error {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        content = data["choices"][0]["message"]["content"] or ""
    except Exception as exc:
        raise RuntimeError("Respuesta inesperada de la API de NVIDIA.") from exc
    obj = _extract_json_object(content)
    gains_raw = obj.get("gains")
    if not isinstance(gains_raw, list) or len(gains_raw) != 10:
        raise RuntimeError("La IA no devolvió las 10 bandas esperadas. Probá de nuevo.")
    gains = [clamp(round(float(g) * 2) / 2.0, -12.0, 12.0) for g in gains_raw]
    name = str(obj.get("name") or "AI EQ").strip()[:30]
    why = str(obj.get("why") or "").strip()
    return {"gains": gains, "name": name, "why": why}


# ============================================================================
#  Widgets de rack: display fluorescente, cassette animado, espectro y VU LED.
#  Todos crean sus items de canvas UNA vez y después solo actualizan colores y
#  coordenadas (itemconfig/coords): mucho más fluido que borrar y redibujar.
# ============================================================================

class DeckDisplay(tk.Canvas):
    """Display fluorescente estilo deck: marquee de título, info, reloj y LEDs."""

    GREEN = "#5dff9b"
    GREEN_DIM = "#2f9e57"
    AMBER = "#ffb000"
    RED = "#ff3b26"
    BLUE = "#80d8ff"
    OFF = "#123120"

    def __init__(self, parent, **kw):
        kw.setdefault("bg", "#03140a")
        kw.setdefault("height", 104)
        kw.setdefault("highlightthickness", 0)
        kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self.title_text = "LQP HiFi RACK PLAYER"
        self.info_text = "Sin pista cargada"
        self.time_text = "00:00"
        self.mode_text = "STANDBY"
        self.rec_on = False
        self.rec_blink = False
        self.signal_on = False
        self.stereo_on = False
        self._offset = 0.0
        self._title_w = 0
        self._built = False
        self._ids: Dict[str, int] = {}
        self.bind("<Configure>", lambda e: self._rebuild())

    def _rebuild(self) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 80 or h < 40:
            return
        self.delete("all")
        # Vidrio del display con líneas de barrido.
        self.create_rectangle(0, 0, w, h, fill="#03140a", outline="#1d3a28", width=2)
        for y in range(5, h, 5):
            self.create_line(2, y, w - 2, y, fill="#052611")
        right_w = 190
        # Título con marquee. El panel derecho se dibuja DESPUÉS y tapa el sobrante.
        self._ids["title"] = self.create_text(
            14, 28, anchor="w", text=self.title_text, fill=self.GREEN,
            font=("Consolas", 17, "bold"))
        self._ids["info"] = self.create_text(
            14, 56, anchor="w", text=self.info_text, fill=self.GREEN_DIM,
            font=("Consolas", 10))
        # Máscara derecha + separador.
        self.create_rectangle(w - right_w, 2, w - 2, h - 2, fill="#03140a", outline="")
        self.create_line(w - right_w, 6, w - right_w, h - 6, fill="#1d3a28")
        self._ids["time"] = self.create_text(
            w - 14, 30, anchor="e", text=self.time_text, fill=self.AMBER,
            font=("Consolas", 24, "bold"))
        self._ids["mode"] = self.create_text(
            w - 14, 58, anchor="e", text=self.mode_text, fill=self.BLUE,
            font=("Consolas", 10, "bold"))
        # Fila de LEDs de estado.
        y_led = h - 18
        x = 16
        for key, label in [("rec", "REC"), ("signal", "SIGNAL"), ("stereo", "STEREO")]:
            self._ids[f"led_{key}"] = self.create_oval(x, y_led - 5, x + 10, y_led + 5, fill=self.OFF, outline="#1d3a28")
            self.create_text(x + 16, y_led, anchor="w", text=label, fill="#2f6e47", font=("Consolas", 8, "bold"))
            x += 78
        self._ids["hint"] = self.create_text(
            w - 14, y_led, anchor="e", text="", fill="#2f6e47", font=("Consolas", 8, "bold"))
        self._built = True
        self._measure_title()

    def _measure_title(self) -> None:
        if not self._built:
            return
        bbox = self.bbox(self._ids["title"])
        self._title_w = (bbox[2] - bbox[0]) if bbox else 0

    def set_texts(self, title: str, info: str, time_text: str, mode_text: str, hint: str = "") -> None:
        if not self._built:
            self.title_text, self.info_text, self.time_text, self.mode_text = title, info, time_text, mode_text
            return
        if title != self.title_text:
            self.title_text = title
            self._offset = 0.0
            self.itemconfig(self._ids["title"], text=title)
            self._measure_title()
        if info != self.info_text:
            self.info_text = info
            self.itemconfig(self._ids["info"], text=info)
        if time_text != self.time_text:
            self.time_text = time_text
            self.itemconfig(self._ids["time"], text=time_text)
        if mode_text != self.mode_text:
            self.mode_text = mode_text
            self.itemconfig(self._ids["mode"], text=mode_text)
        self.itemconfig(self._ids["hint"], text=hint)

    def set_leds(self, rec: bool, signal: bool, stereo: bool) -> None:
        if not self._built:
            return
        self.rec_on = rec
        self.signal_on = signal
        self.stereo_on = stereo

    def tick(self, blink: bool) -> None:
        if not self._built:
            return
        w = self.winfo_width()
        avail = w - 190 - 28
        if self._title_w > avail:
            self._offset += 1.6
            if self._offset > self._title_w + 60:
                self._offset = -avail * 0.25
            self.coords(self._ids["title"], 14 - self._offset, 28)
        else:
            self.coords(self._ids["title"], 14, 28)
        rec_fill = self.RED if (self.rec_on and blink) else ("#5a1410" if self.rec_on else self.OFF)
        self.itemconfig(self._ids["led_rec"], fill=rec_fill)
        self.itemconfig(self._ids["led_signal"], fill=self.AMBER if self.signal_on else self.OFF)
        stereo_fill = self.GREEN if (self.stereo_on and blink) else ("#0d5a2e" if self.stereo_on else self.OFF)
        self.itemconfig(self._ids["led_stereo"], fill=stereo_fill)


class CassetteCanvas(tk.Canvas):
    """Cassette animado: carretes que giran y cinta que pasa del carrete
    izquierdo al derecho siguiendo el progreso del tema."""

    W = 252
    H = 132

    def __init__(self, parent, **kw):
        kw.setdefault("bg", "#0b0e0b")
        super().__init__(parent, width=self.W, height=self.H, highlightthickness=0, bd=0, **kw)
        self.angle = 0.0
        self.progress = 0.0
        self.playing = False
        self._spoke_ids: List[List[int]] = []
        self._tape_ids: List[int] = []
        self._label_id = 0
        self._sub_id = 0
        self._draw_static()

    def _draw_static(self) -> None:
        w, h = self.W, self.H
        # Cuerpo del cassette.
        self.create_rectangle(4, 6, w - 4, h - 6, fill="#20241f", outline="#454d44", width=2)
        self.create_rectangle(8, 10, w - 8, h - 10, fill="#181c17", outline="#2c332b")
        # Etiqueta crema con franja de color, como los TDK/Maxell.
        self.create_rectangle(20, 16, w - 20, 58, fill="#e9e1c8", outline="#b9ad8a")
        self.create_rectangle(20, 16, w - 20, 26, fill="#b8352a", outline="#8f2117")
        self.create_text(w / 2, 21, text="LQP · POSITION CHROME · 90", fill="#f5ead2", font=("Consolas", 7, "bold"))
        self._label_id = self.create_text(w / 2, 38, text="—", fill="#33301f", font=("Consolas", 10, "bold"), width=w - 56)
        self._sub_id = self.create_text(w / 2, 51, text="", fill="#6b6349", font=("Consolas", 8), width=w - 56)
        # Ventana de los carretes.
        self.create_rectangle(58, 62, w - 58, 112, fill="#0a0c0a", outline="#454d44", width=2)
        cx_pairs = [86, w - 86]
        cy = 87
        for i, cx in enumerate(cx_pairs):
            tape = self.create_oval(cx - 18, cy - 18, cx + 18, cy + 18, fill="#241b0e", outline="#0d0a06")
            self._tape_ids.append(tape)
            self.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#d9dfd8", outline="#7c837b", width=2)
            spokes = []
            for k in range(3):
                spokes.append(self.create_line(cx, cy, cx, cy, fill="#3d443c", width=3))
            self._spoke_ids.append(spokes)
        # Tornillos y detalle inferior tipo trapecio con huecos.
        for x, y in [(14, 14), (w - 14, 14), (14, h - 14), (w - 14, h - 14)]:
            self.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#2b302a", outline="#565f55")
            self.create_line(x - 2, y, x + 2, y, fill="#0c0e0c")
        self.create_polygon(78, h - 10, 92, h - 24, w - 92, h - 24, w - 78, h - 10, fill="#141814", outline="#2c332b")
        for dx in (-34, -17, 0, 17, 34):
            self.create_oval(w / 2 + dx - 3, h - 21, w / 2 + dx + 3, h - 15, fill="#060806", outline="#2c332b")
        self._update_reels()

    def set_label(self, text: str, sub: str) -> None:
        self.itemconfig(self._label_id, text=(text or "—")[:34])
        self.itemconfig(self._sub_id, text=(sub or "")[:40])

    def update_state(self, progress: float, playing: bool) -> None:
        self.progress = clamp(progress, 0.0, 1.0)
        self.playing = playing
        if playing:
            self.angle -= 0.38
        self._update_reels()

    def _update_reels(self) -> None:
        w = self.W
        cy = 87
        cx_pairs = [86, w - 86]
        # El carrete izquierdo se vacía y el derecho se llena.
        radii = [10.0 + 9.0 * (1.0 - self.progress), 10.0 + 9.0 * self.progress]
        for i, cx in enumerate(cx_pairs):
            r_t = radii[i] + 8.0
            self.coords(self._tape_ids[i], cx - r_t, cy - r_t, cx + r_t, cy + r_t)
            for k, sid in enumerate(self._spoke_ids[i]):
                a = self.angle + k * (2.0 * math.pi / 3.0)
                x2 = cx + 7.5 * math.cos(a)
                y2 = cy + 7.5 * math.sin(a)
                self.coords(sid, cx, cy, x2, y2)


class SpectrumCanvas(tk.Canvas):
    """Analizador de espectro LED de 20 bandas con peak-hold, estilo rack 80s."""

    ROWS = 16
    FREQ_LABELS = ["31", "62", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]

    def __init__(self, parent, bands: int = 20, **kw):
        kw.setdefault("bg", "#040704")
        kw.setdefault("highlightthickness", 0)
        kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self.bands = bands
        self._built = False
        self._cells: List[List[int]] = []
        self._peaks: List[int] = []
        self._last_lit: List[int] = [-1] * bands
        self._last_peak_y: List[float] = [-1.0] * bands
        self._geom: Tuple[float, float, float, float] = (0, 0, 0, 0)
        self.bind("<Configure>", lambda e: self._rebuild())

    def _row_colors(self, row: int) -> Tuple[str, str]:
        frac = row / float(self.ROWS - 1)
        if frac < 0.62:
            return "#21ff64", "#07230f"
        if frac < 0.86:
            return "#ffb000", "#231803"
        return "#ff3b26", "#230a06"

    def _rebuild(self) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 120 or h < 80:
            return
        self.delete("all")
        self.create_rectangle(0, 0, w, h, fill="#040704", outline="#28332a", width=2)
        left, right, top, bottom = 10, 10, 8, 24
        area_w = w - left - right
        area_h = h - top - bottom
        bw = area_w / self.bands
        cell_gap = 2
        ch = (area_h - (self.ROWS - 1) * cell_gap) / self.ROWS
        self._geom = (left, top, bw, ch + cell_gap)
        self._cells = []
        self._peaks = []
        self._last_lit = [-1] * self.bands
        self._last_peak_y = [-1.0] * self.bands
        for b in range(self.bands):
            x0 = left + b * bw + 2
            x1 = left + (b + 1) * bw - 2
            col_cells = []
            for r in range(self.ROWS):
                y1 = top + area_h - r * (ch + cell_gap)
                y0 = y1 - ch
                _on, off = self._row_colors(r)
                col_cells.append(self.create_rectangle(x0, y0, x1, y1, fill=off, outline="#0c130d"))
            self._cells.append(col_cells)
            self._peaks.append(self.create_rectangle(x0, top + area_h, x1, top + area_h + 2, fill="#ffd27a", outline=""))
            if b % 2 == 0 and b // 2 < len(self.FREQ_LABELS):
                self.create_text((x0 + x1) / 2, h - 11, text=self.FREQ_LABELS[b // 2],
                                 fill="#4d6b52", font=("Consolas", 8, "bold"))
        self._built = True

    def update_levels(self, levels: List[float], peaks: List[float]) -> None:
        if not self._built:
            return
        left, top, _bw, step = self._geom
        area_bottom = None
        for b in range(min(self.bands, len(levels))):
            lit = int(clamp(levels[b], 0.0, 1.0) * self.ROWS + 0.5)
            if lit != self._last_lit[b]:
                cells = self._cells[b]
                for r in range(self.ROWS):
                    on, off = self._row_colors(r)
                    self.itemconfig(cells[r], fill=on if r < lit else off)
                self._last_lit[b] = lit
            # Marcador de pico que cae lento.
            peak_row = clamp(peaks[b], 0.0, 1.0) * self.ROWS
            if abs(peak_row - self._last_peak_y[b]) > 0.15:
                self._last_peak_y[b] = peak_row
                coords = self.coords(self._cells[b][0])
                if coords:
                    x0, _y0, x1, y_base = coords[0], coords[1], coords[2], coords[3]
                    y = y_base - peak_row * step
                    self.coords(self._peaks[b], x0, y - 2, x1, y)


class VUMeterCanvas(tk.Canvas):
    """Vúmetro estéreo LED calibrado en dB con peak-hold y LED de clip."""

    BLOCKS = 46
    DB_TICKS = [(-40, "-40"), (-30, "-30"), (-20, "-20"), (-10, "-10"), (-6, "-6"), (-3, "-3"), (0, "0"), (3, "+3")]

    def __init__(self, parent, **kw):
        kw.setdefault("bg", "#040704")
        kw.setdefault("height", 150)
        kw.setdefault("highlightthickness", 0)
        kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self._built = False
        self._bars: List[List[int]] = []
        self._peak_lines: List[int] = []
        self._clip_led = 0
        self._last_lit = [-1, -1]
        self._last_peak = [-1.0, -1.0]
        self._x0 = 0.0
        self._x1 = 0.0
        self.bind("<Configure>", lambda e: self._rebuild())

    @staticmethod
    def _block_colors(i: int, blocks: int) -> Tuple[str, str]:
        frac = i / float(blocks - 1)
        if frac < 0.64:
            return "#21ff64", "#07230f"
        if frac < 0.87:
            return "#ffb000", "#231803"
        return "#ff3b26", "#230a06"

    def _rebuild(self) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 160 or h < 90:
            return
        self.delete("all")
        self.create_rectangle(0, 0, w, h, fill="#040704", outline="#28332a", width=2)
        x0, x1 = 56.0, w - 78.0
        self._x0, self._x1 = x0, x1
        bar_h = 24
        rows_y = [16.0, 62.0]
        self._bars = []
        self._peak_lines = []
        self._last_lit = [-1, -1]
        self._last_peak = [-1.0, -1.0]
        gap = 2
        bw = (x1 - x0 - (self.BLOCKS - 1) * gap) / self.BLOCKS
        for ch_idx, (label, y) in enumerate(zip(("L", "R"), rows_y)):
            self.create_text(28, y + bar_h / 2, text=label, fill="#b9ffb1", font=("Consolas", 15, "bold"))
            blocks = []
            for i in range(self.BLOCKS):
                bx = x0 + i * (bw + gap)
                _on, off = self._block_colors(i, self.BLOCKS)
                blocks.append(self.create_rectangle(bx, y, bx + bw, y + bar_h, fill=off, outline="#0c130d"))
            self._bars.append(blocks)
            self._peak_lines.append(self.create_line(x0, y - 3, x0, y + bar_h + 3, fill="#ffffff", width=2))
        # Escala en dB (misma calibración que AudioEngine._norm_db).
        y_scale = rows_y[1] + bar_h + 16
        for db, label in self.DB_TICKS:
            norm = clamp((db + 48.0) / 51.0, 0.0, 1.0)
            tx = x0 + norm * (x1 - x0)
            self.create_line(tx, y_scale - 7, tx, y_scale - 3, fill="#4d6b52")
            self.create_text(tx, y_scale + 4, text=label, fill="#4d6b52", font=("Consolas", 8, "bold"))
        self.create_text(x1 + 12, y_scale + 4, anchor="w", text="dB", fill="#4d6b52", font=("Consolas", 8, "bold"))
        # LED de clip.
        self._clip_led = self.create_oval(w - 58, 26, w - 38, 46, fill="#230a06", outline="#3a1a14", width=2)
        self.create_text(w - 48, 58, text="CLIP", fill="#7a4038", font=("Consolas", 9, "bold"))
        self._built = True

    def update_levels(self, l: float, r: float, pl: float, pr: float, clip: bool) -> None:
        if not self._built:
            return
        for ch_idx, (value, peak) in enumerate(((l, pl), (r, pr))):
            lit = int(clamp(value, 0.0, 1.0) * self.BLOCKS + 0.5)
            if lit != self._last_lit[ch_idx]:
                blocks = self._bars[ch_idx]
                for i in range(self.BLOCKS):
                    on, off = self._block_colors(i, self.BLOCKS)
                    self.itemconfig(blocks[i], fill=on if i < lit else off)
                self._last_lit[ch_idx] = lit
            if abs(peak - self._last_peak[ch_idx]) > 0.004:
                self._last_peak[ch_idx] = peak
                px = self._x0 + clamp(peak, 0.0, 1.0) * (self._x1 - self._x0)
                y = 16.0 if ch_idx == 0 else 62.0
                self.coords(self._peak_lines[ch_idx], px, y - 3, px, y + 27)
        self.itemconfig(self._clip_led, fill="#ff3b26" if clip else "#230a06")


class VintageHiFiApp:
    BG = "#070907"
    PANEL = "#111611"
    PANEL2 = "#171d17"
    PANEL3 = "#0d120d"
    TEXT = "#b9ffb1"
    MUTED = "#789073"
    GREEN = "#21ff64"
    GREEN_DARK = "#0a4a24"
    AMBER = "#ffb000"
    RED = "#ff3b26"
    ORANGE = "#ff6a00"
    BLUE = "#80d8ff"
    METAL = "#242724"

    SPEC_BANDS = 20

    EQ_PRESETS: Dict[str, List[float]] = {
        "Flat": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "Hi‑Fi JBL": [1.2, 0.8, 0.4, -0.4, -0.5, 0.0, 0.5, 1.0, 1.4, 1.1],
        # Presets dedicados JBL 104 (monitores coaxiales 4.5"): el 31 Hz se corta
        # porque el driver no lo reproduce y solo roba headroom del puerto.
        "JBL 104 Reference": [-2.0, 1.0, 1.5, 0.5, -0.5, 0.0, 0.5, 1.0, 1.5, 1.0],
        "JBL 104 Bass Boost": [-1.5, 3.0, 3.5, 1.5, 0.0, -0.5, 0.0, 0.5, 1.0, 0.5],
        "JBL 104 Noche": [-3.0, -1.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.0, -1.0, -2.0],
        "JBL 104 Voz/Podcast": [-4.0, -2.0, -0.5, 1.0, 2.0, 2.5, 2.0, 1.0, 0.0, -1.0],
        "Rock 90s": [3, 2, 1, 0, -1, 0, 1.5, 2.5, 3, 2],
        "Rock Nacional FM": [2.2, 1.5, 0.8, 0.0, -0.8, 0.3, 1.4, 2.1, 2.5, 1.2],
        "Vocal / Radio": [-1.2, -1, -0.4, 0.6, 1.6, 2.4, 2.2, 1, 0, -0.8],
        "Bass Boost": [5, 4, 3, 1, 0, -0.5, -0.5, 0, 0.5, 0.5],
        "Tape Warm": [2.4, 1.8, 1.0, 0.3, -0.3, -0.8, -0.5, 0.5, 1.1, 0.6],
        "Night": [-3, -2, -1, 0, 1, 1, 0, -1, -2, -3],
        "Club": [4, 3, 1, 0, -1, 0, 2, 3, 3, 2],
        "FM Clean": [-1, -0.7, -0.3, 0, 0.5, 1.2, 1.0, 0.2, -0.3, -0.8],
    }

    SLEEP_OPTIONS = ["OFF", "15 min", "30 min", "45 min", "60 min", "90 min"]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.engine = AudioEngine()
        self.engine.on_finished = self._track_finished_from_engine
        self.browser = RadioBrowserClient()
        self.recorder = StreamRecorder()
        self.playlist: List[str] = []
        self.current_index: int = -1
        self.radios: List[RadioStation] = [RadioStation(**row) for row in RADIO_PRESETS]
        self.world_radios: List[RadioStation] = []
        self.current_radio_index: int = -1
        self.current_world_radio_index: int = -1
        self.current_radio_scope: str = "ar"
        self.current_station: Optional[RadioStation] = None
        self.logo_cache: Dict[str, ImageTk.PhotoImage] = {}
        self.loading = False
        self.ui_queue: queue.Queue = queue.Queue()
        self.seeking = False
        self.eq_sliders: List[tk.Scale] = []
        self._eq_programmatic = False
        self._playlist_drag_index: Optional[int] = None
        self._playlist_drag_path = ""
        self.device_map: Dict[str, Optional[int]] = {"Salida predeterminada": None}
        self.sleep_deadline: Optional[float] = None
        self._tick_after_id: Optional[str] = None

        # Analizador de espectro.
        self.spec_edges = np.geomspace(30.0, 17000.0, self.SPEC_BANDS + 1)
        self.spec_levels = [0.0] * self.SPEC_BANDS
        self.spec_peaks = [0.0] * self.SPEC_BANDS
        self._spec_win: Optional[np.ndarray] = None
        self._spec_win_n = 0

        cfg = self._load_config()

        self.status_var = tk.StringVar(value="Listo · Drag & drop · EQ manual/automático con IA · Radio AR / World")
        self.device_var = tk.StringVar(value=str(cfg.get("device", "Salida predeterminada")))
        self.volume_var = tk.DoubleVar(value=float(cfg.get("volume", 85)))
        self.preamp_var = tk.DoubleVar(value=float(cfg.get("preamp", 0)))
        self.power_enabled_var = tk.BooleanVar(value=bool(cfg.get("power_enabled", False)))
        self.power_var = tk.DoubleVar(value=float(cfg.get("power_amount", 0)))
        self.shuffle_var = tk.BooleanVar(value=bool(cfg.get("shuffle", False)))
        self.repeat_var = tk.BooleanVar(value=bool(cfg.get("repeat", False)))
        self.radio_search_var = tk.StringVar(value="")
        self.world_radio_search_var = tk.StringVar(value="")
        self.world_city_var = tk.StringVar(value=str(cfg.get("world_city", "Miami")))
        self.eq_mode_var = tk.StringVar(value="MANUAL · LIVE")
        self.sleep_var = tk.StringVar(value="OFF")
        self.sleep_label_var = tk.StringVar(value="--:--")
        self.preset_var = tk.StringVar(value=str(cfg.get("eq_preset", "Flat")))
        self._saved_eq: Optional[List[float]] = cfg.get("eq_gains") if isinstance(cfg.get("eq_gains"), list) else None
        # MEMORY EQ: seteos de ecualización con nombre guardados por el usuario.
        self.user_eq_presets: Dict[str, List[float]] = {}
        raw_user = cfg.get("user_eq_presets")
        if isinstance(raw_user, dict):
            for name, gains in raw_user.items():
                try:
                    if isinstance(gains, list) and len(gains) == 10:
                        self.user_eq_presets[str(name)[:40]] = [clamp(float(g), -12.0, 12.0) for g in gains]
                except Exception:
                    pass
        # AI EQ (NVIDIA): estado del diálogo y últimos datos de equipo usados.
        self.ai_dialog: Optional[tk.Toplevel] = None
        self.ai_busy = False
        self.ai_speakers_default = str(cfg.get("ai_speakers", "JBL 104"))
        self.ai_equipment_default = str(cfg.get("ai_equipment", ""))
        self.nvidia_key_protected = str(cfg.get(NVIDIA_KEY_CONFIG_FIELD, "") or "")
        self.nvidia_api_key = os.environ.get(NVIDIA_API_KEY_ENV, "").strip() or unprotect_secret_for_current_user(self.nvidia_key_protected)
        self.ai_auto_on_track_change = bool(cfg.get("ai_auto_on_track_change", False))
        self.last_radio_maintenance = float(cfg.get("last_radio_maintenance", 0) or 0)
        self._saved_geometry: str = str(cfg.get("geometry", ""))

        # Playlist guardada (solo archivos que siguen existiendo).
        for p in cfg.get("playlist", []) or []:
            try:
                if isinstance(p, str) and Path(p).exists():
                    self.playlist.append(p)
            except Exception:
                pass

        self._setup_window()
        self._build_ui()
        self._bind_keys()
        self._refresh_devices()
        self._apply_saved_state()
        self._refresh_playlist_box()
        self._refresh_radio_box()
        self._refresh_world_radio_box()
        self.root.after(400, self._prefetch_visible_logos)
        if not self.world_radios:
            self.root.after(1200, lambda: self.load_world_city(silent=True))
        if time.time() - self.last_radio_maintenance > 24 * 3600:
            self.root.after(3500, lambda: self.refresh_argentina_radios(silent=True))
        self._tick()

    # ------------------------------------------------------------------ config
    def _radio_from_config(self, row: Any) -> Optional[RadioStation]:
        if not isinstance(row, dict): return None
        allowed=set(RadioStation.__dataclass_fields__.keys())
        try: return RadioStation(**{k:v for k,v in row.items() if k in allowed})
        except Exception: return None

    def _load_config(self) -> Dict[str, Any]:
        path=app_config_path()
        if not path.exists(): return {}
        try: data=json.loads(path.read_text(encoding="utf-8"))
        except Exception: return {}
        if not isinstance(data,dict): return {}
        loaded=[self._radio_from_config(row) for row in data.get("radios",[]) or []]; loaded=[x for x in loaded if x]
        if loaded:
            by_name={x.name.casefold():x for x in loaded}; merged=[]; used=set()
            for station in self.radios:
                key=station.name.casefold(); merged.append(by_name.get(key,station)); used.add(key)
            for station in loaded:
                key=station.name.casefold()
                if key not in used: merged.append(station); used.add(key)
            self.radios=merged
        self.world_radios=[x for x in (self._radio_from_config(row) for row in data.get("world_radios",[]) or []) if x]
        return data

    def _save_config(self) -> bool:
        try:
            gains=[float(getattr(scale,"var").get()) for scale in self.eq_sliders] if self.eq_sliders else (self._saved_eq or [])
            data={"radios":[asdict(x) for x in self.radios],"world_radios":[asdict(x) for x in self.world_radios],"world_city":self.world_city_var.get() if hasattr(self,"world_city_var") else "Miami","playlist":list(self.playlist),"volume":float(self.volume_var.get()),"preamp":float(self.preamp_var.get()),"power_enabled":bool(self.power_enabled_var.get()),"power_amount":float(self.power_var.get()),"shuffle":bool(self.shuffle_var.get()),"repeat":bool(self.repeat_var.get()),"eq_gains":gains,"eq_preset":self.preset_var.get(),"user_eq_presets":self.user_eq_presets,"ai_speakers":self.ai_speakers_default,"ai_equipment":self.ai_equipment_default,"ai_auto_on_track_change":self.ai_auto_on_track_change,NVIDIA_KEY_CONFIG_FIELD:self.nvidia_key_protected,"device":self.device_var.get(),"geometry":self.root.geometry(),"last_radio_maintenance":self.last_radio_maintenance}
            write_json_atomic(app_config_path(),data); return True
        except Exception: return False

    def _apply_saved_state(self) -> None:
        self.engine.set_volume(float(self.volume_var.get()) / 100.0)
        self.engine.set_preamp(float(self.preamp_var.get()))
        self.engine.set_power(bool(self.power_enabled_var.get()), float(self.power_var.get()))
        if self._saved_eq and len(self._saved_eq) == len(self.eq_sliders):
            self._eq_programmatic=True
            try:
                for scale,gain in zip(self.eq_sliders,self._saved_eq): getattr(scale,"var").set(float(gain))
            finally: self._eq_programmatic=False
            self._eq_changed(manual=False); self.preset_var.set("Manual"); self.eq_mode_var.set("MANUAL · RESTAURADO")
        self._power_changed()
        if self.device_var.get() in self.device_map:
            self.engine.set_output_device(self.device_map[self.device_var.get()])

    # ------------------------------------------------------------------ window
    def _setup_window(self) -> None:
        self.root.title(f"{APP_NAME} · {APP_VERSION}")
        geometry = self._saved_geometry or "1500x930"
        try:
            self.root.geometry(geometry)
        except Exception:
            self.root.geometry("1500x930")
        self.root.minsize(1320, 800)
        self.root.configure(bg=self.BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Vintage.TCombobox", fieldbackground=self.PANEL3, background=self.PANEL2, foreground=self.TEXT)
        style.configure("Vintage.TNotebook", background=self.PANEL, borderwidth=0)
        style.configure("Vintage.TNotebook.Tab", background=self.PANEL2, foreground=self.TEXT, padding=(12, 6), font=("Consolas", 10, "bold"))
        style.map("Vintage.TNotebook.Tab", background=[("selected", "#223022")], foreground=[("selected", self.GREEN)])

    # -------------------------------------------------------------- ui helpers
    def _rack_frame(self, parent, **kw) -> tk.Frame:
        return tk.Frame(parent, bg=self.PANEL, bd=2, relief="ridge", highlightbackground="#303830", highlightthickness=1, **kw)

    def _retro_button(self, parent, text, command=None, width=None, fg=None, bg=None) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=bg or "#182018",
            fg=fg or self.TEXT,
            activebackground="#243024",
            activeforeground=self.GREEN,
            bd=2,
            relief="raised",
            font=("Consolas", 10, "bold"),
            cursor="hand2",
            highlightthickness=0,
            padx=8,
            pady=4,
        )

    def _label(self, parent, text="", textvariable=None, size=10, bold=False, fg=None, anchor="w") -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            textvariable=textvariable,
            bg=parent.cget("bg"),
            fg=fg or self.TEXT,
            font=("Consolas", size, "bold" if bold else "normal"),
            anchor=anchor,
        )

    def _scale(self, parent, variable, from_, to, orient="horizontal", command=None, length=None, resolution=1) -> tk.Scale:
        return tk.Scale(
            parent,
            variable=variable,
            from_=from_,
            to=to,
            orient=orient,
            command=command,
            length=length,
            resolution=resolution,
            bg=parent.cget("bg"),
            fg=self.TEXT,
            troughcolor="#050805",
            activebackground=self.GREEN,
            highlightthickness=0,
            bd=0,
            font=("Consolas", 8, "bold"),
        )

    # ---------------------------------------------------------------- build ui
    def _build_ui(self) -> None:
        header = tk.Canvas(self.root, height=92, bg="#090c09", highlightthickness=0)
        header.pack(fill="x", padx=10, pady=(10, 6))
        self._draw_header(header)

        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=10, pady=4)

        left = self._rack_frame(main, width=404)
        left.pack(side="left", fill="both", padx=(0, 8), pady=0)
        left.pack_propagate(False)
        self._build_source_panel(left)

        right = self._rack_frame(main, width=430)
        right.pack(side="right", fill="both", padx=(8, 0), pady=0)
        right.pack_propagate(False)
        self._build_eq_panel(right)

        center = tk.Frame(main, bg=self.BG)
        center.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        self._build_deck_panel(center)
        self._build_power_panel(center)
        self._build_analyzer_panel(center)

        status = self._rack_frame(self.root, height=38)
        status.pack(fill="x", padx=10, pady=(6, 10))
        status.pack_propagate(False)
        self._label(status, textvariable=self.status_var, size=9, fg=self.MUTED).pack(fill="both", expand=True, padx=10)

    def _draw_header(self, canvas: tk.Canvas) -> None:
        def redraw(_event=None):
            canvas.delete("all")
            w = canvas.winfo_width() or 1280
            h = 92
            canvas.create_rectangle(0, 0, w, h, fill="#080a08", outline="#363b36", width=2)
            for y in range(8, h, 8):
                canvas.create_line(0, y, w, y, fill="#101510")
            # --- Logo LQP: placa metálica retro con franjas 70s (estilo JBL/Marantz) ---
            # Placa con doble bisel metálico.
            canvas.create_rectangle(16, 8, 178, 84, fill="#3a423a", outline="#5c665c", width=1)
            canvas.create_rectangle(18, 10, 176, 82, fill="#10140f", outline="#060806", width=1)
            canvas.create_rectangle(21, 13, 173, 79, fill="#151a14", outline="#2c332b", width=1)
            # Franjas de velocidad 70s que atraviesan la placa por detrás del texto.
            for i, col in enumerate(("#ff3b26", "#ff6a00", "#ffb000")):
                y0 = 56 + i * 6
                canvas.create_rectangle(25, y0, 169, y0 + 4, fill=col, outline="")
            # Cola de las franjas en degradé hacia la izquierda (efecto movimiento).
            for i, col in enumerate(("#6e1a10", "#6e2e00", "#6e4c00")):
                y0 = 56 + i * 6
                canvas.create_rectangle(25, y0, 58, y0 + 4, fill=col, outline="")
            # LQP con sombra profunda y golpe de luz (efecto cromo fosforescente).
            canvas.create_text(100, 36, text="LQP", fill="#020803", font=("Impact", 34))
            canvas.create_text(98, 34, text="LQP", fill="#0a5a28", font=("Impact", 34))
            canvas.create_text(95, 31, text="LQP", fill="#b9ffb1", font=("Impact", 34))
            canvas.create_text(96, 32, text="LQP", fill="#21ff64", font=("Impact", 34))
            # Firma de época sobre las franjas.
            canvas.create_rectangle(60, 68, 134, 78, fill="#10140f", outline="")
            canvas.create_text(97, 73, text="AUDIO LABS · 1989", fill="#e8d8a0", font=("Consolas", 7, "bold"))
            # Remaches de la placa.
            for rx, ry in [(26, 18), (168, 18), (26, 74), (168, 74)]:
                canvas.create_oval(rx - 2, ry - 2, rx + 2, ry + 2, fill="#4e584e", outline="#151a14")
            canvas.create_text(192, 26, anchor="w", text="HiFi RACK PLAYER", fill="#d8ffd0", font=("Consolas", 19, "bold"))
            canvas.create_text(194, 56, anchor="w",
                               text="FLAC · RADIO AR/WORLD · MANUAL + AI AUTO · DRAG & DROP · REC",
                               fill=self.MUTED, font=("Consolas", 10))
            canvas.create_text(w - 20, 24, anchor="e", text="WORLD EDITION 4.0", fill=self.AMBER, font=("Consolas", 13, "bold"))
            canvas.create_text(w - 20, 54, anchor="e", text="1989 REFERENCE STREAM DECK · JBL MONITOR MODE", fill=self.GREEN, font=("Consolas", 10, "bold"))
            for x, y in [(12, 12), (w - 12, 12), (12, h - 12), (w - 12, h - 12)]:
                canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#252a25", outline="#4e584e")
                canvas.create_line(x - 3, y, x + 3, y, fill="#0a0c0a")
                canvas.create_line(x, y - 3, x, y + 3, fill="#0a0c0a")
            canvas.create_oval(w - 253, 66, w - 241, 78, fill=self.GREEN, outline="#aaffaa", width=1)
            canvas.create_text(w - 233, 72, anchor="w", text="POWER", fill=self.MUTED, font=("Consolas", 8, "bold"))
            # Jacks decorativos tipo PHONES.
            for i, jx in enumerate((w - 150, w - 110)):
                canvas.create_oval(jx - 8, 64, jx + 8, 80, fill="#0c0f0c", outline="#4e584e", width=2)
                canvas.create_oval(jx - 3, 69, jx + 3, 75, fill="#040604", outline="#2a302a")
            canvas.create_text(w - 130, 88, text="", fill=self.MUTED)
        canvas.bind("<Configure>", redraw)
        self.root.after(10, redraw)

    # ------------------------------------------------------------- source bay
    def _build_source_panel(self, parent: tk.Frame) -> None:
        top=tk.Frame(parent,bg=parent.cget("bg")); top.pack(fill="x",padx=10,pady=(10,6))
        self._label(top,"SOURCE BAY",size=13,bold=True,fg=self.AMBER).pack(side="left")
        self._label(top,"LOCAL / AR / WORLD",size=8,fg=self.MUTED).pack(side="right")
        self.source_notebook=ttk.Notebook(parent,style="Vintage.TNotebook"); self.source_notebook.pack(fill="both",expand=True,padx=10,pady=(0,10))
        tabs=[tk.Frame(self.source_notebook,bg=self.PANEL) for _ in range(3)]
        for tab,text in zip(tabs,(" PLAYLIST "," RADIO FM "," RADIO WORLD ")): self.source_notebook.add(tab,text=text)
        self._build_playlist_tab(tabs[0]); self._build_radio_tab(tabs[1]); self._build_world_radio_tab(tabs[2])

    def _build_playlist_tab(self,parent):
        hint="Arrastrá audio o carpetas desde Windows · arrastrá una pista para reordenarla"
        self._label(parent,hint,size=7,fg=self.BLUE).pack(fill="x",padx=8,pady=(7,0))
        frame=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken"); frame.pack(fill="both",expand=True,padx=8,pady=8)
        self.playlist_box=tk.Listbox(frame,bg="#050805",fg="#d7ffd1",selectbackground="#1c4f28",selectforeground="#fff",activestyle="none",font=("Consolas",10),bd=0,highlightthickness=0,exportselection=False,selectmode=tk.EXTENDED)
        scroll=tk.Scrollbar(frame,orient="vertical",command=self.playlist_box.yview,bg=self.PANEL); self.playlist_box.configure(yscrollcommand=scroll.set)
        self.playlist_box.pack(side="left",fill="both",expand=True,padx=(6,0),pady=6); scroll.pack(side="right",fill="y",pady=6,padx=(0,6))
        self.playlist_box.bind("<Double-Button-1>",lambda _e:self.play_selected()); self.playlist_box.bind("<ButtonPress-1>",self._playlist_drag_start,add="+"); self.playlist_box.bind("<B1-Motion>",self._playlist_drag_motion,add="+"); self.playlist_box.bind("<ButtonRelease-1>",self._playlist_drag_end,add="+")
        if DND_FILES is not None and hasattr(self.playlist_box,"drop_target_register"):
            try: self.playlist_box.drop_target_register(DND_FILES); self.playlist_box.dnd_bind("<<Drop>>",self._playlist_external_drop)
            except Exception: pass
        grid=tk.Frame(parent,bg=parent.cget("bg")); grid.pack(fill="x",padx=8,pady=(0,8))
        buttons=[("+ Archivos",self.add_files),("+ Carpeta",self.add_folder),("↑ Subir",lambda:self.move_selected_track(-1)),("↓ Bajar",lambda:self.move_selected_track(1)),("Quitar",self.remove_selected),("Limpiar",self.clear_playlist),("Importar",self.import_playlist),("Exportar",self.export_playlist)]
        for i,(text,cmd) in enumerate(buttons): self._retro_button(grid,text,cmd).grid(row=i//2,column=i%2,sticky="ew",padx=4,pady=3)
        grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=1)
        opts=tk.Frame(parent,bg=parent.cget("bg")); opts.pack(fill="x",padx=10,pady=(0,8))
        for side,text,var in (("left","Shuffle",self.shuffle_var),("right","Repeat",self.repeat_var)):
            tk.Checkbutton(opts,text=text,variable=var,bg=parent.cget("bg"),fg=self.TEXT,selectcolor="#162016",activebackground=parent.cget("bg"),activeforeground=self.GREEN,font=("Consolas",10,"bold"),command=self._save_config).pack(side=side)

    def _build_radio_tab(self,parent):
        logo_frame=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken"); logo_frame.pack(fill="x",padx=8,pady=8)
        self.logo_label=tk.Label(logo_frame,bg="#050805",width=128,height=128); self.logo_label.pack(side="left",padx=8,pady=8)
        info=tk.Frame(logo_frame,bg=logo_frame.cget("bg")); info.pack(side="left",fill="both",expand=True,padx=8,pady=8)
        self.radio_title_var=tk.StringVar(value="Radio online argentina"); self.radio_genre_var=tk.StringVar(value="Seleccioná una emisora")
        self._label(info,textvariable=self.radio_title_var,size=12,bold=True,fg=self.GREEN).pack(fill="x"); self._label(info,textvariable=self.radio_genre_var,size=8,fg=self.MUTED).pack(fill="x",pady=(4,0))
        self._retro_button(info,"▶ Play Radio",lambda:self.play_selected_radio("ar"),fg="#d7ffd1").pack(fill="x",pady=(8,2))
        actions=tk.Frame(info,bg=info.cget("bg")); actions.pack(fill="x")
        self._retro_button(actions,"✓ Probar",lambda:self.test_selected_radio("ar"),fg=self.AMBER).pack(side="left",fill="x",expand=True,padx=(0,2)); self._retro_button(actions,"↻ Reparar",lambda:self.repair_selected_radio("ar"),fg=self.BLUE).pack(side="left",fill="x",expand=True,padx=(2,0))
        search=tk.Frame(parent,bg=parent.cget("bg")); search.pack(fill="x",padx=8,pady=(0,6)); entry=tk.Entry(search,textvariable=self.radio_search_var,bg="#050805",fg=self.TEXT,insertbackground=self.GREEN,font=("Consolas",10),relief="sunken",bd=2); entry.pack(side="left",fill="x",expand=True,padx=(0,4)); entry.bind("<Return>",lambda _e:self.search_radios_online()); self._retro_button(search,"Buscar",self.search_radios_online,width=8).pack(side="left")
        frame=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken"); frame.pack(fill="both",expand=True,padx=8,pady=(0,8)); self.radio_box=tk.Listbox(frame,bg="#050805",fg="#d7ffd1",selectbackground="#583f00",selectforeground="#fff",activestyle="none",font=("Consolas",9),bd=0,highlightthickness=0,exportselection=False); scroll=tk.Scrollbar(frame,orient="vertical",command=self.radio_box.yview,bg=self.PANEL); self.radio_box.configure(yscrollcommand=scroll.set); self.radio_box.pack(side="left",fill="both",expand=True,padx=(6,0),pady=6); scroll.pack(side="right",fill="y",pady=6,padx=(0,6)); self.radio_box.bind("<<ListboxSelect>>",lambda _e:self._radio_selection_changed("ar")); self.radio_box.bind("<Double-Button-1>",lambda _e:self.play_selected_radio("ar"))
        grid=tk.Frame(parent,bg=parent.cget("bg")); grid.pack(fill="x",padx=8,pady=(0,8)); buttons=[("Top AR",self.load_top_argentina),("Actualizar",self.refresh_argentina_radios),("+ Manual",lambda:self.add_manual_radio("ar")),("Quitar",lambda:self.remove_selected_radio("ar")),("Importar",lambda:self.import_radios("ar")),("Exportar",lambda:self.export_radios("ar"))]
        for i,(text,cmd) in enumerate(buttons): self._retro_button(grid,text,cmd).grid(row=i//2,column=i%2,sticky="ew",padx=4,pady=3)
        grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)

    def _build_world_radio_tab(self,parent):
        city=tk.Frame(parent,bg=parent.cget("bg")); city.pack(fill="x",padx=8,pady=(8,6)); self.world_city_combo=ttk.Combobox(city,textvariable=self.world_city_var,state="readonly",values=list(WORLD_CITY_PRESETS.keys()),style="Vintage.TCombobox",font=("Consolas",9)); self.world_city_combo.pack(side="left",fill="x",expand=True,padx=(0,4)); self.world_city_combo.bind("<<ComboboxSelected>>",lambda _e:self.load_world_city()); self._retro_button(city,"Cargar ciudad",self.load_world_city,width=12).pack(side="left")
        logo_frame=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken"); logo_frame.pack(fill="x",padx=8,pady=(0,8)); self.world_logo_label=tk.Label(logo_frame,bg="#050805",width=96,height=96); self.world_logo_label.pack(side="left",padx=8,pady=8); info=tk.Frame(logo_frame,bg=logo_frame.cget("bg")); info.pack(side="left",fill="both",expand=True,padx=8,pady=8)
        self.world_radio_title_var=tk.StringVar(value="Radio World"); self.world_radio_genre_var=tk.StringVar(value="Elegí una ciudad"); self._label(info,textvariable=self.world_radio_title_var,size=11,bold=True,fg=self.GREEN).pack(fill="x"); self._label(info,textvariable=self.world_radio_genre_var,size=8,fg=self.MUTED).pack(fill="x",pady=(3,0)); self._retro_button(info,"▶ Play World",lambda:self.play_selected_radio("world"),fg="#d7ffd1").pack(fill="x",pady=(7,2)); ar=tk.Frame(info,bg=info.cget("bg")); ar.pack(fill="x"); self._retro_button(ar,"✓ Probar",lambda:self.test_selected_radio("world"),fg=self.AMBER).pack(side="left",fill="x",expand=True,padx=(0,2)); self._retro_button(ar,"↻ Reparar",lambda:self.repair_selected_radio("world"),fg=self.BLUE).pack(side="left",fill="x",expand=True,padx=(2,0))
        search=tk.Frame(parent,bg=parent.cget("bg")); search.pack(fill="x",padx=8,pady=(0,6)); entry=tk.Entry(search,textvariable=self.world_radio_search_var,bg="#050805",fg=self.TEXT,insertbackground=self.GREEN,font=("Consolas",9),relief="sunken",bd=2); entry.pack(side="left",fill="x",expand=True,padx=(0,4)); entry.bind("<Return>",lambda _e:self.search_world_radios()); self._retro_button(search,"Buscar",self.search_world_radios,width=8).pack(side="left")
        frame=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken"); frame.pack(fill="both",expand=True,padx=8,pady=(0,8)); self.world_radio_box=tk.Listbox(frame,bg="#050805",fg="#d7ffd1",selectbackground="#24445d",selectforeground="#fff",activestyle="none",font=("Consolas",8),bd=0,highlightthickness=0,exportselection=False); scroll=tk.Scrollbar(frame,orient="vertical",command=self.world_radio_box.yview,bg=self.PANEL); self.world_radio_box.configure(yscrollcommand=scroll.set); self.world_radio_box.pack(side="left",fill="both",expand=True,padx=(6,0),pady=6); scroll.pack(side="right",fill="y",pady=6,padx=(0,6)); self.world_radio_box.bind("<<ListboxSelect>>",lambda _e:self._radio_selection_changed("world")); self.world_radio_box.bind("<Double-Button-1>",lambda _e:self.play_selected_radio("world"))
        grid=tk.Frame(parent,bg=parent.cget("bg")); grid.pack(fill="x",padx=8,pady=(0,8)); buttons=[("Logos",lambda:self.refresh_logos("world")),("+ Manual",lambda:self.add_manual_radio("world")),("Quitar",lambda:self.remove_selected_radio("world")),("Importar",lambda:self.import_radios("world")),("Exportar",lambda:self.export_radios("world")),("Abrir web",lambda:self.open_selected_radio_homepage("world"))]
        for i,(text,cmd) in enumerate(buttons): self._retro_button(grid,text,cmd).grid(row=i//2,column=i%2,sticky="ew",padx=4,pady=3)
        grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)

    # ------------------------------------------------------------------- deck
    def _build_deck_panel(self, parent: tk.Frame) -> None:
        deck = self._rack_frame(parent)
        deck.pack(fill="x", pady=(0, 8))

        display_row = tk.Frame(deck, bg=deck.cget("bg"))
        display_row.pack(fill="x", padx=12, pady=(12, 6))
        self.cassette = CassetteCanvas(display_row)
        self.cassette.pack(side="left", padx=(0, 10))
        self.deck_display = DeckDisplay(display_row, height=132)
        self.deck_display.pack(side="left", fill="both", expand=True)

        controls = tk.Frame(deck, bg=deck.cget("bg"))
        controls.pack(fill="x", padx=12, pady=(2, 6))
        for text, cmd, color in [
            ("⏮", self.prev_track, self.TEXT), ("▶", self.toggle_play_pause, self.GREEN),
            ("⏸", self.pause, self.AMBER), ("■", self.stop, self.RED), ("⏭", self.next_track, self.TEXT),
        ]:
            self._retro_button(controls, text, cmd, width=6, fg=color).pack(side="left", padx=4)
        self.rec_button = self._retro_button(controls, "● REC", self.toggle_recording, width=8, fg=self.RED)
        self.rec_button.pack(side="left", padx=(16, 4))
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        self._label(controls, textvariable=self.time_var, size=12, bold=True, fg=self.AMBER, anchor="e").pack(side="right", padx=6)

        seek_frame = tk.Frame(deck, bg=deck.cget("bg"))
        seek_frame.pack(fill="x", padx=16, pady=(0, 8))
        self.seek_var = tk.DoubleVar(value=0)
        self.seek = self._scale(seek_frame, self.seek_var, 0, 1000, length=560)
        self.seek.pack(fill="x")
        # El flag de seeking se activa solo con interacción REAL del usuario.
        # (En la 2.0 el command del Scale se disparaba también al actualizar
        #  programáticamente la barra y quedaba congelada.)
        self.seek.bind("<ButtonPress-1>", lambda e: self._seek_press())
        self.seek.bind("<B1-Motion>", lambda e: self._seek_press())
        self.seek.bind("<ButtonRelease-1>", self._seek_release)

        controls2 = tk.Frame(deck, bg=deck.cget("bg"))
        controls2.pack(fill="x", padx=12, pady=(0, 12))

        vol_box = tk.Frame(controls2, bg=deck.cget("bg"))
        vol_box.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self._label(vol_box, "MAIN VOLUME", size=9, bold=True, fg=self.MUTED).pack(anchor="w")
        self._scale(vol_box, self.volume_var, 0, 120, command=lambda v: self.engine.set_volume(float(v) / 100.0), length=240).pack(fill="x")

        pre_box = tk.Frame(controls2, bg=deck.cget("bg"))
        pre_box.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self._label(pre_box, "PREAMP dB", size=9, bold=True, fg=self.MUTED).pack(anchor="w")
        self._scale(pre_box, self.preamp_var, -18, 18, command=lambda v: self.engine.set_preamp(float(v)), length=210).pack(fill="x")

        out_box = tk.Frame(controls2, bg=deck.cget("bg"))
        out_box.pack(side="right", fill="x", expand=True)
        self._label(out_box, "AUDIO OUT", size=9, bold=True, fg=self.MUTED).pack(anchor="w")
        self.device_combo = ttk.Combobox(out_box, textvariable=self.device_var, state="readonly", style="Vintage.TCombobox", font=("Consolas", 9))
        self.device_combo.pack(fill="x", pady=(5, 0))
        self.device_combo.bind("<<ComboboxSelected>>", self._device_changed)

    def _build_power_panel(self, parent: tk.Frame) -> None:
        power = self._rack_frame(parent)
        power.pack(fill="x", pady=(0, 8))
        ptitle = tk.Frame(power, bg=power.cget("bg"))
        ptitle.pack(fill="x", padx=12, pady=(8, 0))
        self._label(ptitle, "POWER STAGE DSP", size=12, bold=True, fg=self.ORANGE).pack(side="left")
        self.power_state_label = self._label(ptitle, "OFF", size=11, bold=True, fg=self.MUTED, anchor="e")
        self.power_state_label.pack(side="right")
        prow = tk.Frame(power, bg=power.cget("bg"))
        prow.pack(fill="x", padx=12, pady=(0, 8))
        tk.Checkbutton(
            prow, text="Activar amplificación controlada", variable=self.power_enabled_var,
            command=self._power_changed, bg=power.cget("bg"), fg=self.TEXT, selectcolor="#162016",
            activebackground=power.cget("bg"), activeforeground=self.GREEN, font=("Consolas", 10, "bold")
        ).pack(anchor="w")
        self._scale(prow, self.power_var, 0, 100, command=lambda v: self._power_changed(), length=620).pack(fill="x", pady=(2, 0))
        self._label(prow, "Ganancia perceptual + compresor/limitador. Subilo de a poco: 20-45 suele ser usable.", size=8, fg=self.MUTED).pack(anchor="w")

    def _build_analyzer_panel(self, parent: tk.Frame) -> None:
        rack = self._rack_frame(parent)
        rack.pack(fill="both", expand=True)
        top = tk.Frame(rack, bg=rack.cget("bg"))
        top.pack(fill="x", padx=12, pady=(8, 0))
        self._label(top, "SPECTRUM ANALYZER · 20 BAND", size=12, bold=True, fg=self.AMBER).pack(side="left")
        self.clip_label = self._label(top, "LIMIT OK", size=10, bold=True, fg=self.GREEN, anchor="e")
        self.clip_label.pack(side="right")
        self.spectrum = SpectrumCanvas(rack, bands=self.SPEC_BANDS)
        self.spectrum.pack(fill="both", expand=True, padx=12, pady=(8, 4))
        self._label(top, "", size=8).pack(side="right")
        vu_title = tk.Frame(rack, bg=rack.cget("bg"))
        vu_title.pack(fill="x", padx=12)
        self._label(vu_title, "DUAL LED VU METER · dB CAL", size=10, bold=True, fg=self.MUTED).pack(side="left")
        self.vu_canvas = VUMeterCanvas(rack, height=150)
        self.vu_canvas.pack(fill="x", padx=12, pady=(4, 12))

    # --------------------------------------------------------------------- eq
    def _build_eq_panel(self, parent: tk.Frame) -> None:
        top=tk.Frame(parent,bg=parent.cget("bg"));top.pack(fill="x",padx=10,pady=(10,6));self._label(top,"GRAPHIC EQUALIZER",size=12,bold=True,fg=self.AMBER).pack(side="left");self._label(top,textvariable=self.eq_mode_var,size=8,bold=True,fg=self.BLUE,anchor="e").pack(side="right")
        ai=tk.Frame(parent,bg=parent.cget("bg"));ai.pack(fill="x",padx=10,pady=(0,6));self._retro_button(ai,"🧠 AI EQ · AUTO / NVIDIA",self.open_ai_eq_dialog,fg=self.AMBER).pack(fill="x")
        box=tk.Frame(parent,bg=self.PANEL3,bd=1,relief="sunken");box.pack(fill="x",padx=10,pady=(0,6));self._label(box,"PRESET / MEMORY",size=8,bold=True,fg=self.MUTED).pack(anchor="w",padx=7,pady=(5,2));self.preset_combo=ttk.Combobox(box,textvariable=self.preset_var,state="readonly",values=self._all_preset_names(),style="Vintage.TCombobox",font=("Consolas",10));self.preset_combo.pack(fill="x",padx=7,pady=(0,6));self.preset_combo.bind("<<ComboboxSelected>>",lambda _e:self.apply_preset(self.preset_var.get()))
        mem=tk.Frame(parent,bg=parent.cget("bg"));mem.pack(fill="x",padx=10,pady=(0,7));buttons=[("Guardar",self.save_user_eq_preset),("Borrar",self.delete_user_eq_preset),("Importar",self.import_eq_presets),("Exportar",self.export_eq_presets)]
        for i,(text,cmd) in enumerate(buttons):b=self._retro_button(mem,text,cmd);b.configure(font=("Consolas",8,"bold"),padx=3,pady=2);b.grid(row=i//2,column=i%2,sticky="ew",padx=2,pady=2)
        mem.columnconfigure(0,weight=1);mem.columnconfigure(1,weight=1)
        area=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken");area.pack(fill="both",expand=True,padx=10,pady=(0,7));labels=["31","62","125","250","500","1k","2k","4k","8k","16k"];sliders=tk.Frame(area,bg=area.cget("bg"));sliders.pack(fill="both",expand=True,padx=5,pady=(6,2));self.eq_sliders.clear()
        for i,label in enumerate(labels):
            col=tk.Frame(sliders,bg=sliders.cget("bg"));col.grid(row=0,column=i,sticky="nsew",padx=1);value=tk.StringVar(value="+0.0");self._label(col,textvariable=value,size=7,bold=True,fg=self.TEXT,anchor="center").pack(fill="x");var=tk.DoubleVar(value=0.0);scale=tk.Scale(col,variable=var,from_=12,to=-12,orient="vertical",length=245,resolution=0.5,command=lambda _v:self._eq_changed(),bg=col.cget("bg"),fg=self.TEXT,troughcolor="#050805",activebackground=self.GREEN,highlightthickness=0,bd=0,width=9,sliderlength=15,showvalue=False);scale.var=var;scale.value_var=value;scale.pack(fill="y",expand=True);scale.bind("<MouseWheel>",lambda e,band=i:self._eq_mousewheel(e,band));scale.bind("<Button-4>",lambda _e,band=i:self._nudge_eq_band(band,0.5));scale.bind("<Button-5>",lambda _e,band=i:self._nudge_eq_band(band,-0.5));scale.bind("<Double-Button-1>",lambda _e,band=i:self._reset_eq_band(band));self._label(col,label,size=8,bold=True,fg=self.AMBER,anchor="center").pack(fill="x",pady=(1,0));self.eq_sliders.append(scale);sliders.columnconfigure(i,weight=1,uniform="eqbands")
        sliders.rowconfigure(0,weight=1);self._label(area,"MANUAL: arrastrá · rueda ±0,5 dB · doble clic resetea una banda",size=7,fg=self.BLUE,anchor="center").pack(fill="x",padx=6,pady=(1,6))
        row=tk.Frame(parent,bg=parent.cget("bg"));row.pack(fill="x",padx=10,pady=(0,7));self._retro_button(row,"FLAT",lambda:self.apply_preset("Flat")).pack(side="left",expand=True,fill="x",padx=(0,3));self._retro_button(row,"JBL HI-FI",lambda:self.apply_preset("Hi‑Fi JBL"),fg=self.GREEN).pack(side="left",expand=True,fill="x",padx=(3,0))
        sleep=tk.Frame(parent,bg=self.PANEL3,bd=2,relief="sunken");sleep.pack(fill="x",padx=10,pady=(0,7));sr=tk.Frame(sleep,bg=sleep.cget("bg"));sr.pack(fill="x",padx=8,pady=7);self._label(sr,"SLEEP",size=10,bold=True,fg=self.BLUE).pack(side="left");combo=ttk.Combobox(sr,textvariable=self.sleep_var,state="readonly",values=self.SLEEP_OPTIONS,style="Vintage.TCombobox",font=("Consolas",9),width=8);combo.pack(side="left",padx=8);combo.bind("<<ComboboxSelected>>",lambda _e:self._sleep_changed());self._label(sr,textvariable=self.sleep_label_var,size=11,bold=True,fg=self.AMBER,anchor="e").pack(side="right")
        tips=tk.Frame(parent,bg=self.PANEL3,bd=1,relief="sunken");tips.pack(fill="x",padx=10,pady=(0,10));tip=self._label(tips,"TIP: AI AUTO toma artista y tema en reproducción · REC guarda MP3 en Música\\LQP Grabaciones.",size=7,fg=self.MUTED);tip.configure(wraplength=390,justify="left");tip.pack(fill="x",padx=8,pady=6)

    # ------------------------------------------------------------------- keys
    def _bind_keys(self) -> None:
        def space(_event=None):
            widget = self.root.focus_get()
            if isinstance(widget, (tk.Entry, ttk.Combobox)):
                return
            self.toggle_play_pause()
        self.root.bind("<space>", space)
        self.root.bind("<Right>", lambda e: self.seek_relative(10))
        self.root.bind("<Left>", lambda e: self.seek_relative(-10))
        self.root.bind("<Up>", lambda e: self._nudge_volume(5))
        self.root.bind("<Down>", lambda e: self._nudge_volume(-5))
        self.root.bind("<Control-o>", lambda e: self.add_files())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _nudge_volume(self, delta: float) -> None:
        widget = self.root.focus_get()
        if isinstance(widget, (tk.Scale, tk.Listbox, ttk.Combobox)):
            return
        value = clamp(float(self.volume_var.get()) + delta, 0, 120)
        self.volume_var.set(value)
        self.engine.set_volume(value / 100.0)


    # ---------------------------------------------------------------- devices
    def _refresh_devices(self) -> None:
        self.device_map = {"Salida predeterminada": None}
        try:
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                if int(dev.get("max_output_channels", 0) or 0) > 0:
                    host = sd.query_hostapis(dev.get("hostapi", 0)).get("name", "")
                    name = f"{idx}: {dev.get('name')} [{host}]"
                    self.device_map[name] = idx
            self.device_combo["values"] = list(self.device_map.keys())
            if self.device_var.get() not in self.device_map:
                self.device_var.set("Salida predeterminada")
        except Exception as exc:
            self.status_var.set(f"No se pudieron listar salidas de audio: {exc}")

    def _device_changed(self, _event=None) -> None:
        name = self.device_var.get()
        self.engine.set_output_device(self.device_map.get(name))
        self.status_var.set(f"Salida de audio seleccionada: {name}")

    # ------------------------------------------------------------------- tick
    def _tick(self) -> None:
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "track_loaded":
                    self._after_track_loaded(payload)
                elif kind == "error":
                    self.loading = False
                    messagebox.showerror("LQP HiFi", str(payload))
                    self.status_var.set("Error: " + str(payload).split("\n")[0])
                elif kind == "track_finished":
                    self._handle_track_finished()
                elif kind == "radio_results":
                    scope, results, replace = payload
                    self.status_var.set(f"Radios agregadas: {self._merge_radios(scope, results, replace)}")
                elif kind == "world_city_results":
                    city, results, silent = payload
                    if results:
                        self.world_radios = results; self.current_world_radio_index = -1
                        self._refresh_world_radio_box(); self._save_config()
                        if not silent: self.status_var.set(f"{city}: {len(results)} radios operativas.")
                elif kind == "radio_refresh_complete":
                    refreshed, changes, silent = payload
                    self.radios = refreshed; self.last_radio_maintenance = time.time()
                    self._refresh_radio_box(); self._save_config()
                    if not silent or changes: self.status_var.set(f"Radios argentinas actualizadas: {changes} URLs.")
                elif kind == "stream_test_result":
                    _scope, _index, station_name, ok, message = payload
                    self.status_var.set(f"{station_name}: {message.splitlines()[0]}")
                    (messagebox.showinfo if ok else messagebox.showwarning)("Test stream", f"{station_name}\n\n{message}")
                elif kind == "radio_repair_result":
                    scope, index, replacement, ok, message = payload
                    target = self.world_radios if scope == "world" else self.radios
                    if ok and replacement is not None and 0 <= index < len(target):
                        previous = target[index]; replacement.name = previous.name; replacement.genre = previous.genre
                        replacement.city = previous.city or replacement.city; replacement.logo_query = previous.logo_query
                        target[index] = replacement
                        if self.current_radio_scope == scope and ((scope == "world" and self.current_world_radio_index == index) or (scope == "ar" and self.current_radio_index == index)):
                            self.current_station = replacement
                        self._refresh_world_radio_box() if scope == "world" else self._refresh_radio_box(); self._save_config()
                        messagebox.showinfo("Reparar radio", f"URL actualizada para {replacement.name}.")
                    else: messagebox.showwarning("Reparar radio", message)
                elif kind == "status":
                    self.status_var.set(str(payload))
                elif kind == "logo_image":
                    key, pil_img = payload
                    self.logo_cache[key] = ImageTk.PhotoImage(pil_img)
                    self._radio_selection_changed("ar"); self._radio_selection_changed("world")
                elif kind == "ai_eq_result":
                    ok, result = payload
                    self._handle_ai_eq_result(ok, result)
        except queue.Empty:
            pass
        try:
            self._update_time_ui()
            self._update_visuals()
            self._update_sleep()
        except Exception:
            pass
        if self.engine.last_error:
            self.status_var.set("Audio engine: " + self.engine.last_error.splitlines()[-1][:140])
            self.engine.last_error = None
        self._tick_after_id = self.root.after(45, self._tick)

    def _update_time_ui(self) -> None:
        if self.engine.mode == "radio":
            pos = self.engine.get_position_seconds()
            buffer_txt = " · BUFFER" if self.engine.radio_buffering and self.engine.playing else ""
            self.time_var.set(f"RADIO {format_time(pos)}{buffer_txt}")
            if not self.seeking:
                self.seek_var.set(0)
            return
        duration = self.engine.get_duration_seconds()
        pos = self.engine.get_position_seconds()
        self.time_var.set(f"{format_time(pos)} / {format_time(duration)}")
        if not self.seeking and duration > 0:
            self.seek_var.set(clamp(pos / duration * 1000, 0, 1000))

    def _update_visuals(self) -> None:
        engine = self.engine
        blink = int(time.time() * 2) % 2 == 0
        playing = engine.playing
        mode = engine.mode

        # Display fluorescente.
        if mode == "local" and engine.loaded_info:
            info = engine.loaded_info
            mode_text = f"{info.codec_hint or 'PCM'} {engine.sample_rate / 1000.0:.1f}k"
            time_text = format_time(engine.get_position_seconds())
        elif mode == "radio" and engine.loaded_info:
            mode_text = "RADIO NET"
            time_text = format_time(engine.get_position_seconds())
        else:
            mode_text = "STANDBY"
            time_text = "00:00"
        hint = ""
        if self.recorder.active:
            hint = f"● REC {format_time(self.recorder.elapsed())} · {self.recorder.station_name[:22]}"
        self.deck_display.set_texts(self._display_title, self._display_info, time_text, mode_text, hint)
        signal_on = mode == "radio" and playing and not engine.radio_buffering
        self.deck_display.set_leds(self.recorder.active, signal_on, playing)
        self.deck_display.tick(blink)

        # Cassette.
        if mode == "local":
            duration = engine.get_duration_seconds()
            progress = engine.get_position_seconds() / duration if duration > 0 else 0.0
        elif mode == "radio":
            progress = (engine.get_position_seconds() % 180.0) / 180.0
        else:
            progress = 0.0
        self.cassette.update_state(progress, playing)

        # Espectro + VU.
        self._compute_spectrum()
        self.spectrum.update_levels(self.spec_levels, self.spec_peaks)
        with engine.lock:
            l, r = engine.vu_left, engine.vu_right
            pl, pr = engine.peak_left, engine.peak_right
            clip = engine.clip_warning
            power_enabled = engine.power_enabled
        self.vu_canvas.update_levels(l, r, pl, pr, clip)
        self.clip_label.config(
            text="LIMIT / CLIP" if clip else ("POWER ON" if power_enabled else "LIMIT OK"),
            fg=self.RED if clip else (self.ORANGE if power_enabled else self.GREEN))

        # Botón REC.
        rec_state = "on" if self.recorder.active else "off"
        if getattr(self, "_rec_btn_state", "") != rec_state:
            self._rec_btn_state = rec_state
            if rec_state == "on":
                self.rec_button.config(bg="#3a0e0a", relief="sunken", text="■ STOP REC")
            else:
                self.rec_button.config(bg="#182018", relief="raised", text="● REC")

    def _compute_spectrum(self) -> None:
        engine = self.engine
        mono = engine.monitor_mono
        if not engine.playing or mono is None or mono.size < 512:
            self.spec_levels = [max(0.0, v - 0.07) for v in self.spec_levels]
            self.spec_peaks = [max(0.0, v - 0.015) for v in self.spec_peaks]
            return
        n = int(min(4096, mono.size))
        x = mono[-n:].astype(np.float64)
        if self._spec_win_n != n or self._spec_win is None:
            self._spec_win = np.hanning(n)
            self._spec_win_n = n
        mag = np.abs(np.fft.rfft(x * self._spec_win)) / (n / 2.0)
        freqs = np.fft.rfftfreq(n, 1.0 / max(8000, engine.sample_rate))
        for i in range(self.SPEC_BANDS):
            lo, hi = self.spec_edges[i], self.spec_edges[i + 1]
            sel = (freqs >= lo) & (freqs < hi)
            if np.any(sel):
                v = float(np.sqrt(np.mean(mag[sel] ** 2)))
            else:
                v = 0.0
            db = 20.0 * math.log10(v + 1e-8)
            # Leve compensación de tilt para que los agudos no queden planchados.
            norm = clamp((db + 64.0) / 62.0 + i * 0.010, 0.0, 1.0)
            prev = self.spec_levels[i]
            self.spec_levels[i] = norm if norm > prev else max(0.0, prev - 0.09)
            pk = self.spec_peaks[i]
            self.spec_peaks[i] = norm if norm > pk else max(0.0, pk - 0.012)

    # ------------------------------------------------------------ sleep timer
    def _sleep_changed(self) -> None:
        value = self.sleep_var.get()
        if value == "OFF":
            self.sleep_deadline = None
            self.sleep_label_var.set("--:--")
            self.engine.set_volume(float(self.volume_var.get()) / 100.0)
            self.status_var.set("Sleep timer apagado.")
            return
        try:
            minutes = int(value.split()[0])
        except Exception:
            return
        self.sleep_deadline = time.time() + minutes * 60
        self.status_var.set(f"Sleep timer: la música se apaga en {minutes} minutos con fade-out.")

    def _update_sleep(self) -> None:
        if not self.sleep_deadline:
            return
        remaining = self.sleep_deadline - time.time()
        base = float(self.volume_var.get()) / 100.0
        if remaining <= 0:
            self.sleep_deadline = None
            self.sleep_var.set("OFF")
            self.sleep_label_var.set("--:--")
            self.engine.pause()
            self.engine.set_volume(base)
            self.status_var.set("Sleep timer: reproducción pausada. Buenas noches.")
            return
        self.sleep_label_var.set(f"{int(remaining // 60):02d}:{int(remaining % 60):02d}")
        if remaining < 12.0:
            self.engine.set_volume(base * (remaining / 12.0))

    # ---------------------------------------------------------------- eq/power
    def _eq_changed(self, manual: bool = True) -> None:
        gains=[float(getattr(x,"var").get()) for x in self.eq_sliders]
        for scale,gain in zip(self.eq_sliders,gains):
            value=getattr(scale,"value_var",None)
            if value is not None:value.set(f"{gain:+.1f}")
        if self._eq_programmatic:return
        self.engine.set_eq_gains(gains)
        if manual:self.eq_mode_var.set("MANUAL · LIVE");self.preset_var.set("Manual")
    def _nudge_eq_band(self,index,delta):
        if not 0<=index<len(self.eq_sliders):return "break"
        var=getattr(self.eq_sliders[index],"var");var.set(clamp(round((float(var.get())+delta)*2)/2,-12,12));self._eq_changed();return "break"
    def _eq_mousewheel(self,event,index):return self._nudge_eq_band(index,0.5 if getattr(event,"delta",0)>0 else -0.5)
    def _reset_eq_band(self,index):
        if 0<=index<len(self.eq_sliders):getattr(self.eq_sliders[index],"var").set(0.0);self._eq_changed()
        return "break"
    def apply_preset(self,name):
        if name=="Manual":self.eq_mode_var.set("MANUAL · LIVE");return
        clean=name[2:] if name.startswith("★ ") else name;gains=self.EQ_PRESETS.get(clean) or self.user_eq_presets.get(clean)
        if not gains:return
        self._eq_programmatic=True
        try:
            for scale,gain in zip(self.eq_sliders,gains):getattr(scale,"var").set(gain)
        finally:self._eq_programmatic=False
        self._eq_changed(manual=False);self.preset_var.set(name);self.eq_mode_var.set("MEMORY · AJUSTABLE" if clean in self.user_eq_presets else "PRESET · AJUSTABLE")

    # ---------------------------------------------------------- memory eq
    def _all_preset_names(self) -> List[str]:
        return ["Manual"] + list(self.EQ_PRESETS.keys()) + [f"★ {n}" for n in sorted(self.user_eq_presets.keys())]

    def _refresh_preset_combo(self) -> None:
        if hasattr(self, "preset_combo"):
            self.preset_combo["values"] = self._all_preset_names()

    def save_user_eq_preset(self) -> None:
        name = simpledialog.askstring("Guardar seteo EQ", "Nombre para este seteo de ecualización:")
        if not name:
            return
        name = name.strip()[:40]
        if not name:
            return
        if name in self.EQ_PRESETS:
            messagebox.showwarning("Guardar seteo EQ", f"'{name}' es un preset de fábrica. Elegí otro nombre.")
            return
        gains = [float(getattr(s, "var").get()) for s in self.eq_sliders]
        existed = name in self.user_eq_presets
        self.user_eq_presets[name] = gains
        self._refresh_preset_combo()
        self.preset_var.set(f"★ {name}")
        self.eq_mode_var.set("MEMORY · AJUSTABLE")
        self._save_config()
        self.status_var.set(("Seteo actualizado: " if existed else "Seteo guardado: ") + name)

    def delete_user_eq_preset(self) -> None:
        name = self.preset_var.get()
        clean = name[2:] if name.startswith("★ ") else name
        if clean not in self.user_eq_presets:
            messagebox.showinfo("Borrar seteo EQ", "Seleccioná primero uno de TUS seteos (marcados con ★) en la lista.\nLos presets de fábrica no se pueden borrar.")
            return
        if not messagebox.askyesno("Borrar seteo EQ", f"¿Borrar el seteo '{clean}'?"):
            return
        self.user_eq_presets.pop(clean, None)
        self._refresh_preset_combo()
        self.preset_var.set("Flat")
        self._save_config()
        self.status_var.set(f"Seteo borrado: {clean}")

    def import_eq_presets(self) -> None:
        path = filedialog.askopenfilename(title="Importar seteos de EQ", filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            items = data.get("eq_presets", data) if isinstance(data, dict) else {}
            if not isinstance(items, dict):
                raise ValueError("El archivo no tiene el formato esperado ({nombre: [10 ganancias]}).")
            added = 0
            for name, gains in items.items():
                if not isinstance(gains, list) or len(gains) != 10:
                    continue
                try:
                    cleaned = [clamp(float(g), -12.0, 12.0) for g in gains]
                except Exception:
                    continue
                self.user_eq_presets[str(name)[:40]] = cleaned
                added += 1
            self._refresh_preset_combo()
            self._save_config()
            self.status_var.set(f"Seteos de EQ importados: {added}")
            if not added:
                messagebox.showwarning("Importar seteos de EQ", "No se encontraron seteos válidos en el archivo.")
        except Exception as exc:
            messagebox.showerror("Importar seteos de EQ", str(exc))

    def export_eq_presets(self) -> None:
        if not self.user_eq_presets:
            messagebox.showinfo("Exportar seteos de EQ", "Todavía no guardaste ningún seteo propio.\nMové los sliders y usá 'Guardar' para crear uno.")
            return
        path = filedialog.asksaveasfilename(title="Exportar seteos de EQ", defaultextension=".json",
                                            initialfile="mis_seteos_eq.json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            data = {"app": APP_NAME, "version": APP_VERSION, "type": "eq_presets", "eq_presets": self.user_eq_presets}
            Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status_var.set(f"Seteos de EQ exportados: {path}")
        except Exception as exc:
            messagebox.showerror("Exportar seteos de EQ", str(exc))

    # ------------------------------------------------------------------ ai eq
    def open_ai_eq_dialog(self) -> None:
        if self.ai_dialog is not None and self.ai_dialog.winfo_exists():self.ai_dialog.lift();self.ai_dialog.focus_force();return
        dlg=tk.Toplevel(self.root);self.ai_dialog=dlg;dlg.title("AI EQ · DETECCIÓN AUTOMÁTICA · NVIDIA");dlg.configure(bg=self.PANEL);dlg.geometry("760x790");dlg.minsize(690,700);dlg.transient(self.root)
        head=tk.Frame(dlg,bg=self.PANEL);head.pack(fill="x",padx=14,pady=(12,2));self._label(head,"🧠 AI EQ · AUTO TRACK",size=14,bold=True,fg=self.AMBER).pack(side="left");self._label(head,"NVIDIA · BYOK",size=8,fg=self.MUTED).pack(side="right")
        self._label(dlg,"Detectá la pista actual, revisá los datos o ecualizá directamente. Después podés retocar las 10 bandas.",size=9,fg=self.MUTED).pack(fill="x",padx=14,pady=(0,8))
        keybox=tk.Frame(dlg,bg=self.PANEL3,bd=2,relief="sunken");keybox.pack(fill="x",padx=14,pady=(0,8));self._label(keybox,"TU NVIDIA API KEY",size=9,bold=True,fg=self.BLUE).pack(anchor="w",padx=8,pady=(7,2));kr=tk.Frame(keybox,bg=keybox.cget("bg"));kr.pack(fill="x",padx=8);self.ai_key_var=tk.StringVar(value=self.nvidia_api_key);self.ai_key_visible_var=tk.BooleanVar(value=False);self.ai_key_entry=tk.Entry(kr,textvariable=self.ai_key_var,show="•",bg="#050805",fg=self.TEXT,insertbackground=self.GREEN,font=("Consolas",10),relief="sunken",bd=2);self.ai_key_entry.pack(side="left",fill="x",expand=True,padx=(0,4));self._retro_button(kr,"Mostrar",self._toggle_ai_key_visibility,width=8).pack(side="left")
        ka=tk.Frame(keybox,bg=keybox.cget("bg"));ka.pack(fill="x",padx=8,pady=(5,7));self.remember_nvidia_key_var=tk.BooleanVar(value=bool(self.nvidia_key_protected) or os.name=="nt");tk.Checkbutton(ka,text="Recordar cifrada para este usuario",variable=self.remember_nvidia_key_var,bg=ka.cget("bg"),fg=self.TEXT,selectcolor="#162016",activebackground=ka.cget("bg"),activeforeground=self.GREEN,font=("Consolas",8,"bold")).pack(side="left");self._retro_button(ka,"Guardar key",self._persist_nvidia_key,fg=self.GREEN).pack(side="right",padx=(3,0));self._retro_button(ka,"Borrar",self._delete_nvidia_key,fg=self.RED).pack(side="right",padx=3);self._retro_button(ka,"Obtener key",self._open_nvidia_keys_page,fg=self.AMBER).pack(side="right",padx=3)
        form=tk.Frame(dlg,bg=self.PANEL);form.pack(fill="x",padx=14,pady=2);form.columnconfigure(1,weight=1);self.ai_genre_var=tk.StringVar();self.ai_band_var=tk.StringVar();self.ai_track_var=tk.StringVar();self.ai_speakers_var=tk.StringVar(value=self.ai_speakers_default);self.ai_equipment_var=tk.StringVar(value=self.ai_equipment_default)
        for row,(label,var,hint) in enumerate([("GÉNERO MUSICAL",self.ai_genre_var,"se toma de los metadatos si existe"),("BANDA / ARTISTA",self.ai_band_var,"automático o manual"),("TEMA ESPECÍFICO",self.ai_track_var,"automático o manual"),("PARLANTES",self.ai_speakers_var,"JBL 104, Edifier..."),("EQUIPO EN LA CADENA",self.ai_equipment_var,"DAC, mixer, Bluetooth...")]):self._label(form,label,size=9,bold=True,fg=self.MUTED).grid(row=row,column=0,sticky="w",pady=4,padx=(0,8));entry=tk.Entry(form,textvariable=var,bg="#050805",fg=self.TEXT,insertbackground=self.GREEN,font=("Consolas",10),relief="sunken",bd=2);entry.grid(row=row,column=1,sticky="ew",pady=4);self._label(form,hint,size=7,fg="#4d6b52").grid(row=row,column=2,sticky="w",padx=(8,0))
        auto=tk.Frame(dlg,bg=self.PANEL3,bd=1,relief="sunken");auto.pack(fill="x",padx=14,pady=(7,7));buttons=tk.Frame(auto,bg=auto.cget("bg"));buttons.pack(fill="x",padx=7,pady=(7,3));self._retro_button(buttons,"🎵 Detectar tema actual",lambda:self.auto_ai_eq_current_track(run_now=False),fg=self.BLUE).pack(side="left",fill="x",expand=True,padx=(0,3));self._retro_button(buttons,"⚡ Detectar + Ecualizar",lambda:self.auto_ai_eq_current_track(run_now=True),fg=self.AMBER).pack(side="left",fill="x",expand=True,padx=(3,0));self.ai_auto_change_var=tk.BooleanVar(value=self.ai_auto_on_track_change);tk.Checkbutton(auto,text="AUTO: recalcular al cambiar de tema local",variable=self.ai_auto_change_var,command=self._toggle_ai_auto_change,bg=auto.cget("bg"),fg=self.TEXT,selectcolor="#162016",activebackground=auto.cget("bg"),activeforeground=self.GREEN,font=("Consolas",8,"bold")).pack(anchor="w",padx=8,pady=(0,7))
        self.ai_btn=self._retro_button(dlg,"🧠 AJUSTAR CON LOS DATOS DEL FORMULARIO",self._ai_eq_submit,fg=self.AMBER);self.ai_btn.pack(fill="x",padx=14,pady=(2,4));self.ai_status_var=tk.StringVar(value="Podés escribir los datos o usar la detección automática.");self._label(dlg,textvariable=self.ai_status_var,size=9,fg=self.BLUE).pack(fill="x",padx=14,pady=(0,6))
        expl=tk.Frame(dlg,bg=self.PANEL3,bd=2,relief="sunken");expl.pack(fill="both",expand=True,padx=14,pady=(0,8));self._label(expl,"POR QUÉ ESTA CURVA:",size=8,bold=True,fg=self.MUTED).pack(fill="x",padx=8,pady=(6,0));self.ai_expl_text=tk.Text(expl,height=4,bg="#050805",fg="#d7ffd1",font=("Consolas",9),wrap="word",relief="flat",bd=0,state="disabled");self.ai_expl_text.pack(fill="both",expand=True,padx=8,pady=6)
        save=tk.Frame(dlg,bg=self.PANEL);save.pack(fill="x",padx=14,pady=(0,14));self._label(save,"NOMBRE:",size=9,bold=True,fg=self.MUTED).pack(side="left",padx=(0,6));self.ai_name_var=tk.StringVar();tk.Entry(save,textvariable=self.ai_name_var,bg="#050805",fg=self.TEXT,insertbackground=self.GREEN,font=("Consolas",10),relief="sunken",bd=2).pack(side="left",fill="x",expand=True,padx=(0,6));self._retro_button(save,"💾 Guardar seteo",self._ai_eq_save_current,fg=self.GREEN).pack(side="right")

    def _toggle_ai_key_visibility(self):
        visible=not bool(self.ai_key_visible_var.get());self.ai_key_visible_var.set(visible);self.ai_key_entry.configure(show="" if visible else "•")
    def _open_nvidia_keys_page(self):
        try:webbrowser.open(NVIDIA_KEYS_URL);self.ai_status_var.set("Abrí NVIDIA Build para generar tu key.")
        except Exception as exc:self.ai_status_var.set(str(exc))
    def _persist_nvidia_key(self):
        key=self.ai_key_var.get().strip() if hasattr(self,"ai_key_var") else self.nvidia_api_key
        if not key:return False
        self.nvidia_api_key=key
        if os.name!="nt":self.ai_status_var.set("Key activa para esta sesión; el guardado cifrado se habilita en Windows.");return True
        try:
            protected=protect_secret_for_current_user(key);previous=self.nvidia_key_protected;self.nvidia_key_protected=protected
            if not self._save_config():self.nvidia_key_protected=previous;raise RuntimeError("No se pudo escribir la configuración.")
            self.ai_status_var.set("API key guardada cifrada con DPAPI.");return True
        except Exception as exc:self.ai_status_var.set(f"No se pudo guardar: {exc}");return False
    def _delete_nvidia_key(self):
        self.nvidia_api_key="";self.nvidia_key_protected="";self.ai_key_var.set("");self._save_config();self.ai_status_var.set("API key eliminada.")
    def _toggle_ai_auto_change(self):
        self.ai_auto_on_track_change=bool(self.ai_auto_change_var.get());self._save_config();self.ai_status_var.set("Modo automático al cambiar de tema: "+("ACTIVADO" if self.ai_auto_on_track_change else "DESACTIVADO"))

    @staticmethod
    def _split_artist_title_from_filename(stem: str) -> Tuple[str,str]:
        for separator in (" - "," – "," — ","_-"):
            if separator in stem:
                left,right=stem.split(separator,1)
                if left.strip() and right.strip():return left.strip(),right.strip()
        return "",stem.strip()
    def _detect_current_track_metadata(self) -> Dict[str,str]:
        info=self.engine.loaded_info
        if self.engine.mode=="radio" and self.current_station:
            return {"genre":self.current_station.genre,"artist":self.current_station.name,"track":"","source":"radio","note":"La emisora no publicó el título del tema; se usaron nombre y género de la radio."}
        path=""
        if info and not info.is_stream:path=info.path
        elif hasattr(self,"playlist_box") and self.playlist_box.curselection():
            index=int(self.playlist_box.curselection()[0]);path=self.playlist[index] if 0<=index<len(self.playlist) else ""
        elif 0<=self.current_index<len(self.playlist):path=self.playlist[self.current_index]
        if not path:return {"genre":"","artist":"","track":"","source":"none","note":"No hay un tema local cargado o seleccionado."}
        meta=read_track_info(path);artist=(meta.artist or (info.artist if info else "")).strip();title=(meta.title or (info.title if info else "")).strip();genre=(meta.genre or (info.genre if info else "")).strip();stem=Path(path).stem
        file_artist,file_title=self._split_artist_title_from_filename(stem)
        if not artist:artist=file_artist
        if not title:title=file_title
        return {"genre":genre,"artist":artist,"track":title,"source":"local","note":f"Detectado desde: {Path(path).name}"}
    def auto_ai_eq_current_track(self,run_now=False,quiet=False):
        data=self._detect_current_track_metadata()
        if data["source"]=="none":
            if hasattr(self,"ai_status_var"):self.ai_status_var.set(data["note"])
            self.status_var.set(data["note"]);return
        if not quiet:
            if not (self.ai_dialog and self.ai_dialog.winfo_exists()):self.open_ai_eq_dialog()
            self.ai_genre_var.set(data["genre"]);self.ai_band_var.set(data["artist"]);self.ai_track_var.set(data["track"]);self.ai_status_var.set(data["note"]+" · Podés corregir los datos antes de aplicar.")
        if not run_now:return
        if quiet:
            key=self.nvidia_api_key
            if not key or self.ai_busy:return
            self.ai_busy=True;self.status_var.set(f"AI AUTO: ecualizando {data['artist']} — {data['track']}...")
            def worker():
                try:self.ui_queue.put(("ai_eq_result",(True,nvidia_eq_suggestion(data["genre"],data["artist"],data["track"],self.ai_speakers_default,self.ai_equipment_default,key))))
                except Exception as exc:self.ui_queue.put(("ai_eq_result",(False,str(exc))))
            threading.Thread(target=worker,daemon=True).start()
        else:self._ai_eq_submit()
    def _ai_eq_submit(self):
        if self.ai_busy:return
        genre=self.ai_genre_var.get().strip();band=self.ai_band_var.get().strip();track=self.ai_track_var.get().strip();speakers=self.ai_speakers_var.get().strip();equipment=self.ai_equipment_var.get().strip();key=self.ai_key_var.get().strip()
        if not key:self.ai_status_var.set("Falta tu NVIDIA API key.");return
        if not (genre or band or track):self.ai_status_var.set("Escribí datos o detectá el tema actual.");return
        self.nvidia_api_key=key;self.ai_speakers_default=speakers;self.ai_equipment_default=equipment
        if self.remember_nvidia_key_var.get():self._persist_nvidia_key()
        self._save_config()
        self.ai_busy=True;self.ai_btn.config(state="disabled",text="⏳ CONSULTANDO NVIDIA...");self.ai_status_var.set("Analizando el tema y tu equipo...")
        def worker():
            try:self.ui_queue.put(("ai_eq_result",(True,nvidia_eq_suggestion(genre,band,track,speakers,equipment,key))))
            except Exception as exc:self.ui_queue.put(("ai_eq_result",(False,str(exc))))
        threading.Thread(target=worker,daemon=True).start()
    def _handle_ai_eq_result(self,ok,result):
        self.ai_busy=False;alive=self.ai_dialog is not None and self.ai_dialog.winfo_exists()
        if alive:self.ai_btn.config(state="normal",text="🧠 AJUSTAR CON LOS DATOS DEL FORMULARIO")
        if not ok:
            msg="Error de AI EQ: "+str(result)[:280]
            if alive:self.ai_status_var.set(msg)
            self.status_var.set(msg);return
        self._eq_programmatic=True
        try:
            for scale,gain in zip(self.eq_sliders,result["gains"]):getattr(scale,"var").set(gain)
        finally:self._eq_programmatic=False
        self._eq_changed(manual=False);self.eq_mode_var.set("AI AUTO · AJUSTABLE" if self.ai_auto_on_track_change else "AI · AJUSTABLE");self.preset_var.set("Manual");name=result.get("name") or "AI EQ";why=result.get("why") or ""
        if alive:self.ai_name_var.set(name);self.ai_expl_text.config(state="normal");self.ai_expl_text.delete("1.0",tk.END);self.ai_expl_text.insert("1.0",why);self.ai_expl_text.config(state="disabled");self.ai_status_var.set("Curva aplicada. Podés ajustar cualquier palanca.")
        self.status_var.set(f"AI EQ aplicada: {name}")
    def _ai_eq_save_current(self):
        name=self.ai_name_var.get().strip()[:40]
        if not name:self.ai_status_var.set("Poné un nombre.");return
        if name in self.EQ_PRESETS:self.ai_status_var.set("Elegí otro nombre.");return
        self.user_eq_presets[name]=[float(getattr(x,"var").get()) for x in self.eq_sliders];self._refresh_preset_combo();self.preset_var.set(f"★ {name}");self.eq_mode_var.set("MEMORY · AJUSTABLE");self._save_config();self.ai_status_var.set("Seteo guardado: "+name)

    def _power_changed(self) -> None:
        enabled = self.power_enabled_var.get()
        amount = self.power_var.get()
        self.engine.set_power(enabled, amount)
        self.power_state_label.config(text=f"ON {amount:.0f}%" if enabled else "OFF", fg=self.ORANGE if enabled else self.MUTED)
        if enabled and amount > 70:
            self.status_var.set("POWER STAGE alto: si el vúmetro llega a rojo, bajá Power o Preamp para cuidar los parlantes.")

    # ----------------------------------------------------------- playlist local
    @staticmethod
    def _path_identity(path):
        try: return os.path.normcase(str(Path(path).expanduser().resolve()))
        except Exception: return os.path.normcase(os.path.abspath(os.path.expanduser(path)))
    def _collect_audio_paths(self,paths):
        out=[]
        for raw in paths or []:
            if not raw: continue
            item=Path(str(raw).strip().strip('"')).expanduser()
            if item.is_dir():
                try: out.extend(str(x.resolve()) for x in sorted(item.rglob('*'),key=lambda v:str(v).casefold()) if x.is_file() and x.suffix.lower() in AUDIO_EXTENSIONS)
                except Exception: pass
            elif item.is_file() and item.suffix.lower() in AUDIO_EXTENSIONS:
                try: out.append(str(item.resolve()))
                except Exception: out.append(str(item))
        return out
    def add_files(self):
        self._add_paths(filedialog.askopenfilenames(title="Agregar música",filetypes=[("Audio","*.flac *.mp3 *.wav *.ogg *.oga *.m4a *.aac *.aiff *.aif *.wma *.opus *.ape *.wv *.tta"),("Todos","*.*")]))
    def add_folder(self):
        folder=filedialog.askdirectory(title="Agregar carpeta de música")
        if folder:self._add_paths([folder])
    def _add_paths(self,paths):
        candidates=self._collect_audio_paths(paths); known={self._path_identity(x) for x in self.playlist}; count=0
        for path in candidates:
            key=self._path_identity(path)
            if key in known: continue
            self.playlist.append(path);known.add(key);count+=1
        self._refresh_playlist_box()
        if count:self._save_config();self.status_var.set(f"Agregadas {count} pistas · total {len(self.playlist)}.")
        return count
    def _playlist_external_drop(self,event):
        try: paths=self.root.tk.splitlist(event.data)
        except Exception: paths=[getattr(event,'data','')]
        self._add_paths(paths);return "break"
    def _playlist_drag_start(self,event):
        if not self.playlist:self._playlist_drag_index=None;return
        index=int(self.playlist_box.nearest(event.y))
        if 0<=index<len(self.playlist):self._playlist_drag_index=index;self._playlist_drag_path=self.playlist[index]
    def _playlist_drag_motion(self,event):
        source=self._playlist_drag_index
        if source is None or not self.playlist:return "break"
        target=max(0,min(int(self.playlist_box.nearest(event.y)),len(self.playlist)-1))
        if target!=source:
            self._move_playlist_item(source,target);self._playlist_drag_index=target;self.playlist_box.selection_clear(0,tk.END);self.playlist_box.selection_set(target);self.playlist_box.see(target)
        return "break"
    def _playlist_drag_end(self,_event=None):
        if self._playlist_drag_index is not None:self._save_config()
        self._playlist_drag_index=None;self._playlist_drag_path=""
    def _move_playlist_item(self,source,target):
        if source==target or not 0<=source<len(self.playlist):return
        target=max(0,min(target,len(self.playlist)-1));playing=self.playlist[self.current_index] if 0<=self.current_index<len(self.playlist) else "";item=self.playlist.pop(source);self.playlist.insert(target,item)
        if playing:
            try:self.current_index=self.playlist.index(playing)
            except ValueError:self.current_index=-1
        self._refresh_playlist_box()
    def move_selected_track(self,direction):
        sel=self.playlist_box.curselection()
        if not sel:return
        source=int(sel[0]);target=source+(-1 if direction<0 else 1)
        if not 0<=target<len(self.playlist):return
        self._move_playlist_item(source,target);self.playlist_box.selection_clear(0,tk.END);self.playlist_box.selection_set(target);self.playlist_box.see(target);self._save_config()
    def _refresh_playlist_box(self):
        if not hasattr(self,'playlist_box'):return
        self.playlist_box.delete(0,tk.END)
        for i,path in enumerate(self.playlist):self.playlist_box.insert(tk.END,("▶ " if i==self.current_index and self.engine.mode=="local" else "  ")+Path(path).name)
    def play_selected(self):
        sel=self.playlist_box.curselection();index=int(sel[0]) if sel else (self.current_index if self.current_index>=0 else (0 if self.playlist else -1))
        if index<0:self.add_files();return
        self.load_and_play(index)
    def load_and_play(self,index):
        if not 0<=index<len(self.playlist):return
        path=self.playlist[index];self.current_index=index;self.current_station=None;self._refresh_playlist_box();self.loading=True;self.status_var.set("Cargando y decodificando audio Hi‑Fi...");self._display_title=Path(path).name;self._display_info="Decodificando con FFmpeg..."
        def worker():
            try:self.ui_queue.put(("track_loaded",self.engine.load_file(path)))
            except Exception as exc:self.ui_queue.put(("error",str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    def _after_track_loaded(self,info):
        self.loading=False;self._display_title=info.display_name;meta=[]
        if info.codec_hint:meta.append(info.codec_hint)
        meta.append(f"{info.sample_rate:,} Hz".replace(",","."))
        if info.bit_depth:meta.append(info.bit_depth)
        meta.append(f"{info.channels} canales")
        if info.album:meta.append(info.album)
        self._display_info=" · ".join(meta)
        if info.is_stream:self.cassette.set_label(info.title,info.album or "Radio online");self.status_var.set("Radio online conectada.")
        else:self.cassette.set_label(info.display_name,info.album or ((info.codec_hint or "AUDIO")+" · SIDE A"));self.status_var.set("Reproduciendo.")
        self.engine.play()
        if self.ai_auto_on_track_change and not info.is_stream and self.nvidia_api_key:
            self.root.after(300,lambda:self.auto_ai_eq_current_track(run_now=True,quiet=True))
    def remove_selected(self):
        selected=sorted({int(x) for x in self.playlist_box.curselection()},reverse=True)
        if not selected:return
        playing=self.playlist[self.current_index] if 0<=self.current_index<len(self.playlist) else "";removed=False
        for i in selected:
            if 0<=i<len(self.playlist):removed|=self.playlist[i]==playing;self.playlist.pop(i)
        if removed:self.stop();self.current_index=-1
        elif playing:
            try:self.current_index=self.playlist.index(playing)
            except ValueError:self.current_index=-1
        self._refresh_playlist_box();self._save_config()
    def clear_playlist(self):
        if self.playlist and messagebox.askyesno("Limpiar playlist","¿Limpiar toda la playlist local?"):
            self.stop();self.playlist.clear();self.current_index=-1;self._refresh_playlist_box();self._save_config()
    def import_playlist(self):
        path=filedialog.askopenfilename(title="Importar playlist",filetypes=[("Playlist","*.m3u *.m3u8 *.json"),("Todos","*.*")])
        if not path:return
        base=Path(path).parent;candidates=[]
        try:
            if path.lower().endswith('.json'):
                data=json.loads(Path(path).read_text(encoding='utf-8'));items=data.get('tracks',data if isinstance(data,list) else []) if isinstance(data,(dict,list)) else []
                for item in items:
                    value=item.get('path') if isinstance(item,dict) else str(item)
                    if value:candidates.append(str((base/Path(value)) if not Path(value).is_absolute() else Path(value)))
            else:
                for line in Path(path).read_text(encoding='utf-8-sig',errors='replace').splitlines():
                    line=line.strip()
                    if line and not line.startswith('#'):candidates.append(str(Path(line) if Path(line).is_absolute() else base/line))
            self.status_var.set(f"Playlist importada · pistas nuevas: {self._add_paths(candidates)}.")
        except Exception as exc:messagebox.showerror("Importar playlist",str(exc))
    def export_playlist(self):
        path=filedialog.asksaveasfilename(title="Exportar playlist",defaultextension='.m3u8',filetypes=[("M3U8","*.m3u8"),("M3U","*.m3u"),("JSON","*.json")])
        if not path:return
        try:
            if path.lower().endswith('.json'):write_json_atomic(Path(path),{"app":APP_NAME,"version":APP_VERSION,"tracks":[{"path":x,"name":Path(x).name} for x in self.playlist]})
            else:
                lines=["#EXTM3U",f"#PLAYLIST:{APP_NAME}"]
                for item in self.playlist:lines.extend([f"#EXTINF:-1,{Path(item).stem}",item])
                Path(path).write_text("\n".join(lines),encoding='utf-8')
        except Exception as exc:messagebox.showerror("Exportar playlist",str(exc))

    # ------------------------------------------------------------------ radio
    def _radio_scope_data(self,scope):
        if scope=="world":return self.world_radios,self.world_radio_box,self.current_world_radio_index,self.world_radio_title_var,self.world_radio_genre_var,self.world_logo_label
        return self.radios,self.radio_box,self.current_radio_index,self.radio_title_var,self.radio_genre_var,self.logo_label
    def _set_radio_index(self,scope,index):
        if scope=="world":self.current_world_radio_index=index
        else:self.current_radio_index=index
    def _get_selected_radio(self,scope):
        radios,box,current,*_=self._radio_scope_data(scope);sel=box.curselection();index=int(sel[0]) if sel else current
        return (index,radios[index]) if 0<=index<len(radios) else (-1,None)
    def _refresh_radio_box(self):
        if not hasattr(self,'radio_box'):return
        self.radio_box.delete(0,tk.END)
        for i,x in enumerate(self.radios):self.radio_box.insert(tk.END,("▶ " if self.engine.mode=="radio" and self.current_radio_scope=="ar" and i==self.current_radio_index else "  ")+x.display_name())
        if self.radios:self.radio_box.selection_set(0);self._radio_selection_changed("ar")
    def _refresh_world_radio_box(self):
        if not hasattr(self,'world_radio_box'):return
        self.world_radio_box.delete(0,tk.END)
        for i,x in enumerate(self.world_radios):self.world_radio_box.insert(tk.END,("▶ " if self.engine.mode=="radio" and self.current_radio_scope=="world" and i==self.current_world_radio_index else "  ")+x.display_name(True))
        if self.world_radios:self.world_radio_box.selection_set(0);self._radio_selection_changed("world")
    def _radio_selection_changed(self,scope="ar"):
        radios,box,_idx,title,genre,logo=self._radio_scope_data(scope);sel=box.curselection()
        if not sel:return
        station=radios[int(sel[0])];title.set(station.name);details=[station.genre]
        if scope=="world":details.append(station.city or station.state or station.country)
        if station.codec:details.append(station.codec+(f" {station.bitrate}k" if station.bitrate else ""))
        genre.set(" · ".join(x for x in details if x));self._show_logo_for_station(station,logo)
    def _logo_key(self,station):return (station.station_uuid or f"{station.country_code}:{station.name}:{station.stream_url}").casefold()
    def _show_logo_for_station(self,station,label):
        key=self._logo_key(station)
        if key in self.logo_cache:label.configure(image=self.logo_cache[key]);label.image=self.logo_cache[key];return
        photo=ImageTk.PhotoImage(create_fallback_logo(station.name,128));self.logo_cache[key]=photo;label.configure(image=photo);label.image=photo;threading.Thread(target=self._load_logo_background,args=(station,),daemon=True).start()
    def _logo_file_for(self,station):
        folder=app_cache_dir()/"logos";folder.mkdir(exist_ok=True);digest=hashlib.sha1((station.name+station.logo_url+station.stream_url).encode('utf-8','ignore')).hexdigest()[:14];return folder/f"{safe_filename(station.name)}_{digest}.png"
    def _load_logo_background(self,station):
        try:
            url=station.logo_url
            if not url:
                match=self.browser.best_match(station,10);url=match.logo_url if match else ""
            if not url or not url.startswith(("http://","https://")):return
            path=self._logo_file_for(station)
            if not path.exists():
                response=requests.get(url,timeout=10,headers={"User-Agent":f"LQP/{APP_VERSION}"});response.raise_for_status()
                if len(response.content)>4*1024*1024:return
                path.write_bytes(response.content)
            image=Image.open(path).convert('RGBA');image.thumbnail((128,128),Image.LANCZOS);canvas=Image.new('RGBA',(128,128),'#050805');canvas.alpha_composite(image,((128-image.width)//2,(128-image.height)//2));self.ui_queue.put(("logo_image",(self._logo_key(station),canvas)))
        except Exception:return
    def _prefetch_visible_logos(self):
        for station in self.radios[:8]+self.world_radios[:8]:threading.Thread(target=self._load_logo_background,args=(station,),daemon=True).start()
    def refresh_logos(self,scope="ar"):
        radios,*_=self._radio_scope_data(scope)
        for station in radios:self.logo_cache.pop(self._logo_key(station),None)
        for station in radios[:12]:threading.Thread(target=self._load_logo_background,args=(station,),daemon=True).start()
    def open_selected_radio_homepage(self,scope="ar"):
        _,station=self._get_selected_radio(scope)
        if station and station.homepage:webbrowser.open(station.homepage)
    def play_selected_radio(self,scope="ar"):
        index,station=self._get_selected_radio(scope)
        if station is None:return
        self._set_radio_index(scope,index);self.current_radio_scope=scope;self.current_station=station;self.current_index=-1;self._refresh_radio_box();self._refresh_world_radio_box();radios,box,*_=self._radio_scope_data(scope);box.selection_clear(0,tk.END);box.selection_set(index);box.see(index);self._display_title=station.name;self._display_info=f"{station.genre} · {station.city or station.country} · Streaming online";self.status_var.set(f"Conectando radio: {station.name}...")
        try:self._after_track_loaded(self.engine.load_radio(station))
        except Exception as exc:messagebox.showerror("Radio online",str(exc))
    def test_selected_radio(self,scope="ar"):
        index,station=self._get_selected_radio(scope)
        if not station:return
        def worker():self.ui_queue.put(("stream_test_result",(scope,index,station.name,*self._test_stream(station.stream_url))))
        threading.Thread(target=worker,daemon=True).start()
    def _test_stream(self,url):
        if not FFMPEG_PATH:return False,"FFmpeg no disponible."
        code,out=_run_subprocess([str(FFMPEG_PATH),"-v","error","-nostdin","-user_agent",f"LQP/{APP_VERSION}","-rw_timeout","8000000","-reconnect","1","-reconnect_streamed","1","-i",url,"-t","4","-f","null","-"],timeout=14)
        return (True,"Stream OK.") if code==0 else (False,"El stream no respondió o cambió la URL."+("\n"+out.strip()[:400] if out.strip() else ""))
    def repair_selected_radio(self,scope="ar"):
        index,station=self._get_selected_radio(scope)
        if not station:return
        def worker():
            replacement=self.browser.best_match(station,25)
            if not replacement:self.ui_queue.put(("radio_repair_result",(scope,index,None,False,"No se encontró una coincidencia confiable.")));return
            ok,msg=self._test_stream(replacement.stream_url);self.ui_queue.put(("radio_repair_result",(scope,index,replacement,ok,msg)))
        threading.Thread(target=worker,daemon=True).start()
    def search_radios_online(self):
        query=self.radio_search_var.get().strip()
        if not query:return
        threading.Thread(target=lambda:self.ui_queue.put(("radio_results",("ar",self.browser.search_station(query,"AR","",30),False))),daemon=True).start()
    def search_world_radios(self):
        query=self.world_radio_search_var.get().strip();city=self.world_city_var.get();preset=WORLD_CITY_PRESETS.get(city,{})
        if not query:return
        def worker():
            results=self.browser.search_station(query,str(preset.get('country_code') or ''),str(preset.get('state') or ''),30)
            for x in results:x.city=city
            self.ui_queue.put(("radio_results",("world",results,False)))
        threading.Thread(target=worker,daemon=True).start()
    def load_top_argentina(self):threading.Thread(target=lambda:self.ui_queue.put(("radio_results",("ar",self.browser.top_argentina(60),False))),daemon=True).start()
    def refresh_argentina_radios(self,silent=False):
        original=list(self.radios)
        def worker():
            updated=list(original);changes=0
            for i,station in enumerate(original[:len(RADIO_PRESETS)]):
                rep=self.browser.best_match(station,20)
                if rep and rep.stream_url:rep.name=station.name;rep.genre=station.genre;rep.logo_query=station.logo_query;rep.source="preset-auto";updated[i]=rep;changes+=int(rep.stream_url!=station.stream_url)
            self.ui_queue.put(("radio_refresh_complete",(updated,changes,silent)))
        threading.Thread(target=worker,daemon=True).start()
    def load_world_city(self,silent=False):
        city=self.world_city_var.get()
        if city in WORLD_CITY_PRESETS:threading.Thread(target=lambda:self.ui_queue.put(("world_city_results",(city,self.browser.featured_city(city,25),silent))),daemon=True).start()
    def _merge_radios(self,scope,results,replace=False):
        target=self.world_radios if scope=="world" else self.radios
        if replace:target.clear()
        by_uuid={x.station_uuid:i for i,x in enumerate(target) if x.station_uuid};by_name={x.name.casefold():i for i,x in enumerate(target)};added=0
        for station in results:
            if not station.stream_url:continue
            index=by_uuid.get(station.station_uuid) if station.station_uuid else by_name.get(station.name.casefold())
            if index is not None:target[index]=station;continue
            target.append(station);added+=1;by_name[station.name.casefold()]=len(target)-1
        self._refresh_world_radio_box() if scope=="world" else self._refresh_radio_box();self._save_config();return added
    def add_manual_radio(self,scope="ar"):
        name=simpledialog.askstring("Agregar radio","Nombre:");url=simpledialog.askstring("Agregar radio","URL del stream:") if name else None
        if not url:return
        genre=simpledialog.askstring("Agregar radio","Género:") or "Radio Online";city=self.world_city_var.get() if scope=="world" else "";preset=WORLD_CITY_PRESETS.get(city,{})
        station=RadioStation(name=name,genre=genre,stream_url=url,logo_query=name,source="manual",country=str(preset.get('country') or 'Argentina'),country_code=str(preset.get('country_code') or 'AR'),city=city,state=str(preset.get('state') or ''))
        (self.world_radios if scope=="world" else self.radios).append(station);self._refresh_world_radio_box() if scope=="world" else self._refresh_radio_box();self._save_config()
    def remove_selected_radio(self,scope="ar"):
        index,station=self._get_selected_radio(scope)
        if not station or not messagebox.askyesno("Quitar radio",f"¿Quitar {station.name}?"):return
        (self.world_radios if scope=="world" else self.radios).pop(index);self._set_radio_index(scope,-1);self._refresh_world_radio_box() if scope=="world" else self._refresh_radio_box();self._save_config()
    def import_radios(self,scope="ar"):
        path=filedialog.askopenfilename(title="Importar radios",filetypes=[("Radios","*.json *.m3u *.m3u8"),("Todos","*.*")]);items=[]
        if not path:return
        try:
            if path.lower().endswith('.json'):
                data=json.loads(Path(path).read_text(encoding='utf-8'));rows=data.get('radios',data if isinstance(data,list) else []) if isinstance(data,(dict,list)) else []
                items=[x for x in (self._radio_from_config(row) for row in rows) if x]
            else:
                name="Radio importada"
                for line in Path(path).read_text(encoding='utf-8-sig',errors='replace').splitlines():
                    line=line.strip()
                    if line.startswith('#EXTINF'):name=line.split(',',1)[-1].strip() or name
                    elif line.startswith(('http://','https://')):items.append(RadioStation(name=name,genre='Importada',stream_url=line,source='import',city=self.world_city_var.get() if scope=='world' else ''))
            self._merge_radios(scope,items)
        except Exception as exc:messagebox.showerror("Importar radios",str(exc))
    def export_radios(self,scope="ar"):
        path=filedialog.asksaveasfilename(title="Exportar radios",defaultextension='.json',filetypes=[("JSON","*.json"),("M3U8","*.m3u8")]);radios=self.world_radios if scope=="world" else self.radios
        if not path:return
        if path.lower().endswith('.json'):write_json_atomic(Path(path),{"app":APP_NAME,"version":APP_VERSION,"radios":[asdict(x) for x in radios]})
        else:
            lines=['#EXTM3U']
            for x in radios:lines.extend([f"#EXTINF:-1,{x.name}",x.stream_url])
            Path(path).write_text("\n".join(lines),encoding='utf-8')

    # -------------------------------------------------------------- recording
    def toggle_recording(self):
        if self.recorder.active:
            path=self.recorder.stop()
            if path:messagebox.showinfo("REC Air-Check",f"Grabación guardada en:\n{path}")
            return
        if self.engine.mode!="radio" or self.current_station is None:messagebox.showinfo("REC Air-Check","Reproducí una radio y apretá REC.");return
        try:self.recorder.start(self.current_station)
        except Exception as exc:messagebox.showerror("REC",str(exc))
    def pause(self):self.engine.pause();self.status_var.set("Pausa.")
    def stop(self):self.engine.stop(close_stream=False);self.status_var.set("Stop.");self.time_var.set("00:00 / 00:00");self._refresh_playlist_box();self._refresh_radio_box();self._refresh_world_radio_box()
    def toggle_play_pause(self):
        if self.loading:return
        if self.engine.playing:self.pause();return
        if self.engine.mode=="idle":
            if self.playlist:self.load_and_play(0)
            elif self.radios:self.play_selected_radio("ar")
        else:self.engine.play()
    def _step_radio(self,direction):
        radios,box,current,*_=self._radio_scope_data(self.current_radio_scope)
        if not radios:return
        index=((current if current>=0 else 0)+direction)%len(radios);box.selection_clear(0,tk.END);box.selection_set(index);box.see(index);self.play_selected_radio(self.current_radio_scope)
    def next_track(self):
        if self.engine.mode=="radio":self._step_radio(1);return
        if not self.playlist:return
        if self.shuffle_var.get() and len(self.playlist)>1:index=random.choice([i for i in range(len(self.playlist)) if i!=self.current_index])
        else:
            index=self.current_index+1
            if index>=len(self.playlist):
                if self.repeat_var.get():index=0
                else:self.stop();return
        self.load_and_play(index)
    def prev_track(self):
        if self.engine.mode=="radio":self._step_radio(-1);return
        if not self.playlist:return
        index=self.current_index-1
        if index<0:index=len(self.playlist)-1 if self.repeat_var.get() else 0
        self.load_and_play(index)

    def _track_finished_from_engine(self) -> None:
        self.ui_queue.put(("track_finished", None))

    def _handle_track_finished(self) -> None:
        if self.engine.mode == "local":
            self.next_track()

    # ------------------------------------------------------------------- seek
    def _seek_press(self) -> None:
        self.seeking = True

    def _seek_release(self, _event=None) -> None:
        duration = self.engine.get_duration_seconds()
        if duration > 0:
            target = float(self.seek_var.get()) / 1000.0 * duration
            self.engine.seek_seconds(target)
        self.seeking = False

    def seek_relative(self, delta_seconds: float) -> None:
        if self.engine.mode != "local":
            return
        self.engine.seek_seconds(self.engine.get_position_seconds() + delta_seconds)

    # ------------------------------------------------------------------ close
    def _on_close(self) -> None:
        if self._tick_after_id:
            try: self.root.after_cancel(self._tick_after_id)
            except Exception: pass
            self._tick_after_id = None
        try:
            if self.recorder.active:
                path = self.recorder.stop()
                if path:
                    print(f"[LQP HiFi] Grabación guardada: {path}")
        except Exception:
            pass
        self._save_config()
        self.engine.close()
        self.root.destroy()

    # Estado del display (los setters de arriba los actualizan).
    _display_title: str = "LQP HiFi RACK PLAYER"
    _display_info: str = "Pipeline float32 · FFmpeg DSP · Spectrum LED · REC Air-Check"


def main() -> None:
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    VintageHiFiApp(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        print(err)
        try:
            messagebox.showerror("LQP HiFi Rack Player", err)
        except Exception:
            pass
