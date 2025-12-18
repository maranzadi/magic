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
    for (const id in jsonTotal) {
        if (jsonTotal.hasOwnProperty(id)) {
            if(lista.includes(id)){
                const carta = jsonTotal[id];
                console.log("ID:", id);
                console.log("------");
                
                var node = document.getElementById('conjunto');
                node.innerHTML += `
                    <div class='bg-gray-600 p-5 rounded-md'>
                        <img src='${carta.image_url}' 
                            class='h-90 w-auto rounded-lg hover:scale-110 transition delay-150 duration-300 ease-in-out'>
                        <h1 class='mt-1.5 text-center text-amber-50'>${carta.name}</h1>
                    </div>
                    `;

                
            }
            
        }
    }
}
