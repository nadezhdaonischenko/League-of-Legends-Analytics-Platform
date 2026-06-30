@echo off

set PYTHONIOENCODING=utf-8

cd /d "C:\...\Project_LOL"

echo ============================= >> pipeline.log
echo %date% %time% >> pipeline.log

echo Запуск полного ETL-пайплайна... >> pipeline.log
"C:\ProgramData\anaconda3\python.exe" -u main.py --stage pipeline >> pipeline.log 2>&1

echo Выполнение завершено. >> pipeline.log
