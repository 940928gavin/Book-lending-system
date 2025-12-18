# -*- coding: utf-8 -*-
import wx
from gui import * # 匯入 gui.py 中所有的 Base 類別
from db_manager import DBManager

# =======================================================================
# 中央管理器：MainFrame
# =======================================================================
class MainFrame(MainFrameBase):
    def __init__(self, parent):
        MainFrameBase.__init__(self, parent)
        self.db = DBManager()
        self.current_user = None  # 儲存登入讀者的 ID
        self.frames = {}

        # 確保搜尋按鈕綁定 (假設按鈕名為 query_button，若不同請修改)
        if hasattr(self, 'query_button'):
            self.query_button.Bind(wx.EVT_BUTTON, self.OnQueryButtonClick)

    def ShowMainFrame(self):
        self.Show(True)

    def GetFrame(self, name, FrameClass):
        if name not in self.frames or self.frames[name] is None:
            self.frames[name] = FrameClass(self)
        return self.frames[name]

    # --- 搜尋書籍功能 ---
    def OnQueryButtonClick(self, event):
        query = self.book_search_input.GetValue().strip()
        print(f"🔍 正在搜尋書籍: {query}")
        
        book = self.db.get_book_by_title(query)
        if book:
            print(f"✅ 找到書籍: {book}")
            self.Hide()
            detail = self.GetFrame('BookDetail', BookDetailFrame)
            detail.UpdateInfo(book) # 將資料庫數據傳入詳情頁
            detail.Show()
        else:
            print("❌ 找不到該書籍")
            wx.MessageBox(f"找不到關於 '{query}' 的書籍。\n請試試搜尋: Python", "查無此書")

    def OnLoginButtonClick(self, event):
        self.Hide()
        self.GetFrame('IdentityChoice', IdentityChoiceFrame).Show()

    def OnViewBorrowRecord(self, event):
        if not self.current_user:
            wx.MessageBox("請先登入讀者帳號！", "提示")
            return
        self.Hide()
        self.GetFrame('BorrowRecord', BorrowRecordFrame).Show()

# =======================================================================
# 讀者流程類別
# =======================================================================

class IdentityChoiceFrame(IdentityChoiceFrameBase):
    def __init__(self, parent):
        IdentityChoiceFrameBase.__init__(self, parent)
        self.main_frame = parent
    def OnReaderLogin(self, event):
        self.Hide(); self.main_frame.GetFrame('ReaderLogin', ReaderLoginForm).Show()
    def OnAdminLogin(self, event):
        self.Hide(); self.main_frame.GetFrame('AdminLogin', AdminLoginForm).Show()
    def OnClose(self, event):
        self.Hide(); self.main_frame.ShowMainFrame()

class ReaderLoginForm(ReaderLoginFormBase):
    def __init__(self, parent):
        ReaderLoginFormBase.__init__(self, parent)
        self.main_frame = parent
    def OnRegisterClick(self, event):
        self.Hide(); self.main_frame.GetFrame('Register', RegisterForm).Show()
    def OnLoginSubmit(self, event):
        rid = self.account_input.GetValue()
        user = self.main_frame.db.get_reader_by_id(rid)
        if user:
            self.main_frame.current_user = rid
            wx.MessageBox(f"登入成功！歡迎回來, {user[1]}", "提示")
            self.Hide(); self.main_frame.ShowMainFrame()
        else:
            wx.MessageBox("帳號錯誤或不存在，請先註冊。", "登入失敗")

class RegisterForm(RegisterFormBase):
    def __init__(self, parent):
        RegisterFormBase.__init__(self, parent)
        self.main_frame = parent
    def OnRegisterSubmit(self, event):
        rid = self.account_name_input.GetValue()
        email = self.email_input.GetValue()
        pwd = self.password_input.GetValue()
        if self.main_frame.db.register_reader(rid, rid, email, pwd):
            wx.MessageBox(f"註冊成功！您的 ID 為: {rid}", "提示")
            self.Hide(); self.main_frame.ShowMainFrame()
        else:
            wx.MessageBox("註冊失敗，ID 可能已被佔用。", "錯誤")

class BookDetailFrame(BookDetailFrameBase):
    def __init__(self, parent):
        BookDetailFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.current_book_data = None  # 儲存當前書籍資料

    def UpdateInfo(self, data):
        """
        data 內容格式: (BookID, Title, Author, ISBN, Available)
        索引對應:      [0]     [1]    [2]     [3]    [4]
        """
        self.current_book_data = data
        print(f"📖 正在更新介面元件，資料: {data}")

        # --- 根據你提供的 gui.py 變數名稱進行對接 ---
        # data[1] 是 Title, data[2] 是 Author... 以此類推
        
        # 書名
        if hasattr(self, 'm_staticText4'):
            self.m_staticText4.SetLabel(f"書名：{data[1]}")
            
        # 作者
        if hasattr(self, 'm_staticText41'):
            self.m_staticText41.SetLabel(f"作者：{data[2]}")
            
        # 書號 (BookID)
        if hasattr(self, 'm_staticText42'):
            self.m_staticText42.SetLabel(f"書號：{data[0]}")
            
        # ISBN
        if hasattr(self, 'm_staticText43'):
            self.m_staticText43.SetLabel(f"ISBN：{data[3]}")
            
        # 狀態 (庫存)
        if hasattr(self, 'm_staticText44'):
            status = "可借閱" if data[4] > 0 else "已借光"
            self.m_staticText44.SetLabel(f"狀態：{status} (剩餘 {data[4]} 本)")

        # 重新佈局，確保文字不會被遮擋
        self.Layout()

    def OnBorrowClick(self, event):
        """處理借閱按鈕點擊"""
        if not self.main_frame.current_user:
            wx.MessageBox("請先登入讀者帳號再進行借閱！", "提示")
            return

        if self.current_book_data:
            book_id = self.current_book_data[0]
            # 呼叫資料庫執行借閱
            if self.main_frame.db.borrow_book(self.main_frame.current_user, book_id):
                wx.MessageBox(f"《{self.current_book_data[1]}》借閱成功！", "通知")
                self.Hide()
                self.main_frame.ShowMainFrame()
            else:
                wx.MessageBox("借閱失敗：可能目前無庫存。", "提示")

