import re
with open("tests/autoscrapper/ocr/test_inventory_vision.py", "r") as f:
    content = f.read()

content = re.sub(r'class TestEnableOcrDebug:[\s\S]*?(?=class TestEnableOcrDebug:)', '', content, count=1)
with open("tests/autoscrapper/ocr/test_inventory_vision.py", "w") as f:
    f.write(content)
