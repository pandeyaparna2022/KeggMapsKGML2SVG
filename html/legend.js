// legend plugin version 1.0.0
// (c) 2024 Aparna Pandey
//
//
//
// Released under MIT license.

function createLegendForPresence(color) {
    const svgNamespace = "http://www.w3.org/2000/svg";

    // Create the SVG element
    let svg1 = document.createElementNS(svgNamespace, "svg");
    svg1.setAttribute("width", "100");
    svg1.setAttribute("height", "45");
    svg1.setAttribute("style", "border: 1px solid black");

    let rect = document.createElementNS(svgNamespace, "rect");
    rect.setAttribute("x", "0");
    rect.setAttribute("y", "0");
    rect.setAttribute("width", "20");
    rect.setAttribute("height", "40");
    rect.setAttribute("stroke", "black"); // Set stroke color to black
    rect.setAttribute("stroke-width", "2"); // Set stroke width
    rect.setAttribute("fill", "url(#color_gradient)");

    // Create text elements
    let presenceText = document.createElementNS(svgNamespace, "text");
    presenceText.setAttribute("x", "27");
    presenceText.setAttribute("y", "12");
    presenceText.setAttribute("font-family", "Arial");
    presenceText.setAttribute("font-size", "12");
    presenceText.setAttribute("fill", "black");
    presenceText.textContent ="Present";

    let absebceText = document.createElementNS(svgNamespace, "text");
    absebceText.setAttribute("x", "27");
    absebceText.setAttribute("y", "35");
    absebceText.setAttribute("font-family", "Arial");
    absebceText.setAttribute("font-size", "12");
    absebceText.setAttribute("fill", "black");
    absebceText.textContent = "Absent";


    // Create the <defs> element
    let defs = document.createElementNS(svgNamespace, "defs");

    var linearGradient = document.createElementNS(svgNamespace, "linearGradient");
    linearGradient.setAttribute("id", "color_gradient");
    linearGradient.setAttribute("x1", "0%");
    linearGradient.setAttribute("x2", "0%");
    linearGradient.setAttribute("y1", "0%");
    linearGradient.setAttribute("y2", "100%");

    // Define the gradient stops with a color variable
    const colors = [
        { offset: "0%", color: color }, // First color stop at 0% with the specified color
        { offset: "50%", color: "white" } // Second color stop at 50% with white color
    ];

    // Calculate the offset for color stops based on the number of colors
    let offset = 100 / colors.length; // This will be 50 for two colors
    let offset1 = 0; // Initialize the first offset to 0%
    let offset2 = offset; // Initialize the second offset to the calculated offset

    // Create and append each stop to the linearGradient
    colors.forEach((colorObj) => { // Iterate over each color object in the colors array
        // Create the first stop element
        let stopElement1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stopElement1.setAttribute('offset', offset1 + '%'); // Set the offset for the first stop
        stopElement1.setAttribute("style", `stop-color:${colorObj.color};stop-opacity:1`); // Set the color and opacity

        // Create the second stop element
        let stopElement2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stopElement2.setAttribute('offset', offset2 + '%'); // Set the offset for the second stop
        stopElement2.setAttribute("style", `stop-color:${colorObj.color};stop-opacity:1`); // Set the color and opacity

        // Append the <stop> elements to the <linearGradient> element
        linearGradient.appendChild(stopElement1); // Append the first stop
        linearGradient.appendChild(stopElement2); // Append the second stop

        // Update the offsets for the next iteration
        offset1 = offset2; // Move the first offset to the second
        offset2 += offset; // Increment the second offset by the calculated offset
    });

    // Append the linearGradient to <defs>
    defs.appendChild(linearGradient); // Add the linearGradient to the <defs> element


    // Append elements to the SVG
    svg1.appendChild(rect);
    svg1.appendChild(presenceText);
    svg1.appendChild(absebceText);
    svg1.appendChild(defs);

    // Append the SVG to the specified div
    const div = document.querySelector('div[id="map"]');
    if (div) {
        div.style.display = 'flex';
        div.appendChild(svg1);
    } else {
        console.error('Div with id "map" not found.');
    }
}




