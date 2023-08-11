# NAMED CONSTANTS
COD = "cash_on_delivery"
ECOD = "electronic_cash_on_Delivery"
QRCODE = "qr_code"
RAZORPAY = "razorpay"
CARD = "card"
UPI = "upi"
CASH = "cash"
NETBANKING = "netbanking"
WEBSITE = "website"
BILL = "BILL"
BILLING = "BILLING"
INVENTORY = "inventory"
CATEGORY = "category"
PRODUCTS = "products"
OTHERS = "others"
CUSTOMER = "customer"
ITEMS = "items"
CART = "cart"
WALLET = "wallet"
EXTERNAL = "external"
EXPRESS = "EXPRESS"
EVERYTHING = "EVERYTHING"

# NUMERIC CONSTANTS
ZERO = 0
ONE = 1
TWO = 2
TEN = 10
THREE = 3
FOUR = 4
EIGHT = 8
FIVE = 5
SIX = 6
TWENTY = 20
FIFTY = 50
HUNDRED = 100
TWO_HUNDRED = 200
ONE_THOUSAND = 1000

# STATUS TYPES
SUCCESS = "SUCCESS"
FAILED = "FAILED"
PENDING = "PENDING"
ORDER_PLACED = "ORDER_PLACED"
CHECKOUT = "CHECKOUT"

# RAZORPAY CONSTANTS
LINK = "link"
INV_PAID = "invoice.paid"
PAYMENT_CAPTURED = "payment.captured"
PAYMENT_FAILED = "payment.failed"
CAPTURED = "captured"
PAYMENT_PENDING = "PAYMENT_PENDING"


# MODEL CHOICES CONSTANTS
FULFILMENT_TYPES = (("TAKE_AWAY", "TAKE_AWAY"), ("DELIVERY", "DELIVERY"))
DELIVERY_TYPES = (
    ("EXPRESS_DELIVERY", "EXPRESS_DELIVERY"),
    ("EVERYTHING", "EVERYTHING"),
    ("TAKE_AWAY", "TAKE_AWAY"),
)
CART_STATUS_TYPES = (
    ("ACTIVE", "ACTIVE"),
    ("DISCARDED", "DISCARDED"),
    ("ORDER_PLACED", "ORDER_PLACED"),
)
ORDER_STATUS_TYPES = (
    ("SUCCESS", "SUCCESS"),
    ("PAYMENT_FAILED", "PAYMENT_FAILED"),
    ("CHECKOUT", "CHECKOUT"),
    ("PAYMENT_SUCCESS", "PAYMENT_SUCCESS"),
)
PAYMENT_STATUS_TYPES = (
    ("PENDING", "PENDING"),
    ("SUCCESS", "SUCCESS"),
    ("CHECKOUT", "CHECKOUT"),
    ("FAILED", "FAILED"),
)
PAYMENT_SOURCES = (
    ("website", WEBSITE),
    ("mobile_application", "Mobile Application"),
    ("BILL", BILL),
)
PAYMENT_MODES = (
    (UPI, "UPI"),
    (CASH, "Cash"),
    (NETBANKING, "Netbanking"),
    (ECOD, "ECOD"),
    (WALLET, "Wallet"),
    (CARD, "Card"),
)

CODE_TYPE = (("A", "ABSOLUTE"), ("P", "PERCENTAGE"))

DELIVERY_STATUS_TYPES = (
    ("ORDER_PLACED", "ORDER_PLACED"),
    ("IN_PACKAGING", "IN_PACKAGING"),
    ("FAILED", "FAILED"),
    ("IN_TRANSIT", "IN_TRANSIT"),
    ("DELIVERED", "DELIVERED"),
    ("ASSIGNED", "ASSIGNED"),
    ("PAYMENT_PENDING", "PAYMENT_PENDING"),
)
APPLIED_CHOICES = (
    ("category", "category"),
    ("products", "products"),
    ("inventory", "inventory"),
    ("customer", "customer"),
    ("others", "others"),
)

APPLY_TYPE_CHOICES = (("cart", "cart"), ("items", "items"))

ATTRIBUTE_CHOICES = (("promotional", "promotional"), ("transactional", "transactional"))
