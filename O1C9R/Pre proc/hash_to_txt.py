import glob

import PIL
import imagehash
import os


kiyas_boyut=0
hashSet=[]
TahminEtiket=[]
def kiyas_fotolari_yukle(kiyas_boyut):
    for img in glob.glob("Karakterler/*.png"):  # klasör içindeki kontrol fotoğrafları listeye aktarılır.
        img2 = PIL.Image.open(img)

        fileNameExtension = os.path.basename(img)
        filename, file_extension = os.path.splitext(fileNameExtension)
        filename = filename.split()[0]  # ilk karakter tahmin değeri olacak

        TahminEtiket.append(filename)  # tahmin listesine fotoğraf etiketleri ekleniyor
        hashSet.append(imagehash.average_hash(img2, 64))  # etiketli kıyas fotoğrafının hash değeri hashSet e atanır
        kiyas_boyut+=1

    # kıyasta kullanılacak fotoğrafların dizi boyutu
    return kiyas_boyut


kiyas_boyut=kiyas_fotolari_yukle(kiyas_boyut)

dosya = open("hash.txt","w",encoding="utf-8")
for i in range(kiyas_boyut):
    dosya.write(TahminEtiket[i]+":"+str(hashSet[i])+"\n")

dosya.close()
loadExamps = open('hash.txt','r').read()
loadExamps = loadExamps.split('\n')


for eachExample in loadExamps:
    try:
        splitEx = eachExample.split(':')
        etiket = splitEx[0]
        hash   = splitEx[1]
        hashSet.append(hash)
        TahminEtiket.append(etiket)

    except Exception as e:
        print("Listenin sonu")
