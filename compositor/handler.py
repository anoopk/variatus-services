import json
import boto3
import botocore
import secrets
from pydub import AudioSegment
import os
import glob
   	
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
	
def randomizeIfAsked(val):
    if val < 0:
        print(val)
        val = secrets.randbelow(val * -1)
        print(val)		
    return val
		
def compose(event, context):
    config = event["config"]
    s3 = boto3.resource('s3') 
    bucket = config["bucket"]
    mixed = AudioSegment.empty()
	
    for step in event["steps"]:
        if "reuse" in step:
            step = event["steps"][step["reuse"]]
			
        files = step["files"]			
        playlist = AudioSegment.silent(step["bars"] * config["barlength"] * step["repeat"])
        for file in files:	
            try:
                sound = AudioSegment.from_file(config["inFolder"]+file["track"])	
                if "bars" in step:					
                    sound = sound[:event["config"]["barlength"] * randomizeIfAsked(step["bars"])]
                if "repeat" in step:
                    sound *=  randomizeIfAsked(step["repeat"])
                if "reverse" in file:		
                    sound =  sound.reverse()
                if "fadein-end"	in file:
                    sound.append(end, crossfade=1500)
					
                playlist = playlist.overlay(sound)
			
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print(file.track, " does not exist in the bucket ", bucket)
                else:
                   raise

        index = secrets.randbits(10)
        print("Saving mixed file to ", config["outFolder"] + config["outFile"] + str(index))			
        playlist.export(config["outFolder"] + config["outFile"] + str(index) + ".wav", format="wav")     		
        mixed += playlist
		
    mixed.export(config["outStream"], format="wav")     		
    return {
        'statusCode': 200,
        'body': json.dumps('Requested files mixed')
    }