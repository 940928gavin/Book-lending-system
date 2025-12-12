# -*- coding: utf-8 -*-

###########################################################################
## main.py - 應用程式啟動主程式碼
###########################################################################

import wx
from app_logic import MainFrame

class MyApp(wx.App):
    def OnInit(self):
        # 創建主畫面實例
        main_frame = MainFrame(None)

        # 將主畫面設定為頂級視窗
        self.SetTopWindow(main_frame)

        # 顯示主畫面
        main_frame.Show(True)

        return True

if __name__ == '__main__':
    # 運行應用程式
    app = MyApp(0)
    app.MainLoop()