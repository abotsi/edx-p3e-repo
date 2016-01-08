# edx-p3e-repo
The source code of the P3E XBlock

Installation
------------

To start developping this xblock, follow this instructions:

1. Fisrt, in ~/my_folder/, install the XBlock SDK by following this tutorial: https://github.com/edx/xblock-sdk#xblock-sdk--

2. Next, in ~/my_folder/, download this repository in another folder:

        $ git clone https://github.com/abotsi/edx-p3e-repo
   
   At this point, you should have:

        my_folder
        ├── xblock-sdk-master/
        ├── edx-p3e-repo/

3. Then, with your venv activated, install p3e-xblock with the command:

        $ pip install -e ../edx-p3e-repo/

4. You can now start the p3e-xblock doing the following

      1. Activate your virtualenv:

              $ source xblock-sdk/bin/activate
              
      2. Run the server:
      
              $ python xblock-sdk/manage.py runserver
              
      3. With a web browser, open the link: http://127.0.0.1:8000/scenario/p3exblock.0/
