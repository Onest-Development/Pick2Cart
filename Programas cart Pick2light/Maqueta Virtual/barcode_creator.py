import barcode
from barcode.writer import ImageWriter

# 1. Define your list of barcode data (can be strings or numbers)
code_list = [
    "V02542512",
    "V01145103",
    "V03542512",
    "V01145003",
    "494114",
    "580204",
    "427625"
    ]

# Choose the barcode format (Code128 works great for general text and numbers)
barcode_format = barcode.get_barcodeclass("code128")

for code in code_list:
    # Create the barcode instance with the data and image writer
    my_barcode = barcode_format(code, writer=ImageWriter())

    # Save the file (it appends .png automatically when using ImageWriter)
    filename = my_barcode.save(f"barcode_{code}")
    print(f"Generated: {filename}")