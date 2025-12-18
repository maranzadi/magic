const lista = [];
let jsonTotal = "";

fetch("./decks/Toph, the First Metalbender.txt")
  .then(res => res.text())
  .then(text => {
    // Separar por saltos de línea
    const lineas = text.split("\n").filter(l => l.trim() !== ""); 
    // Agregar cada línea al array
    lista.push(...lineas); 
    //console.log(lista);
    loadJson()
    
})
.catch(e => console.error(e));

//console.log(lista)

function loadJson(){
    imprimir()
    
    fetch("./cards.json")
    .then(res => res.json())
    .then(data => {
        //console.log(data);
        jsonTotal = data;
        imprimir()
    })
    .catch(e => console.error(e));

}


function imprimir(){
    //console.log(jsonTotal)
    for (let i = 0; i < lista.length; i++) {
        //console.log(lista[i])
    }
}
