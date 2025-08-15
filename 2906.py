import subprocess #line:1
import os #line:2
import hashlib #line:3
import socket #line:4
import sys #line:5
import time #line:6
import zipfile #line:7
import requests #line:8
import re #line:9
from tqdm import tqdm #line:10
CLIENT_VERSION ="1.4"#line:12
JAVA_PATH =r"C:\Quantuum\java\bin\java"#line:13
CLIENT_DIR =r"C:\Quantuum\client\*"#line:14
QUANTUUM_DIR =r"C:\Quantuum"#line:15
ASSETS_DIR =os .path .join (QUANTUUM_DIR ,"assets")#line:16
CLIENT_DIR_PATH =os .path .join (QUANTUUM_DIR ,"client")#line:17
JAVA_DIR_PATH =os .path .join (QUANTUUM_DIR ,"java")#line:18
delay =0.01 #line:20
EXPECTED_CODE ="2556503"#line:22
time_multipliers ={'s':1 ,'m':60 ,'h':3600 ,'d':86400 ,'w':604800 ,'mo':2592000 ,'y':31536000 }#line:24
def get_hwid ():#line:27
    try :#line:28
        O000OOOOO00OOOO0O ='powershell "Get-WmiObject -Class Win32_BIOS | Select-Object -ExpandProperty SerialNumber"'#line:29
        OO000OOOOOO0O0OOO =subprocess .check_output (O000OOOOO00OOOO0O ,shell =True ).decode ().strip ()#line:30
        return hashlib .sha256 (OO000OOOOOO0O0OOO .encode ()).hexdigest ()#line:31
    except Exception :#line:32
        return None #line:33
def run_jar (OOOOOOO00O0OO00O0 ):#line:36
    try :#line:37
        OOOOO0O00OO0O0O00 =os .environ .copy ()#line:38
        OOOOO0O00OO0O0O00 ['CLIENT_LAUNCHED']=EXPECTED_CODE #line:39
        OO0000OO0OO0OO0OO =os .path .dirname (os .path .abspath (CLIENT_DIR .rstrip ('\\*')))#line:40
        os .chdir (OO0000OO0OO0OO0OO )#line:41
        OO0O00O0000OOO0OO =[JAVA_PATH ,f"-Xmx{OOOOOOO00O0OO00O0}G","-noverify","-cp",f"{CLIENT_DIR}","Start"]#line:49
        OO0O00O0000OOO0OO .extend (sys .argv [1 :])#line:50
        O0O0000OO00OO000O =subprocess .CREATE_NO_WINDOW #line:51
        if os .name =='nt':#line:52
            O0O0000OO00OO000O |=subprocess .DETACHED_PROCESS #line:53
        subprocess .Popen (OO0O00O0000OOO0OO ,env =OOOOO0O00OO0O0O00 ,stdout =subprocess .DEVNULL ,stderr =subprocess .DEVNULL ,creationflags =O0O0000OO00OO000O )#line:54
        return True #line:55
    except Exception :#line:56
        return False #line:57
def check_and_setup_directories ():#line:60
    if not os .path .exists (QUANTUUM_DIR ):#line:61
        os .makedirs (QUANTUUM_DIR )#line:62
    return os .path .exists (ASSETS_DIR )and os .path .exists (CLIENT_DIR_PATH )and os .path .exists (JAVA_DIR_PATH )#line:63
def download_and_extract_zip (OOOOO0OO00O00O0OO ,OOOOOOO0OO0O0O000 ):#line:66
    try :#line:67
        print ("  Скачивание клиента...")#line:68
        OOOO00O0O0O0O00O0 =requests .get (OOOOO0OO00O00O0OO ,stream =True )#line:69
        OOOO00O0O0O0O00O0 .raise_for_status ()#line:70
        OO0O0O00O000OOO0O =os .path .join (OOOOOOO0OO0O0O000 ,"client.zip")#line:71
        O000O0O0O000OOOOO =int (OOOO00O0O0O0O00O0 .headers .get ('content-length',0 ))#line:72
        with open (OO0O0O00O000OOO0O ,'wb')as O0OO0O0O00O000OO0 ,tqdm (total =O000O0O0O000OOOOO ,unit ='iB',unit_scale =True ,unit_divisor =1024 )as OOO0000OO0000OO0O :#line:73
            for OO0O0O0OOOO0OO000 in OOOO00O0O0O0O00O0 .iter_content (chunk_size =1024 ):#line:74
                O0OO0O0O00O000OO0 .write (OO0O0O0OOOO0OO000 )#line:75
                OOO0000OO0000OO0O .update (len (OO0O0O0OOOO0OO000 ))#line:76
        with zipfile .ZipFile (OO0O0O00O000OOO0O ,'r')as OOOOO000000000000 :#line:77
            OOOOO000000000000 .extractall (OOOOOOO0OO0O0O000 )#line:78
        os .remove (OO0O0O00O000OOO0O )#line:79
        return True #line:80
    except Exception :#line:81
        return False #line:82
