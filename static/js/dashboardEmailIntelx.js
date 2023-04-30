Apex.grid = {
  show: true,
  borderColor: '#90A4AE',
    padding: {
      right: 0,
      left: 0
    }
  }
  
  Apex.dataLabels = {
    enabled: false
  }
  // the default colorPalette for this dashboard
  //var colorPalette = ['#01BFD6', '#5564BE', '#F7A600', '#EDCD24', '#F74F58'];
  var colorPalette = ['#264653','#2A9D8F',  '#E9C46A', '#F4A261', '#E76F51']
    
  const clavesFechaEmail = [];
  const valoresFechasEmail = [];

  for (const clave in diccionarioFechasEmail) {
    clavesFechaEmail.push(clave);
    valoresFechasEmail.push(diccionarioFechasEmail[clave]);
  }

  var optionsBarHorizontal = {
        series: [{
        name: "Veces filtrado en este año",
        data: valoresFechasEmail
        }],
            chart: {
            type: 'bar',
            height: 380,
            width: '100%',
        },
        plotOptions: {
            bar: {
            borderRadius: 4,
            horizontal: true,
            }
        },
        dataLabels: {
            enabled: true
        },
        xaxis: {
            categories: clavesFechaEmail,
        },
        title: {
            text: 'Años y veces que aparecío el email filtrado',
            align: 'left',
            style: {
            fontSize: '15px'
            }
        },
        colors: ['#E76F51']
    };

  var chartBarHorizontal = new ApexCharts(document.querySelector('#barHorizontalIntelxEmail'), optionsBarHorizontal);


  const clavesTipoEmail = [];
  const valoresTipoEmail = [];

  for (const clave in diccionarioTipoEmail) {
      clavesTipoEmail.push(clave);
      valoresTipoEmail.push(diccionarioTipoEmail[clave]);
  }
  var optionDonut = {
    chart: {
        type: 'donut',
        width: '100%',
        height: 380
    },
    dataLabels: {
      enabled: false,
    },
    plotOptions: {
      pie: {
        customScale: 0.8,
        donut: {
          size: '75%',
        },
        offsetY: 20,
      },
      stroke: {
        colors: undefined
      }
    },
    colors: colorPalette,
    title: {
      text: ' Tipos de archivos donde apareció filtrado el email',
      style: {
        fontSize: '15px'
      }
    },
    series: valoresTipoEmail,
    labels: clavesTipoEmail,
    legend: {
      position: 'left',
      offsetY: 80
    }
  }

  var donut = new ApexCharts(document.querySelector("#donutIntelxEmail"), optionDonut)

  // ordenar diccionario
  var diccionarioTamanyoOrdenado = Object.keys(diccionarioTamanyoEmail).map(function(key) {
    return [key, diccionarioTamanyoEmail[key]];
  });
  diccionarioTamanyoOrdenado.sort(function(first, second) {
    return second[1] - first[1];
  });

  const clavesTamanyoEmail = []
  const valoresTamanyoEmail = []

  for (let i = 0; i < diccionarioTamanyoOrdenado.length; i++) {
    clavesTamanyoEmail.push(diccionarioTamanyoOrdenado[i][0]);
    valoresTamanyoEmail.push(diccionarioTamanyoOrdenado[i][1]);
  }

  var optionsBarVertical = {
    series: [{
    name: "Tamaño del archivo",
    data:  valoresTamanyoEmail
    }],
        chart: {
        type: 'bar',
        height: 380,
        width: '100%',
    },
    plotOptions: {
        bar: {
        borderRadius: 4,
        horizontal: false,
        }
    },
    dataLabels: {
        enabled: false
    },
    xaxis: {
        categories: clavesTamanyoEmail,
    },
    title: {
        text: 'Tamaño de los archivos donde apareció filtrado el email de mayor a menor',
        align: 'left',
        style: {
        fontSize: '15px'
        }
    },
    colors: ["#F4A261"]
};
  
  var chartBarVertical = new ApexCharts(document.querySelector('#barVerticalIntelxEmail'), optionsBarVertical);

  donut.render();
  chartBarVertical.render();
  chartBarHorizontal.render();

  // on smaller screen, change the legends position for donut
  var mobileDonut = function() {
    if($(window).width() < 999) {
      donut.updateOptions({
        plotOptions: {
          pie: {
            offsetY: -15,
          }
        },
        legend: {
          position: 'bottom'
        }
      }, false, false)
    }
    else {
      donut.updateOptions({
        plotOptions: {
          pie: {
            offsetY: 20,
          }
        },
        legend: {
          position: 'left'
        }
      }, false, false)
    }
  }

  $(window).resize(function() {
    mobileDonut()
  });

  if($(window).width < 760){
    var donete = document.getElementById("donete");
    donete.classList.add("mt-4")
  }

  window.dispatchEvent(new Event('resize'))