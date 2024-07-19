
/**
 * Represents a custom plot.  Intended to be used with Plotly.js and custom Component class in python.
 * @class
 */
class ScrollingPlot {
    constructor(plotTitle, htmlElementId, MAX_POINTS = 1000) {
        this.plotTitle = plotTitle;
        this.htmlElementId = htmlElementId;
        this.MAX_POINTS = MAX_POINTS;

        this.layout = {
            title: this.plotTitle,
            xaxis: { title: 'X Axis' },
            yaxis: { title: 'Y Axis' },
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
                const x = data[key].datetime;   //Get the x and y values from the data
                const y = data[key].values;
                
                const trace = {
                    x: x,
                    y: y,
                    mode: 'lines+markers',
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
        const newTraces = this.makeTraces(data);
        if (newTraces.length === 0) {
            return;
        }

        // Plot a new plot
        Plotly.react(this.htmlElementId, newTraces, this.layout);       
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
        newTraces.forEach((trace, index) => {
            try {
                Plotly.extendTraces(this.htmlElementId, {
                    x: [trace.x],
                    y: [trace.y]
                }, [index]);
            } catch (error) {
                Plotly.addTraces(this.htmlElementId, trace);
            }
        });

        // Maintain a fixed number of points in the plot
        const currentLength = graphDiv.data[0].x.length;

        if (currentLength > this.MAX_POINTS) {
            const excess = currentLength - this.MAX_POINTS;
    
            // Slice the data to remove excess points
            graphDiv.data.forEach(trace => {
                trace.x = trace.x.slice(excess);
                trace.y = trace.y.slice(excess);
            });
    
            const minY = [];
            const maxY = [];
            
            // Collect min and max values for all traces
            graphDiv.data.forEach(trace => {
                minY.push(Math.min(...trace.y));
                maxY.push(Math.max(...trace.y));
            });
    
            // Calculate buffer based on the range of all data
            const yBuffer = 0.1 * (Math.max(...maxY) - Math.min(...minY));
            
            Plotly.relayout(this.htmlElementId, {
                'xaxis.range': [graphDiv.data[0].x[0], graphDiv.data[0].x[graphDiv.data[0].x.length - 1]],
                'yaxis.range': [
                    Math.min(...minY) - yBuffer,
                    Math.max(...maxY) + yBuffer,
                ]
            });
        }
    }
    

}
