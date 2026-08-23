/**
 * PILL RED Sovereign Multi-Language (i18n) & Local Currency Localization Engine
 * Titan Black Swan Technologies // 100% Local Sovereign Processing
 */

const SUPPORTED_LANGUAGES = {
    en: { name: "English", flag: "🇺🇸", country: "US" },
    af: { name: "Afrikaans", flag: "🇿🇦", country: "ZA" },
    es: { name: "Español", flag: "🇪🇸", country: "ES" },
    fr: { name: "Français", flag: "🇫🇷", country: "FR" },
    de: { name: "Deutsch", flag: "🇩🇪", country: "DE" },
    pt: { name: "Português", flag: "🇧🇷", country: "BR" },
    zh: { name: "简体中文", flag: "🇨🇳", country: "CN" },
    ja: { name: "日本語", flag: "🇯🇵", country: "JP" },
    ru: { name: "Русский", flag: "🇷🇺", country: "RU" },
    it: { name: "Italiano", flag: "🇮🇹", country: "IT" }
};

const CURRENCY_CONFIG = {
    USD: { code: "USD", symbol: "$", rate: 1.0, proPrice: 49.00, format: "$49.00 USD" },
    ZAR: { code: "ZAR", symbol: "R", rate: 18.15, proPrice: 890.00, format: "R 890.00 ZAR" },
    EUR: { code: "EUR", symbol: "€", rate: 0.92, proPrice: 45.00, format: "€45.00 EUR" },
    GBP: { code: "GBP", symbol: "£", rate: 0.79, proPrice: 39.00, format: "£39.00 GBP" },
    JPY: { code: "JPY", symbol: "¥", rate: 153.0, proPrice: 7500.0, format: "¥7,500 JPY" },
    CAD: { code: "CAD", symbol: "C$", rate: 1.36, proPrice: 65.00, format: "C$ 65.00 CAD" },
    AUD: { code: "AUD", symbol: "A$", rate: 1.52, proPrice: 75.00, format: "A$ 75.00 AUD" },
    BRL: { code: "BRL", symbol: "R$", rate: 5.0, proPrice: 245.00, format: "R$ 245.00 BRL" },
    CNY: { code: "CNY", symbol: "¥", rate: 7.23, proPrice: 350.00, format: "¥350.00 CNY" },
    CHF: { code: "CHF", symbol: "CHF", rate: 0.90, proPrice: 44.00, format: "CHF 44.00" }
};

