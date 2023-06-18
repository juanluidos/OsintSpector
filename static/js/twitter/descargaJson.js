var user = user
var emotions = emotions
var listaTopTweets = listaTopTweets
var lista_tuplas = lista_tuplas
var grafoComunidades = grafoComunidades
var datosComunidades = datosComunidades
var listaLocalizaciones = listaLocalizaciones
var objetoDatos = {};



var conteoEmociones = {};

for (var key in emotions) {
  var emocion = emotions[key];
  if (conteoEmociones.hasOwnProperty(emocion)) {
    conteoEmociones[emocion]++;
  } else {
    conteoEmociones[emocion] = 1;
  }
}



objetoDatos.user = user;
objetoDatos.conteoEmociones = conteoEmociones;
objetoDatos.topEmocionesPorSentimiento = listaTopTweets;
objetoDatos.topInteracciones = lista_tuplas;
objetoDatos.datosComunidades = datosComunidades;
objetoDatos.grafoComunidades = grafoComunidades;
objetoDatos.listaLocalizaciones = listaLocalizaciones;


var jsonString = JSON.stringify(objetoDatos);
var botonDescargar = document.getElementById('botonDescargar');
botonDescargar.addEventListener('click', function() {
  var blob = new Blob([jsonString], { type: 'application/json' });
  var url = URL.createObjectURL(blob);

  // Asigna el objeto URL al enlace de descarga
  botonDescargar.setAttribute('href', url);

  // Remueve el enlace del documento después de un breve retraso
  setTimeout(function() {
    URL.revokeObjectURL(url);
  }, 100);
});