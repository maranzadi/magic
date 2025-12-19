let cardsDB = {}; // Para guardar los datos de cards.json

// Primero cargamos las cartas
fetch("./cards.json")
  .then(res => res.json())
  .then(data => {
    cardsDB = data; // Guardamos los datos de todas las cartas
    return fetch("./decks/Toph, the First Metalbender.json");
  })
  .then(res => res.json())
  .then(deckData => {
    renderDeck(deckData);
  })
  .catch(e => console.error("Error cargando el JSON:", e));

function renderDeck(deckData) {
  const commanderNode = document.getElementById('commander');
  const conjuntoNode = document.getElementById('conjunto');

  // Renderizamos el comandante
  const commander = deckData.commander;
  const commanderCard = cardsDB[commander.id] || {};
  
  commanderNode.innerHTML = `
    <div class='bg-gray-600 p-5 rounded-md'>
      <img src='${commanderCard.image_url || ""}' 
           class='h-90 w-auto rounded-lg hover:scale-110 transition delay-150 duration-300 ease-in-out'>
      <h1 class='mt-1.5 text-center text-amber-50'>
        ${commander.name} - Score: ${commander.score}
      </h1>
      
    </div>
  `;

  // Renderizamos el resto del deck
  deckData.deck.slice(1).forEach(c => {
    const carta = cardsDB[c.id] || {};
    conjuntoNode.innerHTML += `
      <div class='bg-gray-600 p-5 rounded-md'>
        <img src='${carta.image_url || ""}' 
             class='h-90 w-auto rounded-lg hover:scale-110 transition delay-150 duration-300 ease-in-out'>
        <h1 class='mt-1.5 text-center text-amber-50'>
          ${c.name} - Score: ${c.score} ${c.included ? "(Incluida)" : "(No incluida)"}
        </h1>
      </div>
    `;
  });
}

//          PARA VER LAS ESTADISTICAS INTERNAS
//          <pre class='text-white'>${JSON.stringify(c.score_breakdown, null, 2)}</pre>
//          <pre class='text-white'>${JSON.stringify(commander.score_breakdown, null, 2)}</pre>
