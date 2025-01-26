# %%
import tkinter as tk
from tkinter import messagebox
import json
import random
from datetime import datetime
import os

# %%
# تنظیمات اولیه
folder_path = "./"

# بارگیری داده‌ها از فایل‌های JSON
def load_data():
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data = {}
    for file in json_files:
        with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
            data[file] = json.load(f)
    return data

# Function to save updated data back to JSON files
def save_data(data):
    # data = load_data()
    for file_name, content in data.items():
        with open(os.path.join(folder_path, file_name), 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)


# %%
data = load_data()
# Add 'difficulty' and 'last_time_reviewed' fields to each example if they don't exist
for file_name, content in data.items():
    for example in content['examples']:
        for sub_example in example['examples']:
            if 'difficulty' not in sub_example:
                sub_example['difficulty'] = 5  # Default difficulty
            if 'last_time_reviewed' not in sub_example:
                sub_example['last_time_reviewed'] =  "2025-01-01 08:00:00"
save_data(data)


# محاسبه تعداد لغات مرور شده امروز
def get_today_reviewed_count(data):
    today = datetime.now().strftime(r"%Y-%m-%d")
    count = 0
    for file_name, content in data.items():
        for word_data in content['examples']:
            for sub_example in word_data['examples']:
                last_reviewed = sub_example.get('last_time_reviewed', "")  # مقدار پیش‌فرض: رشته خالی
                if last_reviewed.startswith(today):
                    count += 1
    return count

# %%
# ایجاد رابط کاربری
class ReviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامه مرور لغات")
        self.root.geometry("800x600")  # افزایش اندازه پنجره
        
        # تنظیم فونت‌ها
        self.font_word = ("B Nazanin", 20, "bold")  # فونت بزرگ‌تر برای واژه
        self.font_example = ("B Nazanin", 16)  # فونت بزرگ‌تر برای مثال
        self.font_meaning = ("B Nazanin", 14)  # فونت بزرگ‌تر برای معنی
        self.font_button = ("B Nazanin", 14)  # فونت بزرگ‌تر برای دکمه‌ها
        self.font_info = ("B Nazanin", 12)  # فونت برای اطلاعات اضافی
        
        self.data = load_data()
        self.today_reviewed = get_today_reviewed_count(self.data)
        self.reviewed_examples = []
        
        # ایجاد ویجت‌ها
        self.word_label = tk.Label(root, text="", font=self.font_word)
        self.word_label.pack(pady=20)
        
        self.example_label = tk.Label(root, text="", font=self.font_example, wraplength=500)
        self.example_label.pack(pady=10)
        
        self.meaning_label = tk.Label(root, text="", font=self.font_meaning, wraplength=500, fg="black")  # متن فارسی مشکی
        self.meaning_label.pack(pady=10)
        
        self.know_button = tk.Button(root, text="می‌دانم (1)", command=self.know_meaning, font=self.font_button)
        self.know_button.pack(pady=10)
        
        self.dont_know_button = tk.Button(root, text="نمی‌دانم (0)", command=self.dont_know_meaning, font=self.font_button)
        self.dont_know_button.pack(pady=10)

        self.know_well_button = tk.Button(root, text="کامل بلدم (-)", command=self.know_well, font=self.font_button)
        self.know_well_button.pack(pady=10)
        
        # پیام راهنما برای کلمه بعد
        self.next_word_label = tk.Label(root, text="برای کلمه بعد، کلید 1 را بزنید.", font=self.font_info, fg="gray")
        self.next_word_label.pack(pady=10)
        
        # نمایش تعداد بررسی‌های امروز
        self.today_reviewed_label = tk.Label(root, text="", font=self.font_info, fg="green")
        self.today_reviewed_label.pack(pady=10)
        
        # اتصال رویدادهای صفحه‌کلید
        self.root.bind("1", lambda event: self.know_meaning())
        self.root.bind("0", lambda event: self.dont_know_meaning())
        self.root.bind("-", lambda event: self.know_well())
        
        
        self.next_example()
        self.update_today_reviewed_count()  # به‌روزرسانی تعداد بررسی‌های امروز
    
    def next_example(self):
        # جمع‌آوری همه مثال‌ها
        all_examples = []
        for file_name, content in self.data.items():
            for word_data in content['examples']:
                for sub_example in word_data['examples']:
                    last_rev = datetime.strptime(sub_example ['last_time_reviewed'], r"%Y-%m-%d %H:%M:%S")                    
                    if sub_example ['difficulty'] ==0 and (datetime.now()-last_rev).total_seconds() / 3600 >2:
                        all_examples.append({
                            'file_name': file_name,
                            'word': word_data['word'],
                            'example': sub_example
                        })
        
        # محاسبه وزن‌ها برای هر مثال
        weights = []
        for example in all_examples:
            sub_example = example['example']
            difficulty_weight = 1 #sub_example.get('difficulty', 1)  # پیش‌فرض: 1
            time_weight = 1  # پیش‌فرض: 1
            weights.append(difficulty_weight * time_weight)
        
        # انتخاب یک مثال با وزن‌دهی
        selected_example = random.choices(all_examples, weights=weights, k=1)[0]
        self.current_example = selected_example['example']
        self.word_label.config(text=f"{selected_example['word']}")
        self.example_label.config(text=f"{self.current_example['english']}")
        self.meaning_label.config(text="")
    
    def know_well(self):
        self.current_example['difficulty'] = 0
        self.current_example['last_time_reviewed'] = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
        self.reviewed_examples.append({
            'word': self.word_label.cget("text"),
            'english': self.example_label.cget("text"),
            'persian': self.meaning_label.cget("text"),
            'difficulty': self.current_example['difficulty'],
            'last_time_reviewed': self.current_example['last_time_reviewed']
        })
        save_data(self.data)
        self.next_example()
        self.update_today_reviewed_count()  # به‌روزرسانی تعداد بررسی‌های امروز
    
    def know_meaning(self):
        self.current_example['difficulty'] = max(1, self.current_example['difficulty'] - 1)
        self.current_example['last_time_reviewed'] = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
        self.reviewed_examples.append({
            'word': self.word_label.cget("text"),
            'english': self.example_label.cget("text"),
            'persian': self.meaning_label.cget("text"),
            'difficulty': self.current_example['difficulty'],
            'last_time_reviewed': self.current_example['last_time_reviewed']
        })
        save_data(self.data)
        self.next_example()
        self.update_today_reviewed_count()  # به‌روزرسانی تعداد بررسی‌های امروز

    def dont_know_meaning(self):
        self.meaning_label.config(text=f"{self.current_example['persian']}")
        self.current_example['difficulty'] = min(5, self.current_example['difficulty'] + 1)
        self.current_example['last_time_reviewed'] = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
        self.reviewed_examples.append({
            'word': self.word_label.cget("text"),
            'english': self.example_label.cget("text"),
            'persian': self.meaning_label.cget("text"),
            'difficulty': self.current_example['difficulty'],
            'last_time_reviewed': self.current_example['last_time_reviewed']
        })
        save_data(self.data)
        self.update_today_reviewed_count()  # به‌روزرسانی تعداد بررسی‌های امروز
    
    def update_today_reviewed_count(self):
        # محاسبه تعداد بررسی‌های امروز    
        self.today_reviewed += 1
        self.today_reviewed_label.config(text=f"تعداد بررسی‌های امروز: {self.today_reviewed}")

# اجرای برنامه
if __name__ == "__main__":
    root = tk.Tk()
    app = ReviewApp(root)
    root.mainloop()

# %%



