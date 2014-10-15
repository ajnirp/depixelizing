About
-----

Digital Image Processing course project.

References
----------

http://research.microsoft.com/en-us/um/people/kopf/pixelart/index.html
http://www.ucsp.edu.pe/sibgrapi2013/eproceedings/technical/114688_2.pdf

Using pypy
----------

    virtualenv -p `which pypy` depixelizing
    cd depixelizing
    sudo bin/pip install Pillow
    echo 'from PIL import Image' > pypy-pil-test.py
    bin/pypy pypy-pil-test.py

Using `pypy` as above, we observed a speed *drop* on the incomplete codebase.