const TRANSLATIONS = {
    en: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Cryptographic Evidence & Real-time Causal Audit",
        sign_in_title: "Sign In to Command Center",
        sign_in_desc: "Access local evidence engine and sovereign forensic audit tools.",
        create_account_title: "Create Free Auditor Account",
        create_account_desc: "Initialize sovereign cryptographic audit credentials.",
        btn_sign_in: "SIGN IN TO COMMAND CENTER",
        btn_create_account: "CREATE AUDITOR ACCOUNT",
        tab_sign_in: "SIGN IN",
        tab_create_account: "CREATE FREE ACCOUNT",
        first_name: "First Name",
        last_name: "Surname",
        username_or_email: "Username or Email",
        password: "Password",
        confirm_password: "Confirm Password",
        dob: "Date of Birth",
        day: "Day",
        month: "Month",
        year: "Year",
        age: "Age",
        city: "City",
        postal_code: "Postal Code",
        remember_me: "Remember My Session (Local Sovereign)",
        nav_overview: "Overview Dashboard",
        nav_stream: "Live Stream Telemetry",
        nav_models: "Model Arena",
        nav_ledger: "Forensic Merkle Ledger",
        nav_settings: "Configuration",
        plan_free_name: "Free Community Plan",
        plan_pro_name: "Forensic Pro Tier",
        plan_inst_name: "Institutional Tier",
        btn_complete_purchase: "Complete Purchase",
        my_account_title: "My Account & Entitlement",
        edit_profile: "Edit Profile",
        save_profile: "Save Profile",
        cancel: "Cancel"
    },
    af: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Kriptografiese Bewyse & Intydse Kousale Oudit",
        sign_in_title: "Meld Aan by Bevelsentrum",
        sign_in_desc: "Toegang tot plaaslike bewys-enjin en soewereine forensiese ouditgereedskap.",
        create_account_title: "Skep Gratis Ouditeur-rekening",
        create_account_desc: "Inisialiseer soewereine kriptografiese oudit-geloofsbriewe.",
        btn_sign_in: "MELD AAN BY BEVELSENTRUM",
        btn_create_account: "SKEP OUDITEUR-REKENING",
        tab_sign_in: "MELD AAN",
        tab_create_account: "SKEP GRATIS REKENING",
        first_name: "Naam",
        last_name: "Van",
        username_or_email: "Gebruikersnaam of E-pos",
        password: "Wagwoord",
        confirm_password: "Bevestig Wagwoord",
        dob: "Geboortedatum",
        day: "Dag",
        month: "Maand",
        year: "Jaar",
        age: "Ouderdom",
        city: "Stad",
        postal_code: "Poskode",
        remember_me: "Onthou My Sessie (Plaaslik Soewerein)",
        nav_overview: "Oorsig Paneel",
        nav_stream: "Regstreekse Telemetrie",
        nav_models: "Model Arena",
        nav_ledger: "Forensiese Merkle Grootboek",
        nav_settings: "Konfigurasie",
        plan_free_name: "Gratis Gemeenskap Plan",
        plan_pro_name: "Forensic Pro Vlak",
        plan_inst_name: "Institusionele Vlak",
        btn_complete_purchase: "Voltooi Aankoop",
        my_account_title: "My Rekening & Regte",
        edit_profile: "Wysig Profiel",
        save_profile: "Stoor Profiel",
        cancel: "Kanselleer"
    },
    es: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Evidencia Criptográfica y Auditoría Causal en Tiempo Real",
        sign_in_title: "Iniciar Sesión en el Centro de Mando",
        sign_in_desc: "Acceda al motor local de evidencia y herramientas de auditoría forense.",
        create_account_title: "Crear Cuenta de Auditor Gratuita",
        create_account_desc: "Inicialice credenciales de auditoría criptográfica soberana.",
        btn_sign_in: "INICIAR SESIÓN EN CENTRO DE MANDO",
        btn_create_account: "CREAR CUENTA DE AUDITOR",
        tab_sign_in: "INICIAR SESIÓN",
        tab_create_account: "CREAR CUENTA GRATUITA",
        first_name: "Nombre",
        last_name: "Apellido",
        username_or_email: "Usuario o Correo Electrónico",
        password: "Contraseña",
        confirm_password: "Confirmar Contraseña",
        dob: "Fecha de Nacimiento",
        day: "Día",
        month: "Mes",
        year: "Año",
        age: "Edad",
        city: "Ciudad",
        postal_code: "Código Postal",
        remember_me: "Recordar Mi Sesión (Soberana Local)",
        nav_overview: "Panel General",
        nav_stream: "Telemetría en Vivo",
        nav_models: "Arena de Modelos",
        nav_ledger: "Libro Mayor Merkle Forense",
        nav_settings: "Configuración",
        plan_free_name: "Plan Comunitario Gratuito",
        plan_pro_name: "Nivel Forense Pro",
        plan_inst_name: "Nivel Institucional",
        btn_complete_purchase: "Completar Compra",
        my_account_title: "Mi Cuenta y Licencias",
        edit_profile: "Editar Perfil",
        save_profile: "Guardar Perfil",
        cancel: "Cancelar"
    },
    fr: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Preuve Cryptographique & Audit Causal en Temps Réel",
        sign_in_title: "Connexion au Centre de Commande",
        sign_in_desc: "Accédez au moteur local de preuve et aux outils d'audit médico-légal.",
        create_account_title: "Créer un Compte Auditeur Gratuit",
        create_account_desc: "Initialisez les identifiants d'audit cryptographique souverains.",
        btn_sign_in: "SE CONNECTER AU CENTRE DE COMMANDE",
        btn_create_account: "CRÉER UN COMPTE AUDITEUR",
        tab_sign_in: "CONNEXION",
        tab_create_account: "CRÉER UN COMPTE GRATUIT",
        first_name: "Prénom",
        last_name: "Nom de Famille",
        username_or_email: "Identifiant ou E-mail",
        password: "Mot de Passe",
        confirm_password: "Confirmer le Mot de Passe",
        dob: "Date de Naissance",
        day: "Jour",
        month: "Mois",
        year: "Année",
        age: "Âge",
        city: "Ville",
        postal_code: "Code Postal",
        remember_me: "Mémoriser Ma Session (Souveraine Locale)",
        nav_overview: "Tableau de Bord",
        nav_stream: "Télémétrie en Direct",
        nav_models: "Arène des Modèles",
        nav_ledger: "Grand Livre Merkle Forensique",
        nav_settings: "Configuration",
        plan_free_name: "Plan Communautaire Gratuit",
        plan_pro_name: "Niveau Forensic Pro",
        plan_inst_name: "Niveau Institutionnel",
        btn_complete_purchase: "Finaliser l'Achat",
        my_account_title: "Mon Compte & Droits",
        edit_profile: "Modifier le Profil",
        save_profile: "Enregistrer le Profil",
        cancel: "Annuler"
    },
    de: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Kryptografische Beweise & Kausale Echtzeit-Audits",
        sign_in_title: "Im Kommandozentrum Anmelden",
        sign_in_desc: "Zugriff auf die lokale Beweis-Engine und souveräne forensische Audit-Tools.",
        create_account_title: "Kostenloses Prüfer-Konto Erstellen",
        create_account_desc: "Initialisieren Sie souveräne kryptografische Audit-Zugangsdaten.",
        btn_sign_in: "IM KOMMANDOZENTRUM ANMELDEN",
        btn_create_account: "PRÜFER-KONTO ERSTELLEN",
        tab_sign_in: "ANMELDEN",
        tab_create_account: "KOSTENLOSES KONTO ERSTELLEN",
        first_name: "Vorname",
        last_name: "Nachname",
        username_or_email: "Benutzername oder E-Mail",
        password: "Passwort",
        confirm_password: "Passwort Bestätigen",
        dob: "Geburtsdatum",
        day: "Tag",
        month: "Monat",
        year: "Jahr",
        age: "Alter",
        city: "Stadt",
        postal_code: "Postleitzahl",
        remember_me: "Sitzung Speichern (Lokal Souverän)",
        nav_overview: "Übersicht Dashboard",
        nav_stream: "Echtzeit-Telemetrie",
        nav_models: "Modell-Arena",
        nav_ledger: "Forensisches Merkle-Hauptbuch",
        nav_settings: "Konfiguration",
        plan_free_name: "Kostenloser Community-Plan",
        plan_pro_name: "Forensic Pro Stufe",
        plan_inst_name: "Institutionelle Stufe",
        btn_complete_purchase: "Kauf Abschließen",
        my_account_title: "Mein Konto & Berechtigungen",
        edit_profile: "Profil Bearbeiten",
        save_profile: "Profil Speichern",
        cancel: "Abbrechen"
    },
    pt: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Evidência Criptográfica & Auditoria Causal em Tempo Real",
        sign_in_title: "Entrar no Centro de Comando",
        sign_in_desc: "Acesse o mecanismo local de evidências e ferramentas forenses soberanas.",
        create_account_title: "Criar Conta de Auditor Gratuita",
        create_account_desc: "Inicialize credenciais de auditoria criptográfica soberana.",
        btn_sign_in: "ENTRAR NO CENTRO DE COMANDO",
        btn_create_account: "CRIAR CONTA DE AUDITOR",
        tab_sign_in: "ENTRAR",
        tab_create_account: "CRIAR CONTA GRATUITA",
        first_name: "Nome",
        last_name: "Sobrenome",
        username_or_email: "Usuário ou E-mail",
        password: "Senha",
        confirm_password: "Confirmar Senha",
        dob: "Data de Nascimento",
        day: "Dia",
        month: "Mês",
        year: "Ano",
        age: "Idade",
        city: "Cidade",
        postal_code: "Código Postal",
        remember_me: "Lembrar Minha Sessão (Soberana Local)",
        nav_overview: "Painel Geral",
        nav_stream: "Telemetria ao Vivo",
        nav_models: "Arena de Modelos",
        nav_ledger: "Livro-Razão Merkle Forense",
        nav_settings: "Configurações",
        plan_free_name: "Plano Comunitário Gratuito",
        plan_pro_name: "Nível Forensic Pro",
        plan_inst_name: "Nível Institucional",
        btn_complete_purchase: "Concluir Compra",
        my_account_title: "Minha Conta & Licenças",
        edit_profile: "Editar Perfil",
        save_profile: "Salvar Perfil",
        cancel: "Cancelar"
    },
    zh: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "密码学证据与实时因果取证审计",
        sign_in_title: "登录指挥中心",
        sign_in_desc: "访问本地证据引擎和主权取证审计工具。",
        create_account_title: "创建免费审计师账户",
        create_account_desc: "初始化主权密码学审计凭证。",
        btn_sign_in: "登录指挥中心",
        btn_create_account: "创建审计师账户",
        tab_sign_in: "登录",
        tab_create_account: "创建免费账户",
        first_name: "名字",
        last_name: "姓氏",
        username_or_email: "用户名或邮箱",
        password: "密码",
        confirm_password: "确认密码",
        dob: "出生日期",
        day: "日",
        month: "月",
        year: "年",
        age: "年龄",
        city: "城市",
        postal_code: "邮政编码",
        remember_me: "记住我的会话（本地主权）",
        nav_overview: "总览仪表盘",
        nav_stream: "实时遥测数据流",
        nav_models: "模型竞技场",
        nav_ledger: "取证默克尔账本",
        nav_settings: "系统配置",
        plan_free_name: "免费社区计划",
        plan_pro_name: "Forensic Pro 专业级",
        plan_inst_name: "机构定制级",
        btn_complete_purchase: "完成购买",
        my_account_title: "我的账户与授权",
        edit_profile: "编辑个人资料",
        save_profile: "保存资料",
        cancel: "取消"
    },
    ja: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "暗号証拠＆リアルタイム因果監査プロトコル",
        sign_in_title: "コマンドセンターにサインイン",
        sign_in_desc: "ローカル証拠エンジンと主権的フォレンジック監査ツールにアクセス。",
        create_account_title: "無料監査アカウントを作成",
        create_account_desc: "主権的暗号監査クレデンシャルを初期化します。",
        btn_sign_in: "コマンドセンターへサインイン",
        btn_create_account: "監査アカウントを作成",
        tab_sign_in: "サインイン",
        tab_create_account: "無料アカウント作成",
        first_name: "名",
        last_name: "姓",
        username_or_email: "ユーザー名またはメール",
        password: "パスワード",
        confirm_password: "パスワード確認",
        dob: "生年月日",
        day: "日",
        month: "月",
        year: "年",
        age: "年齢",
        city: "市区町村",
        postal_code: "郵便番号",
        remember_me: "セッションを記憶（ローカル主権）",
        nav_overview: "概要ダッシュボード",
        nav_stream: "ライブテレメトリー",
        nav_models: "モデルアリーナ",
        nav_ledger: "フォレンジックマークル台帳",
        nav_settings: "設定",
        plan_free_name: "無料コミュニティプラン",
        plan_pro_name: "Forensic Pro ティア",
        plan_inst_name: "機関・エンタープライズ",
        btn_complete_purchase: "購入を完了",
        my_account_title: "アカウントとライセンス",
        edit_profile: "プロフィール編集",
        save_profile: "保存",
        cancel: "キャンセル"
    },
    ru: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Криптографические Доказательства и Причинно-следственный Аудит",
        sign_in_title: "Войти в Командный Центр",
        sign_in_desc: "Доступ к локальному движку доказательств и форензик-аудиту.",
        create_account_title: "Создать Бесплатный Аккаунт",
        create_account_desc: "Инициализация суверенных криптографических учетных данных.",
        btn_sign_in: "ВОЙТИ В КОМАНДНЫЙ ЦЕНТР",
        btn_create_account: "СОЗДАТЬ АККАУНТ АУДИТОРА",
        tab_sign_in: "ВХОД",
        tab_create_account: "РЕГИСТРАЦИЯ",
        first_name: "Имя",
        last_name: "Фамилия",
        username_or_email: "Логин или Email",
        password: "Пароль",
        confirm_password: "Подтвердите Пароль",
        dob: "Дата Рождения",
        day: "День",
        month: "Месяц",
        year: "Год",
        age: "Возраст",
        city: "Город",
        postal_code: "Почтовый Индекс",
        remember_me: "Запомнить Сессию (Локально)",
        nav_overview: "Обзорная Панель",
        nav_stream: "Телеметрия в Реальном Времени",
        nav_models: "Арена Моделей",
        nav_ledger: "Криптографический Реестр Merkle",
        nav_settings: "Конфигурация",
        plan_free_name: "Бесплатный План Community",
        plan_pro_name: "Уровень Forensic Pro",
        plan_inst_name: "Институциональный Уровень",
        btn_complete_purchase: "Завершить Покупку",
        my_account_title: "Мой Аккаунт и Лицензии",
        edit_profile: "Редактировать Профиль",
        save_profile: "Сохранить",
        cancel: "Отмена"
    },
    it: {
        corp_title: "TITAN BLACK SWAN TECHNOLOGIES",
        app_sub: "Evidenza Crittografica & Audit Causale in Tempo Reale",
        sign_in_title: "Accedi al Centro di Comando",
        sign_in_desc: "Accedi al motore locale di prove e strumenti forensi sovrani.",
        create_account_title: "Crea Account Auditor Gratuito",
        create_account_desc: "Inizializza le credenziali di audit crittografico sovrano.",
        btn_sign_in: "ACCEDI AL CENTRO DI COMANDO",
        btn_create_account: "CREA ACCOUNT AUDITOR",
        tab_sign_in: "ACCEDI",
        tab_create_account: "CREA ACCOUNT GRATUITO",
        first_name: "Nome",
        last_name: "Cognome",
        username_or_email: "Nome Utente o Email",
        password: "Password",
        confirm_password: "Conferma Password",
        dob: "Data di Nascita",
        day: "Giorno",
        month: "Mese",
        year: "Anno",
        age: "Età",
        city: "Città",
        postal_code: "Codice Postale",
        remember_me: "Ricorda la Mia Sessione (Sovrana Locale)",
        nav_overview: "Dashboard Panoramica",
        nav_stream: "Telemetria in Tempo Reale",
        nav_models: "Arena dei Modelli",
        nav_ledger: "Registro Merkle Forense",
        nav_settings: "Configurazione",
        plan_free_name: "Piano Community Gratuito",
        plan_pro_name: "Livello Forensic Pro",
        plan_inst_name: "Livello Istituzionale",
        btn_complete_purchase: "Completa Acquisto",
        my_account_title: "Il Mio Account & Licenze",
        edit_profile: "Modifica Profilo",
        save_profile: "Salva Profilo",
        cancel: "Annulla"
    }
};

