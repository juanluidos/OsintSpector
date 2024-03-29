// Obtener la lista de tuplas desde Flask
var lista_tuplas = lista_tuplas
var user = user
for (let i = 0; i < lista_tuplas.length; i++) {
    if (lista_tuplas[i][0] === user) {
        lista_tuplas.splice(i, 1);
        i--;
    }
    }
// Resto del código para crear el grafo, como se mostró anteriormente

//Opciones del grafo
var options = {
    nodes: {
    shape: 'circle',
    borderWidth: 1,
    },
    physics: {
    enabled: false
    }
};

// Crear un nuevo grafo
var grafo = new vis.Network(
    document.getElementById('grafo'),
    {nodes: [], edges: []},
    options
);

// Agregar el nodo central fijo
var nodos = new vis.DataSet([{id: user, label: user,x: 0, y: 0, fixed:true}]); //Nodo central innamovible

// Agregar los primeros 10 nodos en un círculo alrededor del nodo central
var angulo = 2 * Math.PI / 10;
for (var i = 1; i <= 10; i++) {
    if(lista_tuplas.length >= i){
        var x = Math.cos(i * angulo) * 150;
        var y = Math.sin(i * angulo) * 150;
        var nodo = {id: lista_tuplas[i-1][0], label: lista_tuplas[i-1][0], x: x, y: y,interacciones: "Hola"
        };
        nodos.add(nodo);
    }
    else{
        break
    }
}

// Agregar los siguientes 20 nodos en un círculo exterior alrededor del círculo interior
var angulo2 = 1 * Math.PI / 10;
for (var i = 11; i <= 30; i++) {
    if(lista_tuplas.length >= i){
        var x = Math.cos(i * angulo2) * 300;
        var y = Math.sin(i * angulo2) * 300;
        var nodo = {id: lista_tuplas[i-1][0], label: lista_tuplas[i-1][0], x: x, y: y, interacciones: "Hola"// 
        };
        nodos.add(nodo);
    }
    else{
        break
    }
}

// Agregar las aristas desde la lista de tuplas
var aristas = [];
for (var i = 0; i < lista_tuplas.length; i++) {
    var tupla = lista_tuplas[i];
    var arista = {from: user, to: tupla[0], value: tupla[1]};
    aristas.push(arista);
    var aristasDataSet = new vis.DataSet(aristas)
}

// Cambiar los tamaños de la fuente antes de actualizar el grado con los nuevos nodos
nodos.forEach(function (node) {
    var label = node.label || "";
    var fontSize = Math.max(Math.min(14, 150 / label.length), 10); //cambia el tamaño de la fuente del texto dependiendo de la cantidad de texto del nodo. Minmo 10 maximo 14
    node.font = {size: fontSize, color: '#000000', autoResize: true};
    node.size = 16
    node.color = {highlight:'#727272', inherit: false, opacity:1.0}
});

    // Crear el elemento del popup
    var popup = document.createElement('div');
    popup.style.position = 'absolute';
    popup.style.display = 'none';
    popup.style.zIndex = '1000';
    popup.style.backgroundColor = '#ffffff';
    popup.style.border = '1px solid #ddd';
    popup.style.borderRadius = '45%';
    popup.style.padding = '10px';
    popup.style.textAlign = "center"

    // Agregar el manejador de eventos de clic
    grafo.addEventListener('click', function(params) {
    if ((params.nodes.length > 0 && (params.nodes[0] != user))) {
        // Obtener las coordenadas del evento de clic
        var x = params.event.srcEvent.pageX;
        var y = params.event.srcEvent.pageY;
        var nombreUsuario = params.nodes
        var linkUsuario = "https://twitter.com/" + nombreUsuario

        // Actualizar la posición del popup y hacerlo visible
        popup.style.left = x-30 + 'px';
        popup.style.top = y-30 +'px';
        popup.style.display = 'block';
        
        // Crear el enlace del popup y establecer el destino a Twitter
        var enlace = document.createElement('a');
        enlace.setAttribute('href', linkUsuario);
        enlace.textContent = 'Perfil de Twitter';
        enlace.style.fontWeight = "bold"
        enlace.setAttribute("target", "_blank")
        popup.innerHTML = nombreUsuario + '<br>' + 'Nº Interacciones:'+ aristasDataSet.get(params.edges[0]).value +'<br>'; // nº interacciones que ha tenido el usuario con este nodo
        popup.appendChild(enlace);

    } else {
        // Ocultar el popup si no se hizo clic en un nodo o arista
        popup.style.display = 'none';
    }
    });

    // Agregar el elemento del popup al contenedor de la red
    document.getElementById('grafo').appendChild(popup);

// Actualizar el grafo con los nodos y las aristas
grafo.setData({nodes: nodos, edges: aristas});