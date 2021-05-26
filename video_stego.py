'''
TY BTECH MINI PROJECT (2020-2021)

GROUP MEMBERS:
ARNAV ANAND
VIDYA LAD
JOEL ELDOE
'''

# Importing all the required modules
import cv2              # Module for video processing
import os               # Module for executing system commands
import subprocess       # Module for executing system commands
import glob             # Module to collect specific files recursively
from PIL import Image   # Module for image processing
import stepic           # Module for image steganography
import base64 as b64    # Module for base64 data processing

# ANSI codes for font colors
class colors:
    GREEN = '\033[92m'  #GREEN COLOR
    YELLOW = '\033[93m' #YELLOW COLOR
    RED = '\033[91m'    #RED COLOR
    RESET = '\033[0m'   #RESET COLOR

# Function that implements the rot13 cipher
def rot13(input_text):
    return input_text.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz","NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))

# Function that implements video steganography
def steg_video(video_name, audio):
    # Prompting user input for the secret message
    message = input(f"Enter the message you want to encode in the video:\n{colors.YELLOW}")
    print(f"{colors.RESET}")

    # Encoding the secret message into base64 format and encrypting it using rot13 cipher
    message = b64.b64encode(message.encode())
    print(f"Base64 encoded Message: {colors.YELLOW}{message}{colors.RESET}")
    message = rot13(message.decode())
    print(f"ROT13 Encrypted Message: {colors.YELLOW}{message}{colors.RESET}")

    # Creating a video file object from the selected video file
    video = cv2.VideoCapture(video_name)

    # Creating ./temp directory to store the frames and audio extracted
    no_of_frames = 1
    os.system('mkdir temp && mkdir ./temp/frames/')
    frames_folder = './temp/frames/'

    # Extracting audio from the video
    if(audio == 'y'):
        subprocess.call(["ffmpeg","-i",video_name,"-q:a","0","-map","a","./temp/audio.mp3","-y"],stdout=open(os.devnull,"w"),stderr=subprocess.STDOUT)

    # Dividing the video into frames
    while True:
        success, image1 = video.read()
        if not success:
            break
        cv2.imwrite(os.path.join(frames_folder, f"{no_of_frames}.png"),image1)
        no_of_frames += 1

    # Collecting all the images in the ./temp/frames/ directory into a list
    frames = glob.glob('./temp/frames/*.png')

    # Sorting the image file names according to the creation time
    frames.sort(key=os.path.getmtime)

    # Prompting user input for the frame no. in which the message has to be embedded
    key_frame_no = input(f"\nEnter the frame no.(between 1-{len(frames)}) where you want to embed the message: ")
    key_frame_no = int(key_frame_no)
    if(key_frame_no > len(frames)):
        print(f"\n{colors.RED}Frame no. {key_frame_no} doesn't exist! There are only {len(frames)} frames!{colors.RESET}\n")
        os.system('rm -rf ./temp/')
        exit()

    key_frame_name = frames[key_frame_no-1] # Getting the image file name at the specified position
    key_frame = Image.open(frames[key_frame_no-1]) # Creating an image file object of the selected image
    encoded_frame = stepic.encode(key_frame, message.encode()) # Creating a file with the embedded secret message

    os.remove(key_frame_name) # Deleting the already existing frame or image with the same name

    encoded_frame.save(key_frame_name) # Saving the new frame of image file with the same name

    # Combining all the images inside the ./temp/frames/ directory to create a new video
    frames_array = []
    for frame in frames:
        image2 = cv2.imread(frame)
        height, width, layers = image2.shape
        size = (width, height)
        frames_array.append(image2)

    temp_video_name = "./temp_" + video_name.split(".")[0] + ".avi"
    new_video = cv2.VideoWriter(temp_video_name, cv2.VideoWriter_fourcc(*'DIVX'), 30, size)

    for frame in range(no_of_frames-1):
        new_video.write(frames_array[frame])
    new_video.release()

    new_video_name = "./new_" + video_name.split(".")[0] + ".avi"

    print(f"\n{colors.GREEN}Video created!{colors.RESET}\n")

    # Prompting the user for extracting the secret message
    choice = input("Do you want to decode the message in the video? (y/n): ")
    if(choice == 'y'):
        # Prompting the user to enter the same frame no. where the message is embedded
        key_frame_no2 = input("Enter the key frame no.(where the image is hidden): ")
        key_frame_no2 = int(key_frame_no2)

        if(key_frame_no == key_frame_no2):
            # Extracting and decoding the secret message to its original form
            decoded_message = stepic.decode(encoded_frame)
            print(f"\nExtracted Message: {colors.YELLOW}{decoded_message}{colors.RESET}")

            decoded_message = rot13(decoded_message)
            print(f"ROT13 Decrypted Message: {colors.YELLOW}{decoded_message}{colors.RESET}")

            decoded_message = b64.b64decode(decoded_message)
            decoded_message = decoded_message.decode()
            print(f"Base64 Decoded Message: {colors.YELLOW}{decoded_message}{colors.RESET}")
        else:
            print(f"\n{colors.RED}Incorrect key entered!{colors.RESET}\n") # Notifying the user if the entered key or frame no. is incorrect

    if(audio == 'y'):
        subprocess.call(["ffmpeg","-i",temp_video_name,"-i","./temp/audio.mp3","-codec","copy",new_video_name,"-y"],stdout=open(os.devnull,"w"),stderr=subprocess.STDOUT)
        os.system('rm -rf ./temp/ && rm ' + temp_video_name)
    else:
        os.system('rm -rf ./temp/ && mv ' + temp_video_name + ' ' + new_video_name)
    print(f"\n{colors.GREEN}Thank you!{colors.RESET}\n")

# Function to check the file existence and file format
def check_file(video_name):
    flag = 0
    if((";" in video_name) or ("&&" in video_name)):
        print(f"\n{colors.RED}Invalid characters not allowed!{colors.RESET}\n")
    else:
        if(len(video_name.split(".")) == 2):
            cmd = "file " + video_name
            filetype = subprocess.check_output(cmd, shell=True)
            if("No such file or directory" in filetype.decode()[:-1]):
                print(f"{colors.RED}No video file exists with the name {video_name}!{colors.RESET}")
            elif(("MP4" in filetype.decode()[:-1]) or ("AVI" in filetype.decode()[:-1])):
                flag = 1
            else:
                print(f"{colors.RED}Invalid file format!{colors.RESET}")
        else:
            print(f"{colors.RED}No video file exists with the name {video_name}! (If exists then it should be in the present directory){colors.RESET}")

    if(flag == 1):
        return True
    else:
        return False

# Introduction Banner
print("-----------------------------------------------------------------------")
print(f"------------------------- {colors.GREEN}VIDEO STEGANOGRAPHY{colors.RESET} -------------------------")
print("-----------------------------------------------------------------------\n")

video_name = input('Enter the name of the video file: ')

if(check_file(video_name)):
    audio = input('Does this video have an audio? (y/n): ')
    steg_video(video_name, audio)

# END