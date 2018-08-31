
window.onload = function()
{
    buildHtmlTable("#data", data);

	const imgDiv = document.getElementById("images");

	for (var i = 0; i < Object.keys(data[0]).length; i++)
	{
		if (Object.keys(data[0])[i] == "TIME" || Object.keys(data[0])[i] == "GPS")
			continue;
		
		imgDiv.innerHTML += '<br/><img src="' + Object.keys(data[0])[i] + '.png"></img>';
  }
};

function initMaps()
{
    mapLibLoaded = true;

    while (mapsToInstance.length > 0)
        mapsToInstance.pop().init();

    var map = new Map('map', -25.344, 131.036, 4);
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
