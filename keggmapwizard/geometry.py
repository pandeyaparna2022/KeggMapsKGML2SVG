class Geometry:
    def __init__(self, geometry_coords: dict, geometry_shape: str):
        self.geometry_coords = geometry_coords
        self.geometry_shape = geometry_shape


class Line(Geometry):
    def __init__(self, geometry_coords: dict, geometry_shape: str):
        self.geometry_coords = geometry_coords
        self.geometry_shape = geometry_shape

    @classmethod
    def geometry_details(cls, data):
        # Convert the geometry string to a list of integers
        coords = [int(i) for i in data['graphics']['coords'].split(',')]  # convert to int to catch errors
        # Assert no. of coordinates are even
        assert len(coords) % 2 == 0, f'number of polygon coordinates must be even! {coords} -> {coords}'
        # Group the coordinates into pairs to create points
        points = [(coords[l * 2], coords[l * 2 + 1]) for l in range(len(coords) // 2)]
        # Create a shape_path string in the format 'M x1,y1 L x2,y2 L x3,y3 ...'
        # eg: [(1, 2), (3, 4), (5, 6)] => 'M 1,2 L 3,4 L 5,6'.
        d = 'M ' + ' L '.join(f'{x},{y}' for x, y in points)

        geometry = {
            'd': d
        }
        geometry_shape = 'path'
        return cls(geometry, geometry_shape)


class Circle(Geometry):
    def __init__(self, geometry_coords: dict, geometry_shape: str):
        self.geometry_coords = geometry_coords
        self.geometry_shape = geometry_shape

    @classmethod
    def geometry_details(cls, data):
        # Calculate the radius of the  and assign x and y coordinates to cs and cy
        geometry = {

            # Calculate the radius
            'r': int(data['graphics']['width']) / 2,
            'cx': int(data['graphics']['x']),
            'cy': int(data['graphics']['y'])
        }
        geometry_shape = 'circle'

        return cls(geometry, geometry_shape)


class Rectangle(Geometry):
    def __init__(self, geometry_coords: dict, geometry_shape: str):
        self.geometry_coords = geometry_coords
        self.geometry_shape = geometry_shape

    @classmethod
    def geometry_details(cls, data):

        # Modify the x and y coordinates for svg (KGML specific issue)
        if int(data['graphics']['width']) > 46 and int(data['graphics']['height']) > 17:
            x = int(data['graphics']['x']) + 0.7
            y = int(data['graphics']['y']) + 0.7
        # Adjust the x and y coordinates based on the width and height
        x = int(data['graphics']['x']) - (int(data['graphics']['width']) / 2)
        y = int(data['graphics']['y']) - (int(data['graphics']['height']) / 2)
        # Set the rx and ry values
        if data['graphics']['type'] == 'roundrectangle':
            x = x + 1
            y = y + 1
            rx = 10
            ry = 10
        else:
            rx = 0
            ry = 0

        geometry_shape = 'rect'
        # Calculate the radius of the  and assign x and y coordinates to cs and cy
        geometry = {
            'x': x,
            'y': y,
            'height': data['graphics']['height'],
            'width': data['graphics']['width'],
            'rx': rx,
            'ry': ry
        }
        return cls(geometry, geometry_shape)


def geometry_factory(data):
    if data['graphics']['type'] == 'line':
        return Line.geometry_details(data)
    elif data['graphics']['type'] == 'circle':
        return Circle.geometry_details(data)
    elif data['graphics']['type'] in ['rectangle', 'roundrectangle']:
        return Rectangle.geometry_details(data)
    else:
        return None
