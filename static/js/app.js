//Define State variables
let isRecording = false;
const DEFAULT_SAVE_DIRECTORY = '/Users/benjamin/Downloads'

// Define the components of the system
const components = {
    'MFC1': new MFC('MFC1', '/MFC1'),
    'MFC2': new MFC('MFC2', '/MFC2'),
    'SHT1': new Sensor('SHT1', '/SHT1'),
    'SHT2': new Sensor('SHT2', '/SHT2'),
    'test1': new DAQ('Test1', '/test1'),
    'test2': new DAQ('Test2', '/test2'),
    'test3': new DAQ('Test3', '/test3'),
};

// Initialize the plots
const plots = {
    'main_plot': new ScrollingPlot('Main plot', 'flowPlot_main', 20),
    'subplot1': new ScrollingPlot('Subplot 1', 'flowPlot_sub1', 20),
    'subplot2': new ScrollingPlot('Subplot 2', 'flowPlot_sub2', 20)
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

    $('#reinitializePlotsButton').click(initPlots); // Reinitialize the plots

    //Radio buttons for control mode
    $('#setpointControlButton').change(handleSetpointControlButton);
    $('#manualControlButton').change(handleManualControlButton);
    $('#arbitraryControlButton').change(handleArbitraryControlButton);

    $('#startRecordingButton').click(handleStartRecordingButton);       //Form submission for saving the file and recording data
    $('#abortRecordingButton').click(handleAbortRecordingButton);       //Abort the recording

    //Event listeners for the modal form submission
    $('#sensorForm').submit((e) => {
        e.preventDefault(); // Prevent the default form submission
    });
    $('#mfcForm').submit((e) => {
        e.preventDefault(); // Prevent the default form submission
    });


    console.log('Document Ready');
});

// Loop function to refresh the site
setInterval(async () => {

    const frameData = await getData();
    updatePlots(frameData);
    updateDiagramText(frameData);
    updateConnectionStatus();
}, 1000); 


// --------------------------------
// FUNCTIONS    
// ----------------------------
async function setupSite() {
    // Draw the Flow Diagram for the system
    drawFlowDiagram();

    // Update the status of the system
    //Check the connection status of the components, the function will also update the HTML status
    for (let key in components) {
        components[key].checkConnection();
    }
    initPlots();

    // Update the recording status
    //TODO: Check if the system is recording data
    updateRecordingStatusHTML();
}

async function initPlots() {
    // Fetch data from all the components, initialize the plots
    const frameData = await getData();

    plots['main_plot'].initializePlot( processMainplot(frameData) );
    plots['subplot1'].initializePlot( processSubplot1(frameData) );
    plots['subplot2'].initializePlot( processSubplot2(frameData) );
}

async function updatePlots(frameData){
    try {
        plots['main_plot'].updatePlot( processMainplot(frameData) );
    } catch (error) {    }

    try {
        plots['subplot1'].updatePlot( processSubplot1(frameData) );
    } catch (error) {    }

    try {
        plots['subplot2'].updatePlot( processSubplot2(frameData) );
    } catch (error) {    }
}

// Update the connection status of the components
function updateConnectionStatus() {
    for (let key in components) {
        components[key].checkConnection();
    }
}

// Update the text of the diagram
function updateDiagramText(frameData) {
    //FrameData has the polled data of all components, get the last set of values from each component
    for (let key in components) {
        const data = frameData[key];
        const lastValues = Object.fromEntries(
            Object.entries(data).map(([property, value]) => [property, value.values[value.values.length - 1]])
        );

        // Submit the last set of values to the update function of the component
        components[key].updateDiagramText(lastValues);
    }
}

async function getData(){
    // Fetch data from all the components
    data = {};
    for (let key in components) {
        data[key] = await components[key].fetchData();
    }
    return data;
}

//Process the data to be plotted, basically extract the relevant data from the frameData.
//This defines what each plot will show
function processMainplot(frameData) {
    data = {
            MFC1_flowrate: frameData['MFC1']['flowrate'], 
            MFC2_flowrate: frameData['MFC2']['flowrate'],
            SHT1_temperature: frameData['SHT1']['temperature'], 
            SHT1_humidity: frameData['SHT1']['humidity'],
            SHT2_temperature: frameData['SHT2']['temperature'],
            SHT2_humidity: frameData['SHT2']['humidity'],
            test1_y1: frameData['test1']['y1'],
            test1_y2: frameData['test1']['y2'],
    };

    return data;
}

function processSubplot1(frameData) {
    data = {
        MFC1_flowrate: frameData['MFC1']['flowrate'],
        MFC1_setpoint: frameData['MFC1']['setpoint'],
    };
    return data;
}

function processSubplot2(frameData) {
    data = {
        MFC2_flowrate: frameData['MFC2']['flowrate'],
        MFC2_setpoint: frameData['MFC2']['setpoint'],
    };
    return data;
}



// Draw the Flow Diagram for the system
function drawFlowDiagram() {
    paper.setup('FlowDiagram');

    let MFC1 = components['MFC1'];
    let MFC2 = components['MFC2'];
    let sensor1 = components['SHT1'];
    let sensor2 = components['SHT2'];

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
    $('#manualControlParams').addClass('d-none');         // Hide the manual control parameters
    $('#arbitrary-settings').addClass('d-none');       // Hide the arbitrary setpoint settings
    $('#setpointControlParams').removeClass('d-none');    // Show the setpoint control parameters
    $('#controlSettings-submitButton').removeClass('d-none'); // Show the submit button for the control settings
}

function handleManualControlButton() {
    $('#setpointControlParams').addClass('d-none');    // Hide the setpoint control parameters
    $('#arbitrary-settings').addClass('d-none');       // Hide the arbitrary setpoint settings
    $('#manualControlParams').removeClass('d-none');  // Show the manual control parameters
    $('#controlSettings-submitButton').removeClass('d-none'); // Show the submit button for the control settings
}

function handleArbitraryControlButton() {
    $('#setpointControlParams').addClass('d-none');         // Hide the setpoint control parameters
    $('#manualControlParams').addClass('d-none');         // Hide the manual control parameters
    $('#controlSettings-submitButton').addClass('d-none'); // Hide the submit button for the control settings
    $('#arbitrary-settings').removeClass('d-none');       // Show the arbitrary setpoint settings
}

//Start Recording button handler
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
        isRecording = true;
        updateRecordingStatusHTML();
    }
}

//Abort Recording button handler
function handleAbortRecordingButton() {
    console.log('Abort Recording');
    isRecording = false;
    updateRecordingStatusHTML();
}

//Function to handle the recording status HTML
// Disables the Start Recording button and enables the Abort Recording button when recording
// or vice versa
// Also changes the alert text and class to indicate the recording status
function updateRecordingStatusHTML() {
    if (isRecording) {
        $('#recordingStatusAlert').removeClass('alert-secondary').addClass('alert-success');       // Change the alert class to success
        $('#recordingStatusAlert-text').text('Data Recording');                                  // Change the alert text
        $('#startRecordingButton').prop('disabled', true);                                      // Disable the start recording button
        $('#abortRecordingButton').prop('disabled', false);                                       // Enable the abort recording button
    } else {
        $('#recordingStatusAlert').removeClass('alert-success').addClass('alert-secondary');    // Change the alert class to light
        $('#recordingStatusAlert-text').text('Data Not Recording');                                  // Change the alert text
        $('#startRecordingButton').prop('disabled', false);                                                      // Enable the start recording button
        $('#abortRecordingButton').prop('disabled', true);                                                     // Disable the abort recording button
    }
}
