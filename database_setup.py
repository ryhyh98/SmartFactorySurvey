
import sqlite3
import csv

# 데이터베이스 연결
conn = sqlite3.connect('sfactory_assessment.db')
cur = conn.cursor()

# 테이블 생성
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    score INTEGER NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS evaluation_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    item_no TEXT,
    name TEXT,
    level_step INTEGER,
    base_score REAL,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS maturity_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    level INTEGER,
    score REAL,
    description TEXT,
    FOREIGN KEY (item_id) REFERENCES evaluation_items (id)
)
""")

# CSV 파일 읽어서 데이터 삽입
with open('스마트팩토리수준진단_input.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    
    category_cache = {}
    
    for row in reader:
        # Category 처리
        category_name = row['대분류']
        category_score = int(row['배점'])
        if category_name not in category_cache:
            cur.execute("INSERT OR IGNORE INTO categories (name, score) VALUES (?, ?)", (category_name, category_score))
            conn.commit()
            cur.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category_id = cur.fetchone()[0]
            category_cache[category_name] = category_id
        else:
            category_id = category_cache[category_name]

        # Evaluation Item 처리
        cur.execute("""
        INSERT INTO evaluation_items (category_id, item_no, name, level_step, base_score)
        VALUES (?, ?, ?, ?, ?)
        """, (
            category_id,
            row['No2'],
            row['평가항목'],
            int(row['세부수준']),
            float(row['세부 항목별 배점'])
        ))
        conn.commit()
        item_id = cur.lastrowid

        # Maturity Levels 처리
        for i in range(6):
            level = i
            score = float(row[f'Level{i}'])
            description = row[f'select{i}']
            cur.execute("""
            INSERT INTO maturity_levels (item_id, level, score, description)
            VALUES (?, ?, ?, ?)
            """, (item_id, level, score, description))

conn.commit()
conn.close()

print("데이터베이스 설정 및 데이터 삽입이 완료되었습니다.")
