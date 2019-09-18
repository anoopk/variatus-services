import json
import boto3
import botocore
import secrets
from pydub import AudioSegment

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
    stream = AudioSegment.from_file(event["inFolder"]+event["files"][0])	
	
    for file in event["files"]:
        try:
            sound = AudioSegment.from_file(event["inFolder"]+file)	
            stream = stream + sound
			
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print(file, " does not exist in the bucket ", bucket)
            else:
               raise

    print("Saving stream to ", event["outFolder"] + event["outFile"])			   
    stream.export(event["outFolder"] + event["outFile"], format="wav")     
	
    return {
        'statusCode': 200,
        'body': json.dumps('Requested files mixed')
    }

def compose(event, context):
    s3 = boto3.resource('s3') 
    event =  event["steps"][0]
    upload(event, context)	
    bucket = event["bucket"]
    playlist = AudioSegment.from_file(event["inFolder"]+event["files"][0])	
	
    for file in event["files"]:
        try:
            sound = AudioSegment.from_file(event["inFolder"]+file)	
            playlist = playlist.overlay(sound)
			
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print(file, " does not exist in the bucket ", bucket)
            else:
               raise

    index = secrets.randbits(10)
    print("Saving mixed file to ", event["outFolder"] + event["outFile"] + str(index))			   
    playlist.export(event["outFolder"] + event["outFile"] + str(index), format="wav")     
	
    return {
        'statusCode': 200,
        'body': json.dumps('Requested files mixed')
    }