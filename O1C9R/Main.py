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
import cv2  # OpenCV görüntü işleme kütüphanesi
import os  # Dosya konumlarıyla işlem yapabileceğimiz kütüphane
import glob  # Dosya ve klasör yönetimi modülü
import imagehash  # image hashing ile fotoğraf benzerliği kontrol kütüphanesi
import array as arr  # Dizi işlemleri kütüphanesi

hashSet=[] # Kıyas fotoğraflarının hash bilgilerini tutacak list
TahminEtiket = []  # kıyaslamada kullanılacak eğitim karakterlerin etiketlerini tutan liste
kiyas_boyut = 0 # Kıyas fotoğraf adetini tutacak değişken

# karakterlerin tahmin oranlarını tutan dizi
tahmin_oran = arr.array('f', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

karakter = []  # tahmin edilen karakterlerin sırasız olarak tutulduğu dizi
SiraliKarakterler="" # Program sonunda Txtye yazılacak metni tutan string.

# Aşağıdaki diziler ise karakter dizisindeki tahmin karakterlerinin konumlarını tutar
karakter_konum_y = []  # tahmin edilen karakterin y konumu
karakter_konum_x = []  # tahmin edilen karakterin x konumu
karakter_konum_w = []  # tahmin edilen karakterin taban genişliği
karakter_konum_h = []  # tahmin edilen karakterin yüksekliği


def fotograf_kontrol():  # Fotoğrafın var olup olmadığı kontrolü yapılır
    if (os.path.isfile("img.jpg")): # Proje klasörü içinde fotoğraf varlığı kontrol ediliyor
        print("Fotoğraf kontrolü yapıldı. Fotoğraf bulundu.")
        return 1 # Fotoğraf varsa devam edilir.
    else:
        print("Fotoğraf bulunamadı! \nFotoğraf uygulama klasöründe değil !\nProgram sonlandırılıyor...")
        return 0 # Fotoğraf yoksa program sonlandırılır.


def karakter_belge_kontrol():  # Çıktı output.txt dosyası kontrolü
    if (os.path.isfile("output.txt")):# Proje klasörü içinde çıktı belgesi varlığı kontrol ediliyor
        return 1 # Belge bulundu
    else:
        print("Çıktı belgesi yok! \noutput.txt bulunamdı!\nProgram sonlandırılıyor...")
        return 0 # Belge yoksa program sonlandırılır.


def fotograf_oku():  # Konrolü yapılan fotoğraf ocr için değişkene aktarılır.
    image = cv2.imread('img.jpg') # Fotoğraf OpenCv fonksiyonu yardımıyla bir değişkene aktarıldı.

    # Fotoğraf boyutları bulunuyor
    taban = image.shape[1]
    yukseklik = image.shape[0]

    # Ocr işlemine alınacak fotoğraf boyutu iki katına çıkarılacak.
    if (taban + yukseklik) < 1280:  # Fotoğraf boyutu küçükse karakter tanımlama için uygun boyuta getiriliyor.
        # Fotoğraf 2 katı boyuna genişletiliyor.
        image = cv2.resize(image, (2 * taban, 2 * yukseklik), interpolation=cv2.INTER_AREA)
    return image # Ana programa fotoğraf döndürülüyor.


def fotograf_goster(Image, Baslik): # Parametre olarak gelen fotoğrafı ve açıklamayı yeni pencere içerisinde gösteren fonksiyon.
    window_title = "{}".format(Baslik)
    cv2.imshow(window_title, Image)


def karakter_yaz(karakterler):  # String içindeki formatlı karakterler txt dosyasına fotoğraftaki gibi kaydedilir.
    karakter_belge = open('output.txt', 'w')# output.txt içeriği silinip üzerine yazılıyor.
    karakter_belge.write(karakterler)
    karakter_belge.close() # Dosya yazma işlemi (TextIOWrapper) kapatılıyor.

def fotograf_onislem():
    # Grayscale (Gri seviye dönüştürme)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image fotoğrafı gri seviyeye dönüştürülüp gray değikenine aktarılır.

    # Binary (Siyah-beyaz fotoğraf dönüşümü)
    # 125  gri seviyenin binarye dönüştüğü eşik değer.
    # 33  blockSize:kaç boyutlu filtre ile her pikselin komşusuna bakılıp yeni piksel değeri atanacğını belileyen filtre boyutu.
    # Gaussion _/\_ eğrisi yöntemiyle fotoğraftaki merkez piksel(ağırlıklı pikseller) vurgulanır.
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 125, 33)
    # gray fotoğrafı , ters ikili fotoğrafa dönüştürülüp binary değişkenine aktarılıyor.

    # Dilation (Karakter gövde belirginleştirme)
    yayma_oran = np.ones((2, 2), np.uint8)  # siyah zemin üzerindeki nesneleri 2px dikey ve 2px yatay genişletir
    karakter_dilated = cv2.dilate(binary, yayma_oran, iterations=1)  # binary fotoğrafa bir kez genişletmeyi uygular

    # Dilation (satır bölge belirginleştirme) Satır tespit etmek için karakterler yatay genişletilecek.
    yayma_oran = np.ones((1, 250), np.uint8)  # siyah zemin üzerindeki nesneyi 1px dikey ve 250px yatay genişlet
    satir_dilated = cv2.dilate(binary, yayma_oran, iterations=1)  # binary fotoğrafa bir kez genişletmeyi uygular

    cv2.imwrite("dilated.png", cv2.bitwise_not(karakter_dilated))  # hashing işlemi için fotoğraf rengi tersleniyor.
    kirpilabilir = Image.open("dilated.png") # karakterler kıyaslama için bu fotoğraftan kırpılabilir.

    fotograf_goster(karakter_dilated, "Karakter Yayma")  # Karakterlerin genişletilmiş hali gösterilecek
    fotograf_goster(satir_dilated, "SATIR ALANLARI")  # Satırların belirginleşmiş hali gösterilecek

    return kirpilabilir, karakter_dilated, satir_dilated  # Fotoğraflar ana programa geri döndürülüyor


