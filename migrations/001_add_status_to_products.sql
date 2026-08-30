-- Migration: add `status` column to `products`
-- سبب الحاجة: `products` على قاعدة بيانات Render موجود مسبقاً بدون عمود `status`.
-- `Base.metadata.create_all()` لا يضيف أعمدة جديدة للجداول الموجودة، لذا يجب تنفيذ هذا
-- الملف يدوياً مرة واحدة على قاعدة البيانات قيد التشغيل.

-- تنفيذ هذا الملف سيُضيف عمود `status` لجدول `products` دون حذف أي بيانات.

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'draft';

-- التأكد من النتيجة (يجب أن يعرض صفاً بعمود status)
-- SELECT column_name FROM information_schema.columns
-- WHERE table_name = 'products' AND column_name = 'status';
