# Migrations

المشروع يستخدم `Base.metadata.create_all()` عند الإقلاع، وهو **لا يعدّل الجداول الموجودة**
(لا يضيف أعمدة جديدة). لذا أي تغيير على جدول موجود يحتاج تنفيذ SQL يدوياً هنا.

## لماذا ينكسر زر Save على الويب (Render) وينجح محلياً

- محلياً: أضيف عمود `status` يدوياً إلى قاعدة البيانات المحلية، لذلك يعمل.
- على Render: قاعدة البيانات موجودة سلفاً بدون عمود `status`، و`create_all()` لا يضيفه،
  فيعود `GET /products` بـ 500 (لأن الموديل يطلب العمود).

## خطوات التنفيذ على Render (مرة واحدة)

1. احصل على رابط اتصال قاعدة بيانات Render (يظهر في لوحة تحكم Render تحت PostgreSQL service
   أو من المتغير `DATABASE_URL` في إعدادات خدمة الـ backend).
2. نفّذ أمر `001_add_status_to_products.sql` على قاعدة البيانات:
   - عبر psql:
     ```
     psql "DATABASE_URL" -f 001_add_status_to_products.sql
     ```
   - أو عبر DBeaver / pgAdmin / لوحة Render: الصق محتوى الملف وشغّله.
3. أعد تشغيل/إعادة نشر الـ backend على Render.
4. تحقق: `GET https://backalgeriacommerce.onrender.com/products` يجب أن يعود 200.

ملاحظة: `ADD COLUMN IF NOT EXISTS` آمن — إذا كان العمود موجوداً بالفعل لن يفعل شيئاً.
