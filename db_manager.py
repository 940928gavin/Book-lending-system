# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime, timedelta

# 1. 先設定路徑 (在類別外面)
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'library.db')

class DBManager:
    def __init__(self, db_name=DB_PATH):
        self.db_name = db_name
        try:
            # 2. 建立連線 (在方法裡面，可以使用 self)
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.initialize_db()
            
            # 這裡的 self 是正確的
            print(f"✅ 資料庫連線成功！檔案位置: {os.path.abspath(self.db_name)}")
            
            # 測試是否真的有書
            self.cursor.execute("SELECT Title FROM Books")
            print(f"📚 目前資料庫內的書單: {self.cursor.fetchall()}")
            
        except Exception as e:
            print(f"❌ 資料庫連線失敗: {e}")

    def initialize_db(self):
        """建立表格並初始化資料"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Books (BookID TEXT PRIMARY KEY, Title TEXT, Author TEXT, ISBN TEXT, Available INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Readers (ReaderID TEXT PRIMARY KEY, Name TEXT, Email TEXT, Password TEXT, Credit INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Borrows (BorrowID INTEGER PRIMARY KEY AUTOINCREMENT, BookID TEXT, ReaderID TEXT, BorrowDate TEXT, DueDate TEXT, ReturnDate TEXT)")
        self.conn.commit()

        # 檢查並插入初始資料
        self.cursor.execute("SELECT COUNT(*) FROM Books")
        if self.cursor.fetchone()[0] == 0:
            books = [
                ('B001', 'Python 入門指南', '張大文', '978-001', 5),
                ('B002', 'wxPython 介面設計', '李小美', '978-002', 2)
            ]
            self.cursor.executemany("INSERT INTO Books VALUES (?,?,?,?,?)", books)
            self.cursor.execute("INSERT OR IGNORE INTO Readers VALUES ('admin', '管理員', 'admin@mail.com', 'admin123', 999)")
            self.conn.commit()

    # ... (後續的 get_book_by_title 等方法請確保都在 class 內)

        # 初始化書籍與管理員
        self.cursor.execute("SELECT COUNT(*) FROM Books")
        if self.cursor.fetchone()[0] == 0:
            books = [
                ('B001', 'Python 入門指南', '張大文', '978-001', 5),
                ('B002', 'wxPython 介面設計', '李小美', '978-002', 2),
                ('B003', '資料庫實務', '王老五', '978-003', 3)
            ]
            self.cursor.executemany("INSERT INTO Books VALUES (?,?,?,?,?)", books)
            self.cursor.execute("INSERT OR IGNORE INTO Readers VALUES ('admin', '管理員', 'admin@mail.com', 'admin123', 999)")
            self.conn.commit()

    def get_book_by_title(self, title):
        self.cursor.execute("SELECT * FROM Books WHERE Title LIKE ?", ('%' + title + '%',))
        return self.cursor.fetchone()

    def register_reader(self, rid, name, email, pwd):
        try:
            self.cursor.execute("INSERT INTO Readers VALUES (?, ?, ?, ?, ?)", (rid, name, email, pwd, 100))
            self.conn.commit()
            return True
        except: return False

    def get_all_readers(self):
        self.cursor.execute("SELECT ReaderID, Name, Email, Credit FROM Readers WHERE ReaderID != 'admin'")
        return self.cursor.fetchall()

    def get_reader_by_id(self, rid):
        self.cursor.execute("SELECT * FROM Readers WHERE ReaderID = ?", (rid,))
        return self.cursor.fetchone()

    def borrow_book(self, rid, bid):
        """
        rid: 讀者 ID, bid: 書籍 ID
        """
        # 1. 檢查讀者是否存在
        self.cursor.execute("SELECT * FROM Readers WHERE ReaderID = ?", (rid,))
        if not self.cursor.fetchone():
            print("❌ 借閱失敗：讀者帳號無效")
            return False

        # 2. 檢查書籍庫存
        self.cursor.execute("SELECT Available FROM Books WHERE BookID = ?", (bid,))
        res = self.cursor.fetchone()
        
        if res and res[0] > 0:
            try:
                # 3. 扣除庫存
                self.cursor.execute("UPDATE Books SET Available = Available - 1 WHERE BookID = ?", (bid,))
                
                # 4. 計算日期
                b_date = datetime.now().strftime("%Y-%m-%d")
                # 借期 14 天
                d_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                
                # 5. 新增借閱紀錄 (對應 Borrows 的 6 個欄位: BorrowID(自動), BookID, ReaderID, BorrowDate, DueDate, ReturnDate)
                # 我們不填寫 BorrowID (自動增加) 和 ReturnDate (目前為 None)
                sql = "INSERT INTO Borrows (BookID, ReaderID, BorrowDate, DueDate, ReturnDate) VALUES (?, ?, ?, ?, ?)"
                self.cursor.execute(sql, (bid, rid, b_date, d_date, None))
                
                self.conn.commit()
                print(f"✅ 借閱成功！書籍 {bid} 已借給讀者 {rid}")
                return True
            except Exception as e:
                # 如果發生錯誤，將印在 Terminal (黑框) 給你看
                print(f"❌ 借閱資料庫操作失敗，錯誤原因: {e}")
                self.conn.rollback()
                return False
        else:
            print("❌ 借閱失敗：該書已無庫存或不存在")
            return False

    def get_borrow_history(self, rid):
        self.cursor.execute("""
            SELECT Books.Title, Borrows.BorrowDate, Borrows.DueDate FROM Borrows 
            JOIN Books ON Borrows.BookID = Books.BookID WHERE Borrows.ReaderID = ?
        """, (rid,))
        return self.cursor.fetchall()

    def close(self): self.conn.close()
