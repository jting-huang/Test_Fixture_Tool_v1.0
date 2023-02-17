import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
from tkinter.ttk import Notebook
import time
import connect
from connect import *
import serial
import threading
import multiprocessing as mp
from threading import Thread
from tkinter.font import Font, nametofont
from serial.tools.list_ports import comports
from multiprocessing import Pipe, Value, Lock, freeze_support
from Automation.BDaq import *
from Automation.BDaq.InstantAiCtrl import InstantAiCtrl


cp = ""
sn = ""
voltage = ""
version = "v1.0"

flag = 0

alarm_flag = 0 
alarm_state = 0
alarm_count = 0
count = 0


p1 = None
p2 = None
p3 = None

t1 = None
t2 = None
t3 = None
t4 = None

gataway_data = []

# deviceDescription = "USB-4711A,BID#5"
channelCount = 3
startChannel = 5
deviceDescription = "USB-4704,BID#0"


class main_page():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Y-Serial Testing Fixture Tool" + '  ' + version)        
        self.root.geometry("800x340")
        self.tab = ttk.Notebook(self.root)   

        # reset the font
        default_font = nametofont("TkDefaultFont")
        default_font.configure(size=12)
        text_font = nametofont("TkTextFont")
        text_font.configure(size=12)

        # call the certain functions
        self.menubar()
        self.probe_tab()
        self.device_tab()
        self.display_tab()

    def menu_command(self, event=None):
        print("menu")

    def menubar(self):
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        functions = tk.Menu(menubar)
        functions.add_command(label="menu1", command = self.menu_command)
        menubar.add_cascade(label="Functions", menu=functions)       

    def probe_tab(self):
        self.tab1 = ttk.Frame(self.root)
        self.tab.add(self.tab1, text="Probe")
        self.notebook_1 = Notebook(self.tab1)
        self.notebook_1.pack(side = tk.TOP,fill=tk.BOTH, expand=tk.YES)

        # call each sub page function
        self.sensor_A()
    
    def sensor_A(self, arg_port=''):
        global portChosen, senChosen, ftime, ftempature, iftem, mtem, fhumidity, ifhum, mhum, fNH3, ifNH3, mNH3, fCO2, ifCO2, mCO2, fwind, ifwind, mwind
        self.sensor1 = tk.Frame(self.notebook_1)
        self.notebook_1.add(self.sensor1, text="Sensor A")

        # Comport
        def click_comport(event):
            global cp
            cp = portChosen.get()
            messagebox.showinfo(
                title="Comport",
                message=f"Selected Comport: {cp}")
            print(cp)

        ttk.Label(self.sensor1, text="ComPorts").grid(column=0, row=0, padx=3, pady=3, stick='w')
        global port_list, sen_list
        port_list = ["Disable"]
        for p in comports():
            port_list.append(p.device)
        # print("Comport: " + str(port_list))

        if arg_port != '' and not arg_port in port_list:
            print('Cannot find Port \'%s\'' % (arg_port))
            return

        portChosen = ttk.Combobox(self.sensor1, value=port_list)
        portChosen['values'] = port_list
        portChosen.current(0) 
        portChosen.bind("<<ComboboxSelected>>", click_comport)
        portChosen.grid(row=0, column=1, padx=3, pady=3, stick='w')

        # Sensor
        def click_sensor(event):
            global sn
            sn = senChosen.get()
            messagebox.showinfo(
                title="Sensor",
                message=f"Selected Sensor: {sn}")
            print(sn)

        
        sen_list=["Disable", "X", "EC", "NDIR", "ANEM"]
        ttk.Label(self.sensor1, text="Sensor Type").grid(column=0, row=1, padx=3, pady=3, stick='w')
        senChosen = ttk.Combobox(self.sensor1, value=sen_list)
        senChosen['values'] = sen_list
        senChosen.current(0) 
        senChosen.bind("<<ComboboxSelected>>", click_sensor)
        senChosen.grid(row=1, column=1, padx=3, pady=3, stick='w')

        # Time
        ttk.Label(self.sensor1, text="Time interval").grid(
            row=2, column=0, padx=3, pady=3, stick='w')
        ftime = tk.StringVar()
        ftime.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=ftime,
                        ).grid(row=2, column=1, padx=3, pady=3, sticky='w')
        ttk.Label(self.sensor1, text="increments each read if time is 0").grid(
            row=2, column=2, padx=3, pady=3, stick='w')
    
        # Tempature
        ttk.Label(self.sensor1, text="Initial").grid(
            row=3, column=1, padx=3, pady=3, stick='w')
        ttk.Label(self.sensor1, text="Increment").grid(
            row=3, column=2, padx=3, pady=3, stick='w')
        ttk.Label(self.sensor1, text="Max/Min").grid(
            row=3, column=3, padx=3, pady=3, stick='w')
        ttk.Label(self.sensor1, text="Tempature").grid(
            row=4, column=0, padx=3, pady=3, stick='w')
        ftempature = tk.StringVar()
        ftempature.set(-20)
        tk.Entry(self.sensor1, state='normal', textvariable=ftempature
                        ).grid(row=4, column=1, padx=3, pady=0, sticky='w')

        iftem = tk.StringVar()
        iftem.set(5)
        tk.Entry(self.sensor1, state='normal', textvariable=iftem
                        ).grid(row=4, column=2, padx=3, pady=0, sticky='w')

        mtem = tk.StringVar()
        mtem.set(60)
        tk.Entry(self.sensor1, state='normal', textvariable=mtem
                        ).grid(row=4, column=3, padx=3, pady=0, sticky='w')
    
        # Humidity
        ttk.Label(self.sensor1, text="Humidity").grid(
            row=5, column=0, padx=3, pady=3, stick='w')
        fhumidity = tk.StringVar()
        fhumidity.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=fhumidity
                        ).grid(row=5, column=1, padx=3, pady=0, sticky='w')

        ifhum = tk.StringVar()
        ifhum.set(25)
        tk.Entry(self.sensor1, state='normal', textvariable=ifhum
                        ).grid(row=5, column=2, padx=3, pady=0, sticky='w')

        mhum = tk.StringVar()
        mhum.set(100)
        tk.Entry(self.sensor1, state='normal', textvariable=mhum
                        ).grid(row=5, column=3, padx=3, pady=0, sticky='w')
                     
        # NH3
        ttk.Label(self.sensor1, text="NH3").grid(
            row=6, column=0, padx=3, pady=3, stick='w')
        fNH3 = tk.StringVar()
        fNH3.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=fNH3
                        ).grid(row=6, column=1, padx=3, pady=0, sticky='w')

        ifNH3 = tk.StringVar()
        ifNH3.set(5)
        tk.Entry(self.sensor1, state='normal', textvariable=ifNH3
                        ).grid(row=6, column=2, padx=3, pady=0, sticky='w')

        mNH3 = tk.StringVar()
        mNH3.set(127)
        tk.Entry(self.sensor1, state='normal', textvariable=mNH3
                        ).grid(row=6, column=3, padx=3, pady=0, sticky='w')
    
        # CO2
        ttk.Label(self.sensor1, text="CO2").grid(
            row=7, column=0, padx=3, pady=3, stick='w')
        fCO2 = tk.StringVar()
        fCO2.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=fCO2
                        ).grid(row=7, column=1, padx=3, pady=0, sticky='w')

        ifCO2 = tk.StringVar()
        ifCO2.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=ifCO2
                        ).grid(row=7, column=2, padx=3, pady=0, sticky='w')

        mCO2 = tk.StringVar()
        mCO2.set(20000)
        tk.Entry(self.sensor1, state='normal', textvariable=mCO2
                        ).grid(row=7, column=3, padx=3, pady=0, sticky='w')

        # Wind
        ttk.Label(self.sensor1, text="Wind").grid(
            row=8, column=0, padx=3, pady=3, stick='w')
        fwind = tk.StringVar()
        fwind.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=fwind
                        ).grid(row=8, column=1, padx=3, pady=0, sticky='w')

        ifwind = tk.StringVar()
        ifwind.set(0)
        tk.Entry(self.sensor1, state='normal', textvariable=ifwind
                        ).grid(row=8, column=2, padx=3, pady=0, sticky='w')

        mwind = tk.StringVar()
        mwind.set(70)
        tk.Entry(self.sensor1, state='normal', textvariable=mwind
                        ).grid(row=8, column=3, padx=3, pady=0, sticky='w')


    def device_tab(self):
        self.tab2 = ttk.Frame(self.root)
        self.tab.add(self.tab2, text="Device")
        self.tab.pack(expand=1, fill="both")
        self.notebook_2 = Notebook(self.tab2)
        self.notebook_2.pack(side = tk.TOP,fill=tk.BOTH, expand=tk.YES)

        # self.DAQ()
        self.Gateway()
        # self.Power_Supply()

    def DAQ(self):
        self.daq = tk.Frame(self.notebook_2)
        self.notebook_2.add(self.daq, text="DAQ")
             
        def selection():
            if var:
                print('you have selected ' + var.get())
            if var1:
                print('you have selected ' + var1.get())

        var = tk.StringVar(None, "5V")
        var1 = tk.StringVar(None, "Temp")
        Label(self.daq, text = "DAQ Voltage State Selection", font=('Arial',20,'bold')).place(x=200, y=5)

        # 5V
        r_5V = tk.Radiobutton(self.daq, text='5V', variable=var, value="5V", command=selection)
        r_5V.grid(row=0, column=1, padx=3, pady=50, sticky='we') 

        # 10V
        r_10V = tk.Radiobutton(self.daq, text='10V', variable=var, value="10V", command=selection)
        r_10V.grid(row=0, column=2, padx=3, pady=50, sticky='we') 
        
        # Data State
        r1 = tk.Radiobutton(self.daq, text='Temp', variable=var1, value="Temp", command=selection)
        r1.place(x=3, y=100)
        r2 = tk.Radiobutton(self.daq, text='Humi', variable=var1, value="Humi", command=selection)
        r2.place(x=80, y=100)
        r3 = tk.Radiobutton(self.daq, text='NH3', variable=var1, value="NH3", command=selection)
        r3.place(x=160, y=100)
        r4 = tk.Radiobutton(self.daq, text='CO2', variable=var1, value="CO2", command=selection)
        r4.place(x=240, y=100)
        r5 = tk.Radiobutton(self.daq, text='Wind', variable=var1, value="Wind", command=selection)
        r5.place(x=320, y=100)
        

    def Gateway(self):
        global connect_btn, refresh_btn
        self.gateway = tk.Frame(self.notebook_2)
        self.notebook_2.add(self.gateway, text="Gateway")

        def connect_check(args):
            if "Disable" in clicked_com.get() or "Disable" in clicked_bd.get():
                connect_btn["state"] = "disable"
            else:
                connect_btn["state"] = "active"

        def baud_select():
            global clicked_bd, drop_bd
            clicked_bd = StringVar()
            bds = ["Disable", "9600", "38400", "115200"]      
            clicked_bd.set(bds[0])
            drop_bd = OptionMenu(self.gateway, clicked_bd, *bds, command=connect_check)
            drop_bd.config(width=10)
            drop_bd.grid(column=2, row=3, padx=20)

        def update_coms():
            global clicked_com, drop_COM
            ports = comports()
            coms = [com[0] for com in ports]
            coms.insert(0, "Disable")
            try:
                drop_COM.destroy()
            except:
                pass

            clicked_com = StringVar()
            clicked_com.set(coms[0])
            drop_COM = OptionMenu(self.gateway, clicked_com, *coms, command=connect_check)
            drop_COM.config(width=10)
            drop_COM.grid(column=2, row=2, padx=20)
            connect_check(0)

        def readSerial():
            print("Receiving gateway data")
            gw_str = StringVar()
            global serialData, gw_data
            while serialData: 
                global nh3ppm, signed_temp, humi, rssi, battery
                data = ser.readline()
                str_data = gw_str.set(gataway_data(data))

                gw_data = tk.Label(self.notebook_3,
                            text=check_gatewayData(str_data),
                            borderwidth=0,
                            font=('Arial',24,'bold'),
                            fg='#00FF00')
                gw_data.place(x=180, y=180)
                # time.sleep(3)
                # gw_data.config(text='')
             

        def connection():
            global ser, serialData
            if connect_btn["text"] in "Disconnect":
                serialData = False
                connect_btn["text"] = "Connect"
                refresh_btn["state"] = "active"
                drop_bd["state"] = "active"
                drop_COM["state"] = "active"
            else:
                serialData = True
                connect_btn["text"] = "Disconnect"
                refresh_btn["state"] = "disable"
                drop_bd["state"] = "disable"
                drop_COM["state"] = "disable"
                port = clicked_com.get()
                baud = clicked_bd.get()

                try:
                    ser = serial.Serial(port, baud, timeout=0.5)
                except:
                    pass

                global t4

                t4 = Thread(target=readSerial)
                t4.daemon = True
                t4.start()
                t4.join(1)

        port_lable = Label(self.gateway, text="ComPorts: ")
        port_lable.grid(column=1, row=2, pady=20, padx=10)

        port_bd = Label(self.gateway, text="Baud Rate: ")
        port_bd.grid(column=1, row=3, pady=20, padx=10)

        connect_btn = Button(self.gateway, text="Connect", height=1,
                            width=10, state="disabled", command=connection)
        connect_btn.grid(column=3, row=3)

        refresh_btn = Button(self.gateway, text="Refresh", height=1,
                            width=10, command=update_coms)
        refresh_btn.grid(column=3, row=2)

        baud_select()
        update_coms()


    def display_tab(self):     
        self.tab3 = ttk.Frame(self.root)
        self.tab.add(self.tab3, text="Display")
        self.tab.pack(expand=1, fill="both")
        self.notebook_3 = Notebook(self.tab3)
        self.notebook_3.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        lb_Fixture = tk.Label(self.notebook_3, 
                    font=('Arial',24,'bold'), 
                    text="Probe A", 
                    anchor='nw',
                    fg='blue',
                    padx=5, pady=5)
        lb_Fixture.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        lb_pw = tk.Label(self.notebook_3, 
                    font=('Arial',18,'bold'), 
                    text="Power State : ", 
                    anchor='nw')
        lb_pw.place(x=5, y=60)

        lb_pb = tk.Label(self.notebook_3, 
                    font=('Arial',18,'bold'), 
                    text="Probe State : ", 
                    anchor='nw')
        lb_pb.place(x=5, y=120)


        lb_gt = tk.Label(self.notebook_3, 
                    font=('Arial',18,'bold'),
                    text="Gateway Data:",
                    anchor='nw')               
        lb_gt.place(x=5, y=180)

        lb_al = tk.Label(self.notebook_3, 
                        font=('Arial',18,'bold'),
                        text="Alarm State:",
                        anchor='nw')               
        lb_al.place(x=5, y=240)


        # power state
        def DAQ_NAVI():
            global startChannel, channelCount, voltage, scaledData
            instanceAiObj = InstantAiCtrl(deviceDescription)
            while True:
                time.sleep(0.5) 
                # print("DAQ_NAVI Running")
                _, scaledData = instanceAiObj.readDataF64(startChannel, channelCount)
                for i in range(startChannel, startChannel + channelCount):  
                    if scaledData[0] != None:
                        voltage = format(scaledData[i-startChannel], '.3f')
                        # print("DAQ Value:" + voltage)   
                        global flag, count, lb_ok, lb_error, alarm_flag, al_on, al_off, al_error, alarm_count, alarm_state
                        if (voltage >= "4.825" <= "5.125") and count < 30:
                            lb_ok = tk.Label(self.notebook_3,
                                        text='OK',
                                        font=('Arial',24,'bold'),
                                        fg='#00FF00')                    
                            lb_ok.place(x=165, y=60)
                            count = 0     
                                    
                        if (voltage >= "4.825" <= "5.125") and count > 30:
                            print("Power State Changed")         
                            lb_error = tk.Label(self.notebook_3,
                                        text='FAIL',
                                        font=('Arial',18,'bold'),
                                        fg='#FF0000')
                            lb_error.place(x=160, y=60)   
                            flag = 1 
                            
                        if voltage < "4.825" and count > 30:
                            print("Power State Changed")           
                            lb_error = tk.Label(self.notebook_3,
                                        text='FAIL',
                                        font=('Arial',18,'bold'),
                                        fg='#FF0000')
                            lb_error.place(x=160, y=60) 
                            flag = 1   


                        if voltage != None:
                            if (scaledData[2]) < 1.5:
                                # print("Alarm off vlotage:", voltage)
                                # print("Alarm off count:", alarm_count)
                                time.sleep(0.5)
                                alarm_count += 1
                            
                                if alarm_count > 10 and alarm_flag == 0 and alarm_state == 0:
                                    al_off = tk.Label(self.notebook_3, 
                                                font=('Arial',20,'bold'),
                                                text="Alarm Off",
                                                fg='#00FF00')               
                                    al_off.place(x=150, y=240)
                                    
                                elif alarm_flag == 2:
                                    al_off = tk.Label(self.notebook_3, 
                                                font=('Arial',20,'bold'),
                                                text="Alarm Off",
                                                fg='#00FF00')               
                                    al_off.place(x=150, y=240)
                                    alarm_count = 0

                            # if voltage != None and alarm_count > 30:
                            #     alarm_count = 0   
         
                            if (scaledData[2]) > 1.5:
                                alarm_flag = 1
                                alarm_state = 1
                        
                                if alarm_flag == 1 and alarm_state == 1:
                                    al_on = tk.Label(self.notebook_3, 
                                                font=('Arial',20,'bold'),
                                                text="Alarm On",
                                                fg='#FF8000')               
                                    al_on.place(x=150, y=240)
                                    alarm_flag = 2
                        
                                    if alarm_flag == 2 and alarm_count > 60 and (scaledData[2]) < 1.5:
                                        alarm_state = 2

                                    if alarm_state == 2:
                                        al_error = tk.Label(self.notebook_3, 
                                                    font=('Arial',20,'bold'),
                                                    text="Alarm Fail",
                                                    fg='#FF0000')               
                                        al_error.place(x=150, y=240)
                               

        # probe state
        def probe_state():
            global flag, pb_flag, pb_ok, pb_error
            while True:
                if pb_flag == 0:
                    pb_flag = 1 
                    
                if pb_flag == 1:
                    time.sleep(1)
                    pb_ok = tk.Label(self.notebook_3,
                                    text='OK',
                                    font=('Arial',24,'bold'),
                                    fg='#00FF00')                    
                    pb_ok.place(x=165, y=120)
                
                if flag == 1:
                    pb_flag = 2
                    
                    if pb_flag == 2:
                        time.sleep(1)
                        print("Probe State Error")
                        pb_error = tk.Label(self.notebook_3,
                                        text='FAIL',
                                        font=('Arial',18,'bold'),
                                        fg='#FF0000')                    
                        pb_error.place(x=160, y=120)

                if flag == 0:
                    pb_flag = 0
                    
                    

        # counter
        def time_out():
            global count
            while True:
                time.sleep(1)
                count += 1
                # print("Timeout:", count)
                
        try:
            t1 = Thread(target=DAQ_NAVI)
            t1.daemon = True # kill thread forced
            t1.start()
            t1.join(1) # waiting for main thread join

            t2 = Thread(target=probe_state)
            t2.daemon = True
            t2.start()
            t2.join(1)

            t3 = Thread(target=time_out)
            t3.daemon = True
            t3.start()
            t3.join(1)       
        except BaseException as e:
            print('{!r}; restarting thread'.format(e))


        def reset():
            global scaledData, lb_ok, lb_error, pb_ok, pb_error, flag, pb_flag, count, alarm_flag, al_on, al_off, al_error, alarm_count, alarm_state
            if p1.is_alive:
                p1.terminate()
                print('stop process')
                p1.join()

            if flag == 0:
                lb_ok.config(text="     ")
                scaledData[0] = scaledData
                flag = 0
            else:
               pass

            if flag == 1:
                lb_error.config(text="        ")
                scaledData[0] = scaledData
                flag = 0
            else:
                pass

            if pb_flag == 1:    
                pb_ok.config(text="     ")
            else:
                pass

            if pb_flag == 2:
                  pb_error.config(text="        ")
            else:
                pass

            if alarm_state == 0:
                al_off.config(text="                 ")
            else:
                pass

            if alarm_state == 1:
                al_on.config(text="                 ")
            else:
                pass

            if alarm_state == 2:
                al_error.config(text="                      ")
            else:
                pass


            ftime.set(0)
            ftempature.set(-20)
            iftem.set(5)
            mtem.set(60)
            fhumidity.set(0)
            ifhum.set(25)
            mhum.set(100)
            fNH3.set(0)
            ifNH3.set(5)
            mNH3.set(127)
            fCO2.set(0)
            ifCO2.set(0)
            mCO2.set(20000)
            fwind.set(0)
            ifwind.set(0)
            mwind.set(70)

            count = 0
            alarm_count = 0
            alarm_flag = 0
            alarm_state = 0
            


        # Run Process
        ttk.Button(self.notebook_3, text="Run", 
            command=lambda:click_run(senChosen.get(), ftime.get(), ftempature.get(), iftem.get(), mtem.get(), fhumidity.get(), ifhum.get(), mhum.get(),
            fNH3.get(), ifNH3.get(), mNH3.get(), fCO2.get(), ifCO2.get(), mCO2.get(), fwind.get(), ifwind.get(), mwind.get(), portChosen.get())).place(
            x=680, y=50) 

        # Reset
        ttk.Button(self.notebook_3, text="Reset", command=reset).place(x=680, y=100)

        
        self.root.mainloop()
        # Check Process State
        if p1.is_alive:
            # stop a process gracefully
            p1.terminate()
            print('stop process')
            p1.join()
        else:
            return
        

