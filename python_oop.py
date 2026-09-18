"""
فكره المشروع عباره عن محلل اقتصادي 
حد عوزا يفتح مشروع بيدخل بيانات زاي اسم المشروع و راس المال و المكان 
و AI يحلل البيانات و يطلع توقع
استخدامت API Google Gemini
بخزن الداتا و النتيجه اللي طلعت في Database
استخدامت مكنبه sqlite3
عملت واجهه مستخدام با Streamlit
 streamlit run python_oop.py
"""
import sqlite3
import pandas as pd
import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")



class AIAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)

    def analyze(self, name, idea, budget):
        prompt = f"قم بتحليل اقتصادي لمشروع اسمه {name} وفكرته {idea} وميزانيته {budget}. واذكر المخاطر والنصائح."
        
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return response.text


class Database:
    def __init__(self):
        self.db_name = "projects_clean.db"
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                idea TEXT,
                budget TEXT,
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def insert_project(self, name, idea, budget, analysis):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (name, idea, budget, analysis) VALUES (?, ?, ?, ?)", 
                       (name, idea, budget, analysis))
        conn.commit()
        conn.close()

    def get_projects(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects")
        data = cursor.fetchall()
        conn.close()
        return data


class UserInterface:
    def __init__(self):
        self.ai = AIAnalyzer()
        self.db = Database()

    def run(self):
        st.title("AI Economic Analyst")
        st.write("أدخل بيانات مشروعك للحصول على تحليل اقتصادي")

        name = st.text_input("اسم المشروع")
        idea = st.text_area("فكرة المشروع")
        budget = st.text_input("الميزانية المتوقعة")

        if st.button("تحليل المشروع"):
            if name != "" and idea != "":
                result = self.ai.analyze(name, idea, budget)
                self.db.insert_project(name, idea, budget, result)
                st.success("تم التحليل والحفظ!")
                st.write(result)
            else:
                st.warning("يرجى كتابة اسم المشروع والفكرة")

        st.divider()

        st.subheader("المشاريع السابقة")
        projects = self.db.get_projects()
        if len(projects) > 0:
            df = pd.DataFrame(projects)
            st.dataframe(df)


if __name__ == "__main__":
    app = UserInterface()
    app.run()