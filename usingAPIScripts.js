let acceptURL = function (par, path) {
    url = 'https://hyperbrowser.uio.no'+ path+'/api/' + par;
    return url;
};

let afterSetExtremes = function(e) {

    let chart = Highcharts.charts[0];
    // url = acceptURL(par);
    chart.showLoading('Loading data from server...');
    $.getJSON(url +'&start=' + Math.round(e.min) +
            '&end=' + Math.round(e.max), function (data) {

        chart.series[0].setData(data);
        chart.hideLoading();
    });
};





let prettySelectionText = 'genome';


let countPointLineChartViz = function(container, interval, count, myText) {
    $(container).highcharts({
        chart: {
        type: 'line',
        zoomType: 'x'
    },
        title: {
            text: myText
        },
        xAxis: {
            categories: interval,
            labels: {
                rotation: 270
            }
        },
        yAxis: {
            title: {
                // text: 'Counts [bp]'
            }
        },


        series: [{
            showInLegend: false,
            data: JSON.parse("[" + count + "]")
        }],

        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                }
            }]
        }

    });
};



let overlapLineChartViz = function(container, interval, countBoth, countOnly1, myText) {
    $(container).highcharts({
        chart: {
        type: 'area',
        zoomType: 'x'
    },
        title: {
            text: myText
        },
        xAxis: {
            categories: interval,
            labels: {
                rotation: 270
            }
        },
        yAxis: [{
            title: {
                text: 'Coverage Both'
                }
            },
            {
            labels: {
                style: {
                    color: 'green'
                    }
                },
            title: {
                text: 'Coverage Query',
                style: {
                    color: 'green'
                    }
                },
                opposite: true
            }],


        series: [{
            name: 'coverage by both tracks',
            data: JSON.parse("[" + countBoth + "]"),
             color: 'green',
            yAxis: 1
            },{
                name: 'coverage by query track',
                data: JSON.parse("[" + countOnly1 + "]"),
            // color: 'rgb(124, 181, 236)'
            }],

        /*responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                }
            }]
        }*/

    });
};



let countPointViz = function (container, interval, count, myText) {      // make chart
    $(container).highcharts({
        chart: {
            type: "column",
            zoomType: 'x'
        },

        title: {

            text: myText
        },

        xAxis: {
            categories: interval,
            labels: {
                rotation: 270
            }
        },

        yAxis: {
            title: {
                text: ''
            }
        },
        series: [{
            showInLegend: false,
            name: name,
            data: JSON.parse("[" + count + "]")
        }]

    });
};


let avgSegLenViz = function (container, interval, count, myText) {      // make chart
    $(container).highcharts({
        chart: {
            type: "column",
            zoomType: 'x'
        },

        title: {

            text: myText
        },

        xAxis: {
            categories: interval,
            labels: {
                rotation: 270
            }
        },

        yAxis: {
            title: {
                text: ''
            }
        },
        series: [{
            showInLegend: false,
            name: name,
            data: JSON.parse("[" + count + "]")
        }]

    });
};


let startEndViz = function (container, data, labels) {
    // Highcharts.chart('container', {
    $(container).highcharts({


        chart: {
            // renderTo: container,
            type: 'xrange',
            zoomType: 'xy'
        },
        title: {
            text: 'Overview of data'
        },
        xAxis: {
            type: 'int'
        },
        yAxis: {
            title: {
                text: ''
            },
            labels: {
                step:1
            },
            categories: labels
        },
        series: [{
            showInLegend: false,
            turboThreshold: 5000000,
            pointPadding: 0,
            groupPadding: 0,
            borderColor: 'black',
            pointWidth: 10,
            minPointLength: 10,
            data: data

        }],
        dataLabels: {
            enabled: true
        }
    });

};


let populateArrayCountFromJSON = function (url) {
    let myData = [];
    $.getJSON(url, function (data) {
        myData = data;
    });
    return myData
};

