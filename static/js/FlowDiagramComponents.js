// FlowDiagramComponents.js
// Define a class for the components of the flow diagram

// Define a class for the Flow Diagram Component (Superclass)
class FlowDiagramComponent {
    constructor(position, bounds, showBoundingBox = false) {
        this.x = position[0];
        this.y = position[1];
        this.width = bounds[0];
        this.height = bounds[1];

        // Create a rectangle representing the component
        this.boundingBox = new paper.Path.Rectangle({
            point: position,
            size: bounds,
            strokeColor: 'black',
            strokeWidth: 2
        });
        // Define the bounds of the component
        this.bounds = this.boundingBox.bounds;
        // Show the bounding box if required
        if (!showBoundingBox) {
            this.boundingBox.visible = false;
        }

        // Create a group to hold the parts of the component
        this.group = new paper.Group();

        // Define inlet and outlet centers by default
        this.inlet = new paper.Point([this.boundingBox.bounds.left, this.boundingBox.bounds.center.y]);
        this.outlet = new paper.Point([this.boundingBox.bounds.right, this.boundingBox.bounds.center.y]);
    }

    // Method to route a line from the inlet of one component to the outlet of another
    routeLineTo(component, intermediatePoints = []) {
        let line = new paper.Path({
            strokeColor: 'black',
            strokeWidth: 5
        });
        line.add(this.outlet);
        intermediatePoints.forEach(point => line.add(point));
        line.add(component.inlet);
        return line;
    }

    // Method to make the inlet and outlet markers
    makeInletOutletMarkers() {
        this.inlet_marker = new paper.Path.Circle({
            center: this.inlet,
            radius: 5,
            fillColor: 'blue'
        });
        this.outlet_marker = new paper.Path.Circle({
            center: this.outlet,
            radius: 5,
            fillColor: 'red'
        });
        this.group.addChild(this.inlet_marker);
        this.group.addChild(this.outlet_marker);

        this.inlet_marker.bringToFront();
        this.outlet_marker.bringToFront();
    }

    showBoundingBox() {
        this.boundingBox.visible = true;
    }
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Custom shape class for the MFC figure
class MFCDiagramComponent extends FlowDiagramComponent {
    constructor(position, bounds, label) {
        // Call the superclass constructor
        super(position, bounds);
        this.color = 'red';
        this.label = label;

        // Create the Base of the MFC
        let base_pos = [0.05, 0.85];
        let base_size = [0.9, 0.15];
        this.base = new paper.Path.Rectangle({
            point: base_pos.map((dim, index) => position[index] + dim * bounds[index]),
            size: base_size.map((dim, index) => dim * bounds[index]),
            fillColor: 'black'
        });

        // Create the MFC Display
        let display_size = [0.7, 0.7];
        let display_pos = [0.1, base_pos[1] - display_size[1]];
        this.display = new paper.Path.Rectangle({
            point: display_pos.map((dim, index) => position[index] + dim * bounds[index]),
            size: display_size.map((dim, index) => dim * bounds[index]),
            fillColor: this.color,
            strokeColor: 'black',
            strokeWidth: 2
        });

        // Create the MFC Display Title
        //Align with the left side of the display
        let title_pos = [display_pos[0], 0.1];
        this.title = new paper.PointText({
            point: title_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'left',
            fillColor: 'black',
            fontWeight: 'bold',
            content: this.label,
            fontSize: 20
        });
       
        // Create the MFC Display Texts
        let labels_leftBound = display_pos[0] + 0.05 * display_size[0];
        const fontSize = 20;
        //Pressure
        let pres_pos = [labels_leftBound, display_pos[1] + 0.2 *display_size[1]];
        this.pres_label = new paper.PointText({
            point: pres_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'left',
            fillColor: 'black',
            fontWeight: 'bold',
            fontSize: fontSize,
            content: 'XX.XX psi'
        });
        //Flow Rate
        let flow_pos = [labels_leftBound, display_pos[1] + 0.5 *display_size[1]];
        this.flow_label = new paper.PointText({
            point: flow_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'left',
            fillColor: 'black',
            fontWeight: 'bold',
            fontSize: fontSize,
            content: 'XX.XX sccm'
        });
        //Temperature
        let temp_pos = [labels_leftBound, display_pos[1] + 0.8 *display_size[1]];
        this.temp_label = new paper.PointText({
            point: temp_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'left',
            fillColor: 'black',
            fontWeight: 'bold',
            fontSize: fontSize,
            content: 'XX.XX C'
        });

        // Set up a click event on the group
        this.group = new paper.Group();
        this.group.addChild(this.base);
        this.group.addChild(this.display);
        this.group.addChild(this.title);
        this.group.addChild(this.pres_label);
        this.group.addChild(this.flow_label);
        this.group.addChild(this.temp_label);

        // Define the center of the inlet and outlet of the MFC for the connection lines, put in pixel units
        this.inlet =  new paper.Point([this.base.bounds.left, this.base.bounds.center.y]);
        this.outlet = new paper.Point([this.base.bounds.right, this.base.bounds.center.y]);
    }

