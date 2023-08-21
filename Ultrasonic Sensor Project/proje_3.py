from tkinter import *
from datetime import datetime
import time
import ntplib
import mysql.connector
from time import ctime
from tkinter import ttk
import threading
import RPi.GPIO as GPIO

#gpio pin tanımları
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setwarnings(False)

#window ayarları
root = Tk()
root.geometry("600x500")
root.resizable(1,0)


def PrintTime():#zaman döndurur

    ntpc = ntplib.NTPClient()

    resp = ntpc.request('pool.ntp.org')

    result =  "Global Time : ", ctime(resp.tx_time)

    time_label.config(text=result)
    
def Save_DB_run(num):
    global threads_status
    threads_status=True
    while True:
        #print(num)
        GPIO.output(TRIG, False)
        print ("Olculuyor...")   
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()
            
        while GPIO.input(ECHO)==1:
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        sql=""
        user_time = int(time_entry.get())
        
        if distance > 2 and distance< 400:
            print ("Mesafe:",distance - 0.5,"cm")

            conneciton = mysql.connector.connect(host = '127.0.0.1', user = 'root', password = 'raspberry', database = 'pi')
            cursor = conneciton.cursor()
            
            time_now=datetime.now()
            
            now_dis=distance - 0.5
            
            sql = (f"INSERT INTO range_data (date,data) VALUES ('{str(time_now)}',{now_dis})")
            
            PrintTime()
            
            cursor.execute(sql)
            conneciton.commit()
            conneciton.close()
            
            global treeview_id
            tv.insert(parent='', index=treeview_id, iid=treeview_id, text='', values=(str(time_now),now_dis))            
            treeview_id += 1
            
        else:
            print ('Menzil asildi')
        time.sleep(user_time)
        global stop_threads
        if stop_threads:
            break
    

t1 = threading.Thread(target=Save_DB_run, args=(10,))
treeview_id=0
stop_threads = False
threads_status=False

def StartButtonFunc():#ok butonu    
    global stop_threads
    stop_threads = False
    global t1
    if threads_status==False:
        t1.start()
    else:
        print ('Zaten Çalışıyor')

#tasarımlar
frame_color = "black"
button_color = "yellow"
time_font = ("Times New Roman",20)
entry_font = ("Times New Roman",20)
input_frame = Frame(root)

output_frame = Frame(root)

input_frame.grid(row=0,column=0)

output_frame.grid(row=1,column=0)


time_entry = Entry(input_frame,font=entry_font)

ok_button = Button(input_frame,text = "OK", font=time_font,bg=button_color,width=2,height=1,command=StartButtonFunc)

time_entry.grid(row=0,column=0,padx=(120,10),pady=5)

ok_button.grid(row=1,column=0,pady=5,padx=(120,10))


time_label = Label(output_frame,font=time_font,text="")

time_label.grid(row=1,column=0,pady=5,padx=(90,5))


tv = ttk.Treeview(output_frame,columns=(1,2), show="headings", height="5" )

tv.grid(row=0)

tv.heading(1,text="date")
tv.heading(2,text="data")

root.mainloop()
#tasarımlar end
