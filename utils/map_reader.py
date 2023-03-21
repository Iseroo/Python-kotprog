
import PIL.Image as Image

# Read the map image and return array of the colors

def read_map_image(map_image):
    
        map_image = Image.open(map_image)
    
        map_image = map_image.convert('RGB')
    
        map_image = map_image.load()
    
        return map_image



