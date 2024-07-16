//Define State variables
let isRecording = false;
const DEFAULT_SAVE_DIRECTORY = '/Users/benjamin/Downloads'

// Define the components of the system
const components = {
    'MFC1': new MFC('MFC1', '/MFC1'),
    'MFC2': new MFC('MFC2', '/MFC2'),
    'sensor1': new Sensor('SHT1', '/SHT1', 0x0F),
    'sensor2': new Sensor('SHT2', '/SHT2', 0x1F),
    'test1': new DAQ('Test1', '/test1'),
    'test2': new DAQ('Test2', '/test2'),
    'test3': new DAQ('Test3', '/test3'),
};

// Initialize the plots
const plots = {
    'main_plot': new ScrollingPlot('Test1', 'flowPlot_main', 100),
    'subplot1': new ScrollingPlot('Test 2', 'flowPlot_sub1', 50),
    'subplot2': new ScrollingPlot('Test 3', 'flowPlot_sub2', 10)
};


$(document).ready(function() {
    setupSite();

    $('#dataRecordingFile').val(DEFAULT_SAVE_DIRECTORY); // Set the default save directory

    // Event listeners for the control buttons
    //Button to show the arbitrary flow modal
    $('#arbitrarySetpointModal-Button').click(() => {
        $('#arbitrarySetpointModal').modal('show');
        console.log('Arbitrary Flow Button Clicked');
    });

    //Radio buttons for control mode
    $('#setpointControlButton').change(handleSetpointControlButton);
    $('#manualControlButton').change(handleManualControlButton);

    $('#startRecordingButton').click(handleStartRecordingButton);       //Form submission for saving the file and recording data
    $('#abortRecordingButton').click(handleAbortRecordingButton);       //Abort the recording
    console.log('Document Ready');
});
setInterval(() => {
    updateSite();
}, 1000); 

async function setupSite() {
    // Draw the Flow Diagram for the system
    drawFlowDiagram();

    // Update the status of the system
    //Check the connection status of the components, it will update the HTML status
    for (let key in components) {
        components[key].checkConnection();
    }

    // Fetch data from all the components, initialize the plots
    const frameData = await getData();

    main_plot_data = frameData['test1'];
    // add the test2 data to the main plot
    main_plot_data['test3 y1'] = frameData['test3']['y1'];

    plots['main_plot'].initializePlot(frameData['test1']);
    plots['subplot1'].initializePlot(frameData['test2']);
    plots['subplot2'].initializePlot(frameData['test3']);
}

async function updateSite(){
    const frameData = await getData();
    
    const main_plot_data = frameData['test1'];
    main_plot_data['test3 y1'] = frameData['test3']['y1'];

    plots['main_plot'].updatePlot(main_plot_data);
    plots['subplot1'].updatePlot(frameData['test2']);
    plots['subplot2'].updatePlot(frameData['test3']);
}

async function getData(){
    // Fetch data from all the components
    data = {};
    for (let key in components) {
        data[key] = await components[key].fetchData();
    }
    return data;
}



// Function to create a dummy Plotly graph
function createDummyGraph(id) {
    const trace = {
        x: [1, 2, 3, 4, 5],
        y: [1, 3, 2, 5, 4],
        type: 'scatter'
    };
    const layout = {
        title: `Graph ${id}`,
        xaxis: { title: 'X Axis' },
        yaxis: { title: 'Y Axis' }
    };
    Plotly.newPlot(id, [trace], layout);
}



