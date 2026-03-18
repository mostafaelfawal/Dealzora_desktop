def alter_column_type(cur, con, table_name, column_name, new_type):
    """
    دالة عامة لتغيير نوع عمود في أي جدول SQLite
    تتأكد أولًا إذا كان العمود من النوع الجديد لتجنب إعادة التعديل
    """
    # جلب معلومات الأعمدة
    cur.execute(f"PRAGMA table_info({table_name})")
    columns_info = cur.fetchall()

    # التأكد إذا العمود موجود والتحقق من نوعه الحالي
    qty_type = None
    for col in columns_info:
        _, name, col_type, notnull, _, pk = col
        if name == column_name:
            qty_type = col_type
            break

    if qty_type is None:
        raise ValueError(f"العمود {column_name} غير موجود في {table_name}")

    # إذا النوع الحالي يساوي النوع المطلوب، لا نفعل أي شيء
    if qty_type.upper() == new_type.upper():
        return

    # إنشاء تعريف الأعمدة للجدول المؤقت مع تعديل النوع المطلوب
    new_columns_def = []
    columns = [col[1] for col in columns_info]
    for col in columns_info:
        _, name, col_type, notnull, _, pk = col
        if name == column_name:
            col_type = new_type

        col_def_parts = [name, col_type]
        if pk:
            col_def_parts.append("PRIMARY KEY")
        elif notnull:
            col_def_parts.append("NOT NULL")
        # تجاهل DEFAULT لتجنب syntax errors
        col_def = " ".join(col_def_parts)
        new_columns_def.append(col_def)

    temp_table = f"{table_name}_temp"
    cur.execute(f"CREATE TABLE {temp_table} ({', '.join(new_columns_def)})")

    columns_str = ", ".join(columns)
    cur.execute(
        f"INSERT INTO {temp_table} ({columns_str}) SELECT {columns_str} FROM {table_name}"
    )

    cur.execute(f"DROP TABLE {table_name}")
    cur.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")

    con.commit()
    print(f"تم تغيير نوع العمود {column_name} في جدول {table_name} إلى {new_type}")
