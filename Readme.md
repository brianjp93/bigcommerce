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