let currentLang = "en";
let currentCurrency = "USD";

function detectSovereignLocaleAndCurrency() {
    const savedLang = localStorage.getItem("pillred_lang");
    const savedCurr = localStorage.getItem("pillred_currency");
    if (savedLang && SUPPORTED_LANGUAGES[savedLang]) {
        currentLang = savedLang;
    }
    if (savedCurr && CURRENCY_CONFIG[savedCurr]) {
        currentCurrency = savedCurr;
    }

    if (savedLang && savedCurr) return { lang: currentLang, currency: currentCurrency };

    try {
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        const browserLocale = (navigator.language || navigator.userLanguage || "en").toLowerCase();
        const primaryLang = browserLocale.split("-")[0];

        if (timeZone.includes("Johannesburg") || timeZone.includes("Harare") || browserLocale.includes("za")) {
            currentCurrency = "ZAR";
            currentLang = browserLocale.startsWith("af") ? "af" : "en";
        } else if (timeZone.includes("Berlin") || timeZone.includes("Vienna") || browserLocale.startsWith("de")) {
            currentCurrency = "EUR";
            currentLang = "de";
        } else if (timeZone.includes("Paris") || browserLocale.startsWith("fr")) {
            currentCurrency = "EUR";
            currentLang = "fr";
        } else if (timeZone.includes("Madrid") || browserLocale.startsWith("es")) {
            currentCurrency = "EUR";
            currentLang = "es";
        } else if (timeZone.includes("Rome") || browserLocale.startsWith("it")) {
            currentCurrency = "EUR";
            currentLang = "it";
        } else if (timeZone.includes("London") || browserLocale.includes("gb")) {
            currentCurrency = "GBP";
            currentLang = "en";
        } else if (timeZone.includes("Tokyo") || browserLocale.startsWith("ja")) {
            currentCurrency = "JPY";
            currentLang = "ja";
        } else if (timeZone.includes("Shanghai") || timeZone.includes("Chongqing") || browserLocale.startsWith("zh")) {
            currentCurrency = "CNY";
            currentLang = "zh";
        } else if (timeZone.includes("Sao_Paulo") || browserLocale.startsWith("pt")) {
            currentCurrency = "BRL";
            currentLang = "pt";
        } else if (timeZone.includes("Toronto") || timeZone.includes("Vancouver") || browserLocale.includes("ca")) {
            currentCurrency = "CAD";
            currentLang = "en";
        } else if (timeZone.includes("Sydney") || timeZone.includes("Melbourne") || browserLocale.includes("au")) {
            currentCurrency = "AUD";
            currentLang = "en";
        } else if (timeZone.includes("Zurich") || browserLocale.includes("ch")) {
            currentCurrency = "CHF";
            currentLang = "de";
        } else if (timeZone.includes("Moscow") || browserLocale.startsWith("ru")) {
            currentCurrency = "USD";
            currentLang = "ru";
        } else {
            currentCurrency = "USD";
            currentLang = SUPPORTED_LANGUAGES[primaryLang] ? primaryLang : "en";
        }
    } catch (e) {
        currentLang = "en";
        currentCurrency = "USD";
    }

    return { lang: currentLang, currency: currentCurrency };
}

