#!/bin/bash
cd /home/site/wwwroot/backend
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
