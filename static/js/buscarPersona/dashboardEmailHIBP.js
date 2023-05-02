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
  
    var resultadosPwnedEmailBreach = resultadosPwnedEmail[0]
    var resultadosPwnedEmailPaste = resultadosPwnedEmail[1]

    diccionarioFechasBreach = {}
    for(let elemento of resultadosPwnedEmailBreach){
      let fecha = elemento[2]
      if(fecha !== undefined ){
        if(fecha in diccionarioFechasBreach){
          diccionarioFechasBreach[fecha] +=1
        }else{
          diccionarioFechasBreach[fecha] = 1
        }
      }
    }

    const clavesFechasEmailBreach = []
    const valoresFechasEmailBreach  = []
    for (const clave in diccionarioFechasBreach) {
      clavesFechasEmailBreach.push(clave);
      valoresFechasEmailBreach.push(diccionarioFechasBreach[clave]);
    }


    diccionarioFechasPaste = {}

    for(let elemento of resultadosPwnedEmailPaste){
      let fecha = elemento[2]
      if(fecha !== null ){
        if(fecha in diccionarioFechasPaste){
          diccionarioFechasPaste[fecha] +=1
        }else{
          diccionarioFechasPaste[fecha] = 1
        }
      }
    }

    const clavesFechasEmailPaste = []
    const valoresFechasEmailPaste  = []
    for (const clave in diccionarioFechasPaste) {
      clavesFechasEmailPaste.push(clave);
      valoresFechasEmailPaste.push(diccionarioFechasPaste[clave]);
    }

    var diccionarioFechasTotal = {...diccionarioFechasBreach, ...diccionarioFechasPaste}

    var listaFechas = Object.keys(diccionarioFechasTotal);

    var optionsBarHorizontal = {
          series: [{
          name: "Veces filtrado en este año debido a un Breach",
          data: valoresFechasEmailBreach
          },
          {
          name: "Veces filtrado en este año debido a un Paste",
          data: valoresFechasEmailPaste
          }],
              chart: {
              type: 'bar',
              height: 380,
              width: '100%',
              stacked: true
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
              categories: listaFechas,
          },
          title: {
              text: 'Años y veces que aparecío el email filtrado',
              align: 'left',
              style: {
              fontSize: '15px'
              }
          },
          colors: ['#E76F51','#E9C46A']
      };
  
    var chartBarHorizontal = new ApexCharts(document.querySelector('#barHorizontalHibpEmail'), optionsBarHorizontal);
  

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
        text: 'Cantidad de Breaches y Pastes del email',
        style: {
          fontSize: '15px'
        }
      },
      series: [resultadosPwnedEmailBreach.length, resultadosPwnedEmailPaste.length],
      labels: ["Breaches", "Pastes"],
      legend: {
        position: 'left',
        offsetY: 80
      }
    }
  
    var donut = new ApexCharts(document.querySelector("#donutHibpEmail"), optionDonut)
  
    let leakDictEmail = {};

    for (let leak of resultadosPwnedEmailBreach) {
      for (let i = 0; i < leak[4].length; i++) {
        let dataType = leak[4][i];
        if (dataType in leakDictEmail) {
          leakDictEmail[dataType] += 1;
        } else {
          leakDictEmail[dataType] = 1;
        }
      }
    }

    const clavesDatosEmailComprometidos = []
    const valoresDatosEmailComprometidos  = []
    for (const clave in leakDictEmail) {
      clavesDatosEmailComprometidos.push(clave);
      valoresDatosEmailComprometidos.push(leakDictEmail[clave]);
    }


    var optionsBarVertical = {
      series: [{
      name: "Nº veces comprometido",
      data:  valoresDatosEmailComprometidos
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
          categories: clavesDatosEmailComprometidos,
      },
      title: {
          text: 'Nº veces de tipos de datos comprometidos por el email',
          align: 'left',
          style: {
          fontSize: '15px'
          }
      },
      colors: ["#F4A261"]
  };
    
    var chartBarVertical = new ApexCharts(document.querySelector('#barVerticalHibpEmail'), optionsBarVertical);
  
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