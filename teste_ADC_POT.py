# F. E. T. LIBERATO SALZANO VIEIRA DA CUNHA 
# TC ELETRÔNICA
# SISTEMA DE CONTROLE POR ALGORITMOS DE INTELIGÊNCIA ARTIFICIAL 
# AUTORES: DIEGO MACHADO
#......... GABRIEL GOSMANN

import time
import pigpio
import os
import math
import cv2

#defines
address_1 = 0x68	#address of MCP3428_1

change = 0
rbon = 0
il = 0

pi = pigpio.pi()

pot = pi.spi_open(0, 100000, 0) 
pi.i2c_open(1, address_1)

stop = time.time() + 600


file = open('/home/pi/Desktop/code/TC/trains/sistema_analogo_1/dataset/dataset.csv', 'a+') 
	
def pot(res):
    
    pack_send = int((res/10000.0)*1023.0)

    a = pack_send>>2
    b = pack_send&3
   
   # print (pack_send)
  #  print (a)
   # print (b)

    state = pi.spi_write(0, [0, a, b])
    time.sleep(0.1)
	
def analog_digital(device_n, add, w_byte):
        #value = 0
        
	#for i in range(10):
            
        #time.sleep(0.000001)
        pi.i2c_write_byte(device_n, w_byte)  				# escreve o write_byte no MCP3428   					 
        (count, data) = pi.i2c_read_device(device_n, 2)		# le 2 bytes do MCP3428
	
        byte_0 = data[0]
        byte_1 = data[1]
		
        byte_0 = byte_0<<8
        digital = byte_0|byte_1
        value=digital

       # value/= 10
	
	return value										# retorna o valor digital recebido do ADC
def config_register(channel, resolution, gain):			# formato binario conforme o datasheet
	
	config_byte = (0b1<<7)|(channel<<5)|(0b1<<4)|(resolution<<2)|(gain)
	return config_byte

def bin_to_volts(digitalWord, gain):					# formato binario conforme o datasheet
	readWord = 2.048*(digitalWord/32767.0)				# voltRef * (variable/ resolution) 
	return readWord

		
time.sleep(1)

rbon = 5000.0

pot(rbon)

while 1:
	
	bt = pi.read(26)
	if bt:
		print "\nMUDANCA DE PARAMETRO: "
		change = float(input())
    
	config_byte_il = config_register(0b01, 0b10, 0b00)
	#time.sleep(0.1)
	
	bin_word_il = analog_digital(0, address_1, config_byte_il)
	il_v = bin_to_volts(bin_word_il, 0b00)
	
	time.sleep(0.1)
	
	config_byte_vbe = config_register(0b10, 0b10, 0b00)
	#time.sleep(0.1)
	
	bin_word_vbe = analog_digital(0, address_1, config_byte_vbe)
	vbe = bin_to_volts(bin_word_vbe, 0b00)
	time.sleep(0.1)
	
	config_byte_vcc = config_register(0b11, 0b10, 0b00)
	# time.sleep(0.1)
	
	bin_word_vcc = analog_digital(0, address_1, config_byte_vcc)
	vcc = bin_to_volts(bin_word_vcc, 0b00)
	
	time.sleep(0.1)
	
	config_byte_vce = config_register(0b00, 0b10, 0b00)
	# time.sleep(0.1)
	
	bin_word_vce = analog_digital(0, address_1, config_byte_vce)
	vce = bin_to_volts(bin_word_vce, 0b00)
	
	time.sleep(0.1)

	il_v *= 122.179
	vcc *= 12.53
	vce *= 16.8681


        if(il_v >= 120.0):
		rbon -= 90.5
		
	if(il_v <= 60.0):
		rbon += 90.5
	
	if(il_v >= 101.0):
		rbon -= 20.5
		
	if(il_v <= 98.0):
		rbon += 20.5
	
	if(il_v <= 101.0):
		rbon += 5.5
	
	if(il_v >= 100.0):
		rbon -= 5.5
	
	if(rbon > 10000.0):
		rbon = 10000.0
		
	if(rbon < 0.0):
		rbon = 0.0
	
	pot(rbon)
	
	if(il_v>=100.0 and il_v<=100.9):
                        print "MUDAR PARAMETRO"
			printVariable2 = "{:1.3f}, {:1.3f}, {:1.3f}, {:1.3f}".format(vbe, vcc, vce, rbon)
			file.writelines(printVariable2+'\n')
	
	printVariable = "IL: {:1.3f}mA, VBE: {:1.3f}V, VCC: {:1.3f}V, VCE: {:1.3f}V, RB: {:1}".format(il_v, vbe, vcc, vce, rbon)		
	print (printVariable)
	

    
