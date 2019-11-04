# Kütüphane eklenirken ki hataları yakalamak için try-except bloğu
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# Tesseract kütüphanesinin çalışabilmesi için tesseract dosya konumu tanıtılmalı
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\RCP\\AppData\\Local\\Tesseract-OCR\\tesseract'

# Fotoğraftan yazıya dönüşüm için fotoğraf konumu ve belge dili seçimleri yapılır
text = pytesseract.image_to_string(Image.open("images/img.png"), lang='eng')

#Çıktı string olarak alınır
print(text)