let histogramViz = function(container, count, text){

    let chart,
binnedData = binData(count);

$(function() {
  $(container).highcharts({
    chart: {
      type: 'column',
        zoomType: 'x',
      margin: [40, 40, 40, 40]
    },
    title: {
      text: text,
      x: 10
    },
    legend: {
      enabled: false
    },
    credits: {
      enabled: false
    },
    exporting: {
      enabled: true
    },
    tooltip: {},
    plotOptions: {
      series: {
        pointPadding: 0,
        groupPadding: 0,
        borderWidth: 0.5,
        borderColor: 'rgba(255,255,255,0.5)',
        color: Highcharts.getOptions().colors[1]
      }
    },
    xAxis: {
      title: {
        text: 'Sepal Width (cm)'
      }
    },
    yAxis: {
      title: {
        text: ''
      }
    }
  });
  chart = $(container).highcharts();
  chart.addSeries({
      showInLegend: false,
    name: 'Distribution',
    data: binnedData
  });

});

//-------------------------------------------------------
function binData(data) {

  let hData = [], //the output array
    size = data.length, //how many data points
    bins = Math.round(Math.sqrt(size)); //determine how many bins we need
  bins = bins > 50 ? 50 : bins; //adjust if more than 50 cells
  let max = Math.max.apply(null, data), //lowest data value
    min = Math.min.apply(null, data), //highest data value
    range = (max - min)/20, //total range of the data
    width = range / bins, //size of the bins
    bin_bottom, //place holders for the bounds of each bin
    bin_top;

  //loop through the number of cells
  for (let i = 0; i < bins; i++) {

    //set the upper and lower limits of the current cell
    bin_bottom = min + (i * width);
    bin_top = bin_bottom + width;

    //check for and set the x value of the bin
    if (!hData[i]) {
      hData[i] = [];
      hData[i][0] = bin_bottom + (2*width);
    }

    //loop through the data to see if it fits in this bin
    for (let j = 0; j < size; j++) {
      let x = data[j];

      //adjust if it's the first pass
      i == 0 && j == 0 ? bin_bottom -= 1 : bin_bottom = bin_bottom;

      //if it fits in the bin, add it
      if (x > bin_bottom && x <= bin_top) {
        !hData[i][1] ? hData[i][1] = 1 : hData[i][1]++;
      }
    }
  }
  $.each(hData, function(i, point) {
    if (typeof point[1] == 'undefined') {
      hData[i][1] = 0;
    }
  });
  return hData;
}


};

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

function jsonToArray(data){
            rawArrayKey = [];
            rawArrayValue = [];

            for (chr in data) {
                rawArrayKey.push((data[chr])[0]);
                if (data[chr] == undefined)
                {

                }
                else
                    {
                    if (data[chr][1] == undefined)
                    {

                    }
                    else
                        {
                            if (data[chr][1]["Result"] == undefined)
                            {

                            }
                            else
                            {
                                rawArrayValue.push(data[chr][1]["Result"]);
                            }

                        }
                 }
            }

            return {rawArrayKey, rawArrayValue};
}
let method ='GET';

const myFetch = function(url, method, limit=7) {
    let myHeader = new Headers({
            'Accept': 'application/json',
            'Content-Type': 'application/json ; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'
        });
    try {
        return fetch(url, {
            myHeader,
            method: method,
            credentials: 'same-origin',
        }).then(response => {
            if(response.status != 200 && --limit){
                return myFetch(url, method, limit)
            }
            return response;
        })
    }
    catch (error) {
        alert('There seems to be some problem with the server. Please try again.')
    }
};



function getStartEndStat(url, container) {
    if (url.includes('stat=StartEndStat')) {
    return myFetch(url)
        .then((response) => response.json())
        .then(function(data) {
            myData = data[0];
            labels = data[1];
            startEndViz(container, myData, labels);
        })
        }
}

function getProportionCountStat(url, container) {
    if (url.includes('stat=ProportionCountStat')) {
        return myFetch(url)
        .then((response) => response.json())
            .then(function (data) {
            rawArrayKey = jsonToArray(data).rawArrayKey;
            rawArrayValue = jsonToArray(data).rawArrayValue;
                myName = 'ProportionalCountStat';
                myText = 'Proportional bp coverage of ' + prettySelectionText;
            countPointViz(container, rawArrayKey, rawArrayValue, myText, myName);

        });

    }
}

