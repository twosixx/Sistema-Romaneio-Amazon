@echo off
set "APPDIR=%~dp0"
pushd "%APPDIR%"
if exist "C:\Users\EDM-VITOR\AppData\Local\Programs\Python\Python312\python.exe" (
  start "Romaneio Amazon" /min "C:\Users\EDM-VITOR\AppData\Local\Programs\Python\Python312\python.exe" "%APPDIR%server.py"
) else (
  start "Romaneio Amazon" /min python "%APPDIR%server.py"
)
popd
