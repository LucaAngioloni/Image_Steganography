# Image_Steganography

Steganography applied to conceal small files inside a PNG image.

-------
## Description
This script allows to conceal small files inside png images, using a well known steganographic method: hide the data in the least significant bits of an image pixels.
This produces little changes to the image that usually aren't noticed by just looking at the image.

## Usage

The script usage:

```
usage: Image_Steganography.py [-h] [-e | -d] [-i IMAGE] [-f FILE] [-o OUTPUT]

Conceal small files inside a PNG image and extract them back

optional arguments:
  -h, --help            show this help message and exit
  -e, --encode          If present the script will conceal the file in the
                        image and produce a new encoded image
  -d, --decode          If present the script will decode the concealed data
                        in the image and produce a new file with this data
  -i IMAGE, --image IMAGE
                        Path to an image to use for concealing or file
                        extraction
  -f FILE, --file FILE  Path to the file to conceal or to extract
  -o OUTPUT, --output OUTPUT
                        Path where to save the encoded image. Specify only the
                        file name, or use .png extension; png extension will
                        be added automatically

```

## Example

We could encode a simple txt file like `file.txt`:
```
This script is working!!!
```

Running the script like:
```
$ python3 Image_Steganography.py -e -i resources/original.png -f resources/file.txt -o resources/encoded.png
```

The result is an encoded image which looks identical to the original:

![Original](resources/original.png) | ![Encoded](resources/encoded.png)
|:---:|:---:|
| Original | Encoded |

From the encoded image we can extract the concealed file:
```
$ python3 Image_Steganography.py -d -i resources/encoded.png -f resources/file_concealed.txt
```

## Requirements
| Software       | Version        | Required |
| -------------- |:--------------:| --------:|
| **Python**     | Either 2 or 3  |    Yes   |
| **Numpy**      |Tested on v1.13 |    Yes   |
| **Pillow**     |Tested on v4.3.0|    Yes   |
| **imageio**    |Tested on v2.2.0|    Yes   |

## Future developements
Maybe implement a GUI.

## License
Licensed under the term of [MIT License](http://en.wikipedia.org/wiki/MIT_License). See attached file LICENSE.