def animated_print (O0000OOO0OO000OO0 ):#line:85
    for OO00O000O00OO0000 in O0000OOO0OO000OO0 :#line:86
        sys .stdout .write (OO00O000O00OO0000 )#line:87
        sys .stdout .flush ()#line:88
        time .sleep (delay )#line:89
    print ()#line:90
def get_input (OOO0OOO0O0000O00O ,digits_only =False ):#line:93
    OOOOOO00O0O00O0O0 =input (OOO0OOO0O0000O00O )#line:94
    if digits_only and not OOOOOO00O0O00O0O0 .isdigit ():#line:95
        return ""#line:96
    return OOOOOO00O0O00O0O0 #line:97
def parse_duration (OOOO00000OO0OOO0O ):#line:100
    OOO0OO00000OOOOO0 =0 #line:101
    if OOOO00000OO0OOO0O .lower ()=="lifetime":#line:102
        return None #line:103
    O00OO0O000OO0OO00 =re .findall (r'(\d+)(y|mo|w|d|h|m|s)',OOOO00000OO0OOO0O .lower ())#line:104
    for O0000O0OOO00O0OOO ,O0O000OOO00000O00 in O00OO0O000OO0OO00 :#line:105
        OOO0OO00000OOOOO0 +=int (O0000O0OOO00O0OOO )*time_multipliers [O0O000OOO00000O00 ]#line:106
    return OOO0OO00000OOOOO0 #line:107
def format_russian_time (OO00O0000OOOOOO0O ):#line:110
    if OO00O0000OOOOOO0O is None :#line:111
        return "∞"#line:112
    OOO000O0O0O00OOO0 =OO00O0000OOOOOO0O //86400 #line:113
    O0OO00000000OOO0O =(OO00O0000OOOOOO0O %86400 )//3600 #line:114
    O0O0O0000O00OO0O0 =(OO00O0000OOOOOO0O %3600 )//60 #line:115
    OOO0OOO0OOO0O0000 =[]#line:116
    if OOO000O0O0O00OOO0 >0 :#line:117
        OOO0OOO0OOO0O0000 .append (f"{OOO000O0O0O00OOO0} дн.")#line:118
    if O0OO00000000OOO0O >0 :#line:119
        OOO0OOO0OOO0O0000 .append (f"{O0OO00000000OOO0O} ч.")#line:120
    if O0O0O0000O00OO0O0 >0 :#line:121
        OOO0OOO0OOO0O0000 .append (f"{O0O0O0000O00OO0O0} мин.")#line:122
    return ' '.join (OOO0OOO0OOO0O0000 )or "меньше минуты"#line:123
