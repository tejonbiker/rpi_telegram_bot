import telepot
import sys
import time
import thread
import os
import urllib2
from fractions import Fraction
from io import BytesIO
from picamera import PiCamera
import threading

'''
Jose Federico Ramos Ortega 

This code is the demonstration of the API of telegram bot via telepot library
This code is specially crafted for the Tepache Hacklab Dev Night 10, Leon Gto, 27 May

python rpi_telegram_bot.py BotToken ChatID

For more go to Github:
https://github.com/tejonbiker/rpi_telegram_bot
'''

#The insteresting effects are:
#photo_effects_list=["emboss","gpen","pastel","sketch","cartoon"]
photo_effects_list=['cartoon','negative', 'sketch', 'denoise', 'emboss', 'oilpaint', 'hatch', 'gpen', 'pastel', 'watercolor', 'film', 'blur', 'saturation']
restricted_id_chat=0

def send_messages_lowlight(chat_id,bot):
	time.sleep(18)
	bot.sendMessage(chat_id,"Iniciando captura")
	time.sleep(10)
	bot.sendMessage(chat_id,"Fin de Captura")
	return	

#This loop handles the receiving of the messages of the bot
def handle(msg):
	global my_stream
	global camera

	#Extract some basic info of the message
	content_type, chat_type, chat_id=telepot.glance(msg)

	print "chatid: " + str(chat_id)

	#The chat is the authorized?
	if(chat_id!=restricted_id_chat):
		return

	#The first word will be a command
	command=(msg['text']).split()
			
	#want to take a photo?
	if(command[0]=="photo"):

		print "Camara Res: "
		print camera.resolution
		bot.sendMessage(chat_id,"Tomando foto")

		photo_effect="none";

		#want to add a effect? (second word of the message)
		if(len(command)>1):
			if(command[1] in photo_effects_list):
				photo_effect=command[1]
				bot.sendMessage(chat_id,photo_effect + " ")
			else:
				bot.sendMessage(chat_id,"normal ")

		else:
			bot.sendMessage(chat_id,"normal ")

		#Send message: wait
		bot.sendMessage(chat_id,"espere...")

		#Rewind stream (for start from the beginning)
		my_stream.seek(0)
		current_effect=camera.image_effect 	#Save the current effect
		camera.image_effect=photo_effect   	#Set the desired effect
		time.sleep(4)
		#camera.capture(my_stream,'jpeg')	#Capture the image
		camera.capture('file_direct.jpeg')
		camera.image_effect=current_effect	#Restore the before effect
		my_stream.seek(0)			#Rewind for a correct lecture of the stream
		#bot.sendPhoto(chat_id,my_stream)	#Send the image stream bytes to the chat
		#bot.sendPhoto(chat_id,open("file_direct.jpeg","rb"))
		bot.sendDocument(chat_id,open("file_direct.jpeg","rb"))

	#want a video?
	elif(command[0]=="video"):
		current_resolution=camera.resolution            #Save the before resolution and framerate
		camera.resolution=(1900,1080)
		bot.sendMessage(chat_id,"Tomando video, espere...")

		photo_effect="none";

		#This part of effects is experimental, no tested completed
                if(len(command)>1):
                        if(command[1] in photo_effects_list):
                                photo_effect=command[1]
                                bot.sendMessage(chat_id,photo_effect + " ")
                        else:
                                bot.sendMessage(chat_id,"normal ")

                else:
                        bot.sendMessage(chat_id,"normal ")
	

		os.system("rm my_video.h264 my_video.mp4") 	#Let's remove the files (if we have some previous capture)
		camera.image_effect=photo_effect		#set the effect (experimental)
		camera.start_recording('my_video.h264')		#Start to record the video
		camera.wait_recording(10)			#Wait 10 seconds
		camera.stop_recording()				#Stop to record
		bot.sendMessage(chat_id,"Convirtiendo...")	#Send: "converting" to the chat
		os.system("MP4Box -add my_video.h264 my_video.mp4") 	#Via os commands convert to mp4
		bot.sendMessage(chat_id,"adjuntando...")		#Send message: "attaching"
		bot.sendVideo(chat_id,open("my_video.mp4","rb"));	#Send video file (for some reason converted to GIF)

		camera.resolution=current_resolution;

	#want a slow motion video effect?
	elif(command[0]=="slow"):
		bot.sendMessage(chat_id,"Tomando video, espere...")

                os.system("rm my_video.h264 my_video.mp4") 	#Removing files

		current_resolution=camera.resolution		#Save the before resolution and framerate
		current_fps=camera.framerate

		camera.resolution=(640, 480)
		camera.framerate=90				#Set the correct resolution and framerate to enable 90 fps mode
		
                camera.start_recording('my_video.h264')		#Start video capture
                camera.wait_recording(5)			#Record 5 seconds
                camera.stop_recording()				#Stop Recording

		camera.resolution=current_resolution		#Restore the before resolution and fps
                camera.framerate=current_fps

                bot.sendMessage(chat_id,"Convirtiendo...")		#Send message: Converting
                os.system("MP4Box -add my_video.h264 my_video.mp4")	#Convert to mp4 via os commands
                bot.sendMessage(chat_id,"adjuntando...")		#Send message: attaching
                bot.sendVideo(chat_id,open("my_video.mp4","rb"));	#Attach video file

	elif(command[0]=="lowlight"):
		bot.sendMessage(chat_id,"Comando recibido")
		before_ss=camera.shutter_speed;
		before_fps=camera.framerate;
		before_exposure_mode=camera.exposure_mode
		before_iso=camera.iso

		#camera.framerate=Fraction(1,1);
		camera.framerate=Fraction(1, 10);

		camera.exposure_mode = 'off'
    		camera.iso = 100

		bot.sendMessage(chat_id,"Camara ajustada, esperando estabilizacion (20 seg)")

		if(len(command)>1):
			camera.shutter_speed=int(command[1]);
		else:
			camera.shutter_speed=10000000

		bot.sendMessage(chat_id,"obturador a :" + str(camera.shutter_speed)+ " usec")

		time.sleep(20)

		print "Camera mode changed\n"

		bot.sendMessage(chat_id,"capturando...")
		my_stream.seek(0)

		t=threading.Thread(target=send_messages_lowlight,args=(chat_id,bot,))
		t.start()
                camera.capture(my_stream,'jpeg')        #Capture the image

                my_stream.seek(0)                       #Rewind for a correct lecture of the stream
		bot.sendMessage(chat_id,"adjuntando...")
                #bot.sendPhoto(chat_id,my_stream)        #Send the image stream bytes to the chat
		bot.sendDocument(chat_id,my_stream)

		my_stream.seek(0)
		photo_file=open("test_save_file.jpg", "wb")
		#photo_file.write(my_stream.read());
		photo_file.write("12345");
		photo_file.close()

		camera.shutter_speed=before_ss;
		camera.framerate=before_fps;
		camera.exposure_mode=before_exposure_mode
                camera.iso=before_iso

	
	#want help? display the commands and some explanations
	elif(command[0]=="ayuda"):
		tabulator="\n   -"
		photo_options=""
		for effect in photo_effects_list:
			photo_options=photo_options + tabulator + effect

		bot.sendMessage(chat_id,"Comandos disponibles:\n >photo: Captura una fotografia,efectos:"+photo_options+"\n >video: Captura un video de 10 seg\n >slow: Captura un video a 90 fps de 5 seg\n >location: envia una muestra de punto gps\n >sound: envia una muestra de audio\n >log: adjunta el archivo /var/log/messages")
		
	#Want to shutdown?
	elif(command[0]=="shutdown"):
		print "shutting down"
		bot.sendMessage(chat_id,"apagando")
		os.system("sudo poweroff")

	#Show how to attach a document
	elif(command[0]=="log"):
		bot.sendDocument(chat_id,open("/var/log/messages","rb"))	
	#show how to attach a sound
	elif(command[0]=="sound"):
		bot.sendAudio(chat_id,open("/usr/share/sounds/alsa/Front_Center.wav","rb"));
	#show how to attach a GPS location
	elif(command[0]=="location"):
		bot.sendLocation(chat_id,21.119314, -101.674775);
	#else, show a little help message
	else:
		bot.sendMessage(chat_id,"comando invalido,para informacion en comandos escriba: ayuda ");
	
		

TOKEN=sys.argv[1] 			#get bot token
restricted_id_chat=int(sys.argv[2]) 	#Get chat restriction
bot=telepot.Bot(TOKEN)			#Start bot
bot.message_loop(handle)			#setup the callback function
print("Escuchando")

my_stream=BytesIO()			#Start the variable to handle the byte stream image
camera = PiCamera(sensor_mode=0)	#Instance of the camera
#camera.resolution = (1024, 768)	#If you want setup resolution
camera.resolution =(3280,2464)          #Full HD for photos and videos
print camera.resolution

camera.start_preview()			#Start a preview
					#Camera Warn-Up time
time.sleep(2)

while 1:				#Polling the main thread
	time.sleep(1)

