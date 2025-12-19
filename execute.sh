
# generar virtual enviroment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 export.py
python3 main.py


PORT=8000
fuser -k $PORT/tcp 2>/dev/null


cd webPage/src
python3 -m http.server $PORT &

SERVER_PID=$!




cleanup() {
    echo "Deteniendo servidor..."
    kill $SERVER_PID
    exit 0
}

trap cleanup INT


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


wait $SERVER_PID
