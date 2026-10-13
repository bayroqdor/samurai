# E'lonlar sozlamasi (format: locales/en/announcements.ftl ga qarang)
#
# Faqat config.toml dagi [locale] default = "uz" bo'lganda ishlatiladi.
# Guruhga xos e'lonlar uchun "@groups: -100..." qatorini qo'shing.


# ============================
# XABAR SHABLONLARI
# ============================

msg-report-reminder =
    ❕ <b>!report</b> buyrug'ini unutmang: u <u>qoidabuzarlarni</u> adminlar e'tiboriga yetkazadi.
    
    <tg-spoiler><i>Bu buyruqni spam qilish butunlay ban bilan jazolanadi.</i></tg-spoiler>

msg-chat-rules =
    <b>📁 Chat qoidalari</b>
    Xushmuomala bo'ling va qoidalarga amal qiling!
    
    📈 Chatda <u>reputatsiya tizimi</u> ishlaydi
    ⛔️ Yangi a'zolar media yubora olmaydi
    🤬 So'kinishlar <u>avtomatik o'chiriladi</u>
    👹 Mavzudan tashqari va spam uchun 🍌 ban beriladi
    
    <b>Hammaga tinchlik 🤞</b>

msg-spam-warning =
    🛡 <b>Ehtiyot bo'ling!</b>
    "Uydan turib kuniga 500 ming", "bepul iPhone", "kartangiz bloklandi" kabi xabarlar — firibgarlik.
    Havolalarni bosmang, karta ma'lumotlari va SMS kodlarni hech kimga bermang.
    Shubhali xabarni ko'rsangiz, unga <b>!report</b> deb javob yozing.


# ===============================
# E'LONLAR (rejali yuborish)
# ===============================

announcement-1 =
    @message: msg-report-reminder
    @every: 10000-20000

announcement-2 =
    @message: msg-chat-rules
    @every: 9600-12000

announcement-3 =
    @message: msg-spam-warning
    @every: 19800-23400
