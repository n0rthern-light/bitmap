#!/usr/bin/env python3

import argparse
import struct
import math
import os
import subprocess
import platform

def write_grayscale_bmp(input_file, output_file, width, offset=0):
    with open(input_file, "rb") as f:
        data = f.read()

    # Apply offset
    data = data[offset:]

    # Calculate height based on width
    height = math.ceil(len(data) / width)

    # Prepare BMP headers
    row_padding = (4 - (width % 4)) % 4
    pixel_data_offset = 54
    file_size = pixel_data_offset + (width + row_padding) * height

    bmp_header = b'BM'
    bmp_header += struct.pack('<I', file_size)  # File size
    bmp_header += struct.pack('<H', 0)  # Reserved
    bmp_header += struct.pack('<H', 0)  # Reserved
    bmp_header += struct.pack('<I', pixel_data_offset)  # Offset to pixel data

    dib_header = struct.pack('<I', 40)  # DIB header size
    dib_header += struct.pack('<i', width)  # Image width
    dib_header += struct.pack('<i', -height)  # Image height (negative for top-down)
    dib_header += struct.pack('<H', 1)  # Number of color planes
    dib_header += struct.pack('<H', 8)  # Bits per pixel (8-bit grayscale)
    dib_header += struct.pack('<I', 0)  # No compression
    dib_header += struct.pack('<I', file_size - pixel_data_offset)  # Image size
    dib_header += struct.pack('<I', 2835)  # Horizontal resolution (pixels/meter)
    dib_header += struct.pack('<I', 2835)  # Vertical resolution (pixels/meter)
    dib_header += struct.pack('<I', 256)  # Number of colors in the palette
    dib_header += struct.pack('<I', 0)  # Important colors

    # Create grayscale palette
    palette = bytearray()
    for i in range(256):
        palette.extend((i, i, i, 0))  # Grayscale RGB + reserved byte

    # Create pixel data
    pixel_data = bytearray()
    for row in range(height):
        start = row * width
        end = start + width
        pixel_row = data[start:end]
        pixel_data.extend(pixel_row)
        pixel_data.extend(b'\x00' * (width - len(pixel_row)))  # Padding for last row
        pixel_data.extend(b'\x00' * row_padding)

    # Write BMP file
    with open(output_file, "wb") as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(palette)
        f.write(pixel_data)

def get_output_file_path(input_file):
    return f"{input_file}.bitmap.bmp"

def open_image_in_os(output_file):
    if platform.system() == "Windows":
        subprocess.run(["start", output_file], shell=True)
    elif platform.system() == "Darwin":
        subprocess.run(["open", output_file])
    else:
        subprocess.run(["xdg-open", output_file])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a grayscale BMP from a binary file.")
    parser.add_argument("input_file", type=str, help="Path to the input file")
    parser.add_argument("--width", type=int, required=True, help="Width of the output BMP image in pixels")
    parser.add_argument("--offset", type=int, default=0, help="Offset in the file to start reading bytes (default: 0)")
    parser.add_argument("--open", action="store_true", help="Automatically open the result image in default image viewer (default: False)")

    args = parser.parse_args()

    output_file = get_output_file_path(args.input_file)
    write_grayscale_bmp(args.input_file, output_file, args.width, offset=args.offset)

    if args.open:
        open_image_in_os(output_file)

