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
  
    var resultadosPwnedPhoneBreach = resultadosPwnedPhone

    diccionarioFechasBreach = {}
    for(let elemento of resultadosPwnedPhoneBreach){
      let fecha = elemento[2]
      if(fecha !== undefined ){
        if(fecha in diccionarioFechasBreach){
          diccionarioFechasBreach[fecha] +=1
        }else{
          diccionarioFechasBreach[fecha] = 1
        }
      }
    }

    const clavesFechasPhoneBreach = []
    const valoresFechasPhoneBreach  = []
    for (const clave in diccionarioFechasBreach) {
      clavesFechasPhoneBreach.push(clave);
      valoresFechasPhoneBreach.push(diccionarioFechasBreach[clave]);
    }




    var diccionarioFechasTotal = diccionarioFechasBreach

    var listaFechas = Object.keys(diccionarioFechasTotal);

    var optionsBarHorizontal = {
          series: [{
          name: "Veces filtrado en este año debido a un Breach",
          data: valoresFechasPhoneBreach
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
              horizontal: false,
              }
          },
          dataLabels: {
              enabled: true
          },
          xaxis: {
              categories: listaFechas,
          },
          title: {
              text: 'Años y veces que aparecío el teléfono filtrado',
              align: 'left',
              style: {
              fontSize: '15px'
              }
          },
          colors: ['#E76F51','#E9C46A']
      };
  
    var chartBarHorizontal = new ApexCharts(document.querySelector('#barHorizontalHibpPhone'), optionsBarHorizontal);
  
    let leakDictPhone = {};

    for (let leak of resultadosPwnedPhoneBreach) {
      console.log(resultadosPwnedPhoneBreach)
      for (let i = 0; i < leak[4].length; i++) {
        let dataType = leak[4][i];
        if (dataType in leakDictPhone) {
          leakDictPhone[dataType] += 1;
        } else {
          leakDictPhone[dataType] = 1;
        }
      }
    }

    const clavesDatosPhoneComprometidos = []
    const valoresDatosPhoneComprometidos  = []
    for (const clave in leakDictPhone) {
      clavesDatosPhoneComprometidos.push(clave);
      valoresDatosPhoneComprometidos.push(leakDictPhone[clave]);
    }


    var optionsBarVertical = {
      series: [{
      name: "Nº veces comprometido",
      data:  valoresDatosPhoneComprometidos
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
          categories: clavesDatosPhoneComprometidos,
      },
      title: {
          text: 'Nº veces de tipos de datos comprometidos por el teléfono',
          align: 'left',
          style: {
          fontSize: '15px'
          }
      },
      colors: ["#F4A261"]
  };
    
    var chartBarVertical = new ApexCharts(document.querySelector('#barVerticalHibpPhone'), optionsBarVertical);
  

    chartBarVertical.render();
    chartBarHorizontal.render();
  
    window.dispatchEvent(new Event('resize'))