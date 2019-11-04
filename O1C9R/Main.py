#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019
@author: RecepKarademir
O1CR9
"""

# 64 bit pillow için

from PIL import Image  # Fotoğrafı okumak kaydetme göstermek boyutlandırmak için eklenen kütüphane.
import PIL
import numpy as np  # Fotoğrafı matrise çevirme, çok boyutlu matris işlemleri vs. görevler için.
import cv2  # OpenCV görüntü işleme kütüphanesi programa dahil ediliyor
import os  # Dosya konumlarıyla işlem yapabileceğimiz kütüphane
import glob  # Dosya ve klasör yönetimi modülü
import imagehash  # image hashing ile fotoğraf benzerliği kontrol kütüphanesi
import array as arr  # Dizi işlemleri kütüphanesi

img_data = []  # kıyaslamada kullanılacak eğitim karakterlerin fotoğraflarını tutan liste
TahminEtiket = []  # kıyaslamada kullanılacak eğitim karakterlerin etiketlerini tutan liste
kiyas_boyut = 0

# karakterlerin tahmin oranlarını tutan dizi
tahmin_oran = arr.array('f', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# karakterler arası boşluk kontrolü için konum farklarını tutan dizi
bosluk_fark = arr.array('i', [0, 0])

# 0.indis satırın y konumunu     1.indis satırın yüksekliğini tutar
satir_sonu_konum = arr.array('i', [0, 0, 0, 0])

karakter = []  # tahmin edilen karakterlerin sırasız olarak tutulduğu dizi

# Aşağıdaki diziler ise karakter dizisindeki tahmin karakterlerinin konumlarını tutar
karakter_konum_y = []  # tahmin edilen karakterin y konumu
karakter_konum_x = []  # tahmin edilen karakterin x konumu
karakter_konum_w = []  # tahmin edilen karakterin taban genişliği
karakter_konum_h = []  # tahmin edilen karakterin yüksekliği


def fotograf_kontrol():  # Fotoğrafın var olup olmadığı kontrolü
    if (os.path.isfile("img.jpg")):
        print("Fotoğraf kontrolü yapıldı. Fotoğraf bulundu.")
        return 1
    else:
        print("Fotoğraf bulunamadı! \nFotoğraf uygulama klasöründe değil !\nProgram sonlandırılıyor...")
        return 0


def karakter_belge_kontrol():  # Çıktı txt dosyası kontrolü
    if (os.path.isfile("output.txt")):
        karakter_belge = open('output.txt', 'w')  # txtnin boş olması gerekli
        karakter_belge.write("")  # dosya içini boşalttık
        return 1
    else:
        print("Çıktı belgesi yok! \noutput.txt bulunamdı!\nProgram sonlandırılıyor...")
        return 0


def fotograf_oku():  # Fotoğraf okuma fonksiyonu
    image = cv2.imread('img.jpg')

    width = image.shape[1]  # Başarıyla okunulan fotoğraf boyutları okunuyor
    height = image.shape[0]

    dim = (2 * width, 2 * height)  # Ocr işlemine alınacak fotoğraf boyutu iki katına çıkarılacak.
    if (width + height) < 1280:  # Fotoğraf boyutu küçükse karakter tanımlama için uygun boyuta getiriliyor.
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return image


def fotograf_goster(Image, Baslik):
    window_title = "{}".format(Baslik)
    cv2.imshow(window_title, Image)


def karakter_yaz(karakter):  # Karakterler txt dosyasına fotoğraftaki formatta kaydedilir.
    karakter_belge = open('output.txt', 'a')  # txtnin sonuna eklemeyle karakteler yazılır
    karakter_belge.write(karakter)


def fotograf_onislem():
    # Grayscale (Gri seviye dönüştürme)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image fotoğrafı gri seviyeye dönüştürülüp gray değikenine aktarılır.

    # Binary (Siyah-beyaz fotoğraf dönüşümü)
    # 125  gri seviyenin binarye dönüştüğü eşik değer.
    # 37  blockSize:kaç boyutlu filtre ile her pikselin komşusuna bakılıp yeni piksel değeri atanacğını belileyen filtre boyutu.
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 125, 33)
    # gray fotoğrafı ikili fotoğrafa dönüştürülüp binary değişkenine aktarılıyor.

    # Dilation (Karakter gövde belirginleştirme)
    kernel = np.ones((2, 2), np.uint8)  # siyah zemin üzerindeki nesneyi 2px dikey ve 1px yatay genişlet
    img_dilation = cv2.dilate(binary, kernel, iterations=1)  # binary fotoğrafa bir kez genişletmeyi uygular

    # Dilation (Karakter gövde belirginleştirme) Satır tespit etmek için karakterler yatay genişletilecek.
    kernel = np.ones((1, 250), np.uint8)  # siyah zemin üzerindeki nesneyi 1px dikey ve 250px yatay genişlet
    satir_konum_dilation = cv2.dilate(binary, kernel, iterations=1)  # binary fotoğrafa bir kez genişletmeyi uygular

    cv2.imwrite("dilation.png", cv2.bitwise_not(img_dilation))  # hashing işlemi için fotoğraf rengi tersleniyor.
    image_invert_dilation = Image.open("dilation.png")

    fotograf_goster(img_dilation, "Karakter Yayma")  # Karakterlerin genişletilmiş hali
    fotograf_goster(satir_konum_dilation, "SATIR ALANLARI")  # Satırların belirginleşmiş hali

    return image_invert_dilation, img_dilation, satir_konum_dilation  # Paramatreler geri döndürülüyor


def kontur_bul():
    ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)  # cv2.RETR_EXTERNAL yerine cv2.RETR_TREE kullanmak iç içe yapılarda karakter tanıma yapabilir
    ctrs_satir, hier2 = cv2.findContours(satir_konum_dilation.copy(), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)  # iç içe yapılarda karakter tanımlama yapamaz

    # Konturlar sıralanıyor
    sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[
        0])  # 0 : fotoğrafta soldan sağa doğru konturları sıralar. Sıralı karakter tespiti için
    sorted_ctrs_satir = sorted(ctrs_satir, key=lambda ctr: cv2.boundingRect(ctr)[
        1])  # 1 :fotoğrafta yukarıdan aşağı doğru konturları sıralar. Satırlar için
    # Kontur sıralaması ilk sıralı karakter ve sıralı satır tespitine kullanılır.

    return sorted_ctrs, sorted_ctrs_satir


def kiyas_fotolari_yukle():
    for img in glob.glob("Karakterler/*.png"):  # klasör içindeki kontrol fotoğrafları listeye aktarılır.
        img2 = PIL.Image.open(img)
        img_data.append(img2)  # listeye kontrol fotoğrafları ekleniyor
        fileNameExtension = os.path.basename(img)
        TahminEtiket.append(fileNameExtension)  # tahmin listesine fotoğraf etiketleri ekleniyor

    kiyas_boyut = len(img_data)  # kıyasta kullanılacak fotoğrafların dizi boyutu
    return kiyas_boyut


def karakter_tahmin():
    for i, ctr in enumerate(sorted_ctrs):

        # Sınır konumları alınıyor.
        x, y, w, h = cv2.boundingRect(ctr)

        # Kıyas yapılacak bölge fotoğraftan kırpılıyor
        karakter_bolgesi = image_invert_dilation.crop((x, y, x + w, y + h))

        roi = karakter_bolgesi.convert('P', colors=255,
                                       palette=Image.ADAPTIVE)  # karakter bölgesini roi değikenine atar


        hash0 = imagehash.average_hash(roi, 64)  # roi bölgesinin hash kodunu hosh0 a atar.

        if w > 15 or h > 15:  # çok küçük boyutlu bölgelerde karakter tanımlama yapılmaz
            tahmin_oran = [0] * 10  # bütün dizi elemanları 0 olacak

            for index in range(kiyas_boyut):
                img2 = img_data[index]

                # filename tahminde kullanılacak karakter etiketleri olacak
                fileNameExtension = TahminEtiket[index]
                filename, file_extension = os.path.splitext(fileNameExtension)
                filename = filename.split()[0]  # ilk karakter tahmin değeri olacak

                width, height = roi.size
                # kontrol yapılacak bölgenin, kıyas yapılacak karakter fotoğrafıyla aynı boyutta olamsı gerekli
                img2 = img2.resize((width, height), Image.ANTIALIAS)

                hash1 = imagehash.average_hash(img2, 64)  # etiketli kıyas fotoğrafının hash değeri hash1 e atanır

                i = int(filename)  # filename etiketli tahmindir
                fark = (1 - ((hash0 - hash1) / len(hash0.hash) ** 2))  # hash farkları hesaplanıyor.
                if fark > tahmin_oran[i]:  # en çok benzerlik içeren oran tahmin dizisine eklenir
                    tahmin_oran[i] = fark

            digit = (tahmin_oran.index(max(tahmin_oran)))  # en yüksek benzerlik içeren etiket bulunur
            if tahmin_oran[digit] > 0.73:  # %73 benzerlik içeren karakter etiketi için tahmin yapılır
                fc = str(digit)  # etiket stringe dönüştürülür

                cv2.rectangle(image, (x, y), (x + w - 1, y + h - 1), (0, 0, 255),
                              1)  # tahmin karakteri alanı işaretlenir
                cv2.putText(image, fc, (x, y + 5), cv2.FONT_HERSHEY_PLAIN, 2, (36, 255, 12),2)  # B:36 G:255 R:12 yazı renk kodu. etiket fotoğrafa eklendi

                karakter.append(fc)  # tahmin edilen karakter sırasız olarak listeye kaydediliyor
                karakter_konum_x.append(x)  # karakterin konum bilgileri de kaydediliyor
                karakter_konum_y.append(y)
                karakter_konum_w.append(w)
                karakter_konum_h.append(h)


def satir_bosluk_bul():
    kiyas_boyut = len(karakter)
    bosluk_index = 0
    bosluk_bayrak = 0

    for i, ctrs_konum in enumerate(
            sorted_ctrs_konum):  # sırasıyla satırlar bulunur. Satır içindeki karakterler arası boşluk bulunur.

        # satırın konumları alınıyor
        x, y, w, h = cv2.boundingRect(ctrs_konum)

        if w > 15 and h > 15:  # satır küçük boyutlarda olamaz
            cv2.rectangle(image, (x, y), (x + w - 1, y + h - 1), (0, 255, 0),
                          1)  # satır alanını yeşil dikdörtgenle çizecek
            if i == 0:
                satir_sonu_konum[0] = y  # satır sonunun y başlangıç konumunu tutar
                satir_sonu_konum[1] = h  # satır sonunun yüksekliğini tutar
            elif i % 2 == 0:
                if abs(y - satir_sonu_konum[0]) > int(satir_sonu_konum[1] / 2):
                    karakter_yaz("\n")  # Satır sonu txt ye yazılıyor
            else:
                if abs(y - satir_sonu_konum[0]) > (int)(satir_sonu_konum[1] / 2):
                    karakter_yaz("\n")  # Satır sonu txt ye yazılıyor
            for index in range(kiyas_boyut):
                merkez_X = int(karakter_konum_x[index] + karakter_konum_w[
                    index] / 2)  # Satır içindeki karakterin merkez noktası hesaplanıyor
                merkez_Y = int(karakter_konum_y[index] + karakter_konum_h[
                    index] / 2)  # Satır içindeki karakterin merkez noktası hesaplanıyor

                # Satır içindeki karakterin merkez noktası, satır kordinatları içindeyse txt ye karakter kaydediliyor.
                if x <= merkez_X <= (x + w) and y <= merkez_Y <= (y + h):
                    bosluk_fark[bosluk_index] = index
                    if bosluk_bayrak == 0:  # karakterler arasında bir karakterlik boşluk varsa boşluk eklenecek
                        fark = abs((karakter_konum_x[bosluk_fark[0]] + karakter_konum_w[bosluk_fark[0]]) - (
                            karakter_konum_x[bosluk_fark[1]]))
                        if fark > (karakter_konum_w[bosluk_fark[
                            0]] * 2):  # karakterler arasında iki karakterlik boşluk varsa boşluk eklenecek
                            karakter_yaz(" ")  # Boşluk txt ye yazılıyor
                        bosluk_index = 0
                        bosluk_bayrak = 1
                    else:
                        temp = bosluk_fark[0]
                        bosluk_fark[0] = bosluk_fark[1]
                        bosluk_fark[1] = temp
                        fark = abs((karakter_konum_x[bosluk_fark[0]] + karakter_konum_w[bosluk_fark[0]]) - (
                            karakter_konum_x[bosluk_fark[1]]))
                        if fark > (karakter_konum_w[bosluk_fark[
                            0]] * 2):  # karakterler arasında iki karakterlik boşluk varsa boşluk eklenecek
                            karakter_yaz(" ")  # Boşluk txt ye yazılıyor

                    karakter_yaz(karakter[index])  # Tahmin edilen karakter txt ye yazılıyor.


"""
    PROGRAM BAŞLANGIÇ KISMI
