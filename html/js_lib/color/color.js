// clickevent plugin version 1.0.0
// (c) 2024 Aparna Pandey
//
// Released under MIT license.

function colorAll(color = 'blue') {
  
  // Get all shape elements
  const groupElement = document.querySelector('g[name="shapes"]'); // Select all <g> elements
  const shapes = groupElement.querySelectorAll('circle, rect, path'); 

  // Set the fill and stroke of each element to the specified color
  shapes.forEach(shape => {
      shape.setAttribute('fill', color);
      shape.setAttribute('stroke', color);
      shape.setAttribute('stroke-width', '3');
      shape.setAttribute('fill-opacity', '0.15');
  });
}

function colorOrg(org, color = 'blue') {
  // Get all shape elements
  const groupElement = document.querySelector('g[name="shapes"]'); // Select the <g> element
  const shapes = groupElement.querySelectorAll('circle, rect, path'); 
  const appliedColors = [];
  // Set the fill and stroke of each element to the specified color
  shapes.forEach(shape => {
      let titleElement = shape.getElementsByTagName('title')[0]; // Access title for the current shape
      //console.log(titleElement)

      // Extract the title text if the title element exists
      if (titleElement) {
          const titleText = eval(titleElement.textContent); // Use caution with eval
          const query = org + ":";
          //console.log(query)
          // Check if the title text contains the organism prefix
          if (titleText.some(item => item.includes(query))) {
              shape.setAttribute('stroke', color);
              shape.setAttribute('stroke-width', '3');
              shape.setAttribute('fill', color);
              shape.setAttribute('fill-opacity', '0.15');

              // Add the color to the appliedColors array
              appliedColors.push(color);
          }
      }
  });

  // Return the list of applied colors
      return appliedColors;
 
}

function defineLegend(colors, colorFunc) {
  const STROKE = 'black'; // Assuming a default stroke color, modify as needed

  const svgWidth = parseInt(document.getElementById('svg-container').querySelector('svg').getBoundingClientRect().width);
  //const svgWidth = a.getBoundingClientRect().width;
  //console.log(svgWidth);


  // Create the inner rectangle for "Absent"
  const innerRect1 = document.createElementNS("http://www.w3.org/2000/svg", 'rect');
  innerRect1.setAttribute('x', String(svgWidth-190));
  innerRect1.setAttribute('y', "10");
  innerRect1.setAttribute('fill', 'white');
  innerRect1.setAttribute('stroke', STROKE);
  innerRect1.setAttribute('width', String(20));
  innerRect1.setAttribute('height', String(20));
  innerRect1.setAttribute('style', "pointer-events: none");

  // Create the text element for "Absent"
  const textElement1 = document.createElementNS("http://www.w3.org/2000/svg", 'text');
  textElement1.setAttribute('x', String(svgWidth -160));
  textElement1.setAttribute('y', "25");
  textElement1.setAttribute('fill', "black");
  textElement1.setAttribute('style', "font-size: 18px; pointer-events: none");
  textElement1.textContent = "Absent";

  document.getElementById('svg-container').querySelector('svg').appendChild(innerRect1);
  document.getElementById('svg-container').querySelector('svg').appendChild(textElement1);



  let yCoordText = 45;
  let yCoordRect = 30;
  const filteredColors = [...new Set(colors.filter(color => color !== 'white'))];

  if (filteredColors.length === 1) {
      const innerRect2 = document.createElementNS("http://www.w3.org/2000/svg", 'rect');
      innerRect2.setAttribute('x', String(svgWidth-190));
      innerRect2.setAttribute('y', String(yCoordRect));
      innerRect2.setAttribute('fill', filteredColors[0]);
      innerRect2.setAttribute('stroke', STROKE);
      innerRect2.setAttribute('width', String(20));
      innerRect2.setAttribute('height', String(20));
      innerRect2.setAttribute('style', "pointer-events: none");

      // Create the text element for "Present"
      const textElement2 = document.createElementNS("http://www.w3.org/2000/svg", 'text');
      textElement2.setAttribute('x', String(svgWidth -160));
      textElement2.setAttribute('y', String(yCoordText));
      textElement2.setAttribute('fill', "black");
      textElement2.setAttribute('style', "font-size: 18px; pointer-events: none");
      textElement2.textContent = "Present";

      document.getElementById('svg-container').querySelector('svg').appendChild(innerRect2);
      document.getElementById('svg-container').querySelector('svg').appendChild(textElement2);
  } else if (filteredColors.length > 1) {
      let counter = 0;
      for (const color of filteredColors) {
          // Create the inner rectangle for each color
          const innerRect2 = document.createElementNS("http://www.w3.org/2000/svg", 'rect');
          innerRect2.setAttribute('x', String(svgWidth-190));
          innerRect2.setAttribute('y', String(yCoordRect));
          innerRect2.setAttribute('fill', color);
          innerRect2.setAttribute('stroke', STROKE);
          innerRect2.setAttribute('width', String(20));
          innerRect2.setAttribute('height', String(20));
          innerRect2.setAttribute('style', "pointer-events: none");

          // Create the text element for each color
          const textElement2 = document.createElementNS("http://www.w3.org/2000/svg", 'text');
          textElement2.setAttribute('x', String(svgWidth -160));
          textElement2.setAttribute('y', String(yCoordText));
          textElement2.setAttribute('fill', "black");
          textElement2.setAttribute('style', "font-size: 18px; pointer-events: none");

          if (colorFunc.name === "color_custom_annotations") {
              counter += 1;
              textElement2.textContent = "org/genome: " + counter;
          } else if (colorFunc.name === "add_linear_gradient_groups") {
              counter += 25;
              textElement2.textContent = "%_org_in_group: <=" + counter;
          }

          // Append the inner rectangle and text element to the document

          document.getElementById('svg-container').querySelector('svg').appendChild(innerRect2);
          document.getElementById('svg-container').querySelector('svg').appendChild(textElement2);

     
          yCoordText += 20;
          yCoordRect += 20;
      }
  }
}