    // Method to update the text content
    updateText(newVals) {
        let formattedNumbers = newVals.map(num => `${num.toFixed(2)}`);
        console.log(formattedNumbers);

        this.pres_label.content = `${formattedNumbers[0]} psi`;
        this.flow_label.content = `${formattedNumbers[1]} sccm`;
        this.temp_label.content = `${formattedNumbers[2]} C`;
    }

    // Method to update the color of the display
    updateColor(newColor) {
        this.color = newColor;
        this.display.fillColor = newColor;
    }
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Custom shape class for the Sensor figure
class SensorDiagramComponent extends FlowDiagramComponent {
    constructor(position, bounds, label, color = 'green') {
        // Call the superclass constructor
        super(position, bounds);
        this.color = color;
        this.label = label;

        // Create the Sensor Display Circle
        let display_size = 1;
        this.display = new paper.Path.Circle({
            center: [this.x + bounds[0]/2, this.y + bounds[0]/2],
            radius: display_size * bounds[0]/2,
            fillColor: this.color,
            strokeColor: 'black',
            strokeWidth: 2
        });

        // Create the Sensor Display Title
        let title_pos = [0.5, -0.05];
        this.title = new paper.PointText({
            point: title_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'center',
            fillColor: 'black',
            fontWeight: 'bold',
            content: this.label,
            fontSize: 20
        });
       
        // Create the Sensor Display Texts
        //Humidity
        let pres_pos = [0.5, 0.7];
        this.pres_label = new paper.PointText({
            point: pres_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'center',
            fillColor: 'black',
            fontWeight: 'bold',
            fontSize: 18,
            content: 'XX.XX %'
        });
        //Temperature
        let temp_pos = [0.5, 0.9];
        this.temp_label = new paper.PointText({
            point: temp_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'center',
            fillColor: 'black',
            fontWeight: 'bold',
            fontSize: 18,
            content: 'XX.XX C'
        });

        // Set up a click event on the group
        this.group = new paper.Group();
        this.group.addChild(this.boundingBox);
        this.group.addChild(this.display);
        this.group.addChild(this.title);
        this.group.addChild(this.pres_label);
        this.group.addChild(this.temp_label);

        // Define the center of the inlet and outlet of the Sensor for the connection lines, put in pixel units
        this.inlet =  new paper.Point([this.bounds.left, this.display.bounds.center.y]);
        this.outlet =  new paper.Point([this.bounds.right, this.display.bounds.center.y]);
    }

    // Method to update the text content
    updateText(newVals) {
        let formattedNumbers = newVals.map(num => `${num.toFixed(2)}`);
        console.log(formattedNumbers);

        this.pres_label.content = `${formattedNumbers[0]} psi`;
        this.flow_label.content = `${formattedNumbers[1]} sccm`;
        this.temp_label.content = `${formattedNumbers[2]} C`;
    }
    // Method to update the color of the display
    updateColor(newColor) {
        this.color = newColor;
        this.display.fillColor = newColor;
    }
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Custom shape class for the Gas Cylinder Component
class GasCylinderDiagramComponent extends FlowDiagramComponent{
    constructor(position, bounds) {
        // Call the superclass constructor
        super(position, bounds);

        // Create a rectangle representing a Gas Cylinder
        this.gasCyl = new paper.Path.Rectangle({
            point: position,
            size: bounds,
            strokeColor: 'black',
            strokeWidth: 2,
            fillColor: 'green'
        });

        // Create text for the Gas Cylinder
        this.gasCyl_text = new paper.PointText({
            point: new paper.Point(this.gasCyl.bounds.center.x, this.gasCyl.bounds.bottom + 20),
            justification: 'center',
            fillColor: 'black',
            fontWeight: 'bold',
            content: 'O2 Cylinder',
            fontSize: 20 // Set the font size
        });

        // Create a circle representing the valve of the Gas Cylinder
        this.gasCyl_valve = new paper.Path.Circle({
            center: new paper.Point(this.gasCyl.bounds.center.x, this.gasCyl.bounds.top),
            radius: 0.25*this.gasCyl.bounds.width,
            fillColor: 'black'
        });

        this.gasCyl_valve.insertBelow(this.gasCyl);

        // Define the center of the valve
        this.inlet = new paper.Point(this.gasCyl_valve.bounds.center);
        this.outlet = new paper.Point(this.gasCyl_valve.bounds.center);
    }
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Custom shape class for the Humidifier Component
class HumidifierDiagramComponent extends FlowDiagramComponent{
    constructor(position, bounds) {
        // Call the superclass constructor
        super(position, bounds);

        // Create a rectangle representing a Humidifier
        this.body = new paper.Path.Rectangle({
            point: position,
            size: bounds,
            strokeColor: 'black',
            strokeWidth: 2,
            fillColor: 'blue'
        });

        // Create text for the Humidifier
        let text_pos = [0.5, -0.2];
        this.text = new paper.PointText({
            point: text_pos.map((dim, index) => position[index] + dim * bounds[index]),
            justification: 'center',
            fillColor: 'black',
            fontWeight: 'bold',
            content: 'Humidifier',
            fontSize: 20
        });

        // Define the center of the valve
        this.inlet = new paper.Point([this.bounds.left, this.bounds.center.y]);
        this.outlet = new paper.Point([this.bounds.right, this.bounds.center.y]);
    }
}