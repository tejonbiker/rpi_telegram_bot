import telepot
import sys
import time
import thread
import os
import urllib2
from io import BytesIO
from picamera import PiCamera

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
		camera.capture(my_stream,'jpeg')	#Capture the image
		camera.image_effect=current_effect	#Restore the before effect
		my_stream.seek(0)			#Rewind for a correct lecture of the stream
		bot.sendPhoto(chat_id,my_stream)	#Send the image stream bytes to the chat

	#want a video?
	elif(command[0]=="video"):
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

	
	#want help? display the commands and some explanations
	elif(command[0]=="ayuda"):
		tabulator="\n   -"
		photo_options=""
		for effect in photo_effects_list:
			photo_options=photo_options + tabulator + effect

		bot.sendMessage(chat_id,"Comandos disponibles:\n >photo: Captura una fotografia,efectos:"+photo_options+"\n >video: Captura un video de 10 seg\n >slow: Captura un video a 90 fps de 5 seg\n >location: envia una muestra de punto gps\n >sound: envia una muestra de audio")
		
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
camera = PiCamera()			#Instance of the camera
#camera.resolution = (1024, 768)	#If you want setup resolution

camera.start_preview()			#Start a preview

					#Camera Warn-Up time
time.sleep(2)

while 1:				#Polling the main thread
	time.sleep(1)
