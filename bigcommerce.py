"""
bigcommerce.py
8/10/15
Brian Perrett with Moonlight Feather Inc.
API connection with big commerce.
"""
from __future__ import division
import requests
import csv
import base64
import json
import pprint
from multiprocessing.dummy import Pool as ThreadPool


class BigCommerce(object):
    error_codes = {
                   200: "OK",
                   201: "Created",
                   202: "Accepted",
                   204: "No Content",
                   301: "Moved Permanently",
                   302: "Found",
                   304: "Not Modified",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   405: "Method Not Allowed",
                   406: "Not Acceptable",
                   409: "Conflict",
                   413: "Request Entity Too Large",
                   415: "Unsupported Media Type",
                   429: "Too Many Requests"
                   }

    def __init__(self):
        # user and key from settings -> legacy api settings
        # api endpoint
        self.path = self._getPath()
        self.user = self._getUser()
        self.key = self._getKey()
        # auth must be base64 encoded in <user>:<key> format
        self.auth = base64.b64encode(self.user + ':' + self.key)
        self.headers = {
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Basic ' + self.auth,
               'User-Agent': 'python-bigcommerce v0.1'
               }

    @staticmethod
    def _getUser():
        with open("bc.data", "rb") as f:
            for line in f:
                line = line.split()
                # print(line[0])
                if line[0] == "user":
                    user = line[1]
        try:
            return user
        except:
            raise Exception("No User Found in bc.data.  Add 'user <user>' to bc.data file.")

    @staticmethod
    def _getKey():
        with open("bc.data", "rb") as f:
            for line in f:
                line = line.split()
                if line[0] == "key":
                    key = line[1]
        try:
            return key
        except:
            raise Exception("No Key Found in bc.data.  Add 'key <key>' to bc.data file.")

    @staticmethod
    def _getPath():
        with open("bc.data", "rb") as f:
            for line in f:
                line = line.split()
                if line[0] == "path":
                    path = line[1]
        try:
            return path
        except:
            raise Exception("No Key Found in bc.data.  Add 'key <key>' to bc.data file.")


