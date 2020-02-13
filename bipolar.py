import sys, os
import numpy

def copyArray(src,dst,start,end,prefix_src,prefix_dst):
    for i in range(start,end):
        #print("start:",start," end:",end," pSrc:",prefix_src," pDst:",prefix_dst," lenSrc:",len(src)," lenDst:",len(dst))
        #print("dst:",(prefix_dst+i)," src:",(prefix_src+i))
        dst[prefix_dst+i] = src[prefix_src+i]

def jsHideIntoJpegMini(imgSrc,scriptToHide,imgDst):

    with open(imgSrc,'rb') as f1: bytesImgSrc = f1.read(10000000);
    # Si /* o */ fichero no valido
    # FF D8 FF E0 00 10 bla bla --> posicion 4 y 5 tam de cabecera
    tamCabeceraActual = bytesImgSrc[4]*256+bytesImgSrc[5]
    leidos = len(bytesImgSrc)

    jpgFinal = bytearray(leidos-tamCabeceraActual+2362+4) #2362=0x093A - Todo tal cual le quito la cabecera, le pongo el tamao nuevo de cabecera y los 4 bytes de cierre 2A 2F 2F 2F FF D9

    # Copiar bloques de bytes
    copyArray(bytesImgSrc,jpgFinal,0,4,0,0)  #copio los primeros 4 bytes --> tipicamente FFD8 FFE0, la cabecera
    jpgFinal[4] = 0x09; jpgFinal[5] = 0x3A; #copio nuevo tamano
    copyArray(bytesImgSrc,jpgFinal,6,10,0,0) #copio los primeros 4 bytes de la cabecera sin contar el tam. Tipicametne JFIF
    jpgFinal[10] = 0x2F; jpgFinal[11] = 0x2A;
    copyArray(bytesImgSrc,jpgFinal,0,tamCabeceraActual-6,10,12) #copio lo que queda de tamCabeceraActual
    with open(scriptToHide,'rb') as f3: linesScriptToHide = f3.read(10000000); # payload js
    for i in range(0,2362-tamCabeceraActual-2-len(linesScriptToHide)): jpgFinal[(12+tamCabeceraActual-6)+i] = 0x00;
    payloadLen = len(linesScriptToHide)
    copyArray(linesScriptToHide,jpgFinal,0,len(linesScriptToHide),0,2362-payloadLen+4) #le meto el payload
    copyArray(bytesImgSrc,jpgFinal,0,(leidos-(tamCabeceraActual+4))-2,tamCabeceraActual+4,2362+4) # No copio FF D9 #copio lo que queda de tamCabeceraActual |      # COPIO EL RESTO DEL FICHERO MENOS LOS DOS ULTIMOS BYTES

    jpgFinal[len(jpgFinal)-7] = 0x2A;   jpgFinal[len(jpgFinal)-6] = 0x2F;    jpgFinal[len(jpgFinal)-5] = 0x2F; 	# A final de fichero copio el cierre
    jpgFinal[len(jpgFinal)-4] = 0x2F;   jpgFinal[len(jpgFinal)-3] = 0xFF;    jpgFinal[len(jpgFinal)-2] = 0xD9;

    with open(imgDst,'wb') as f2: f2.write(jpgFinal)

