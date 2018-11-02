
var units = {
	'CO2': 'ppm', 'TEMP': 'ºC', 'Turbidity': 'NTU',
	'LUXES': 'lx', 'TEMPH2O': 'ºC'
}

var headers = [];

window.onload = function()
{
    var data2 = [];

    for (value in data)
    {
        var val = {};

        for (var i = 0; i < Object.keys(data[value]).length; i++)
        {
            var key = Object.keys(data[value])[i];
            var str = key;

            if (units[key] != undefined)
                str = str + " (" + units[key] + ")";
            
            val[str] = data[value][key];
        }

        data2.push(val);
    }

    buildHtmlTable("#data", data2);

    headers = document.getElementsByTagName("th");

    for (var i = 0; i < headers.length; i++)
        headers[i].onclick = function() { showGraph(this); };

    var gpsCoord = data[data.length - 1]["GPS"].split(",");
    var map = new Map('map', parseFloat(gpsCoord[0]), parseFloat(gpsCoord[1]), 12);
};

function initMaps()
{
    mapLibLoaded = true;

    while (mapsToInstance.length > 0)
        mapsToInstance.pop().init();
}

function buildHtmlTable(selector, myList)
{
    var columns = addAllColumnHeaders(myList, selector);
  
    for (var i = 0; i < myList.length; i++)
    {
        if (myList[i] == null)
            continue;

        var row$ = $('<tr/>');

        for (var colIndex = 0; colIndex < columns.length; colIndex++)
        {
            var cellValue = myList[i][columns[colIndex]];
            if (cellValue == null) cellValue = "";
                row$.append($('<td/>').html(cellValue));
        }
 
        $(selector).append(row$);
    }
}

function addAllColumnHeaders(myList, selector)
{
    var columnSet = [];
    var headerTr$ = $('<tr/>');

    for (var i = 0; i < myList.length; i++)
    {
        if (myList[i] == null)
            continue;

        var rowHash = myList[i];

        for (var key in rowHash)
        {
            if ($.inArray(key, columnSet) == -1)
            {
                columnSet.push(key);
                headerTr$.append($('<th/>').html(key));
            }
        }
    }

    $(selector).append(headerTr$);

    return columnSet;
}

function showGraph(elem)
{
    var name = elem.innerHTML.split(' ')[0];
    const imgDiv = document.getElementById("images");

	if (name != "TIME" && name != "GPS")
        imgDiv.innerHTML = '<br/><img class="graph" src="' + name + '.png"></img><br/>';
}