function getAvgSegLenStat(url, container) {
    if (url.includes('stat=AvgSegLenStat')) {
        return myFetch(url)
        .then((response) => response.json())
            .then(function (data) {
                rawArrayKey = [];
                rawArrayValue = [];
                for (chr in data) {
                    rawArrayKey.push(chr);
                    rawArrayValue.push(data[chr]["Result"]);
                }
                myName = 'AvgSegLenStat';
                myText = 'Distribution of average segment length of ' + prettySelectionText;
            avgSegLenViz(container, rawArrayKey, rawArrayValue, myText, myName);

        });

    }
}

function getCountStat(url, container) {
    if (url.includes('stat=CountStat')) {
        return myFetch(url)
            .then((response) => response.json())
            .then(function (data) {
            rawArrayKey = jsonToArray(data).rawArrayKey;
            rawArrayValue = jsonToArray(data).rawArrayValue;
            myName = 'CountStat';
            myText = 'Counts of covered bp per ' + prettySelectionText + '';
            countPointLineChartViz(container, rawArrayKey, rawArrayValue, myText, myName);
        });
    }
}

function getSegmentLengthsStat(url, container) {
    if (url.includes('stat=SegmentLengthsStat')) {
        return myFetch(url)
            .then((response) => response.json())
            .then(function (data) {
            rawArray = data;
            text = 'Length of the segments for ... ';
            histogramViz(container, rawArray, text);
        });
    }
}

function getSegmentDistancesStat(url, container) {
    if (url.includes('stat=SegmentDistancesStat')) {
        return myFetch(url)
            .then((response) => response.json())
            .then(function (data) {
            rawArray = data;
            text = 'The distribution of distances between segments';
            histogramViz(container, rawArray, text);
        });
    }
}

function getRawOverlapStat (url, container) {
    if (url.includes('stat=RawOverlapStat')){
        return myFetch(url)
            .then((response) => response.json())
                .then(function(data) {
                    myData = data;

                    rawArrayKey = myData[0];
                    rawArrayValueBoth = myData[1];
                    rawArrayValueOnly1 = myData[2];
                        myName = 'RawOverlapStat: Coverage both';
                        myText = 'Distribution for ' + myName;
                        myText = 'Overlap between data';
                        overlapLineChartViz("#first", rawArrayKey, rawArrayValueBoth, rawArrayValueOnly1, myText, myName);



                })
    }
}

function acceptFromSelected (url) {
    return myFetch(url, 'GET')
        .then((response) => response.json())
}

let plotFinalChart = function (par, path, container) {
    let url = acceptURL(par, path);
    allStats = [getStartEndStat(url, container),
                getProportionCountStat(url, container),
                getCountStat(url, container),
                getSegmentLengthsStat(url, container),
                getSegmentDistancesStat(url, container),
                getAvgSegLenStat(url, container)
        ];
};

let plotFinalChartForOverlap = function (par, path, container) {
    let url = acceptURL(par, path);
    getRawOverlapStat(url, container);
};

let getSelectedGSuiteTrack = function (par, path) {
    let url = acceptURL(par, path);
    acceptFromSelected(url);
};


function makeButtons(trackTitle, numberOfTracks) {
        var navButtons = document.getElementById("nav-buttons");
        titleArray = trackTitle;
        for (var b = 0; b < parseInt(numberOfTracks); b++) {
            currentTitle = titleArray[b];
            var buttonGSuite = document.createElement("button");
                buttonGSuite.className = "ui primary basic button";
                buttonGSuite.innerHTML = titleArray[b];
                buttonGSuite.value = currentTitle;
                buttonGSuite.addEventListener("click", buttonClicked);
                navButtons.appendChild(buttonGSuite);
        }
}

function firedButton (trackTitle, firstTrack) {
    let firedButton = $('#selectedOption').val();
    if ((trackTitle.indexOf(firedButton)) > -1) {
        posInTitle = trackTitle.indexOf(firedButton);
        firstTrack = firstTrack[posInTitle];
        firstTrack1 = firstTrack.map(x => '"' + String(x) + '"');

        firstTrack = '[' + firstTrack1 + ']';
        return firstTrack;
    }
    else {
        firstTrack = firstTrack[0];
        firstTrack1 = firstTrack.map(x => '"' + String(x) + '"');
        firstTrack = '[' + firstTrack1 + ']';
        return firstTrack;
    }
}
