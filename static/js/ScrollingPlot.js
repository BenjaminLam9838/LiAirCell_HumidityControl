
/**
 * Represents a custom plot.  Intended to be used with Plotly.js and custom Component class in python.
 * @class
 */
class ScrollingPlot {
    constructor(plotTitle, htmlElementId, MAX_TIME_WINDOW_s = 10, yRange = [0, 100]) {
        this.plotTitle = plotTitle;
        this.htmlElementId = htmlElementId;
        this.MAX_TIME_WINDOW_ms = MAX_TIME_WINDOW_s*1000;

        this.layout = {
            title: { text: this.plotTitle, x: 0, font: { family: 'Arial, sans-serif', weight: 'bold' } },
            xaxis: { title: 'X Axis' },
            yaxis: { title: 'Y Axis', range: yRange },
            showlegend: true,
            margin: {
                l: 50,  // left margin in pixels
                r: 50,  // right margin in pixels
                t: 50,  // top margin in pixels
                b: 50,  // bottom margin in pixels
                pad: 5  // padding around the plot area in pixels
            }
        };
    }
    

    // Create traces dynamically from dictionary data
    makeTraces(data) {
        const traces = [];

        Object.keys(data).forEach(key => {
            //There may be errors if the data is not in the expected format
            try {
                const x = data[key]['data'].datetime;   //Get the x and y values from the data
                const y = data[key]['data'].values;
                const marker = data[key]['marker'];     //Get the marker from the data

                const trace = {
                    x: x,
                    y: y,
                    mode: 'lines+markers',
                    marker: marker,
                    name: `${key.toUpperCase()}`
                };
                traces.push(trace);
            } catch (error) {
                console.debug('Could not make trace, likely no data found: ', `Trace Key: ${key}`, error);
                return [];
            }
        });
        return traces;
    }

    // Initialize the plot
    initializePlot(data) {
        console.log('Initializing plot with data: ', data);
        const newTraces = this.makeTraces(data);
        console.log('New traces: ', newTraces);
        if (newTraces.length === 0) {
            return;
        }

        // Plot a new plot
        Plotly.react(this.htmlElementId, newTraces, this.layout);       
        this.scrollXAxis(document.getElementById(this.htmlElementId));
    }

    updatePlot(data) {
        if (data.length === 0) {
            return;
        }
    
        const graphDiv = document.getElementById(this.htmlElementId);
        const newTraces = this.makeTraces(data); // Create new traces from new data
        if (newTraces.length === 0) {
            console.debug(`${this.plotTitle}: `, 'Could not update traces');
            return;
        }

        // Extend existing traces with new data points, otherwise add new traces
        newTraces.forEach((trace) => {
            //Get the index of the trace with the same name in graphDiv.data
            const index = graphDiv.data.findIndex((element) => element.name === trace.name);

            //If the trace exists, extend it, otherwise add a new trace
            if (index !== -1) {
                // Extend existing trace
                Plotly.extendTraces(this.htmlElementId, {
                    x: [trace.x],
                    y: [trace.y]
                }, [index]);
            } else {
                // Add new trace
                Plotly.addTraces(this.htmlElementId, trace);
            }
        });
        
        // Scale the x-axis to show the last MAX_TIME_WINDOW_s seconds of data (scrolling effect)
        this.scrollXAxis(graphDiv);
    }

    scrollXAxis(graphDiv) {
        // Variables to track the global x-axis range, this tracks the latest x-value across all traces
        let globalMaxX = Number.NEGATIVE_INFINITY;

        // Maintain a fixed time window for the x-axis and trim the data accordingly
        graphDiv.data.forEach(trace => {
            // Assuming x values are time-based and sorted in ascending order
            const maxX = Math.max(...trace.x);
            const minX = maxX - this.MAX_TIME_WINDOW_ms;

            // Update the global min and max x-values
            if (maxX > globalMaxX) globalMaxX = maxX;

            // Filter the trace data to keep only points within the time window
            const validIndices = trace.x.map((value, index) => value >= minX ? index : -1).filter(index => index !== -1);

            trace.x = validIndices.map(index => trace.x[index]);
            trace.y = validIndices.map(index => trace.y[index]);

            // console.log(trace.name, trace.x);
        });

        // console.log([globalMaxX-this.MAX_TIME_WINDOW_ms, globalMaxX]);
        // Perform a single relayout to update the x-axis range
        Plotly.relayout(this.htmlElementId, {
            'xaxis.range': [globalMaxX-this.MAX_TIME_WINDOW_ms, globalMaxX],
        });
    }
}
