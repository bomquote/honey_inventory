![Image of honey_logo](https://github.com/bomquote/honey_inventory/blob/master/images/honey_img.png?raw=true)

# Honey Inventory: sweet command line inventory control

## About

Honey Inventory began out of a need for a flexible inventory control database for our [honeygear.com](https://www.honeygear.com) products that can 
handle input from barcode scanning UPC codes. Also, we wanted an inventory application which 
can be locally used at different locations but still integrate and sync with our 
[bomquote.com](https://www.bomquote.com) webapp, so I built it. Honey Inventory is a command line 
driven app but it is also able to be easily wrapped and used in a webapp or desktop application. 
Currently, it is opinionated to fit our use case and depends on a relational database which is compatible
with SQLAlchemy and also Redis for caching. 

## Primary Goals
1. allows easy creation of transient or permanent storage locations that can contain multiple skus. This is a solution
 for dealing with a scenerio like:
   - "I just recalled 5000pcs of product from Amazon.com FBA covering 50 SKUs, and of course they shipped 
 them back to me in 200 different mixed sized cartons of jumbled up SKUs, and I need to do an inventory audit."
2. support barcode scanning to be able to quickly deal with a scenerio like:
   - slap a label on the mixed carton Amazon sent you to call it a "inventory location", scan all the UPCs of the carton
    contents to get a count of what's in the carton, throw them back in the carton so you don't have to deal with sorting 
    them while still knowing for certain what's in the cartons. 
3. generalize this to be a core inventory solution that integrates with python based webapps like bomquote.com 

## NOTE: UNDER ACTIVE DEVELOPMENT

Currently this library is under active development and is not fully abstracted 
for use as a general public library. You can definitely make it work for you 
right now but you'll need to review the source code and probably make changes to 
fit your environment and get it running. Note that the scripts in the `bin` folder 
currently use the `click` command line library because that's what I started out 
before switching over to the Cement Application framework, which is a more robust 
framework for both command line and backend development in general. But, I intend to 
keep up with the click maintenance so you can use it with click if you desire. DB migrations 
are also handled with `click` for convenience in using it as a script configuration in 
my Pycharm IDE. Integrating the alembic migrations into the `honey` application itself is 
planned but lower on my priority list.

Otherwise, I recommend you read up on the excellent 
[Cement documentation](https://docs.builtoncement.com/getting-started/framework-overview),
a few easily overlooked points are below:

- Ensure to set your config in config/honey.yml and some coode logic assumes the 
the filename will be called `honey.yml`

- All configuration settings can be overridden by their associated environment variables. 
For example config['honey']['foo'] is overridable by $HONEY_FOO.

## Quickstart Installation

1. git clone or fork this library and clone it to your local repository.

2. ensure you have a top level database created in postgresql or similar which is compatible with SQLAlchemy.

3. navitage to the repo `config` folder.  Find the `honey.yml` and modify the `DB_CONNECTION` string to fit your needs. 
On my dev machine this is `DB_CONNECTION: 'postgresql+psycopg2://postgres:password@localhost:5432/hgdb'`

4. Install requirements, If you are running miniconda, which I'm sure you are because this is 2020, then be sure to 
activate your environment to install the requirements. 
    ```
    $ pip install -r requirements-dev.txt
    
    $ pip install e .
    ```
5. Honey Inventory uses Alembic for database schema migrations. This allows you to create new database tables or modify 
existing tables. To brush up on Alembic see the 
[Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html). 
  To get started, you need to:
    - edit the `sqlalchemy.url` parameter in the alembic.ini file to ensure your database connection string is correct, 
like `sqlalchemy.url = postgresql+psycopg2://postgres:password@localhost:5432/hgdb`
    - init your database for alembic migrations by running the alembic init command

6. after your database is initialized with the blank tables created, to run the application, navigate to the repo folder:

    ```cmd
    c:\Users\bjord\repos\honey_inventory>
    ```

    Then, run the `honey` command in your command prompt window.  For help, run `honey --help`.

7. populate your database with some initial warehouse, container, and product/SKU data, like your barcode numbers and 
SKU descriptions.  For example, we have about 50 different product SKUs for our HoneyGear.com products and all those SKUs 
can be stored in various carton sizes, so the 50 SKUs in different carton sizes quickly become a few hundred different 
inventoriable items. That top level descriptive data all needs to be entered intially for configuration before you can 
do things like add specific quantities for your SKUs. So, we need to populate the following five tables with 
configuration data:
    - `warehouses` table
      - enter unique names to designate top level locations for places where goods are stored
      ![Image of warehouse tbl](https://github.com/bomquote/honey_inventory/blob/master/images/warehouses_tbl.png?raw=true)
    - `containers` table
      - list the kind of containers are your goods stored in and reference them to each other to describe parent-child relations. 
      ![Image of containers tbl](https://github.com/bomquote/honey_inventory/blob/master/images/container_tbl.png?raw=true)
    - `sku_owners` table
      - create an entry for each of the ultimate owners of the inventory/products in your database
      ![Image of sku_owners tbl](https://github.com/bomquote/honey_inventory/blob/master/images/sku_owners_tbl.png?raw=true)
    - `sku_attrs` table
      - A table allowing the creation of key:value grouping designations for Skus.
        Like, Sku Family (Grapple, Flux-Field, ...) and Sku Class ('Pro', 'Grip', ...) and Colors ('white', 'black', ...).
        This allows to detail the main features which comprise your product SKU variants, similar to setting up variants 
        on Shopify, Ebay, Amazon, etc.
      ![Image of sku_attrs tbl](https://github.com/bomquote/honey_inventory/blob/master/images/sku_attrs_tbl.png?raw=true)
    - `product_skus` table
      - enter in your detailed sku numbers, upc codes, descriptions, owner_id, and container_id
      ![Image of product_skus tbl](https://github.com/bomquote/honey_inventory/blob/master/images/product_skus_tbl.png?raw=true)



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