def click_run(sen, ftime, tem, item, mtem, hum, ihum, mhum, nh3, inh3, mnh3, CO2, iCO2, mCO2, wind, iwind, mwind, port):
    ftime, tem, item, hum, ihum, nh3, inh3 = float(ftime), float(tem), float(item), float(hum), float(ihum), float(nh3), float(inh3)
    CO2, iCO2, wind, iwind = float(CO2), float(iCO2), float(wind), float(iwind)  
    fmtem, fmhum, fmnh3, fmco2, fmwind = float(mtem), float(mhum), float(mnh3), float(mCO2), float(mwind)

    print(port, sen, "time:", ftime)
    print("t\t", tem, item, fmtem, "\th\t", hum, ihum, fmhum, "\tammonia\t", nh3, inh3, fmnh3)
    print("CO2\t", CO2, iCO2, fmco2, "\twind\t", wind, iwind, fmwind)

    global p1, p2, p3
  
    p1 = mp.Process(target=connect.send_data, args=(sen, ftime, tem, item, fmtem, hum, ihum, fmhum, 
        nh3, inh3, fmnh3, CO2, iCO2, fmco2, wind, iwind, fmwind, port))
    p1.start()
    p1.join(1)

    

# def reset():
    # for widget in self.sensor1.winfo_children():
    #     if isinstance(widget, ttk.Combobox):
    #         widget.delete(0, 'end')
    #     if isinstance(widget, tk.Entry):
    #         widget.delete(0, 'end')
    #     if isinstance(widget, tk.Text):
    #         widget.delete('1.0', 'end')
    #     if isinstance(widget, tk.Checkbutton):
    #         widget.deselect()
    #     if isinstance(widget, tk.Radiobutton):
    #         r_time.set(None)


def main():
    display = main_page()
    display.root.mainloop()


if __name__ == "__main__":
    # Add support for when a program which uses multiprocessing
    # has been frozen to produce a Windows executable.
    freeze_support()
    main()