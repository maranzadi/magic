const lista = [];

fetch("./decks/Toph, the First Metalbender.txt")
  .then(res => res.text())
  .then(text => {
    // Separar por saltos de línea
    const lineas = text.split("\n").filter(l => l.trim() !== ""); 
    // Agregar cada línea al array
    lista.push(...lineas); 
    //console.log(lista); // ✔ Cada línea es un índice
})
.catch(e => console.error(e));

//console.log(lista)




for (let i = 0; i < lista.length; i++) {
  console.log(lista[i])
}