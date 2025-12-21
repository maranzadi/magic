#!/bin/sh

toph="Toph_the_First_Metalbender.json"
donde="webPage/src/decks"
archivo="$donde/$toph"

# Comenzar bisect
git bisect start
git bisect bad
git bisect good 68fb76e63375ccbebab7fc267ec4870711090003

encontrado=0

while [ "$encontrado" -eq 0 ]; do

  # Mostrar commit actual
  echo "=============================="
  echo "Probando commit:"
  git log -1 --pretty=format:"%h %ad %an %s" --date=short

  # Limpiar carpeta si quieres
  rm -rf "$donde"

  # Ejecutar tu código
  python3 export.py > /dev/null 2>&1
  python3 main.py > /dev/null 2>&1

  # Comprobar si el archivo existe
  if [ -f "$archivo" ]; then
    echo "Resultado: GOOD (archivo existe)"
    git bisect good
  else
    echo "Resultado: BAD (archivo NO existe)"
    git bisect bad
    encontrado=1   # Marcamos que encontramos el commit malo
    echo "¡Primer commit malo encontrado!"
  fi

done

# Terminar bisect
git bisect reset
