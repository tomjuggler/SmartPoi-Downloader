"""
Image Handling Functions

This module provides functions for image manipulation, including rotation, resizing, and conversion to an 8-bit R3G3B2 format.

"""

import math
import os

from PIL import Image, ImageEnhance


def rotate_image(file):
    """
    Rotate the input image by 90 degrees clockwise.

    Args:
        file (PIL.Image.Image): Input image to be rotated.

    Returns:
        PIL.Image.Image: Rotated image.
    """
    return file.rotate(-90, expand=True)


def unrotate_image(file):
    """
    Rotate the input image by 90 degrees counterclockwise.

    Args:
        file (PIL.Image.Image): Input image to be rotated.

    Returns:
        PIL.Image.Image: Rotated image.
    """
    return file.rotate(90, expand=True)


def resize_image(image, basewidth):
    """
    Resize the input image to a specified width while maintaining the aspect ratio.

    Args:
        image (PIL.Image.Image): Input image to be resized.
        basewidth (int): Desired width of the resized image.

    Returns:
        PIL.Image.Image: Resized image.
    """
    wpercent = basewidth / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))
    img = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    return img


# def resize_image(image, basewidth): # todo: nope?
#     """
#     Resize the input image to a specified width while maintaining the aspect ratio.

#     Args:
#         image (PIL.Image.Image): Input image to be resized.
#         basewidth (int): Desired width of the resized image.

#     Returns:
#         PIL.Image.Image: Resized image.
#     """
#     img = image.copy()
#     img.thumbnail((basewidth, img.height), Image.Resampling.LANCZOS)
#     return img


def compress_image_to_8bit_color(input_image, size):
    """
    Compress the input image to an 8-bit color format and return the binary data.

    Args:
        input_image (PIL.Image): The input image.
        size (int): The size of the POI.

    Returns:
        bytes: The binary data of the compressed image.
    """
    print(f"input_image height: {input_image.height}, width: {input_image.width}")
    new_width = size
    binary_data = []

    # Ensure the image is in RGB format
    if input_image.mode != "RGB":
        input_image = input_image.convert("RGB")

    # Rotate image 90 degrees for viewing on the poi
    try:
        rotated_image = rotate_image(input_image)
        print(
            f"rotated_image height: {rotated_image.height}, width: {rotated_image.width}"
        )
    except Exception as e:
        print(f"Error rotating image: {e}")
        return None

    # Resize image to pre-defined poi size
    try:
        resized_image = resize_image(rotated_image, new_width)
        print(
            f"resized_image height: {resized_image.height}, width: {resized_image.width}"
        )
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

    # Loop over each pixel in the input image and encode it
    for x in range(resized_image.height):
        for y in range(resized_image.width):
            r, g, b = resized_image.getpixel((y, x))
            # print(f"Pixel at ({y}, {x}): R={r}, G={g}, B={b}")
            encoded = (r & 0xE0) | ((g & 0xE0) >> 3) | (b >> 6)
            binary_data.append(encoded)

    return bytes(binary_data)


def convert_8bit_color_to_image(binary_data, width):
    """
    Convert a previously compressed 8-bit color image back to a rotated and resized PIL image.

    Args:
        binary_data (bytes): The binary data of the compressed image.
        width (int): Width of the output image.

    Returns:
        PIL.Image.Image: Converted image.
    """
    # Calculate the dimensions of the output image
    height = (len(binary_data) + width - 1) // width

    # Create an image from the binary data
    output_image = Image.new("RGB", (width, height))
    for i, b in enumerate(binary_data):
        r = b & 0xE0
        g = (b & 0x1C) << 3
        b = (b & 0x03) << 6
        x, y = i % width, i // width
        output_image.putpixel((x, y), (r, g, b))

    print(f"output_image height: {output_image.height}, width: {output_image.width}")

    # Un-rotate the image
    return_image = unrotate_image(output_image)
    print(f"return_image height: {return_image.height}, width: {return_image.width}")

    return return_image


