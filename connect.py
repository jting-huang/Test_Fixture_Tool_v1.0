import serial, struct, time , random
# from random import randint
# from multiprocessing import Process, Value, Lock

pb_flag = 0
pb_list = [0, 1, 2]
 
# def get_xData(x):
#     global x_temp # 宣告全域性變數
#     time.sleep(0.01)
#     # with x_temp.get_lock(): # 直接呼叫get_lock()函式獲取鎖
#     x.value = x_temp
             

def send_data(sen, ftime, temperature, it, mt, humidity, ih, mh, ammonia, inh3, mnh3, 
    CO2, iCO2, mCO2, wind, iwind, mwind, port):
    global x_temp
   
    read_times = 0 
    incre_when = 2
    
    if sen == "NDIR":
        ser = serial.Serial(port, 38400, timeout=1)  # open serial port
    elif sen == "ANEM":
        ser = serial.Serial(port, 9600, timeout=1)
    else:
        ser = serial.Serial(port, 115200, timeout=1)
    

    start_time = time.time()
    g1ec_counter = 0

    while True:    
        if sen == "NDIR":
            send = ser.read(7)
        elif sen == "EC":
            send = ser.read(11)
        else:
            send = ser.read(5)
        print(send, "send") 

        if ftime != 0:
            if(time.time()-start_time > ftime):
                start_time = time.time()
                if it >= 0:
                    temperature = min(temperature+it, mt)
                elif it <= 0:
                    temperature = max(temperature+it, mt)
                
                if ih >= 0:
                    humidity = min(humidity+ih, mh)
                if ih < 0:
                    humidity = max(humidity+ih, mh)
                
                if inh3 >= 0:
                    ammonia = min(ammonia+inh3, mnh3)
                elif inh3 < 0:
                    ammonia = max(ammonia+inh3, mnh3)
                
                if iCO2 >= 0:
                    CO2 = min(CO2+iCO2, mCO2)
                elif iCO2 < 0:
                    CO2 = max(CO2+iCO2, mCO2)

                if iwind >= 0:
                    wind = min(wind+iwind, mwind)
                elif iwind < 0:
                    wind = max(wind+iwind, mwind)
                # print("temperature:\t", temperature, "\thumidity:\t", humidity, "\tammonia:\t",  ammonia)
                # print("CO2:\t\t", CO2, "\twind:\t\t",  wind) 

        if sen == "X":    
            if(send == b'E\x00\x01\x13Y'): 
                print("receive data")
                global pb_flag, x_temp
                pb_flag = 0
                # print(get_pb(0))
                # print("pb_flag:", pb_flag)
                # ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B, 0xCD, 0xCC, 0xCC, 0x41, 0x66, 0x66, 0x86, 0x42, 0x3A]))
                send_th(ser, temperature, humidity)
                # x_temp = temperature
                # print("xData_temp:", x_temp)
                # x_humi = humidity
                # print("xData_humi:", x_humi)
                # ser.write(serial.to_bytes([]))
    
                if ftime == 0: # and read_times%incre_when == 0:
                    if it >= 0:
                        temperature = min(temperature+it, mt)
                    elif it < 0:
                        temperature = max(temperature+it, mt)
                    
                    if ih >= 0:
                        humidity = min(humidity+ih, mh)
                    if ih < 0:
                        humidity = max(humidity+ih, mh)
                # read_times += 1
                # print("read", read_times, incre_when)
            
            if(send == b'E\x00\x01\xca\x10'):
                pb_flag = 1
                # print(get_pb(1))   
                # print("pb_flag:", pb_flag) 
                # ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B, 0x9A, 0x99, 0x49, 0x41, 0xBD]))
                time.sleep(0.364)
                send_xnh3(ser, ammonia) 
                # x_ammo = ammonia
                # print("xData_ammo:", x_ammo)

                # gl_nh3 = send_ammo(ammonia)
                # print("Got NH3 data:", send_nh3)

                if ftime == 0 and read_times%incre_when == 0: 
                    if inh3 >= 0:
                        ammonia = min(ammonia+inh3, mnh3)
                    elif inh3 < 0:
                        ammonia = max(ammonia+inh3, mnh3)  
              
        elif sen == "EC":
            # b'E\x00\x01\xe0\x26' ppm        
            if(send == b'E\x00\x01\xe0\x26'):   
                # ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B, 0x9A, 0x99, 0x49, 0x41, 0xBD]))
                send_ecnh3(ser, ammonia)
                if ftime == 0 and g1ec_counter == 1: 
                    print(" second command")
                    ammonia = min(ammonia+inh3, mnh3) 
                    g1ec_counter = 0
                elif ftime == 0 and g1ec_counter == 0:
                    print(" first command")
                    g1ec_counter += 1

            # for low power
            elif(send == b'\x00\x00\x00E\x00\x01C\x89\x01\x01'):
                # print('sent "OK" as low power')                
                # ser.write(serial.to_bytes([0x4F, 0x4B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x9A])) 

                print('sent "NG" as low power')                
                ser.write(serial.to_bytes([0x4E, 0x47, 0x00, 0x00, 0x00, 0x00, 0x00, 0x95])) 
    

            elif(send == b'\x00\x00\x00E\x00\x01\xe0&'):
                send_ecnh3(ser, ammonia)
                if ftime == 0: 
                    ammonia = min(ammonia+inh3, mnh3) 

            elif(send == b'\x00\x00\x00E\x00\x01C\x89\x01\x01\x00\x00\x00E\x00\x01C\x89\x01\x01'):
                ser.write(serial.to_bytes([0x4F, 0x4B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x9A])) 
                send_ecnh3(ser, ammonia)
                if ftime == 0: 
                    ammonia = min(ammonia+inh3, mnh3)

        elif sen == "NDIR":
            if(send == b'\x10\x13\x06\x10\x1F\x00\x58'):     
            # if(send == b'\x10\x130\x10\x1f\x00\x82'):    
                send_co2(ser, CO2)
                # print("Hello")
                if ftime == 0: 
                    CO2 = min(CO2+iCO2, mCO2)

        elif sen == "ANEM":
            if(send == b'\xaa\x01\x03\x0f\x00'): 
                send_wind(ser, wind)
                if ftime == 0: 
                    wind = min(wind+iwind, mwind)
        else:
            print("Sensor type is erroneous")


