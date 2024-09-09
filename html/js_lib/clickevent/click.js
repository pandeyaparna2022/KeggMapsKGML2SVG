// clickevent plugin version 1.0.0
// (c) 2024 Aparna Pandey
//
//
//
// Released under MIT license.
function addOnClickToShapes() {
  // Get all shape elements
  const groupElement = document.querySelector('g[name="shapes"]');
  const shapes = groupElement.querySelectorAll('circle, rect, path');

  // Loop through each shape element
  shapes.forEach((shape) => {
    // Add contextmenu event listener
    shape.addEventListener('contextmenu', (event) => showContextMenu(event, shape));
  });
}

function showContextMenu(event, element) {
  let descMenuHeight = 0; // Variable to store the height of the description menu
  event.preventDefault(); // Prevent the default context menu
  const contextMenu = document.createElement('div');
  contextMenu.className = 'context-menu';
  contextMenu.style.position = 'absolute';
  contextMenu.style.left = `${event.pageX}px`;
  contextMenu.style.top = `${event.pageY}px`;
  contextMenu.style.backgroundColor = 'pink'; // Set background color to blue
  contextMenu.style.color = 'white'; // Optional: Set text color to white for better contrast
  contextMenu.style.padding = '10px'; // Optional: Add some padding
  contextMenu.style.borderRadius = '5px'; // Optional: Add rounded corners

  // Get title and description
  const titleText = element.querySelector("title").textContent;
  const cleanedString = titleText
    .replace(/'/g, '"') // Replace single quotes with double quotes
    .replace(/\\n/g, '\\n') // Ensure newlines are escaped
    //.replace(/(\w+):/g, '"$1":') // Enclose keys in double quotes
    .replace(/\\+/g, '\\\\'); // Escape backslashes
  console.log(cleanedString)
  const titles = JSON.parse(cleanedString.trim());
  const decodedDesc = decodeURIComponent(element.querySelector("desc").textContent);
  const desc = JSON.parse(decodedDesc.replace(/'/g, '"'));
  //const desc = decodeURIComponent(element.querySelector("desc").textContent);
  console.log(desc)
 

  // Create menu items for each character in the title
  for (let i = 0; i < titles.length; i++) {
    const menuItem = document.createElement('div');
    menuItem.className = 'dropdown-item'; // Add class for styling
    menuItem.textContent = `${i}: ${titles[i]}`; // Display character and index
    menuItem.style.cursor = 'pointer'; // Change cursor to pointer
    //descMenu.remove();
    // Add click event to each menu item

    menuItem.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent closing the context menu


      showDescriptionMenu(e, i, desc[i].description,contextMenu,descMenuHeight); // Show description menu
    });

    contextMenu.appendChild(menuItem); // Append the menu item to the context menu
  }

  document.body.appendChild(contextMenu); // Append the context menu to the body

  // Remove the context menu when clicking elsewhere
  window.addEventListener('click', () => {
    contextMenu.remove();
  }, { once: true }); // Use { once: true } to ensure the listener is removed after the first click
}


function showDescriptionMenu(event,index, description, contextMenu,descMenuHeight) {
  console.log(descMenuHeight);
  // Create a custom description context menu
  const descMenu = document.createElement('div');
  descMenu.className = 'context-menu';
  descMenu.style.position = 'absolute';
  descMenu.style.left = `${contextMenu.offsetLeft}px`; // Align with the title menu
  descMenu.style.top = `${contextMenu.offsetTop + contextMenu.offsetHeight + descMenuHeight}px`; // Position below the title menu
  descMenu.style.backgroundColor = 'green'; // Set background color to green
  descMenu.style.color = 'white'; // Optional: Set text color to white for better contrast
  descMenu.style.padding = '10px'; // Optional: Add some padding
  descMenu.style.borderRadius = '5px'; // Optional: Add rounded corners
  descMenu.style.display = 'flex';
  //descMenu.style.overflowY = 'auto'; // Enable vertical scrolling if content overflows
  descMenu.textContent = `${index}: ${description}`;

  // Append the description menu to the body
  document.body.appendChild(descMenu);
  descMenuHeight = descMenu.offsetHeight; // Record the height of the description menu
  // Remove the description menu when clicking elsewhere
  window.addEventListener('click', () => {
    descMenu.remove();


  });
}


function showInputField() {
  document.getElementById('inputContainer').style.display = 'block';
}