function createLegendForGradient(value_for_legend) {
    const svgNamespace = "http://www.w3.org/2000/svg";

    // Create the SVG element
    let svg1 = document.createElementNS(svgNamespace, "svg");
    svg1.setAttribute("width", "50");
    svg1.setAttribute("height", "400");
    svg1.setAttribute("style", "border: 1px solid transparent");

    let rect = document.createElementNS(svgNamespace, "rect");
    rect.setAttribute("x", "0");
    rect.setAttribute("y", "100");
    rect.setAttribute("width", "20");
    rect.setAttribute("height", "180");
    rect.setAttribute("fill", "url(#color_gradient)");

    // Create text elements
    let minValueText = document.createElementNS(svgNamespace, "text");
    minValueText.setAttribute("x", "27");
    minValueText.setAttribute("y", "112");
    minValueText.setAttribute("font-family", "Arial");
    minValueText.setAttribute("font-size", "12");
    minValueText.setAttribute("fill", "black");
    minValueText.textContent = -value_for_legend;

    let zeroText = document.createElementNS(svgNamespace, "text");
    zeroText.setAttribute("x", "27");
    zeroText.setAttribute("y", "196");
    zeroText.setAttribute("font-family", "Arial");
    zeroText.setAttribute("font-size", "12");
    zeroText.setAttribute("fill", "black");
    zeroText.textContent = "0";

    let maxValueText = document.createElementNS(svgNamespace, "text");
    maxValueText.setAttribute("x", "27");
    maxValueText.setAttribute("y", "280");
    maxValueText.setAttribute("font-family", "Arial");
    maxValueText.setAttribute("font-size", "12");
    maxValueText.setAttribute("fill", "black");
    maxValueText.textContent = value_for_legend;

    // Create the <defs> element
    let defs = document.createElementNS(svgNamespace, "defs");

    var linearGradient = document.createElementNS(svgNamespace, "linearGradient");
    linearGradient.setAttribute("id", "color_gradient");
    linearGradient.setAttribute("x1", "0%");
    linearGradient.setAttribute("x2", "0%");
    linearGradient.setAttribute("y1", "0%");
    linearGradient.setAttribute("y2", "100%");

    // Define the gradient stops
    const colors = [
        { offset: "0%", color: "#CD0000" },
        { offset: "10%", color: "#C92F2F" },
        { offset: "20%", color: "#C55F5F" },
        { offset: "30%", color: "#C18E8E" },
        { offset: "40%", color: "#BEBEBE" },
        { offset: "50%", color: "#FFFFFF" },
        { offset: "60%", color: "#BEBEBE" },
        { offset: "70%", color: "#8ECE8E" },
        { offset: "80%", color: "#5FDE5F" },
        { offset: "90%", color: "#2FEE2F" },
        { offset: "100%", color: "#00FF00" }
    ];

    // Create and append each stop to the linearGradient
    colors.forEach(color => {
        let stop = document.createElementNS(svgNamespace, "stop");
        stop.setAttribute("offset", color.offset);
        stop.setAttribute("style", `stop-color:${color.color};stop-opacity:1`);
        linearGradient.appendChild(stop);
    });

    // Append the linearGradient to <defs>
    defs.appendChild(linearGradient);

    // Append elements to the SVG
    svg1.appendChild(rect);
    svg1.appendChild(minValueText);
    svg1.appendChild(zeroText);
    svg1.appendChild(maxValueText);
    svg1.appendChild(defs);

    // Append the SVG to the specified div
    const div = document.querySelector('div[id="play"]');
    if (div) {
        div.style.display = 'flex';
        div.appendChild(svg1);
    } else {
        console.error('Div with id "play" not found.');
    }
}
