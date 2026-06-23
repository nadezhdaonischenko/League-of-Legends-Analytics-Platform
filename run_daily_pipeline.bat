@echo off

:: UTF-8 для корректного вывода
set PYTHONIOENCODING=utf-8

:: Переход в папку проекта
cd /d "C:\Users\dima_\Desktop\Project_LOL"

echo ============================= >> pipeline.log
echo %date% %time% >> pipeline.log

echo Запуск EXTRACT... >> pipeline.log
"C:\ProgramData\anaconda3\python.exe" -u main.py >> pipeline.log 2>&1

echo Запуск TRANSFORM + LOAD... >> pipeline.log
"C:\ProgramData\anaconda3\python.exe" -u run_transform_load.py >> pipeline.log 2>&1

echo Запуск EDA... >> pipeline.log
"C:\ProgramData\anaconda3\python.exe" -u EDA.py >> pipeline.log 2>&1

echo Запуск DASHBOARD ETL... >> pipeline.log
"C:\ProgramData\anaconda3\python.exe" -u dashboard_etl.py >> pipeline.log 2>&1

echo Выполнение завершено. >> pipeline.log