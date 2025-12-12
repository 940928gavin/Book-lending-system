# -*- coding: utf-8 -*-

###########################################################################
## app_logic.py - 應用程式邏輯與事件處理 (整合 15 個畫面, 引用路徑已修正)
###########################################################################

import wx
from gui import (
    MainFrameBase, QueryBookFrameBase, IdentityChoiceFrameBase,
    ReaderLoginFormBase, RegisterFormBase, BorrowRecordFrameBase,
    BookDetailFrameBase, BorrowResultFrameBase, ReserveResultFrameBase,
    AdminLoginFormBase, AdminPanelFrameBase, AdminBookDetailBase,
    EditBookFormBase, ReaderListFrameBase, EditReaderFormBase
)

# ----------------------------------------------------------------------
# 中央管理器：管理所有畫面實例
# ----------------------------------------------------------------------
class MainFrame(MainFrameBase):
    def __init__(self, parent):
        MainFrameBase.__init__(self, parent)

        self.frames = {}
        # 初始化所有潛在的畫面實例佔位符 (簡化寫法，也可以在 GetFrame 中動態創建)
        self.frames['IdentityChoice'] = None
        self.frames['BorrowRecord'] = None
        self.frames['BookDetail'] = None
        self.frames['AdminPanel'] = None # 管理員主控台
        self.frames['AdminLogin'] = None
        # 註冊/登入/修改表單等通常為臨時畫面，不在 MainFrame 級別預設創建

    def ShowMainFrame(self):
        """用於其他畫面返回主畫面時呼叫"""
        self.Show(True)

    def GetFrame(self, name, FrameClass, parent=None):
        """獲取或創建指定名稱的畫面實例"""
        if name not in self.frames or self.frames[name] is None:
            # 對於需要知道 MainFrame 的子畫面，傳入 self 作為 parent
            if parent is None: parent = self 
            
            # 使用 getattr 查找是否存在 FrameClass，否則動態創建
            if name in ['AdminLogin', 'ReaderLogin', 'Register', 'BorrowResult', 'ReserveResult', 'EditBook', 'EditReader']:
                 # 臨時性表單/結果頁，不需要在 self.frames 裡永久儲存 (或可以儲存但隨時覆蓋)
                 return FrameClass(parent)
            
            self.frames[name] = FrameClass(parent)
            
        return self.frames[name]

    # --- MainFrame 事件 ---
    
    # 點擊「查詢」
    def OnQueryButtonClick(self, event):
        book_name = self.book_search_input.GetValue().strip()
        if book_name:
            self.Hide()
            # 獲取 BookDetailFrame，並傳入 MainFrame
            detail_frame = self.GetFrame('BookDetail', BookDetailFrame, parent=self)
            detail_frame.SetTitle(f"書籍資料: {book_name}")
            detail_frame.Show()
        else:
            wx.MessageBox("請輸入書籍名稱以進行查詢。", "提示", wx.OK | wx.ICON_INFORMATION)
            event.Skip()

    # 點擊「登入/出」
    def OnLoginButtonClick(self, event):
        self.Hide()
        identity_frame = self.GetFrame('IdentityChoice', IdentityChoiceFrame, parent=self)
        identity_frame.Show()

    # 點擊「查看借閱紀錄」
    def OnViewBorrowRecord(self, event):
        self.Hide()
        record_frame = self.GetFrame('BorrowRecord', BorrowRecordFrame, parent=self)
        record_frame.Show()

# ----------------------------------------------------------------------
# 畫面組 A: 讀者流程
# ----------------------------------------------------------------------
class IdentityChoiceFrame(IdentityChoiceFrameBase):
    def __init__(self, parent):
        IdentityChoiceFrameBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnReaderLogin(self, event):
        self.Hide()
        # 直接通過 main_frame 獲取下一個畫面
        reader_login_frame = self.main_frame.GetFrame('ReaderLogin', ReaderLoginForm, parent=self.main_frame)
        reader_login_frame.Show()

    def OnAdminLogin(self, event):
        self.Hide()
        # 直接通過 main_frame 獲取下一個畫面
        admin_login_frame = self.main_frame.GetFrame('AdminLogin', AdminLoginForm, parent=self.main_frame)
        admin_login_frame.Show()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()

