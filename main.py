
import os, json, hashlib, time, uuid, random
from datetime import datetime

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('kivy', 'keyboard_mode', 'systemanddock')

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.core.window import Window

BG    = (.09, .10, .13, 1)
SURF  = (.14, .16, .20, 1)
SURF2 = (.18, .21, .26, 1)
PRI   = (.13, .47, .71, 1)
PRI2  = (.10, .35, .56, 1)
GRN   = (.13, .70, .40, 1)
RED   = (.85, .22, .22, 1)
GOLD  = (.98, .78, .08, 1)
PURP  = (.50, .18, .86, 1)
MOUT  = (.11, .38, .60, 1)
MIN   = (.17, .20, .25, 1)
TXT   = (.92, .94, .96, 1)
TXT2  = (.50, .56, .64, 1)
TXT3  = (.32, .37, .44, 1)
DIV   = (.17, .20, .25, 1)
WHT   = (1, 1, 1, 1)
TR    = (0, 0, 0, 0)
ADMBG = (.07, .05, .15, 1)
ADMP  = (.48, .16, .82, 1)

ACOLORS = ['#1E88E5','#43A047','#E53935','#FB8C00',
           '#8E24AA','#00ACC1','#F4511E','#D81B60']

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0,2,4)) + (1,)


def set_bg(w, color, r=0):
    """Установить фон виджету"""
    def draw(*a):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*color)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[r])
    w.bind(pos=draw, size=draw)

def make_btn(text, bg=None, fg=None, h=50, fs=15, r=12, bold=True):
    """Создать кнопку без кастомного класса"""
    b = Button(
        text=text,
        background_normal='',
        background_color=TR,
        color=fg or WHT,
        font_size=dp(fs),
        bold=bold,
        size_hint_y=None,
        height=dp(h)
    )
    bc = list(bg or PRI)
    def draw(*a):
        b.canvas.before.clear()
        with b.canvas.before:
            Color(*bc)
            RoundedRectangle(pos=b.pos, size=b.size, radius=[r])
    def on_press(*a):
        bc[3] = 0.75
        draw()
    def on_release(*a):
        bc[3] = 1.0
        draw()
    b.bind(pos=draw, size=draw,
           on_press=lambda x: on_press(),
           on_release=lambda x: on_release())
    return b

def make_input(hint='', pwd=False, fs=15, h=52):
    """Создать поле ввода"""
    inp = TextInput(
        hint_text=hint,
        password=pwd,
        multiline=False,
        background_normal='',
        background_active='',
        background_color=TR,
        foreground_color=TXT,
        hint_text_color=TXT3,
        cursor_color=PRI,
        font_size=dp(fs),
        padding=[dp(16), dp(14)],
        size_hint_y=None,
        height=dp(h)
    )
    def draw(*a):
        inp.canvas.before.clear()
        with inp.canvas.before:
            Color(*SURF)
            RoundedRectangle(pos=inp.pos, size=inp.size, radius=[dp(12)])
            Color(*(PRI[:3] + (0.5,)))
            Line(points=[inp.x+dp(10), inp.y+2,
                         inp.right-dp(10), inp.y+2], width=1.2)
    inp.bind(pos=draw, size=draw)
    return inp

def make_divider():
    w = Widget(size_hint_y=None, height=dp(1))
    def draw(*a):
        w.canvas.clear()
        with w.canvas:
            Color(*DIV)
            RoundedRectangle(pos=w.pos, size=w.size)
    w.bind(pos=draw, size=draw)
    return w

def make_avatar(text='?', color='#1E88E5', sz=46):
    s = dp(sz)
    box = BoxLayout(size_hint=(None, None), size=(s, s))
    col = rgb(color)
    def draw(*a):
        box.canvas.before.clear()
        with box.canvas.before:
            Color(*col)
            Ellipse(pos=box.pos, size=box.size)
    box.bind(pos=draw, size=draw)
    is_emoji = len(text) <= 2 and any(
        ord(c) > 127 for c in text) if text else False
    fs = dp(sz * 0.48) if is_emoji else dp(sz * 0.38)
    lbl = Label(
        text=text, color=WHT, bold=(not is_emoji),
        font_size=fs,
        halign='center', valign='middle'
    )
    lbl.bind(size=lbl.setter('text_size'))
    box.add_widget(lbl)
    return box


def make_icon_btn(text, color=None, sz=42, fs=20, on_tap=None):
    """Иконка-кнопка"""
    b = Button(
        text=text,
        background_normal='', background_color=TR,
        color=color or TXT2, font_size=dp(fs),
        size_hint=(None, None), size=(dp(sz), dp(sz))
    )
    if on_tap:
        b.bind(on_release=on_tap)
    return b

def make_topbar(title='', sub='', on_back=None, right_items=None):
    outer = BoxLayout(orientation='vertical', size_hint_y=None,
                      height=dp(59))
    bar = BoxLayout(
        orientation='horizontal',
        size_hint_y=None, height=dp(58),
        padding=[dp(2), dp(6), dp(8), dp(6)],
        spacing=dp(4)
    )
    set_bg(bar, PRI2)
    if on_back:
        bb = Button(
            text='←', background_normal='', background_color=TR,
            color=WHT, font_size=dp(24),
            size_hint=(None, 1), width=dp(44)
        )
        bb.bind(on_release=on_back)
        bar.add_widget(bb)
    mid = BoxLayout(orientation='vertical', size_hint_x=1)
    tl = Label(text=title, color=WHT, font_size=dp(17), bold=True,
               halign='left', valign='middle',
               size_hint_y=None, height=dp(24))
    tl.bind(size=tl.setter('text_size'))
    mid.add_widget(tl)
    if sub:
        sl = Label(text=sub, color=TXT2, font_size=dp(12),
                   halign='left', valign='middle',
                   size_hint_y=None, height=dp(16))
        sl.bind(size=sl.setter('text_size'))
        mid.add_widget(sl)
    bar.add_widget(mid)
    for icon, action in (right_items or []):
        rb = Button(
            text=icon, background_normal='', background_color=TR,
            color=TXT2, font_size=dp(20),
            size_hint=(None, 1), width=dp(42)
        )
        rb.bind(on_release=action)
        bar.add_widget(rb)
    outer.add_widget(bar)
    div = Widget(size_hint_y=None, height=dp(1))
    set_bg(div, (.08,.09,.12,1))
    outer.add_widget(div)
    return outer

def show_popup(title, msg, ok_text='OK', on_ok=None,
               cancel=False, on_cancel=None):
    box = BoxLayout(orientation='vertical',
                    padding=dp(16), spacing=dp(10))
    p = Popup(
        title=title, content=box,
        size_hint=(.88, None), height=dp(210 if cancel else 175),
        background='', background_color=SURF2,
        title_color=WHT, separator_color=PRI
    )
    lbl = Label(text=msg, color=TXT, font_size=dp(14),
                halign='center', valign='middle',
                text_size=(dp(270), None), size_hint_y=1)
    box.add_widget(lbl)
    row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
    if cancel:
        cb = make_btn('Отмена', bg=SURF2, h=44)
        cb.bind(on_release=lambda *a: (p.dismiss(),
                on_cancel() if on_cancel else None))
        row.add_widget(cb)
    ob = make_btn(ok_text, h=44)
    ob.bind(on_release=lambda *a: (p.dismiss(),
            on_ok() if on_ok else None))
    row.add_widget(ob)
    box.add_widget(row)
    p.open()
    return p


