Text following a greater-than sign (>) is something you should type into a shell like CygWin or PowerShell
    e.g: >cd C:\
    I recommend using PowerShell

Install python 2.7: https://www.python.org/downloads/release/python-278/
    make sure it works by opening PowerShell and typing >python -V.  You should see something like "Python 2.7.8"
    If it that command doesn't work you might need to restart your computer.
Get the code: https://github.com/mark-archer/StaceMail/archive/master.zip
    unzip it somewhere easy to type like C:\StaceMail
Setup pip
    open PowerShell and change your directory to where you unzipped the code
        e.g: >cd C:\StaceMail
    run code to get pip
        >python get-pip.py
Get dependencies for StaceMail
    >pip install --upgrade google-api-python-client
    >pip install python-gflags
Test that StaceMail is working
    >python StaceMail.py
