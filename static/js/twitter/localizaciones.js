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
for (var i = 0; i < listaLocalizaciones.length; i++) {
    var item = listaLocalizaciones[i];
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