"""

if fotograf_kontrol() and karakter_belge_kontrol():  # Fotoğraf ve çıktı belgesi varsa karakter tanımlama başlıyor.
    print("Karakter tanımlama başlıyor...")

    image = fotograf_oku()  # Fotoğraf oknup değişkene aktarıldı

    image_invert_dilation, img_dilation, satir_konum_dilation = fotograf_onislem()  # Fotoğraf önişleme alınıyor

    sorted_ctrs, sorted_ctrs_konum = kontur_bul()  # Karakter tahmin alanları ve satır alanları kontur tespitiyle bulunuyor

    kiyas_boyut = kiyas_fotolari_yukle()  # Tahmin için kıyaslanacak fotoğraflar okunuyor.

    karakter_tahmin()  # Fotoğraftaki karakterlerin eğitimdeki karakterlerle kıyaslandığı fonksiyon

    satir_bosluk_bul()  # Satırları ve karakterler arasındaki boşlukları bulan fonksiyon

    fotograf_goster(image, "Fotograf")  # ocr yapılan fotoğraf
    os.startfile(r'output.txt')  # Ocr sonucu Notepad ile açılıyor

    cv2.waitKey(0)  # Pencerelerin kapatılmak için tuşa basılmasını bekleniyor
    exit(1)

else:  # Fotoğraf bulunamışsa uygulama sonlandırılır.
    exit(1)