def jsHideIntoJpegBig(imgSrc,scriptToHide,imgDst):

    with open(imgSrc,'rb') as f1: bytesImgSrc = f1.read(10000000);
    #Falta considerar /* */ el fichero no es valido para stego

    # FF D8 FF E0 00 10 bla bla --> posicion 4 y 5 tam de cabecera
    tamCabeceraActual = bytesImgSrc[4]*256+bytesImgSrc[5]
    leidos = len(bytesImgSrc)
    #2F 2A -> 12074 -2 = 12072
    tamCabeceraDestino = 12074-tamCabeceraActual

    # Anado los 00 que hacen falta a la cabecera para tamano 2F2A
	# El payload js necesita antes 4 bytes -> FF FE 00 1C (00 1C -> el tam del payload+2)
	# Machacar [4] y [5] con el tam nuevo de cabecera

    with open(scriptToHide,'rb') as f3: linesScriptToHide = f3.read(10000000); # payload js
    payloadLen = len(linesScriptToHide)

    jpgFinal = bytearray(leidos+tamCabeceraDestino+payloadLen+4+1+2)

    copyArray(bytesImgSrc,jpgFinal,0,4,0,0)  #copio los primeros 4 bytes --> tipicamente FFD8 FFE0, la cabecera
    jpgFinal[4] = 0x2F; jpgFinal[5] = 0x2A; #copio nuevo tamano

    for i in range(0,tamCabeceraDestino):
        jpgFinal[i+tamCabeceraActual+4] = 0x00;

    jpgFinal[tamCabeceraActual+4+tamCabeceraDestino] = 0xFF
    jpgFinal[tamCabeceraActual+4+tamCabeceraDestino+1] = 0xFE

	# Anadir el tamano del javascript con dos bytes por ejemplo 00 C1
    jpgFinal[tamCabeceraActual+4+tamCabeceraDestino+2] = 0x00; #CALCULARLO BIEN
    jpgFinal[tamCabeceraActual+4+tamCabeceraDestino+3]= payloadLen+2 #CALCULARLO BIEN

    copyArray(linesScriptToHide,jpgFinal,0,payloadLen,0,tamCabeceraActual+4+tamCabeceraDestino+4)

    copyArray(bytesImgSrc,jpgFinal,0,leidos-tamCabeceraActual-4+1,
    tamCabeceraActual+4-1,tamCabeceraActual+4+tamCabeceraDestino+4+payloadLen)

    jpgFinal[len(jpgFinal)-5] = 0x2A;
    jpgFinal[len(jpgFinal)-4] = 0x2F;
    jpgFinal[len(jpgFinal)-3] = 0xFF;
    jpgFinal[len(jpgFinal)-2] = 0xD9;

    with open(imgDst,'wb') as f2: f2.write(jpgFinal)

def shHideIntoJpeg(imgSrc,scriptToHide,imgDst):

    with open(imgSrc,'rb') as f1: bytesImgSrc = f1.read(10000000);
    with open(scriptToHide,'rb') as f3: linesScriptToHide = f3.read(10000000); # payload js
    payloadLen = len(linesScriptToHide)

    leidos = len(bytesImgSrc)
    #en el fichero no puede haber 0x27
    # Si no tiene 0x27 entonces al final del script pongo : ' y al final de fichero '
    # // FF D8 FF E0 00 10 bla bla --> posicion 4 y 5 tam de cabecera
    tamCabeceraActual = bytesImgSrc[4]*256+bytesImgSrc[5]

    jpgFinal = bytearray(leidos+tamCabeceraActual+291)
    # 291=0x0123 - Todo tal cual le quito la cabecera, le pongo el tamano nuevo de cabecera
    copyArray(bytesImgSrc,jpgFinal,0,4,0,0)  #copio los primeros 4 bytes --> tipicamente FFD8 FFE0, la cabecera
    jpgFinal[4] = 0x01; jpgFinal[5] = 0x23; #copio nuevo tamano

    copyArray(bytesImgSrc,jpgFinal,6,10,0,0)

    for i in range(0,tamCabeceraActual-6):
        if bytesImgSrc[10+i] == 0x00:
        #if ByteToHex(bytesImgSrc[10+i]) == "00":
            jpgFinal[10+i] = 0x01
        else:
            jpgFinal[10+i] = bytesImgSrc[10+i]

    for i in range(0,291-tamCabeceraActual):
        jpgFinal[(10+tamCabeceraActual-6)+i] = 0x01;  # es 0x01 pq el 0x00 da error en script bash

    jpgFinal[tamCabeceraActual+4] = 0x0D;
    jpgFinal[tamCabeceraActual+4+1] = 0x0A;

    copyArray(linesScriptToHide,jpgFinal,0,payloadLen,0,tamCabeceraActual+4+2)

    copyArray(bytesImgSrc,jpgFinal,0,leidos-tamCabeceraActual-4,tamCabeceraActual+4,291+4)


    with open(imgDst,'wb') as f2: f2.write(jpgFinal)

