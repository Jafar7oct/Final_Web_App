FROM python:3.9-slim

WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كل ملفات المشروع
COPY . .

# تحديد المتغيرات اللازمة لتشغيل Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production  # إيقاف وضع debug نهائيًا داخل الحاوية

# فتح المنفذ الذي يعمل عليه التطبيق
EXPOSE 5000

# الأمر لتشغيل التطبيق
CMD ["flask", "run"]
