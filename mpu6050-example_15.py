#!/usr/bin/env python

from mpu6050_mod import mpu6050
from stepper_motor_4 import Stepper
import time
import math
import pigpio
import serial
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader

ser = serial.Serial(
	port='/dev/ttyAMA0', 
	baudrate = 115200, 
	parity=serial.PARITY_NONE, 
	stopbits=serial.STOPBITS_ONE, 
	bytesize=serial.EIGHTBITS,
	timeout= 0 )
	
counter=0

sensor = mpu6050(0x68)

sensor.set_accel_range(sensor.ACCEL_RANGE_4G)    	# ACCEL_RANGE_4G = 0x08
sensor.set_gyro_range(sensor.GYRO_RANGE_250DEG)		# GYRO_RANGE_250DEG = 0x00

recieve = sensor.write_i2c_word(0x1A,0x03)
print("receive: {:}".format(recieve))

pi = pigpio.pi()

# defines as output
pi.set_mode(16, pigpio.OUTPUT)
pi.set_mode(19, pigpio.OUTPUT)
pi.set_mode(23, pigpio.OUTPUT)
pi.set_mode(24, pigpio.OUTPUT)
# enable pins
pi.write(24, 0)
pi.write(19, 0)
# direction
pi.write(16, 0)
pi.write(23, 1)
# pwm
pi.hardware_PWM(18, 0, 100000)
pi.hardware_PWM(13, 0, 100000)

aux = 0

cal_x= 4.05751068702
cal_y= 0.167098473282
cal_z= 0.265226717557

#-0.15700000
cal_z_a =  -0.14100000

a_x, a_y, a_z, g_x, g_y, g_z, angle_x, angle_y, angle_z = (0, 0, 0, 0, 0, 0, 0, 0, 0)
kP, kI, kD, set_gyro_angles, last_g_x, last_g_y, last_g_z = (0, 0, 0, 0, 0, 0, 0)
start_time = 0
self_balance_pid_setpoint = 0
last_error = 0
pid_i_mem = 0
period = 0
speed = 0
speed2 = 0
start = 0
angle_change = 0

file1 = open('/home/pi/Desktop/code/TC/sbr/dataset_1/dataset2.csv', 'a+')
file2 = open('/home/pi/Desktop/code/TC/sbr/dataset_2/dataset2.csv', 'a+')
file3 = open('/home/pi/Desktop/code/TC/sbr/dataset_3/dataset2.csv', 'a+')

printVariable1 = ''
printVariable2 = ''
printVariable3 = ''

rna1 = NetworkReader.readFrom('/home/pi/Desktop/rna1_1_200.xml')

def busy_wait(dt):
	current_time = time.clock()
	while (time.clock() < current_time+dt):
		# print anything here
		pass

#prepara pra iniciar com bons valores
for i in xrange(10):
	gyro_data = sensor.get_gyro_data()
	a_x, a_y, a_z = sensor.get_accel_data(True)
	
try:
	while True:	
		
		x=ser.read()
		
		if(x == "\x01"):
			aux = 1
	
		elif(x == "\x09"):
			aux = 2
		
		if(aux==1):
			print "um"
	
		elif(aux==2):
			print "zero"
			
		else:
			#print "null"
			pass
			
		start_time = time.clock()
		
		a_x, a_y, a_z = sensor.get_accel_data(True)
		a_z -= cal_z_a
		
		gyro_data = sensor.get_gyro_data()
		
		g_x = ((gyro_data['x'])-cal_x)
		g_y = ((gyro_data['y'])-cal_y)
		g_z = ((gyro_data['z'])-cal_z)
		
		angle_x += (g_x)*period*3.5
		angle_y += (g_y)*period*3.5
		angle_z += (g_z)*period*3.5
		
		last_g_x = g_x
		last_g_y = g_y
		last_g_z = g_z
		
		raw_y = angle_y
		
		if(a_z > 0.99):
			a_z = 0.99
		elif(a_z < -0.99): 
			a_z = -0.99 
			  
		angle_x_a = -(math.asin(float(a_z))*57.3)
		
		if(start == 0):
			angle_y = angle_x_a
			start = 1
			print("here")
		
		else:
			angle_y = angle_y*0.995 + angle_x_a*0.005

			if(angle_y < 0):
				angle_change = -angle_y
			
			else:
				angle_change = angle_y
								
		kP = 90
		kI = 10
		kD = 200
		
		error = (math.tan(angle_change/57.3))*100
				
		pid_i_mem += kI*error
		if(pid_i_mem > 1500):pid_i_mem = 1500
		if(pid_i_mem < -1500):pid_i_mem = -1500
					
		#if(error >1):
		#	speed += error*70
		
		#elif(error < -1):
		#	speed -= error*70
		
		#if(error > 2 or error < -2):
		#	error += speed*0.002
							
		
		#speed = error*kP+(error-last_error)*kD+pid_i_mem
		speed = rna1.activate([last_error, error])

		speed_real = (speed*400.0)-200.0

                #print speed
		
		#printVariable2 = "{:1.8f}, {:1.8f}, {:1.8f}".format(error, last_error, speed2/1000.0)	
		
		last_error = error
				
		if(speed_real > 200): speed_real=200
		elif(speed_real < -200): speed_read=-200
			
		#if(speed < 30 and speed > -30):
			#print("here")
			#speed=0
			#pid_i_mem = 0
			#angle_y = angle_x_a
				
		if(angle_y > 30 or angle_y < -30):
			speed_real = 0
			pid_i_mem = 0
				
		if(angle_y >= 0):
			#speed2 = speed-20
			pi.hardware_PWM(18, (speed_real), 250000)
			pi.hardware_PWM(13, (speed_real), 250000)
			pi.write(16, 1)
			pi.write(23, 0)
			
		elif(angle_y < 0):
			#speed2 = speed+20
			#speed_real -= speed_real
			pi.hardware_PWM(18, (speed_real), 250000)
			pi.hardware_PWM(13, (speed_real), 250000)
			pi.write(16, 0)
			pi.write(23, 1)
		
		else:
			speed2 = -speed
			pi.hardware_PWM(18, 0, 250000)
			pi.hardware_PWM(13, 0, 250000)
			pi.write(16, 0)
			pi.write(23, 1)	
			
		#printVariable1 = "{:1.8f}, {:1.8f}, {:1.8f}".format(raw_y, angle_x_a, speed2/1000.0)
			
		#printVariable3 = "{:1.8f}, {:1.8f}".format(error, speed2/1000.0)	
			
		if(aux == 1):
			
			file1.writelines(printVariable1+'\n')
		
			file2.writelines(printVariable2+'\n')
		
			file3.writelines(printVariable3+'\n')
									
		#print("x:{:7.3f}, y:{:7.3f}, z:{:7.3f}, t:{:7.3f}, x:{:7.3f}, y:{:7.3f}, z:{:7.3f}".format(a_x, a_y, a_z, temp, g_x, g_y, g_z))
		print("angle_x:{:6.2f}, angle_x_a:{:6.2f}, speed: {:}, motores: {:}".format(angle_y, angle_x_a, speed, speed_real))
				
		finish_time = time.clock()
		
		period = (time.clock()-start_time)
		#print("{:f}".format(period))			
		busy_wait(0.004-period)
		period = (time.clock()-start_time)
		#print("{:f}".format(period))
		
		
		
except KeyboardInterrupt:
	#print("fim")
	pi.hardware_PWM(18, 0, 250000)
	pi.hardware_PWM(13, 0, 250000)
	pi.write(24, 1)
	pi.write(19, 1)
	pi.stop()
	
    
