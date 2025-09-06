
import sqlite3
import json

DATABASE = 'sfactory_assessment.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_assessment_data_as_json():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    
    assessment_structure = []
    for category in categories:
        category_dict = dict(category)
        
        items = conn.execute('SELECT * FROM evaluation_items WHERE category_id = ?', (category['id'],)).fetchall()
        
        items_list = []
        for item in items:
            item_dict = dict(item)
            
            levels = conn.execute('SELECT * FROM maturity_levels WHERE item_id = ? ORDER BY level', (item['id'],)).fetchall()
            item_dict['levels'] = [dict(level) for level in levels]
            items_list.append(item_dict)
            
        category_dict['items'] = items_list
        assessment_structure.append(category_dict)
        
    conn.close()
    return json.dumps(assessment_structure, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    print(get_assessment_data_as_json())
