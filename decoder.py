import sys
import time
import os
from cryptography.fernet import Fernet
file_paths = sys.argv[1]  # the first argument is the script itself
head_tail = os.path.split(file_paths)
filename = head_tail[1]
with open('filekey.key', 'rb') as filekey: 
    key = filekey.read() 
fernet = Fernet(key) 

with open(filename, 'rb') as enc_file: 
    encrypted = enc_file.read() 
decrypted = fernet.decrypt(encrypted) 

with open('output.csv', 'wb') as dec_file: 
    dec_file.write(decrypted) 
print("DONE")
time.sleep(1)
