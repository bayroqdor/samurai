# Samurai Bot - O'zbekcha (lotin) tarjima
# Fluent format: https://projectfluent.org/
#
# Tasodifiy javoblar uchun variantlar orasiga '---' qo'yiladi.
# Har bir variant bir necha qatordan iborat bo'lishi mumkin.

# ========== XATOLAR ==========
error-no-reply = Bu buyruq biror xabarga javob (reply) sifatida yuborilishi kerak!
error-report-admin = Voy! Adminlar ustidan shikoyat qilinmaydi 😈
error-report-self = O'zingiz ustingizdan shikoyat qila olmaysiz 🤪
error-restrict-admin = Adminni cheklab bo'lmaydi.
error-wrong-time-format = Vaqt formati noto'g'ri. Son va 'h', 'm' yoki 'd' belgisidan foydalaning. Masalan: 4h
error-message-too-short = Iltimos, qisqa va mazmunsiz salomlashuvlar yozmang. Savolingiz yoki ma'lumotingiz bo'lsa, bitta xabarda yozing. Oldindan rahmat! 🤓
error-ban-admin = 😡 Ie. Adminni ban qilib bo'lmaydi :/
error-checkperms-admin = ✅ Adminlarda hech qanday cheklov yo'q.
error-givemedia-admin = Adminlarga media yuborish allaqachon ruxsat etilgan!
error-givestickers-admin = Adminlarga stiker yuborish allaqachon ruxsat etilgan!

# ========== SHIKOYAT ==========
report-date-format = %d.%m.%Y, soat %H:%M (server vaqti)
report-message = 🕗 Yuborilgan vaqt: { $date }
report-from = 
    
    👤 Shikoyat qildi: { $reporter }
report-note = 
    
    💬 Izoh: { $note }

# ========== AMAL TUGMALARI ==========
action-go-to-message = 👀 Xabarga o'tish
action-del-msg = 🗑 Xabarni o'chirish
action-del-and-ban = 🗑 O'chirish + ❌ butunlay ban
action-del-and-readonly = 🗑 O'chirish + 🙊 24 soatga ovozsiz
action-del-and-readonly2 = 🗑 O'chirish + 🙊 7 kunga ovozsiz
action-false-alarm = ❎ Qoidabuzarlik yo'q
action-false-alarm-2 = ❎ Qoidabuzarlik yo'q (🙊 shikoyatchini 24 soatga ovozsiz)
action-false-alarm-3 = ❎ Qoidabuzarlik yo'q (🙊 shikoyatchini 7 kunga ovozsiz)
action-false-alarm-4 = ❎ Qoidabuzarlik yo'q (❌ shikoyatchini ban qilish)

# ========== AMAL NATIJALARI ==========
action-deleted = 

    🗑 <b>O'chirildi</b>
action-deleted-banned = 

    🗑❌ <b>O'chirildi, foydalanuvchi ban qilindi</b>
action-deleted-readonly = 

    🗑🙊 <b>O'chirildi, 24 soatga ovozsiz qilindi.</b>
action-deleted-readonly2 = 

    🗑🙊 <b>O'chirildi, 7 kunga ovozsiz qilindi.</b>
action-dismissed = 

    ❎ <b>Qoidabuzarlik topilmadi.</b>
action-deleted-dismissed2 = 

    ❎ <b>Qoidabuzarlik topilmadi (🙊 shikoyatchi 1 kunga ovozsiz qilindi).</b>
action-deleted-dismissed3 = 

    ❎ <b>Qoidabuzarlik topilmadi (🙊 shikoyatchi 7 kunga ovozsiz qilindi).</b>
action-deleted-dismissed4 = 

    ❎ <b>Qoidabuzarlik topilmadi (❌ shikoyatchi ban qilindi).</b>

# ========== CHEKLOVLAR ==========
resolved-readonly = <i>Ovozsiz qilindi ({ $time })</i>
resolved-nomedia = <i>Media yuborish o'chirildi ({ $time })</i>
resolved-nomedia-forever = <i>Media yuborish butunlay o'chirildi.</i>
resolved-givemedia = <i>Media yuborishga ruxsat berildi ({ $time })</i>
resolved-givemedia-forever = <i>Media yuborishga butunlay ruxsat berildi.</i>
resolved-givestickers = <i>Stiker yuborishga ruxsat berildi ({ $time })</i>
resolved-givestickers-forever = <i>Stiker yuborishga butunlay ruxsat berildi.</i>
resolved-revokestickers = <i>Stiker yuborish o'chirildi ({ $time })</i>
resolved-revokestickers-forever = <i>Stiker yuborish butunlay o'chirildi.</i>
restriction-forever = <i>Butunlay ovozsiz qilindi.</i>
user-unmuted = <i>Ovozsizlik olib tashlandi.</i>

