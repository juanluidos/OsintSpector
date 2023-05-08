var datosComunidad = datosComunidades
console.log(datosComunidad[1])
var tableColumns = [
    {title: "Color", field: "color", hozAlign:"center", headerFilter: "input"},
    {title: "Densidad", field: "densidad", hozAlign:"center", headerSort:true, sorter:"number"},
    {title: "Excentricidad", field: "excentricidad", hozAlign:"center", headerSort:true, sorter:"number"},
    {title: "Centro", field: "centro", hozAlign:"center", headerSort:false, responsive:3},
    {title: "Grado medio", field: "grado_medio", hozAlign:"center", headerSort:true, sorter:"number"},
    {title: "Clustering medio", field: "clustering_medio", hozAlign:"center", headerSort:true, sorter:"number"},
    {title: "Cohesión", field: "cohesion", headerSort:true, hozAlign:"center", sorter:"number"},
    {title: "Centralidad de intermediación", field: "betweenness_comunidad", hozAlign:"center", headerSort:true, sorter:"number", responsive:2},
];
var tableData = [];
for (var i = 0; i < datosComunidad[1].length; i++) {
    console.log(datosComunidad[1][i])
    var item = datosComunidad[1][i];
    tableData.push({
        color: item.color,
        densidad: item.densidad,
        excentricidad: item.excentricidad,
        centro: JSON.stringify(item.centro).replace(/[\[\]"]/g, '').replace(/,/g, ', '),
        grado_medio: item.grado_medio,
        clustering_medio: item.clustering_medio,
        cohesion: item.cohesion,
        betweenness_comunidad: item.betweenness_comunidad && Object.keys(item.betweenness_comunidad).length !== 0 ? JSON.stringify(item.betweenness_comunidad).replace(/[{}"]/g, '').replace(/,/g, ', ').replace(/:/g, ': ') : "No existe dicho valor para esta comunidad"
    });
}

var table = new Tabulator("#tablaComunidad", {
    data: tableData,
    autoResize: true,
    responsiveLayout:"collapse",
    layout: "fitDataFill",
    groupBy: function(data){
        //data - the data object for the row being grouped
        return data.color; //groups by location
    },
    groupStartOpen: false,
    columns: tableColumns,
    placeholder:"No hay datos disponibles sobre las comunidades, ya que no existen para este usuario",
});