class Products(BigCommerce):

    def __init__(self, debug=False):
        """
        Mostly just playing with the debug idea.  Haven't really implemented it.
        """
        self.debug = debug
        super(Products, self).__init__()
        self.path = self.path + "products/"


    #########################
    # START Product Methods #
    #########################

    def _listProducts(
                      self,
                      page=1,
                      limit=250,
                      min_id=None,
                      max_id=None,
                      name=None,
                      keyword_filter=None,
                      description=None,
                      sku=None,
                      condition=None,
                      availability=None,
                      brand_id=None,
                      min_date_created=None,
                      max_date_created=None,
                      min_date_modified=None,
                      max_date_modified=None,
                      min_date_last_imported=None,
                      max_date_last_imported=None,
                      min_price=None,
                      max_price=None,
                      min_number_sold=None,
                      max_number_sold=None,
                      is_visible=None,
                      is_featured=None,
                      min_inventory_level=None,
                      max_inventory_level=None,
                      include_sku=None,
                      category=None,
                      product_tax_code=None
                      ):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/products
        RETRIEVES -> a page of {limit} products based on filters (all defaulted to None
            aka no filters).
        RETURNS   -> the request response which contains the json dictionary (r.json)
        __VARIABLES__
        refer to url reference for descriptions of the variables
        """
        # print("Running _listProducts Function.")
        path = self.path
        payload = {"page": page, "limit": limit}
        # conditionally add filters if filter is not None
        if min_id is not None: payload["min_id"] = min_id
        if max_id is not None: payload["max_id"] = max_id
        if name is not None: payload["name"] = name
        if keyword_filter is not None: payload["keyword_filter"] = keyword_filter
        if description is not None: payload["description"] = description
        if sku is not None: payload["sku"] = str(sku)
        if condition is not None: payload["condition"] = condition
        if availability is not None: payload["availability"] = availability
        if brand_id is not None: payload["brand_id"] = brand_id
        if min_date_created is not None: payload["min_date_created"] = min_date_created
        if max_date_created is not None: payload["max_date_created"] = max_date_created
        if min_date_modified is not None: payload["min_date_modified"] = min_date_modified
        if max_date_modified is not None: payload["max_date_modified"] = max_date_modified
        if min_date_last_imported is not None: payload["min_date_last_imported"] = min_date_last_imported
        if max_date_last_imported is not None: payload["max_date_last_imported"] = max_date_last_imported
        if min_price is not None: payload["min_price"] = min_price
        if max_price is not None: payload["max_price"] = max_price
        if min_number_sold is not None: payload["min_number_sold"] = min_number_sold
        if max_number_sold is not None: payload["max_number_sold"] = max_number_sold
        if is_visible is not None: payload["is_visible"] = is_visible
        if is_featured is not None: payload["is_featured"] = is_featured
        if min_inventory_level is not None: payload["min_inventory_level"] = min_inventory_level
        if max_inventory_level is not None: payload["max_inventory_level"] = max_inventory_level
        if include_sku is not None: payload["include_sku"] = include_sku
        if category is not None: payload["category"] = category
        if product_tax_code is not None: payload["product_tax_code"] = product_tax_code
        print("Requesting {} items on page {}.".format(limit, page))
        # print(path)
        # print(self.headers)
        # print(payload)
        # print(path)
        r = requests.get(url=path, headers=self.headers, params=payload)
        if self.debug:
            print(r.text)
        return r

    def getAllProducts(self):
        """
        multithreaded
        returns a dictionary of information
            {skus}
            skus is a dictionary with many keys and values
            refer to output.txt to see what information it holds
        """
        skus = {}
        page = 1
        num_pages = 8
        r = None
        found_empty = False
        pool = ThreadPool(num_pages)
        while not found_empty:
            pages = range(page, page + num_pages)
            results = pool.map(lambda x: self._listProducts(page=x), pages)
        # print(results)
            for r in results:
                if str(r.status_code) == "204":
                    found_empty = True
                    break
                if str(r.status_code).startswith("4"):
                    raise Exception("Error {}: {}.".format(r.status_code, BigCommerce.error_codes[int(r.status_code)]))
                temp_data = r.json()
                for item in temp_data:
                    sku = item["sku"]
                    skus[sku] = item
                page += 1
        return {"skus": skus}

    def getSingleProduct(self, sku):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/products
        RETURNS a single product based on sku.
        __VARIABLES__
        sku -> self explanatory
        """
        r = self._listProducts(sku=sku)
        if str(r.status_code) == "204":
            print("Sku not found.")
        elif str(r.status_code).startswith("4"):
            print(r.url)
            raise Exception("Error {}: {}. Message: {}".format(r.status_code, BigCommerce.error_codes[int(r.status_code)], r.json()[0]["message"]))
        else:
            temp_data = r.json()
            item = temp_data[0]
            return item

    def listProductImages(self, id, page=1, limit=250):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/products/images
        Lists image information for a single product based on a given id.
        """
        path = "{}{}/images".format(self.path, id)
        # print(path)
        payload = {"page": page, "limit": limit}
        r = requests.get(url=path, headers=self.headers, params=payload)
        return r

    def createProductImage(self, id, image_file):
        """
        REFERNCE -> https://developer.bigcommerce.com/api/stores/v2/products/images
        """
        path = "{}{}/images".format(self.path, id)
        data = {}
        data["image_file"] = image_file
        r = requests.post(path, data=json.dumps(data), headers=self.headers)
        if self.debug:
            print(r.text)
        return r

    def updateProductImage(self, id, image_id, image_file, sort_order=None):
        """
        REFERNCE -> https://developer.bigcommerce.com/api/stores/v2/products/images
        """
        path = "{}{}/images/{}".format(self.path, id, image_id)
        data = {}
        data["image_file"] = image_file
        if sort_order is not None: data["sort_order"] = sort_order
        r = requests.put(path, data=json.dumps(data), headers=self.headers)
        if self.debug:
            print(r.text)
        return r

    def updateProduct(
                      self,
                      id,
                      type_var=None,
                      sku=None,
                      description=None,
                      search_keywords=None,
                      availability_description=None,
                      price=None,
                      cost_price=None,
                      retail_price=None,
                      sale_price=None,
                      calculated_price=None,
                      sort_order=None,
                      is_visible=None,
                      is_featured=None,
                      related_products=None,
                      inventory_level=None,
                      inventory_warning_level=None,
                      warranty=None,
                      weight=None,
                      width=None,
                      height=None,
                      depth=None,
                      fixed_cost_shipping_price=None,
                      is_free_shipping=None,
                      inventory_tracking=None,
                      rating_total=None,
                      rating_count=None,
                      total_sold=None,
                      date_created=None,
                      brand_id=None,
                      view_count=None,
                      page_title=None,
                      meta_keywords=None,
                      meta_description=None,
                      layout_file=None,
                      is_price_hidden=None,
                      price_hidden_label=None,
                      categories=None,
                      date_modified=None,
                      event_date_field_name=None,
                      event_date_type=None,
                      event_date_start=None,
                      event_date_end=None,
                      myob_asset_account=None,
                      myob_income_account=None,
                      myob_expense_account=None,
                      peachtree_gl_account=None,
                      condition=None,
                      is_condition_known=None,
                      preorder_release_date=None,
                      is_preorder_only=None,
                      preorder_message=None,
                      order_quantity_minimum=None,
                      order_quantity_maximum=None,
                      open_graph_type=None,
                      open_graph_title=None,
                      open_graph_description=None,
                      is_open_graph_thumbnail=None,
                      upc=None,
                      date_last_imported=None,
                      option_set_id=None,
                      tax_class_id=None,
                      option_set_display=None,
                      bin_picking_number=None,
                      custom_url=None,
                      availability=None,
                      brand=None,
                      downloads=None,
                      images=None,
                      discount_rules=None,
                      configurable_fields=None,
                      custom_fields=None,
                      videos=None,
                      skus=None,
                      rules=None,
                      option_set=None,
                      options=None,
                      tax_class=None,
                      avalara_product_tax_code=None
                      ):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/products#update-a-product
                  -> https://developer.bigcommerce.com/api/objects/v2/product
        RETURNS nothing
        Updates products based on given arguments
        """
        path = self.path + str(id)
        data = {}
        if type_var is not None: data["type"] = type_var
        if sku is not None: data["sku"] = sku
        if description is not None: data["description"] = description
        if search_keywords is not None: data["search_keywords"] = search_keywords
        if availability_description is not None: data["availability_description"] = availability_description
        if price is not None: data["price"] = price
        if cost_price is not None: data["cost_price"] = cost_price
        if retail_price is not None: data["retail_price"] = retail_price
        if sale_price is not None: data["sale_price"] = sale_price
        if calculated_price is not None: data["calculated_price"] = calculated_price
        if sort_order is not None: data["sort_order"] = sort_order
        if is_visible is not None: data["is_visible"] = is_visible
        if is_featured is not None: data["is_featured"] = is_featured
        if related_products is not None: data["related_products"] = related_products
        if inventory_level is not None: data["inventory_level"] = inventory_level
        if inventory_warning_level is not None: data["inventory_warning_level"] = inventory_warning_level
        if warranty is not None: data["warranty"] = warranty
        if weight is not None: data["weight"] = weight
        if width is not None: data["width"] = width
        if height is not None: data["height"] = height
        if depth is not None: data["depth"] = depth
        if fixed_cost_shipping_price is not None: data["fixed_cost_shipping_price"] = fixed_cost_shipping_price  # OMG OVER 70 CHARACTERS PEP8 ME I DARE YOU
        if is_free_shipping is not None: data["is_free_shipping"] = is_free_shipping
        if inventory_tracking is not None: data["inventory_tracking"] = inventory_tracking
        if rating_total is not None: data["rating_total"] = rating_total
        if rating_count is not None: data["rating_count"] = rating_count
        if total_sold is not None: data["total_sold"] = total_sold
        if date_created is not None: data["date_created"] = date_created
        if brand_id is not None: data["brand_id"] = brand_id
        if view_count is not None: data["view_count"] = view_count
        if page_title is not None: data["page_title"] = page_title
        if meta_keywords is not None: data["meta_keywords"] = meta_keywords
        if meta_description is not None: data["meta_description"] = meta_description
        if layout_file is not None: data["layout_file"] = layout_file
        if is_price_hidden is not None: data["is_price_hidden"] = is_price_hidden
        if price_hidden_label is not None: data["price_hidden_label"] = price_hidden_label
        if categories is not None: data["categories"] = categories
        if date_modified is not None: data["date_modified"] = date_modified
        if event_date_field_name is not None: data["event_date_field_name"] = event_date_field_name
        if event_date_type is not None: data["event_date_type"] = event_date_type
        if event_date_start is not None: data["event_date_start"] = event_date_start
        if event_date_end is not None: data["event_date_end"] = event_date_end
        if myob_asset_account is not None: data["myob_asset_account"] = myob_asset_account
        if myob_income_account is not None: data["myob_income_account"] = myob_income_account
        if myob_expense_account is not None: data["myob_expense_account"] = myob_expense_account
        if peachtree_gl_account is not None: data["peachtree_gl_account"] = peachtree_gl_account
        if condition is not None: data["condition"] = condition
        if is_condition_known is not None: data["is_condition_known"] = is_condition_known
        if preorder_release_date is not None: data["preorder_release_date"] = preorder_release_date
        if is_preorder_only is not None: data["is_preorder_only"] = is_preorder_only
        if preorder_message is not None: data["preorder_message"] = preorder_message
        if order_quantity_minimum is not None: data["order_quantity_minimum"] = order_quantity_minimum
        if order_quantity_maximum is not None: data["order_quantity_maximum"] = order_quantity_maximum
        if open_graph_type is not None: data["open_graph_type"] = open_graph_type
        if open_graph_title is not None: data["open_graph_title"] = open_graph_title
        if open_graph_description is not None: data["open_graph_description"] = open_graph_description
        if is_open_graph_thumbnail is not None: data["is_open_graph_thumbnail"] = is_open_graph_thumbnail
        if upc is not None: data["upc"] = upc
        if date_last_imported is not None: data["date_last_imported"] = date_last_imported
        if option_set_id is not None: data["option_set_id"] = option_set_id
        if tax_class_id is not None: data["tax_class_id"] = tax_class_id
        if option_set_display is not None: data["option_set_display"] = option_set_display
        if bin_picking_number is not None: data["bin_picking_number"] = bin_picking_number
        if custom_url is not None: data["custom_url"] = custom_url
        if availability is not None: data["availability"] = availability
        if brand is not None: data["brand"] = brand
        if downloads is not None: data["downloads"] = downloads
        if images is not None: data["images"] = images
        if discount_rules is not None: data["discount_rules"] = discount_rules
        if configurable_fields is not None: data["configurable_fields"] = configurable_fields
        if custom_fields is not None: data["custom_fields"] = custom_fields
        if videos is not None: data["videos"] = videos
        if skus is not None: data["skus"] = skus
        if rules is not None: data["rules"] = rules
        if option_set is not None: data["option_set"] = option_set
        if options is not None: data["options"] = options
        if tax_class is not None: data["tax_class"] = tax_class
        if avalara_product_tax_code is not None: data["avalara_product_tax_code"] = avalara_product_tax_code
        print("Updating id {}.".format(id))
        r = requests.put(path, data=json.dumps(data), headers=self.headers)
        if self.debug:
            print(r.text)
        return r

    #######################
    # END Product Methods #
    #######################

    ##############################
    # START Bulk Pricing Methods #
    ##############################
    def createBulkPricingRule(self, product_id, type_var, type_value, mini, maxi):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/products/discount_rules
        RETURNS   -> r, the requests.post returned value
        __VARIABLES__
        product_id (str) is the id set by big commerce
        type_var (str) can be "price", "percentage", "fixed"
        type_value (int) is the value associated with the type
        min and max (int) refer to the quantity that must be purchased
            in order for the bulk pricing rule to take effect.
        """
        path = self.path + str(product_id) + "/discount_rules"
        data = {
                "min": str(mini),
                "max": str(maxi),
                "type": type_var,
                "type_value": int(type_value)
                }
        r = requests.post(
                          path,
                          data=json.dumps(data),
                          headers=self.headers
                          )
        if self.debug:
            print(r.text)
        return r

    ############################
    # END Bulk Pricing Methods #
    ############################


class Orders(BigCommerce):
    transactions_data_path = "transactions/bctransactions.csv"
    backup_path = "transactions/bctransactionsbackup.csv"

    def __init__(self, debug=False):
        self.debug = debug
        super(Products, self).__init__()
        self.path = self.path + "orders/"

    def listOrders(
                   self,
                   page=1,
                   limit=250,
                   sort=None,
                   min_id=None,
                   max_id=None,
                   min_total=None,
                   max_total=None,
                   customer_id=None,
                   status_id=None,
                   is_deleted=None,
                   payment_method=None,
                   min_date_created=None,
                   max_date_created=None,
                   min_date_modified=None,
                   max_date_modified=None
                   ):
        """
        """
        path = self.path
        payload = {"page": page, "limit": limit}
        if sort is not None: payload["sort"] = sort
        if min_id is not None: payload["min_id"] = min_id
        if max_id is not None: payload["max_id"] = max_id
        if min_total is not None: payload["min_total"] = min_total
        if max_total is not None: payload["max_total"] = max_total
        if customer_id is not None: payload["customer_id"] = customer_id
        if status_id is not None: payload["status_id"] = status_id
        if is_deleted is not None: payload["is_deleted"] = is_deleted
        if payment_method is not None: payload["payment_method"] = payment_method
        if min_date_created is not None: payload["min_date_created"] = min_date_created
        if max_date_created is not None: payload["max_date_created"] = max_date_created
        if min_date_modified is not None: payload["min_date_modified"] = min_date_modified
        if max_date_modified is not None: payload["max_date_modified"] = max_date_modified
        print("Requesting {} orders on page {}".format(limit, page))
        r = requests.get(path, params=payload, headers=self.headers)
        if self.debug:
            print(r.text)
        return r

    def listOrderProducts(self, order_id, page=1, limit=250):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/orders/products
        returns requests.get value
        r.json() contains the items in the order
        """
        order_id = str(order_id)
        path = "{}{}/products".format(self.path, order_id)
        payload = {"page": page, "limit": limit}
        print("Requesting {} products on page {} for order {}".format(limit, page, order_id))
        r = requests.get(path, params=payload, headers=self.headers)
        if self.debug:
            print(r.text)
        return r

    def getAllTransactions(self, num_transactions=500):
        """
        """
        o = {}
        t = {}
        r = None
        page = 1
        while r is None or r.status_code != 204:
            r = self.listOrders(page=page)
            page += 1
            try:
                orders = r.json()
                for order in orders:
                    order_id = order["id"]
                    o[order_id] = order
            except:
                pass
        # get products from orders
        for order in o:
            items = self.listOrderProducts(order).json()
            # print(items)
            for item in items:
                t_id = item["id"]
                t[t_id] = item
        return t

    def getOldTransactions(self):
        old_t = {}
        with open(self.transactions_data_path, "rb") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tr = row["transaction"]
                sku = row["sku"]
                quantity = row["quantity"]
                base_cost_price = row["base_cost_price"]
                base_price = row["base_price"]
                base_total = row["base_total"]
                order_id = row["order_id"]
                price_ex_tax = row["price_ex_tax"]
                price_inc_tax = row["price_inc_tax"]
                total_ex_tax = row["total_ex_tax"]
                total_inc_tax = row["total_inc_tax"]
                old_t[tr] = {
                             "sku": sku, 
                             "quantity": quantity,
                             "base_cost_price": base_cost_price,
                             "base_price": base_price,
                             "base_total": base_total,
                             "order_id": order_id,
                             "price_ex_tax": price_ex_tax,
                             "price_inc_tax": price_inc_tax,
                             "total_ex_tax": total_ex_tax,
                             "total_inc_tax": total_inc_tax
                             }
        return old_t

    def saveTransactions(self, num_transactions=500):
        """
        returns unseen transactions and writes the last 5000 transactions to a spreadsheet.
        """
        old_t = self.getOldTransactions()
        new_t = self.getAllTransactions()
        new_trans = {}
        for t in new_t:
            if str(t) not in old_t:
                tr = new_t[t]
                old_t[t] = {
                            "sku": tr["sku"],
                            "quantity": tr["quantity"],
                            "base_cost_price": tr["base_cost_price"],
                            "base_price": tr["base_price"],
                            "base_total": tr["base_total"],
                            "order_id": tr["order_id"],
                            "price_ex_tax": tr["price_ex_tax"],
                            "price_inc_tax": tr["price_inc_tax"],
                            "total_ex_tax": tr["price_ex_tax"],
                            "total_inc_tax": tr["total_inc_tax"]
                            }
                new_trans[t] = {
                                "sku": tr["sku"],
                                "quantity": tr["quantity"],
                                "base_cost_price": tr["base_cost_price"],
                                "base_price": tr["base_price"],
                                "base_total": tr["base_total"],
                                "order_id": tr["order_id"],
                                "price_ex_tax": tr["price_ex_tax"],
                                "price_inc_tax": tr["price_inc_tax"],
                                "total_ex_tax": tr["price_ex_tax"],
                                "total_inc_tax": tr["total_inc_tax"]
                                }
        st = sorted(old_t.items(), key=lambda x: -int(x[0]))
        # print(st)
        with open(self.transactions_data_path, "wb") as f:
            fieldnames = ["transaction",
                          "sku",
                          "quantity",
                          "base_cost_price",
                          "base_price",
                          "base_total",
                          "order_id",
                          "price_ex_tax",
                          "price_inc_tax",
                          "total_ex_tax",
                          "total_inc_tax",
                          ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            counter = 0
            for t in st:
                if counter > 5000:
                    break
                tr = t[1]
                writer.writerow({"transaction": str(t[0]),
                                 "sku": tr["sku"],
                                 "quantity": tr["quantity"],
                                 "base_cost_price": tr["base_cost_price"],
                                 "base_price": tr["base_price"],
                                 "base_total": tr["base_total"],
                                 "order_id": tr["order_id"],
                                 "price_ex_tax": tr["price_ex_tax"],
                                 "price_inc_tax": tr["price_inc_tax"],
                                 "total_ex_tax": tr["total_ex_tax"],
                                 "total_inc_tax": tr["total_inc_tax"]
                                 })
                counter += 1
        return new_trans

    def getDebits(self, num_transactions):
        t = self.saveTransactions()
        debits = {}
        for tr in t:
            sku = t[tr]["sku"]
            if sku in debits:
                debits[sku] += int(t[tr]["quantity"])
            else:
                debits[sku] = int(t[tr]["quantity"])
        return debits

    def listShipments(self, order_id, page=1, limit=50):
        path = "{}{}/shipments".format(self.path, order_id)
        payload = {"page": str(page), "limit": str(limit)}
        r = requests.get(path, headers=self.headers, params=payload)
        print(r.status_code)
        return r

    def getShipmentId(self, order_id):
        r = self.listShipments(order_id)
        return r.json()[0]["id"]

    def updateShipmentTracking(self, order_id, tracking_number):
        """
        Only works on packages that have already been marked as shipped 
            and "ship items" has been clicked.
        """
        sid = self.getShipmentId(order_id)
        path = self.path + str(order_id) + "/shipments/" + str(sid)
        print(path)
        data = {"tracking_number": str(tracking_number)}
        r = requests.put(path, data=json.dumps(data), headers=self.headers)
        return r

    def createShipment(self):
        pass


class Content(BigCommerce):

    def __init__(self):
        super(Products, self).__init__()

    def createABlog(self, title, body, author=None, tags=None):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/blog/posts
        __VARIABLES__
        title (str)    -> The title of the blog post
        body  (str)    -> The html body of the blog post
        author (str)   -> The author of the article
        tags (list)    -> list of tag strings
        Apparently post requests are not allowed on this url path?
        Unusable right now.
        """
        path = self.path + "blog/posts"
        print(path)
        data = {}
        data["title"] = title
        data["body"] = body
        if author is not None: data["author"] = author
        if tags is not None: data["tags"] = str(tags)
        r = requests.post(self.path, headers=self.headers, data=data)
        return r


class Customers(BigCommerce):

    def __init__(self):
        super(Products, self).__init__()
        self.path = self.path + "customer_groups/"

    def listCustomerGroups(self, name=None, is_default=None, page=1, limit=50):
        path = self.path
        payload = {"page": page, "limit": limit}
        if name is not None: payload["name"] = name
        if is_default is not None: payload["is_default"] = is_default
        r = requests.get(path, headers=self.headers, params=payload)
        return r

    def getWholesaleID(self):
        r = self.listCustomerGroups()
        data = r.json()
        for group in data:
            if group["name"] == "Wholesale":
                return str(group["id"])
        raise Exception("Wholesale group not found.")

    def updateCustomerGroup(self, id, data):
        """
        REFERENCE -> https://developer.bigcommerce.com/api/stores/v2/customer_groups
        id   -> customer group id number.
        data -> put request data
        """
        path = self.path + str(id)
        r = requests.put(path, data=data, headers=self.headers)
        return r


def testclasses():
    print(Products.path)


def testCreateBulkPricingRule():
    p = Products()
    r = p.createBulkPricingRule(11334, "percent", "5", "13", "14")
    print(r.url)
    print(r.text)
    # 201 is the success status code.
    print(r.status_code)
    print(r.json())


def testListProducts():
    p = Products()
    r = p._listProducts(limit=2)
    # print(r.json())
    # print(r.text)
    # print(r.status_code)
    # print(r.url)
    print(pprint.pformat(r.json()))


def testGetAllProducts():
    p = Products()
    skus = p.getAllProducts()["skus"]
    for sku in skus:
        print("{}: id={}, stock={}".format(sku, skus[sku]["id"], skus[sku]["inventory_level"]))


def testGetSingleProduct():
    p = Products()
    sku = p.getSingleProduct("1335")
    print(sku)


def testGetOrders():
    o = Orders()
    r = o.listOrders()
    print(pprint.pformat(r.json()))


def testListOrderProducts():
    o = Orders()
    r = o.listOrderProducts(101)
    print(pprint.pformat(r.json()))


def testGetAllTransactions():
    o = Orders()
    t = o.getAllTransactions()
    print(pprint.pformat(t))


def testSaveTransactions():
    o = Orders()
    t = o.getAllTransactions()
    o.saveTransactions(500)


def listCustomerGroups():
    c = Customers()
    r = c.listCustomerGroups()
    print(pprint.pformat(r.json()))


def testListShipments():
    o = Orders()
    r = o.listShipments(164)
    print(r.json()[0])


def testUpdateShipmentTracking():
    o = Orders()
    r = o.updateShipmentTracking("164", "9400115901648459036562")
    print(r.content)


def testListProductImages():
    p = Products()
    r = p.listProductImages(7579)
    print(pprint.pformat(r.json()))


def testCreateProductImage():
    """
    Don't know if this works
    """
    p = Products()
    r = p.createProductImage(7579, "https://www.featherout.com/assets/Product_Photos/pink3.jpg")
    # print(pprint.pformat(r.json()))
    print(r.text)


def testUpdateProductImage():
    """
    works
    """
    p = Products()
    r = p.updateProductImage(7580, "18471", "https://www.featherout.com/assets/Product_Photos/white1.jpg", sort_order=0)
    print(pprint.pformat(r.json()))
    # print(dir(r))
    # print(r.content)
    # print(r.headers)


if __name__ == '__main__':
    # testclasses()
    # testCreateBulkPricingRule()
    # testListProducts()
    # testGetAllProducts()
    # testGetSingleProduct()
    # testGetOrders()
    # testListOrderProducts()
    # testGetAllTransactions()
    # testSaveTransactions()
    # listCustomerGroups()
    # testListShipments()
    # testUpdateShipmentTracking()
    # testListProductImages()
    # testCreateProductImage()
    testUpdateProductImage()
