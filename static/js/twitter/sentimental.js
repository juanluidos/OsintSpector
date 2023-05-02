// Contar la cantidad de cada emoción en la lista
var count = {};
var emotions = emotions
var listaTopTweets = listaTopTweets
for (var i = 0; i < emotions.length; i++) {
    var emotion = emotions[i];
    count[emotion] = (count[emotion] || 0) + 1;
}

// Crear un array con los valores de conteo
//Primero creamos la estructura de datos vacía

var data = {
    labels: [],
    datasets: [{
        data: [],
        backgroundColor: []
    }]
};

var backgroundColors = [
'rgba(255, 99, 132, 0.7)',
'rgba(54, 162, 235, 0.7)',
'rgba(255, 206, 86, 0.7)',
'rgba(75, 192, 192, 0.7)',
'rgba(153, 102, 255, 0.7)',
'rgba(255, 159, 64, 0.7)',
'rgba(255, 0, 0, 0.7)',
'rgba(0, 0, 255, 0.7)',
'rgba(0, 255, 0, 0.7)',
'rgba(128, 128, 128, 0.7)'
]

var colorMap = {
    'anger': 'rgba(255, 99, 132, 0.7)',
    'joy': 'rgba(75, 192, 192, 0.7)',
    'sadness': 'rgba(54, 162, 235, 0.7)',
    'fear': 'rgba(215, 215, 215, 0.7)'
};

for (var emotion in count) {
    if (count.hasOwnProperty(emotion)) {
        data.labels.push(emotion);
        data.datasets[0].data.push(count[emotion]);
        data.datasets[0].backgroundColor.push(colorMap[emotion]);
    }
}

var total = data.datasets[0].data.reduce(function(a, b) { return a + b; }, 0);

//Opciones
var options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                boxWidth: 15,
                fontSize: 12,
                fontColor: 'black',
                usePointStyle: true,
            }
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    var index = context.dataIndex;
                    var value = context.dataset.data[index];
                    var label = context.label || '';
                    var percentage = Math.round(value / total * 100);
                    return label + ' ' + value + ' (' + percentage + '%)';
                }
            }
        }
    }
};

// Crear el gráfico y mostrarlo en el canvas con el ID 'chart'
var ctx = document.getElementById('chart').getContext('2d');
var chart = new Chart(ctx, {
    type: 'pie',
    data: data,
    options: options
});

//Hacemos responsive el grafico
var canvas = document.getElementById('chart');
var heightRatio = 1.5;
canvas.height = canvas.width * heightRatio;