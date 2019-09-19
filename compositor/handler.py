import json
import boto3
import botocore
import secrets
from pydub import AudioSegment
import os
import glob

def extract(event, context):
    sound = AudioSegment.from_file(event["config"]["inFolder"] + event["steps"][0]["files"][0])
    test = sound[:event["config"]["barlength"]] * 4
    test.export("test.wav", format="wav")     	
    	

def upload(event, context):
    s3 = boto3.client('s3')
    bucket = event["bucket"]	
    for file in event["files"]:
        s3.upload_file(event["inFolder"] + file, bucket, file)	
		
    return {
        'statusCode': 200,
        'body': json.dumps('Requested files uploaded')
    }
	
def concat(event, context):	
    config = event["config"]
    path = config["outFolder"]
    files = glob.glob(path + "*")
    stream = AudioSegment.empty()
    for file in files:
        try:
            print("Adding ", file)		
            sound = AudioSegment.from_file(file)	
            stream += sound
			
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print(file, " does not exist in the bucket ", bucket)
            else:
               raise

    print("Saving the final stream as ", config["outStream"])			   
    stream.export(config["outStream"], format="wav")     	
	
    return {
        'statusCode': 200,
        'stream,': config["outStream"]
    }

def empty(path):
    files = glob.glob(path + "*")
    for f in files:
        os.remove(f)

def variate(event, context):
    empty(event["config"]["outFolder"])	
    compose(event, {})
     		
    return {
        'statusCode': 200,
        'body': json.dumps('Variation components ready')
    }		
	
def compose(event, context):
    config = event["config"]
    s3 = boto3.resource('s3') 
    bucket = config["bucket"]
    i = 0
	
    mixed = AudioSegment.empty()
    for step in event["steps"]:
        files = step["files"]				
        playlist = AudioSegment.from_file(config["inFolder"]+event["steps"][0]["files"][0])	# get rid of this
        if "repeat" in step:
            playlist *= step["repeat"]
		
        for file in files:	
            try:
                sound = AudioSegment.from_file(config["inFolder"]+file)	
                print("$$$$$$$$$$$$$ ",  sound.frame_rate)
                if "repeat" in step:
                    sound *= step["repeat"]
                playlist = playlist.overlay(sound)
			
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print(file, " does not exist in the bucket ", bucket)
                else:
                   raise

        index = secrets.randbits(10)
        print("Saving mixed file to ", config["outFolder"] + config["outFile"] + str(i))
		
        if "reverse" in step:		
            playlist = playlist.reverse()
			
        playlist.export(config["outFolder"] + config["outFile"] + str(i) + ".wav", format="wav")     
        mixed += playlist
        i += 1
    mixed.export(config["outStream"], format="wav")     		
    return {
        'statusCode': 200,
        'body': json.dumps('Requested files mixed')
    }