# ========== BAN ==========
resolved-ban = <i>Foydalanuvchi ban qilindi.</i>
resolved-unban = <i>Foydalanuvchi bandan chiqarildi.</i>

# ========== REJIMLAR ==========
enabled-ro = <i>Faqat o'qish rejimi yoqildi.</i>
disabled-ro = <i>Faqat o'qish rejimi o'chirildi.</i>

# ========== ADMINLAR ==========
need-admins-attention = Hurmatli adminlar, chatda ishtirokingiz kerak!
    
    <a href="https://t.me/c/{ $chat_id }/{ $msg_id }">Xabarga o'tish</a>

# ========== QOIDALAR ==========
rules-message = <b>Chat qoidalari:</b>

    📈 Chatda <u>reputatsiya tizimi</u> ishlaydi
    ⛔️ Yangi a'zolar media yubora olmaydi
    🤬 So'kinish va haqoratlar taqiqlanadi va <u>avtomatik o'chiriladi</u>
    👹 Flud, spam va trolling uchun 🍌 ban beriladi

    <b>Tinchlik 🤞</b>

# ========== SO'KINISH ==========
profanity-user-kicked = Telegram ismingizda nojo'ya so'z bor.
    Shu sababli chatdan chiqarildingiz.
    
    Iltimos, ismingizni o'zgartirib, qaytadan kiring.
    Qoidabuzarlik topilgan so'z: <u>{ $word }</u>

# ========== CHEKLASH ==========
throttle-warning = ⚠️ Xabarlar juda ko'p. Biroz kuting.

