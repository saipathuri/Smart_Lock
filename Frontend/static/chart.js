var textFromFile = "";
var rawFile = new XMLHttpRequest();
rawFile.open("GET", "static/numberToUserTable.txt", false);
rawFile.onreadystatechange = function ()
{
	if(rawFile.readyState === 4 && (rawFile.status === 200 || rawFile.status == 0))
		textFromFile = rawFile.responseText;
}
rawFile.send(null);

function getUsername(value)
{
	var tempTextFromFile = textFromFile;
	var line = "";
	if (tempTextFromFile.indexOf("\n") != -1)
	{
		line = tempTextFromFile.substring(0, tempTextFromFile.indexOf("\n"));
		tempTextFromFile = tempTextFromFile.substring(tempTextFromFile.indexOf("\n") + 1);
	}
	else
	{
		line = tempTextFromFile;
		tempTextFromFile = "";
	}
				
	while (line.length > 0 && tempTextFromFile.length > 0 && !(line.substring(0, line.indexOf(":")) === (value.toString())))
	{
		if (tempTextFromFile.indexOf("\n") != -1)
		{
			line = tempTextFromFile.substring(0, tempTextFromFile.indexOf("\n"));
			tempTextFromFile = tempTextFromFile.substring(tempTextFromFile.indexOf("\n") + 1);
		}
		else
		{
			line = tempTextFromFile;
			tempTextFromFile = "";
		}
	}

	return line.substring(line.indexOf(":") + 1);
}

var data = JSON.parse(chartData);
var chartOptions =
{
	width: '1000px',
	height: '400px',
	chartPadding:
	{
		left: 10,
		right: 50,
		top: 70
	},
	low: 0,
	axisX:
	{
		onlyInteger: true,
		labelInterpolationFnc: function(value)
		{
			if (value == 0)
				return "12am"
			else if (value == 12)
				return "12pm"
			else if (value == 24)
				return "12am"
			else if (value < 12)
				return value + "am"
			else if (value > 12 && value < 25)
				return (value - 12) + "pm"
			else
				return "ERROR"
		}
	},
	axisY:
	{
		onlyInteger: true,
		labelInterpolationFnc: function(value)
		{
			if (value == 0)
				return ' '
			else
			{
				return getUsername(value);
			}
		}
	}
};

var chart = new Chartist.Line('.ct-chart', data, chartOptions);