def name():

    print("")
    print("                               ___         ___                         ___           ___     ")
    print("    _____        ___          /  /\       /  /\                       /  /\         /  /\    ")
    print("   /  /::\      /  /\        /  /::\     /  /::\                     /  /::\       /  /::\   ")
    print("  /  /:/\:\    /  /:/       /  /:/\:\   /  /:/\:\    ___     ___    /  /:/\:\     /  /:/\:\  ")
    print(" /  /:/~/::\  /__/::\      /  /:/~/:/  /  /:/  \:\  /__/\   /  /\  /  /:/~/::\   /  /:/~/:/  ")
    print("/__/:/ /:/\:| \__\/\:\__  /__/:/ /:/  /__/:/ \__\:\ \  \:\ /  /:/ /__/:/ /:/\:\ /__/:/ /:/___")
    print("\  \:\/:/~/:/    \  \:\/\ \  \:\/:/   \  \:\ /  /:/  \  \:\  /:/  \  \:\/:/__\/ \  \:\/:::::/")
    print(" \  \::/ /:/      \__\::/  \  \::/     \  \:\  /:/    \  \:\/:/    \  \::/       \  \::/~~~~ ")
    print("  \  \:\/:/       /__/:/    \  \:\      \  \:\/:/      \  \::/      \  \:\        \  \:\     ")
    print("   \  \::/        \__\/      \  \:\      \  \::/        \__\/        \  \:\        \  \:\    ")
    print("    \__\/                     \__\/       \__\/                       \__\/         \__\/    ")
    print("")
    print(" -- --=[ bipolar 0.1 experimental (March 2020)]")
    print(" -- --=[ Author: Dr. Alfonso Munoz @mindcrypt]")
    print("")

def menu():
    name()

def main(paramIn):

    if len(sys.argv)<5:
        menu()
        print(" -- --=[ #bipolar <typeScript (JS/PHP/ShellScript/Powershell)> <input> <script> <output>]")
        print("")
        print(" -- --=[ >bipolar js|sh|php|pw in.jpg payload out.jpg]")
        print(" -- --=[ >bipolar js cat.jpg payload.js catPolyglot.jpg]")
    else:
        if sys.argv[1] == "js":
            print(" -- --=[ Creating JPEG-JS polyglot ]...")
            jsHideIntoJpegMini(sys.argv[2],sys.argv[3],sys.argv[4])
            #jsHideIntoJpegBig(sys.argv[2],sys.argv[3],sys.argv[4])
            print(" -- --=[ Done ]...")
        elif sys.argv[1] == "sh":
            print(" -- --=[ Creating JPEG-ShellScript polyglot ]...")
            shHideIntoJpeg(sys.argv[2],sys.argv[3],sys.argv[4])
            print(" -- --=[ Done ]...")
        elif sys.argv[1] == 'php':
            print(" -- --=[ Creating JPEG-PHP polyglot ]...")
            jsHideIntoJpegMini(sys.argv[2],sys.argv[3],sys.argv[4])
            print(" -- --=[ Done ]...")
        elif sys.argv[1] == 'pw':
            print(" -- --=[ Creating JPEG-Powershell polyglot ]...")
            shHideIntoJpeg(sys.argv[2],sys.argv[3],sys.argv[4])
            print(" -- --=[ Done ]...")
        else:
            print(" -- --=[ #bipolar <typeScript> <input> <script> <output>]")
            print(" -- --=[ Payload format does not support ]...")
    print("")

main(sys.argv)
