@echo off
title 1stop Certificate Verification & QR Code App
cd /d "%~dp0"
echo =====================================================================
echo  1stop Certificate Verification and QR Code Traceback Web Application
echo =====================================================================
echo.
echo Starting Streamlit server...
echo Local Access:   http://localhost:8501
echo Mobile/Network: http://%COMPUTERNAME%:8501
echo.
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