// Draw the Flow Diagram for the system
function drawFlowDiagram() {
    paper.setup('FlowDiagram');

    let MFC1 = components['MFC1'];
    let MFC2 = components['MFC2'];
    let sensor1 = components['sensor1'];
    let sensor2 = components['sensor2'];

    // Make the gas cylinder
    const gascyl = new GasCylinderDiagramComponent([50, 120], [80, 300]);

    // Make the MFCs
    MFC1.drawDiagram([250, 10],  [190, 190]);
    MFC2.drawDiagram([250, 225], [190, 190]);

    // Make the humidifier
    //Align the humidifier inlet with the MFC outlet
    const humidifierHeight = 35;
    const humidifier_y = MFC2.diagram.outlet.y - humidifierHeight/2;
    const humidifier_x = MFC2.diagram.outlet.x + 30;
    const humidifier = new HumidifierDiagramComponent([humidifier_x, humidifier_y], [100, humidifierHeight], 'Humidifier');

    // Make Sensor 1 (Output of the system)
    //Align the sensor1 with the MFC1
    const sensor1Size = 50;
    const sensor1_x = 750;
    const sensor1_y = MFC1.diagram.outlet.y - sensor1Size/2;
    sensor1.drawDiagram([sensor1_x, sensor1_y], [sensor1Size, 2*sensor1Size]);

    // Make Sensor 2 (Humidifier Output)
    //Align the sensor2 with the humidifier
    const sensor2Size = 50;
    const sensor2_x = humidifier.outlet.x + 40;
    const sensor2_y = humidifier.outlet.y - sensor2Size/2;
    sensor2.drawDiagram([sensor2_x, sensor2_y], [sensor2Size, 2*sensor2Size])

    // Draw the lines connecting the components to denote flow
    gascyl.routeLineTo(MFC1.diagram, [
        [gascyl.outlet.x, gascyl.outlet.y - 50],
        [(gascyl.outlet.x + MFC1.diagram.inlet.x)/2, gascyl.outlet.y - 50],
        [(gascyl.outlet.x + MFC1.diagram.inlet.x)/2, MFC1.diagram.inlet.y]
    ]);
    gascyl.routeLineTo(MFC2.diagram, [
        [gascyl.outlet.x, gascyl.outlet.y - 50],
        [(gascyl.outlet.x + MFC2.diagram.inlet.x)/2, gascyl.outlet.y - 50],
        [(gascyl.outlet.x + MFC2.diagram.inlet.x)/2, MFC2.diagram.inlet.y]
    ]);
    MFC2.diagram.routeLineTo(humidifier);
    humidifier.routeLineTo(sensor2.diagram);
    MFC1.diagram.routeLineTo(sensor1.diagram);
    sensor2.diagram.routeLineTo(sensor1.diagram, [
        [(sensor2.diagram.outlet.x + sensor1.diagram.inlet.x)/2, sensor2.diagram.outlet.y],
        [(sensor2.diagram.outlet.x + sensor1.diagram.inlet.x)/2, sensor1.diagram.inlet.y]
    ]);

    // Draw an arrow to denote the output of the system
    const arrowLength = 100;
    const arrow = new paper.Path({
        segments: [[sensor1.diagram.outlet.x, sensor1.diagram.outlet.y], [sensor1.diagram.outlet.x + arrowLength, sensor1.diagram.outlet.y]],
        strokeColor: 'black',
        strokeWidth: 5
    });
    //Make the arrowhead
    const arrowhead = new paper.Path.RegularPolygon({
        center: [sensor1.diagram.outlet.x + arrowLength, sensor1.diagram.outlet.y],
        sides: 3,
        radius: 10,
        fillColor: 'black'
    });
    arrowhead.rotate(90, [sensor1.diagram.outlet.x + arrowLength, sensor1.diagram.outlet.y]);
    //Label the output
    const text = new paper.PointText({
        point: [arrow.bounds.right-15, arrow.bounds.top-10],
        content: 'Flow Out',
        fillColor: 'black',
        fontSize: 20
    });
}


function handleSetpointControlButton() {
    $('#setpointControlParams').removeClass('d-none');    // Show the setpoint control parameters
    $('#manualControlParams').addClass('d-none');         // Hide the manual control parameters
}

function handleManualControlButton() {
    $('#setpointControlParams').addClass('d-none');    // Hide the setpoint control parameters
    $('#manualControlParams').removeClass('d-none');  // Show the manual control parameters
}

function handleStartRecordingButton() {
    console.log('Start Recording');
    // Handle the form submission
    $('#saveFileForm').submit(() => {
        e.preventDefault(); // Prevent the default form submission
        console.log('Save File form submitted');
    });

    const serverSuccess = true; // Assume the server responds with success
    //Change the alert class to success, if the server responds with a success message
    if (serverSuccess) {
        console.log('Data Save Directory:', $('#dataRecordingFile').val());
        $('#recordingStatusAlert').removeClass('alert-secondary').addClass('alert-success');    // Change the alert class to success
        $('#recordingStatusAlert-text').text('Data Recording');                                  // Change the alert text
        $('#startRecordingButton').prop('disabled', true);                                                 // Disable the start recording button
        $('#abortRecordingButton').prop('disabled', false);                                                  // Enable the abort recording button
        isRecording = true;
    }
}

function handleAbortRecordingButton() {
    console.log('Abort Recording');
    $('#recordingStatusAlert').removeClass('alert-success').addClass('alert-secondary');    // Change the alert class to light
    $('#recordingStatusAlert-text').text('Data Not Recording');                                  // Change the alert text
    $('#startRecordingButton').prop('disabled', false);                                                      // Enable the start recording button
    $('#abortRecordingButton').prop('disabled', true);                                                     // Disable the abort recording button
    isRecording = false;
}
