# edx-p3e-repo
The source code of the P3E XBlock

Installation
------------

To start developping this xblock, follow this instructions:

1.  Fisrt, install the XBlock SDK by following this tutorial:

        https://github.com/edx/xblock-sdk#xblock-sdk--

2. Then, download this repo:

        $ git clone https://github.com/abotsi/edx-p3e-repo

3. Move the sources into the sdk folder:

        $ mv edx-p3e-repo/* xblock-sdk/

4. You can now start the p3e-xblock doing the following

      1. Activate your virtualenv:

              $ source xblock-sdk/bin/activate
              
      2. Run the server:
      
              $ python xblock-sdk/manage.py runserver
              
      3. With a web browser, open the link: http://127.0.0.1:8000/scenario/p3exblock.0/
