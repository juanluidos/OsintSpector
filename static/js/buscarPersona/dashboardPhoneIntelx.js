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
    
  const clavesFechaPhone = [];
  const valoresFechasPhone = [];

  for (const clave in diccionarioFechasPhone) {
    clavesFechaPhone.push(clave);
    valoresFechasPhone.push(diccionarioFechasPhone[clave]);
  }

  var optionsBarHorizontal = {
        series: [{
        name: "Veces filtrado en este año",
        data: valoresFechasPhone
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
            categories: clavesFechaPhone,
        },
        title: {
            text: 'Años y veces que aparecío el teléfono filtrado',
            align: 'left',
            style: {
            fontSize: '15px'
            }
        },
        colors: ['#E76F51']
    };

  var chartBarHorizontal = new ApexCharts(document.querySelector('#barHorizontalIntelxPhone'), optionsBarHorizontal);


  const clavesTipoPhone = [];
  const valoresTipoPhone = [];

  for (const clave in diccionarioTipoPhone) {
      clavesTipoPhone.push(clave);
      valoresTipoPhone.push(diccionarioTipoPhone[clave]);
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
      text: ' Tipos de archivos donde apareció filtrado el teléfono',
      style: {
        fontSize: '15px'
      }
    },
    series: valoresTipoPhone,
    labels: clavesTipoPhone,
    legend: {
      position: 'left',
      offsetY: 80
    }
  }

  var donut = new ApexCharts(document.querySelector("#donutIntelxPhone"), optionDonut)

  // ordenar diccionario
  var diccionarioTamanyoOrdenado = Object.keys(diccionarioTamanyoPhone).map(function(key) {
    return [key, diccionarioTamanyoPhone[key]];
  });
  diccionarioTamanyoOrdenado.sort(function(first, second) {
    return second[1] - first[1];
  });

  const clavesTamanyoPhone = []
  const valoresTamanyoPhone = []

  for (let i = 0; i < diccionarioTamanyoOrdenado.length; i++) {
    clavesTamanyoPhone.push(diccionarioTamanyoOrdenado[i][0]);
    valoresTamanyoPhone.push(diccionarioTamanyoOrdenado[i][1]);
  }

  var optionsBarVertical = {
    series: [{
    name: "Tamaño del archivo",
    data:  valoresTamanyoPhone
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
        categories: clavesTamanyoPhone,
    },
    title: {
        text: 'Tamaño de los archivos donde apareció filtrado el teléfono de mayor a menor',
        align: 'left',
        style: {
        fontSize: '15px'
        }
    },
    colors: ["#F4A261"]
};
  
  var chartBarVertical = new ApexCharts(document.querySelector('#barVerticalIntelxPhone'), optionsBarVertical);

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