def is_image_very_white(image, threshold=200, white_ratio=0.4):
    """
    Check if the image is predominantly white.

    Args:
        image (PIL.Image): The image to check.
        threshold (int): Brightness threshold to consider a pixel as white.
        white_ratio (float): The ratio of white pixels to total pixels to consider the image predominantly white.

    Returns:
        bool: True if the image is predominantly white, False otherwise.
    """
    grayscale = image.convert("L")  # Convert image to grayscale
    histogram = grayscale.histogram()

    # Calculate the number of white pixels
    white_pixels = sum(histogram[threshold:])
    total_pixels = sum(histogram)

    return (white_pixels / total_pixels) > white_ratio


def rotate_visual_poi_style(input_image, basewidth):
    """
    Rotate an image in a visual style to create a spinning effect.

    Args:
        input_image (PIL.Image.Image): Input image to be rotated.
        basewidth (int): Desired fixed width for the rotated image.

    Returns:
        PIL.Image.Image: Rotated image with spinning effect.
    """
    # Ensure the image is in RGB format
    if input_image.mode != "RGB":
        input_image = input_image.convert("RGB")

    # Check if the image is very white
    if not is_image_very_white(input_image):
        print("image is not bright")
        # Enhance the brightness
        brightness_enhancer = ImageEnhance.Brightness(input_image)
        input_image = brightness_enhancer.enhance(
            1.5
        )  # Increase brightness by a factor of 1.5

    img = rotate_image(input_image)
    img_rotated = resize_image(img, basewidth)

    # Start rotate image now
    fit = 1
    if img_rotated.height > 360:
        fit = 3
    else:
        fit = 3
    if fit == 2:
        fit = 3  # looks better with 3

    # Create a blank image and rotate the input image onto it multiple times
    # to create the final spinning effect
    new_height = int(360 // fit)
    newImg = Image.new(
        mode="RGB", size=(600, 600)
    )  # todo: change for different size poi?

    # Resize for rotation
    img_rotated = img_rotated.resize(
        (img_rotated.width, new_height), Image.Resampling.LANCZOS
    )

    incrRotation = 0
    while incrRotation < 360:
        w, h = img_rotated.size
        for y in range(h):
            for x in range(w):
                adjacent = int((x + 90) * math.sin(math.radians(-y + incrRotation)))
                opposite = int((x + 90) * math.cos(math.radians(-y + incrRotation)))
                pixel_color = img_rotated.getpixel((x, y))
                set_x = adjacent + (newImg.width // 2)
                set_y = opposite + (newImg.height // 2)
                newImg.putpixel((set_x, set_y), pixel_color)
        incrRotation += new_height

    return newImg


def compress_and_convert_image(image_name, size):
    """
    Uses the compress_image_to_8bit_color function to create .bin file from image

    Args:
        image_name (string): name of the image in static/images folder
        size (int): The size of the POI.

    Returns:
        compressed_data: the .bin file

    """
    # Construct the full path to the .jpg image
    image_path = os.path.join("static/images", image_name + ".jpg")
    input_image = Image.open(image_path)

    # Compress the image to 8-bit color
    compressed_data = compress_image_to_8bit_color(input_image, size)
    return compressed_data


def add_compressed_images_for(size):
    """
    Compresses all images in the static/images directory and saves the .bin files to the appropriate directory based on the size.

    Args:
        size (int): The size of the POI.
    """
    # Define the base directory for saving .bin files
    base_dir = "static/bins"
    size_dirs = {
        36: "bin_36",
        60: "bin_60",
        72: "bin_72",
        120: "bin_120",
        144: "bin_144",
    }

    # Determine the directory to save the .bin files
    save_dir = os.path.join(base_dir, size_dirs.get(size, "bin_"))
    os.makedirs(save_dir, exist_ok=True)

    # List all .jpg image files in the static/images directory
    image_dir = "static/images"
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]

    for image_file in image_files:
        image_name = os.path.splitext(image_file)[0]
        image_path = os.path.join(image_dir, image_file)
        compressed_data = compress_and_convert_image(image_name, size)
        print(f'saving {image_name}')
        # Save the compressed data to the appropriate directory with .bin extension
        save_path = os.path.join(save_dir, f"{image_name}.bin")
        with open(save_path, "wb") as f:
            f.write(compressed_data)


if __name__ == "__main__":
    add_compressed_images_for(36)