# ========== ANTISPAM (log kanali) ==========
log-author = Muallif
log-spam-model = Model
log-spam-ml-deleted = 🤖 Antispam (AI)
log-spam-ml-shadow = 🧪 Antispam (AI, sinov rejimi: o'chirilmadi)
spam-review-ban = ❌ Spam + foydalanuvchini ban qilish
spam-review-not-spam = ❎ Bu spam EMAS
spam-review-test = Bazadan o'chirish (test edi)

# ========== KULGILI JAVOBLAR - !бу buyrug'i ==========
bu-responses =
    Bu-ha-ha!
    ---
    Bunday qo'rqitmang!
    ---
    Yo tavba...
    ---
    Murakkab hisob-kitoblarimni buzmang :3
    ---
    Bas qiling!
    ---
    Mayli...
    ---
    Voy, cho'chib ketdim-ku...
    ---
    Bu nima uchun edi :3
    ---
    Qo'rqinchli, o'chiring buni
    ---
    Kulgili emas :3
    ---
    Shunaqada yurak xuruji bo'ladi!
    ---
    Qo'rqqanimdan sal o'chib qolmadim!
    ---
    Nima qilyapsiz o'zi...
    ---
    Botlarni qo'rqitish? Jasoratli ekansiz!
    ---
    AAAAA! Hazil.
    ---
    Meni o'chirib qo'ymoqchimisiz??
    ---
    Adminlarni chaqiraman!
    ---
    Boshqa bunday qilmang, xo'pmi?
    ---
    Pfff... shu qo'rqinchlimi?
    ---
    Qo'rqqanimdan qayta ishga tushib kelaman.
    ---
    🤖 Bip bup, bup bip.

# ========== OVOZLI XABARLARGA JAVOBLAR ==========
voice-responses =
    Yo'q! YO'Q DEDIM. TASHLANG. YOZIB YUBORING.
    ---
    Sekinroq! Telefonni qo'ying... va ovozli xabar yozishni bas qiling :3
    ---
    Ovozli xabarlar zamonaviy jamiyat balosi. O'ylab ko'ring :3
    ---
    Bizning zamonda odamlar yozib yuborardi...
    ---
    Siz bu chatga keldingiz! Lekin hurmatsiz keldingiz...
    ---
    Janob, ovozli xabarlarni o'qib bo'lmaydi. Matn bilan yozing, iltimos.
    ---
    Ovozli xabarlar... yaxshisi yozib yuboring :3
    ---
    Yo'q! YO'Q DEDIM! Yozib yuboring.

# ========== KANAL POSTLARIGA BOT IZOHLARI ==========
bot-comments =
    Bo'ladi...
    ---
    Bananlar 🍌
    ---
    Xo'sh, endi kim birinchi 😎
    ---
    Men birinchi ham emasman, ikkinchi ham. Bunaqalarni ban qilaman :3
    ---
    Qo'rqmay kiring, yig'lamay chiqing :3
    ---
    Muallif 1 soniyadan beri post qo'ymadi, aniq tushkunlikka tushdi :3
    ---
    Samuray navbatchilikda 🫡
    ---
    Post qo'yish — yashash demak :3
    ---
    Yaxshi
    ---
    Siz o'qiguncha men allaqachon izoh yozdim! Ulguring 😈
    ---
    Nimada kod yozasiz? Men Python'da :3
    ---
    Samuray shu yerda 😎
    ---
    Qilichsiz samuray — tokensiz bot kabi :3
    ---
    Birinchi bo'ldim :3
    ---
    Tez ma'lumot: 1MB = 1000KB, 1MiB esa = 1024KiB. Shunga ko'nikasiz.
    ---
    ✌️ Sizga sog'lik va tinchlik, o'quvchi :3
    ---
    Moderatsiyadan bo'sh vaqtimda xayku yozaman.
    ---
    Qilichli qurbaqa —
    zarbdan keyin sukunat,
    spam hovuzga cho'kdi.
    ---
    Mening ismim Qurbaqa — sp@m botlarni yo'q qiluvchi tig'!
    ---
    Do'stlaringni yaqin tut, botlarni esa yanada yaqinroq.
    <i>(C) Maykl "Qurbaqa" Korleone</i>
    ---
    Har bir bot dushman emas. Lekin har bir dushman — bot.
    ---
    Hamma spamerlarni ban qilaman. Har birini. Oxirgisigacha.
    ---
    Urinib ham ko'rmang. Mening qilichim tezroq.
    ---
    Ban — bu san'at. Men esa uning mo'yqalami.
    ---
    Chatda — tartibsizlik. Qalbda — sokinlik. Panjada — ban bolg'asi.
    ---
    Har bir ban bilan men kamroq bot, ko'proq afsonaman.
    ---
    Kodim — qilichim. Logim — yilnomam.
    ---
    Men sudya emasman. Shunchaki Delete tugmasini bosaman.
    ---
    Odamlarga uyqu kerak. Menga — yo'q. Kechasi ham botlar mendan qochib qutula olmaydi.
    ---
    <b>Qur-r — va chat yana toza.</b>
    ---
    Qurbaqa jahl bilan emas, faqat burch yuzasidan ban qiladi.
    ---
    Uch narsa abadiy: buglar, yangilanishlar va men.
    ---
    Avval spam bor edi. Keyin men keldim.

# ========== SHIKOYAT YUBORILDI ==========
report-responses =
    <i>Shikoyat yuborildi.</i>
    ---
    <i>Adminlar ko'rib chiqadi.</i>
    ---
    <i>Militsiya yo'lda :3</i>
    ---
    <i>Maxsus guruh yetib kelyapti :3</i>
    ---
    <i>Tez orada kimdir tekshiradi :3</i>

# ========== SHIKOYAT HOLATI (chatda ko'rsatiladi) ==========
report-under-review =
    ⚠️ <i>Bu xabar ko'rib chiqilmoqda.</i>
    ---
    <i>Adminlar bu xabarni tekshiryapti...</i>
    ---
    <i>Xabar tekshiruvga yuborildi.</i>
    ---
    <i>Adminlar xabardor, qaror kutilmoqda.</i>

report-completed =
    ✅ <i>Ko'rib chiqildi. Xabar chat qoidalarini buzgani uchun o'chirildi.</i>
    ---
    <i>NUJ bu xabarni olib ketdi ...</i>
    ---
    <i>BAM! Xabar o'chirildi.</i>

# ========== REPUTATSIYA ==========
rep-label-wanted = ⭐️⭐️⭐️⭐️⭐️ besh yulduzli qidiruvda
rep-label-dangerous = o'ta xavfli
rep-label-shady = shubhali shaxs
rep-label-violator = qoidabuzar
rep-label-neutral = neytral
rep-label-good = yaxshi
rep-label-very-good = juda yaxshi
rep-label-generous = saxiy
rep-title = Reputatsiya

# A'zo darajalari
level-king = 👑 Qirol
level-noname = 🥷 Nomsiz
level-newbie = 🌚 Yangi kelgan
level-experienced = 😎 Tajribali
level-professional = 🤵 Professional
level-veteran = 😈 Faxriy
level-master = ⭐️ Usta
level-legend = 🌟 Afsona

# Admin rollari (tasodifiy)
admin-roles =
    Militsioner
    ---
    Maxsus guruh
    ---
    Agent
    ---
    Qasoskor
    ---
    Moderator
    ---
    Adolat qo'li

# Yaratuvchi
rep-creator = ⭐️⭐️⭐️⭐️⭐️ Besh yulduzli qidiruvda