function setLocaleAndCurrency(lang, currency) {
    if (lang && SUPPORTED_LANGUAGES[lang]) {
        currentLang = lang;
        localStorage.setItem("pillred_lang", lang);
    }
    if (currency && CURRENCY_CONFIG[currency]) {
        currentCurrency = currency;
        localStorage.setItem("pillred_currency", currency);
    }
    applyTranslations();
    updateCurrencyDisplays();
}

function getFormattedProPrice() {
    const config = CURRENCY_CONFIG[currentCurrency] || CURRENCY_CONFIG.USD;
    return config.format;
}

function getProPriceAmount() {
    const config = CURRENCY_CONFIG[currentCurrency] || CURRENCY_CONFIG.USD;
    return config.proPrice;
}

function getCurrencyCode() {
    return currentCurrency;
}

function t(key, fallback = "") {
    const langDict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    return langDict[key] || TRANSLATIONS.en[key] || fallback;
}

function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.dataset.i18n;
        const translated = t(key);
        if (translated) {
            if (el.tagName === "INPUT" && el.placeholder) {
                el.placeholder = translated;
            } else {
                el.textContent = translated;
            }
        }
    });

    const langPickerBtn = document.getElementById("activeLocaleDisplay");
    if (langPickerBtn) {
        const langObj = SUPPORTED_LANGUAGES[currentLang] || SUPPORTED_LANGUAGES.en;
        const currObj = CURRENCY_CONFIG[currentCurrency] || CURRENCY_CONFIG.USD;
        langPickerBtn.innerHTML = `${langObj.flag} ${currObj.code} (${currObj.symbol}) ▾`;
    }
}

function updateCurrencyDisplays() {
    const priceText = getFormattedProPrice();
    
    const summaryPrice = document.getElementById("planSelectedPriceSummary");
    if (summaryPrice) summaryPrice.textContent = priceText;

    const paypalCheckoutText = document.getElementById("btnPaypalCheckoutText");
    if (paypalCheckoutText) {
        paypalCheckoutText.textContent = `${t("btn_complete_purchase", "Complete Purchase")} (${priceText})`;
    }

    const cardPriceTag = document.getElementById("planCardProPrice");
    if (cardPriceTag) {
        const currObj = CURRENCY_CONFIG[currentCurrency] || CURRENCY_CONFIG.USD;
        cardPriceTag.innerHTML = `${currObj.symbol}${currObj.proPrice} <span class="plan-cycle">/ month</span>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    detectSovereignLocaleAndCurrency();
    applyTranslations();
    updateCurrencyDisplays();
});