class DB:
    def __init__(self):
        try:
            from android.storage import app_storage_path
            base = app_storage_path()
        except:
            try:
                from android import mActivity
                base = str(mActivity.getFilesDir())
            except:
                base = os.path.join(os.path.expanduser('~'), '.pygram5')
        os.makedirs(base, exist_ok=True)
        self.fu = os.path.join(base, 'u.json')
        self.fc = os.path.join(base, 'c.json')
        self.fm = os.path.join(base, 'm.json')
        self.fg = os.path.join(base, 'g.json')
        self.fp = os.path.join(base, 'ph.json')
        self.fs = os.path.join(base, 'sess.json')
        self._boot()

    def _h(self, p):
        return hashlib.sha256(p.encode()).hexdigest()

    def _r(self, f):
        try:
            if os.path.exists(f):
                with open(f, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
        except:
            pass
        return {}

    def _w(self, f, d):
        try:
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(d, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            print('DB write error:', e)

    def _mk(self, uid, uname, dname, pwd, color,
            admin=False, prem=False, stars=0,
            phone='', verified=False, bio=''):
        init = ''.join(w[0].upper() for w in dname.split()[:2]) \
               or uname[:2].upper()
        return {
            'id': uid, 'username': uname, 'display_name': dname,
            'pw': self._h(pwd), 'bio': bio or 'Привет! Я в PyGram 🚀',
            'color': color, 'init': init, 'online': False,
            'last_seen': time.time() - random.randint(0, 3600),
            'phone': phone,
            'joined': time.time() - 86400 * random.randint(5, 200),
            'is_admin': admin, 'banned': False,
            'premium': prem, 'stars': stars, 'verified': verified,
        }

    def _boot(self):
        users = self._r(self.fu)

        defaults = {
            'u1':  self._mk('u1','alice','Alice Johnson','alice123',
                            '#1E88E5',prem=True,stars=1250,
                            phone='+7 900 111-11-11',verified=True),
            'u2':  self._mk('u2','bob','Bob Smith','bob123',
                            '#43A047',stars=0,phone='+7 900 222-22-22'),
            'u3':  self._mk('u3','carol','Carol White','carol123',
                            '#D81B60',prem=True,stars=300),
            'u4':  self._mk('u4','dave','Dave Brown','dave123',
                            '#FB8C00'),
            'adm': self._mk('adm','hailendsky','Hailendsky','12345',
                            '#8E24AA',admin=True,prem=True,
                            stars=99999,phone='+7 999 000-00-00',
                            verified=True,bio='Создатель PyGram 👑'),
        }
        changed = False
        for uid, usr in defaults.items():
            if not any(v.get('username') == usr['username']
                       for v in users.values()):
                users[uid] = usr
                changed = True

        if changed:
            users['u1']['online'] = True
            users['u3']['online'] = True
            users['adm']['online'] = True
            self._w(self.fu, users)

        if not os.path.exists(self.fc): self._w(self.fc, {})
        if not os.path.exists(self.fm): self._w(self.fm, {})
        if not os.path.exists(self.fg):
            self._w(self.fg, {
                'g1': {'id':'g1','name':'PyGram Official','color':'#8E24AA',
                       'init':'PO','desc':'Официальный чат',
                       'members':['u1','u2','u3','u4','adm']},
                'g2': {'id':'g2','name':'Общий чат 💬','color':'#1E88E5',
                       'init':'ОЧ','desc':'Для всех',
                       'members':['u1','u2','adm']},
            })
        if not os.path.exists(self.fp):
            pool = []
            for _ in range(300):
                pool.append(
                    f'+7 9{random.randint(0,9)}{random.randint(0,9)} '
                    f'{random.randint(100,999)}-'
                    f'{random.randint(10,99)}-'
                    f'{random.randint(10,99)}'
                )
            self._w(self.fp, {'pool': pool, 'issued': []})

    def login(self, uname, pwd):
        u = self._r(self.fu)
        h = self._h(pwd)
        for uid, usr in u.items():
            if usr['username'].lower() == uname.lower():
                if usr.get('banned'):
                    return None, '⛔ Аккаунт заблокирован'
                if usr['pw'] == h:
                    usr['online'] = True
                    usr['last_seen'] = time.time()
                    u[uid] = usr
                    self._w(self.fu, u)
                    return usr, None
                return None, 'Неверный пароль'
        return None, 'Пользователь не найден'

    def register(self, uname, dname, pwd):
        if len(uname) < 3: return None, 'Логин мин. 3 символа'
        if len(pwd) < 5:   return None, 'Пароль мин. 5 символов'
        u = self._r(self.fu)
        for usr in u.values():
            if usr['username'].lower() == uname.lower():
                return None, 'Логин уже занят'
        uid = 'u_' + uuid.uuid4().hex[:8]
        usr = self._mk(uid, uname, dname, pwd,
                       random.choice(ACOLORS))
        usr['online'] = True
        usr['last_seen'] = time.time()
        u[uid] = usr
        self._w(self.fu, u)
        return usr, None

    def user(self, uid):    return self._r(self.fu).get(uid)
    def users(self):        return self._r(self.fu)

    def upd(self, uid, d):
        u = self._r(self.fu)
        if uid in u:
            u[uid].update(d)
            self._w(self.fu, u)
            return u[uid]

    def search(self, q):
        q = q.lower().lstrip('@')
        return [u for u in self._r(self.fu).values()
                if q in u['username'].lower()
                or q in u.get('display_name','').lower()
                or q == u['id'].lower()]

    def save_sess(self, u): self._w(self.fs, u)
    def load_sess(self):
        if os.path.exists(self.fs): return self._r(self.fs)
    def clear_sess(self):
        if os.path.exists(self.fs): os.remove(self.fs)

    def get_chat(self, u1, u2):
        c = self._r(self.fc)
        for cid, ch in c.items():
            if set(ch.get('members', [])) == {u1, u2}:
                return ch
        cid = 'c_' + uuid.uuid4().hex[:8]
        ch = {'id': cid, 'members': [u1, u2],
              'last_msg': '', 'last_time': 0, 'unread': {}}
        c[cid] = ch
        self._w(self.fc, c)
        return ch

    def user_chats(self, uid):
        c = self._r(self.fc)
        r = [ch for ch in c.values()
             if uid in ch.get('members', [])]
        r.sort(key=lambda x: x.get('last_time', 0), reverse=True)
        return r

    def send(self, cid, sender, text):
        m = self._r(self.fm)
        c = self._r(self.fc)
        mid = 'm_' + uuid.uuid4().hex[:10]
        ts = time.time()
        msg = {'id': mid, 'cid': cid, 'from': sender,
               'text': text, 'ts': ts, 'status': 'sent'}
        if cid not in m: m[cid] = []
        m[cid].append(msg)
        self._w(self.fm, m)
        if cid in c:
            c[cid]['last_msg'] = text[:50]
            c[cid]['last_time'] = ts
            for mem in c[cid].get('members', []):
                if mem != sender:
                    c[cid]['unread'][mem] = \
                        c[cid]['unread'].get(mem, 0) + 1
            self._w(self.fc, c)
        return msg

    def msgs(self, cid, limit=80):
        m = self._r(self.fm).get(cid, [])
        return m[-limit:]

    def mark_read(self, cid, uid):
        c = self._r(self.fc)
        if cid in c:
            c[cid]['unread'][uid] = 0
            self._w(self.fc, c)

    def user_groups(self, uid):
        g = self._r(self.fg)
        return {gid: gr for gid, gr in g.items()
                if uid in gr.get('members', [])}

    def all_groups(self):
        return self._r(self.fg)

    def send_grp(self, gid, sender, text):
        return self.send(gid, sender, text)

    def grp_msgs(self, gid, limit=80):
        return self.msgs(gid, limit)

    def issue_phone(self, uid):
        p = self._r(self.fp)
        for iss in p.get('issued', []):
            if iss['uid'] == uid:
                return iss['phone'], False
        pool = p.get('pool', [])
        if not pool:
            pool = [
                f'+7 9{random.randint(0,9)}{random.randint(0,9)} '
                f'{random.randint(100,999)}-'
                f'{random.randint(10,99)}-'
                f'{random.randint(10,99)}'
                for _ in range(200)
            ]
        phone = pool.pop(0)
        p.setdefault('issued', []).append(
            {'uid': uid, 'phone': phone, 'ts': time.time()})
        p['pool'] = pool
        self._w(self.fp, p)
        self.upd(uid, {'phone': phone})
        return phone, True

    def issued_phones(self):
        return self._r(self.fp).get('issued', [])

    def add_stars(self, uid, n):
        u = self.user(uid)
        if u:
            new = u.get('stars', 0) + n
            self.upd(uid, {'stars': new})
            return new
        return 0

    def stats(self):
        u = self._r(self.fu)
        m = self._r(self.fm)
        g = self._r(self.fg)
        return {
            'users':   len(u),
            'online':  sum(1 for x in u.values() if x.get('online')),
            'msgs':    sum(len(v) for v in m.values()),
            'premium': sum(1 for x in u.values() if x.get('premium')),
            'banned':  sum(1 for x in u.values() if x.get('banned')),
            'groups':  len(g),
            'phones':  len(self._r(self.fp).get('issued', [])),
        }

    def fmt_time(self, ts):
        if not ts: return ''
        dt = datetime.fromtimestamp(ts)
        diff = datetime.now() - dt
        if diff.days == 0: return dt.strftime('%H:%M')
        if diff.days == 1: return 'Вчера'
        if diff.days < 7:  return dt.strftime('%a')
        return dt.strftime('%d.%m')

    def fmt_seen(self, ts):
        if not ts: return 'давно'
        d = time.time() - ts
        if d < 60:     return 'только что'
        if d < 3600:   return f'{int(d//60)} мин. назад'
        if d < 86400:
            return f'сегодня {datetime.fromtimestamp(ts).strftime("%H:%M")}'
        return f'вчера {datetime.fromtimestamp(ts).strftime("%H:%M")}'


class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)

        top = BoxLayout(orientation='vertical', size_hint_y=.4,
                        padding=[30, 40, 30, 10], spacing=8)
        aw = BoxLayout(size_hint_y=None, height=dp(86))
        aw.add_widget(Widget())
        av = make_avatar('✈', '#1E88E5', 74)
        aw.add_widget(av)
        aw.add_widget(Widget())
        top.add_widget(aw)
        top.add_widget(Label(
            text='PyGram', color=WHT, font_size=dp(34),
            bold=True, size_hint_y=None, height=dp(44)))
        top.add_widget(Label(
            text='Мессенджер нового поколения',
            color=TXT2, font_size=dp(13),
            size_hint_y=None, height=dp(22)))
        root.add_widget(top)

        frm = BoxLayout(orientation='vertical', size_hint_y=.6,
                        padding=[28, 8, 28, 24], spacing=10)
        self.fu = make_input('Логин (@username)')
        self.fp = make_input('Пароль', pwd=True)
        self.fp.bind(on_text_validate=lambda *a: self._login())
        self.err = Label(text='', color=RED, font_size=dp(13),
                         size_hint_y=None, height=dp(20))

        btn = make_btn('ВОЙТИ')
        btn.bind(on_release=lambda *a: self._login())

        reg = Button(
            text='Нет аккаунта? Зарегистрироваться',
            background_normal='', background_color=TR,
            color=PRI, font_size=dp(14),
            size_hint_y=None, height=dp(42))
        reg.bind(on_release=lambda *a: A.go('reg'))

        sep = Label(text='─── Быстрый вход ───', color=TXT3,
                    font_size=dp(12), size_hint_y=None, height=dp(22))

        demos = BoxLayout(size_hint_y=None, height=dp(44), spacing=6)
        for nm, col in [('alice', '#1E88E5'), ('bob', '#43A047'),
                        ('carol', '#D81B60'), ('hailendsky', '#8E24AA')]:
            b = make_btn(nm[:9], bg=rgb(col), h=40, fs=12)
            b.bind(on_release=lambda x, n=nm: self._quick(n))
            demos.add_widget(b)

        for w in [self.fu, self.fp, self.err, btn, reg,
                  sep, demos, Widget()]:
            frm.add_widget(w)
        root.add_widget(frm)
        self.add_widget(root)

    def on_enter(self):
        self.fu.text = ''
        self.fp.text = ''
        self.err.text = ''

    def _login(self):
        u, e = DB.login(self.fu.text.strip(), self.fp.text.strip())
        if u:
            DB.save_sess(u)
            A.me = u
            A.go('main')
        else:
            self.err.text = e or 'Ошибка'

    def _quick(self, n):
        pw = {'alice': 'alice123', 'bob': 'bob123',
              'carol': 'carol123', 'dave': 'dave123',
              'hailendsky': '12345'}
        self.fu.text = n
        self.fp.text = pw.get(n, n + '123')
        Clock.schedule_once(lambda dt: self._login(), .05)


class RegScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)
        root.add_widget(make_topbar(
            'Регистрация',
            on_back=lambda *a: A.go('login')))
        frm = BoxLayout(orientation='vertical',
                        padding=[28, 20, 28, 20], spacing=12)
        self.fn = make_input('Имя и фамилия')
        self.fu = make_input('Логин (без пробелов)')
        self.fp = make_input('Пароль', pwd=True)
        self.fc = make_input('Повторите пароль', pwd=True)
        self.err = Label(text='', color=RED, font_size=dp(13),
                         size_hint_y=None, height=dp(22))
        b = make_btn('СОЗДАТЬ АККАУНТ')
        b.bind(on_release=self._reg)
        bk = Button(
            text='Уже есть аккаунт? Войти',
            background_normal='', background_color=TR,
            color=PRI, font_size=dp(14),
            size_hint_y=None, height=dp(42))
        bk.bind(on_release=lambda *a: A.go('login'))
        for w in [self.fn, self.fu, self.fp, self.fc,
                  self.err, b, bk, Widget()]:
            frm.add_widget(w)
        root.add_widget(frm)
        self.add_widget(root)

    def _reg(self, *a):
        if self.fp.text != self.fc.text:
            self.err.text = 'Пароли не совпадают'
            return
        u, e = DB.register(
            self.fu.text.strip(),
            self.fn.text.strip(),
            self.fp.text.strip())
        if u:
            DB.save_sess(u)
            A.me = u
            A.go('main')
        else:
            self.err.text = e or 'Ошибка'


