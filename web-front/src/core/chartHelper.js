export default class ChartHelper {
  
  static buildChart (title, legendName, xData, yData, chartType = 'line', chartColor) {
      let ymin = Math.min(...yData)
      if (ymin >= 0.5) {
          ymin = ymin - 0.5
      }
      let ymax = Math.max(...yData) + 1
      let lineOption = {
          'color': [ (chartColor || '#C23736')],
          'title': {
              'text': title,
              'textStyle': {
                  color: 'grey',
                  fontFamily: 'Helvetica, Verdana, Arial',
                  fontSize: 12
              }
          },
          'tooltip': { 'show': 'true' },
          'legend': {
              'data': [legendName]
          },
          grid: {
            left: 30,
            top: 40,
            right: 20,
            bottom: 30
          },
          'xAxis': {
              'data': xData,
            //    splitLine: {
            //       lineStyle: {type: 'dashed', color: 'sliver'}
            //   }
          },
          'yAxis': [{ 'type': 'value', 'min': ymin, 'max': ymax }],
          
          'series': [{
              'name': legendName,
              'type': chartType,
              'data': yData,
              'areaStyle': {
                  normal: {
                      color: '#FBBC05'
                  }
              },
              label: {
                normal: {
                    show: true,
                    position: 'top'
                }
              }
          }]
      }

      return lineOption

  }

  static buildStackedChart (title, legendName, xData, ySeries, chartType = 'bar') {
    ySeries.forEach(item => {
        item.type = chartType
        item.stack = '总数'
        item.label = {
            normal: {
                show: true
                // position: 'insideCenter'
            }
        }
    }) 
    let stackOption = {
        'color': ['red', 'green'],
        'title': {
            'text': title,
            'textStyle': {
                color: 'grey',
                fontFamily: 'Helvetica, Verdana, Arial',
                fontSize: 12
            }
        },
        'tooltip': { 'show': 'true' },
        legend: {
            left: 'center',
            data: ySeries.map(item => item.name)
        },
        grid: {
          left: 40,
          top: 40,
          right: 20,
          bottom: 30
        },
        'xAxis': {
            type : 'category',
            'data': xData
        },
        'yAxis': [{'type': 'value'}
        ],
        series: ySeries
        // 'series': [{
        //     'name': legendName,
        //     'type': chartType,
        //     'data': yData
           
        // }]
    }

    return stackOption
  }

  static buildMultipleLine (title, legendNames, xDataArray, yDataArray) {
      let yminArray = yDataArray.map(itemArray => Math.min(...itemArray))
      let ymaxArray = yDataArray.map(itemArray => Math.max(...itemArray))

      let ymin = Math.min(...yminArray)
      if (ymin >= 0.5) {
          ymin = ymin - 0.5
      }
      let ymax = Math.max(...ymaxArray) + 1
      let xAxisVal = xDataArray.map(item => {
          return { type: 'category', data: item }
      })
      let seriesVal = yDataArray.map((item, k) => {
          return { name: legendNames[k], type: 'line', data: item }
      })
      let lineOption = {
          'title': {
              'text': title,
              'textStyle': {
                  color: 'grey',
                  fontFamily: 'Helvetica, Verdana, Arial',
                  fontSize: 12
              }
          },
          'tooltip': { 'show': 'true' },
          'legend': {
              'data': legendNames
          },
          'xAxis': xAxisVal,
          'yAxis': [{ 'type': 'value', 'min': ymin, 'max': ymax }],
          'series': seriesVal
      }

      return lineOption

  }


  static buildPieChart (title, legendName, items, labels = null) {
      if (labels == null) {
          labels = items.map(item => item.name)
      }
      const pieOption = {
          'title': {
              'text': `${title}`,
              'x': 'center',
              'textStyle': {
                  color: 'grey',
                  fontFamily: 'Helvetica, Verdana, Arial',
                  fontSize: 12
              }
          },
          'tooltip': {
              'trigger': 'item',
              'formatter': "{a} <br/>{b} : {c} ({d}%)"
          },
          'legend': {
              'orient': 'vertical',
              'left': 'left',
              'data': labels
          },
          'series': [{
              'name': legendName,
              'type': 'pie',
              'radius': '55%',
              'center': ['50%', '60%'],
              'data': items,
              'itemStyle': {
                  'emphasis': {
                      'shadowBlur': 10,
                      'shadowOffsetX': 0,
                      'shadowColor': 'rgba(0, 0, 0, 0.5)'
                  }
              }
          }]
      }

      return pieOption

  }

  static buildGeomapChart (title, legendName, items, labels) {
      const vmin = Math.min(...(items.map(item => item.value)))
      const vmax = Math.max(...(items.map(item => item.value)))

      const mapOptions = {
          title: {
              text: title,
              left: 'center',
              'textStyle': {
                  color: 'grey',
                  fontFamily: 'Helvetica, Verdana, Arial',
                  fontSize: 12
              }
          },
          tooltip: {
              trigger: 'item'
          },
          legend: {
              orient: 'vertical',
              left: 'left',
              data: labels
          },
          visualMap: {
              min: vmin,
              max: vmax,
              left: 'left',
              top: 'bottom',
              text: ['高', '低'], // 文本，默认为数值文本
              calculable: true
          },
          toolbox: {
              show: true,
              orient: 'vertical',
              left: 'right',
              top: 'center',
              feature: {
                  dataView: { readOnly: false },
                  restore: {},
                  saveAsImage: {}
              }
          },
          series: [{
              name: labels[0],
              type: 'map',
              mapType: 'china',
              roam: false,
              label: {
                  normal: {
                      show: true
                  },
                  emphasis: {
                      show: true
                  }
              },
              data: items
          }]
      }

      return mapOptions
  }

  static buildFlowChart ({stockName, xData, yBarData, yLineData}) {
    let lineOption = {
      color: ['#3682B8', '#FF2C35'],
      // color: ['#EFAE3D', '#FF2C35'],
      title: {
          text: `${stockName} 持有占比曲线`,
          textStyle: {
            color: 'grey',
            fontFamily: 'Helvetica',
            fontSize: 12
          }
      },
      tooltip: {show: true},
      legend: {
          data: ['持有量', '持有占比(%)']
      },
      grid: {
          left: 80,
          top: 40,
          right: 30,
          bottom: 30
      },
      xAxis: [{
          type: 'category', 
          data: xData
      }],
      yAxis: [
          {
              type: 'value',
              position: 'left'
          },
          {
              type: 'value',
              position: 'right'
          }
      ],
      series: [{
          name: '持有量',
          type: 'bar',
          data: yBarData
      }, {
          name: '持有占比(%)',
          type: 'line',
          data: yLineData,
          yAxisIndex: 1
      }]
    }

    return lineOption
  }

  static buildXueqiuChart (stockName, xData, yLine1, yLine2) {
    let lineOption = {
      color: ['#3682B8', '#FF2C35'],
      title: {
          text: `${stockName} 雪球社交曲线`,
          textStyle: {
            color: 'grey',
            fontFamily: 'Helvetica',
            fontSize: 14,
            fontWeight: 'bold'
          }
      },
      tooltip: {show: true},
      legend: {
          data: ['讨论数', '关注人数']
      },
      grid: {
          left: 80,
          top: 40,
          right: 60,
          bottom: 30
      },
      xAxis: [{
          type: 'category', 
          data: xData
      }],
      yAxis: [
          {
              type: 'value',
              position: 'left'
          },
          {
              type: 'value',
              position: 'right'
          }
      ],
      series: [{
          name: '讨论数',
          type: 'line',
          data: yLine2,
          yAxisIndex: 1
      }, {
          name: '关注人数',
          type: 'line',
          data: yLine1,
      }]
    }

    return lineOption
  }

  static buildRelationChart (title, categories, nodes, links) {

    const relationOption = {
        'title': {
            'text': `${title}`,
            'x': 'left',
            'textStyle': {
                color: 'grey',
                fontFamily: 'Helvetica, Verdana, Arial',
                fontSize: 12
            }
        },
        tooltip: {},
        lengend: [{
            data: categories.map(item => item.name)
        }],
        animation: false,
        series: [{  
            type: 'graph',  
            layout: 'force',  
            animation: false,  
            label: {  
                normal: {  
                    show: true,  
                    position: 'center'
                }  
            },  
            draggable: true,  
            data: nodes,  
            categories: categories,  
            lineStyle: {
                normal: {
                    color: 'source',
                    curveness: 0.2
                }
            },
            force: {
                // initLayout: 'circular'
                // repulsion: 20,
                edgeLength: 200,
                repulsion: 100,
                gravity: 0.2
            },
            roam: true,
            links: links  
        }]  
    }

    return relationOption
  }
}
