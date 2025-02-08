from xml.etree import ElementTree as ET
from color_function_base import set_gradient


def check_anno(title_text, group, group_no):
    colors = []

    # Iterate over each key-value pair in the query
    for key, values in group[0].items():

        # Check if any value in the list of values of the query dictionary
        # matches the title text

        if any(value in item for item in title_text for value in values):
            colors.append(1)  # Add the specified color
        else:
            colors.append(0)  # Default to white
        for value in values:
            if any(value in item for item in title_text):
                # Create a new list to replace items
                updated_title_text = []
                # Update title text with the key
                for item in title_text:
                    if (value in item):
                        updated_title_text.append(f"group{group_no}:{key}:{item}")
                    else:
                        updated_title_text.append(item)  # Keep the original 

                    title_text = updated_title_text
                    # item if conditions are not met
                    # Replace the title_text with updated_title_text
    if len(colors) == 0:
        percentage_presence = 0
    else:
        percentage_presence = (sum(colors) / len(colors)) * 100

    return title_text, percentage_presence


def add_linear_gradient_groups(query: list, predefined_colors: list = ['yellow', 'red', 'blue', 'green'], data=None):
    # assign the data parameter to the root variable. 
    root = data
    elements = root.find('.//g')
    # Create a <defs> element
    defs = ET.Element('defs')
    # Set the fill of each element to the specified color
    no_of_groups, groups = assess_no_of_groups(query)

    if no_of_groups == 0:
        return root, None

    for shapes in elements:
        colors = []
        # Extract the title element from shapes
        title_element = shapes.find('title')

        # Extract the title text if the title element           
        title_text = eval(title_element.text)

        group_count = 0
        for sublist in groups:
            group_count = group_count + 1
            updated_title_text, color = check_anno(title_text, sublist, group_count)

            updated_title_text = remove_duplicate_groups(updated_title_text)
            colors.append(color)
            title_element.text = str(updated_title_text)
            title_text = eval(title_element.text)

        gradient_colors, legend_colors = define_color(colors)

        if gradient_colors and any(c != 'white' for c in gradient_colors):
            shapes.set('fill-opacity', '0.5')
            defs = ET.Element('defs')
            defs = set_gradient(shapes.get('shape_id'), shapes, defs, gradient_colors)  # Set gradient
            root.append(defs)  # Append definitions to root

    return root, legend_colors


def assess_no_of_groups(shape_id: list):
    if not any(isinstance(i, list) for i in shape_id):
        no_of_groups = len([shape_id])
    else:
        no_of_groups = sum(isinstance(i, list) for i in shape_id)

    if no_of_groups == 0:
        groups = []
    elif no_of_groups == 1:
        groups = [[shape_id]]
    else:
        groups = shape_id

    return no_of_groups, groups


def define_color(color_percent_list, predefined_colors=['yellow', 'red', 'blue', 'green']):
    colors = []
    if len(predefined_colors) < 4:
        predefined_colors = ['yellow', 'red', 'blue', 'green']

    for color_percent in color_percent_list:
        if color_percent == 0:
            colors.append('white')
        elif color_percent <= 25:
            colors.append(predefined_colors[0])
        elif color_percent <= 50:
            colors.append(predefined_colors[1])
        elif color_percent <= 75:
            colors.append(predefined_colors[2])
        else:
            colors.append(predefined_colors[3])
    return colors, predefined_colors


def remove_duplicate_groups(data):
    result = []

    for entry in data:
        segments = entry.split(':')
        seen_groups = set()
        new_segments = []

        for segment in segments:
            # Check if the segment matches the "group followed by a number" pattern
            if segment.startswith('group'):
                if segment not in seen_groups:
                    seen_groups.add(segment)
                    new_segments.append(segment)
            else:
                new_segments.append(segment)  # Always add non-group segments

        # Join the new segments and add to the result
        result.append(':'.join(new_segments))

    return result
