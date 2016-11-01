# This is a guide to manage Python packages.


## Preliminaries

You can either use `pip` or `anaconda` to manage your python
packages. If you want to use pip, then follow the `pip` guide, otherwise
the `anaconda` steps.

### Pip

1. Install `pip`

 Depending on you OS, install pip. The following snippet is for
 Ubuntu. `pip` is a package manager which uses Pypi as repository.

 ```
 sudo apt-get update && sudo apt-get -y upgrade
 sudo apt-get install python-pip python-dev build-essential 
 sudo pip install --upgrade pip
 ```

2. Install `virtualenv`.

 `Virtualenv` is a tool to create isolated development
 environment. That is, it enables the user to customise the Python
 packages for each particular project.

 ```
 sudo pip install virtualenv
 ```

3. Initiate virtual environment.

 To initiate your virtual environment, execute the following.

 ```
 virtualenv venv
 ```

 After you have initiated the environment, you can activate it with

 ```
 source venv/bin/activate
 ```

 You will see the prefix `(venv)` appended to your command line. This
 should be done everytime you start working on the project.

4. Install and update requirements.

 After you have initiated the virtual environment, now we can start
 installing the required package for the project.

 Pull the `requirements.txt` from the master branch, then install the
 packages.

 **NOTE (Michael): Make sure you are in the virtual environment,
   otherwise, it would be a system wide installation.**

 ```
 git checkout master -- requirements.txt
 pip install -r requirements.txt
 ```

 All future dependent packages should be installed via `pip`.

 If you have updated the package requirements, make sure to update the
 `requirements.txt` with

 ```
 pip freeze > requirements.txt
 ```

 After updating the package and current development, you can make a
 pull request to update your developments and the package
 requirements.

5. Leaving the virtual environment.

 After the developments, you can exit the virtual environment simply
 by typing

 ```
 deactivate
 ```

 You will be able to use all the packages that has been installed
 system wide.