class MainScreen(Screen):
    """Главный экран — 3 вкладки: Чаты, Группы, Контакты"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self._tab = 'chats'
        self._timer = None

        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)

        top = BoxLayout(orientation='horizontal', size_hint_y=None,
                        height=dp(58),
                        padding=[dp(10), dp(9), dp(10), dp(9)],
                        spacing=dp(8))
        set_bg(top, PRI2)
        self.my_av = make_avatar('?', '#1E88E5', 36)
        self.my_av.bind(
            on_touch_down=lambda w, t:
            A.go('myprofile') if w.collide_point(*t.pos) else None)
        top.add_widget(self.my_av)

        self.search = TextInput(
            hint_text='Поиск',
            multiline=False,
            background_normal='', background_active='',
            background_color=SURF,
            foreground_color=TXT,
            hint_text_color=TXT3,
            cursor_color=PRI,
            font_size=dp(14),
            padding=[dp(14), dp(10)])
        def draw_search(*a):
            self.search.canvas.before.clear()
            with self.search.canvas.before:
                Color(*SURF)
                RoundedRectangle(
                    pos=self.search.pos, size=self.search.size,
                    radius=[dp(20)])
        self.search.bind(
            pos=draw_search, size=draw_search,
            text=self._on_search)
        top.add_widget(self.search)

        edit_btn = Button(
            text='✏', background_normal='', background_color=TR,
            color=TXT2, font_size=dp(20),
            size_hint=(None, 1), width=dp(40))
        edit_btn.bind(on_release=self._new_chat_dlg)
        top.add_widget(edit_btn)
        root.add_widget(top)

        tabs = BoxLayout(size_hint_y=None, height=dp(48))
        set_bg(tabs, SURF)
        tab_div = Widget(size_hint_y=None, height=dp(1))
        set_bg(tab_div, DIV)
        self.tab_btns = []
        for key, label in [('chats', '💬  Чаты'),
                            ('groups', '👥  Группы'),
                            ('contacts', '👤  Контакты')]:
            b = Button(
                text=label,
                background_normal='', background_color=TR,
                color=TXT2, font_size=dp(13), bold=True)
            b.bind(on_release=lambda x, k=key: self._switch(k))
            self.tab_btns.append((key, b))
            tabs.add_widget(b)
        root.add_widget(tabs)

        self.sv = ScrollView(do_scroll_x=False)
        self.lb = BoxLayout(
            orientation='vertical', size_hint_y=None, spacing=0)
        self.lb.bind(minimum_height=self.lb.setter('height'))
        self.sv.add_widget(self.lb)
        root.add_widget(self.sv)

        fab_box = BoxLayout(size_hint_y=None, height=dp(74),
                            padding=[0, dp(10), dp(16), dp(10)])
        fab_box.add_widget(Widget())
        fab = Button(
            text='✏',
            background_normal='', background_color=TR,
            color=WHT, font_size=dp(22), bold=True,
            size_hint=(None, None), size=(dp(54), dp(54)))
        def draw_fab(*a):
            fab.canvas.before.clear()
            with fab.canvas.before:
                Color(*PRI)
                Ellipse(pos=fab.pos, size=fab.size)
        fab.bind(pos=draw_fab, size=draw_fab,
                 on_release=self._new_chat_dlg)
        fab_box.add_widget(fab)
        root.add_widget(fab_box)
        self.add_widget(root)

    def on_enter(self):
        if A.me:
            f = DB.user(A.me['id'])
            if f:
                A.me = f
                DB.save_sess(f)
            self.my_av.children[0].text = A.me.get('init', '?')
        self._switch(self._tab)
        self._timer = Clock.schedule_interval(
            lambda dt: self._reload(), 3)

    def on_leave(self):
        if self._timer:
            self._timer.cancel()

    def _switch(self, tab):
        self._tab = tab
        for key, btn in self.tab_btns:
            btn.color = PRI if key == tab else TXT2
        self._reload()

    def _on_search(self, w, text):
        self._reload(text.strip())

    def _reload(self, search=''):
        if not A.me: return
        uid = A.me['id']
        self.lb.clear_widgets()
        if self._tab == 'chats':
            self._load_chats(uid, search)
        elif self._tab == 'groups':
            self._load_groups(uid, search)
        else:
            self._load_contacts(uid, search)

    def _badges(self, u):
        b = ''
        if u.get('premium'):  b += ' ⭐'
        if u.get('verified'): b += ' ✓'
        if u.get('is_admin'): b += ' 👑'
        return b

    def _load_chats(self, uid, search=''):
        chats = DB.user_chats(uid)
        found = False
        for ch in chats:
            oid = next((m for m in ch['members'] if m != uid), None)
            if not oid: continue
            other = DB.user(oid)
            if not other: continue
            if search and search.lower() not in \
               other['display_name'].lower() and \
               search.lower() not in other['username'].lower():
                continue
            found = True
            unread = ch.get('unread', {}).get(uid, 0)
            self.lb.add_widget(self._row(
                av_text=other.get('init', '?'),
                av_color=other.get('color', '#1E88E5'),
                name=other['display_name'] + self._badges(other),
                sub=ch.get('last_msg', '') or 'Нет сообщений',
                time=DB.fmt_time(ch.get('last_time', 0)),
                unread=unread,
                online=other.get('online', False),
                on_tap=lambda x, c=ch, o=other: A.open_chat(c, o)
            ))
            self.lb.add_widget(make_divider())
        if not found:
            self.lb.add_widget(Label(
                text='Нет чатов\nНажмите ✏ чтобы написать',
                color=TXT2, font_size=dp(15), halign='center'))

    def _load_groups(self, uid, search=''):
        groups = DB.user_groups(uid)
        found = False
        for gid, g in groups.items():
            if search and search.lower() not in g['name'].lower():
                continue
            found = True
            msgs = DB.grp_msgs(gid, 1)
            sub, lt = g.get('desc', ''), 0
            if msgs:
                last = msgs[-1]
                snd = DB.user(last['from'])
                sn = snd['display_name'].split()[0] if snd else '?'
                sub = f"{sn}: {last['text'][:30]}"
                lt = last['ts']
            self.lb.add_widget(self._row(
                av_text=g.get('init', 'G'),
                av_color=g.get('color', '#8E24AA'),
                name=g['name'], sub=sub,
                time=DB.fmt_time(lt),
                unread=0, online=False,
                on_tap=lambda x, gr=g: A.open_group(gr)
            ))
            self.lb.add_widget(make_divider())
        if not found:
            self.lb.add_widget(Label(
                text='Нет групп', color=TXT2,
                font_size=dp(15), halign='center'))

    def _load_contacts(self, uid, search=''):
        users = DB.users()
        found = False
        for u_id, u in sorted(
                users.items(),
                key=lambda x: x[1].get('display_name', '')):
            if u_id == uid: continue
            if search and search.lower() not in \
               u['display_name'].lower() and \
               search.lower() not in u['username'].lower():
                continue
            found = True
            self.lb.add_widget(self._row(
                av_text=u.get('init', '?'),
                av_color=u.get('color', '#1E88E5'),
                name=u['display_name'] + self._badges(u),
                sub=f"@{u['username']}",
                time='',
                unread=0,
                online=u.get('online', False),
                on_tap=lambda x, u2=u: A.open_user(u2['id'])
            ))
            self.lb.add_widget(make_divider())
        if not found:
            self.lb.add_widget(Label(
                text='Контакты не найдены', color=TXT2,
                font_size=dp(15), halign='center'))

    def _row(self, av_text, av_color, name, sub,
             time, unread, online, on_tap):
        row = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            height=dp(72),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(10))
        set_bg(row, BG)

        av_fl = FloatLayout(size_hint=(None, None),
                            size=(dp(52), dp(52)))
        av = make_avatar(av_text, av_color, 50)
        av_fl.add_widget(av)
        if online:
            dot = BoxLayout(
                size_hint=(None, None), size=(dp(13), dp(13)),
                pos_hint={'right': 1.0, 'y': 0})
            set_bg(dot, GRN, 7)
            av_fl.add_widget(dot)
        row.add_widget(av_fl)

        info = BoxLayout(orientation='vertical', size_hint_x=1)
        top_row = BoxLayout(size_hint_y=None, height=dp(24))
        nl = Label(
            text=name, color=TXT, font_size=dp(15), bold=True,
            halign='left', valign='middle', size_hint_x=1,
            shorten=True, shorten_from='right')
        nl.bind(size=nl.setter('text_size'))
        tl = Label(
            text=time, color=TXT3, font_size=dp(12),
            size_hint=(None, 1), width=dp(50),
            halign='right', valign='middle')
        top_row.add_widget(nl)
        top_row.add_widget(tl)

        bot_row = BoxLayout(size_hint_y=None, height=dp(20))
        sl = Label(
            text=sub[:46], color=TXT2, font_size=dp(13),
            halign='left', valign='middle', size_hint_x=1,
            shorten=True, shorten_from='right')
        sl.bind(size=sl.setter('text_size'))
        bot_row.add_widget(sl)
        if unread > 0:
            bdg = BoxLayout(
                size_hint=(None, None), size=(dp(22), dp(22)))
            set_bg(bdg, PRI, 11)
            bdg.add_widget(Label(
                text=str(unread), color=WHT,
                font_size=dp(11), bold=True))
            bot_row.add_widget(bdg)

        info.add_widget(top_row)
        info.add_widget(bot_row)
        row.add_widget(info)
        row.bind(
            on_touch_down=lambda w, t:
            on_tap(w) if w.collide_point(*t.pos) else None)
        return row

    def _new_chat_dlg(self, *a):
        uid = A.me['id']
        users = DB.users()
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(8), dp(8), dp(8), dp(8)], spacing=dp(6))
        s_inp = TextInput(
            hint_text='Поиск...', multiline=False,
            background_normal='', background_color=SURF,
            foreground_color=TXT, hint_text_color=TXT3,
            cursor_color=PRI, font_size=dp(14),
            padding=[dp(12), dp(10)],
            size_hint_y=None, height=dp(44))

        sv = ScrollView(size_hint_y=1)
        lb = BoxLayout(
            orientation='vertical', size_hint_y=None, spacing=dp(2))
        lb.bind(minimum_height=lb.setter('height'))

        p = Popup(
            title='Новый чат', content=content,
            size_hint=(.94, .85), background='',
            background_color=BG, title_color=WHT,
            separator_color=PRI)

        def build(q=''):
            lb.clear_widgets()
            for u_id, u in users.items():
                if u_id == uid: continue
                if q and q.lower() not in \
                   u['display_name'].lower() and \
                   q.lower() not in u['username'].lower():
                    continue
                row = BoxLayout(
                    size_hint_y=None, height=dp(62),
                    padding=[dp(10), dp(6)], spacing=dp(12))
                row.add_widget(
                    make_avatar(u.get('init','?'),
                                u.get('color','#1E88E5'), 42))
                inf = BoxLayout(orientation='vertical')
                nm = u['display_name']
                if u.get('premium'): nm += ' ⭐'
                if u.get('verified'): nm += ' ✓'
                if u.get('is_admin'): nm += ' 👑'
                nl = Label(
                    text=nm, color=TXT, font_size=dp(14),
                    bold=True, halign='left', valign='middle')
                nl.bind(size=nl.setter('text_size'))
                ul = Label(
                    text=f"@{u['username']}",
                    color=TXT2, font_size=dp(12),
                    halign='left', valign='middle')
                ul.bind(size=ul.setter('text_size'))
                inf.add_widget(nl)
                inf.add_widget(ul)
                row.add_widget(inf)

                def tap(w, t, user=u):
                    if row.collide_point(*t.pos):
                        p.dismiss()
                        ch = DB.get_chat(uid, user['id'])
                        A.open_chat(ch, user)
                row.bind(on_touch_down=tap)
                lb.add_widget(row)
                lb.add_widget(make_divider())

        s_inp.bind(text=lambda w, t: build(t))
        build()
        sv.add_widget(lb)
        content.add_widget(s_inp)
        content.add_widget(sv)
        cb = Button(
            text='Отмена',
            background_normal='', background_color=TR,
            color=TXT2, font_size=dp(14),
            size_hint_y=None, height=dp(44))
        cb.bind(on_release=p.dismiss)
        content.add_widget(cb)
        p.open()


class ChatScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.chat = None
        self.other = None
        self._timer = None
        self._last = 0
        self._typing = False

        root = BoxLayout(orientation='vertical')
        set_bg(root, (.08, .09, .11, 1))

        self.hdr = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            height=dp(58),
            padding=[dp(2), dp(6), dp(10), dp(6)], spacing=dp(6))
        set_bg(self.hdr, PRI2)
        bb = Button(
            text='←', background_normal='', background_color=TR,
            color=WHT, font_size=dp(24),
            size_hint=(None, 1), width=dp(44))
        bb.bind(on_release=lambda *a: A.go('main'))
        self.hdr.add_widget(bb)
        self.h_av = make_avatar('?', '#1E88E5', 40)
        self.hdr.add_widget(self.h_av)
        hi = BoxLayout(orientation='vertical', size_hint_x=1)
        self.h_name = Label(
            text='', color=WHT, font_size=dp(16), bold=True,
            halign='left', valign='middle',
            size_hint_y=None, height=dp(24))
        self.h_name.bind(size=self.h_name.setter('text_size'))
        self.h_sub = Label(
            text='', color=TXT2, font_size=dp(12),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(16))
        self.h_sub.bind(size=self.h_sub.setter('text_size'))
        hi.add_widget(self.h_name)
        hi.add_widget(self.h_sub)
        self.hdr.add_widget(hi)
        info_btn = Button(
            text='ℹ', background_normal='', background_color=TR,
            color=TXT2, font_size=dp(19),
            size_hint=(None, 1), width=dp(38))
        info_btn.bind(
            on_release=lambda *a:
            A.open_user(self.other['id']) if self.other else None)
        call_btn = Button(
            text='📞', background_normal='', background_color=TR,
            color=TXT2, font_size=dp(17),
            size_hint=(None, 1), width=dp(38))
        call_btn.bind(on_release=lambda *a:
            show_popup('📞 Звонок', 'Скоро будет!', ok_text='OK'))
        self.hdr.add_widget(call_btn)
        self.hdr.add_widget(info_btn)
        root.add_widget(self.hdr)

        self.sv = ScrollView(do_scroll_x=False)
        self.mb = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(2), padding=[dp(8), dp(8), dp(8), dp(8)])
        self.mb.bind(minimum_height=self.mb.setter('height'))
        self.sv.add_widget(self.mb)
        root.add_widget(self.sv)

        ibar = BoxLayout(
            size_hint_y=None, height=dp(62),
            padding=[dp(6), dp(7), dp(6), dp(7)], spacing=dp(6))
        set_bg(ibar, SURF)
        emoji_btn = Button(
            text='😊', background_normal='', background_color=TR,
            color=TXT2, font_size=dp(20),
            size_hint=(None, 1), width=dp(38))
        emoji_btn.bind(on_release=lambda *a: self._show_emoji())
        ibar.add_widget(emoji_btn)
        self.inp = TextInput(
            hint_text='Сообщение...', multiline=False,
            background_normal='', background_active='',
            background_color=(.12, .14, .18, 1),
            foreground_color=TXT, hint_text_color=TXT3,
            cursor_color=PRI, font_size=dp(15),
            padding=[dp(14), dp(12)])
        def draw_inp(*a):
            self.inp.canvas.before.clear()
            with self.inp.canvas.before:
                Color(.12, .14, .18, 1)
                RoundedRectangle(
                    pos=self.inp.pos, size=self.inp.size,
                    radius=[dp(22)])
        self.inp.bind(
            pos=draw_inp, size=draw_inp,
            on_text_validate=lambda *a: self._send())
        sb = Button(
            text='▶', background_normal='', background_color=TR,
            color=WHT, font_size=dp(22), bold=True,
            size_hint=(None, 1), width=dp(48))
        def draw_sb(*a):
            sb.canvas.before.clear()
            with sb.canvas.before:
                Color(*PRI)
                RoundedRectangle(
                    pos=sb.pos, size=sb.size, radius=[dp(12)])
        sb.bind(pos=draw_sb, size=draw_sb,
                on_release=lambda *a: self._send())
        ibar.add_widget(self.inp)
        ibar.add_widget(sb)
        root.add_widget(ibar)
        self.add_widget(root)

    def load(self, chat, other):
        self.chat = chat
        self.other = other
        name = other.get('display_name', '')
        if other.get('premium'): name += ' ⭐'
        if other.get('verified'): name += ' ✓'
        self.h_name.text = name
        self.h_av.children[0].text = other.get('init', '?')
        self._upd_sub()
        self._load_msgs()
        DB.mark_read(chat['id'], A.me['id'])

    def _upd_sub(self):
        if not self.other: return
        f = DB.user(self.other['id'])
        if f: self.other = f
        if self.other.get('online'):
            self.h_sub.text = 'в сети'
            self.h_sub.color = GRN
        else:
            self.h_sub.text = DB.fmt_seen(
                self.other.get('last_seen', 0))
            self.h_sub.color = TXT2

    def on_enter(self):
        self._timer = Clock.schedule_interval(
            lambda dt: self._poll(), 2)

    def on_leave(self):
        if self._timer: self._timer.cancel()

    def _poll(self):
        if not self.chat: return
        m = DB.msgs(self.chat['id'])
        if len(m) != self._last:
            self._load_msgs()
            DB.mark_read(self.chat['id'], A.me['id'])
        self._upd_sub()

    def _load_msgs(self):
        if not self.chat: return
        msgs = DB.msgs(self.chat['id'])
        self._last = len(msgs)
        self.mb.clear_widgets()
        uid = A.me['id']
        for msg in msgs:
            self.mb.add_widget(
                self._bubble(msg, msg['from'] == uid))
        Clock.schedule_once(
            lambda dt: setattr(self.sv, 'scroll_y', 0), .05)

    def _bubble(self, msg, is_out):
        ts = datetime.fromtimestamp(
            msg.get('ts', 0)).strftime('%H:%M')
        text = msg.get('text', '')
        status = ' ✓✓' if is_out and \
                 msg.get('status') == 'read' else ' ✓' if is_out else ''
        full = text + f'\n{ts}{status}'
        bg_col = MOUT if is_out else MIN
        max_w = dp(268)
        test = Label(text=full, font_size=dp(14),
                     text_size=(max_w - dp(28), None))
        test.texture_update()
        bw = min(test.texture_size[0] + dp(32), max_w)
        bh = test.texture_size[1] + dp(24)
        r = [dp(16), dp(16), dp(3), dp(16)] if is_out else \
            [dp(16), dp(16), dp(16), dp(3)]
        bubble = BoxLayout(
            size_hint=(None, None), size=(bw, bh),
            padding=[dp(12), dp(8), dp(12), dp(6)])
        with bubble.canvas.before:
            Color(*bg_col)
            RoundedRectangle(pos=(0,0), size=bubble.size, radius=r)
        bubble.bind(
            pos=lambda w, *a, c=bg_col, rr=r: self._rd(w, c, rr),
            size=lambda w, *a, c=bg_col, rr=r: self._rd(w, c, rr))
        lbl = Label(
            text=full, font_size=dp(14), color=TXT,
            halign='left', valign='top',
            text_size=(bw - dp(28), None), size_hint_y=1)
        bubble.add_widget(lbl)
        wrap = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            padding=[0, dp(2), 0, dp(2)],
            height=bh + dp(4))
        if is_out:
            wrap.add_widget(Widget())
            wrap.add_widget(bubble)
        else:
            wrap.add_widget(bubble)
            wrap.add_widget(Widget())
        return wrap

    def _rd(self, w, col, r):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*col)
            RoundedRectangle(pos=w.pos, size=w.size, radius=r)

    def _show_emoji(self):
        emojis = ['😀','😂','😍','🥰','😎','🤩','😭','😱',
                  '👍','👎','❤️','🔥','💯','🎉','🙏','💪',
                  '😅','🤔','😏','🥳','🤯','😴','🤮','👀',
                  '✅','❌','⭐','💎','🚀','🎮','🎵','🍕']
        content = BoxLayout(orientation='vertical',
                            padding=dp(8), spacing=dp(6))
        grid = GridLayout(cols=8, size_hint_y=None, spacing=dp(4))
        grid.bind(minimum_height=grid.setter('height'))
        p = Popup(title='Эмодзи', content=content,
                  size_hint=(.92, .52), background='',
                  background_color=SURF2, title_color=WHT,
                  separator_color=PRI)
        for em in emojis:
            b = Button(text=em, background_normal='',
                       background_color=SURF, font_size=dp(22),
                       size_hint=(None, None), size=(dp(42), dp(42)))
            b.bind(on_release=lambda x, e=em: (
                setattr(self.inp, 'text', self.inp.text + e),
                p.dismiss()))
            grid.add_widget(b)
        sv2 = ScrollView()
        sv2.add_widget(grid)
        content.add_widget(sv2)
        p.open()

    def _send(self):
        text = self.inp.text.strip()
        if not text or not self.chat: return
        self.inp.text = ''
        msg = DB.send(self.chat['id'], A.me['id'], text)
        self.mb.add_widget(self._bubble(msg, True))
        self._last += 1
        Clock.schedule_once(
            lambda dt: setattr(self.sv, 'scroll_y', 0), .05)
        if self.other and not self._typing:
            Clock.schedule_once(
                lambda dt: self._auto_reply(),
                random.uniform(1.0, 2.5))

    def _auto_reply(self):
        if not self.other or not self.chat: return
        self._typing = True
        r = random.choice([
            'Понял 👍', 'Окей!', 'Хорошо', 'Спасибо 😊',
            'Договорились ✅', '🚀', 'Ясно', 'Отлично!'])
        DB.send(self.chat['id'], self.other['id'], r)
        self._typing = False
        self._load_msgs()


class GroupScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.grp = None
        self._timer = None
        self._last = 0
        root = BoxLayout(orientation='vertical')
        set_bg(root, (.08, .09, .11, 1))
        self.hdr = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            height=dp(58),
            padding=[dp(2), dp(6), dp(10), dp(6)], spacing=dp(6))
        set_bg(self.hdr, PRI2)
        bb = Button(
            text='←', background_normal='', background_color=TR,
            color=WHT, font_size=dp(24),
            size_hint=(None, 1), width=dp(44))
        bb.bind(on_release=lambda *a: A.go('main'))
        self.hdr.add_widget(bb)
        self.g_av = make_avatar('G', '#8E24AA', 40)
        self.hdr.add_widget(self.g_av)
        gi = BoxLayout(orientation='vertical', size_hint_x=1)
        self.g_name = Label(
            text='', color=WHT, font_size=dp(16), bold=True,
            halign='left', valign='middle',
            size_hint_y=None, height=dp(24))
        self.g_name.bind(size=self.g_name.setter('text_size'))
        self.g_sub = Label(
            text='', color=TXT2, font_size=dp(12),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(16))
        self.g_sub.bind(size=self.g_sub.setter('text_size'))
        gi.add_widget(self.g_name)
        gi.add_widget(self.g_sub)
        self.hdr.add_widget(gi)
        root.add_widget(self.hdr)
        self.sv = ScrollView(do_scroll_x=False)
        self.mb = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(2), padding=[dp(8), dp(8), dp(8), dp(8)])
        self.mb.bind(minimum_height=self.mb.setter('height'))
        self.sv.add_widget(self.mb)
        root.add_widget(self.sv)
        ibar = BoxLayout(
            size_hint_y=None, height=dp(62),
            padding=[dp(6), dp(7), dp(6), dp(7)], spacing=dp(6))
        set_bg(ibar, SURF)
        emoji_btn = Button(
            text='😊', background_normal='', background_color=TR,
            color=TXT2, font_size=dp(20),
            size_hint=(None, 1), width=dp(38))
        emoji_btn.bind(on_release=lambda *a: self._show_emoji())
        ibar.add_widget(emoji_btn)
        self.inp = TextInput(
            hint_text='Сообщение...', multiline=False,
            background_normal='', background_active='',
            background_color=(.12, .14, .18, 1),
            foreground_color=TXT, hint_text_color=TXT3,
            cursor_color=PRI, font_size=dp(15),
            padding=[dp(14), dp(12)])
        def draw_inp(*a):
            self.inp.canvas.before.clear()
            with self.inp.canvas.before:
                Color(.12, .14, .18, 1)
                RoundedRectangle(
                    pos=self.inp.pos, size=self.inp.size,
                    radius=[dp(22)])
        self.inp.bind(
            pos=draw_inp, size=draw_inp,
            on_text_validate=lambda *a: self._send())
        sb = Button(
            text='▶', background_normal='', background_color=TR,
            color=WHT, font_size=dp(22), bold=True,
            size_hint=(None, 1), width=dp(48))
        def draw_sb(*a):
            sb.canvas.before.clear()
            with sb.canvas.before:
                Color(*PRI)
                RoundedRectangle(
                    pos=sb.pos, size=sb.size, radius=[dp(12)])
        sb.bind(pos=draw_sb, size=draw_sb,
                on_release=lambda *a: self._send())
        ibar.add_widget(self.inp)
        ibar.add_widget(sb)
        root.add_widget(ibar)
        self.add_widget(root)

    def load(self, grp):
        self.grp = grp
        self.g_name.text = grp['name']
        n = len(grp.get('members', []))
        self.g_sub.text = f'{n} участников'
        self.g_av.children[0].text = grp.get('init', 'G')
        self._load_msgs()

    def on_enter(self):
        self._timer = Clock.schedule_interval(
            lambda dt: self._poll(), 2)

    def on_leave(self):
        if self._timer: self._timer.cancel()

    def _poll(self):
        if not self.grp: return
        m = DB.grp_msgs(self.grp['id'])
        if len(m) != self._last: self._load_msgs()

    def _load_msgs(self):
        if not self.grp: return
        msgs = DB.grp_msgs(self.grp['id'])
        self._last = len(msgs)
        self.mb.clear_widgets()
        uid = A.me['id']
        for msg in msgs:
            is_out = msg['from'] == uid
            sender = None if is_out else DB.user(msg['from'])
            self.mb.add_widget(self._bubble(msg, is_out, sender))
        Clock.schedule_once(
            lambda dt: setattr(self.sv, 'scroll_y', 0), .05)

    def _bubble(self, msg, is_out, sender=None):
        ts = datetime.fromtimestamp(
            msg.get('ts', 0)).strftime('%H:%M')
        text = msg.get('text', '')
        sn = sender['display_name'].split()[0] if sender else ''
        sc = sender.get('color', '#1E88E5') if sender else '#1E88E5'
        full = (f'[{sn}]\n' if sn else '') + text + f'\n{ts}'
        bg_col = MOUT if is_out else MIN
        max_w = dp(265)
        test = Label(text=full, font_size=dp(14),
                     text_size=(max_w - dp(28), None))
        test.texture_update()
        bw = min(test.texture_size[0] + dp(32), max_w)
        bh = test.texture_size[1] + dp(24)
        bubble = BoxLayout(
            size_hint=(None, None), size=(bw, bh),
            padding=[dp(12), dp(8), dp(12), dp(6)])
        with bubble.canvas.before:
            Color(*bg_col)
            RoundedRectangle(
                pos=(0,0), size=bubble.size, radius=[dp(12)])
        bubble.bind(
            pos=lambda w, *a, c=bg_col: self._rd(w, c),
            size=lambda w, *a, c=bg_col: self._rd(w, c))
        if sn:
            snl = Label(
                text=sn, color=rgb(sc), font_size=dp(12),
                bold=True, halign='left', valign='middle',
                size_hint_y=None, height=dp(18))
            snl.bind(size=snl.setter('text_size'))
            bubble.add_widget(snl)
        lbl = Label(
            text=text + f'\n{ts}', font_size=dp(14), color=TXT,
            halign='left', valign='top',
            text_size=(bw - dp(28), None), size_hint_y=1)
        bubble.add_widget(lbl)
        wrap = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            padding=[0, dp(2), 0, dp(2)], height=bh + dp(4))
        if is_out:
            wrap.add_widget(Widget())
            wrap.add_widget(bubble)
        else:
            wrap.add_widget(bubble)
            wrap.add_widget(Widget())
        return wrap

    def _rd(self, w, col):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*col)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(12)])

    def _send(self):
        text = self.inp.text.strip()
        if not text or not self.grp: return
        self.inp.text = ''
        DB.send_grp(self.grp['id'], A.me['id'], text)
        self._load_msgs()


class UserScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._uid = None
        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)
        self._topbar = make_topbar(
            'Профиль',
            on_back=lambda *a: A.go(A._prev or 'main'))
        root.add_widget(self._topbar)
        sv = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        padding=[0, 0, 0, dp(20)])
        box.bind(minimum_height=box.setter('height'))
        hdr = BoxLayout(orientation='vertical', size_hint_y=None,
                        height=dp(195), spacing=dp(6),
                        padding=[0, dp(22), 0, dp(10)])
        set_bg(hdr, PRI2)
        aw = BoxLayout(size_hint_y=None, height=dp(94))
        aw.add_widget(Widget())
        self.av = make_avatar('?', '#1E88E5', 88)
        aw.add_widget(self.av)
        aw.add_widget(Widget())
        hdr.add_widget(aw)
        self.u_name = Label(
            text='', color=WHT, font_size=dp(21), bold=True,
            halign='center', size_hint_y=None, height=dp(32))
        self.u_sub = Label(
            text='', color=TXT2, font_size=dp(13),
            halign='center', size_hint_y=None, height=dp(22))
        hdr.add_widget(self.u_name)
        hdr.add_widget(self.u_sub)
        box.add_widget(hdr)
        act = BoxLayout(size_hint_y=None, height=dp(72),
                        padding=[dp(16), dp(12)], spacing=dp(10))
        self.msg_btn = make_btn('✉ Написать')
        self.msg_btn.bind(on_release=self._start)
        act.add_widget(self.msg_btn)
        box.add_widget(act)
        box.add_widget(make_divider())
        self.info_box = BoxLayout(
            orientation='vertical', size_hint_y=None, height=0)
        box.add_widget(self.info_box)
        sv.add_widget(box)
        root.add_widget(sv)
        self.add_widget(root)

    def load(self, uid):
        self._uid = uid
        u = DB.user(uid)
        if not u: return
        name = u['display_name']
        if u.get('premium'): name += ' ⭐'
        if u.get('verified'): name += ' ✓'
        if u.get('is_admin'): name += ' 👑'
        self.u_name.text = name
        self.av.children[0].text = u.get('init', '?')
        if u.get('online'):
            self.u_sub.text = 'в сети'
            self.u_sub.color = GRN
        else:
            self.u_sub.text = DB.fmt_seen(u.get('last_seen', 0))
            self.u_sub.color = TXT2
        self.msg_btn.opacity = 0 if uid == A.me['id'] else 1
        self.msg_btn.disabled = uid == A.me['id']
        self.info_box.clear_widgets()
        rows = [
            ('📱', 'Логин',       f"@{u['username']}"),
            ('ℹ',  'Bio',        u.get('bio', '—')),
            ('📞', 'Телефон',     u.get('phone', '') or '—'),
            ('⭐', 'Звёзды',      f"{u.get('stars',0):,}"),
            ('💎', 'Premium',     'Да ✨' if u.get('premium') else 'Нет'),
            ('📅', 'С нами с',   datetime.fromtimestamp(
                u.get('joined', time.time())).strftime('%d.%m.%Y')),
        ]
        self.info_box.height = len(rows) * dp(61)
        for icon, lbl, val in rows:
            row = BoxLayout(size_hint_y=None, height=dp(60),
                            padding=[dp(16), dp(8)], spacing=dp(14))
            set_bg(row, BG)
            row.add_widget(Label(
                text=icon, font_size=dp(22),
                size_hint=(None, 1), width=dp(32)))
            inf = BoxLayout(orientation='vertical')
            ll = Label(
                text=lbl, color=TXT2, font_size=dp(12),
                halign='left', valign='middle',
                size_hint_y=None, height=dp(18))
            ll.bind(size=ll.setter('text_size'))
            vl = Label(
                text=val, color=TXT, font_size=dp(14),
                halign='left', valign='middle',
                size_hint_y=None, height=dp(24))
            vl.bind(size=vl.setter('text_size'))
            inf.add_widget(ll)
            inf.add_widget(vl)
            row.add_widget(inf)
            self.info_box.add_widget(row)
            self.info_box.add_widget(make_divider())

    def _start(self, *a):
        if not self._uid or self._uid == A.me['id']: return
        other = DB.user(self._uid)
        ch = DB.get_chat(A.me['id'], self._uid)
        A.open_chat(ch, other)


class MyProfileScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)
        root.add_widget(make_topbar(
            'Мой профиль',
            on_back=lambda *a: A.go('main'),
            right_items=[('👑', lambda *a: A.go('admin'))]))
        sv = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        padding=[0, 0, 0, dp(20)])
        box.bind(minimum_height=box.setter('height'))
        hdr = BoxLayout(orientation='vertical', size_hint_y=None,
                        height=dp(195), spacing=dp(6),
                        padding=[0, dp(22), 0, dp(10)])
        set_bg(hdr, PRI2)
        aw = BoxLayout(size_hint_y=None, height=dp(94))
        aw.add_widget(Widget())
        self.av = make_avatar('?', '#1E88E5', 88)
        aw.add_widget(self.av)
        aw.add_widget(Widget())
        hdr.add_widget(aw)
        self.nm = Label(
            text='', color=WHT, font_size=dp(20), bold=True,
            halign='center', size_hint_y=None, height=dp(30))
        self.un = Label(
            text='', color=PRI, font_size=dp(13),
            halign='center', size_hint_y=None, height=dp(22))
        hdr.add_widget(self.nm)
        hdr.add_widget(self.un)
        box.add_widget(hdr)
        pills = BoxLayout(size_hint_y=None, height=dp(58),
                          padding=[dp(16), dp(8)], spacing=dp(10))
        sc = BoxLayout(size_hint_x=1, padding=[dp(12), dp(8)],
                       spacing=dp(8))
        set_bg(sc, SURF, 12)
        sc.add_widget(Label(text='⭐', font_size=dp(22),
                            size_hint=(None, 1), width=dp(28)))
        self.sl = Label(text='0', color=GOLD, font_size=dp(17),
                        bold=True)
        sc.add_widget(self.sl)
        pc = BoxLayout(size_hint_x=1, padding=[dp(12), dp(8)],
                       spacing=dp(8))
        set_bg(pc, SURF, 12)
        pc.add_widget(Label(text='💎', font_size=dp(22),
                            size_hint=(None, 1), width=dp(28)))
        self.pl = Label(text='Free', color=TXT2, font_size=dp(15),
                        bold=True)
        pc.add_widget(self.pl)
        pills.add_widget(sc)
        pills.add_widget(pc)
        box.add_widget(pills)
        box.add_widget(make_divider())
        edit = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12)], spacing=dp(10),
                         size_hint_y=None, height=dp(194))
        edit.add_widget(Label(
            text='Изменить профиль', color=TXT2, font_size=dp(12),
            halign='left', size_hint_y=None, height=dp(20)))
        self.inp_n = make_input('Отображаемое имя')
        self.inp_b = make_input('Bio / статус')
        sv_btn = make_btn('💾 Сохранить')
        sv_btn.bind(on_release=self._save)
        edit.add_widget(self.inp_n)
        edit.add_widget(self.inp_b)
        edit.add_widget(sv_btn)
        box.add_widget(edit)
        box.add_widget(make_divider())
        btns = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12)], spacing=dp(10),
                         size_hint_y=None, height=dp(222))
        self.adm_btn = make_btn('👑 Админ-панель', bg=ADMP)
        self.adm_btn.bind(on_release=lambda *a: A.go('admin'))
        av_btn = make_btn('🎨 Сменить аватарку', bg=(.20,.22,.28,1))
        av_btn.bind(on_release=lambda *a: A.go('avatar'))
        set_btn = make_btn('⚙ Настройки', bg=SURF2)
        set_btn.bind(on_release=lambda *a: A.go('settings'))
        logout = make_btn('🚪 Выйти', bg=RED)
        logout.bind(on_release=self._logout)
        btns.add_widget(self.adm_btn)
        btns.add_widget(av_btn)
        btns.add_widget(set_btn)
        btns.add_widget(logout)
        box.add_widget(btns)
        sv.add_widget(box)
        root.add_widget(sv)
        self.add_widget(root)

    def on_enter(self):
        u = A.me
        if not u: return
        f = DB.user(u['id'])
        if f: A.me = f; DB.save_sess(f); u = f
        name = u.get('display_name', '')
        if u.get('premium'): name += ' ⭐'
        if u.get('verified'): name += ' ✓'
        self.nm.text = name
        self.un.text = f"@{u.get('username','')} · ID {u['id']}"
        self.av.children[0].text = u.get('init', '?')
        self.sl.text = f"{u.get('stars',0):,}"
        self.pl.text = 'Premium ✨' if u.get('premium') else 'Free'
        self.pl.color = GOLD if u.get('premium') else TXT2
        self.inp_n.text = u.get('display_name', '')
        self.inp_b.text = u.get('bio', '')
        self.adm_btn.opacity = 1 if u.get('is_admin') else 0
        self.adm_btn.disabled = not u.get('is_admin')

    def _save(self, *a):
        nm = self.inp_n.text.strip()
        if not nm: return
        init = ''.join(w[0].upper() for w in nm.split()[:2])
        DB.upd(A.me['id'], {
            'display_name': nm,
            'bio': self.inp_b.text.strip(),
            'init': init or nm[:2].upper()
        })
        f = DB.user(A.me['id'])
        if f: A.me = f; DB.save_sess(f)
        self.on_enter()
        show_popup('✅', 'Профиль сохранён!')

    def _logout(self, *a):
        show_popup('Выход', 'Выйти из аккаунта?',
                   ok_text='Выйти', cancel=True,
                   on_ok=lambda: (
                       DB.clear_sess(),
                       setattr(A, 'me', None),
                       A.go('login')))


EMOJI_AVATARS = [
    ('😀','Счастливый'), ('😎','Крутой'), ('🤩','Звезда'),
    ('😈','Дьявол'),    ('🤖','Робот'),   ('👾','Пришелец'),
    ('🦊','Лис'),       ('🐱','Котик'),   ('🐺','Волк'),
    ('🦁','Лев'),       ('🐸','Лягушка'), ('🦋','Бабочка'),
    ('🔥','Огонь'),     ('⚡','Молния'),  ('🌙','Луна'),
    ('🌈','Радуга'),    ('💎','Алмаз'),   ('👑','Корона'),
    ('🚀','Ракета'),    ('🎭','Маска'),   ('🎨','Художник'),
    ('🎮','Геймер'),    ('🎸','Рокер'),   ('🏆','Чемпион'),
]

AVATAR_COLORS_LIST = [
    ('#1E88E5', 'Синий'),   ('#43A047', 'Зелёный'),
    ('#E53935', 'Красный'), ('#FB8C00', 'Оранжевый'),
    ('#8E24AA', 'Фиолет.'), ('#00ACC1', 'Голубой'),
    ('#D81B60', 'Розовый'), ('#6D4C41', 'Коричн.'),
    ('#00897B', 'Бирюзов.'), ('#F4511E', 'Коралл'),
]


class AvatarPickerScreen(Screen):
    """Экран выбора аватарки — эмодзи + цвет фона"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self._chosen_emoji = '😎'
        self._chosen_color = '#1E88E5'

        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)
        root.add_widget(make_topbar(
            '🎨 Выбор аватарки',
            on_back=lambda *a: A.go(A._prev or 'myprofile')))

        sv = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        padding=[dp(12), dp(12)], spacing=dp(14))
        box.bind(minimum_height=box.setter('height'))

        prev_row = BoxLayout(orientation='vertical',
                             size_hint_y=None, height=dp(120),
                             spacing=dp(8))
        prev_box = BoxLayout(size_hint_y=None, height=dp(90))
        prev_box.add_widget(Widget())
        self.preview = make_avatar(self._chosen_emoji,
                                   self._chosen_color, 82)
        prev_box.add_widget(self.preview)
        prev_box.add_widget(Widget())
        prev_row.add_widget(prev_box)
        self.prev_lbl = Label(
            text='Предпросмотр', color=TXT2, font_size=dp(12),
            size_hint_y=None, height=dp(20))
        prev_row.add_widget(self.prev_lbl)
        box.add_widget(prev_row)
        box.add_widget(make_divider())

        box.add_widget(Label(
            text='Выберите эмодзи', color=PRI, font_size=dp(13),
            bold=True, halign='left',
            size_hint_y=None, height=dp(26)))
        self.emoji_grid = GridLayout(
            cols=6, size_hint_y=None, spacing=dp(6),
            padding=[dp(4), dp(4)])
        self.emoji_grid.bind(
            minimum_height=self.emoji_grid.setter('height'))
        for emoji, name in EMOJI_AVATARS:
            btn = Button(
                text=emoji,
                background_normal='',
                background_color=SURF,
                font_size=dp(26),
                size_hint=(None, None),
                size=(dp(52), dp(52)))
            set_bg_r = lambda w, *a, c=SURF: None
            btn.bind(
                on_release=lambda x, e=emoji: self._pick_emoji(e))
            self.emoji_grid.add_widget(btn)
        box.add_widget(self.emoji_grid)
        box.add_widget(make_divider())

        box.add_widget(Label(
            text='Цвет фона', color=PRI, font_size=dp(13),
            bold=True, halign='left',
            size_hint_y=None, height=dp(26)))
        color_grid = GridLayout(
            cols=5, size_hint_y=None, height=dp(108),
            spacing=dp(6), padding=[dp(4), dp(4)])
        for col_hex, col_name in AVATAR_COLORS_LIST:
            cb = Button(
                text=col_name,
                background_normal='',
                background_color=rgb(col_hex),
                color=WHT, font_size=dp(10), bold=True,
                size_hint=(None, None),
                size=(dp(66), dp(44)))
            cb.bind(
                on_release=lambda x, c=col_hex: self._pick_color(c))
            color_grid.add_widget(cb)
        box.add_widget(color_grid)
        box.add_widget(Widget(size_hint_y=None, height=dp(8)))

        save_btn = make_btn('💾 Сохранить аватарку', h=52)
        save_btn.bind(on_release=self._save)
        box.add_widget(save_btn)
        box.add_widget(Widget(size_hint_y=None, height=dp(20)))
        sv.add_widget(box)
        root.add_widget(sv)
        self.add_widget(root)

    def on_enter(self):
        u = A.me
        if u:
            self._chosen_emoji = u.get('init', '😎')
            if len(self._chosen_emoji) == 1:
                self._chosen_emoji = '😎'
            self._chosen_color = u.get('color', '#1E88E5')
            self._update_preview()

    def _pick_emoji(self, e):
        self._chosen_emoji = e
        self._update_preview()

    def _pick_color(self, c):
        self._chosen_color = c
        self._update_preview()

    def _update_preview(self):
        self.preview.children[0].text = self._chosen_emoji
        col = rgb(self._chosen_color)
        self.preview._c = col
        self.preview._d()

    def _save(self, *a):
        if not A.me: return
        DB.upd(A.me['id'], {
            'emoji_avatar': self._chosen_emoji,
            'color': self._chosen_color,
            'init': self._chosen_emoji,
        })
        f = DB.user(A.me['id'])
        if f:
            A.me = f
            DB.save_sess(f)
        show_popup('✅', 'Аватарка обновлена!')
        Clock.schedule_once(
            lambda dt: A.go(A._prev or 'myprofile'), 1.0)


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        set_bg(root, BG)
        root.add_widget(make_topbar(
            'Настройки',
            on_back=lambda *a: A.go('myprofile')))
        sv = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        padding=[dp(16), dp(16)], spacing=dp(10))
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(
            text='СМЕНА ПАРОЛЯ', color=PRI, font_size=dp(12),
            bold=True, halign='left',
            size_hint_y=None, height=dp(28)))
        self.op = make_input('Текущий пароль', pwd=True)
        self.np = make_input('Новый пароль', pwd=True)
        self.np2 = make_input('Повторите', pwd=True)
        ch = make_btn('🔑 Сменить пароль', bg=SURF2)
        ch.bind(on_release=self._chpwd)
        for w in [self.op, self.np, self.np2, ch]:
            box.add_widget(w)
        box.add_widget(make_divider())
        box.add_widget(Label(
            text='PyGram v5 · Python + Kivy · Android 14+',
            color=TXT3, font_size=dp(12), halign='center',
            size_hint_y=None, height=dp(40)))
        sv.add_widget(box)
        root.add_widget(sv)
        self.add_widget(root)

    def _chpwd(self, *a):
        if hashlib.sha256(
                self.op.text.encode()).hexdigest() != \
                A.me.get('pw', ''):
            show_popup('Ошибка', 'Неверный текущий пароль')
            return
        if len(self.np.text) < 5:
            show_popup('Ошибка', 'Мин. 5 символов')
            return
        if self.np.text != self.np2.text:
            show_popup('Ошибка', 'Пароли не совпадают')
            return
        DB.upd(A.me['id'], {
            'pw': hashlib.sha256(
                self.np.text.encode()).hexdigest()})
        f = DB.user(A.me['id'])
        if f: A.me = f; DB.save_sess(f)
        for w in [self.op, self.np, self.np2]:
            w.text = ''
        show_popup('✅', 'Пароль изменён!')


class AdminScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sel = None
        root = BoxLayout(orientation='vertical')
        set_bg(root, ADMBG)
        root.add_widget(make_topbar(
            '👑 Панель администратора',
            sub='Управление платформой',
            on_back=lambda *a: A.go('myprofile')))
        self.sv = ScrollView(do_scroll_x=False)
        self.box = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(12), dp(12), dp(12), dp(24)],
            spacing=dp(10))
        self.box.bind(minimum_height=self.box.setter('height'))
        self.sv.add_widget(self.box)
        root.add_widget(self.sv)
        self.add_widget(root)

    def on_enter(self):
        if not A.me or not A.me.get('is_admin'):
            A.go('main')
            return
        self._build()

    def _sec(self, t):
        l = Label(
            text=t, color=(.4, .8, 1, 1), font_size=dp(12),
            bold=True, halign='left',
            size_hint_y=None, height=dp(28))
        l.bind(size=l.setter('text_size'))
        return l

    def _build(self):
        self.box.clear_widgets()
        self.box.add_widget(self._sec('📊 СТАТИСТИКА'))
        st = DB.stats()
        srow = BoxLayout(size_hint_y=None, height=dp(88),
                         spacing=dp(8))
        for ic, lb, val, col in [
            ('👥', 'Юзеры',   str(st['users']),   PRI),
            ('🟢', 'Онлайн',  str(st['online']),  GRN),
            ('💬', 'Сообщ.',  str(st['msgs']),    (.4,.7,1,1)),
            ('💎', 'Premium', str(st['premium']), GOLD),
        ]:
            card = BoxLayout(orientation='vertical', size_hint_x=1,
                             padding=[dp(8), dp(8)])
            set_bg(card, SURF, 12)
            card.add_widget(Label(
                text=ic, font_size=dp(22),
                size_hint_y=None, height=dp(26)))
            card.add_widget(Label(
                text=val, color=col, font_size=dp(18),
                bold=True, size_hint_y=None, height=dp(24)))
            card.add_widget(Label(
                text=lb, color=TXT2, font_size=dp(10),
                size_hint_y=None, height=dp(16)))
            srow.add_widget(card)
        self.box.add_widget(srow)

        self.box.add_widget(self._sec('👥 ВСЕ ПОЛЬЗОВАТЕЛИ'))
        users = DB.users()
        for uid, u in sorted(
                users.items(),
                key=lambda x: x[1].get('display_name', '')):
            self.box.add_widget(self._user_row(u))
            self.box.add_widget(make_divider())

        self.box.add_widget(self._sec('✅ ВЫБРАННЫЙ ПОЛЬЗОВАТЕЛЬ'))
        self.sel_card = BoxLayout(
            orientation='vertical', size_hint_y=None,
            height=dp(50), padding=[dp(14), dp(8)])
        set_bg(self.sel_card, SURF, 14)
        self.sel_lbl = Label(
            text='↑ Нажмите "Выбрать" рядом с пользователем',
            color=TXT2, font_size=dp(13), halign='center')
        self.sel_lbl.bind(size=self.sel_lbl.setter('text_size'))
        self.sel_card.add_widget(self.sel_lbl)
        self.box.add_widget(self.sel_card)

        self.box.add_widget(self._sec('🔍 ПОИСК'))
        sr = BoxLayout(size_hint_y=None, height=dp(52),
                       spacing=dp(8))
        self.s_inp = make_input('Логин или имя...', h=48)
        sb = make_btn('🔎', h=48)
        sb.size_hint_x = None
        sb.width = dp(54)
        sb.bind(on_release=lambda *a: self._find())
        sr.add_widget(self.s_inp)
        sr.add_widget(sb)
        self.box.add_widget(sr)

        self.box.add_widget(self._sec('⚡ ДЕЙСТВИЯ'))
        actions = [
            ('📱 Выдать номер',     SURF2, self._issue_phone),
            ('📋 Все номера',       SURF2, self._show_phones),
            ('⭐ +100 звёзд',      GOLD,  lambda *a: self._stars(100)),
            ('⭐ +1000 звёзд',     GOLD,  lambda *a: self._stars(1000)),
            ('⭐ +10000 звёзд',    GOLD,  lambda *a: self._stars(10000)),
            ('💎 Дать Premium',    GOLD,  lambda *a: self._prem(True)),
            ('💎 Убрать Premium',  SURF2, lambda *a: self._prem(False)),
            ('✅ Верифицировать',  GRN,   lambda *a: self._ver(True)),
            ('✕ Снять верифик.',   SURF2, lambda *a: self._ver(False)),
            ('⛔ Заблокировать',   RED,   lambda *a: self._ban(True)),
            ('✅ Разблокировать',  GRN,   lambda *a: self._ban(False)),
            ('👑 Сделать Админом', ADMP,  lambda *a: self._adm(True)),
            ('✕ Снять Права',      SURF2, lambda *a: self._adm(False)),
        ]
        for txt, col, fn in actions:
            b = make_btn(txt, bg=col, h=46)
            b.bind(on_release=fn)
            self.box.add_widget(b)

        self.box.add_widget(self._sec('✏ ИЗМЕНИТЬ @ЛОГИН'))
        ur = BoxLayout(size_hint_y=None, height=dp(52),
                       spacing=dp(8))
        self.uname_inp = make_input('Новый @логин', h=48)
        ub = make_btn('OK', h=48)
        ub.size_hint_x = None
        ub.width = dp(58)
        ub.bind(on_release=self._change_uname)
        ur.add_widget(self.uname_inp)
        ur.add_widget(ub)
        self.box.add_widget(ur)

    def _user_row(self, u):
        row = BoxLayout(size_hint_y=None, height=dp(60),
                        padding=[dp(8), dp(6)], spacing=dp(10))
        set_bg(row, BG)
        row.add_widget(make_avatar(
            u.get('init', '?'), u.get('color', '#1E88E5'), 40))
        inf = BoxLayout(orientation='vertical', size_hint_x=1)
        name = u['display_name']
        b = ''
        if u.get('premium'):  b += ' 💎'
        if u.get('verified'): b += ' ✅'
        if u.get('is_admin'): b += ' 👑'
        if u.get('banned'):   b += ' ⛔'
        nl = Label(
            text=name + b, color=TXT, font_size=dp(13),
            bold=True, halign='left', valign='middle')
        nl.bind(size=nl.setter('text_size'))
        ul = Label(
            text=f"@{u['username']} · ⭐{u.get('stars',0):,}",
            color=TXT2, font_size=dp(12),
            halign='left', valign='middle')
        ul.bind(size=ul.setter('text_size'))
        inf.add_widget(nl)
        inf.add_widget(ul)
        row.add_widget(inf)
        sel = Button(
            text='Выбрать',
            background_normal='', background_color=ADMP,
            color=WHT, font_size=dp(12), bold=True,
            size_hint=(None, 1), width=dp(72))
        sel.bind(on_release=lambda x, usr=u: self._select(usr))
        row.add_widget(sel)
        return row

    def _select(self, u):
        self._sel = DB.user(u['id']) or u
        self._refresh_sel()

    def _refresh_sel(self):
        if not self._sel: return
        u = DB.user(self._sel['id']) or self._sel
        self._sel = u
        self.sel_card.clear_widgets()
        self.sel_card.height = dp(90)
        name = u['display_name']
        b = ''
        if u.get('premium'):  b += ' 💎'
        if u.get('verified'): b += ' ✅'
        if u.get('is_admin'): b += ' 👑'
        if u.get('banned'):   b += ' ⛔'
        nl = Label(
            text=name + b, color=WHT, font_size=dp(15),
            bold=True, halign='center',
            size_hint_y=None, height=dp(26))
        nl.bind(size=nl.setter('text_size'))
        ul = Label(
            text=f"@{u['username']} · {u['id']}",
            color=PRI, font_size=dp(12), halign='center',
            size_hint_y=None, height=dp(20))
        ul.bind(size=ul.setter('text_size'))
        dl = Label(
            text=f"⭐{u.get('stars',0):,}  📞{u.get('phone','—')}  "
                 f"{'🔴Ban' if u.get('banned') else '🟢OK'}",
            color=TXT2, font_size=dp(12), halign='center',
            size_hint_y=None, height=dp(20))
        dl.bind(size=dl.setter('text_size'))
        self.sel_card.add_widget(nl)
        self.sel_card.add_widget(ul)
        self.sel_card.add_widget(dl)

    def _find(self):
        q = self.s_inp.text.strip()
        if not q: return
        results = DB.search(q)
        if results:
            self._select(results[0])
            show_popup('✅', f'Найден: @{results[0]["username"]}')
        else:
            show_popup('❌', f'Не найдено: {q}')

    def _need(self):
        if not self._sel:
            show_popup('⚠️', 'Сначала выберите пользователя')
            return False
        return True

    def _issue_phone(self, *a):
        if not self._need(): return
        ph, new = DB.issue_phone(self._sel['id'])
        self._refresh_sel()
        show_popup('📱', f'{"Выдан:" if new else "Уже был:"}\n{ph}')

    def _show_phones(self, *a):
        issued = DB.issued_phones()
        if not issued:
            show_popup('📋', 'Номеров не выдано')
            return
        us = DB.users()
        lines = []
        for iss in issued[-20:]:
            u = us.get(iss['uid'], {})
            lines.append(f"@{u.get('username','?')}: {iss['phone']}")
        show_popup('📋 Номера', '\n'.join(lines[-15:]))

    def _stars(self, n):
        if not self._need(): return
        total = DB.add_stars(self._sel['id'], n)
        self._refresh_sel()
        show_popup('⭐', f'+{n:,} звёзд\nВсего: {total:,}')

    def _prem(self, val):
        if not self._need(): return
        DB.upd(self._sel['id'], {'premium': val})
        self._refresh_sel()
        show_popup('💎', 'Premium выдан!' if val else 'Убран')

    def _ver(self, val):
        if not self._need(): return
        DB.upd(self._sel['id'], {'verified': val})
        self._refresh_sel()
        show_popup('✅', 'Верификация выдана' if val else 'Снята')

    def _ban(self, val):
        if not self._need(): return
        if self._sel['id'] == A.me['id']:
            show_popup('Ошибка', 'Нельзя заблокировать себя')
            return
        DB.upd(self._sel['id'], {'banned': val, 'online': False})
        self._refresh_sel()
        show_popup('⛔' if val else '✅',
                   'Заблокирован' if val else 'Разблокирован')

    def _adm(self, val):
        if not self._need(): return
        if not val and self._sel['id'] == A.me['id']:
            show_popup('Ошибка', 'Нельзя снять права с себя')
            return
        DB.upd(self._sel['id'], {'is_admin': val, 'verified': val})
        self._refresh_sel()
        show_popup('👑', 'Права выданы' if val else 'Сняты')

    def _change_uname(self, *a):
        if not self._need(): return
        nw = self.uname_inp.text.strip().lstrip('@')
        if len(nw) < 3:
            show_popup('Ошибка', 'Мин. 3 символа')
            return
        us = DB.users()
        for u in us.values():
            if u['username'].lower() == nw.lower() and \
               u['id'] != self._sel['id']:
                show_popup('Ошибка', 'Логин занят')
                return
        DB.upd(self._sel['id'], {'username': nw})
        self.uname_inp.text = ''
        self._refresh_sel()
        show_popup('✅', f'Логин: @{nw}')


