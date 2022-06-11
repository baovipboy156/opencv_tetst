import re
import cv2 as cv
import numpy as np
import win32gui
import winsound
import time

from threading import Thread

from window import window
from imgProcess import imgProcess

def read_configs():
    file=open('config.txt')
    configs=[]
    for line in file.read().splitlines():
        configs.append(line.split(','))
    return configs
#dùng regex để filter window 
def get_all_EVE_window_HWND():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindow(hwnd):
            window_name = win32gui.GetWindowText(hwnd)
            if re.match( '^EVE \\- |^EVE' , window_name):   
                if win32gui.IsWindowVisible(hwnd):
                    #ignore cái launcher
                    if window_name == 'EVE Launcher':
                        pass
                    else:
                        list_EVE_HWND.append(hwnd)
    list_EVE_HWND = []
    win32gui.EnumWindows(winEnumHandler, None)
    return list_EVE_HWND

def load_EVE_windows(list_EVE_HWND):
    from window import window
    global windows
    windows=[]
    for HWND in list_EVE_HWND:
        windows.append(window(HWND))
    return windows

def sort_EVE_HWND_by_config(configs,list_EVE_HWND):
    sorted_list_EVE_HWND=[]
    for config in configs:
        for HWND in list_EVE_HWND:
            window_name= win32gui.GetWindowText(HWND)
            #config[0] : EVE - S0RASI
            if config[0]==window_name:
                sorted_list_EVE_HWND.append(HWND)
    for HWND1 in sorted_list_EVE_HWND:
        for HWND2 in list_EVE_HWND:
            if HWND2 == HWND1:
                list_EVE_HWND.pop(list_EVE_HWND.index(HWND2))
    return sorted_list_EVE_HWND +list_EVE_HWND

   
def set_detect(bool_var):
    global detect, red, org, neu,alerting
    detect = bool_var
    if bool_var == False:
        red = org = neu = None
        alerting=0
        winsound.PlaySound(None,winsound.SND_PURGE)
        print('Detect disabled')
    else:
        #khởi tạo imgprocess
        red = imgProcess('10.jpg')
        org = imgProcess('5.jpg')
        neu = imgProcess('0.jpg')
        print('Detect enabled')

def alert(num):
    global alerting
    if num!=0 and alerting !=1:
        winsound.PlaySound(None,winsound.SND_PURGE)
        winsound.PlaySound("alert.wav",winsound.SND_ASYNC|winsound.SND_LOOP)
        alerting=1


def restore_window(hwnd):
    try:
        win32gui.ShowWindow(hwnd,1)
        win32gui.SetForegroundWindow(hwnd)
    except:
        print("can't find",hwnd)

def on_mouse(event, x, y, flags, param):
    global mouseX, mouseY
    #switch window theo vị trí mouse
    if event == cv.EVENT_LBUTTONDOWN:
        for window in windows:
            i = windows.index(window)
            if (rec[1]) * i < x < (rec[1])*(i+1):
               restore_window(window.getHwnd())
    if event == cv.EVENT_RBUTTONDOWN:
        winsound.PlaySound(None,winsound.SND_PURGE)

    if event == cv.EVENT_RBUTTONDBLCLK:
        #bật tắt detect theo kiểu toggle
        #vì dùng thư viện playsound dạng loop nên cần tắt bằng cái Playsound(None,flags)
        if detect:
            set_detect(False)
            winsound.PlaySound(None,winsound.SND_PURGE)
            winsound.PlaySound("stop.wav",winsound.SND_ASYNC)
        else:
            set_detect(True)
            winsound.PlaySound(None,winsound.SND_PURGE)
            winsound.PlaySound("start.wav",winsound.SND_ASYNC)
    #reload lại list và window
    if event == cv.EVENT_MBUTTONDOWN:
        cv.resizeWindow(windowname,rec[1]*len(list_EVE_HWND),rec[0])
        load_EVE_windows(sort_EVE_HWND_by_config(read_configs(),get_all_EVE_window_HWND()))

def main_thread():
    while (cv.getWindowProperty(windowname, cv.WND_PROP_VISIBLE)):
        #list chứa img sẽ cap
        img_array = []
        # loop_time = time.time()
        # print (loop_time)
        #get hwnd của window dg focus
        curWin = win32gui.GetForegroundWindow()
        for window in windows: 
            if win32gui.IsWindow(window.getHwnd()): #window có tồn tại hay không
                if window.getHwnd() == curWin:
                    img= window.cap(rec[0],rec[1],rec[2],rec[3])
                    if len(img): #nếu độ dài img >0
                        #khi cv vẽ rect sẽ tính từ 0 nên cần -1 
                        cv.rectangle(img, (0, img.shape[0]-1), (img.shape[1]-1, 0), (0,255,0), cv.MARKER_CROSS, 1)
                    img_array.append(img)
                else:
                    img= window.cap(rec[0],rec[1],rec[2],rec[3])
                    if len(img):
                        cv.rectangle(img, (0, img.shape[0]-1), (img.shape[1]-1, 0), (100,100,100), cv.MARKER_CROSS, 1)
                    img_array.append(img)
        if detect:
            global alerting
            if img_array:
                #gộp ảnh lại với nhau, theo hàng ngang
                all_img = np.concatenate(img_array, axis=1) 
                t1= red.find(all_img, 0.7)
                t2= org.find(all_img, 0.7)
                t3= neu.find(all_img, 0.78)
                #ảnh cần tìm.find >>return số điểm đã phát hiện
                if t1+t2+t3>0:
                    alert(t1+t2+t3)
                else:
                    if alerting:
                        winsound.PlaySound(None,winsound.SND_PURGE)
                        alerting=False
                # print(t1+t2+t3)
                cv.imshow(windowname, all_img) #show ảnh 
        else:
            if img_array:
                all_img = np.concatenate(img_array, axis=1) #gộp ảnh lại với nhau, theo hàng ngang
                cv.imshow(windowname, all_img) #show ảnh
        cv.waitKey(1)

#detect on/of , cảnh báo on/off
detect = False
alerting=False
red = org = neu = None

#tạo window, set property ontop, set mouse listener
windowname = 'Watch Krab'
cv.namedWindow(windowname,cv.WINDOW_FREERATIO )
cv.setWindowProperty(windowname, cv.WND_PROP_TOPMOST, 1)
cv.setMouseCallback(windowname, on_mouse)

#window đang forcus hiện tại
curWin = None
#lấy list window HWND
list_EVE_HWND=get_all_EVE_window_HWND()
#khởi tạo window cap từ litt HWND
windows =load_EVE_windows(list_EVE_HWND)
print('list HWND is:',list_EVE_HWND)
print('list window eve is:',windows)

#chiề cao, chiều rộng vùng cần set , 1568 là offset chiều rộng, 180 là offset chiều cao
rec=[400,40,1568,180]
print('capturing at:',rec)

t= Thread(target=main_thread())
t.start()
t.join()

