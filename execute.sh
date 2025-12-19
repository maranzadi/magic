
# generar virtual enviroment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 export.py
python3 main.py

cd webPage/src
python3 -m http.server 8000 &

SERVER_PID=$!
sleep 1
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8000
else
    echo "Sistema operativo no soportado para abrir automáticamente el navegador."
fi