class BorrowRecordFrame(BorrowRecordFrameBase):
    def __init__(self, parent):
        BorrowRecordFrameBase.__init__(self, parent)
        self.main_frame = parent
        self.Bind(wx.EVT_SHOW, self.OnShow)

    def OnShow(self, event):
        if event.IsShown() and self.main_frame.current_user:
            history = self.main_frame.db.get_borrow_history(self.main_frame.current_user)
            if history and hasattr(self, 'm_staticText6'):
                h = history[-1]
                self.m_staticText6.SetLabel(f"最新紀錄: {h[0]} (借閱日: {h[1]})")
        event.Skip()

    def OnBackClick(self, event):
        self.Hide(); self.main_frame.ShowMainFrame()

# =======================================================================
# 管理員流程類別
# =======================================================================

class AdminLoginForm(AdminLoginFormBase):
    def __init__(self, parent):
        AdminLoginFormBase.__init__(self, parent)
        self.main_frame = parent
    def OnAdminLoginSubmit(self, event):
        acc = self.account_input.GetValue()
        pwd = self.password_input.GetValue()
        if acc == 'admin' and pwd == 'admin123':
            self.Hide()
            self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()
        else:
            wx.MessageBox("管理員密碼錯誤。", "錯誤")

class AdminPanelFrame(AdminPanelFrameBase):
    def __init__(self, parent):
        AdminPanelFrameBase.__init__(self, parent)
        self.main_frame = parent
    def OnViewReaders(self, event):
        self.Hide()
        self.main_frame.GetFrame('ReaderList', ReaderListFrame).Show()
    def OnLogout(self, event):
        self.Hide(); self.main_frame.ShowMainFrame()

class ReaderListFrame(ReaderListFrameBase):
    def __init__(self, parent):
        ReaderListFrameBase.__init__(self, parent)
        self.main_frame = parent
        
        # 綁定顯示事件，確保每次切換到這畫面都會刷新列表
        self.Bind(wx.EVT_SHOW, self.OnShow)

    def OnShow(self, event):
        """當視窗顯示時觸發，從資料庫撈取資料填入表格"""
        if event.IsShown():
            print("📊 管理員正在刷新讀者清單表格...")
            self.RefreshReaderTable()
        event.Skip()

    def RefreshReaderTable(self):
        """清除舊資料並載入資料庫中所有讀者"""
        # 1. 先清空 ListCtrl 中的所有項目
        self.reader_list_ctrl.DeleteAllItems()
        
        # 2. 從資料庫獲取所有讀者資料
        # 資料格式: [(ID1, Name1, Email1, Credit1), (ID2, Name2, Email2, Credit2), ...]
        readers = self.main_frame.db.get_all_readers()
        
        if not readers:
            print("⚠️ 資料庫目前沒有任何讀者紀錄。")
            return

        # 3. 循環每一筆資料並填入表格
        for i, r in enumerate(readers):
            # InsertItem 建立新的一列，並填入第一欄 (讀者編號)
            index = self.reader_list_ctrl.InsertItem(i, str(r[0]))
            
            # SetItem 填入後續欄位 (姓名、Email、信用分)
            self.reader_list_ctrl.SetItem(index, 1, str(r[1])) # 姓名
            self.reader_list_ctrl.SetItem(index, 2, str(r[2])) # E-Mail
            self.reader_list_ctrl.SetItem(index, 3, str(r[3])) # 信用分
            
        print(f"✅ 已成功載入 {len(readers)} 筆讀者資料。")
        self.Layout()

    def OnBackClick(self, event):
        """處理返回按鈕，回到管理面板"""
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

    def OnEditReader(self, event):
        """處理修改資料按鈕 (可選)"""
        selected = self.reader_list_ctrl.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("請先從列表中選擇一位讀者！", "提示")
            return
        
        # 獲取選中讀者的 ID
        reader_id = self.reader_list_ctrl.GetItemText(selected, 0)
        wx.MessageBox(f"準備修改讀者 {reader_id} 的資料 (功能開發中)", "提示")

    def OnBackClick(self, event):
        """返回管理員主面板"""
        self.Hide()
        self.main_frame.GetFrame('AdminPanel', AdminPanelFrame).Show()

# =======================================================================
# 備用類別：防止未定義錯誤
# =======================================================================
class BorrowResultFrame(BorrowResultFrameBase): pass
class ReserveResultFrame(ReserveResultFrameBase): pass
class AdminBookDetail(AdminBookDetailBase): pass
class EditBookForm(EditBookFormBase): pass
class EditReaderForm(EditReaderFormBase): pass
