import firebase_admin
import numpy as np
from firebase_admin import credentials
from firebase_admin import firestore
import serial

cred = credentials.Certificate("/home/pi/Desktop/serviceAccountKey.json") #you have to add your own JSON authentication file here to communicate with firebase.
firebase_admin.initialize_app(cred)
db = firestore.client() #access the database.
parking_list = ["slot A","slot B","slot C","slot D"]
isCBooked = False
isDBooked = False

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0',9600, timeout=0.2)
    ser.flush()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            tmplist = line.split("_")
            tmplist.pop(-1)
            npList = (np.array(list(map(int,tmplist)))>0).tolist()
            if len(tmplist) == 4:
                print(npList)
                slotCollection = db.collection("Parking Master")
                slotDict = dict(zip(parking_list,npList))
                slotCollection.document("Parking Slots").set(slotDict)
                premiumBookColl = db.collection("Parking Master").document("Premium Book").get()
                gateColl = db.collection("Parking Master").document("Premium Gate").get()
                writeStr = ""
                if premiumBookColl.to_dict().get("slot C") and not(isCBooked):
                    writeStr = writeStr+"CB"
                    isCBooked = True
                elif not(premiumBookColl.to_dict().get("slot C")):
                    writeStr = writeStr+"CC"
                    isCBooked = False
                else:
                    writeStr = writeStr+"NN"
                if premiumBookColl.to_dict().get("slot D") and not(isDBooked):
                    writeStr = writeStr+"DB"
                    isDBooked = True
                elif not(premiumBookColl.to_dict().get("slot D")):
                    writeStr = writeStr+"DC"
                    isDBooked = False
                else:
                    writeStr = writeStr+"NN"
                if gateColl.to_dict().get("C Gate"):
                    writeStr = writeStr+"CG"
                else:
                    writeStr = writeStr+"CT"
                if gateColl.to_dict().get("D Gate"):
                    writeStr = writeStr+"DG\n"
                else:
                    writeStr = writeStr+"DT\n"
                ser.write(b""+writeStr.encode('utf-8'))