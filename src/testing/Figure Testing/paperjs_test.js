paper.setup('myCanvas');

// Create a rectangle representing a boiler
var boiler = new paper.Path.Rectangle(new paper.Point(100, 100), new paper.Size(200, 100));
boiler.fillColor = 'blue';

// Create text for the boiler
var boilerText = new paper.PointText(new paper.Point(200, 160));
boilerText.justification = 'center';
boilerText.fillColor = 'white';
boilerText.content = 'Boiler';

// Create a circle representing a turbine
var turbine = new paper.Path.Circle(new paper.Point(500, 150), 50);
turbine.fillColor = 'yellow';

// Create text for the turbine
var turbineText = new paper.PointText(new paper.Point(500, 155));
turbineText.justification = 'center';
turbineText.fillColor = 'white';
turbineText.content = 'Turbine';

// Create text elements for displaying numbers
var boilerNumberText = new paper.PointText(new paper.Point(200, 210));
boilerNumberText.justification = 'center';
boilerNumberText.fillColor = 'black';
boilerNumberText.content = '0';

var turbineNumberText = new paper.PointText(new paper.Point(500, 210));
turbineNumberText.justification = 'center';
turbineNumberText.fillColor = 'black';
turbineNumberText.content = '0';

function updateDiagram(status) {
    if (status === 'Normal') {
        boiler.fillColor = 'blue';
        turbine.fillColor = 'green';
        boilerNumberText.content = '10'; // Example number
        turbineNumberText.content = '20'; // Example number
    } else {
        boiler.fillColor = 'red';
        turbine.fillColor = 'red';
        boilerNumberText.content = '5'; // Example number
        turbineNumberText.content = '10'; // Example number
    }
}

// Expose the changeStatus function to the global scope
window.changeStatus = function(status) {
    updateDiagram(status);
    paper.view.update();
};