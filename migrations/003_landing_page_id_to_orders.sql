-- Migration: add `landing_page_id` to `orders`
-- سبب الحاجة: تتبّع الطلبات القادمة من صفحات الهبوط (landing pages) ضمن جدول
-- الطلبات الموحّد `orders` بدلاً من جدول `landing_orders` المنفصل الذي أُلغي.
-- `Base.metadata.create_all()` لا يضيف أعمدةً جديدةً للجداول الموجودة، لذا يجب
-- تنفيذ هذا الملف يدوياً مرة واحدة على قاعدة البيانات قيد التشغيل.
-- (قاعدة بيانات جديدة تُنشأ تلقائياً بالعمود من الموديل مباشرة، فلا حاجة
-- لهذا الملف في بيئات جديدة.)

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS landing_page_id integer
    REFERENCES landing_pages(id) ON DELETE SET NULL;

-- تنظيف الجدول المُلغى إن وُجدت بيانات له من تنفيذ سابق.
DROP TABLE IF EXISTS landing_orders;

-- التأكد من النتيجة:
-- SELECT column_name FROM information_schema.columns
-- WHERE table_name = 'orders' AND column_name = 'landing_page_id';