def get_pb():
    global pb_flag
    if pb_flag == 0:
        pb_flag = pb_list[0]
        print("state 1")
        pb_flag = 1
    elif pb_flag == 1:
        pb_flag = pb_list[1]
        print("state 2")
    elif pb_flag != 0 and pb_flag != 1:
        pb_flag = 2
    elif pb_flag == 2:
        pb_flag = pb_list[2]
        print("state 3")
    return pb_flag


# flag = [1, 2, 3]

# def get_probeFlag():
#     if flag == 1:
#         print("Probe flag A")
#     elif flag == 2:
#         print("Probe flag B")
#     elif flag == 3:
#         print("Probe flag C")
#     return flag


def bytes_to_int(bytes):
    _number = bytes
    _number = _number.decode("utf-8")
    _number = "0x"+ _number
    _number = int(_number,16)
    return _number

def at_cmd_cksum(data):
    cksum = 0
    cmd_cksum = 0
    if(data[0:5] == b'at+s='):
        cmd_str = data[0:46].decode("utf-8")
        slot = 0
        for c in cmd_str:
            cksum += ord(c)

        # print(data[46:49],'/', hex(cksum))
        if(data[46:49] != b''):
            cmd_cksum = bytes_to_int(data[46:49])
        # print(cmd_cksum, type(cmd_cksum))
        # print(cmd_cksum,'/', hex(cksum))
        if(cmd_cksum == cksum):
            return 'OK'
        else:
            return 'xOK'


def check_gatewayData(send):
    global nh3ppm, signed_temp, humi
    if(at_cmd_cksum(send) == 'OK'):
        lora_id = send[5:(5+8)]
        # print("lora_id:", lora_id)
        payload_data = send[(5+8+10):(5+8+10+22)]
        # print("payload_data:", payload_data)

        payload_hex = []
        for i in range(0, 22, 2):
           payload_hex.append(bytes_to_int(payload_data[i:(i+2)])) # for checksum
           
        if(payload_hex[0] == 1): # Regular measurement package (Y gen1)
            tx_idx = payload_hex[1]
            nh3ppm = payload_hex[2]
            temp = payload_hex[3]
            byte_temp = temp.to_bytes(1, "little")
            temp = struct.unpack('b', byte_temp)
            signed_temp = temp[0]
            humi = payload_hex[4]
            # print(tx_idx, nh3ppm, signed_temp, humi)
            print("gateway:", "NH3:", nh3ppm, "Temp:", signed_temp, "Humi:", humi)
        elif(payload_hex[0] == 2): # Status report package (Y gen1)
            tx_idx = payload_hex[1]
        elif(payload_hex[0] == 3): # System information package (Y gen1)
            tx_idx = payload_hex[1]
        elif(payload_hex[0] == 4): # System parameter package (Y gen1)
            tx_idx = payload_hex[1]
        
        return nh3ppm, signed_temp, humi

def NH3_Data(send):
    global nh3ppm
    if(at_cmd_cksum(send) == 'OK'):
        lora_id = send[5:(5+8)]
        # print("lora_id:", lora_id)
        payload_data = send[(5+8+10):(5+8+10+22)]
        # print("payload_data:", payload_data)

        payload_hex = []
        for i in range(0, 22, 2):
           payload_hex.append(bytes_to_int(payload_data[i:(i+2)])) # for checksum
           
        if(payload_hex[0] == 1): # Regular measurement package (Y gen1)
            tx_idx = payload_hex[1]
            nh3ppm = payload_hex[2]
            # print("NH3:", nh3ppm)
        elif(payload_hex[0] == 2): # Status report package (Y gen1)
            tx_idx = payload_hex[1]
        elif(payload_hex[0] == 3): # System information package (Y gen1)
            tx_idx = payload_hex[1]
        elif(payload_hex[0] == 4): # System parameter package (Y gen1)
            tx_idx = payload_hex[1]
        
        return nh3ppm


