# BigCommerce

### Setup
- Go to your big commerce dashboard
- Under settings go to legacy api settings and setup a new user
- In the directory where you will be running python (Probably wherever bigcommerce.py is located) create a "bc.data" file.
  - enter text into the file like so, replacing <user> with your username, etc.
  ```text
  user <user>
  key <key>
  path <api_path>
  ```