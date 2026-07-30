@echo off
setlocal
cd /d "%~dp0"
py -3 src\lqp_hifi_rack_player.py
if errorlevel 1 (
  echo.
  echo LQP HiFi Rack Player could not start.
  echo Check docs\es\MANUAL_USUARIO.md for installation help.
  pause
)
