# BigCommerce

### Setup
- Go to your big commerce dashboard
- Under settings go to legacy api settings and setup a new user
- In the directory where you will be running python (Probably wherever bigcommerce.py is located) create a "bc.data" file.
  - enter text into the file like so, replacing \<user> with your username, etc.
  ```text
  user <user>
  key <key>
  path <api_path>
  ```

### Basic Usage

#### Get a product and data
- Assuming you have a SKU = 1234, we can write:
```python
from bigcommerce import Product
p = Product()
sku1234 = p.getSingleProduct("1234")
```
  - sku1234 will be a dictionary of information about sku 1234

#### Get all skus
```python
from bigcommerce import Product
p = Product()
skus = p.getAllProducts()
```
  - Now we can do
```python
skus["1234"]
```
  to view information about sku 1234.

#### Update a product
- take note that ```updateProduct``` takes a bigcommerce product id instead of a sku.  I often use this method in conjuction with ```getAllProducts``` or ```getSingleProduct```.
```python
from bigcommerce import Product
p = Product()
p.updateProduct("12034", inventory_level="40")  # Updates id 12034 with stock = 40
```

#### Convert a sku to its Big Commerce ID number
- say we want to know what the big commerce id number is for sku 1234.  It is simply a dictionary key and value.
```python
from bigcommerce import Product
p = Product()
sku1234 = p.getSingleProduct("1234")
id1234 = sku1234["id"]
```
- or we can likewise do
```python
from bigcommerce import Product
p = Product()
skus = p.getAllProducts()
id1234 = skus["1234"]["id"]
```
- The latter method is nice because we don't have to keep calling ```getSingleProduct```, to get id numbers.  We've just asked for all the information at once.  This may be overkill in some situations where you only need a few id numbers, or other information about a sku.

There are more methods available which I may write about later if I find the motivation.

### License
https://opensource.org/licenses/MIT