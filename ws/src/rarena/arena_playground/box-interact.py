import time
import random
import numpy 
import paho.mqtt.client as mqtt
import signal
import sys

mqtt_broker="oz.andrew.cmu.edu"
scene_path="/topic/render/"
object_name="cube_x"

# Object starting point, global so click handler can modify it
x=1.0
y=1.0
z=1.0


def signal_handler(sig, frame):
	client.publish(scene_path+object_name,"",retain=True)  
        print("Removing objects before I quit...")
	time.sleep(1)	
        sys.exit(0)


#define callbacks
def on_click_input(client, userdata, msg):
    global x
    global y
    global z
    print("got click: %s \"%s\"" % (msg.topic, msg.payload))
    click_x,click_y,click_z,user = msg.payload.split(',')
    print( "Clicked by: " + user )
    obj_x=float(x)-float(click_x)
    obj_y=float(y)-float(click_y)
    obj_z=float(z)-float(click_z)
    if str(msg.topic).find("mousedown") != -1:
      print( "Obj relative click: " + str(obj_x) + "," + str(obj_y) + "," + str(obj_z) )
    x=click_x
    y=click_y
    z=click_z
    cube_str = "property: position; to: {} {} {}; dur: 100; easing: linear"
    # Publish an animation command to move the object
    client.publish(scene_path+object_name+"/animation",cube_str.format(x,y,z))
    print( "Update Box Location" )


client= mqtt.Client("client-001", clean_session=True, userdata=None ) 


print("connecting to broker ",mqtt_broker)
client.connect(mqtt_broker) 




############
# Setup box
# Delete the object from the scene to get a fresh start with a null message
client.publish(scene_path+object_name,"")  
color = "#%06x" % random.randint(0, 0xFFFFFF)
cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
# Publish a cube with x,y,z and color parameters
# retain=True makes it persistent
client.publish(scene_path+object_name,cube_str.format(x,y,z,color),retain=True)

# Enable click listener for object (allows it to be clickable)
client.publish(scene_path+object_name+"/click-listener","enable",retain=True)

client.subscribe(scene_path+object_name+"/mouseup")
client.subscribe(scene_path+object_name+"/mousedown")
client.message_callback_add(scene_path+object_name+"/mouseup", on_click_input)
client.message_callback_add(scene_path+object_name+"/mousedown", on_click_input)

client.loop_start() #start loop to process received mqtt messages
# add signal handler to remove objects on quit
signal.signal(signal.SIGINT, signal_handler)

# Main loop that runs every 5 seconds and changes the object color
while True:
    print("Main loop changing color" )
    color = "#%06x" % random.randint(0, 0xFFFFFF)
    cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
    # Draw cube at x,y,z location with a new color
    client.publish(scene_path+object_name,cube_str.format(x,y,z,color),retain=True)
    time.sleep(5.0)

client.disconnect() #disconnect
client.loop_stop() #stop loop