DB = None
A  = None


if __name__ == '__main__':

    class PyGram(App):
        def __init__(self, **kw):
            super().__init__(**kw)
            self.me = None
            self.title = 'PyGram'
            self._prev = 'main'

        def build(self):
            global DB, A
            DB = DB_cls()
            A = self
            Window.clearcolor = BG
            self.sm = ScreenManager(transition=NoTransition())
            for name, cls in [
                ('login',     LoginScreen),
                ('reg',       RegScreen),
                ('main',      MainScreen),
                ('chat',      ChatScreen),
                ('group',     GroupScreen),
                ('user',      UserScreen),
                ('myprofile', MyProfileScreen),
                ('avatar',    AvatarPickerScreen),
                ('settings',  SettingsScreen),
                ('admin',     AdminScreen),
            ]:
                self.sm.add_widget(cls(name=name))
            saved = DB.load_sess()
            if saved:
                fresh = DB.user(saved.get('id', ''))
                self.me = fresh or saved
                self.sm.current = 'main'
            else:
                self.sm.current = 'login'
            return self.sm

        def go(self, screen):
            self._prev = self.sm.current
            self.sm.current = screen

        def open_chat(self, chat, other):
            self._prev = self.sm.current
            s = self.sm.get_screen('chat')
            s.load(chat, other)
            self.sm.current = 'chat'

        def open_group(self, grp):
            self._prev = self.sm.current
            s = self.sm.get_screen('group')
            s.load(grp)
            self.sm.current = 'group'

        def open_user(self, uid):
            self._prev = self.sm.current
            s = self.sm.get_screen('user')
            s.load(uid)
            self.sm.current = 'user'

        def on_pause(self):  return True
        def on_resume(self): pass

    DB_cls = DB.__class__
    PyGram().run()