# Honey Inventory: sweet command line inventory control

## NOTE - AT THIS POINT, THIS LIBRARY IS FOR REFERENCE ONLY

Currently this library is not yet abstracted for use as a general public library. 
You could make it work for you but you'll need to review the source code.
Note that the scripts in the `bin` folder currently use the `click` command 
line library because that's what I started out with before deciding to switch 
over to the Cement Application framework, which is a more robust framework for 
both command line and backend development in general.  DB migrations are also 
handled with `click` for convenience in using it as a script configuration in 
my Pycharm IDE.

Otherwise, read up on the Cement documentation at 
https://docs.builtoncement.com/getting-started/framework-overview,
a few highlights are below:

- Ensure to set your config in config/honey.yml and some coode logic assumes the 
the filename will be called `honey.yml`

- All configuration settings can be overridden by their associated environment variables. 
For example config['honey']['foo'] is overridable by $HONEY_FOO.



## Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

To run the application, navigate to the config folder:

```cmd
c:\Users\bjord\PycharmProjects\hg_inventory\config>
```

Then, run the `honey` command.  For help, run `honey --help`.

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run app cli application

$ app --help


### run pytest / coverage

$ make test
```



## Deployments

### Docker  (not working yet)

Included is a basic `Dockerfile` for building and distributing `HG Inventory`,
and can be built with the included `make` helper:

```
$ make docker

$ docker run -it app --help
```