# float to hex
def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])
    
# ieee_754 fomat   
def ieee_754(num):
    hexnum = []
    a = float_to_hex(num)
    hexnum.append(int(a[0:4], 16))
    for i in range(4, len(a), 2):
        b = "0x"+a[i:i+2]
        hexnum.append(int(b, 16))
    
    if(num == 0):
        hexnum = [0, 0, 0, 0]
    return hexnum

# gl_t = 0.0
# gl_h = 0.0
def send_th(ser, temperature, humidity):
    global gl_t, gl_h
    gl_t = temperature
    gl_h = humidity

    t, h = ieee_754(temperature), ieee_754(humidity) 
    t.reverse()
    h.reverse()
    th = t+h
    checkth = hex(sum(th))
    if(sum(th) == 0):
        checkth = "0x00"  
    checkth2 = int(checkth[:2]+checkth[-2:], 16)

    # wrong checksum
    random_error = random.uniform(0, 1)
    # print(random_error)
    # if random_error > 0.5:
    #     print("T/H data CHECKSUM ERROR")
    #     checkth2 = 0

    th.append(checkth2) # Mark down

    # OK
    # random_error = random.uniform(0, 1)
    # if random_error > 0.5:
    #     print("T/H OK CHECKSUM ERROR")
    #     ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9A] + th))
    # else:


    ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B] + th)) # Mark down

    # test_s = hex(sum([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00]))
    # print( "sum", test_s, int(test_s[:2]+test_s[-2:], 16))

    # NG 
    # ser.write(serial.to_bytes([0x4E, 0x47, 0x00, 0x00, 0x00, 0x00, 0x00, 0x95] + th))
    print("simulator:", "temp:", temperature, "hum:", humidity)
    return temperature, humidity

def send_xnh3(ser, ammonia):
    global gl_nh3
    gl_nh3 = ammonia
    nh3 = ieee_754(ammonia)
    nh3.reverse()
    check = hex(sum(nh3))
    if(sum(nh3) == 0):
        check = "0x00"
    check2 = int(check[:2]+check[-2:], 16)

    # wrong checksum
    # random_error = random.uniform(0, 1)
    # print(random_error)
    # if random_error > 0.5:
    #     print("NH3 data CHECKSUM ERROR")
    #     check2 += 1

    random_error = random.uniform(0, 1)
    # print(random_error)
    if random_error > 0.5:
        # print("T/H data CHECKSUM ERROR")
        check2 = 0
    nh3.append(check2)

    # OK
    # random_error = random.uniform(0, 1)
    # if random_error > 0.5:
    #     print("NH3 OK CHECKSUM ERROR")
    #     ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9A] + nh3))
    # else:
    #     ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B] + nh3))   
    ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B] + nh3))

    # NG 
    # ser.write(serial.to_bytes([0x4E, 0x47, 0x00, 0x00, 0x00, 0x00, 0x00, 0x95] + nh3))         
    print("simulator:", "ammonia", ammonia)
    return ammonia


# def send_temphumi(temperature, humidity):
#     t = temperature
#     h = humidity
#     print("temp:", temperature, "hum:", humidity) 
#     return t, h 


def send_ammo(ammonia):
    global gl_nh3
    gl_nh3 = ieee_754(ammonia)
    gl_nh3.reverse()
    # print("ammo:", ammonia)
    return gl_nh3
   

def send_ecnh3(ser, ammonia):
    nh3 = ieee_754(ammonia)
    nh3.reverse()
    check = hex(sum(nh3))
    if(sum(nh3) == 0):
        check = "0x00"
    check2 = int(check[:2]+check[-2:], 16)
    nh3.append(check2)
    ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B, 0x00, 0x00] + nh3))            
    print("ammonia", ammonia)

def send_co2(ser, fco2):    
    # ser.write(serial.to_bytes([0x4F, 0x4B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x9B, 0x9A, 0x99, 0x49, 0x41, 0xBD]))
    checksumB = []
    co2 = ieee_754(fco2)
    co2.reverse()
    raw_buffer = [0x10, 0x1A, 0x08, 0x01, 0x00, 0x00, 0x00] + co2 + [0x10, 0x1F]
    checksum = sum(raw_buffer)
    checksum = checksum.to_bytes(2, byteorder="big")
    checksumB.append(checksum[0])
    checksumB.append(checksum[1])
    # time.sleep(1)
    ser.write(serial.to_bytes(raw_buffer + checksumB))
    print("CO2", fco2)
    return

def send_wind(ser, ws):
    raw_buffer = [0x57, 0x53, 0x3D]
    raw_buffer2 = [0x6D, 0x2F, 0x73, 0x0A]
    ser.write(serial.to_bytes(raw_buffer))
    float_num = float(ws)
    if float_num >= 70:
        float_num = 70.0
    ser.write((str(format(float_num, '2.1f')).zfill(4)).encode())
    # print(type(ws)) 
    ser.write(serial.to_bytes(raw_buffer2))
    print("Wind", ws)
    return


if __name__ == '__main__':
    send_data()