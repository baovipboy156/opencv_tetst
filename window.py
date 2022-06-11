import numpy as np
import win32gui, win32ui, win32con
class window():
	hwnd=None 		#hwnd của window
	h=w=0			#chiều cao,chiều rộng của ảnh cần cap
	x=y=0			#toạ độ ảnh cần cap
	windowName=None	#tên của window
	wDC=dcObj=cDC=dataBitMap=None
	def __init__(self,hwnd):
		self.hwnd = hwnd
		self.windowName= win32gui.GetWindowText(hwnd)
		self.wDC = win32gui.GetWindowDC(hwnd)
		self.dcObj = win32ui.CreateDCFromHandle(self.wDC)
		self.cDC = self.dcObj.CreateCompatibleDC()
		print('initing window handler for',self.windowName)
	def cap(self,h,w,x,y):
		if win32gui.IsWindowVisible(self.hwnd):
			if not self.dataBitMap:
				print("Creating dataBitMap for",self.windowName)
				self.dataBitMap = win32ui.CreateBitmap()
				self.dataBitMap.CreateCompatibleBitmap(self.dcObj, w, h)
			if self.dataBitMap:
				self.cDC.SelectObject(self.dataBitMap)
				self.cDC.BitBlt((0, 0), (w,h), self.dcObj, (x,y), win32con.SRCCOPY)
				img=np.fromstring(self.dataBitMap.GetBitmapBits(True), dtype='uint8').reshape(h,w,4)
				img = img[...,:3]
			return np.ascontiguousarray(img)
		return 0
	def close(self):
		try:
			win32gui.DeleteObject(self.dataBitMap.GetHandle())
			self.cDC.DeleteDC()
			self.dcObj.DeleteDC()
			win32gui.ReleaseDC(self.hwnd, self.wDC)
			print('closed window handler')
		except:
			print("can't close window handler")
	def getHwnd(self):
		return self.hwnd