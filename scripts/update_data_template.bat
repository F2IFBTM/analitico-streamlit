@echo off
REM ====== TEMPLATE AGGIORNAMENTO DATI ======
REM Modifica le variabili sorgente qui sotto
set SRC_DB_EL=C:\path\to\Elasticita_recap.db
set SRC_DB_AG=C:\path\to\Aggregati.db
set SRC_PNG_DIR=C:\path\to\Previsioni

copy /Y "%SRC_DB_EL%" Elasticita\Elasticita_recap.db
copy /Y "%SRC_DB_AG%" Aggregati\Aggregati.db
xcopy /Y /I "%SRC_PNG_DIR%\*.png" Previsioni\

git add Elasticita Aggregati Previsioni
git commit -m "Aggiornamento dati"
git push
