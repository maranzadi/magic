#!/bin/sh

# Variables
toph="Toph_the_First_Metalbender.json"
donde="webPage/src/decks"
archivo="$donde/$toph"
rm -rf "webPage/src/decks"

# Mostrar commit actual
echo "=============================="
echo "Probando commit:"
git log -1 --pretty=format:"%h %ad %an %s" --date=short

# Ejecutar tu script que genera el archivo
echo "Ejecutando execute.sh..."
python3 export.py > /dev/null
python3 main.py > /dev/null

rm -rf "webPage/src/"


# Comprobar si el archivo existe
if [ -f "$archivo" ]; then
  echo "Resultado: GOOD (archivo existe)"
  git bisect good
else
  echo "Resultado: BAD (archivo NO existe)"
  git bisect bad
fi
