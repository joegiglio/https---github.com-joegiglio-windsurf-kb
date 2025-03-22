from PIL import Image

# Create a new image with a blue background
img = Image.new('RGB', (100, 100), color='blue')
img.save('test_image.jpg')