def kontur_bul(): # Fotoğraftaki nesnelerin çevrelerinin belirlendiği  fonksiyon.
    karakter_konturlari, a = cv2.findContours(karakter_dilated.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  # cv2.RETR_EXTERNAL yerine cv2.RETR_TREE kullanmak iç içe yapılarda karakter tanıma yapabilir
    satir_konturlari, b = cv2.findContours(satir_dilated.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  # iç içe yapılarda karakter tanımlama yapamaz

    # Konturlar sıralanıyor
    sirali_karakter_konturlari = sorted(karakter_konturlari, key=lambda ctr: cv2.boundingRect(ctr)[0])  # 0 : fotoğrafta soldan sağa doğru konturları sıralar. Sıralı karakter tespiti için
    sirali_satir_konturlari = sorted(satir_konturlari, key=lambda ctr: cv2.boundingRect(ctr)[1])  # 1 :fotoğrafta yukarıdan aşağı doğru konturları sıralar. Satırlar için
    # Kontur sıralaması sıralı karakter ve sıralı satır tespitine kullanılır.
    return sirali_karakter_konturlari, sirali_satir_konturlari #kontur bilgileri ana programa geri döndürülüyor.

def kiyas_fotolari_yukle(): # Karakter klasöründeki fotoğrafların hash bilgileri hashSet listesine kaydedilecek.
    for img in glob.glob("Karakterler/*.png"):  # klasör içindeki kıyas fotoğrafları listeye aktarılır.
        file_full_name = os.path.basename(img) # Fotoğraf tam adı  ABC (D).PNG bulunuyor
        # filename tahminde kullanılacak karakter etiketleri olacak
        filename, file_extension = os.path.splitext(file_full_name) # file_extension= .png veya .jpg   filename= 1  2  3 vs
        filename = filename.split()[0]  # ilk karakter tahmin etiketi listesine eklenecek
        TahminEtiket.append(filename)  # tahmin listesine fotoğraf etiketleri ekleniyor
        hashSet.append(imagehash.average_hash(PIL.Image.open(img), 64))  # Kıyas fotoğrafının hash değeri hashSet e atanır
        # Hash kıyasta kullanılacak fotoğrafların dizi boyutu
    return len(TahminEtiket) # Kıyas hashsetinin boyutu

def karakter_tahmin(): # Etiketli fotoğraflarla kırpılan fotoğrafların kıyaslanacağı fonksiyon.
    for kontur in sirali_karakter_konturlari: #soldan sağa doğru kaydedilen karakter alanları
        # Karakter alanlarının sınır konumları alınıyor.
        x, y, w, h = cv2.boundingRect(kontur)

        # Kıyas yapılacak bölge fotoğraftan kırpılıyor
        karakter_bolgesi = kirpilabilir.crop((x, y, x + w, y + h)) # Başlangıç(x, y) ,Bitiş(x + w, y + h)
        kirpilan = karakter_bolgesi.convert('P', colors=255,palette=Image.ADAPTIVE)  # karakter bölgesi kirpilan değikenine atar

        hash0 = imagehash.average_hash(kirpilan, 64)  # kirpilan bölgesinin hash kodunu hash0 a atar. 64x64 lük hash kodu üretir.

        if w > 15 or h > 15:  # çok küçük boyutlu bölgelerde karakter tanımlama yapılmaz
            tahmin_oran = [0] * 10  # Her karakter tanımlanacağı zaman o anki tahmin oranını tutan dizi elemanları 0 olacak.
            for indis in range(kiyas_boyut): # kiyas_boyut: Hashset dizi boyutudur. Etiketli karakterlerin "Karakter" klasöründeki adeti kadar.

                filename = TahminEtiket[indis] # Sırasıyla bütün etiketli fotoğrafların hash değerleri kıyaslanacak.
                hash1 = hashSet[indis]
                i = int(filename)  # filename etiketli tahmindir
                benzerlik = (1 - ((hash0 - hash1) / len(hash0.hash) ** 2))  # hash benzerliği hesaplanıyor. 0 tamamen farklı. 1 tamamen aynı
                if benzerlik > tahmin_oran[i]:  # en çok benzerlik içeren oran tahmin dizisine eklenir
                    tahmin_oran[i] = benzerlik
            tahmin_etiket = (tahmin_oran.index(max(tahmin_oran)))  # en yüksek benzerlik içeren indis tahmin etiketi bulunur

            if tahmin_oran[tahmin_etiket] > 0.73:  # Tahmin oranı %73 benzerlik içeren karakter, tahmin stringine eklenir.
                tahmin = str(tahmin_etiket)  # etiket stringe dönüştürülür

                # tahmin karakteri alanı fotoğrafta yeşil ile işaretlenir
                cv2.rectangle(image, (x, y), (x + w - 1, y + h - 1), (0, 0, 255),1)
                # Fotoğrafa tahmin etiketi kırmızı renk ile yazılır.
                cv2.putText(image, tahmin, (x, y + 5), cv2.FONT_HERSHEY_PLAIN, 2, (36, 255, 12),2)  # B:36 G:255 R:12 yazı renk kodu. etiket fotoğrafa eklendi

                # tahmin edilen karakter satırı belirsiz olarak listeye kaydediliyor
                karakter.append(tahmin)
                # karakterin konum bilgileri de kaydediliyor
                karakter_konum_x.append(x)
                karakter_konum_y.append(y)
                karakter_konum_w.append(w)
                karakter_konum_h.append(h)

def satir_ve_bosluk_bul(SiraliKarakterler): # Satırlar ve satır içindeki karakterlerin boşlukları tahmin stringine eklenecek.
    # tahmin_karakter_adeti: karakter dizisinin boyutu. Boşluk bulmada ve karakteri satır içindeki konumuna yerleştirmede kulanılır.
    tahmin_karakter_adeti = len(karakter)

    satir_konum_boyut = int(len(sirali_satir_konturlari)) # tespit edilen satır sayısı

    # yukarıdan aşağı sırasıyla satır bilgileri okunur. Satır içindeki karakterler arası boşluk bulunur.
    for i,satir_kontur in enumerate(sirali_satir_konturlari):
        # satırın konumları alınıyor
        x, y, w, h = cv2.boundingRect(satir_kontur)
        if i<(satir_konum_boyut-1): # son satır hariç her satır için bir sonraki satırla olan konum uzaklık kontrolü yapılır.
            x2, y2, w2, h2 = cv2.boundingRect(sirali_satir_konturlari[i+1]) # sonraki satır konumları
            if w > 15 and h > 15:  # satır küçük boyutlarda olamaz
                cv2.rectangle(image, (x, y), (x + w - 1, y + h - 1), (0, 255, 0),1)  # satır alanını yeşil dikdörtgenle çizecek
                satir_sonu_konum  = y2  # sonraki satır sonunun y başlangıç konumunu tutar
                satir_sonu_konum2 = h2  # sonraki satır sonunun yüksekliğini tutar
                if abs(y - satir_sonu_konum) > int(satir_sonu_konum2 / 2):
                    SiraliKarakterler = SiraliKarakterler+"\n" # Satır sonu stringe yazılıyor
        else:
            SiraliKarakterler = SiraliKarakterler+"\n"  # Son satır sonu stringe yazılıyor
        sonraki_karakter = 0

        for indis in range(tahmin_karakter_adeti): # ocr foto. içinde tahmin edilen karakter sayısı kadar kontrol yapılacak.
            merkez_X = int(karakter_konum_x[indis] + karakter_konum_w[indis] / 2)  # Satır içindeki karakterin merkez noktası hesaplanıyor
            merkez_Y = int(karakter_konum_y[indis] + karakter_konum_h[indis] / 2)  # Satır içindeki karakterin merkez noktası hesaplanıyor

            # Satır içindeki karakterin merkez noktası, satır kordinatları içindeyse stringe karakter kaydediliyor.
            if x <= merkez_X <= (x + w) and y <= merkez_Y <= (y + h):
                # Tahmin edilen satır içinde olduğundan karakter stringe eklendi
                SiraliKarakterler = SiraliKarakterler + karakter[indis]

                gecici = indis
                onceki_karakter = sonraki_karakter
                sonraki_karakter = gecici

                # bosluk: iki karakter arasındaki bosluk piksel olarak hesaplanıyor
                bosluk = abs((karakter_konum_x[onceki_karakter] + karakter_konum_w[onceki_karakter]) - (karakter_konum_x[sonraki_karakter]))

                # karakterler arasında ortalama bir karakterlik boşluk varsa boşluk eklenecek
                if bosluk > ((karakter_konum_w[onceki_karakter]+karakter_konum_w[sonraki_karakter])/2):
                    SiraliKarakterler = SiraliKarakterler+" "  # Boşluk stringe eklendi
        i=i+1
    return SiraliKarakterler

"""
    PROGRAM BAŞLANGIÇ KISMI
"""
if fotograf_kontrol() and karakter_belge_kontrol():  # Fotoğraf ve çıktı belgesi varsa karakter tanımlama başlıyor.

    print("Karakter tanımlama başlıyor...")

    image = fotograf_oku()  # Ocr uygulanacak fotoğraf okundu ve değişkene aktarıldı

    kirpilabilir, karakter_dilated, satir_dilated = fotograf_onislem()  # Fotoğraf ön işleme alınıyor

    sirali_karakter_konturlari, sirali_satir_konturlari = kontur_bul()  # Karakter tahmin alanları ve satır alanları kontur tespitiyle bulunuyor

    kiyas_boyut = kiyas_fotolari_yukle()  # Tahmin için kıyaslanacak fotoğraflar okunuyor.

    karakter_tahmin()  # Fotoğraftaki karakterlerin eğitimdeki karakterlerle kıyaslandığı fonksiyon

    SiraliKarakterler=satir_ve_bosluk_bul(SiraliKarakterler)  # Satırları ve karakterler arasındaki boşlukları bulan fonksiyon

    fotograf_goster(image, "Fotograf")  # ocr yapılan fotoğraf
    karakter_yaz(SiraliKarakterler) # Tahmin edilen karakter txt ye yazılıyor.
    os.startfile(r'output.txt')  # Ocr sonucu Notepad ile açılıyor

    cv2.waitKey(0)  # Pencerelerin kapatılmak için tuşa basılmasını bekleniyor
    exit(1)

else:  # Fotoğraf bulunamışsa uygulama sonlandırılır.
    exit(1)