class ReaderLoginForm(ReaderLoginFormBase):
    def __init__(self, parent):
        ReaderLoginFormBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnRegisterClick(self, event):
        self.Hide()
        register_frame = self.main_frame.GetFrame('Register', RegisterForm, parent=self.main_frame)
        register_frame.Show()

    def OnLoginSubmit(self, event):
        wx.MessageBox("讀者登入成功！", "提示", wx.OK | wx.ICON_INFORMATION)
        self.Hide()
        self.main_frame.ShowMainFrame()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class RegisterForm(RegisterFormBase):
    def __init__(self, parent):
        RegisterFormBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnRegisterSubmit(self, event):
        wx.MessageBox("註冊成功！請登入。", "提示", wx.OK | wx.ICON_INFORMATION)
        self.Hide()
        reader_login_frame = self.main_frame.GetFrame('ReaderLogin', ReaderLoginForm, parent=self.main_frame)
        reader_login_frame.Show()

    def OnClose(self, event):
        self.Hide()
        reader_login_frame = self.main_frame.GetFrame('ReaderLogin', ReaderLoginForm, parent=self.main_frame)
        reader_login_frame.Show()


class BorrowRecordFrame(BorrowRecordFrameBase):
    def __init__(self, parent):
        BorrowRecordFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnBackClick(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class BookDetailFrame(BookDetailFrameBase):
    def __init__(self, parent):
        BookDetailFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnBorrowClick(self, event):
        self.Hide()
        borrow_result = self.main_frame.GetFrame('BorrowResult', BorrowResultFrame, parent=self.main_frame)
        borrow_result.Show()

    def OnReserveClick(self, event):
        self.Hide()
        reserve_result = self.main_frame.GetFrame('ReserveResult', ReserveResultFrame, parent=self.main_frame)
        reserve_result.Show()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class BorrowResultFrame(BorrowResultFrameBase):
    def __init__(self, parent):
        BorrowResultFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class ReserveResultFrame(ReserveResultFrameBase):
    def __init__(self, parent):
        ReserveResultFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()

# ----------------------------------------------------------------------
# 畫面組 B: 管理員流程
# ----------------------------------------------------------------------
class AdminLoginForm(AdminLoginFormBase):
    def __init__(self, parent):
        AdminLoginFormBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnAdminLoginSubmit(self, event):
        is_successful = True
        if is_successful:
            wx.MessageBox("管理員登入成功！", "提示", wx.OK | wx.ICON_INFORMATION)
            self.Hide()
            admin_panel = self.main_frame.GetFrame('AdminPanel', AdminPanelFrame, parent=self.main_frame)
            admin_panel.Show()
        else:
            wx.MessageBox("帳號或密碼錯誤。", "錯誤", wx.OK | wx.ICON_ERROR)

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class AdminPanelFrame(AdminPanelFrameBase):
    def __init__(self, parent):
        AdminPanelFrameBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnQueryBook(self, event):
        self.Hide()
        # 跳轉到 AdminBookDetailFrame，並傳入 MainFrame
        book_detail = self.main_frame.GetFrame('AdminBookDetail', AdminBookDetailFrame, parent=self.main_frame)
        book_detail.Show()

    def OnViewReaders(self, event):
        self.Hide()
        # 跳轉到 ReaderListFrame，並傳入 MainFrame
        reader_list = self.main_frame.GetFrame('ReaderList', ReaderListFrame, parent=self.main_frame)
        reader_list.Show()

    def OnLogout(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.ShowMainFrame()


class AdminBookDetailFrame(AdminBookDetailBase):
    def __init__(self, parent):
        AdminBookDetailBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnEditBook(self, event):
        self.Hide()
        # 通過 main_frame 獲取 EditBookForm
        edit_form = self.main_frame.GetFrame('EditBook', EditBookForm, parent=self.main_frame)
        edit_form.Show()

    def OnDeleteBook(self, event):
        wx.MessageBox("書籍已下架！", "提示", wx.OK | wx.ICON_INFORMATION)

    def OnClose(self, event):
        self.Hide()
        # 返回 AdminPanelFrame
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()


class EditBookForm(EditBookFormBase):
    def __init__(self, parent):
        EditBookFormBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnCancel(self, event):
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

    def OnComplete(self, event):
        wx.MessageBox("書籍資料修改完成！", "提示", wx.OK | wx.ICON_INFORMATION)
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()


class ReaderListFrame(ReaderListFrameBase):
    def __init__(self, parent):
        ReaderListFrameBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnEditReader(self, event):
        self.Hide()
        # 通過 main_frame 獲取 EditReaderForm
        edit_form = self.main_frame.GetFrame('EditReader', EditReaderForm, parent=self.main_frame)
        edit_form.Show()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()


class EditReaderForm(EditReaderFormBase):
    def __init__(self, parent):
        EditReaderFormBase.__init__(self, parent)
        self.main_frame = parent # parent 必須是 MainFrame
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnCancel(self, event):
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

    def OnComplete(self, event):
        wx.MessageBox("讀者資料修改完成！", "提示", wx.OK | wx.ICON_INFORMATION)
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

    def OnClose(self, event):
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()