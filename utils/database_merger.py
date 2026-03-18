import sqlite3
from typing import Dict, List, Tuple, Optional, Callable
import threading

class DatabaseMerger:
    """
    أداة مساعدة لدمج قواعد البيانات مع الاحتفاظ بالبيانات الجديدة
    """
    
    # تعريف الجداول ومفاتيحها الأساسية وسلوك الدمج
    TABLES_CONFIG = {
        "customers": {
            "primary_key": "id",
            "conflict_resolution": "ignore",  # تجاهل إذا موجود (الاحتفاظ بالجديد)
            "order_by": "id",
            "required_tables": []  # جداول يجب وجودها قبل هذا الجدول
        },
        "suppliers": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": []
        },
        "category": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": []
        },
        "products": {
            "primary_key": "id",
            "conflict_resolution": "merge_quantity",  # دمج الكميات للمنتجات المكررة
            "order_by": "id",
            "required_tables": ["category", "suppliers"]
        },
        "sales": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": ["customers"]
        },
        "sale_items": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": ["sales", "products"]
        },
        "stock_movements": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": ["products"]
        },
        "users": {
            "primary_key": "id",
            "conflict_resolution": "ignore",
            "order_by": "id",
            "required_tables": []
        }
    }
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.statistics = {
            "tables_processed": 0,
            "rows_inserted": 0,
            "rows_merged": 0,
            "rows_skipped": 0,
            "errors": []
        }
    
    def update_progress(self, message: str, percent: float = None):
        """تحديث التقدم"""
        if self.progress_callback:
            self.progress_callback(message, percent)
        else:
            print(f"{message} - {percent if percent else ''}%")
    
    def get_table_schema(self, cursor: sqlite3.Cursor, table_name: str) -> Dict:
        """الحصول على هيكل الجدول"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        return {
            "name": table_name,
            "columns": [col[1] for col in columns],
            "types": [col[2] for col in columns],
            "primary_key": next((col[1] for col in columns if col[5] == 1), "id")
        }
    
    def get_all_tables(self, cursor: sqlite3.Cursor) -> List[str]:
        """الحصول على جميع الجداول في قاعدة البيانات"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        # استثناء جداول النظام
        return [t for t in tables if not t.startswith('sqlite_') and t != 'sqlite_sequence']
    
    def table_exists(self, cursor: sqlite3.Cursor, table_name: str) -> bool:
        """التحقق من وجود جدول"""
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def ensure_tables_exist(self, source_cursor: sqlite3.Cursor, target_cursor: sqlite3.Cursor):
        """التأكد من وجود جميع الجداول في قاعدة البيانات الهدف"""
        source_tables = self.get_all_tables(source_cursor)
        
        for table_name in source_tables:
            if not self.table_exists(target_cursor, table_name):
                # الحصول على هيكل الجدول من المصدر
                source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                create_sql = source_cursor.fetchone()[0]
                
                # إنشاء الجدول في الهدف
                target_cursor.execute(create_sql)
                self.update_progress(f"تم إنشاء جدول {table_name}", None)
    
    def merge_row(self, 
                  table_name: str,
                  row: Tuple,
                  columns: List[str],
                  target_cursor: sqlite3.Cursor,
                  config: Dict) -> bool:
        """دمج صف واحد مع معالجة التعارضات"""
        
        primary_key = config.get("primary_key", "id")
        conflict_resolution = config.get("conflict_resolution", "ignore")
        
        try:
            # البحث عن المفتاح الأساسي
            if primary_key in columns:
                pk_index = columns.index(primary_key)
                pk_value = row[pk_index]
                
                # التحقق من وجود السجل
                target_cursor.execute(
                    f"SELECT {primary_key} FROM {table_name} WHERE {primary_key}=?",
                    (pk_value,)
                )
                existing = target_cursor.fetchone()
                
                if existing:
                    # يوجد تعارض
                    if conflict_resolution == "ignore":
                        self.statistics["rows_skipped"] += 1
                        return False
                    
                    elif conflict_resolution == "merge_quantity" and table_name == "products":
                        # تجاهل المنتج المكرر بالكامل
                        self.statistics["rows_skipped"] += 1
                        return False
            
            # إدراج سجل جديد
            placeholders = ','.join(['?' for _ in columns])
            columns_str = ','.join(columns)
            
            target_cursor.execute(
                f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                row
            )
            
            if target_cursor.rowcount > 0:
                self.statistics["rows_inserted"] += 1
                return True
            else:
                self.statistics["rows_skipped"] += 1
                return False
                
        except Exception as e:
            self.statistics["errors"].append(f"خطأ في جدول {table_name}: {str(e)}")
            return False
    
    def merge_database(self, source_path: str, target_path: str) -> Tuple[bool, str, Dict]:
        """
        دمج قاعدة البيانات المصدر مع الهدف
        
        Returns:
            Tuple[bool, str, Dict]: (نجاح/فشل, رسالة, إحصائيات)
        """
        source_conn = None
        target_conn = None
        
        try:
            self.update_progress("جاري فتح قواعد البيانات...", 5)
            
            # الاتصال بقاعدة البيانات الهدف
            target_conn = sqlite3.connect(target_path)
            target_conn.execute("PRAGMA foreign_keys = OFF")  # تعطيل المفاتيح الخارجية مؤقتاً
            target_cursor = target_conn.cursor()
            
            # الاتصال بقاعدة البيانات المصدر
            source_conn = sqlite3.connect(source_path)
            source_cursor = source_conn.cursor()
            
            # الحصول على جميع الجداول من المصدر
            source_tables = self.get_all_tables(source_cursor)
            
            if not source_tables:
                return False, "لا توجد جداول في قاعدة البيانات المصدر", self.statistics
            
            self.update_progress(f"تم العثور على {len(source_tables)} جدول", 10)
            
            # التأكد من وجود الجداول في الهدف
            self.ensure_tables_exist(source_cursor, target_cursor)
            
            # ترتيب الجداول حسب التبعيات
            ordered_tables = self.order_tables_by_dependencies(source_tables)
            
            total_tables = len(ordered_tables)
            processed_tables = 0
            
            # دمج كل جدول
            for table_name in ordered_tables:
                if table_name not in source_tables:
                    continue
                    
                processed_tables += 1
                progress_percent = 10 + (processed_tables / total_tables * 80)
                
                self.update_progress(
                    f"جاري دمج جدول {table_name}...", 
                    progress_percent
                )
                
                # الحصول على هيكل الجدول
                schema = self.get_table_schema(source_cursor, table_name)
                config = self.TABLES_CONFIG.get(table_name, {
                    "primary_key": schema["primary_key"],
                    "conflict_resolution": "ignore"
                })
                
                # الحصول على البيانات من المصدر
                source_cursor.execute(f"SELECT * FROM {table_name}")
                rows = source_cursor.fetchall()
                
                if not rows:
                    continue
                
                # دمج كل صف
                table_inserts = 0
                for row in rows:
                    if self.merge_row(table_name, row, schema["columns"], target_cursor, config):
                        table_inserts += 1
                
                # حفظ التغييرات لكل جدول
                target_conn.commit()
                
                self.statistics["tables_processed"] += 1
            
            # إعادة تفعيل المفاتيح الخارجية
            target_conn.execute("PRAGMA foreign_keys = ON")
            
            # تحديث تسلسل المعرفات
            self.update_sequences(target_cursor)
            target_conn.commit()
            
            self.update_progress("اكتمل الدمج بنجاح!", 100)
            
            return True, "تم دمج البيانات بنجاح", self.statistics
            
        except Exception as e:
            if target_conn:
                target_conn.rollback()
            self.statistics["errors"].append(str(e))
            return False, f"فشل الدمج: {str(e)}", self.statistics
            
        finally:
            if source_conn:
                source_conn.close()
            if target_conn:
                target_conn.close()
    
    def order_tables_by_dependencies(self, tables: List[str]) -> List[str]:
        """ترتيب الجداول حسب التبعيات"""
        ordered = []
        remaining = set(tables)
        
        while remaining:
            added = False
            for table in list(remaining):
                config = self.TABLES_CONFIG.get(table, {"required_tables": []})
                required = set(config.get("required_tables", []))
                
                if required.issubset(set(ordered)):
                    ordered.append(table)
                    remaining.remove(table)
                    added = True
            
            if not added and remaining:
                # إذا لم نتمكن من إضافة أي جدول، نضيف الباقي كما هو
                ordered.extend(remaining)
                break
        
        return ordered
    
    def update_sequences(self, cursor: sqlite3.Cursor):
        """تحديث تسلسل المعرفات التلقائية"""
        try:
            cursor.execute("SELECT name FROM sqlite_sequence")
            sequences = cursor.fetchall()
            
            for (seq_name,) in sequences:
                cursor.execute(f"SELECT MAX(id) FROM {seq_name}")
                max_id = cursor.fetchone()[0]
                if max_id:
                    cursor.execute(
                        f"UPDATE sqlite_sequence SET seq=? WHERE name=?",
                        (max_id, seq_name)
                    )
        except:
            pass  # تجاهل الأخطاء في تحديث التسلسل

def merge_databases_with_thread(source_path: str, target_path: str, 
                                 progress_callback: Callable = None,
                                 complete_callback: Callable = None):
    """
    دمج قواعد البيانات في thread منفصل
    """
    def run_merge():
        merger = DatabaseMerger(progress_callback)
        success, message, stats = merger.merge_database(source_path, target_path)
        
        if complete_callback:
            complete_callback(success, message, stats)
    
    thread = threading.Thread(target=run_merge)
    thread.daemon = True
    thread.start()
    return thread