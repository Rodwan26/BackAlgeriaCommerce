from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.carrier import Carrier
import app.models.carrier_connection


SEED_CARRIERS = [
    {
        "id": "zr-express",
        "name": "ZR Express",
        "name_ar": "زد أر إكسبرس",
        "dashboard_url": "https://zr-express.com",
        "sorted_order": 1,
        "credential_schema": [
            {
                "key": "token",
                "label": "الرمز (API Token)",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "من لوحة تحكم ZR Express",
                "help": "ادخل إلى حسابك في ZR Express ثم افتح «الإعدادات» وقسم «API». انسخ قيمة Token وKey كاملة.",
            },
            {
                "key": "key",
                "label": "المفتاح (API Key)",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "بجانب الرمز في نفس القسم",
                "help": "المفتاح (Key) موجود بجانب الرمز (Token) في نفس صفحة الإعدادات. انسخ الاثنين معاً.",
            },
        ],
    },
    {
        "id": "yalidine",
        "name": "Yalidine",
        "name_ar": "ياليدين",
        "dashboard_url": "https://www.yalidine.dz",
        "sorted_order": 2,
        "credential_schema": [
            {
                "key": "apiId",
                "label": "معرّف (API ID)",
                "type": "text",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "من إعدادات الحساب في Yalidine",
                "help": "سجّل الدخول إلى منصة Yalidine ثم «الإعدادات» ← «API». ستجد API ID و API Token.",
            },
            {
                "key": "apiToken",
                "label": "الرمز (API Token)",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "مقابل المعرّف",
                "help": "انسخ الـ API Token من نفس صفحة الإعدادات التي أخذت منها المعرّف.",
            },
        ],
    },
    {
        "id": "maystro",
        "name": "Maystro",
        "name_ar": "مايسترو",
        "dashboard_url": "https://www.maystro.com",
        "sorted_order": 3,
        "credential_schema": [
            {
                "key": "apiKey",
                "label": "مفتاح API",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "حقل واحد فقط يكفي",
                "help": "تتطلب Maystro مفتاح API وحيداً. تجده في الإعدادات ← التكامل مع المتاجر.",
            },
        ],
    },
    {
        "id": "noest",
        "name": "NOEST",
        "name_ar": "نويست",
        "dashboard_url": "https://noest.com",
        "sorted_order": 4,
        "credential_schema": [
            {
                "key": "apiToken",
                "label": "الرمز (API Token)",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "من لوحة تحكم NOEST",
                "help": "ادخل إلى لوحة NOEST ثم «الإعدادات» للحصول على الـ API Token و GUID الخاصين بحسابك.",
            },
            {
                "key": "guid",
                "label": "المعرّف (GUID)",
                "type": "text",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "معرّف حسابك لدى NOEST",
                "help": "الـ GUID يميز حسابك. تجده في نفس صفحة الإعدادات بجوار الـ Token.",
            },
        ],
    },
    {
        "id": "ecotrack-dhd",
        "name": "DHD (Ecotrack)",
        "name_ar": "دي إتش دي",
        "dashboard_url": "https://platform.dhd-dz.com",
        "sorted_order": 5,
        "credential_schema": [
            {
                "key": "token",
                "label": "الرمز (Token)",
                "type": "password",
                "required": True,
                "dir": "ltr",
                "placeholder": "••••••••",
                "hint": "من بيئة الشركة على Ecotrack",
                "help": "ادخل إلى منصة Ecotrack الخاصة بشركتك ثم أنشئ مفتاح API من الإعدادات.",
            },
            {
                "key": "baseUrl",
                "label": "رابط المنصة",
                "type": "url",
                "required": True,
                "dir": "ltr",
                "placeholder": "https://platform.dhd-dz.com",
                "hint": "رابط حسابك على المنصة",
                "help": "أدخل رابط المنصة الخاص بشركة التوصيل كما يظهر في متصفحك عند الدخول، ويبدأ بـ https://.",
            },
        ],
    },
]


def seed_carriers(db: Session) -> dict:
    inserted = 0
    skipped = 0

    for data in SEED_CARRIERS:
        exists = (
            db.query(Carrier)
            .filter(Carrier.id == data["id"])
            .first()
        )

        if exists is not None:
            skipped += 1
            continue

        db.add(Carrier(**data))
        inserted += 1

    db.commit()
    return {
        "inserted": inserted,
        "skipped": skipped,
    }


def main() -> None:
    db: Session = SessionLocal()

    try:
        summary = seed_carriers(db)
        total = (
            db.query(Carrier)
            .count()
        )
        print(
            f"[seed] carriers inserted={summary['inserted']} "
            f"skipped(existing)={summary['skipped']} total={total}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
