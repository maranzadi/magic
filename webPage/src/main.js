// let cardsDB = {}; // Para guardar los datos de cards.json

// Primero cargamos las cartas
function baraja(){
  fetch("./decks/mainFile.json")
    .then(res => res.json())
    .then(deckData => {
      renderDeck(deckData);
    })
    .catch(e => console.error("Error cargando el JSON:", e));
}



function renderDeck(deckData) {
  const commanderNode = document.getElementById('commander');
  const conjuntoNode = document.getElementById('conjunto');
  const otrosNode = document.getElementById('noIncluidas');
  // const ilegales = document.getElementById('ilegales');



  // Renderizamos el comandante
  const commander = deckData.commander;

  
  commanderNode.innerHTML = imagen(commander) ;

  // Renderizamos el resto del deck
    deckData.deck
    .slice(1)
    .forEach(c => {
    conjuntoNode.innerHTML += imagen(c) ;
  });


  deckData.other_cards
    .forEach(c => {
    otrosNode.innerHTML += imagen(c) ;
  });

  // ilegales.other_cards
  //   .forEach(c => {
  //   otrosNode.innerHTML += imagen(c) ;
  // });
}


function imagen(c){
    valor= `
      <div class='bg-gray-600 p-5 rounded-md flex flex-col items-center justify-center'>
        <img src='${c.image_url || ""}' 
             class='h-90 rounded-lg hover:scale-110 transition delay-150 duration-300 ease-in-out'>
        <h1 class='mt-1.5 text-center text-amber-50'>
          ${c.name} - Score: ${c.score} ${c.included ? "(Incluida)" : "(No incluida)"}
        </h1>
      </div>
    `;

    return valor
}


//          PARA VER LAS ESTADISTICAS INTERNAS
//          <pre class='text-white'>${JSON.stringify(c.score_breakdown, null, 2)}</pre>
//          <pre class='text-white'>${JSON.stringify(commander.score_breakdown, null, 2)}</pre>
