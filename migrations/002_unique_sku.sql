-- Migration: add a unique index on `product_variants.sku`
-- سبب الحاجة: ضمان عدم وجود SKU مكرر على مستوى قاعدة البيانات (Postgres).
-- `Base.metadata.create_all()` لا يضيف فهارس/قيوداً جديدة للجداول الموجودة، لذا يجب
-- تنفيذ هذا الملف يدوياً مرة واحدة على قاعدة البيانات قيد التشغيل.

-- فهرس فريد جزئي: يضمن فرادة القيم غير الفارغة فقط (لأن `sku` عمود nullable).
-- يجب ألا توجد قيم مكررة في العمود قبل الإنشاء.

CREATE UNIQUE INDEX IF NOT EXISTS ux_product_variants_sku
    ON product_variants (sku)
    WHERE sku IS NOT NULL AND sku <> '';

-- التأكد من النتيجة:
-- SELECT indexname FROM pg_indexes
-- WHERE tablename = 'product_variants' AND indexname = 'ux_product_variants_sku';