def main ():#line:126
    O0OO000OO0OO0O000 =["░██████╗░██╗░░░██╗░█████╗░███╗░░██╗████████╗██╗░░░██╗██╗░░░██╗███╗░░░███╗","██╔═══██╗██║░░░██║██╔══██╗████╗░██║╚══██╔══╝██║░░░██║██║░░░██║████╗░████║","██║██╗██║██║░░░██║███████║██╔██╗██║░░░██║░░░██║░░░██║██║░░░██║██╔████╔██║","╚██████╔╝██║░░░██║██╔══██║██║╚████║░░░██║░░░██║░░░██║██║░░░██║██║╚██╔╝██║","░╚═██╔═╝░╚██████╔╝██║░░██║██║░╚███║░░░██║░░░╚██████╔╝╚██████╔╝██║░╚═╝░██║","░░░╚═╝░░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝░░░╚═╝░░░░╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝"]#line:135
    for O000O00O0O0OOO0OO in O0OO000OO0OO0O000 :#line:136
        print (O000O00O0O0OOO0OO )#line:137
    O000000O000OO0OO0 =get_input ("\nЛогин: ")#line:139
    OOOOO0OOOOO000O00 =get_input ("Пароль: ")#line:140
    O0O0OO0OOO0OO0O00 =get_hwid ()#line:142
    if O0O0OO0OOO0OO0O00 is None :#line:143
        animated_print ("\nНе удалось получить HWID. Завершение работы.")#line:144
        time .sleep (5 )#line:145
        return #line:146
    O00O0O0O00000O000 =f"{O000000O000OO0OO0}:{OOOOO0OOOOO000O00}:{O0O0OO0OOO0OO0O00}:{CLIENT_VERSION}"#line:148
    OO0O0000OO0OO0OO0 ="e1.aurorix.net"#line:149
    O0OOOO0O0O000OO0O =20717 #line:150
    try :#line:152
        O00000O000OO0O000 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:153
        O00000O000OO0O000 .connect ((OO0O0000OO0OO0OO0 ,O0OOOO0O0O000OO0O ))#line:154
        O00000O000OO0O000 .sendall (O00O0O0O00000O000 .encode ())#line:155
        O0O00O00O0O00OO0O =O00000O000OO0O000 .recv (8192 ).decode ()#line:156
        O00000O000OO0O000 .close ()#line:157
        if O0O00O00O0O00OO0O =="Invalid username or password":#line:159
            print ("\nНеверный логин или пароль.")#line:160
            time .sleep (5 )#line:161
            return #line:162
        if O0O00O00O0O00OO0O =="Subscription expired":#line:164
            print ("\nПодписка истекла.")#line:165
            time .sleep (5 )#line:166
            return #line:167
        if O0O00O00O0O00OO0O .startswith ("Update required"):#line:169
            print (f"\n{O0O00O00O0O00OO0O}")#line:170
            time .sleep (5 )#line:171
            return #line:172
        if O0O00O00O0O00OO0O .startswith ("Subscription active"):#line:174
            O000O000O000OO0OO =re .search (r"Time:\s*(.*?)\s*(?:\r?\n)Download:\s*(\S+)",O0O00O00O0O00OO0O )#line:176
            if not O000O000O000OO0OO :#line:177
                print ("\nНе удалось разобрать ответ сервера.")#line:178
                time .sleep (5 )#line:179
                return #line:180
            OOOOO0OOO0O0O00OO ,OOO000O00OO0O0000 =O000O000O000OO0OO .groups ()#line:181
            O00OOOO0OO00OO00O =parse_duration (OOOOO0OOO0O0O00OO )#line:183
            OOOOOO0OO0O0OO0O0 =format_russian_time (O00OOOO0OO00OO00O )#line:184
            print (f"\nОсталось времени: {OOOOOO0OO0O0OO0O0}\n")#line:185
            if check_and_setup_directories ():#line:187
                O000OOO00O000O0OO =get_input ("\nRAM (ГБ): ",digits_only =True )#line:188
                if not O000OOO00O000O0OO :#line:189
                    print ("\nНеверный ввод RAM.")#line:190
                    time .sleep (5 )#line:191
                    return #line:192
                if run_jar (O000OOO00O000O0OO ):#line:193
                    print ("\nКлиент запущен. Лоадер закроется через 5 секунд.")#line:194
                    time .sleep (5 )#line:195
                    return #line:196
                else :#line:197
                    print ("\nНе удалось запустить клиент.")#line:198
            else :#line:199
                if OOO000O00OO0O0000 :#line:200
                    if download_and_extract_zip (OOO000O00OO0O0000 ,QUANTUUM_DIR ):#line:201
                        print ("\nУстановка успешно завершена. Перезапустите лоадер.")#line:202
                        time .sleep (5 )#line:203
                        return #line:204
                    else :#line:205
                        print ("\nОшибка при обновлении. Пожалуйста, обратитесь к создателю.")#line:206
                        time .sleep (5 )#line:207
                        return #line:208
                else :#line:209
                    print ("\nНе удалось получить ссылку на клиент.")#line:210
                    time .sleep (5 )#line:211
                    return #line:212
        print (f"\nНеизвестный ответ сервера: {O0O00O00O0O00OO0O}")#line:214
        time .sleep (5 )#line:215
    except Exception as O0OOOOO00O0O0O0OO :#line:217
        print (f"\nОшибка при подключении к серверу: {O0OOOOO00O0O0O0OO}")#line:218
        time .sleep (5 )#line:219
if __name__ =="__main__":#line:221
    main ()#line:222
