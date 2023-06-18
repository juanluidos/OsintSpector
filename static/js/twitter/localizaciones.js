listaLocalizaciones = listaLocalizaciones
var tableColumns = [
    {title: "Fecha publicación", field: "datetime", hozAlign:"center", formatter: "plaintext", headerFilter: "input", headerFilterPlaceholder:"Filtro fechas",
    sorter: function(a, b, aRow, bRow, column, dir, sorterParams) {
        // Convertir la cadena de fecha en un objeto de fecha
        var dateA = new Date(a);
        var dateB = new Date(b);
        
        // Crear un valor numérico basado en el formato deseado
        var numA = dateA.getFullYear() * 10000000000 + (dateA.getMonth()+1) * 100000000 + dateA.getDate() * 1000000 + dateA.getHours() * 10000 + dateA.getMinutes() * 100 + dateA.getSeconds();
        var numB = dateB.getFullYear() * 10000000000 + (dateB.getMonth()+1) * 100000000 + dateB.getDate() * 1000000 + dateB.getHours() * 10000 + dateB.getMinutes() * 100 + dateB.getSeconds();
        
        // Devolver el resultado de la comparación
        return numA - numB;
    }},
    {title: "URL Tweet", field: "url", vertAlign: "top", formatter: "link", headerSort:false, formatterParams: {labelField: "url", target: "_blank"}}
];

var tableData = [];
var locationsList = []
for (var i = 0; i < listaLocalizaciones.length; i++) {
    var item = listaLocalizaciones[i];
    locationsList.push(item.location)
    for (var j = 0; j < item.datetime.length; j++) {
        var time = item.datetime[j].slice(5)
        tableData.push({
            location: item.location,
            datetime: time,
            maps: item.maps,
            url: item.url[j],
        });
    }
}

var table = new Tabulator("#tablaLocalizaciones", {
    data: tableData,
    layout: "fitDataStretch",
    columns: tableColumns,
    placeholder:"No hay localizaciones disponibles en los tweets del usuario",
    groupBy: function(data){
        //data - the data object for the row being grouped
        return data.location; //groups by location
    },
    groupHeader:function(value, count, data, group){
        //value - the value all members of this group share
        //count - the number of rows in this group
        //data - an array of all the row data objects in this group
        //group - the group component for the group
    
        return value  + " - " + "<a href='" + data[0].maps +"'target='_blank'>Link localización</a>" +"<span style='color:#d00; margin-left:10px;'>(" + count + " item)</span>";
    }
});
//MAPA

//Timeout porq no da tiempo al DOM q se cargue por completo antes de que el script corra    
setTimeout(() => {
// Eliminamos las ubicaciones repetidas
var uniqueLocations = [...new Set(locationsList)];

// Generamos una lista vacía para almacenar los resultados
var resultsList = [];

// Obtenemos la clave de la API desde una variable de entorno

// Iteramos sobre cada ubicación única
uniqueLocations.forEach(function(location) {
  // Creamos la URL para hacer la petición a la API de Google Maps
  var url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + encodeURIComponent(location) + "&key=" + "NotToday";

  // Hacemos la petición a la API
  fetch(url)
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    // Obtenemos la latitud y longitud de la respuesta de la API
    var lat = data.results[0].geometry.location.lat;
    var lng = data.results[0].geometry.location.lng;

    // Creamos un objeto con la ubicación, latitud y longitud
    var result = {
      "location": location,
      "lat": lat,
      "lng": lng
    };

    // Agregamos el objeto a la lista de resultados
    resultsList.push(result);

    // Si ya hemos terminado de procesar todas las ubicaciones, imprimimos los resultados
    if (resultsList.length === uniqueLocations.length) {

      var mymap = L.map('mapid').setView([0, 0], 2);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { // Agrega una capa de mapa base de OpenStreetMap
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(mymap);

      resultsList.forEach(function(result) {
        var lat = result.lat;
        var lon = result.lng;
        L.marker([lat, lon]).addTo(mymap).bindPopup(result.location); // Crea un marcador en la ubicación encontrada y muestra la ubicación en el popup
      });
    }
  });
});

  
  }, 1000);
  