function colorCustomAnnotations(query, ...args) {

    console.log(args)
  // Return early if the query is empty
  if (Object.keys(query).length === 0) {
    return null;
}


  // Determine the color to use; default to 'blue' if not provided
  let color = args.length > 0 ? args[0] : Array(query.length).fill('blue');

  if (!Array.isArray(color)) {
      color = [color];
  }
  


    // Get all shape elements
    const groupElement = document.querySelector('g[name="shapes"]'); // Select the <g> element
    const shapes = groupElement.querySelectorAll('circle, rect, path'); 
  
    // If the length of query is less than 5 execute the following commands
    if (Object.keys(query).length < 5) {

        
        shapes.forEach(shape => { // Corrected from shape to shapes
  
          let titleElement = shape.getElementsByTagName('title')[0]; // Access title for the current shape
          let titleText = titleElement ? titleElement.textContent.split(', ') : []; // Extract title text
          
          /** Color only shapes with indicated annotation blue */
          let colors = [];

          let counter = 0;
    
          // Parse the string to convert it into an object
          const jsonString = query[0].replace(/'/g, '"'); // Replace single quotes with double quotes
         
          const genomes = JSON.parse(jsonString); // Parse the JSON string
          
          for (let queryDict of  genomes) {
            // Extract the number of key-value pairs
            let numKeyValuePairs = Object.keys(queryDict).length; // This gives the count of keys
            
            let color = args.length > 0 ? args[0] : Array(numKeyValuePairs).fill('blue');

    
          // Iterate over each key-value pair in the query
          for (let [key, values] of Object.entries(queryDict)) {
              // Check if any value in the list of values of the query dictionary matches the title text

              if (values.some(value => titleText.some(item => item.includes(value)))) {
                  colors.push(color[counter]); // Add the specified color
              } else {
                  colors.push('white'); // Default to white
              }
              
              // Update title text based on matches
              values.forEach(value => {
                  if (titleText.some(item => item.includes(value))) {
                      // Create a new list to replace items
                      let updatedTitleText = [];
                      // Update title text with the key
                      titleText.forEach(item => {
                          if (item.includes(value)) {
                            updatedTitleText.push(`'${key}:${item.replace(/'/g, "")}'`);
                              
                              shape.setAttribute('fill-opacity', '0.5'); // Set opacity
                              
                              // If the length of queries is 1 then the shape will be filled with specified color
                              if (numKeyValuePairs === 1) {
                                  //console.log(numKeyValuePairs)
                                  shape.setAttribute('fill', color[0]);
                              }
                          } else {
                              updatedTitleText.push(item); // Keep the original item if conditions are not met
                          }
                      });
                      // Replace the titleText with updatedTitleText
                      titleElement.textContent = updatedTitleText.join(', ');
                  }
              });
              counter++;
          }
        }
  
          // Executed when length of queries is more than 1
          // Check if any color is not white
         if (colors.length > 1 && colors.some(c => c !== 'white')) {
              // Create a new definitions element
              let defs = document.createElement('defs');
              let defs1 = document.querySelector('defs#shape-color-defs');

              defs1 = setGradient(shape.getAttribute('shape_id'), shape, defs1, colors); // Set gradient
              //document.getElementById('svg-container').querySelector('svg').appendChild(defs); // Append definitions to root
          }
        });
    }
  
    return color;
  }

  function setGradient(anno, shapeElement, defs, colors = ['yellow', 'red', 'blue', 'green']) {
    const gradientId = 'gradient_' + anno;

    // Calculate the offset for each color
    const offset = 100 / colors.length;

    // Create a <linearGradient> element with the generated gradientId and attributes
    const gradientElement = document.createElementNS("http://www.w3.org/2000/svg", 'linearGradient');
    gradientElement.setAttribute('id', gradientId);
    gradientElement.setAttribute('x1', '0%');
    gradientElement.setAttribute('y1', '0%');
    gradientElement.setAttribute('x2', '100%');
    gradientElement.setAttribute('y2', '0%');

    let offset1 = 0;
    let offset2 = offset;

    // Create <stop> elements for all the colors
    colors.forEach((color) => {
        const stopElement1 = document.createElementNS("http://www.w3.org/2000/svg", 'stop');
        stopElement1.setAttribute('offset', offset1 + '%');
        stopElement1.setAttribute('stop-color', color);
        gradientElement.appendChild(stopElement1);

        const stopElement2 = document.createElementNS("http://www.w3.org/2000/svg", 'stop');
        stopElement2.setAttribute('offset', offset2 + '%');
        stopElement2.setAttribute('stop-color', color);
        gradientElement.appendChild(stopElement2);

        // Update the offset values for the next color stop
        offset1 = offset2;
        offset2 += offset;
    });

    // Append the gradient element to the defs
    defs.appendChild(gradientElement);

    // Set the 'fill' and 'stroke' attributes of the shapeElement to reference the gradientId
    shapeElement.setAttribute('fill', 'url(#' + gradientId + ')');
    shapeElement.setAttribute('stroke', 'url(#' + gradientId + ')');

    return defs;
}









