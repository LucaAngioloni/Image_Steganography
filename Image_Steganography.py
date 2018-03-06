# MIT License

# Copyright (c) 2018 Luca Angioloni

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import numpy as np
from imageio import imread, imwrite

import argparse

max_value = 255 # max uint value per pixel per channel
header_len = 4*8 # uint32 bit length

def read_image(img_path):
    """
        Reads an image from file and flattens it.
        Args:
            img_path    path to the image
        Returns:
            ndarray     numpy array containing the image in a flat shape
            ndarray     shape of the read image before flattening
    """
    img = np.array(imread(img_path), dtype=np.uint8)
    orig_shape = img.shape
    return img.flatten(), orig_shape

def write_image(img_path, img_data, shape):
    """
        Writes an image to a path from a flat numpy array, usig the shape provided.
        Args:
            img_path    path were to save the image
            img_data    numpy array containing the image (flat)
            shape       shape of the image to be saved
    """
    img_data = np.reshape(img_data, shape)
    imwrite(img_path, img_data)

def bytes2array(byte_data):
    """
        Converts byte data to a bit array (numpy array, dtype=np.uint8).
        Args:
            byte_data   the byte data
        Returns:
            ndarray     a numpy array of the single bits that composed the byte data
    """
    byte_array = np.frombuffer(byte_data, dtype=np.uint8)
    return np.unpackbits(byte_array)

def array2bytes(bit_array):
    """
        Converts a bit array (numpy array, dtype=np.uint8) to byte data.
        Args:
            bit_array   the bit array
        Returns:
            bytes       the byte data
    """
    byte_array = np.packbits(bit_array)
    return byte_array.tobytes()

def read_file(file_path):
    """
        Reads a file as a bit array (numpy array, dtype=np.uint8)
        Args:
            file_path   path to the file
        Returns:
            ndarray     the bit array
    """
    file_bytes = open(file_path, "rb").read()
    return bytes2array(file_bytes)

def write_file(file_path, file_bit_array):
    """
        Writes a file to a path from a bit array (numpy array, dtype=np.uint8).
        Args:
            file_path       path to the file
            file_bit_array  the bit array of the file
    """
    bytes_data = array2bytes(file_bit_array)
    f = open(file_path, 'wb')
    f.write(bytes_data)
    f.close()

def encode_data(image, file_data):
    """
        Encodes the file data onto the image
        Args:
            image       the original image numpy array (flat)
            file_data   the file data (bit array)
        Returns:
            ndarray     the encoded image as a numpy array
    """
    or_mask = file_data
    and_mask = np.zeros_like(or_mask)
    and_mask = (and_mask + max_value - 1) + or_mask 
    res = np.bitwise_or(image, or_mask)
    res = np.bitwise_and(res, and_mask)
    return res

def decode_data(encoded_data):
    """
        Decodes the data from an image
        Args:
            encoded_data    the encoded image as numpy array
        Returns:
            ndarray         the bit array containig the file bits
    """
    out_mask = np.ones_like(encoded_data)
    output = np.bitwise_and(encoded_data, out_mask)
    return output

def _main(args):
    """Main fuction of the script"""
    if args.image is not None and args.file is not None:
        if args.encode:
            img_path = args.image
            file_path = args.file
            if not os.path.isfile(img_path):
                print("Image file does not exist")
                return
            if not os.path.isfile(file_path):
                print("File does not exist")
                return

            output_path = args.output
            extension = os.path.splitext(output_path)[1][1:]
            if extension == '':  # if no extension, append png
                output_path = output_path + '.png'
            elif extension != 'png':  # replace the wrong extension with png
                li = output_path.rsplit(extension, 1)
                output_path = 'png'.join(li)

            image, shape_orig = read_image(img_path)
            file = read_file(file_path)
            file_len = file.shape[0]
            len_array = np.array([file_len], dtype=np.uint32).view(np.uint8)
            len_array = np.unpackbits(len_array)
            img_len = image.shape[0]

            if file_len >= img_len - header_len:  # 4 bytes are used to store file length
                print("File too big, error")
                return
            else:  #  Insert padding. Using random padding, otherwise values would all be even if padding with zeros (could be noticed in histogram).
                tmp = file
                file = np.random.randint(2, size=img_len, dtype=np.uint8)
                file[header_len:header_len+file_len] = tmp
                # file = np.pad(file, (header_len,img_len - file_len - header_len), 'constant', constant_values=(0, 0))

            file[:header_len] = len_array
            encoded_data = encode_data(image, file)

            write_image(output_path, encoded_data, shape_orig)
            print("Image encoded")
            return

        if args.decode:
            img_path = args.image
            if not os.path.isfile(img_path):
                print("Image file does not exist")
                return
            file_path = args.file
            encoded_data, shape_orig = read_image(img_path)
            data = decode_data(encoded_data)
            el_array = np.packbits(data[:header_len])
            extracted_len = el_array.view(np.uint32)[0]
            data = data[header_len:extracted_len+header_len]
            write_file(file_path, data)
            print("Image decoded")
            return

        print("Error, no action specified!")
        return

    print("Error, image or file not specified")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Conceal small files inside a PNG image and extract them back')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-e',
        '--encode',
        help='If present the script will conceal the file in the image and produce a new encoded image',
        action="store_true")
    group.add_argument(
        '-d',
        '--decode',
        help='If present the script will decode the concealed data in the image and produce a new file with this data',
        action="store_true")
    parser.add_argument(
        '-i',
        '--image',
        help='Path to an image to use for concealing or file extraction')
    parser.add_argument(
        '-f',
        '--file',
        help='Path to the file to conceal or to extract')
    parser.add_argument(
        '-o',
        '--output',
        help='Path where to save the encoded image. Specify only the file name, or use .png extension; png extension will be added automatically',
        default='encoded.png')

    _main(parser.parse_args())