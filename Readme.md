# Questions

# Thesis

Why mention OGB? The KMW precursor is in OGB!

"OGB (One Gene Bank)"?! Is that you, ChatGTP?

No Python dependencies? But you use requests and pillow?!

# My changes

- replaced requests with urllib.request from standard library
- removed 200 pixels on the right side of the images - find another way of adding a legend!
- all pixels are now black with variable opacity.
- made proper package
  - fixed imports (from .file import ...)
  - replaced main.py with cli via Fire (uv pip install -e .; )

# eval

Why use eval anywhere?

# annotation_settings_ap.py

html_class and descr_prefix not necessary?
ignore

# opacity

```python
if pixdata[x_coord, y_coord] == (255, 255, 255, 255):
    # If so, make it transparent
    pixdata[x_coord, y_coord] = (255, 255, 255, 0)
```
could be

```python
r, b, g, a = pixdata[x_coord, y_coord]
assert r == b == g  # Ensure the image is grayscale
assert a == 0  # Verify that the image doesn't use opacity yet
pixdata[x_coord, y_coord] = (0, 0, 0, 255 - r)  # Black with inverted transparency
```

# class Geometry

```python
class Geometry:
    def __gometry_object(data):
        if  data['graphics']['type'] == 'line':
            return Line.geometry_details(data)
        elif data['graphics']['type'] == 'circle':
            return Circle.geometry_details(data)
        elif data['graphics']['type'] in ['rectangle', 'roundrectangle']:
            return  Rectangle.geometry_details(data)
        else:
            return None
```

- This function should be abstract and overwritten by child classes, no?
- `data` is actually `self`, this is not a abstractmethod or anything

# geometry_annotation

Why `result.replace("<->", "(1->4)")`?

This should probably be done using dictionaries:

```python
                 if query_type == 'compound' or query_type == 'reaction':
                     if parts[0] == "gl":
                         anno_type = "G"
                     if parts[0] == "dr":
                         anno_type = "D"
                     if parts[0] == "cpd":
                         anno_type = "C"
                     if parts[0] == "DG":
                         anno_type = "DG"
                     if parts[0] == "rn":
                         anno_type = "R"
                     if parts[0] == "rc":
                         anno_type = "RC"
                 elif query_type == 'enzyme':
                     anno_type = "EC"
                 elif query_type == 'ortholog':
                     anno_type = "K"
                 elif query_type == 'brite':
                     anno_type = "BR" 
                 elif query_type == 'map':
                     anno_type = "MAP" 
                     anno_name = 'map'+anno_name[-5:]
                 elif query_type == 'group':
                     anno_type = "GR"        
                 elif query_type == 'other':
                     anno_type = "O"     
                 elif query_type == 'gene':
                     anno_type ='Gene'
```

e.g.

```python
anno_type = some_dict[parts[0]]
```

Maybe using the dictionary in annotation_settings_ap?

