# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'photo_maker.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import sys
import os
import io

# Ensure UTF-8 console and log encoding on Windows so Khmer text never throws UnicodeEncodeError
if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Configure application directory and Python runtime
if getattr(sys, 'frozen', False):
    _app_dir = os.path.dirname(sys.executable)
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))

_internal_python = os.path.join(_app_dir, '_internal', 'python.exe')

# If launched with an external Python (e.g. system Python 3.14 via IDE/Terminal),
# automatically hand over execution to the bundled _internal\python.exe environment
# where all studio models, PyTorch, OpenCV, CustomTkinter, and Tcl 8.6.12 are fully installed.
if not getattr(sys, 'frozen', False) and os.path.exists(_internal_python):
    _cur_exe = os.path.normcase(os.path.abspath(sys.executable))
    _tgt_exe = os.path.normcase(os.path.abspath(_internal_python))
    if _cur_exe != _tgt_exe:
        import subprocess
        _env = os.environ.copy()
        _env['PYTHONIOENCODING'] = 'utf-8'
        _env['PYTHONUTF8'] = '1'
        try:
            _ret = subprocess.call([_internal_python] + sys.argv, env=_env)
            sys.exit(_ret)
        except KeyboardInterrupt:
            sys.exit(0)

# Configure Tcl/Tk library paths ONLY for the bundled _internal Python runtime or frozen executable
_is_internal = getattr(sys, 'frozen', False) or (
    os.path.exists(_internal_python) and os.path.normcase(os.path.abspath(sys.executable)) == os.path.normcase(os.path.abspath(_internal_python))
)

if _is_internal:
    _tcl_data = os.path.join(_app_dir, '_internal', '_tcl_data')
    _tk_data = os.path.join(_app_dir, '_internal', '_tk_data')

    if os.path.exists(_tcl_data):
        _tcl_norm = _tcl_data.replace('\\', '/')
        if not _tcl_norm.lower().startswith('c:') and not _tcl_norm.startswith('//?/'):
            os.environ['TCL_LIBRARY'] = '//?/' + _tcl_norm
        else:
            os.environ['TCL_LIBRARY'] = _tcl_data

    if os.path.exists(_tk_data):
        _tk_norm = _tk_data.replace('\\', '/')
        if not _tk_norm.lower().startswith('c:') and not _tk_norm.startswith('//?/'):
            os.environ['TK_LIBRARY'] = '//?/' + _tk_norm
        else:
            os.environ['TK_LIBRARY'] = _tk_data

# Configure offline AI models path
_cand_models = [
    os.path.join(_app_dir, 'AI_Models'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI_Models'),
    os.path.join(os.path.dirname(sys.executable), 'AI_Models'),
    os.path.join(os.path.abspath('.'), 'AI_Models'),
    os.path.join(os.path.abspath('.'), '_internal', 'AI_Models')
]
_ai_models_dir = None
for _cand in _cand_models:
    if os.path.exists(_cand):
        _ai_models_dir = _cand
        break

if _ai_models_dir:
    os.environ['U2NET_HOME'] = _ai_models_dir
    os.environ['REMBG_HOME'] = _ai_models_dir
os.environ['MODEL_CHECKSUM_DISABLED'] = '1'

# Prevent Numba caching errors in packaged environments
try:
    from numba.core.dispatcher import Dispatcher
    Dispatcher.enable_caching = lambda self: None
except Exception:
    pass

APP_VERSION = "3.0.0"
DEFAULT_UPDATE_URL = "https://raw.githubusercontent.com/khinratana087210-arch/RN-Photography/main/version.json"

import subprocess
import json
import urllib.request
import urllib.parse
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageEnhance, ImageTk, ImageDraw, ImageFilter
import io
import threading
import cv2
import numpy as np
import math
import colorsys
import sys
import os
import shutil
import warnings
import sys
import os
import customtkinter
customtkinter.set_appearance_mode('Dark')
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['TQDM_DISABLE'] = '1'
import customtkinter as ctk
import tkinter as tk
try:
    import mediapipe as mp
except ImportError:
    pass
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    target = os.path.join(base_path, relative_path)
    if not os.path.exists(target):
        internal_target = os.path.join(base_path, '_internal', relative_path)
        if os.path.exists(internal_target):
            return internal_target
    return target
ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('dark-blue')

# --- Optimized Smooth & Responsive MouseWheel Scrolling for CTkScrollableFrame ---
def _optimized_check_if_valid_scroll(self, widget):
    if widget is None:
        return False
    if widget == self._parent_canvas:
        return True
    if isinstance(widget, (ctk.CTkScrollbar, ctk.CTkSlider, ctk.CTkTextbox)):
        return False
    try:
        if str(widget).startswith(str(self._parent_canvas)):
            return True
    except Exception:
        pass
    w = getattr(widget, 'master', None)
    while w is not None:
        if w == self._parent_canvas:
            return True
        w = getattr(w, 'master', None)
    return False

def _optimized_mouse_wheel_all(self, event):
    if not self._check_if_valid_scroll(event.widget):
        return

    # Responsive scroll step: ~42px per notch on Windows (clean, natural, immediate)
    if sys.platform.startswith("win"):
        delta = -int(event.delta / 2.8) if getattr(event, 'delta', 0) else 0
    elif sys.platform == "darwin":
        delta = -int(event.delta * 2) if getattr(event, 'delta', 0) else 0
    else:
        if getattr(event, 'num', None) == 4:
            delta = -40
        elif getattr(event, 'num', None) == 5:
            delta = 40
        else:
            delta = 0

    if delta == 0:
        return

    try:
        if getattr(self, '_shift_pressed', False):
            if hasattr(self, '_parent_canvas') and self._parent_canvas.winfo_exists() and self._parent_canvas.xview() != (0.0, 1.0):
                self._parent_canvas.xview("scroll", delta, "units")
        else:
            if hasattr(self, '_parent_canvas') and self._parent_canvas.winfo_exists() and self._parent_canvas.yview() != (0.0, 1.0):
                self._parent_canvas.yview("scroll", delta, "units")
    except Exception:
        pass

ctk.CTkScrollableFrame._check_if_valid_scroll = _optimized_check_if_valid_scroll
ctk.CTkScrollableFrame._mouse_wheel_all = _optimized_mouse_wheel_all

class PhotoMakerApp(ctk.CTk):
    def report_callback_exception(self, exc, val, tb):
        import traceback
        err_str = "".join(traceback.format_exception(exc, val, tb))
        try:
            from tkinter import messagebox
            messagebox.showerror('បញ្ហា', f'មានបញ្ហាក្នុងដំណើរការ:\n{val}')
        except Exception:
            pass

    def invalidate_bg_cache(self):
        self._bg_cache = None
        self._bg_base_image = None

    def register_rgb_widget(self, widget, hover_bw=2):
        return widget

    def register_all_rgb_buttons(self, container=None):
        pass


    def on_canvas_configure(self, event=None):
        if not getattr(self, 'processed_image', None):
            self.render_empty_canvas()

    def render_empty_canvas(self):
        self.canvas.delete('all')
        self.canvas.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            cw, ch = 760, 600
        cx, cy = cw // 2, ch // 2
        bx, by = 260, 135
        self.canvas.create_rectangle(cx - bx, cy - by, cx + bx, cy + by, outline='#151F32', width=1, dash=(4, 4), tags='empty_elem')
        cor = 18
        self.canvas.create_line(cx - bx, cy - by + cor, cx - bx, cy - by, cx - bx + cor, cy - by, fill='#00F2FE', width=2, tags='empty_elem')
        self.canvas.create_line(cx + bx - cor, cy - by, cx + bx, cy - by, cx + bx, cy - by + cor, fill='#00F2FE', width=2, tags='empty_elem')
        self.canvas.create_line(cx - bx, cy + by - cor, cx - bx, cy + by, cx - bx + cor, cy + by, fill='#8B5CF6', width=2, tags='empty_elem')
        self.canvas.create_line(cx + bx - cor, cy + by, cx + bx, cy + by, cx + bx, cy + by - cor, fill='#8B5CF6', width=2, tags='empty_elem')
        self.canvas.create_text(cx, cy - 65, text='✦ STUDIO WORKSPACE ✦', fill='#00F2FE', font=('Segoe UI', 11, 'bold'), tags='empty_elem')
        self.empty_text = self.canvas.create_text(
            cx, cy - 10,
            text='សូមបញ្ចូលរូបថតដើម្បីចាប់ផ្ដើមកាត់ត\n(Upload photo or drag and drop)',
            fill='#F1F5F9', font=('Khmer OS Battambang', 15, 'bold'), justify='center', tags='empty_elem'
        )
        self.canvas.create_text(
            cx, cy + 50,
            text='🖱️ Scroll Mouse ដើម្បី Zoom  •  🖐️ Drag Mouse ដើម្បីផ្លាស់ទីរូប',
            fill='#64748B', font=('Khmer OS Battambang', 11), justify='center', tags='empty_elem'
        )
        self.canvas.create_text(
            cx, cy + 85,
            text='Offline AI Powered • 1200 DPI Studio Quality',
            fill='#334155', font=('Segoe UI', 9, 'italic'), justify='center', tags='empty_elem'
        )

    def __init__(self):
        super().__init__()
        self.title('RN Photography v3.0 - Professional Studio Edition')
        self.withdraw()
        self.show_splash_screen()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = min(1400, max(1240, int(sw * 0.90)))
        h = min(880, max(780, int(sh * 0.88)))
        x = max(0, int(sw / 2 - w / 2))
        y = max(0, int(sh / 2 - h / 2) - 15)
        self.geometry(f'{w}x{h}+{x}+{y}')
        self.minsize(1100, 680)
        self.configure(fg_color='#07090E')
        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('app_icon.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            self.iconbitmap(ico_path)
        except Exception:
            try:
                logo_ico_cand = resource_path('RNPHOTOGRAPHY_orig.png')
                if not os.path.exists(logo_ico_cand):
                    logo_ico_cand = resource_path('logo.png')
                icon_img = ImageTk.PhotoImage(Image.open(logo_ico_cand))
                self.iconphoto(True, icon_img)
            except Exception as e:
                print('បញ្ហា Icon:', e)
        self.font_title = ctk.CTkFont(family='Arial Black', size=24, weight='bold')
        self.font_bold = ctk.CTkFont(family='Khmer OS Battambang', size=13, weight='bold')
        self.font_text = ctk.CTkFont(family='Khmer OS Battambang', size=12)
        self.font_btn = ctk.CTkFont(family='Khmer OS Battambang', size=13)
        self.font_btn_bold = ctk.CTkFont(family='Khmer OS Battambang', size=13, weight='bold')
        self.font_version = ctk.CTkFont(family='Segoe UI', size=11, weight='bold')
        self.original_image_path = None
        self.processed_image = None
        self.output_dpi = (1200, 1200)
        self.undo_stack = []
        self.redo_stack = []
        self.action_counts = {'bg_blue': 0, 'bg_white': 0, 'bg_custom': 0, 'enhance': 0, 'color': 0, 'makeup': 0, 'retouch_studio': 0, 'lighting': 0, 'upscale': 0, 'lut': 0, 'crop_3x4': 0, 'crop_4x6': 0, 'manual_crop': 0, 'spot_heal': 0, 'live_makeup': 0, 'liquify': 0, 'eraser': 0, 'auto_align': 0, 'symmetry_studio': 0}
        self.check_labels = {}
        self.zoom_level = 1.0
        self.canvas_img_x = 0
        self.canvas_img_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_mouse_x = 0
        self.current_mouse_y = 0
        self.tk_image = None
        self.healing_active = False
        self.lips_brush_active = False
        self.eraser_active = False
        self.liquify_active = False
        self.heal_mask = None
        self.heal_mask_soft = None
        self.lips_mask_layer = None
        self.eraser_cv = None
        self.liq_has_moved = False
        self._canvas_update_scheduled = False
        self.light_panel_open = False
        self._makeup_after_id = None
        self._light_after_id = None
        self.bg_session = None
        self.bg_model_name = 'birefnet-general-lite'
        self.loaded_bg_model = None
        self._bg_cache = None
        self._bg_base_image = None
        self.face_det_model = None
        self._rotate_base_image = None
        self._rotate_base_suit = None
        self.ps_mode = False
        self.ps_image_path = None
        self.ps_in_path = None
        self.ps_out_path = None
        if len(sys.argv) > 1 and sys.argv[1] == 'ps_mode':
            self.ps_mode = True
            if len(sys.argv) > 2:
                self.ps_image_path = sys.argv[2]
        elif len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            self.ps_image_path = sys.argv[1]

        # Layout Frames
        self.frame_left = ctk.CTkScrollableFrame(self, width=375, corner_radius=0, fg_color='#0D111A')
        self.frame_left.pack(side='left', fill='y')

        self.frame_tools = ctk.CTkScrollableFrame(self, width=175, corner_radius=0, fg_color='#0A0E17')
        self.frame_tools.pack(side='right', fill='y')

        self.frame_center = ctk.CTkFrame(self, corner_radius=0, fg_color='#06080D')
        self.frame_center.pack(side='left', fill='both', expand=True)

        # Branding Header (Modern & Compact)
        header_box = ctk.CTkFrame(self.frame_left, fg_color='transparent')
        header_box.pack(fill='x', padx=12, pady=(10, 4))

        logo_path = resource_path('RNPHOTOGRAPHY_orig.png')
        if not os.path.exists(logo_path):
            logo_path = resource_path('logo.png')
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                self.logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(46, 46))
                self.lbl_logo = ctk.CTkLabel(header_box, image=self.logo_ctk, text='')
                self.lbl_logo.pack(side='left', padx=(2, 10))
            except Exception:
                pass

        title_col = ctk.CTkFrame(header_box, fg_color='transparent')
        title_col.pack(side='left', fill='both', expand=True)

        self.lbl_title = ctk.CTkLabel(
            title_col, text='RN Photography', font=('Arial Black', 20, 'bold'),
            text_color='#38BDF8', cursor='hand2', anchor='w'
        )
        self.lbl_title.pack(anchor='w', pady=(0, 2))
        self.lbl_title.bind('<Button-1>', lambda event: self.open_about_window())
        def on_enter_title(event):
            self.lbl_title.configure(text_color='#00F2FE')
        def on_leave_title(event):
            self.lbl_title.configure(text_color='#38BDF8')
        self.lbl_title.bind('<Enter>', on_enter_title)
        self.lbl_title.bind('<Leave>', on_leave_title)

        if self.ps_mode:
            self.lbl_version = ctk.CTkLabel(
                title_col, text='⚡ PHOTOSHOP LIVE', font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'),
                text_color='#FF4466', fg_color='#2A0814', corner_radius=6, height=20, padx=6
            )
        else:
            self.lbl_version = ctk.CTkLabel(
                title_col, text='✦ STUDIO EDITION v3.0 ✦', font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'),
                text_color='#00F5A0', fg_color='#062D24', corner_radius=6, height=20, padx=6
            )
        self.lbl_version.pack(anchor='w')

        # Header Pill Row: License Pill + Update Check Button
        pill_row = ctk.CTkFrame(title_col, fg_color='transparent')
        pill_row.pack(anchor='w', pady=(4, 0))

        self.btn_license_pill = ctk.CTkButton(
            pill_row,
            text='🔐 កំពុងពិនិត្យ License...',
            font=('Khmer OS Siemreap', 10, 'bold'),
            height=24,
            corner_radius=6,
            fg_color='#1E2433',
            hover_color='#2A3346',
            border_width=1,
            border_color='#334155',
            text_color='#94A3B8',
            command=self.show_license_info_window,
            cursor='hand2'
        )
        self.btn_license_pill.pack(side='left', padx=(0, 6))

        self.btn_check_update = ctk.CTkButton(
            pill_row,
            text='🔄 Update',
            font=('Khmer OS Siemreap', 10, 'bold'),
            height=24,
            width=78,
            corner_radius=6,
            fg_color='#132038',
            hover_color='#1E3258',
            border_width=1,
            border_color='#38BDF8',
            text_color='#38BDF8',
            command=lambda: self.check_for_updates(manual=True),
            cursor='hand2'
        )
        self.btn_check_update.pack(side='left')
        self.update_license_ui_badge()

        # Silent background auto-check for updates after 3 seconds
        try:
            self.after(3000, self.start_silent_update_check)
        except Exception:
            pass

        # Upload Hero Section
        if not self.ps_mode:
            self.upload_frame = ctk.CTkFrame(self.frame_left, fg_color='#111724', corner_radius=10, border_width=1, border_color='#0284C7')
            self.upload_frame.pack(pady=(2, 6), padx=12, fill='x')
            
            self.btn_guideline = ctk.CTkButton(
                self.upload_frame, text='ℹ️', width=38, height=38, corner_radius=8,
                font=self.font_btn, fg_color='#162032', hover_color='#1E2E4A',
                border_width=1, border_color='#0284C7', command=self.show_guideline_window
            )
            self.btn_guideline.pack(side='left', padx=(6, 4), pady=6)
            
            self.btn_upload = ctk.CTkButton(
                self.upload_frame, text='📥  បញ្ចូលរូបថត (Upload)',
                font=self.font_btn_bold, height=38, corner_radius=8,
                fg_color='#0284C7', hover_color='#0369A1',
                border_width=1, border_color='#38BDF8',
                command=self.upload_image
            )
            self.btn_upload.pack(side='left', expand=True, fill='x', padx=(0, 6), pady=6)
            self.lbl_dummy = ctk.CTkLabel(self.upload_frame, text='', width=0)

        def reg_btn(btn, key):
            btn._base_text = btn.cget('text')
            self.check_labels[key] = btn
            return btn

        # Card 1: Crop & Size
        card_crop = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_crop.pack(pady=4, padx=12, fill='x')

        head_crop = ctk.CTkFrame(card_crop, fg_color='transparent')
        head_crop.pack(fill='x', padx=10, pady=(6, 3))
        ctk.CTkLabel(head_crop, text='●', font=('Arial', 10), text_color='#A855F7').pack(side='left', padx=(0, 5))
        self.label_crop = ctk.CTkLabel(head_crop, text='១. កាត់ទំហំ (Crop & Size)', font=self.font_bold, text_color='#F1F5F9')
        self.label_crop.pack(side='left')

        row_crop_btns = ctk.CTkFrame(card_crop, fg_color='transparent')
        row_crop_btns.pack(fill='x', padx=8, pady=(2, 6))
        row_crop_btns.grid_columnconfigure((0, 1, 2), weight=1, uniform='crop_btn')

        b_c34 = ctk.CTkButton(
            row_crop_btns, text='✂️ 3x4 cm', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#1F1635', hover_color='#2E1065', border_width=1, border_color='#7C3AED', text_color='#E9D5FF',
            command=lambda: self.open_template_crop('3x4')
        )
        b_c34.grid(row=0, column=0, padx=(0, 2), sticky='ew')
        reg_btn(b_c34, 'crop_3x4')

        b_c46 = ctk.CTkButton(
            row_crop_btns, text='✂️ 4x6 cm', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#132337', hover_color='#1E3A8A', border_width=1, border_color='#2563EB', text_color='#DBEAFE',
            command=lambda: self.open_template_crop('4x6')
        )
        b_c46.grid(row=0, column=1, padx=2, sticky='ew')
        reg_btn(b_c46, 'crop_4x6')

        b_mc = ctk.CTkButton(
            row_crop_btns, text='📐 Manual', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#131A26', hover_color='#1E293B', border_width=1, border_color='#334155', text_color='#E2E8F0',
            command=self.open_manual_crop
        )
        b_mc.grid(row=0, column=2, padx=(2, 0), sticky='ew')
        reg_btn(b_mc, 'manual_crop')

        # Card 2: Rotate & Degree
        card_rotate = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_rotate.pack(pady=4, padx=12, fill='x')

        head_rot = ctk.CTkFrame(card_rotate, fg_color='transparent')
        head_rot.pack(fill='x', padx=10, pady=(6, 3))
        ctk.CTkLabel(head_rot, text='●', font=('Arial', 10), text_color='#38BDF8').pack(side='left', padx=(0, 5))
        self.label_rot = ctk.CTkLabel(head_rot, text='២. បង្វិល & ដឺក្រេ (Rotate & Angle)', font=self.font_bold, text_color='#F1F5F9')
        self.label_rot.pack(side='left')

        # Align & Symmetry Buttons (Auto Align & Symmetry Studio)
        row_align_btns = ctk.CTkFrame(card_rotate, fg_color='transparent')
        row_align_btns.pack(fill='x', padx=8, pady=(2, 4))
        row_align_btns.grid_columnconfigure((0, 1), weight=1, uniform='align_btn')

        b_align = ctk.CTkButton(
            row_align_btns, text='🎯 Auto Align', font=('Khmer OS Battambang', 11, 'bold'),
            height=32, corner_radius=8, fg_color='#0E2A38', hover_color='#154359',
            border_width=1, border_color='#00F2FE', text_color='#38BDF8',
            command=self.auto_align_face
        )
        b_align.grid(row=0, column=0, padx=(0, 2), sticky='ew')
        reg_btn(b_align, 'auto_align')

        b_sym = ctk.CTkButton(
            row_align_btns, text='🪞 Symmetry Studio', font=('Khmer OS Battambang', 11, 'bold'),
            height=32, corner_radius=8, fg_color='#1F1635', hover_color='#2E1065',
            border_width=1, border_color='#A855F7', text_color='#E9D5FF',
            command=self.open_symmetry_studio
        )
        b_sym.grid(row=0, column=1, padx=(2, 0), sticky='ew')
        reg_btn(b_sym, 'symmetry_studio')

        # 4 quick buttons in 1 row
        quick_rot_frame = ctk.CTkFrame(card_rotate, fg_color='transparent')
        quick_rot_frame.pack(fill='x', padx=8, pady=2)
        quick_rot_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform='rot_btn')

        ctk.CTkButton(
            quick_rot_frame, text='↺ 90°', font=('Khmer OS Battambang', 11, 'bold'), height=30, width=0, corner_radius=6,
            fg_color='#162032', hover_color='#1E2E4A', border_width=1, border_color='#0284C7', text_color='#38BDF8',
            command=lambda: self.rotate_quick(90)
        ).grid(row=0, column=0, padx=(0, 2), sticky='ew')

        ctk.CTkButton(
            quick_rot_frame, text='↻ 90°', font=('Khmer OS Battambang', 11, 'bold'), height=30, width=0, corner_radius=6,
            fg_color='#162032', hover_color='#1E2E4A', border_width=1, border_color='#0284C7', text_color='#38BDF8',
            command=lambda: self.rotate_quick(-90)
        ).grid(row=0, column=1, padx=2, sticky='ew')

        ctk.CTkButton(
            quick_rot_frame, text='⇄ ត្រឡប់', font=('Khmer OS Battambang', 11, 'bold'), height=30, width=0, corner_radius=6,
            fg_color='#162032', hover_color='#1E2E4A', border_width=1, border_color='#475569', text_color='#E2E8F0',
            command=self.flip_horizontal
        ).grid(row=0, column=2, padx=2, sticky='ew')

        ctk.CTkButton(
            quick_rot_frame, text='🔄 0°', font=('Khmer OS Battambang', 11, 'bold'), height=30, width=0, corner_radius=6,
            fg_color='#1E293B', hover_color='#334155', border_width=1, border_color='#475569', text_color='#E2E8F0',
            command=self.reset_rotate_degree
        ).grid(row=0, column=3, padx=(2, 0), sticky='ew')

        # Slider + Value Row
        rot_deg_header = ctk.CTkFrame(card_rotate, fg_color='transparent')
        rot_deg_header.pack(fill='x', padx=10, pady=(3, 1))
        ctk.CTkLabel(rot_deg_header, text='មុំដឺក្រេ (Angle):', font=self.font_text, text_color='#94A3B8').pack(side='left')
        self.lbl_rotate_deg_val = ctk.CTkLabel(
            rot_deg_header, text='0.0°', font=('Segoe UI', 11, 'bold'),
            text_color='#00F2FE', fg_color='#071626', corner_radius=6, padx=8, pady=1
        )
        self.lbl_rotate_deg_val.pack(side='right')

        self.sl_rotate_deg = ctk.CTkSlider(
            card_rotate, from_=-180, to=180, number_of_steps=360, height=14,
            progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#7DD3FC',
            command=self.on_rotate_slider_change
        )
        self.sl_rotate_deg.set(0)
        self.sl_rotate_deg.pack(fill='x', padx=10, pady=(2, 4))

        # Compact degree input
        input_deg_frame = ctk.CTkFrame(card_rotate, fg_color='transparent')
        input_deg_frame.pack(fill='x', padx=8, pady=(0, 6))

        ctk.CTkLabel(input_deg_frame, text='បញ្ចូលដឺក្រេ:', font=self.font_text, text_color='#CBD5E1').pack(side='left', padx=(2, 4))
        self.ent_rotate_deg = ctk.CTkEntry(
            input_deg_frame, width=54, height=28, corner_radius=6,
            fg_color='#0A0E17', border_color='#334155', text_color='#00F2FE',
            font=('Segoe UI', 11, 'bold'), justify='center'
        )
        self.ent_rotate_deg.insert(0, '0')
        self.ent_rotate_deg.pack(side='left', padx=(0, 2))
        self.ent_rotate_deg.bind('<Return>', lambda e: self.apply_manual_rotate_degree())

        ctk.CTkLabel(input_deg_frame, text='°', font=('Segoe UI', 12, 'bold'), text_color='#94A3B8').pack(side='left', padx=(0, 4))

        ctk.CTkButton(
            input_deg_frame, text='✅ កំណត់', width=64, height=28, corner_radius=6,
            font=self.font_btn, fg_color='#059669', hover_color='#047857',
            border_width=1, border_color='#34D399', command=self.apply_manual_rotate_degree
        ).pack(side='left', padx=(0, 2))

        # Card 3: AI Background
        card_bg = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_bg.pack(pady=4, padx=12, fill='x')

        head_bg = ctk.CTkFrame(card_bg, fg_color='transparent')
        head_bg.pack(fill='x', padx=10, pady=(6, 3))
        ctk.CTkLabel(head_bg, text='●', font=('Arial', 10), text_color='#00F2FE').pack(side='left', padx=(0, 5))
        self.label_bg = ctk.CTkLabel(head_bg, text='៣. ប្ដូរផ្ទៃខាងក្រោយ (AI Background)', font=self.font_bold, text_color='#F1F5F9')
        self.label_bg.pack(side='left')

        # Model Selector Dropdown
        self.model_map = {
            '⚡ BiRefNet Lite (កាត់លឿន & សក់ស្អាត ណែនាំ)': 'birefnet-general-lite',
            '👑 BiRefNet Portrait (Ultra Hair HD)': 'birefnet-portrait',
            '🔷 IS-Net (កាត់លឿនបំផុត Lightning)': 'isnet-general-use',
            '📦 U2Net (Legacy)': 'u2net'
        }
        self.model_display_names = list(self.model_map.keys())
        self.bg_model_var = ctk.StringVar(value=self.model_display_names[0])
        self.bg_model_opt = ctk.CTkOptionMenu(
            card_bg,
            values=self.model_display_names,
            variable=self.bg_model_var,
            command=self.on_bg_model_changed,
            font=('Khmer OS Siemreap', 10),
            dropdown_font=('Khmer OS Siemreap', 10),
            fg_color='#141E33',
            button_color='#1E293B',
            button_hover_color='#334155',
            dropdown_fg_color='#0F172A',
            text_color='#00F2FE',
            height=28
        )
        self.bg_model_opt.pack(fill='x', padx=8, pady=(2, 4))

        # 3 color pills in 1 row
        row_bg_btns = ctk.CTkFrame(card_bg, fg_color='transparent')
        row_bg_btns.pack(fill='x', padx=8, pady=(2, 6))
        row_bg_btns.grid_columnconfigure((0, 1, 2), weight=1, uniform='bg_btn')

        b_bg_b = ctk.CTkButton(
            row_bg_btns, text='🟦 ផ្ទៃខៀវ', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#0C2744', hover_color='#0369A1', border_width=1, border_color='#0284C7', text_color='#BAE6FD',
            command=lambda: self.change_background('blue')
        )
        b_bg_b.grid(row=0, column=0, padx=(0, 2), sticky='ew')
        reg_btn(b_bg_b, 'bg_blue')

        b_bg_w = ctk.CTkButton(
            row_bg_btns, text='⬜ ផ្ទៃស', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#1E293B', hover_color='#334155', border_width=1, border_color='#64748B', text_color='#FFFFFF',
            command=lambda: self.change_background('white')
        )
        b_bg_w.grid(row=0, column=1, padx=2, sticky='ew')
        reg_btn(b_bg_w, 'bg_white')

        b_bg_c = ctk.CTkButton(
            row_bg_btns, text='🎨 Custom', font=('Khmer OS Battambang', 11, 'bold'), height=34, width=0, corner_radius=8,
            fg_color='#141B29', hover_color='#1E293B', border_width=1, border_color='#475569', text_color='#E2E8F0',
            command=self.open_color_picker
        )
        b_bg_c.grid(row=0, column=2, padx=(2, 0), sticky='ew')
        reg_btn(b_bg_c, 'bg_custom')

        # Card 4: AI Retouch & Beauty
        self.card_pro = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        self.card_pro.pack(pady=4, padx=12, fill='x')

        head_pro = ctk.CTkFrame(self.card_pro, fg_color='transparent')
        head_pro.pack(fill='x', padx=10, pady=(6, 3))
        ctk.CTkLabel(head_pro, text='●', font=('Arial', 10), text_color='#FF2E93').pack(side='left', padx=(0, 5))
        self.label_pro = ctk.CTkLabel(head_pro, text='៤. កែសម្រស់ & គុណភាព (AI Retouch)', font=self.font_bold, text_color='#F1F5F9')
        self.label_pro.pack(side='left')

        grid_retouch = ctk.CTkFrame(self.card_pro, fg_color='transparent')
        grid_retouch.pack(fill='x', padx=8, pady=(2, 6))
        grid_retouch.grid_columnconfigure((0, 1), weight=1, uniform='retouch_col')

        # Row 1: Skin Retouch (1-Click Smooth & Retouch Studio)
        b_mk1 = ctk.CTkButton(
            grid_retouch, text='💄 1-Click មុខរលោង', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#340D24', hover_color='#500724', border_width=1, border_color='#DB2777', text_color='#FBCFE8',
            command=self.apply_natural_retouch_1click
        )
        b_mk1.grid(row=0, column=0, padx=(0, 3), pady=2, sticky='ew')
        reg_btn(b_mk1, 'makeup')

        b_rst = ctk.CTkButton(
            grid_retouch, text='🎛️ Retouch Studio', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#251233', hover_color='#3B1854', border_width=1, border_color='#A855F7', text_color='#E9D5FF',
            command=self.open_retouch_studio
        )
        b_rst.grid(row=0, column=1, padx=(3, 0), pady=2, sticky='ew')
        reg_btn(b_rst, 'retouch_studio')

        # Row 2: AI Restore & Enhance HD
        b_clr = ctk.CTkButton(
            grid_retouch, text='✨ AI Restore មុខ', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#331B08', hover_color='#451A03', border_width=1, border_color='#D97706', text_color='#FDE68A',
            command=self.apply_ai_face_restore
        )
        b_clr.grid(row=1, column=0, padx=(0, 3), pady=2, sticky='ew')
        reg_btn(b_clr, 'color')

        b_enh = ctk.CTkButton(
            grid_retouch, text='🔍 Enhance HD', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#062D24', hover_color='#064E3B', border_width=1, border_color='#059669', text_color='#A7F3D0',
            command=self.enhance_quality
        )
        b_enh.grid(row=1, column=1, padx=(3, 0), pady=2, sticky='ew')
        reg_btn(b_enh, 'enhance')

        # Row 3: Studio Lighting & LUTs
        b_lgt = ctk.CTkButton(
            grid_retouch, text='💡 Studio Light ▼', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#2D2008', hover_color='#432F09', border_width=1, border_color='#F59E0B', text_color='#FDE68A',
            command=self.toggle_light_panel
        )
        b_lgt.grid(row=2, column=0, padx=(0, 3), pady=2, sticky='ew')
        reg_btn(b_lgt, 'lighting')

        b_lut = ctk.CTkButton(
            grid_retouch, text='🎨 Studio LUTs', font=('Khmer OS Battambang', 11, 'bold'), height=36, width=0, corner_radius=8,
            fg_color='#2E180A', hover_color='#482109', border_width=1, border_color='#EA580C', text_color='#FED7AA',
            command=self.open_lut_studio
        )
        b_lut.grid(row=2, column=1, padx=(3, 0), pady=2, sticky='ew')
        reg_btn(b_lut, 'lut')

        # Card 5: Studio Lighting Controls (Expandable - hidden by default, pops under Card 4 when Studio Light is toggled)
        self.container_light = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#F59E0B')

        self.btn_toggle_light = ctk.CTkButton(
            self.container_light,
            text='💡  កំណត់ពន្លឺរូបភាព (Studio Light) ▲',
            font=self.font_bold,
            fg_color='#141C2B',
            hover_color='#1D283E',
            border_width=1,
            border_color='#F59E0B',
            text_color='#FBBF24',
            height=34,
            corner_radius=8,
            command=self.toggle_light_panel
        )
        self.btn_toggle_light.pack(fill='x', padx=8, pady=(8, 4))

        self.light_frame = ctk.CTkFrame(self.container_light, fg_color='transparent')
        self.sl_wb = self.create_slider('White Balance (កម្ដៅ):', (-100), 100)
        self.sl_bright = self.create_slider('Brightness (ពន្លឺ):', (-100), 100)
        self.sl_hl = self.create_slider('Highlights (ពន្លឺខ្លាំង):', (-100), 100)
        self.sl_shadow = self.create_slider('Shadows (ស្រមោល):', (-100), 100)
        self.sl_black = self.create_slider('Blacks (ពណ៌ខ្មៅ):', (-100), 100)
        self.btn_apply_light = ctk.CTkButton(
            self.light_frame,
            text='✅  អនុវត្តពន្លឺ (Apply Light)',
            font=self.font_btn,
            fg_color='#059669',
            hover_color='#047857',
            border_width=1,
            border_color='#34D399',
            height=34,
            corner_radius=8,
            command=self.apply_lighting
        )
        self.btn_apply_light.pack(pady=(4, 8), padx=10, fill='x')

        # Card 5 (formerly Card 6): Actions & Export
        card_actions = ctk.CTkFrame(self.frame_left, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_actions.pack(pady=4, padx=12, fill='x')

        head_act = ctk.CTkFrame(card_actions, fg_color='transparent')
        head_act.pack(fill='x', padx=10, pady=(6, 3))
        ctk.CTkLabel(head_act, text='●', font=('Arial', 10), text_color='#10B981').pack(side='left', padx=(0, 5))
        self.label_act = ctk.CTkLabel(head_act, text='៥. រក្សាទុក & គ្រប់គ្រង (Save & Export)', font=self.font_bold, text_color='#F1F5F9')
        self.label_act.pack(side='left')

        # Undo / Redo Row
        self.frame_undo = ctk.CTkFrame(card_actions, fg_color='transparent')
        self.frame_undo.pack(fill='x', padx=8, pady=(3, 3))
        self.btn_undo = ctk.CTkButton(
            self.frame_undo, text='↩️ Undo', font=self.font_btn,
            fg_color='#151C2C', hover_color='#1E293B',
            border_width=1, border_color='#334155',
            height=34, corner_radius=8, command=self.undo
        )
        self.btn_undo.pack(side='left', expand=True, fill='x', padx=(0, 3))
        self.btn_redo = ctk.CTkButton(
            self.frame_undo, text='Redo ↪️', font=self.font_btn,
            fg_color='#151C2C', hover_color='#1E293B',
            border_width=1, border_color='#334155',
            height=34, corner_radius=8, command=self.redo
        )
        self.btn_redo.pack(side='right', expand=True, fill='x', padx=(3, 0))

        # Big Prominent Button: Send / Open in Photoshop Auto
        self.btn_ps_open = ctk.CTkButton(
            card_actions, text='🎨  យករូបចូល Photoshop (Auto)',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            fg_color='#0284C7', hover_color='#0369A1',
            text_color='#FFFFFF', border_width=1.5, border_color='#38BDF8',
            height=44, corner_radius=10,
            command=self.send_to_photoshop if self.ps_mode else self.open_in_photoshop
        )
        self.btn_ps_open.pack(pady=(4, 4), padx=8, fill='x')

        row_save_clear = ctk.CTkFrame(card_actions, fg_color='transparent')
        row_save_clear.pack(fill='x', padx=8, pady=(0, 6))

        self.btn_save = ctk.CTkButton(
            row_save_clear, text='💾  ទាញយក (Save)',
            font=self.font_btn_bold, fg_color='#059669', hover_color='#047857',
            border_width=1.5, border_color='#34D399',
            height=36, corner_radius=8, command=self.save_image
        )
        self.btn_save.pack(side='left', expand=True, fill='x', padx=(0, 3))

        self.btn_clear = ctk.CTkButton(
            row_save_clear, text='🔄 Clear',
            font=self.font_btn, fg_color='#151C2C', hover_color='#25131E',
            border_width=1, border_color='#334155',
            height=36, corner_radius=8, command=self.clear_all
        )
        self.btn_clear.pack(side='right', expand=True, fill='x', padx=(3, 0))

        self.lbl_copyright = ctk.CTkLabel(
            self.frame_left,
            text='● RN Printing © 2026',
            font=ctk.CTkFont(family='Khmer OS Battambang', size=11),
            text_color='#00F5A0'
        )
        self.lbl_copyright.pack(side='bottom', pady=(10, 15))

        # Right Studio Tools Dock
        self.theme_switch = customtkinter.CTkSwitch(
            self.frame_tools, text='Light',
            font=ctk.CTkFont(family='Segoe UI', size=10),
            command=self.toggle_theme,
            progress_color='#00F2FE'
        )
        self.theme_switch.pack(pady=(12, 8), padx=10)

        # Card: Retouch Tools
        self.card_tools = ctk.CTkFrame(self.frame_tools, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_tools = self.card_tools
        card_tools.pack(fill='x', padx=8, pady=(0, 8))

        head_t = ctk.CTkFrame(card_tools, fg_color='transparent')
        head_t.pack(fill='x', padx=8, pady=(8, 4))
        ctk.CTkLabel(head_t, text='●', font=('Arial', 10), text_color='#00F2FE').pack(side='left', padx=(0, 4))
        ctk.CTkLabel(head_t, text='TOOLS', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#F1F5F9').pack(side='left')

        def get_white_icon(filename):
            img = Image.open(resource_path(filename)).convert('RGBA')
            white_img = Image.new('RGBA', img.size, (255, 255, 255, 255))
            if len(img.split()) == 4:
                white_img.putalpha(img.split()[3])
            return white_img

        img_spot_heal = ctk.CTkImage(light_image=get_white_icon('spot healing.png'), size=(20, 20))
        img_lips = ctk.CTkImage(light_image=get_white_icon('lips.png'), size=(20, 20))
        img_eraser = ctk.CTkImage(light_image=Image.open(resource_path('eraser.png')), size=(20, 20))
        img_liquify = ctk.CTkImage(light_image=Image.open(resource_path('liquify.png')), size=(20, 20))

        grid_tools = ctk.CTkFrame(card_tools, fg_color='transparent')
        grid_tools.pack(pady=4)

        r1 = ctk.CTkFrame(grid_tools, fg_color='transparent')
        r1.pack(pady=3)
        self.btn_spot_heal = ctk.CTkButton(
            r1, text='', image=img_spot_heal, width=52, height=50, corner_radius=10,
            fg_color='#141C2B', hover_color='#1E293B',
            border_width=1, border_color='#1E2A3E',
            command=self.toggle_healing
        )
        self.btn_spot_heal.pack(side='left', padx=3)

        self.btn_lips_brush = ctk.CTkButton(
            r1, text='', image=img_lips, width=52, height=50, corner_radius=10,
            fg_color='#141C2B', hover_color='#1E293B',
            border_width=1, border_color='#1E2A3E',
            command=self.toggle_lips_brush
        )
        self.btn_lips_brush.pack(side='left', padx=3)

        r2 = ctk.CTkFrame(grid_tools, fg_color='transparent')
        r2.pack(pady=(0, 4))
        self.btn_eraser = ctk.CTkButton(
            r2, text='', image=img_eraser, width=52, height=50, corner_radius=10,
            fg_color='#141C2B', hover_color='#1E293B',
            border_width=1, border_color='#1E2A3E',
            command=self.toggle_eraser
        )
        self.btn_eraser.pack(side='left', padx=3)

        self.btn_liquify = ctk.CTkButton(
            r2, text='', image=img_liquify, width=52, height=50, corner_radius=10,
            fg_color='#141C2B', hover_color='#1E293B',
            border_width=1, border_color='#1E2A3E',
            command=self.toggle_liquify
        )
        self.btn_liquify.pack(side='left', padx=3)

        # Card: Brush Controls
        card_brush = ctk.CTkFrame(self.frame_tools, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_brush.pack(fill='x', padx=8, pady=(0, 8))

        head_b = ctk.CTkFrame(card_brush, fg_color='transparent')
        head_b.pack(fill='x', padx=8, pady=(8, 4))
        ctk.CTkLabel(head_b, text='●', font=('Arial', 10), text_color='#00F2FE').pack(side='left', padx=(0, 4))
        ctk.CTkLabel(head_b, text='BRUSH', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#F1F5F9').pack(side='left')

        row_bs = ctk.CTkFrame(card_brush, fg_color='transparent')
        row_bs.pack(fill='x', padx=8, pady=(2, 0))
        ctk.CTkLabel(row_bs, text='Size:', font=ctk.CTkFont(family='Segoe UI', size=10), text_color='#94A3B8').pack(side='left')
        self.lbl_brush_val = ctk.CTkLabel(row_bs, text='30px', font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), text_color='#00F2FE')
        self.lbl_brush_val.pack(side='right')

        self.cached_brush_radius = 30.0
        self.cached_brush_hardness = 0.50

        def on_brush_val(v):
            self.cached_brush_radius = float(v)
            self.lbl_brush_val.configure(text=f'{int(v)}px')
            self.on_brush_size_change(v)

        self.sl_brush = ctk.CTkSlider(card_brush, from_=5, to=150, orientation='horizontal', height=14, command=on_brush_val, fg_color='#182234', progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#00F2FE')
        self.sl_brush.set(30)
        self.sl_brush.pack(fill='x', padx=8, pady=(2, 6))

        row_bh = ctk.CTkFrame(card_brush, fg_color='transparent')
        row_bh.pack(fill='x', padx=8, pady=(2, 0))
        ctk.CTkLabel(row_bh, text='Hardness:', font=ctk.CTkFont(family='Segoe UI', size=10), text_color='#94A3B8').pack(side='left')
        self.lbl_hard_val = ctk.CTkLabel(row_bh, text='50%', font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), text_color='#00F2FE')
        self.lbl_hard_val.pack(side='right')

        def on_hard_val(v):
            self.cached_brush_hardness = float(v) / 100.0
            self.lbl_hard_val.configure(text=f'{int(v)}%')

        self.sl_hard = ctk.CTkSlider(card_brush, from_=0, to=100, orientation='horizontal', height=14, command=on_hard_val, fg_color='#182234', progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#00F2FE')
        self.sl_hard.set(50)
        self.sl_hard.pack(fill='x', padx=8, pady=(2, 6))
        self.lbl_hard = self.lbl_hard_val

        self.lbl_heal_check = ctk.CTkLabel(card_brush, text='', font=ctk.CTkFont(weight='bold', size=11), text_color='#00FF9D')
        self.lbl_heal_check.pack(pady=(0, 4))

        # Card: Make-up
        card_makeup = ctk.CTkFrame(self.frame_tools, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_makeup.pack(fill='x', padx=8, pady=(0, 8))

        head_m = ctk.CTkFrame(card_makeup, fg_color='transparent')
        head_m.pack(fill='x', padx=8, pady=(8, 4))
        ctk.CTkLabel(head_m, text='●', font=('Arial', 10), text_color='#FF2E93').pack(side='left', padx=(0, 4))
        ctk.CTkLabel(head_m, text='MAKE-UP', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#F1F5F9').pack(side='left')

        frame_mu_grid = ctk.CTkFrame(card_makeup, fg_color='transparent')
        frame_mu_grid.pack(pady=4)

        frame_r1 = ctk.CTkFrame(frame_mu_grid, fg_color='transparent')
        frame_r1.pack(pady=2)
        f_tone = ctk.CTkFrame(frame_r1, fg_color='transparent')
        f_tone.pack(side='left', padx=4)
        ctk.CTkLabel(f_tone, text='Tone', font=ctk.CTkFont(size=10), text_color='#CBD5E1').pack()
        self.sl_tone = ctk.CTkSlider(f_tone, from_=(-50), to=50, orientation='vertical', height=60, width=14, command=self.live_preview_makeup, fg_color='#182234', progress_color='#FF2E93', button_color='#F472B6', button_hover_color='#FF2E93')
        self.sl_tone.set(0)
        self.sl_tone.pack()

        f_glow = ctk.CTkFrame(frame_r1, fg_color='transparent')
        f_glow.pack(side='left', padx=4)
        ctk.CTkLabel(f_glow, text='Glow', font=ctk.CTkFont(size=10), text_color='#CBD5E1').pack()
        self.sl_glow = ctk.CTkSlider(f_glow, from_=0, to=100, orientation='vertical', height=60, width=14, command=self.live_preview_makeup, fg_color='#182234', progress_color='#F59E0B', button_color='#FBBF24', button_hover_color='#F59E0B')
        self.sl_glow.set(0)
        self.sl_glow.pack()

        frame_r2 = ctk.CTkFrame(frame_mu_grid, fg_color='transparent')
        frame_r2.pack(pady=2)
        f_matte = ctk.CTkFrame(frame_r2, fg_color='transparent')
        f_matte.pack(side='left', padx=4)
        ctk.CTkLabel(f_matte, text='Matte', font=ctk.CTkFont(size=10), text_color='#CBD5E1').pack()
        self.sl_matte = ctk.CTkSlider(f_matte, from_=0, to=100, orientation='vertical', height=60, width=14, command=self.live_preview_makeup, fg_color='#182234', progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#00F2FE')
        self.sl_matte.set(0)
        self.sl_matte.pack()

        f_lips = ctk.CTkFrame(frame_r2, fg_color='transparent')
        f_lips.pack(side='left', padx=4)
        ctk.CTkLabel(f_lips, text='Lips', font=ctk.CTkFont(size=10), text_color='#CBD5E1').pack()
        self.sl_lips = ctk.CTkSlider(f_lips, from_=0, to=100, orientation='vertical', height=60, width=14, command=self.live_preview_makeup, fg_color='#182234', progress_color='#EC4899', button_color='#F472B6', button_hover_color='#EC4899')
        self.sl_lips.set(0)
        self.sl_lips.pack()

        self.btn_apply_makeup = ctk.CTkButton(
            card_makeup, text='✅ Apply',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            height=28, fg_color='#DB2777', hover_color='#BE185D',
            border_width=1, border_color='#F472B6', corner_radius=8,
            command=self.apply_makeup_live
        )
        self.btn_apply_makeup.pack(fill='x', padx=8, pady=(3, 5))
        self.lbl_makeup_check = ctk.CTkLabel(card_makeup, text='', font=ctk.CTkFont(weight='bold', size=11), text_color='#00FF9D')
        self.lbl_makeup_check.pack(pady=(0, 2))

        # Card: Wardrobe
        card_wardrobe = ctk.CTkFrame(self.frame_tools, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        card_wardrobe.pack(fill='x', padx=8, pady=(0, 15))

        head_w = ctk.CTkFrame(card_wardrobe, fg_color='transparent')
        head_w.pack(fill='x', padx=8, pady=(8, 4))
        ctk.CTkLabel(head_w, text='●', font=('Arial', 10), text_color='#818CF8').pack(side='left', padx=(0, 4))
        ctk.CTkLabel(head_w, text='WARDROBE', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#F1F5F9').pack(side='left')

        btn_wardrobe = ctk.CTkButton(
            card_wardrobe, text='👔  បំពាក់អាវ (Suits)',
            font=ctk.CTkFont(family='Khmer OS Battambang', size=12, weight='bold'),
            height=40, corner_radius=8,
            fg_color='#1E1B4B', hover_color='#312E81',
            border_width=1.5, border_color='#818CF8',
            command=self.open_wardrobe
        )
        btn_wardrobe.pack(fill='x', padx=8, pady=(4, 6))

        self.btn_remove_suit = ctk.CTkButton(
            card_wardrobe, text='❌ ដកអាវចេញ',
            font=ctk.CTkFont(family='Khmer OS Battambang', size=11),
            height=30, corner_radius=6,
            fg_color='#450A0A', hover_color='#7F1D1D',
            border_width=1, border_color='#EF4444',
            command=self.remove_suit_layer
        )

        # Center Workspace & Canvas
        self.canvas_container = ctk.CTkFrame(
            self.frame_center, corner_radius=12,
            fg_color='#080B12', border_width=1, border_color='#162032'
        )
        self.canvas_container.pack(expand=True, fill='both', padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_container, bg='#080B12', highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=2, pady=2)
        self.canvas.bind('<MouseWheel>', self.zoom)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Leave>', self.on_mouse_leave)
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_press)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<Configure>', lambda e: self.on_canvas_configure(e))

        self.render_empty_canvas()
        self.refresh_checkmarks()
        self.bind_all('<KeyPress>', self.on_global_key_press)
        for seq in ('<Control-z>', '<Control-Z>', '<Control-Key-z>', '<Control-Key-Z>'):
            self.bind_all(seq, lambda e: self.undo())
        for seq in ('<Control-y>', '<Control-Y>', '<Control-Key-y>', '<Control-Key-Y>', '<Control-r>', '<Control-R>', '<Control-Shift-Z>', '<Control-Shift-z>'):
            self.bind_all(seq, lambda e: self.redo())
        if self.ps_image_path:
            self.after(600, lambda: self.load_ps_image(self.ps_image_path))

        img_b_a = ctk.CTkImage(light_image=Image.open(resource_path('b&a.png')), size=(20, 20))
        self.btn_before_after = ctk.CTkButton(
            self.canvas_container, text='B / A', image=img_b_a, compound='left',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            width=85, height=36, corner_radius=18,
            fg_color='#0F172A', hover_color='#1E293B',
            border_width=1.5, border_color='#00F2FE', text_color='#00F2FE'
        )
        self.btn_before_after.place(relx=0.96, rely=0.95, anchor='se')
        self.btn_before_after.bind('<ButtonPress-1>', self.show_before_image)
        self.btn_before_after.bind('<ButtonRelease-1>', self.show_after_image)
        if not self.ps_mode:
            threading.Thread(target=lambda: self.install_photoshop_script(silent=True), daemon=True).start()
        threading.Thread(target=lambda: self.get_bg_session('birefnet-general-lite'), daemon=True).start()
    def force_foreground(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetAncestor(self.winfo_id(), 3)
            if hwnd:
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)
                else:
                    user32.ShowWindow(hwnd, 5)
                fore_hwnd = user32.GetForegroundWindow()
                if fore_hwnd and fore_hwnd != hwnd:
                    fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None)
                    cur_thread = kernel32.GetCurrentThreadId()
                    if fore_thread != cur_thread:
                        user32.AttachThreadInput(fore_thread, cur_thread, True)
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                        user32.AttachThreadInput(fore_thread, cur_thread, False)
                    else:
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                else:
                    user32.BringWindowToTop(hwnd)
                    user32.SetForegroundWindow(hwnd)
                if getattr(self, 'ps_mode', False):
                    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0043)
                else:
                    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0043)
                    user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0043)
        except Exception:
            pass
        try:
            if getattr(self, 'ps_mode', False):
                self.attributes('-topmost', True)
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            pass
    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            customtkinter.set_appearance_mode('Light')
        else:
            customtkinter.set_appearance_mode('Dark')
    def show_before_image(self, event=None):
        if not getattr(self, 'processed_image', None):
            return
        else:
            if not getattr(self, 'undo_stack', None):
                return
            else:
                current_w, current_h = self.processed_image.size
                current_ar = round(current_w / current_h, 2)
                base_img = None
                for state in self.undo_stack:
                    w, h = state['image'].size
                    if round(w / h, 2) == current_ar:
                        base_img = state['image']
                        break
                if not base_img:
                    base_img = self.undo_stack[0]['image']
                if base_img.size != (current_w, current_h):
                    from PIL import Image
                    base_img = base_img.resize((current_w, current_h), Image.Resampling.LANCZOS)
                self.temp_after_image = self.processed_image
                self.processed_image = base_img
                self.update_canvas_display()
    def show_after_image(self, event=None):
        if hasattr(self, 'temp_after_image') and self.temp_after_image:
                self.processed_image = self.temp_after_image
                self.update_canvas_display()
                self.temp_after_image = None
    def get_soft_brush(self, radius, hardness):
        radius = max(1, int(radius))
        cache_key = (radius, round(float(hardness), 2))
        if not hasattr(self, '_brush_mask_cache'):
            self._brush_mask_cache = {}
        if cache_key in self._brush_mask_cache:
            return self._brush_mask_cache[cache_key]

        y, x = np.ogrid[-radius:radius, -radius:radius]
        dist = np.sqrt(x ** 2 + y ** 2)
        solid_radius = radius * hardness
        fade_dist = radius - solid_radius
        if fade_dist <= 0:
            mask = np.where(dist <= radius, 1.0, 0.0)
        else:
            mask = np.where(dist <= solid_radius, 1.0, np.where(dist <= radius, 1.0 - (dist - solid_radius) / fade_dist, 0.0))
        result = mask.astype(np.float32)
        if len(self._brush_mask_cache) > 64:
            self._brush_mask_cache.clear()
        self._brush_mask_cache[cache_key] = result
        return result
    def load_ps_image(self, path):
        try:
            self.canvas.update_idletasks()
            if self.canvas.winfo_width() <= 1:
                self.after(500, lambda: self.load_ps_image(path))
            else:
                self.original_image_path = path
                img = Image.open(path)
                try:
                    from PIL import ImageOps
                    img = ImageOps.exif_transpose(img)
                except Exception:
                    pass
                self.processed_image = img
                self.invalidate_bg_cache()
                self.suit_overlay_image = None
                self._rotate_base_image = None
                self._rotate_base_suit = None
                if hasattr(self, 'sl_rotate_deg'):
                    self.sl_rotate_deg.set(0)
                if hasattr(self, 'lbl_rotate_deg_val'):
                    self.lbl_rotate_deg_val.configure(text='0.0°')
                if hasattr(self, 'ent_rotate_deg'):
                    self.ent_rotate_deg.delete(0, 'end')
                    self.ent_rotate_deg.insert(0, '0')
                if hasattr(self, 'undo_stack'):
                    self.undo_stack.clear()
                if hasattr(self, 'redo_stack'):
                    self.redo_stack.clear()
                if hasattr(self, 'action_counts'):
                    for key in self.action_counts:
                        self.action_counts[key] = 0
                if hasattr(self, 'refresh_checkmarks'):
                    self.refresh_checkmarks()
                self.lips_mask_layer = None
                self.fit_image()
                if getattr(self, 'ps_mode', False):
                    self.attributes('-topmost', True)
                self.force_foreground()
        except Exception as e:
            messagebox.showerror('Error', f'មិនអាចទាញរូបពី Photoshop បានទេ: {str(e)}')
    def send_to_photoshop(self):
        if not self.ensure_license_active("បញ្ជូនរូបទៅ Photoshop"):
            return
        if self.processed_image:
            try:
                import os
                import tempfile
                import subprocess
                try:
                    self.attributes('-topmost', False)
                    import ctypes
                    hwnd = ctypes.windll.user32.GetAncestor(self.winfo_id(), 3)
                    if hwnd:
                        ctypes.windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0043)
                except Exception:
                    pass
                temp_dir = tempfile.gettempdir()
                out_path = os.path.join(temp_dir, 'mt_result_image.png')
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image:
                    save_img = Image.alpha_composite(self.processed_image.convert('RGBA'), self.suit_overlay_image).convert('RGB')
                else:
                    save_img = self.processed_image.convert('RGB')
                save_img.save(out_path, format='PNG')
                vbs_path = os.path.join(temp_dir, 'send_to_ps.vbs')
                with open(vbs_path, 'w', encoding='utf-8') as f:
                    f.write('On Error Resume Next\n')
                    f.write('Set psApp = GetObject(, "Photoshop.Application")\n')
                    f.write('If Err.Number <> 0 Or psApp Is Nothing Then\n')
                    f.write('    Err.Clear\n')
                    f.write('    Set psApp = CreateObject("Photoshop.Application")\n')
                    f.write('End If\n')
                    f.write(f'psApp.Open "{out_path}"\n')
                    f.write('psApp.BringToFront\n')
                subprocess.Popen(['wscript', vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
                self.destroy()
            except Exception as e:
                messagebox.showerror('បញ្ហា', f'មិនអាចបញ្ជូនរូបទៅកាន់ Photoshop បានទេ៖ {str(e)}')

    def find_photoshop_exe(self):
        cached = getattr(self, '_cached_photoshop_exe', None)
        if cached and os.path.isfile(cached):
            return cached

        import string
        from ctypes import windll
        import winreg

        cands = [
            r'F:\Adobe\Adobe Setup\Adobe Photoshop 2026\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2021\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop CC 2019\Photoshop.exe',
            r'C:\Program Files (x86)\Adobe\Adobe Photoshop CS6\Photoshop.exe',
        ]
        for c in cands:
            if os.path.isfile(c):
                self._cached_photoshop_exe = c
                return c

        for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                try:
                    k = winreg.OpenKey(root, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe', 0, winreg.KEY_READ | flag)
                    def_val, _ = winreg.QueryValueEx(k, '')
                    winreg.CloseKey(k)
                    if def_val and os.path.isfile(def_val):
                        self._cached_photoshop_exe = def_val
                        return def_val
                except Exception:
                    pass

        try:
            locs = self.find_all_photoshop_locations()
            for p in locs:
                exe = os.path.join(p, 'Photoshop.exe')
                if os.path.isfile(exe):
                    self._cached_photoshop_exe = exe
                    return exe
        except Exception:
            pass

        try:
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter + ':\\')
                bitmask >>= 1
            for d in drives:
                adobe_dirs = [
                    os.path.join(d, 'Adobe'),
                    os.path.join(d, 'Adobe', 'Adobe Setup'),
                    os.path.join(d, 'Program Files', 'Adobe'),
                    os.path.join(d, 'Program Files (x86)', 'Adobe'),
                ]
                for ad in adobe_dirs:
                    if os.path.isdir(ad):
                        try:
                            for entry in os.listdir(ad):
                                if 'photoshop' in entry.lower():
                                    cand_exe = os.path.join(ad, entry, 'Photoshop.exe')
                                    if os.path.isfile(cand_exe):
                                        self._cached_photoshop_exe = cand_exe
                                        return cand_exe
                        except Exception:
                            pass
        except Exception:
            pass

        return None

    def open_in_photoshop(self):
        if not self.processed_image:
            messagebox.showwarning('ដំណឹង', 'សូមបើក ឬកាត់តរូបភាពមួយសិន មុននឹងបើកក្នុង Photoshop!')
            return

        try:
            import os
            import tempfile
            import subprocess
            from PIL import Image

            if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image:
                export_img = Image.alpha_composite(self.processed_image.convert('RGBA'), self.suit_overlay_image)
            else:
                export_img = self.processed_image.copy()

            temp_dir = tempfile.gettempdir()
            base_name = "RN_Photography_Edited"
            if self.original_image_path:
                try:
                    raw_name = os.path.splitext(os.path.basename(self.original_image_path))[0]
                    base_name = f"{raw_name}_edited"
                except Exception:
                    pass

            out_path = os.path.join(temp_dir, f"{base_name}.png")
            export_img.save(out_path, format='PNG', dpi=getattr(self, 'output_dpi', (300, 300)))

            opened = False

            # Try COM Automation first
            try:
                vbs_path = os.path.join(temp_dir, 'open_ps_doc.vbs')
                with open(vbs_path, 'w', encoding='utf-8') as f:
                    f.write('On Error Resume Next\n')
                    f.write('Set psApp = GetObject(, "Photoshop.Application")\n')
                    f.write('If Err.Number <> 0 Or psApp Is Nothing Then\n')
                    f.write('    Err.Clear\n')
                    f.write('    Set psApp = CreateObject("Photoshop.Application")\n')
                    f.write('End If\n')
                    f.write(f'psApp.Open "{out_path}"\n')
                    f.write('psApp.BringToFront\n')
                res = subprocess.run(['wscript', vbs_path], creationflags=subprocess.CREATE_NO_WINDOW, timeout=3)
                if res.returncode == 0:
                    opened = True
            except Exception:
                opened = False

            # If COM Automation failed, launch Photoshop.exe directly
            if not opened:
                ps_exe = self.find_photoshop_exe()
                if not ps_exe:
                    choose = messagebox.askyesno(
                        'រកមិនឃើញ Photoshop',
                        'មិនបានរកឃើញកម្មវិធី Adobe Photoshop ដោយស្វ័យប្រវត្តិទេ!\n\nតើអ្នកចង់ជ្រើសរើសឯកសារ Photoshop.exe ដោយផ្ទាល់ដែរឬទេ?'
                    )
                    if choose:
                        sel = filedialog.askopenfilename(
                            title='ជ្រើសរើសឯកសារ Photoshop.exe',
                            filetypes=[('Photoshop Executable', 'Photoshop.exe'), ('All files', '*.*')]
                        )
                        if sel and os.path.isfile(sel):
                            ps_exe = os.path.normpath(sel)
                            self._cached_photoshop_exe = ps_exe

                if ps_exe and os.path.isfile(ps_exe):
                    subprocess.Popen([ps_exe, out_path])
                    opened = True
                else:
                    os.startfile(out_path)
                    opened = True

            messagebox.showinfo('ជោគជ័យ', '✅ បានបញ្ជូនរូបភាពទៅបើកក្នុង Adobe Photoshop រួចរាល់!')
        except Exception as e:
            messagebox.showerror('បញ្ហា', f'មិនអាចបើកក្នុង Photoshop បានទេ៖ {str(e)}')

    def find_all_photoshop_locations(self):
        import winreg
        import string
        from ctypes import windll

        ps_dirs = set()

        # 1. Registry: App Paths (Direct registration in Windows)
        for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                try:
                    k = winreg.OpenKey(root, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe', 0, winreg.KEY_READ | flag)
                    try:
                        p, _ = winreg.QueryValueEx(k, 'Path')
                        if p and os.path.isdir(p):
                            ps_dirs.add(os.path.normpath(p))
                    except Exception:
                        pass
                    try:
                        def_val, _ = winreg.QueryValueEx(k, '')
                        if def_val and os.path.isfile(def_val):
                            ps_dirs.add(os.path.normpath(os.path.dirname(def_val)))
                    except Exception:
                        pass
                    winreg.CloseKey(k)
                except Exception:
                    pass

        # 2. Registry: Adobe Photoshop Keys
        for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for rk in [r'SOFTWARE\Adobe\Photoshop', r'SOFTWARE\WOW6432Node\Adobe\Photoshop']:
                for flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                    try:
                        k = winreg.OpenKey(root, rk, 0, winreg.KEY_READ | flag)
                        for i in range(winreg.QueryInfoKey(k)[0]):
                            sub = winreg.EnumKey(k, i)
                            try:
                                sk = winreg.OpenKey(k, sub, 0, winreg.KEY_READ | flag)
                                try:
                                    val, _ = winreg.QueryValueEx(sk, 'ApplicationPath')
                                    if val and os.path.isdir(val):
                                        ps_dirs.add(os.path.normpath(val))
                                except Exception:
                                    pass
                                try:
                                    app_sk = winreg.OpenKey(sk, 'ApplicationPath', 0, winreg.KEY_READ | flag)
                                    val2, _ = winreg.QueryValueEx(app_sk, '')
                                    if val2 and os.path.isdir(val2):
                                        ps_dirs.add(os.path.normpath(val2))
                                    winreg.CloseKey(app_sk)
                                except Exception:
                                    pass
                                winreg.CloseKey(sk)
                            except Exception:
                                pass
                        winreg.CloseKey(k)
                    except Exception:
                        pass

        # 3. Scan all fixed and ready drives
        try:
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter + ':\\')
                bitmask >>= 1

            for d in drives:
                candidates = [
                    os.path.join(d, 'Adobe', 'Adobe Setup'),
                    os.path.join(d, 'Adobe'),
                    os.path.join(d, 'Program Files', 'Adobe'),
                    os.path.join(d, 'Program Files (x86)', 'Adobe')
                ]
                for cand in candidates:
                    if os.path.isdir(cand):
                        try:
                            for entry in os.listdir(cand):
                                full = os.path.join(cand, entry)
                                if os.path.isdir(full) and 'photoshop' in entry.lower():
                                    if os.path.isfile(os.path.join(full, 'Photoshop.exe')) or os.path.isdir(os.path.join(full, 'Presets')):
                                        ps_dirs.add(os.path.normpath(full))
                        except Exception:
                            pass
        except Exception:
            pass

        return ps_dirs

    def install_photoshop_script(self, silent=True):
        try:
            import shutil
            from ctypes import windll

            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))

            src_jsx = os.path.join(app_dir, 'RN_PhotoMaker_v3.jsx')
            if not os.path.exists(src_jsx):
                src_jsx = os.path.join(app_dir, 'MT_PhotoMaker_v3.jsx')
            if not os.path.exists(src_jsx):
                # Search parent or current dir
                cands = [
                    os.path.join(os.getcwd(), 'RN_PhotoMaker_v3.jsx'),
                    os.path.join(os.getcwd(), 'MT_PhotoMaker_v3.jsx'),
                    os.path.join(os.path.dirname(app_dir), 'RN_PhotoMaker_v3.jsx'),
                    os.path.join(os.path.dirname(app_dir), 'MT_PhotoMaker_v3.jsx')
                ]
                for c in cands:
                    if os.path.exists(c):
                        src_jsx = c
                        break

            if not os.path.exists(src_jsx):
                if not silent:
                    messagebox.showerror('បញ្ហា', 'មិនអាចស្វែងរកឯកសារ Script (RN_PhotoMaker_v3.jsx) ឃើញទេ!')
                return 0

            with open(src_jsx, 'r', encoding='utf-8') as f:
                jsx_text = f.read()

            target_exe = os.path.join(app_dir, 'PhotoMaker.exe').replace('\\', '/')
            if f'"{target_exe}"' not in jsx_text:
                marker = "var candidates = ["
                idx = jsx_text.find(marker)
                if idx >= 0:
                    jsx_text = jsx_text[:idx + len(marker)] + f'\n        "{target_exe}",' + jsx_text[idx + len(marker):]

            ps_dirs = self.find_all_photoshop_locations()

            if not ps_dirs and not silent:
                # Ask user to pick the Photoshop directory
                choose = messagebox.askyesno(
                    'តភ្ជាប់ជាមួយ Photoshop',
                    'មិនទាន់រកឃើញ Folder Adobe Photoshop ដោយស្វ័យប្រវត្តិទេ!\n\nតើអ្នកចង់ជ្រើសរើស Folder Adobe Photoshop ដោយផ្ទាល់ដែរឬទេ?'
                )
                if choose:
                    sel = filedialog.askdirectory(title='ជ្រើសរើស Folder Adobe Photoshop (ឧទាហរណ៍ Adobe Photoshop 2026)')
                    if sel and os.path.isdir(sel):
                        ps_dirs.add(os.path.normpath(sel))

            if not ps_dirs:
                if not silent:
                    messagebox.showwarning(
                        'ដំណឹង',
                        'មិនបានរកឃើញ Folder Adobe Photoshop លើកុំព្យូទ័រនេះទេ!\nអ្នកអាច Copy ឯកសារ RN_PhotoMaker_v3.jsx ទៅកាន់ Presets\\Scripts ក្នុង Photoshop ដោយដៃ។'
                    )
                return 0

            installed_count = 0
            installed_list = []
            for p in ps_dirs:
                scripts_dir = os.path.join(p, "Presets", "Scripts")
                try:
                    os.makedirs(scripts_dir, exist_ok=True)
                    # Always purge old MT_PhotoMaker_v3.jsx so Photoshop has only ONE clean script
                    dst_jsx_mt = os.path.join(scripts_dir, "MT_PhotoMaker_v3.jsx")
                    if os.path.exists(dst_jsx_mt):
                        try:
                            os.remove(dst_jsx_mt)
                        except Exception:
                            pass

                    dst_jsx_rn = os.path.join(scripts_dir, "RN_PhotoMaker_v3.jsx")
                    with open(dst_jsx_rn, 'w', encoding='utf-8') as f:
                        f.write(jsx_text)
                    installed_count += 1
                    installed_list.append(p)
                except PermissionError:
                    # Elevated copy fallback for protected Program Files
                    try:
                        import tempfile
                        tmp_f = os.path.join(tempfile.gettempdir(), 'RN_PhotoMaker_v3.jsx')
                        with open(tmp_f, 'w', encoding='utf-8') as tf:
                            tf.write(jsx_text)
                        cmd = f'/c del /f /q "{dst_jsx_mt}" & copy /y "{tmp_f}" "{dst_jsx_rn}"'
                        windll.shell32.ShellExecuteW(None, 'runas', 'cmd.exe', cmd, None, 0)
                        installed_count += 1
                        installed_list.append(p)
                    except Exception:
                        pass
                except Exception:
                    pass

            if not silent:
                if installed_count > 0:
                    names = "\n".join([f"• {p}" for p in installed_list])
                    messagebox.showinfo(
                        'ជោគជ័យ',
                        f'✅ បានតភ្ជាប់ជាមួយ Photoshop ({installed_count} កំណែ) ដោយជោគជ័យ!\n\n{names}\n\n👉 សូមបើក Photoshop រួចចូលទៅកាន់:\nFile > Scripts > RN_PhotoMaker_v3'
                    )
                else:
                    messagebox.showwarning(
                        'ដំណឹង',
                        'មិនអាចសរសេរ Script ចូល Photoshop បានទេ។ សូមដំណើរការកម្មវិធីជា Run as Administrator ឬ Copy ឯកសារដោយដៃ។'
                    )
            return installed_count
        except Exception as e:
            if not silent:
                messagebox.showerror('បញ្ហា', f'មានកំហុសក្នុងការតភ្ជាប់ Script: {str(e)}')
            return 0
    def save_state(self):
        if self.processed_image:
            self.undo_stack.append({
                'image': self.processed_image.copy(),
                'counts': self.action_counts.copy(),
                'suit': self.suit_overlay_image.copy() if getattr(self, 'suit_overlay_image', None) is not None else None
            })
            if len(self.undo_stack) > 15:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
    def clear_all(self):
        self.original_image_path = None
        self.processed_image = None
        self.tk_image = None
        self.invalidate_bg_cache()
        self._cached_face_box = None
        self._rotate_base_image = None
        self._rotate_base_suit = None
        self._rotate_preview_base = None
        self._rotate_preview_suit = None
        self._rotate_temp_disp = None
        self._rotate_temp_suit = None
        if hasattr(self, '_rotate_debounce_id') and self._rotate_debounce_id:
            try:
                self.after_cancel(self._rotate_debounce_id)
            except Exception:
                pass
            self._rotate_debounce_id = None
        self.undo_stack.clear()
        self.redo_stack.clear()
        for key in self.action_counts:
            self.action_counts[key] = 0
        self.refresh_checkmarks()
        if getattr(self, 'healing_active', False):
            self.toggle_healing()
        if getattr(self, 'lips_brush_active', False):
            self.toggle_lips_brush()
        if getattr(self, 'eraser_active', False):
            self.toggle_eraser()
        if getattr(self, 'liquify_active', False):
            self.toggle_liquify()
        if self.light_panel_open:
            self.toggle_light_panel()
        self.reset_sliders()
        self.sl_tone.set(0)
        self.sl_glow.set(0)
        self.sl_matte.set(0)
        self.sl_lips.set(0)
        self.lips_mask_layer = None
        self._rotate_base_image = None
        self._rotate_base_suit = None
        if hasattr(self, 'sl_rotate_deg'):
            self.sl_rotate_deg.set(0)
        if hasattr(self, 'lbl_rotate_deg_val'):
            self.lbl_rotate_deg_val.configure(text='0.0°')
        if hasattr(self, 'ent_rotate_deg'):
            self.ent_rotate_deg.delete(0, 'end')
            self.ent_rotate_deg.insert(0, '0')
        if hasattr(self, 'preview_makeup_img'):
            delattr(self, 'preview_makeup_img')
        if hasattr(self, 'base_makeup_img'):
            delattr(self, 'base_makeup_img')
        if hasattr(self, 'preview_lighting_img'):
            delattr(self, 'preview_lighting_img')
        if hasattr(self, 'base_lighting_img'):
            delattr(self, 'base_lighting_img')
        self.canvas.delete('all')
        self.render_empty_canvas()
        if hasattr(self, 'btn_remove_suit'):
            self.btn_remove_suit.pack_forget()
        self.suit_overlay_image = None
        self.image_before_suit = None
    def on_global_key_press(self, event):
        widget = getattr(event, 'widget', None)
        if widget is not None:
            try:
                w_class = widget.winfo_class()
                if w_class in ('Entry', 'Text', 'TEntry') or isinstance(widget, (tk.Entry, tk.Text)):
                    return
            except Exception:
                pass

        # Check Control modifier: bit 0x0004 or 0x20000 (extended)
        is_ctrl = bool(event.state & 4) or bool(event.state & 0x20000)
        is_shift = bool(event.state & 1)

        kc = getattr(event, 'keycode', 0)
        ks = (getattr(event, 'keysym', '') or '').lower()

        if is_ctrl:
            # VK_Z = 90
            if kc == 90 or ks == 'z':
                if is_shift:
                    self.redo()
                else:
                    self.undo()
                return 'break'
            # VK_Y = 89, VK_R = 82
            elif kc in (89, 82) or ks in ('y', 'r'):
                self.redo()
                return 'break'

    def undo(self):
        if self.undo_stack:
            if self.processed_image:
                self.redo_stack.append({
                    'image': self.processed_image.copy(),
                    'counts': self.action_counts.copy(),
                    'suit': self.suit_overlay_image.copy() if getattr(self, 'suit_overlay_image', None) is not None else None
                })
            state = self.undo_stack.pop()
            self.processed_image = state['image']
            self.action_counts = state['counts'].copy()
            if 'suit' in state:
                self.suit_overlay_image = state['suit']
                if self.suit_overlay_image:
                    if hasattr(self, 'btn_remove_suit'):
                        self.btn_remove_suit.pack(fill='x', padx=8, pady=(0, 6))
                else:
                    if hasattr(self, 'btn_remove_suit'):
                        self.btn_remove_suit.pack_forget()
            if self.light_panel_open:
                self.toggle_light_panel()
            self.refresh_checkmarks()
            self._composite_cache_key = None
            self._composite_cache_img = None
            self.invalidate_bg_cache()
            self.update_canvas_display()

    def redo(self):
        if self.redo_stack:
            if self.processed_image:
                self.undo_stack.append({
                    'image': self.processed_image.copy(),
                    'counts': self.action_counts.copy(),
                    'suit': self.suit_overlay_image.copy() if getattr(self, 'suit_overlay_image', None) is not None else None
                })
            state = self.redo_stack.pop()
            self.processed_image = state['image']
            self.action_counts = state['counts'].copy()
            if 'suit' in state:
                self.suit_overlay_image = state['suit']
                if self.suit_overlay_image:
                    if hasattr(self, 'btn_remove_suit'):
                        self.btn_remove_suit.pack(fill='x', padx=8, pady=(0, 6))
                else:
                    if hasattr(self, 'btn_remove_suit'):
                        self.btn_remove_suit.pack_forget()
            if self.light_panel_open:
                self.toggle_light_panel()
            self.refresh_checkmarks()
            self._composite_cache_key = None
            self._composite_cache_img = None
            self.invalidate_bg_cache()
            self.update_canvas_display()
    def create_slider(self, text, min_val, max_val):
        header = ctk.CTkFrame(self.light_frame, fg_color='transparent')
        header.pack(fill='x', padx=14, pady=(6, 2))
        lbl = ctk.CTkLabel(header, text=text, font=self.font_text, text_color='#CBD5E1')
        lbl.pack(side='left')
        val_lbl = ctk.CTkLabel(header, text='0', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#F59E0B')
        val_lbl.pack(side='right')

        def on_change(v):
            val = int(v)
            val_lbl.configure(text=f'{val:+d}' if val != 0 else '0')
            self.live_preview_lighting(v)

        sl = ctk.CTkSlider(
            self.light_frame, from_=min_val, to=max_val, number_of_steps=100,
            command=on_change,
            fg_color='#182234', progress_color='#F59E0B',
            button_color='#FBBF24', button_hover_color='#F59E0B',
            height=14
        )
        sl.set(0)
        sl.pack(fill='x', padx=14, pady=(0, 6))
        sl._val_lbl = val_lbl
        return sl

    def create_action_row(self, text, command, key, fg_color=None, hover_color=None, parent=None, border_color=None, border_width=1, text_color=None):
        target_parent = parent if parent is not None else self.frame_left
        row = ctk.CTkFrame(target_parent, fg_color='transparent')
        row.pack(pady=3, padx=10, fill='x')
        kwargs = {
            'text': text,
            'font': self.font_btn,
            'command': command,
            'height': 36,
            'corner_radius': 8,
            'anchor': 'w'
        }
        if fg_color:
            kwargs['fg_color'] = fg_color
        if hover_color:
            kwargs['hover_color'] = hover_color
        if border_color:
            kwargs['border_color'] = border_color
            kwargs['border_width'] = border_width
        if text_color:
            kwargs['text_color'] = text_color
        btn = ctk.CTkButton(row, **kwargs)
        btn.pack(side='left', expand=True, fill='x')
        lbl = ctk.CTkLabel(row, text='', width=38, font=ctk.CTkFont(family='Segoe UI', weight='bold', size=11), text_color='#00FF9D', corner_radius=6)
        lbl.pack(side='right', padx=(4, 0))
        self.check_labels[key] = lbl
        return btn

    def refresh_checkmarks(self):
        for key, count in self.action_counts.items():
            if key == 'spot_heal':
                if hasattr(self, 'lbl_heal_check'):
                    if count > 0:
                        self.lbl_heal_check.configure(text=f'✔({count})', text_color='#00FF9D')
                    else:
                        self.lbl_heal_check.configure(text='')
                continue
            elif key == 'live_makeup':
                if hasattr(self, 'lbl_makeup_check'):
                    if count > 0:
                        self.lbl_makeup_check.configure(text=f'✔({count})', text_color='#00FF9D')
                    else:
                        self.lbl_makeup_check.configure(text='')
                continue
            else:
                if key not in self.check_labels:
                    continue
                widget = self.check_labels[key]
                if isinstance(widget, ctk.CTkButton):
                    orig_text = getattr(widget, '_base_text', None)
                    if orig_text is None:
                        orig_text = widget.cget('text')
                        widget._base_text = orig_text
                    if count == 0:
                        widget.configure(text=orig_text)
                    else:
                        widget.configure(text=f"{orig_text} ✔")
                else:
                    if count == 0:
                        widget.configure(text='', fg_color='transparent')
                    else:
                        if count <= 3:
                            widget.configure(text='✔' * count, fg_color='#04291B', text_color='#00FF9D')
                        else:
                            widget.configure(text=f'✔({count})', fg_color='#04291B', text_color='#00FF9D')

    def increment_action(self, key):
        self.action_counts[key] += 1
        self.refresh_checkmarks()

    def reset_sliders(self):
        for sl in (self.sl_wb, self.sl_bright, self.sl_hl, self.sl_shadow, self.sl_black):
            sl.set(0)
            if hasattr(sl, '_val_lbl'):
                sl._val_lbl.configure(text='0')
    def upload_image(self):
        if not self.ensure_license_active("បញ្ចូលរូបថត (Upload Photo)"):
            return
        file_path = filedialog.askopenfilename(filetypes=[('Image files', '*.jpg *.jpeg *.png')])
        if file_path:
            self.original_image_path = file_path
            img = Image.open(file_path)
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            self.processed_image = img
            self.invalidate_bg_cache()
            self.suit_overlay_image = None
            if hasattr(self, 'btn_remove_suit'):
                self.btn_remove_suit.pack_forget()
            self._rotate_base_image = None
            self._rotate_base_suit = None
            if hasattr(self, 'sl_rotate_deg'):
                self.sl_rotate_deg.set(0)
            if hasattr(self, 'lbl_rotate_deg_val'):
                self.lbl_rotate_deg_val.configure(text='0.0°')
            if hasattr(self, 'ent_rotate_deg'):
                self.ent_rotate_deg.delete(0, 'end')
                self.ent_rotate_deg.insert(0, '0')
            self.undo_stack.clear()
            self.redo_stack.clear()
            for key in self.action_counts:
                self.action_counts[key] = 0
            self.refresh_checkmarks()
            if self.light_panel_open:
                self.toggle_light_panel()
            self.lips_mask_layer = None
            self.fit_image()

    def rotate_quick(self, angle_deg):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        self.save_state()
        self.invalidate_bg_cache()
        self._rotate_base_image = None
        self._rotate_base_suit = None
        if angle_deg == 90:
            self.processed_image = self.processed_image.transpose(Image.Transpose.ROTATE_90)
            if getattr(self, 'suit_overlay_image', None) is not None:
                self.suit_overlay_image = self.suit_overlay_image.transpose(Image.Transpose.ROTATE_90)
        elif angle_deg == -90:
            self.processed_image = self.processed_image.transpose(Image.Transpose.ROTATE_270)
            if getattr(self, 'suit_overlay_image', None) is not None:
                self.suit_overlay_image = self.suit_overlay_image.transpose(Image.Transpose.ROTATE_270)
        else:
            self.processed_image = self.processed_image.rotate(angle_deg, expand=True, resample=Image.Resampling.BICUBIC)
            if getattr(self, 'suit_overlay_image', None) is not None:
                self.suit_overlay_image = self.suit_overlay_image.rotate(angle_deg, expand=True, resample=Image.Resampling.BICUBIC)
        if hasattr(self, 'sl_rotate_deg'):
            self.sl_rotate_deg.set(0)
        if hasattr(self, 'lbl_rotate_deg_val'):
            self.lbl_rotate_deg_val.configure(text='0.0°')
        if hasattr(self, 'ent_rotate_deg'):
            self.ent_rotate_deg.delete(0, 'end')
            self.ent_rotate_deg.insert(0, '0')
        self.fit_image()

    def flip_horizontal(self):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        self.save_state()
        self.invalidate_bg_cache()
        self._rotate_base_image = None
        self._rotate_base_suit = None
        self.processed_image = self.processed_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if getattr(self, 'suit_overlay_image', None) is not None:
            self.suit_overlay_image = self.suit_overlay_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.fit_image()

    def on_rotate_slider_change(self, val):
        if not getattr(self, 'processed_image', None):
            return
        deg = round(float(val), 1)
        if hasattr(self, 'lbl_rotate_deg_val'):
            sign = '+' if deg > 0 else ''
            self.lbl_rotate_deg_val.configure(text=f'{sign}{deg}°')
        if hasattr(self, 'ent_rotate_deg'):
            self.ent_rotate_deg.delete(0, 'end')
            self.ent_rotate_deg.insert(0, str(deg))
        if getattr(self, '_rotate_base_image', None) is None:
            self._rotate_base_image = self.processed_image.copy()
            self._rotate_base_suit = self.suit_overlay_image.copy() if getattr(self, 'suit_overlay_image', None) is not None else None
            # Prepare fast downscaled preview base for 60fps live rotation during drag
            max_dim = max(self._rotate_base_image.size)
            if max_dim > 1000:
                scale = 1000.0 / max_dim
                pw, ph = max(10, int(self._rotate_base_image.width * scale)), max(10, int(self._rotate_base_image.height * scale))
                self._rotate_preview_base = self._rotate_base_image.resize((pw, ph), Image.Resampling.BILINEAR)
                self._rotate_preview_suit = self._rotate_base_suit.resize((pw, ph), Image.Resampling.BILINEAR) if self._rotate_base_suit is not None else None
            else:
                self._rotate_preview_base = self._rotate_base_image.copy()
                self._rotate_preview_suit = self._rotate_base_suit.copy() if self._rotate_base_suit is not None else None

        self._pending_rotate_deg = deg
        fill = (255, 255, 255) if self._rotate_base_image.mode == 'RGB' else (0, 0, 0, 0)

        # Super fast live preview on downscaled proxy without hitching UI thread
        if getattr(self, '_rotate_preview_base', None) is not None:
            rot_prev = self._rotate_preview_base.rotate(-deg, resample=Image.Resampling.BILINEAR, expand=True, fillcolor=fill)
            self._rotate_temp_disp = rot_prev
            if getattr(self, '_rotate_preview_suit', None) is not None:
                self._rotate_temp_suit = self._rotate_preview_suit.rotate(-deg, resample=Image.Resampling.BILINEAR, expand=True)
            else:
                self._rotate_temp_suit = None
            self.update_canvas_display(preview_mode=True, use_rotate=True)

        # Debounce the high-res bicubic render so it never freezes the UI while dragging
        if hasattr(self, '_rotate_debounce_id') and self._rotate_debounce_id:
            try:
                self.after_cancel(self._rotate_debounce_id)
            except Exception:
                pass
        self._rotate_debounce_id = self.after(120, self._commit_rotate_high_res)

    def _commit_rotate_high_res(self):
        self._rotate_debounce_id = None
        if getattr(self, '_rotate_base_image', None) is None:
            return
        deg = getattr(self, '_pending_rotate_deg', 0.0)
        fill = (255, 255, 255) if self._rotate_base_image.mode == 'RGB' else (0, 0, 0, 0)
        self.processed_image = self._rotate_base_image.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=fill)
        if self._rotate_base_suit is not None:
            self.suit_overlay_image = self._rotate_base_suit.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True)
        self._rotate_temp_disp = None
        self._rotate_temp_suit = None
        self.update_canvas_display()

    def apply_manual_rotate_degree(self):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        if hasattr(self, '_rotate_debounce_id') and self._rotate_debounce_id:
            try:
                self.after_cancel(self._rotate_debounce_id)
            except Exception:
                pass
            self._rotate_debounce_id = None
        try:
            val_str = self.ent_rotate_deg.get().strip()
            deg = round(float(val_str), 1)
        except Exception:
            deg = 0.0
        
        fill = (255, 255, 255) if self.processed_image.mode == 'RGB' else (0, 0, 0, 0)
        if getattr(self, '_rotate_base_image', None) is not None:
            self.save_state()
            self.invalidate_bg_cache()
            self.processed_image = self._rotate_base_image.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=fill)
            if self._rotate_base_suit is not None:
                self.suit_overlay_image = self._rotate_base_suit.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True)
        else:
            if abs(deg) > 0.01:
                self.save_state()
                self.invalidate_bg_cache()
                self.processed_image = self.processed_image.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=fill)
                if getattr(self, 'suit_overlay_image', None) is not None:
                    self.suit_overlay_image = self.suit_overlay_image.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True)
        
        self._rotate_base_image = None
        self._rotate_base_suit = None
        self._rotate_preview_base = None
        self._rotate_preview_suit = None
        self._rotate_temp_disp = None
        self._rotate_temp_suit = None
        if hasattr(self, 'sl_rotate_deg'):
            self.sl_rotate_deg.set(0)
        if hasattr(self, 'lbl_rotate_deg_val'):
            self.lbl_rotate_deg_val.configure(text='0.0°')
        if hasattr(self, 'ent_rotate_deg'):
            self.ent_rotate_deg.delete(0, 'end')
            self.ent_rotate_deg.insert(0, '0')
        self.fit_image()

    def reset_rotate_degree(self):
        if hasattr(self, '_rotate_debounce_id') and self._rotate_debounce_id:
            try:
                self.after_cancel(self._rotate_debounce_id)
            except Exception:
                pass
            self._rotate_debounce_id = None
        if getattr(self, '_rotate_base_image', None) is not None:
            self.processed_image = self._rotate_base_image.copy()
            self.suit_overlay_image = self._rotate_base_suit.copy() if self._rotate_base_suit is not None else None
            self._rotate_base_image = None
            self._rotate_base_suit = None
            self.invalidate_bg_cache()
        self._rotate_preview_base = None
        self._rotate_preview_suit = None
        self._rotate_temp_disp = None
        self._rotate_temp_suit = None
        if hasattr(self, 'sl_rotate_deg'):
            self.sl_rotate_deg.set(0)
        if hasattr(self, 'lbl_rotate_deg_val'):
            self.lbl_rotate_deg_val.configure(text='0.0°')
        if hasattr(self, 'ent_rotate_deg'):
            self.ent_rotate_deg.delete(0, 'end')
            self.ent_rotate_deg.insert(0, '0')
        self.fit_image()

    def auto_align_face(self):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')

        self.save_state()
        self.config(cursor='watch')
        self.update_idletasks()

        loading_win = ctk.CTkToplevel(self)
        loading_win.title('កំពុងដំណើរការ...')
        main_x, main_y = (self.winfo_x(), self.winfo_y())
        main_w, main_h = (self.winfo_width(), self.winfo_height())
        load_w, load_h = (340, 150)
        pos_x = main_x + main_w // 2 - load_w // 2
        pos_y = main_y + main_h // 2 - load_h // 2
        loading_win.geometry(f'{load_w}x{load_h}+{pos_x}+{pos_y}')
        loading_win.grab_set()
        loading_win.attributes('-topmost', True)
        ctk.CTkLabel(loading_win, text='🎯 កំពុងស្កេន និងតម្រង់មុខ...\nសូមរង់ចាំបន្តិច (AI Aligning)', font=('Khmer OS Siemreap', 13, 'bold'), text_color='#00F2FE').pack(pady=(20, 8))
        prog = ctk.CTkProgressBar(loading_win, width=260, height=10, progress_color='#00F2FE', mode='indeterminate')
        prog.pack(pady=4)
        prog.start()
        loading_win.update()

        align_res = {'error': None, 'tilt': 0.0, 'shift_x': 0.0, 'done': False}

        def worker():
            try:
                import torch
                import math
                import numpy as np
                import cv2
                from PIL import Image

                if getattr(self, 'face_det_model', None) is None:
                    from facexlib.detection import init_detection_model
                    model_root = os.path.join(_app_dir, 'gfpgan', 'weights')
                    if not os.path.exists(model_root):
                        model_root = resource_path('gfpgan/weights')
                    self.face_det_model = init_detection_model('retinaface_resnet50', half=False, device='cpu', model_rootpath=model_root)

                img_rgb = np.array(self.processed_image.convert('RGB'))
                img_bgr = img_rgb[:, :, ::-1].copy()
                H, W = img_bgr.shape[:2]

                with torch.no_grad():
                    faces = self.face_det_model.detect_faces(img_bgr)

                if len(faces) == 0:
                    align_res['error'] = 'រកមិនឃើញផ្ទៃមុខក្នុងរូបថតទេ សូមពិនិត្យមើលរូបថតឡើងវិញ!'
                    align_res['done'] = True
                    return

                best_face = None
                max_area = 0
                for f in faces:
                    area = (f[2] - f[0]) * (f[3] - f[1])
                    if area > max_area:
                        max_area = area
                        best_face = f

                if best_face is None:
                    align_res['error'] = 'រកមិនឃើញផ្ទៃមុខច្បាស់លាស់ទេ!'
                    align_res['done'] = True
                    return

                lx, ly = float(best_face[5]), float(best_face[6])
                rx, ry = float(best_face[7]), float(best_face[8])
                dx = rx - lx
                dy = ry - ly
                tilt_deg = math.degrees(math.atan2(dy, dx))
                center_x = (lx + rx) / 2.0
                center_y = (ly + ry) / 2.0

                # Transformation matrix to level eyes horizontally and center horizontally
                M = cv2.getRotationMatrix2D((center_x, center_y), tilt_deg, 1.0)
                shift_x = (W / 2.0) - center_x
                M[0, 2] += shift_x

                aligned_bgr = cv2.warpAffine(img_bgr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                aligned_rgb = aligned_bgr[:, :, ::-1]

                if self.processed_image.mode == 'RGBA':
                    alpha_chan = np.array(self.processed_image)[:, :, 3]
                    aligned_alpha = cv2.warpAffine(alpha_chan, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    aligned_rgba = np.dstack((aligned_rgb, aligned_alpha))
                    self.processed_image = Image.fromarray(aligned_rgba)
                else:
                    self.processed_image = Image.fromarray(aligned_rgb)

                if getattr(self, 'suit_overlay_image', None) is not None:
                    try:
                        suit_np = np.array(self.suit_overlay_image)
                        warped_suit = cv2.warpAffine(suit_np, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
                        self.suit_overlay_image = Image.fromarray(warped_suit)
                    except Exception:
                        pass

                self.invalidate_bg_cache()
                self._composite_cache_key = None
                self._composite_cache_img = None
                align_res['tilt'] = tilt_deg
                align_res['shift_x'] = shift_x
                align_res['done'] = True
            except Exception as ex:
                align_res['error'] = str(ex)
                align_res['done'] = True

        threading.Thread(target=worker, daemon=True).start()

        def check_done():
            if not loading_win.winfo_exists():
                return
            if not align_res['done']:
                self.after(50, check_done)
            else:
                try:
                    prog.stop()
                    loading_win.destroy()
                except Exception:
                    pass
                self.config(cursor='')
                self.force_foreground()
                if align_res['error']:
                    messagebox.showwarning('ជូនដំណឹង', align_res['error'])
                else:
                    self.increment_action('auto_align')
                    self.fit_image()
                    tilt_val = align_res['tilt']
                    shift_val = align_res['shift_x']
                    msg = f"✅ បានតម្រង់មុខត្រង់ស្មើ និងចំកណ្ដាលជោគជ័យ!\n• មុំផ្អៀងកែសម្រួល: {abs(tilt_val):.1f}°\n• កែតម្រូវចំកណ្ដាល: {shift_val:+.1f}px"
                    messagebox.showinfo('ជោគជ័យ', msg)

        self.after(50, check_done)

    def open_color_picker(self):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        else:
            color_win = ctk.CTkToplevel(self)
            color_win.title('Theme Colors')
            color_win.configure(fg_color='#0A0E17')
            w_win, h_win = (310, 335)
            main_x, main_y = (self.winfo_x(), self.winfo_y())
            main_w, main_h = (self.winfo_width(), self.winfo_height())
            color_win.geometry(f'{w_win}x{h_win}+{main_x + main_w // 2 - w_win // 2}+{main_y + main_h // 2 - h_win // 2}')
            color_win.grab_set()
            color_win.attributes('-topmost', True)
            theme_colors = [
                ['#FFFFFF', '#000000', '#E7E6E6', '#44546A', '#5B9BD5', '#ED7D31', '#A5A5A5', '#FFC000', '#4472C4', '#70AD47'],
                ['#F2F2F2', '#808080', '#D0CECE', '#D6DCE4', '#DEEBF7', '#FBE5D6', '#EDEDED', '#FFF2CC', '#D9E1F2', '#E2EFDA'],
                ['#D9D9D9', '#595959', '#AEAAAA', '#AEB9C7', '#BDD7EE', '#F8CBAD', '#DBDBDB', '#FFE699', '#B4C7E7', '#C6E0B4'],
                ['#BFBFBF', '#404040', '#757171', '#8497B0', '#9BC2E6', '#F4B084', '#C9C9C9', '#FFD966', '#8EA9DB', '#A9D08E'],
                ['#A6A6A6', '#262626', '#3A3838', '#333F4F', '#2E75B6', '#C55A11', '#7B7B7B', '#BF8F00', '#305496', '#548235'],
                ['#7F7F7F', '#0D0D0D', '#161616', '#222A35', '#1F4E79', '#833C0C', '#525252', '#7F6000', '#203764', '#375623']
            ]
            standard_colors = ['#C00000', '#FF0000', '#FFC000', '#FFFF00', '#92D050', '#00B050', '#00B0F0', '#0070C0', '#002060', '#7030A0']
            def apply_selected_color(hex_code):
                color_win.destroy()
                self.force_foreground()
                self.change_background(hex_code)
            def on_color_close():
                color_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            color_win.protocol("WM_DELETE_WINDOW", on_color_close)
            frame_theme = ctk.CTkFrame(color_win, fg_color='transparent')
            frame_theme.pack(pady=(12, 5), padx=10)
            ctk.CTkLabel(frame_theme, text='Theme Colors', font=('Segoe UI', 11, 'bold'), text_color='#94A3B8').grid(row=0, column=0, columnspan=10, sticky='w', padx=2, pady=(0, 5))
            for r, row_colors in enumerate(theme_colors):
                for c, hex_code in enumerate(row_colors):
                    btn = ctk.CTkButton(frame_theme, text='', width=24, height=24, corner_radius=4, fg_color=hex_code, hover_color=hex_code, border_width=1 if hex_code.upper() in ('#FFFFFF', '#F2F2F2', '#D9D9D9') else 0, border_color='#475569', command=lambda hc=hex_code: apply_selected_color(hc))
                    btn.grid(row=r + 1, column=c, padx=2, pady=2)
            ctk.CTkFrame(color_win, height=1, fg_color='#1E293B').pack(fill='x', padx=15, pady=8)
            frame_std = ctk.CTkFrame(color_win, fg_color='transparent')
            frame_std.pack(pady=0, padx=10)
            ctk.CTkLabel(frame_std, text='Standard Colors', font=('Segoe UI', 11, 'bold'), text_color='#94A3B8').grid(row=0, column=0, columnspan=10, sticky='w', padx=2, pady=(0, 5))
            for c, hex_code in enumerate(standard_colors):
                btn = ctk.CTkButton(frame_std, text='', width=24, height=24, corner_radius=4, fg_color=hex_code, hover_color=hex_code, command=lambda hc=hex_code: apply_selected_color(hc))
                btn.grid(row=1, column=c, padx=2, pady=2)
            ctk.CTkFrame(color_win, height=1, fg_color='#1E293B').pack(fill='x', padx=15, pady=8)
            from tkinter.colorchooser import askcolor
            def choose_custom_color():
                color_win.attributes('-topmost', False)
                chosen_color = askcolor(title='ជ្រើសរើស ឬវាយកូដពណ៌ (Color Code)')[1]
                if chosen_color:
                    apply_selected_color(chosen_color)
                else:
                    color_win.attributes('-topmost', True)
            btn_more = ctk.CTkButton(color_win, text='🎨 ជ្រើសរើសពណ៌បន្ថែម (More Colors)...', font=('Khmer OS Battambang', 12), fg_color='#151C2C', hover_color='#1E293B', border_width=1, border_color='#00F2FE', text_color='#00F2FE', height=34, corner_radius=8, command=choose_custom_color)
            btn_more.pack(fill='x', padx=15, pady=(4, 10))
    def get_bg_session(self, model_name=None):
        if not model_name:
            model_name = getattr(self, 'bg_model_name', 'birefnet-general-lite')
        if getattr(self, 'bg_session', None) is not None and getattr(self, 'loaded_bg_model', None) == model_name:
            return self.bg_session

        try:
            from numba.core.dispatcher import Dispatcher
            Dispatcher.enable_caching = lambda self: None
        except Exception:
            pass

        import rembg
        import onnxruntime as ort
        models_dir = os.environ.get('U2NET_HOME')
        if not models_dir or not os.path.exists(models_dir):
            _cand_list = [
                os.path.join(_app_dir, 'AI_Models'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI_Models'),
                resource_path('AI_Models'),
                os.path.join(os.path.abspath('.'), 'AI_Models')
            ]
            for _c in _cand_list:
                if os.path.exists(_c):
                    models_dir = _c
                    break
        if models_dir and os.path.exists(models_dir):
            os.environ['U2NET_HOME'] = models_dir
            os.environ['REMBG_HOME'] = models_dir
        os.environ['MODEL_CHECKSUM_DISABLED'] = '1'

        candidates = [model_name]
        for fallback in ['birefnet-general-lite', 'birefnet-portrait', 'isnet-general-use', 'u2net']:
            if fallback not in candidates:
                candidates.append(fallback)

        sess_opts = ort.SessionOptions()
        sess_opts.intra_op_num_threads = min(8, max(2, (os.cpu_count() or 4) // 2))
        sess_opts.inter_op_num_threads = 1
        sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        for cand in candidates:
            try:
                self.bg_session = rembg.new_session(cand, session_options=sess_opts)
                self.loaded_bg_model = cand
                self.bg_model_name = cand
                return self.bg_session
            except Exception:
                continue

        return None

    def on_bg_model_changed(self, choice):
        target_model = getattr(self, 'model_map', {}).get(choice, 'birefnet-general-lite')
        if target_model != getattr(self, 'loaded_bg_model', None):
            self.bg_model_name = target_model
            self.invalidate_bg_cache()
            def reload_worker():
                self.get_bg_session(target_model)
            threading.Thread(target=reload_worker, daemon=True).start()

    def change_background(self, color):
        if not getattr(self, 'processed_image', None) and (not getattr(self, 'original_image_path', None)):
            messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
            return

        if color == 'blue':
            bg_color = (0, 132, 255, 255)
        elif color == 'white':
            bg_color = (255, 255, 255, 255)
        else:
            hex_c = color.lstrip('#')
            if len(hex_c) == 6:
                bg_color = tuple(int(hex_c[i:i + 2], 16) for i in [0, 2, 4]) + (255,)
            else:
                bg_color = (255, 255, 255, 255)

        target_model = getattr(self, 'bg_model_name', 'birefnet-general-lite')
        current_img_size = self.processed_image.size if self.processed_image else None

        # Check if we have a valid cached cutout for this image & model -> Instant Swap!
        bg_cache = getattr(self, '_bg_cache', None)
        can_reuse_cache = (
            bg_cache is not None
            and bg_cache.get('model') == target_model
            and bg_cache.get('size') == current_img_size
            and bg_cache.get('fg_clean') is not None
            and bg_cache.get('alpha') is not None
        )

        if can_reuse_cache:
            self.save_state()
            alpha = bg_cache['alpha']
            fg_clean = bg_cache['fg_clean']
            target_bg_rgb = np.array(bg_color[:3], dtype=np.float32)
            composite_rgb = np.clip(fg_clean * alpha + target_bg_rgb * (1.0 - alpha), 0, 255).astype(np.uint8)
            self.processed_image = Image.fromarray(composite_rgb).convert('RGBA')
            self._composite_cache_key = None
            self._composite_cache_img = None
            self.update_canvas_display()
            if color == 'blue':
                self.increment_action('bg_blue')
            elif color == 'white':
                self.increment_action('bg_white')
            else:
                self.increment_action('bg_custom')
            return

        self.save_state()
        loading_win = ctk.CTkToplevel(self)
        loading_win.title('កំពុងដំណើរការ...')
        self.update_idletasks()
        main_x, main_y = (self.winfo_x(), self.winfo_y())
        main_w, main_h = (self.winfo_width(), self.winfo_height())
        load_w, load_h = (350, 180)
        loading_win.geometry(f'{load_w}x{load_h}+{main_x + main_w // 2 - load_w // 2}+{main_y + main_h // 2 - load_h // 2}')
        loading_win.grab_set()
        loading_win.attributes('-topmost', True)
        lbl = ctk.CTkLabel(loading_win, text='✂️ ដំណើរការដូរផ្ទៃក្រោយ (AI Background)\nកាត់សរសៃសក់កម្រិត Ultra HD...', font=('Khmer OS Siemreap', 14, 'bold'), text_color='#3498DB')
        lbl.pack(pady=(20, 10))
        progress_var = tk.DoubleVar(value=0.0)
        ctk.CTkProgressBar(loading_win, variable=progress_var, width=280, height=15, progress_color='#3498DB').pack(pady=(0, 5))
        lbl_percent = ctk.CTkLabel(loading_win, text='0%', font=('Arial', 13, 'bold'), text_color='white')
        lbl_percent.pack()
        self.config(cursor='watch')
        loading_win.update()
        bg_result = {'done': False, 'error': None}
        def run_bg():
            try:
                import io
                from PIL import Image

                try:
                    from numba.core.dispatcher import Dispatcher
                    Dispatcher.enable_caching = lambda self: None
                except Exception:
                    pass

                base_cand = getattr(self, '_bg_base_image', None)
                if base_cand is not None and self.processed_image and base_cand.size == self.processed_image.size:
                    orig_img = base_cand.copy()
                elif self.processed_image:
                    orig_img = self.processed_image.copy()
                    self._bg_base_image = orig_img.copy()
                else:
                    orig_img = Image.open(self.original_image_path).copy()
                    self._bg_base_image = orig_img.copy()

                if orig_img.mode not in ('RGB', 'RGBA'):
                    orig_img = orig_img.convert('RGB')
                orig_size = orig_img.size
                w, h = orig_size

                # Native optimal resolution for BiRefNet AI model is 1024px
                max_dim = 1024
                if max(w, h) > max_dim:
                    scale = max_dim / float(max(w, h))
                    proc_size = (int(w * scale), int(h * scale))
                    ai_input = orig_img.convert('RGB').resize(proc_size, Image.Resampling.BILINEAR)
                else:
                    proc_size = orig_size
                    ai_input = orig_img.convert('RGB')

                session = self.get_bg_session(target_model)
                if not session:
                    raise RuntimeError("មិនអាចបើកដំណើរការ AI Model បានទេ")

                import rembg
                # Direct PIL input skips slow PNG encoding and decoding
                mask_data = rembg.remove(ai_input, session=session, only_mask=True)
                if isinstance(mask_data, Image.Image):
                    mask_img = mask_data.convert('L')
                elif isinstance(mask_data, bytes):
                    mask_img = Image.open(io.BytesIO(mask_data)).convert('L')
                else:
                    mask_img = Image.fromarray(mask_data).convert('L')

                import cv2
                import numpy as np

                # Ultra-fast edge color decontamination on 1024px buffer (preserves fine hair strands without old background bleed)
                mask_small = np.array(mask_img).astype(np.float32) / 255.0
                solid_mask = (mask_small >= 0.85)
                border_mask = (mask_small > 0.03) & (mask_small < 0.85)

                if np.any(solid_mask) and np.any(border_mask):
                    ai_np = np.array(ai_input)
                    known = np.where(solid_mask[:, :, None], ai_np, 0).astype(np.uint8)
                    clean_fg_small = cv2.inpaint(known, (~solid_mask).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)
                    clean_fg = cv2.resize(clean_fg_small, orig_size, interpolation=cv2.INTER_LINEAR)
                else:
                    clean_fg = None

                if proc_size != orig_size:
                    mask_img = mask_img.resize(orig_size, Image.Resampling.BILINEAR)

                alpha = (np.array(mask_img).astype(np.float32) / 255.0)[:, :, None]
                orig_rgb_np = np.array(orig_img.convert('RGB'))
                orig_float = orig_rgb_np.astype(np.float32)

                if clean_fg is not None:
                    blend_ratio = np.clip((0.85 - alpha) / 0.82, 0.0, 1.0)
                    fg_clean = np.where((alpha > 0.03) & (alpha < 0.85), orig_float * (1.0 - blend_ratio * 0.65) + clean_fg * (blend_ratio * 0.65), orig_float)
                else:
                    fg_clean = orig_float

                # Cache cutout and clean foreground for instant future color swaps!
                self._bg_cache = {
                    'model': target_model,
                    'size': orig_size,
                    'fg_clean': fg_clean,
                    'alpha': alpha,
                    'mask_img': mask_img
                }

                target_bg_rgb = np.array(bg_color[:3], dtype=np.float32)
                composite_rgb = np.clip(fg_clean * alpha + target_bg_rgb * (1.0 - alpha), 0, 255).astype(np.uint8)
                self.processed_image = Image.fromarray(composite_rgb).convert('RGBA')
                self._composite_cache_key = None
                self._composite_cache_img = None
                bg_result['done'] = True
            except Exception as e:
                bg_result['error'] = str(e)
                bg_result['done'] = True
        threading.Thread(target=run_bg, daemon=True).start()
        def check_progress():
            if not loading_win.winfo_exists():
                return
            if not bg_result['done']:
                cur = progress_var.get()
                if cur < 0.80:
                    new_val = cur + 0.03
                elif cur < 0.92:
                    new_val = cur + 0.01
                elif cur < 0.97:
                    new_val = cur + 0.003
                else:
                    new_val = min(0.98, cur + 0.001)
                progress_var.set(new_val)
                lbl_percent.configure(text=f'{int(new_val * 100)}%')
                self.after(80, check_progress)
            else:
                progress_var.set(1.0)
                lbl_percent.configure(text='100%')
                loading_win.update()
                self.after(150, finish_bg)
        def finish_bg():
            if loading_win.winfo_exists():
                loading_win.destroy()
            self.force_foreground()
            self.after(50, self.force_foreground)
            self.config(cursor='')
            if bg_result['error']:
                messagebox.showerror('បញ្ហា', f"មាន Error ពេលដូរផ្ទៃក្រោយ:\n{bg_result['error']}")
                return
            else:
                self.update_canvas_display()
                if color == 'blue':
                    self.increment_action('bg_blue')
                else:
                    if color == 'white':
                        self.increment_action('bg_white')
                    else:
                        self.increment_action('bg_custom')
        self.after(50, check_progress)

    def enhance_quality(self):
        if not self.processed_image:
            return
        self.save_state()
        self.config(cursor='watch')
        self.update_idletasks()

        loading_win = ctk.CTkToplevel(self)
        loading_win.title('កំពុងដំណើរការ...')
        main_x, main_y = (self.winfo_x(), self.winfo_y())
        main_w, main_h = (self.winfo_width(), self.winfo_height())
        load_w, load_h = (320, 140)
        pos_x = main_x + main_w // 2 - load_w // 2
        pos_y = main_y + main_h // 2 - load_h // 2
        loading_win.geometry(f'{load_w}x{load_h}+{pos_x}+{pos_y}')
        loading_win.grab_set()
        loading_win.attributes('-topmost', True)
        ctk.CTkLabel(loading_win, text='✨ កំពុង AI Enhance...\nសូមមេត្តារង់ចាំបន្តិច 🙏', font=('Khmer OS Siemreap', 13, 'bold'), text_color='#00F5A0').pack(pady=(18, 8))
        prog = ctk.CTkProgressBar(loading_win, width=240, height=10, progress_color='#00F5A0', mode='indeterminate')
        prog.pack(pady=4)
        prog.start()
        loading_win.update()

        def worker():
            try:
                import cv2
                import numpy as np
                from PIL import Image, ImageEnhance
                img = self.processed_image
                w, h = img.size
                upscaled_img = img.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
                open_cv_image = np.array(upscaled_img.convert('RGB'))[:, :, ::-1].copy()
                smoothed = cv2.bilateralFilter(open_cv_image, d=7, sigmaColor=40, sigmaSpace=40)
                gaussian = cv2.GaussianBlur(smoothed, (0, 0), 3.0)
                sharp_cv = cv2.addWeighted(smoothed, 1.8, gaussian, -0.8, 0)
                final_pil = Image.fromarray(cv2.cvtColor(sharp_cv, cv2.COLOR_BGR2RGB))
                final_pil = ImageEnhance.Sharpness(final_pil).enhance(2.0)
                final_pil = ImageEnhance.Color(final_pil).enhance(1.1)
                final_pil = ImageEnhance.Contrast(final_pil).enhance(1.05)
                suit_up = None
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None:
                    suit_up = self.suit_overlay_image.resize((w * 2, h * 2), Image.Resampling.LANCZOS)

                def on_done():
                    try:
                        self.processed_image = final_pil
                        if suit_up is not None:
                            self.suit_overlay_image = suit_up
                        self.fit_image()
                        self.increment_action('enhance')
                    finally:
                        self.config(cursor='')
                        try:
                            loading_win.grab_release()
                            loading_win.destroy()
                        except Exception:
                            pass
                self.after(0, on_done)
            except Exception as e:
                print('Error ពេល Enhance:', e)
                def on_err():
                    self.config(cursor='')
                    try:
                        loading_win.grab_release()
                        loading_win.destroy()
                    except Exception:
                        pass
                self.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()
    def apply_ai_face_restore(self):
        if not self.processed_image:
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        else:
            loading_win = ctk.CTkToplevel(self)
            loading_win.title('កំពុងដំណើរការ...')
            self.update_idletasks()
            main_x, main_y = (self.winfo_x(), self.winfo_y())
            main_w, main_h = (self.winfo_width(), self.winfo_height())
            load_w, load_h = (350, 180)
            pos_x = main_x + main_w // 2 - load_w // 2
            pos_y = main_y + main_h // 2 - load_h // 2
            loading_win.geometry(f'{load_w}x{load_h}+{pos_x}+{pos_y}')
            loading_win.grab_set()
            loading_win.attributes('-topmost', True)
            lbl = ctk.CTkLabel(loading_win, text='✨ Ai កំពុងដំណើរការ...\nសូមមេត្តារង់ចាំ (Loading) 🙏', font=('Khmer OS Siemreap', 16, 'bold'), text_color='#F39C12')
            lbl.pack(pady=(20, 10))
            progress_var = tk.DoubleVar()
            progress_var.set(0.0)
            progress_bar = ctk.CTkProgressBar(loading_win, variable=progress_var, width=280, height=15, progress_color='#2ECC71')
            progress_bar.pack(pady=(0, 5))
            lbl_percent = ctk.CTkLabel(loading_win, text='0%', font=('Arial', 13, 'bold'), text_color='white')
            lbl_percent.pack()
            self.config(cursor='watch')
            loading_win.update()
            ai_result = {'img': None, 'error': None, 'done': False}
            def run_ai():
                try:
                    import cv2
                    import numpy as np
                    from PIL import Image
                    import os
                    import sys

                    # Ensure torchvision backward compatibility patch for GFPGAN
                    try:
                        import torchvision.transforms.functional as TF
                        if 'torchvision.transforms.functional_tensor' not in sys.modules:
                            sys.modules['torchvision.transforms.functional_tensor'] = TF
                    except Exception:
                        pass

                    try:
                        from gfpgan import GFPGANer
                    except Exception as imp_err:
                        ai_result['error'] = f'បរាជ័យក្នុងការ Import GFPGANer: {imp_err}'
                        ai_result['done'] = True
                        return

                    img_cv = np.array(self.processed_image.convert('RGB'))[:, :, ::(-1)].copy()

                    cand_models = [
                        os.path.join(_app_dir, 'AI_Models', 'GFPGANv1.4.pth'),
                        os.path.join('AI_Models', 'GFPGANv1.4.pth'),
                        resource_path('AI_Models/GFPGANv1.4.pth'),
                        resource_path('GFPGANv1.4.pth'),
                    ]
                    model_path = None
                    for _c in cand_models:
                        if os.path.exists(_c):
                            model_path = _c
                            break

                    if not model_path:
                        ai_result['error'] = 'រកមិនឃើញ File GFPGANv1.4.pth ក្នុង AI_Models ទេ!\nសូមប្រាកដថាបានដាក់ File ម៉ូដែលត្រឹមត្រូវ។'
                        ai_result['done'] = True
                        return

                    restorer = GFPGANer(model_path=model_path, upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None)
                    cropped_faces, restored_faces, restored_img = restorer.enhance(img_cv, has_aligned=False, only_center_face=False, paste_back=True, weight=0.2)
                    if restored_img is not None:
                        ai_result['img'] = Image.fromarray(restored_img[:, :, ::(-1)])
                    ai_result['done'] = True
                except Exception as e:
                    ai_result['error'] = str(e)
                    ai_result['done'] = True
            import threading
            threading.Thread(target=run_ai, daemon=True).start()
            def check_progress():
                if not loading_win.winfo_exists():
                    return
                else:
                    if not ai_result['done']:
                        current_val = progress_var.get()
                        if current_val < 0.95:
                            new_val = current_val + 0.02
                            progress_var.set(new_val)
                            lbl_percent.configure(text=f'{int(new_val * 100)}%')
                        self.after(200, check_progress)
                    else:
                        progress_var.set(1.0)
                        lbl_percent.configure(text='100%')
                        loading_win.update()
                        self.after(300, finish_ai)
            def finish_ai():
                if loading_win.winfo_exists():
                    loading_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
                self.config(cursor='')
                if ai_result['error']:
                    messagebox.showerror('បញ្ហា', f"មាន Error ពេលដំណើរការ AI: {ai_result['error']}")
                    return
                else:
                    if ai_result['img']:
                        self.save_state()
                        self.processed_image = ai_result['img']
                        self.fit_image()
                        self.increment_action('color')
                        success_win = ctk.CTkToplevel(self)
                        success_win.title('✨ លទ្ធផល')
                        succ_w, succ_h = (450, 150)
                        succ_x = main_x + main_w // 2 - succ_w // 2
                        succ_y = main_y + main_h // 2 - succ_h // 2
                        success_win.geometry(f'{succ_w}x{succ_h}+{succ_x}+{succ_y}')
                        success_win.grab_set()
                        success_win.attributes('-topmost', True)
                        def on_ok():
                            success_win.destroy()
                            self.force_foreground()
                            self.after(50, self.force_foreground)
                        success_win.protocol("WM_DELETE_WINDOW", on_ok)
                        msg_lbl = ctk.CTkLabel(success_win, text='✅ មុខងារ Ai ជួសជុលមុខបានដំណើររួចរាល់ 100%', font=('Khmer OS Siemreap', 16, 'bold'), text_color='#2ECC71')
                        msg_lbl.pack(expand=True, pady=(20, 10))
                        ok_btn = ctk.CTkButton(success_win, text='យល់ព្រម (OK)', font=('Khmer OS Siemreap', 14), command=on_ok, width=120)
                        ok_btn.pack(pady=(0, 20))
            self.after(100, check_progress)
    def process_natural_skin_retouch(self, img_bgr, smooth_val=0.68, blemish_val=0.72, texture_val=0.82, radiance_val=10, precomputed_mask=None):
        h_img, w_img = img_bgr.shape[:2]
        scale_ref = min(h_img, w_img)

        # 1. Skin Mask with edge and feature protection (Eyes, eyebrows, lips, nostrils)
        if precomputed_mask is not None:
            feathered_mask = precomputed_mask
        else:
            ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
            mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77], dtype=np.uint8), np.array([255, 175, 127], dtype=np.uint8))
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            mask_hsv1 = cv2.inRange(hsv, np.array([0, 15, 30], dtype=np.uint8), np.array([28, 255, 255], dtype=np.uint8))
            mask_hsv2 = cv2.inRange(hsv, np.array([165, 15, 30], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8))
            mask_hsv = cv2.bitwise_or(mask_hsv1, mask_hsv2)
            skin = cv2.bitwise_and(mask_ycrcb, mask_hsv)
            if cv2.countNonZero(skin) < (h_img * w_img * 0.02):
                skin = mask_ycrcb

            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            med = float(np.median(gray))
            lower = int(max(0, 0.66 * med))
            upper = int(min(255, 1.33 * med))
            edges = cv2.Canny(gray, lower, upper)
            k_edge = max(3, int(scale_ref * 0.006)) | 1
            edge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_edge, k_edge))
            dilated_edges = cv2.dilate(edges, edge_kernel, iterations=1)

            dark_mask = (gray < 35).astype(np.uint8) * 255
            lip_mask = ((ycrcb[:, :, 1] > 175) & (hsv[:, :, 1] > 140)).astype(np.uint8) * 255
            excluded = cv2.bitwise_or(dilated_edges, dark_mask)
            excluded = cv2.bitwise_or(excluded, lip_mask)
            skin[excluded > 0] = 0

            feather_k = max(7, int(scale_ref * 0.015)) | 1
            feathered_mask = cv2.GaussianBlur(skin, (feather_k, feather_k), 0).astype(np.float32) / 255.0

        # 2. Smart Acne & Blemish Removal (Inpainting detected pimples/spots without smearing)
        cleaned_img = img_bgr.copy()
        if blemish_val > 0.05:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            spot_radius = max(5, int(scale_ref * 0.012)) | 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (spot_radius, spot_radius))
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            b, g, r = cv2.split(img_bgr)
            redness = cv2.subtract(r, g)
            red_blackhat = cv2.morphologyEx(redness, cv2.MORPH_TOPHAT, kernel)
            combined_spot_resp = cv2.addWeighted(blackhat, 0.6, red_blackhat, 0.4, 0)
            skin_u8 = (feathered_mask > 0.35).astype(np.uint8)
            combined_spot_resp = cv2.bitwise_and(combined_spot_resp, combined_spot_resp, mask=skin_u8)
            thresh_val = max(12, int(28 - blemish_val * 16))
            _, spot_mask = cv2.threshold(combined_spot_resp, thresh_val, 255, cv2.THRESH_BINARY)
            spot_mask = cv2.morphologyEx(spot_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
            dil_k = max(3, int(scale_ref * 0.005)) | 1
            spot_mask = cv2.dilate(spot_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil_k, dil_k)), iterations=1)
            if cv2.countNonZero(spot_mask) > 0:
                inpaint_radius = max(3, int(scale_ref * 0.006))
                inpainted = cv2.inpaint(img_bgr, spot_mask, inpaint_radius, cv2.INPAINT_TELEA)
                spot_f = cv2.GaussianBlur(spot_mask, (dil_k | 1, dil_k | 1), 0).astype(np.float32) / 255.0 * blemish_val
                spot_3c = np.repeat(spot_f[:, :, np.newaxis], 3, axis=2)
                cleaned_img = np.clip(img_bgr.astype(np.float32) * (1.0 - spot_3c) + inpainted.astype(np.float32) * spot_3c, 0, 255).astype(np.uint8)

        # 3. Frequency Separation & Guided Filtering (Natural texture preservation)
        if smooth_val > 0.01:
            radius = max(5, int(scale_ref * 0.015 * (0.5 + smooth_val * 0.8))) | 1
            eps = (0.02 + 0.04 * smooth_val) * (255 * 255)
            if hasattr(cv2, 'ximgproc') and hasattr(cv2.ximgproc, 'guidedFilter'):
                smoothed = cv2.ximgproc.guidedFilter(guide=cleaned_img, src=cleaned_img, radius=radius, eps=eps)
            else:
                d_val = max(9, int(scale_ref * 0.02)) | 1
                smoothed = cv2.bilateralFilter(cleaned_img, d_val, 75, 75)

            # High Frequency texture: extract micro pores & authentic fine details
            diff = cv2.subtract(cleaned_img, smoothed)
            high_pass = cv2.GaussianBlur(diff, (3, 3), 0)
            smooth_with_texture = cv2.addWeighted(smoothed, 1.0, high_pass, float(texture_val), 0)

            # Subtle Skin Radiance / Glow
            if radiance_val != 0:
                glow_val = radiance_val * 0.15
                smooth_with_texture = np.clip(smooth_with_texture.astype(np.float32) + glow_val, 0, 255).astype(np.uint8)

            mask_3c = np.repeat(feathered_mask[:, :, np.newaxis], 3, axis=2)
            effective_mask = np.clip(mask_3c * smooth_val, 0.0, 1.0)
            final_bgr = (img_bgr.astype(np.float32) * (1.0 - effective_mask) + smooth_with_texture.astype(np.float32) * effective_mask)
            final_bgr = np.clip(final_bgr, 0, 255).astype(np.uint8)
        else:
            final_bgr = cleaned_img

        return final_bgr, feathered_mask

    def apply_natural_retouch_1click(self):
        if not self.ensure_license_active("មុខងារ 1-Click មុខរលោង"):
            return
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ជាក់', 'សូមបញ្ចូលរូបថតជាមុនសិន!')

        self.save_state()
        self.config(cursor='watch')
        self.update_idletasks()

        loading_win = ctk.CTkToplevel(self)
        loading_win.title('កំពុងដំណើរការ...')
        load_w, load_h = (360, 150)
        main_x, main_y = (self.winfo_x(), self.winfo_y())
        main_w, main_h = (self.winfo_width(), self.winfo_height())
        pos_x = main_x + main_w // 2 - load_w // 2
        pos_y = main_y + main_h // 2 - load_h // 2
        loading_win.geometry(f'{load_w}x{load_h}+{pos_x}+{pos_y}')
        loading_win.grab_set()
        loading_win.attributes('-topmost', True)

        ctk.CTkLabel(loading_win, text='✨ កំពុង Retouch មុខម៉ដ្ឋ & លុបមុនបែបធម្មជាតិ...\nសូមមេត្តារង់ចាំបន្តិច 🙏', font=('Khmer OS Siemreap', 13, 'bold'), text_color='#EC4899').pack(pady=(20, 8))
        prog = ctk.CTkProgressBar(loading_win, width=270, height=10, progress_color='#EC4899', mode='indeterminate')
        prog.pack(pady=4)
        prog.start()
        loading_win.update()

        def worker():
            try:
                base_bgr = np.array(self.processed_image.convert('RGB'))[:, :, ::-1].copy()
                final_bgr, _ = self.process_natural_skin_retouch(base_bgr, smooth_val=0.68, blemish_val=0.72, texture_val=0.82, radiance_val=10)
                final_pil = Image.fromarray(cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB))

                def on_done():
                    try:
                        self.processed_image = final_pil
                        if hasattr(self, 'base_makeup_img'):
                            self.base_makeup_img = self.processed_image.copy()
                        self.update_canvas_display()
                        self.increment_action('makeup')
                    finally:
                        self.config(cursor='')
                        try:
                            loading_win.grab_release()
                            loading_win.destroy()
                        except Exception:
                            pass
                        self.force_foreground()

                    # Success Popup with option to open Retouch Studio for fine-tuning
                    succ_win = ctk.CTkToplevel(self)
                    succ_win.title('✨ ស្បែករលោងបែបធម្មជាតិ')
                    w_s, h_s = (450, 175)
                    sw = self.winfo_screenwidth()
                    sh = self.winfo_screenheight()
                    succ_win.geometry(f'{w_s}x{h_s}+{int(sw/2 - w_s/2)}+{int(sh/2 - h_s/2)}')
                    succ_win.attributes('-topmost', True)
                    succ_win.grab_set()

                    def close_succ():
                        try:
                            succ_win.destroy()
                        except Exception:
                            pass
                        self.force_foreground()

                    succ_win.protocol('WM_DELETE_WINDOW', close_succ)
                    ctk.CTkLabel(succ_win, text='✅ មុខ Smooth & លុបមុនបែបធម្មជាតិ បានអនុវត្តរួចរាល់ 100%!', font=('Khmer OS Siemreap', 14, 'bold'), text_color='#10B981').pack(pady=(18, 6))
                    ctk.CTkLabel(succ_win, text='(រក្សាគ្រាប់ស្បែក និងរន្ធញើសធម្មជាតិ មិនបាត់បង់គុណភាព)', font=('Khmer OS Siemreap', 11), text_color='#94A3B8').pack(pady=(0, 14))

                    btn_row = ctk.CTkFrame(succ_win, fg_color='transparent')
                    btn_row.pack(pady=4)
                    ctk.CTkButton(btn_row, text='យល់ព្រម (OK)', font=('Khmer OS Siemreap', 12, 'bold'), width=120, height=34, fg_color='#059669', hover_color='#047857', command=close_succ).pack(side='left', padx=6)
                    ctk.CTkButton(btn_row, text='🎛️ បើកផ្ទាំងសារ៉េកម្រិត (Studio)', font=('Khmer OS Siemreap', 12, 'bold'), width=180, height=34, fg_color='#7C3AED', hover_color='#6D28D9', command=lambda: (close_succ(), self.open_retouch_studio())).pack(side='left', padx=6)
                    succ_win.after(3500, close_succ)

                self.after(0, on_done)
            except Exception as e:
                print('Error in natural retouch 1-click:', e)
                def on_err():
                    self.config(cursor='')
                    try:
                        loading_win.grab_release()
                        loading_win.destroy()
                    except Exception:
                        pass
                    messagebox.showerror('បញ្ហា', f'បរាជ័យក្នុងការ Retouch ស្បែក: {e}')
                self.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()

    def apply_makeup(self):
        self.apply_natural_retouch_1click()

    def open_retouch_studio(self):
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')

        base_pil = self.processed_image.convert('RGB')
        orig_bgr = np.array(base_pil)[:, :, ::-1].copy()
        h_orig, w_orig = orig_bgr.shape[:2]

        # Fast live preview buffer: downscale to max 1000px so sliders are buttery smooth (50ms response)
        max_p_dim = 1000
        scale_p = min(1.0, float(max_p_dim) / max(w_orig, h_orig))
        pw = max(10, int(w_orig * scale_p))
        ph = max(10, int(h_orig * scale_p))
        if scale_p < 1.0:
            preview_bgr = cv2.resize(orig_bgr, (pw, ph), interpolation=cv2.INTER_AREA)
        else:
            preview_bgr = orig_bgr.copy()

        preview_base_pil = Image.fromarray(cv2.cvtColor(preview_bgr, cv2.COLOR_BGR2RGB))
        display_pil = preview_base_pil.copy()

        # Precompute skin mask on preview buffer once
        _, cached_skin_mask = self.process_natural_skin_retouch(preview_bgr, smooth_val=0.0, blemish_val=0.0)

        retouch_win = ctk.CTkToplevel(self)
        retouch_win.title('✨ Natural Skin Retouch Studio (មុខម៉ដ្ឋរលោង & លុបមុនបែបធម្មជាតិ)')
        retouch_win.configure(fg_color='#07090E')
        retouch_win.transient(self)
        retouch_win.attributes('-topmost', True)

        w_win, h_win = (1280, 750)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        pos_x = max(10, int(sw / 2 - w_win / 2))
        pos_y = max(10, int(sh / 2 - h_win / 2))
        retouch_win.geometry(f'{w_win}x{h_win}+{pos_x}+{pos_y}')
        retouch_win.grab_set()

        # Interactive Canvas State
        zoom_level = [1.0]
        canvas_img_x = [400]
        canvas_img_y = [300]
        is_comparing_before = [False]
        after_debounce_id = [None]
        pan_last_pos = [0, 0]

        # UI Layout: Left Controls + Center Canvas
        left_frame = ctk.CTkFrame(retouch_win, width=370, fg_color='#0F172A', corner_radius=12, border_width=1, border_color='#1E293B')
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)

        center_frame = ctk.CTkFrame(retouch_win, fg_color='#080B12', corner_radius=12, border_width=1, border_color='#1E293B')
        center_frame.pack(side='left', fill='both', expand=True, padx=5, pady=10)

        # Top Bar: Status Badge + Dimensions + Zoom Controls
        top_bar = ctk.CTkFrame(center_frame, fg_color='#0B101D', height=40, corner_radius=8)
        top_bar.pack(fill='x', padx=8, pady=(8, 4))

        lbl_status_badge = ctk.CTkLabel(
            top_bar, text='✨ កែរួច (AFTER)',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            fg_color='#064E3B', text_color='#34D399', corner_radius=6, width=120, height=26
        )
        lbl_status_badge.pack(side='left', padx=(8, 4), pady=6)

        ctk.CTkLabel(
            top_bar, text=f'ទំហំ: {w_orig}×{h_orig}px',
            font=('Khmer OS Siemreap', 10), text_color='#94A3B8'
        ).pack(side='left', padx=6)

        # Zoom Controls inside Top Bar
        frame_zoom = ctk.CTkFrame(top_bar, fg_color='transparent')
        frame_zoom.pack(side='right', padx=8, pady=4)

        lbl_zoom = ctk.CTkLabel(frame_zoom, text='100%', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#00F2FE', width=52)

        def zoom_by_factor(factor, center_x=None, center_y=None):
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            if center_x is None:
                center_x = cw // 2
            if center_y is None:
                center_y = ch // 2

            new_zoom = max(0.1, min(8.0, zoom_level[0] * factor))
            if abs(new_zoom - zoom_level[0]) < 1e-4:
                return
            actual_factor = new_zoom / zoom_level[0]
            canvas_img_x[0] = int(center_x - (center_x - canvas_img_x[0]) * actual_factor)
            canvas_img_y[0] = int(center_y - (center_y - canvas_img_y[0]) * actual_factor)
            zoom_level[0] = new_zoom
            lbl_zoom.configure(text=f'{int(zoom_level[0] * 100)}%')
            render_canvas()

        def set_zoom_exact(val):
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            actual_factor = val / zoom_level[0]
            canvas_img_x[0] = int(cw // 2 - (cw // 2 - canvas_img_x[0]) * actual_factor)
            canvas_img_y[0] = int(ch // 2 - (ch // 2 - canvas_img_y[0]) * actual_factor)
            zoom_level[0] = val
            lbl_zoom.configure(text=f'{int(zoom_level[0] * 100)}%')
            render_canvas()

        def fit_canvas_image():
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            zoom_level[0] = min(cw / pw, ch / ph) * 0.95
            canvas_img_x[0] = cw // 2
            canvas_img_y[0] = ch // 2
            lbl_zoom.configure(text=f'{int(zoom_level[0] * 100)}%')
            render_canvas()

        ctk.CTkButton(frame_zoom, text='➖', width=28, height=26, font=('Arial', 10), fg_color='#1E293B', hover_color='#334155', command=lambda: zoom_by_factor(0.85)).pack(side='left', padx=2)
        lbl_zoom.pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='➕', width=28, height=26, font=('Arial', 10), fg_color='#1E293B', hover_color='#334155', command=lambda: zoom_by_factor(1.15)).pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='100%', width=44, height=26, font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), fg_color='#1E293B', hover_color='#334155', command=lambda: set_zoom_exact(1.0)).pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='⛶ Fit', width=44, height=26, font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), fg_color='#1E293B', hover_color='#334155', command=lambda: fit_canvas_image()).pack(side='left', padx=2)

        # Interactive Zoomable Canvas
        canvas = tk.Canvas(center_frame, bg='#080B12', highlightthickness=0, cursor='hand2')
        canvas.pack(fill='both', expand=True, padx=6, pady=6)

        def render_canvas():
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)

            img_to_show = preview_base_pil if is_comparing_before[0] else display_pil
            img_w, img_h = img_to_show.size
            z = zoom_level[0]

            disp_w = max(1, int(img_w * z))
            disp_h = max(1, int(img_h * z))

            cx = canvas_img_x[0]
            cy = canvas_img_y[0]

            x1 = cx - disp_w // 2
            y1 = cy - disp_h // 2

            # Viewport-aware slice to keep redraw times under 2ms even at 500% zoom
            src_x1 = max(0, int((0 - x1) / z))
            src_y1 = max(0, int((0 - y1) / z))
            src_x2 = min(img_w, int((cw - x1) / z) + 1)
            src_y2 = min(img_h, int((ch - y1) / z) + 1)

            canvas.delete('all')
            if src_x2 > src_x1 and src_y2 > src_y1:
                crop_w = max(1, int((src_x2 - src_x1) * z))
                crop_h = max(1, int((src_y2 - src_y1) * z))
                part = img_to_show.crop((src_x1, src_y1, src_x2, src_y2)).resize((crop_w, crop_h), Image.Resampling.BILINEAR)
                tk_photo = ImageTk.PhotoImage(part)
                dst_x = int(x1 + src_x1 * z)
                dst_y = int(y1 + src_y1 * z)

                canvas.create_image(dst_x, dst_y, image=tk_photo, anchor='nw')
                canvas._photo_cache = tk_photo

        # Canvas Mouse Wheel Zoom & Pan Bindings
        def on_mouse_wheel(e):
            factor = 1.15 if e.delta > 0 else 0.85
            zoom_by_factor(factor, e.x, e.y)

        canvas.bind('<MouseWheel>', on_mouse_wheel)
        canvas.bind('<Button-4>', lambda e: zoom_by_factor(1.15, e.x, e.y))
        canvas.bind('<Button-5>', lambda e: zoom_by_factor(0.85, e.x, e.y))

        def on_pan_press(e):
            pan_last_pos[0] = e.x
            pan_last_pos[1] = e.y
            canvas.configure(cursor='fleur')

        def on_pan_drag(e):
            dx = e.x - pan_last_pos[0]
            dy = e.y - pan_last_pos[1]
            pan_last_pos[0] = e.x
            pan_last_pos[1] = e.y
            canvas_img_x[0] += dx
            canvas_img_y[0] += dy
            render_canvas()

        def on_pan_release(e):
            canvas.configure(cursor='hand2')

        canvas.bind('<ButtonPress-1>', on_pan_press)
        canvas.bind('<B1-Motion>', on_pan_drag)
        canvas.bind('<ButtonRelease-1>', on_pan_release)

        canvas.bind('<ButtonPress-2>', on_pan_press)
        canvas.bind('<B2-Motion>', on_pan_drag)
        canvas.bind('<ButtonRelease-2>', on_pan_release)

        canvas.bind('<ButtonPress-3>', on_pan_press)
        canvas.bind('<B3-Motion>', on_drag) if 'on_drag' in locals() else None
        canvas.bind('<ButtonRelease-3>', on_pan_release)

        canvas.bind('<Double-Button-1>', lambda e: fit_canvas_image() if abs(zoom_level[0] - 1.0) < 0.15 else set_zoom_exact(1.0))

        # Header in Left Controls
        head_l = ctk.CTkFrame(left_frame, fg_color='transparent')
        head_l.pack(fill='x', padx=14, pady=(14, 4))
        ctk.CTkLabel(head_l, text='●', font=('Arial', 12), text_color='#EC4899').pack(side='left', padx=(0, 6))
        ctk.CTkLabel(head_l, text='កែសម្រស់ស្បែកមុខបែបធម្មជាតិ', font=ctk.CTkFont(family='Khmer OS Siemreap', size=14, weight='bold'), text_color='#F1F5F9').pack(side='left')

        ctk.CTkLabel(left_frame, text='បច្ចេកវិទ្យា Frequency Separation រក្សាគ្រាប់ស្បែក 100%', font=('Khmer OS Siemreap', 10), text_color='#94A3B8').pack(anchor='w', padx=16, pady=(0, 8))

        scroll_controls = ctk.CTkScrollableFrame(left_frame, fg_color='transparent')
        scroll_controls.pack(fill='both', expand=True, padx=4, pady=2)

        # Variables for Sliders
        var_smooth = ctk.DoubleVar(value=65.0)
        var_blemish = ctk.DoubleVar(value=70.0)
        var_texture = ctk.DoubleVar(value=80.0)
        var_radiance = ctk.DoubleVar(value=10.0)

        val_labels = {}

        def process_retouch_pipeline():
            sm = var_smooth.get() / 100.0
            bl = var_blemish.get() / 100.0
            tx = var_texture.get() / 100.0
            rd = var_radiance.get()

            # Process on preview_bgr (takes ~30ms, completely lag-free)
            res_bgr, _ = self.process_natural_skin_retouch(
                preview_bgr, smooth_val=sm, blemish_val=bl, texture_val=tx, radiance_val=rd, precomputed_mask=cached_skin_mask
            )

            nonlocal display_pil
            display_pil = Image.fromarray(cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB))
            if not is_comparing_before[0]:
                render_canvas()

        def on_slider_moved(val=None):
            val_labels['smooth'].configure(text=f'{int(var_smooth.get())}%')
            val_labels['blemish'].configure(text=f'{int(var_blemish.get())}%')
            val_labels['texture'].configure(text=f'{int(var_texture.get())}%')
            rad_val = int(var_radiance.get())
            val_labels['radiance'].configure(text=f'+{rad_val}' if rad_val > 0 else str(rad_val))

            if after_debounce_id[0]:
                retouch_win.after_cancel(after_debounce_id[0])
            after_debounce_id[0] = retouch_win.after(25, process_retouch_pipeline)

        def create_slider_row(parent, title_km, var, min_v, max_v, key, color='#EC4899', btn_color='#F472B6'):
            box = ctk.CTkFrame(parent, fg_color='#111827', corner_radius=8, border_width=1, border_color='#1E293B')
            box.pack(fill='x', pady=5, padx=6)

            top_r = ctk.CTkFrame(box, fg_color='transparent')
            top_r.pack(fill='x', padx=10, pady=(6, 2))
            ctk.CTkLabel(top_r, text=title_km, font=('Khmer OS Siemreap', 11, 'bold'), text_color='#E2E8F0').pack(side='left')
            v_lbl = ctk.CTkLabel(top_r, text=f'{int(var.get())}%', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color=color)
            v_lbl.pack(side='right')
            val_labels[key] = v_lbl

            sl = ctk.CTkSlider(
                box, from_=min_v, to=max_v, variable=var, command=on_slider_moved,
                fg_color='#1E293B', progress_color=color, button_color=btn_color, button_hover_color=color, height=14
            )
            sl.pack(fill='x', padx=10, pady=(2, 8))
            return sl

        create_slider_row(scroll_controls, '💧 កម្រិតម៉ដ្ឋរលោង (Smooth Skin)', var_smooth, 0, 100, 'smooth', color='#EC4899', btn_color='#F472B6')
        create_slider_row(scroll_controls, '🧹 លុបមុន & ស្នាមអុច (Acne Removal)', var_blemish, 0, 100, 'blemish', color='#F59E0B', btn_color='#FBBF24')
        create_slider_row(scroll_controls, '🔬 រក្សាគ្រាប់ស្បែក (Skin Texture)', var_texture, 0, 100, 'texture', color='#10B981', btn_color='#34D399')
        create_slider_row(scroll_controls, '✨ ពន្លឺស្បែក (Skin Radiance)', var_radiance, -50, 50, 'radiance', color='#06B6D4', btn_color='#38BDF8')

        # Presets Card
        card_presets = ctk.CTkFrame(scroll_controls, fg_color='#111827', corner_radius=8, border_width=1, border_color='#1E293B')
        card_presets.pack(fill='x', pady=(8, 6), padx=6)
        ctk.CTkLabel(card_presets, text='🎨 ម៉ូតស្ទូឌីយោ Preset ពេញនិយម', font=('Khmer OS Siemreap', 11, 'bold'), text_color='#38BDF8').pack(pady=(6, 4))

        grid_p = ctk.CTkFrame(card_presets, fg_color='transparent')
        grid_p.pack(pady=4, padx=6)

        def apply_preset(sm, bl, tx, rd):
            var_smooth.set(sm)
            var_blemish.set(bl)
            var_texture.set(tx)
            var_radiance.set(rd)
            on_slider_moved()

        r1 = ctk.CTkFrame(grid_p, fg_color='transparent')
        r1.pack(fill='x', pady=2)
        ctk.CTkButton(r1, text='🌸 ធម្មជាតិ (Natural)', font=('Khmer OS Siemreap', 10), width=155, height=28, fg_color='#1E293B', hover_color='#334155', command=lambda: apply_preset(50, 60, 85, 5)).pack(side='left', padx=3)
        ctk.CTkButton(r1, text='👑 ស្ទូឌីយោ (Studio Pro)', font=('Khmer OS Siemreap', 10), width=155, height=28, fg_color='#1E293B', hover_color='#334155', command=lambda: apply_preset(70, 75, 80, 12)).pack(side='left', padx=3)

        r2 = ctk.CTkFrame(grid_p, fg_color='transparent')
        r2.pack(fill='x', pady=(2, 6))
        ctk.CTkButton(r2, text='✨ ម៉ដ្ឋខៃ (Glamour)', font=('Khmer OS Siemreap', 10), width=155, height=28, fg_color='#1E293B', hover_color='#334155', command=lambda: apply_preset(88, 90, 70, 18)).pack(side='left', padx=3)
        ctk.CTkButton(r2, text='🔄 កំណត់ដើម (Reset)', font=('Khmer OS Siemreap', 10), width=155, height=28, fg_color='#1E293B', hover_color='#334155', command=lambda: apply_preset(0, 0, 100, 0)).pack(side='left', padx=3)

        # Bottom controls in Left Panel (Before/After & Apply/Cancel)
        bot_ctrl = ctk.CTkFrame(left_frame, fg_color='transparent')
        bot_ctrl.pack(fill='x', side='bottom', padx=10, pady=(6, 12))

        def set_comparing(state):
            is_comparing_before[0] = state
            if state:
                lbl_status_badge.configure(text='📷 រូបដើម (BEFORE)', fg_color='#881337', text_color='#FB7185')
            else:
                lbl_status_badge.configure(text='✨ កែរួច (AFTER)', fg_color='#064E3B', text_color='#34D399')
            render_canvas()

        btn_compare = ctk.CTkButton(
            bot_ctrl, text='👁️ ចុចសង្កត់ដើម្បីមើលរូបដើម (Hold Before)',
            font=('Khmer OS Siemreap', 11, 'bold'),
            fg_color='#1E293B', hover_color='#334155', text_color='#E2E8F0', height=36, corner_radius=8
        )
        btn_compare.pack(fill='x', pady=(0, 8))
        btn_compare.bind('<ButtonPress-1>', lambda e: set_comparing(True))
        btn_compare.bind('<ButtonRelease-1>', lambda e: set_comparing(False))

        row_act = ctk.CTkFrame(bot_ctrl, fg_color='transparent')
        row_act.pack(fill='x')

        def close_studio():
            try:
                retouch_win.destroy()
            except Exception:
                pass
            self.force_foreground()
            self.after(50, self.force_foreground)

        def apply_studio_changes():
            sm = var_smooth.get() / 100.0
            bl = var_blemish.get() / 100.0
            tx = var_texture.get() / 100.0
            rd = var_radiance.get()

            # If user reset (0, 0, 100, 0), close without reprocessing
            if sm < 0.01 and bl < 0.05 and abs(rd) < 1 and abs(tx - 1.0) < 0.05:
                close_studio()
                return

            self.save_state()

            if scale_p < 1.0:
                # Apply on FULL RESOLUTION image with a clean progress indicator
                loading_apply = ctk.CTkToplevel(retouch_win)
                loading_apply.title('កំពុងអនុវត្ត...')
                main_x, main_y = (retouch_win.winfo_x(), retouch_win.winfo_y())
                main_w, main_h = (retouch_win.winfo_width(), retouch_win.winfo_height())
                pos_x = main_x + main_w // 2 - 160
                pos_y = main_y + main_h // 2 - 60
                loading_apply.geometry(f'320x120+{pos_x}+{pos_y}')
                loading_apply.attributes('-topmost', True)
                loading_apply.grab_set()

                ctk.CTkLabel(loading_apply, text='✨ កំពុងរក្សាទុកគុណភាពខ្ពស់ 100%...\nសូមរង់ចាំបន្តិច 🙏', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#10B981').pack(pady=(16, 6))
                prog = ctk.CTkProgressBar(loading_apply, width=240, height=8, progress_color='#10B981', mode='indeterminate')
                prog.pack(pady=4)
                prog.start()
                loading_apply.update()

                def do_full_res():
                    try:
                        final_bgr, _ = self.process_natural_skin_retouch(
                            orig_bgr, smooth_val=sm, blemish_val=bl, texture_val=tx, radiance_val=rd
                        )
                        final_pil = Image.fromarray(cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB))
                        def on_done():
                            try:
                                self.processed_image = final_pil
                                if hasattr(self, 'base_makeup_img'):
                                    self.base_makeup_img = self.processed_image.copy()
                                self.update_canvas_display()
                                self.increment_action('retouch_studio')
                            finally:
                                try:
                                    loading_apply.grab_release()
                                    loading_apply.destroy()
                                except Exception:
                                    pass
                                close_studio()
                        self.after(0, on_done)
                    except Exception as e:
                        print('Apply full-res error:', e)
                        self.after(0, close_studio)

                threading.Thread(target=do_full_res, daemon=True).start()
            else:
                self.processed_image = display_pil.copy()
                if hasattr(self, 'base_makeup_img'):
                    self.base_makeup_img = self.processed_image.copy()
                self.update_canvas_display()
                self.increment_action('retouch_studio')
                close_studio()

        retouch_win.protocol("WM_DELETE_WINDOW", close_studio)
        ctk.CTkButton(row_act, text='បោះបង់ (Cancel)', font=('Khmer OS Siemreap', 12), width=130, height=38, fg_color='#334155', hover_color='#475569', command=close_studio).pack(side='left', padx=(0, 6))
        ctk.CTkButton(row_act, text='✅ យល់ព្រម (Apply)', font=('Khmer OS Siemreap', 12, 'bold'), height=38, fg_color='#059669', hover_color='#047857', command=apply_studio_changes).pack(side='left', fill='x', expand=True)

        center_frame.bind('<Configure>', lambda e: fit_canvas_image() if zoom_level[0] == 1.0 else render_canvas())

        # Initial fit and render
        retouch_win.update_idletasks()
        fit_canvas_image()
        process_retouch_pipeline()

    def open_symmetry_studio(self):
        if not self.ensure_license_active("Symmetry Studio"):
            return
        if not getattr(self, 'processed_image', None):
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')

        main_x, main_y = (self.winfo_x(), self.winfo_y())
        main_w, main_h = (self.winfo_width(), self.winfo_height())
        loading_win = ctk.CTkToplevel(self)
        loading_win.title('កំពុងស្កេនទម្រង់មុខ...')
        load_w, load_h = (360, 160)
        pos_x = main_x + main_w // 2 - load_w // 2
        pos_y = main_y + main_h // 2 - load_h // 2
        loading_win.geometry(f'{load_w}x{load_h}+{pos_x}+{pos_y}')
        loading_win.grab_set()
        loading_win.attributes('-topmost', True)
        loading_win.configure(fg_color='#0A0E17')

        ctk.CTkLabel(
            loading_win,
            text='🪞 កំពុងស្កេន និងវិភាគទម្រង់មុខ...\nសូមរង់ចាំបន្តិច (Face & Symmetry AI)',
            font=('Khmer OS Siemreap', 13, 'bold'),
            text_color='#00F2FE'
        ).pack(pady=(22, 10))

        prog = ctk.CTkProgressBar(loading_win, width=280, height=10, progress_color='#00F2FE', mode='indeterminate')
        prog.pack(pady=4)
        prog.start()
        loading_win.update()

        detect_res = {'error': None, 'faces': None, 'done': False}

        def detect_worker():
            try:
                import torch
                if getattr(self, 'face_det_model', None) is None:
                    from facexlib.detection import init_detection_model
                    model_root = os.path.join(_app_dir, 'gfpgan', 'weights')
                    if not os.path.exists(model_root):
                        model_root = resource_path('gfpgan/weights')
                    self.face_det_model = init_detection_model('retinaface_resnet50', half=False, device='cpu', model_rootpath=model_root)

                img_rgb = np.array(self.processed_image.convert('RGB'))
                img_bgr = img_rgb[:, :, ::-1].copy()

                with torch.no_grad():
                    faces = self.face_det_model.detect_faces(img_bgr)
                detect_res['faces'] = faces
                detect_res['done'] = True
            except Exception as e:
                detect_res['error'] = str(e)
                detect_res['done'] = True

        threading.Thread(target=detect_worker, daemon=True).start()

        def wait_detection():
            if not loading_win.winfo_exists():
                return
            if not detect_res['done']:
                self.after(50, wait_detection)
                return

            try:
                loading_win.grab_release()
                loading_win.destroy()
            except Exception:
                pass

            if detect_res['error']:
                return messagebox.showerror('បញ្ហា', f"មាន Error ពេលស្កេនមុខ: {detect_res['error']}")

            faces = detect_res['faces']
            if faces is None or len(faces) == 0:
                return messagebox.showwarning('បញ្ហា', 'រកមិនឃើញផ្ទៃមុខក្នុងរូបថតទេ សូមពិនិត្យមើលរូបថតឡើងវិញ!')

            best_face = None
            max_area = 0
            for f in faces:
                area = (f[2] - f[0]) * (f[3] - f[1])
                if area > max_area:
                    max_area = area
                    best_face = f

            if best_face is None:
                return messagebox.showwarning('បញ្ហា', 'រកមិនឃើញផ្ទៃមុខច្បាស់លាស់ទេ!')

            self._launch_symmetry_studio_ui(best_face)

        self.after(60, wait_detection)

    def _launch_symmetry_studio_ui(self, best_face):
        orig_pil = self.processed_image.copy()
        is_rgba = (orig_pil.mode == 'RGBA')
        orig_np = np.array(orig_pil)
        H_orig, W_orig = orig_np.shape[:2]
        orig_bgr = orig_np[:, :, :3][:, :, ::-1].copy()
        orig_alpha = orig_np[:, :, 3].copy() if is_rgba else None

        full_lms = [float(v) for v in best_face[5:15]]

        # Live preview downscale buffer (max 1000px for buttery smooth 10ms response)
        scale_p = min(1.0, 1000.0 / max(W_orig, H_orig))
        pw = max(10, int(W_orig * scale_p))
        ph = max(10, int(H_orig * scale_p))
        preview_bgr = cv2.resize(orig_bgr, (pw, ph), interpolation=cv2.INTER_AREA) if scale_p < 1.0 else orig_bgr.copy()
        preview_alpha = cv2.resize(orig_alpha, (pw, ph), interpolation=cv2.INTER_AREA) if (orig_alpha is not None and scale_p < 1.0) else (orig_alpha.copy() if orig_alpha is not None else None)
        p_lms = [v * scale_p for v in full_lms]

        def deform_face_symmetry(img_bgr, landmarks, params):
            H, W = img_bgr.shape[:2]
            lx, ly, rx, ry, nx, ny, lmx, lmy, rmx, rmy = [float(v) for v in landmarks]
            eye_dist = float(math.hypot(rx - lx, ry - ly))
            if eye_dist < 5.0:
                return img_bgr.copy(), None
            face_mid_x = float((lx + rx) / 2.0)
            face_mid_y = float((ly + ry) / 2.0)

            grid_y, grid_x = np.indices((H, W), dtype=np.float32)
            map_x = grid_x.copy()
            map_y = grid_y.copy()

            def shift_radial(cx, cy, radius, dx, dy):
                if dx == 0 and dy == 0:
                    return
                dist_sq = (grid_x - cx)**2 + (grid_y - cy)**2
                r_sq = radius * radius
                mask = dist_sq < r_sq
                if not np.any(mask):
                    return
                w = (1.0 - (dist_sq[mask] / r_sq)) ** 2
                map_x[mask] -= dx * w
                map_y[mask] -= dy * w

            def scale_radial(cx, cy, radius, scale):
                if scale == 0:
                    return
                dist_sq = (grid_x - cx)**2 + (grid_y - cy)**2
                r_sq = radius * radius
                mask = dist_sq < r_sq
                if not np.any(mask):
                    return
                w = (1.0 - (dist_sq[mask] / r_sq)) ** 2
                map_x[mask] -= (grid_x[mask] - cx) * scale * w
                map_y[mask] -= (grid_y[mask] - cy) * scale * w

            def shift_horiz_pinch(cx, cy, rx_rad, ry_rad, amount):
                if amount == 0:
                    return
                norm_sq = ((grid_x - cx) / rx_rad)**2 + ((grid_y - cy) / ry_rad)**2
                mask = norm_sq < 1.0
                if not np.any(mask):
                    return
                w = (1.0 - norm_sq[mask]) ** 2
                map_x[mask] -= (grid_x[mask] - cx) * amount * w

            eye_r = eye_dist * 0.44
            brow_r = eye_dist * 0.38
            nose_r = eye_dist * 0.48
            mouth_r = eye_dist * 0.50
            cheek_r = eye_dist * 0.65
            chin_r = eye_dist * 0.45
            ear_r = eye_dist * 0.45
            hair_r = eye_dist * 0.85

            # 1. Eyes
            e_l_y = params.get('eye_l_y', 0.0) / 100.0
            if e_l_y != 0:
                shift_radial(lx, ly, eye_r, 0, e_l_y * (eye_dist * 0.18))
            e_r_y = params.get('eye_r_y', 0.0) / 100.0
            if e_r_y != 0:
                shift_radial(rx, ry, eye_r, 0, e_r_y * (eye_dist * 0.18))
            e_l_s = params.get('eye_l_scale', 0.0) / 100.0
            if e_l_s != 0:
                scale_radial(lx, ly, eye_r, e_l_s * 0.28)
            e_r_s = params.get('eye_r_scale', 0.0) / 100.0
            if e_r_s != 0:
                scale_radial(rx, ry, eye_r, e_r_s * 0.28)
            e_d = params.get('eye_dist', 0.0) / 100.0
            if e_d != 0:
                d = e_d * (eye_dist * 0.12)
                shift_radial(lx, ly, eye_r, -d, 0)
                shift_radial(rx, ry, eye_r, d, 0)

            # 2. Eyebrows
            brow_l_y = ly - eye_dist * 0.35
            brow_r_y = ry - eye_dist * 0.35
            b_l_y = params.get('brow_l_y', 0.0) / 100.0
            if b_l_y != 0:
                shift_radial(lx, brow_l_y, brow_r, 0, b_l_y * (eye_dist * 0.18))
            b_r_y = params.get('brow_r_y', 0.0) / 100.0
            if b_r_y != 0:
                shift_radial(rx, brow_r_y, brow_r, 0, b_r_y * (eye_dist * 0.18))

            # 3. Nose
            n_x = params.get('nose_x', 0.0) / 100.0
            if n_x != 0:
                shift_radial(nx, ny, nose_r, n_x * (eye_dist * 0.18), 0)
            n_w = params.get('nose_w', 0.0) / 100.0
            if n_w != 0:
                shift_horiz_pinch(nx, ny, eye_dist * 0.35, eye_dist * 0.28, n_w * 0.30)

            # 4. Mouth
            mc_x = (lmx + rmx) / 2.0
            mc_y = (lmy + rmy) / 2.0
            m_x = params.get('mouth_x', 0.0) / 100.0
            if m_x != 0:
                shift_radial(mc_x, mc_y, mouth_r, m_x * (eye_dist * 0.18), 0)
            m_y = params.get('mouth_y', 0.0) / 100.0
            if m_y != 0:
                shift_radial(mc_x, mc_y, mouth_r, 0, m_y * (eye_dist * 0.18))
            m_w = params.get('mouth_w', 0.0) / 100.0
            if m_w != 0:
                shift_horiz_pinch(mc_x, mc_y, eye_dist * 0.52, eye_dist * 0.28, m_w * 0.30)
            sm = params.get('smile', 0.0) / 100.0
            if sm != 0:
                lift = sm * (eye_dist * 0.12)
                shift_radial(lmx, lmy, eye_dist * 0.28, 0, -lift)
                shift_radial(rmx, rmy, eye_dist * 0.28, 0, -lift)

            # 5. Ears
            ear_l_x = lx - eye_dist * 0.95
            ear_r_x = rx + eye_dist * 0.95
            ear_y = (ly + ny) / 2.0
            e_l_x = params.get('ear_l_x', 0.0) / 100.0
            if e_l_x != 0:
                shift_radial(ear_l_x, ear_y, ear_r, e_l_x * (eye_dist * 0.22), 0)
            e_r_x = params.get('ear_r_x', 0.0) / 100.0
            if e_r_x != 0:
                shift_radial(ear_r_x, ear_y, ear_r, e_r_x * (eye_dist * 0.22), 0)

            # 6. Jawline / Face Slim
            cheek_l_x = lx - eye_dist * 0.65
            cheek_r_x = rx + eye_dist * 0.65
            cheek_y = ny + eye_dist * 0.15
            f_s = params.get('face_slim', 0.0) / 100.0
            if f_s != 0:
                slim = f_s * (eye_dist * 0.18)
                shift_radial(cheek_l_x, cheek_y, cheek_r, slim, 0)
                shift_radial(cheek_r_x, cheek_y, cheek_r, -slim, 0)

            # 7. Chin
            chin_x = mc_x
            chin_y = mc_y + eye_dist * 0.55
            ch_y = params.get('chin_y', 0.0) / 100.0
            if ch_y != 0:
                shift_radial(chin_x, chin_y, chin_r, 0, ch_y * (eye_dist * 0.18))

            # 8. Hair Volume
            hair_top_x = face_mid_x
            hair_top_y = ly - eye_dist * 0.75
            h_v = params.get('hair_vol', 0.0) / 100.0
            if h_v != 0:
                scale_radial(hair_top_x, hair_top_y, hair_r, h_v * 0.25)

            res = cv2.remap(img_bgr, map_x, map_y, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return res, (map_x, map_y)

        # Build initial display image
        if preview_alpha is not None:
            init_rgba = np.dstack((cv2.cvtColor(preview_bgr, cv2.COLOR_BGR2RGB), preview_alpha))
            preview_base_pil = Image.fromarray(init_rgba)
        else:
            preview_base_pil = Image.fromarray(cv2.cvtColor(preview_bgr, cv2.COLOR_BGR2RGB))
        display_pil = [preview_base_pil.copy()]

        # Create Studio Window
        sym_win = ctk.CTkToplevel(self)
        sym_win.title('🪞 Face & Symmetry Studio (កែទម្រង់មុខ & សរីរាង្គមិនស្មើគ្នា)')
        sym_win.configure(fg_color='#07090E')
        sym_win.transient(self)
        sym_win.attributes('-topmost', True)

        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            sym_win.iconbitmap(ico_path)
        except Exception:
            pass

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w_win = min(1320, sw - 30)
        h_win = min(820, sh - 50)
        pos_x = max(10, int(sw / 2 - w_win / 2))
        pos_y = max(10, int(sh / 2 - h_win / 2))
        sym_win.geometry(f'{w_win}x{h_win}+{pos_x}+{pos_y}')
        sym_win.grab_set()

        # Canvas & Interactive State
        zoom_level = [1.0]
        canvas_img_x = [450]
        canvas_img_y = [320]
        pan_last_pos = [0, 0]
        is_holding_before = [False]
        show_guides = [True]
        warp_after_id = [None]

        param_keys = [
            'eye_l_y', 'eye_r_y', 'eye_l_scale', 'eye_r_scale', 'eye_dist',
            'brow_l_y', 'brow_r_y',
            'nose_x', 'nose_w',
            'mouth_x', 'mouth_y', 'mouth_w', 'smile',
            'ear_l_x', 'ear_r_x',
            'face_slim', 'chin_y', 'hair_vol'
        ]
        current_params = {k: 0.0 for k in param_keys}
        slider_widgets = {}
        value_labels = {}

        # UI Layout: Left Control Panel + Center Canvas
        left_frame = ctk.CTkFrame(sym_win, width=390, fg_color='#0F172A', corner_radius=12, border_width=1, border_color='#1E293B')
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)

        center_frame = ctk.CTkFrame(sym_win, fg_color='#080B12', corner_radius=12, border_width=1, border_color='#1E293B')
        center_frame.pack(side='left', fill='both', expand=True, padx=5, pady=10)

        # Header Box in Left Panel
        header_box = ctk.CTkFrame(left_frame, fg_color='transparent')
        header_box.pack(fill='x', padx=12, pady=(10, 4))
        ctk.CTkLabel(
            header_box, text='🪞 Face & Symmetry Studio',
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color='#00F2FE'
        ).pack(anchor='w')
        ctk.CTkLabel(
            header_box, text='កែសម្រួលតុល្យភាព ភ្នែក ច្រមុះ មាត់ ត្រចៀក សក់ ឲ្យស្មើគ្នាម៉ត់',
            font=('Khmer OS Siemreap', 10),
            text_color='#94A3B8'
        ).pack(anchor='w', pady=(0, 4))

        # Quick Actions Row
        quick_row = ctk.CTkFrame(left_frame, fg_color='transparent')
        quick_row.pack(fill='x', padx=10, pady=(2, 6))
        quick_row.grid_columnconfigure(0, weight=2)
        quick_row.grid_columnconfigure(1, weight=1)

        btn_auto_sym = ctk.CTkButton(
            quick_row, text='🎯 1-Click Auto Symmetry',
            font=('Khmer OS Siemreap', 11, 'bold'),
            height=34, corner_radius=8,
            fg_color='#1E1238', hover_color='#2D1B54',
            border_width=1.5, border_color='#A855F7',
            text_color='#E9D5FF',
            command=lambda: apply_auto_symmetry()
        )
        btn_auto_sym.grid(row=0, column=0, padx=(0, 4), sticky='ew')

        btn_reset_all = ctk.CTkButton(
            quick_row, text='🔄 Reset',
            font=('Khmer OS Siemreap', 11, 'bold'),
            height=34, corner_radius=8,
            fg_color='#1E293B', hover_color='#334155',
            border_width=1, border_color='#475569',
            text_color='#F1F5F9',
            command=lambda: reset_all_sliders()
        )
        btn_reset_all.grid(row=0, column=1, padx=(4, 0), sticky='ew')

        # Scrollable Frame for Sliders
        scroll_ctrl = ctk.CTkScrollableFrame(left_frame, fg_color='transparent')
        scroll_ctrl.pack(fill='both', expand=True, padx=4, pady=4)

        def make_section_card(parent, title, accent_color='#38BDF8'):
            card = ctk.CTkFrame(parent, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
            card.pack(fill='x', padx=4, pady=4)
            head = ctk.CTkFrame(card, fg_color='transparent')
            head.pack(fill='x', padx=8, pady=(6, 3))
            ctk.CTkLabel(head, text='●', font=('Arial', 9), text_color=accent_color).pack(side='left', padx=(0, 4))
            ctk.CTkLabel(head, text=title, font=ctk.CTkFont(family='Khmer OS Battambang', size=11, weight='bold'), text_color='#F1F5F9').pack(side='left')
            return card

        def make_slider_row(parent, key, label_khmer, min_val=-100, max_val=100, default_val=0):
            row = ctk.CTkFrame(parent, fg_color='transparent')
            row.pack(fill='x', padx=8, pady=1)

            top_line = ctk.CTkFrame(row, fg_color='transparent')
            top_line.pack(fill='x', pady=(2, 0))
            ctk.CTkLabel(top_line, text=label_khmer, font=('Khmer OS Siemreap', 10), text_color='#CBD5E1').pack(side='left')
            lbl_val = ctk.CTkLabel(top_line, text='0', font=('Segoe UI', 10, 'bold'), text_color='#00F2FE')
            lbl_val.pack(side='right')
            value_labels[key] = lbl_val

            sl = ctk.CTkSlider(
                row, from_=min_val, to=max_val, number_of_steps=int(max_val - min_val),
                height=12, progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#7DD3FC',
                command=lambda v: on_slider_change(key, v)
            )
            sl.set(default_val)
            sl.pack(fill='x', pady=(1, 4))
            slider_widgets[key] = sl

        # Card 1: Eyes & Eyebrows
        c_eyes = make_section_card(scroll_ctrl, '👁️  ភ្នែក & ចិញ្ចើម (Eyes & Eyebrows)', '#38BDF8')
        make_slider_row(c_eyes, 'eye_l_y', 'ភ្នែកឆ្វេង ខ្ពស់-ទាប (Left Eye Height):')
        make_slider_row(c_eyes, 'eye_r_y', 'ភ្នែកស្តាំ ខ្ពស់-ទាប (Right Eye Height):')
        make_slider_row(c_eyes, 'eye_l_scale', 'ទំហំភ្នែកឆ្វេង (Left Eye Size):')
        make_slider_row(c_eyes, 'eye_r_scale', 'ទំហំភ្នែកស្តាំ (Right Eye Size):')
        make_slider_row(c_eyes, 'eye_dist', 'ចម្ងាយចន្លោះភ្នែក (Eye Distance):')
        make_slider_row(c_eyes, 'brow_l_y', 'ចិញ្ចើមឆ្វេង ខ្ពស់-ទាប (Left Brow Height):')
        make_slider_row(c_eyes, 'brow_r_y', 'ចិញ្ចើមស្តាំ ខ្ពស់-ទាប (Right Brow Height):')

        # Card 2: Nose
        c_nose = make_section_card(scroll_ctrl, '👃  ច្រមុះ (Nose)', '#F59E0B')
        make_slider_row(c_nose, 'nose_x', 'រំកិលច្រមុះ ឆ្វេង-ស្តាំ (Nose Shift X):')
        make_slider_row(c_nose, 'nose_w', 'ទទឹងស្លាបច្រមុះ (Nose Width):')

        # Card 3: Mouth & Smile
        c_mouth = make_section_card(scroll_ctrl, '👄  មាត់ & ស្នាមញញឹម (Mouth & Smile)', '#EC4899')
        make_slider_row(c_mouth, 'mouth_x', 'រំកិលមាត់ ឆ្វេង-ស្តាំ (Mouth Shift X):')
        make_slider_row(c_mouth, 'mouth_y', 'កម្ពស់មាត់ លើ-ក្រោម (Mouth Height Y):')
        make_slider_row(c_mouth, 'mouth_w', 'ទទឹងមាត់ (Mouth Width):')
        make_slider_row(c_mouth, 'smile', 'លើកជ្រុងមាត់ / ញញឹម (Smile Lift):')

        # Card 4: Ears
        c_ears = make_section_card(scroll_ctrl, '👂  ត្រចៀក (Ears)', '#10B981')
        make_slider_row(c_ears, 'ear_l_x', 'ត្រចៀកឆ្វេង រុញចូល/ចេញ (Left Ear In/Out):')
        make_slider_row(c_ears, 'ear_r_x', 'ត្រចៀកស្តាំ រុញចូល/ចេញ (Right Ear In/Out):')

        # Card 5: Face & Hair
        c_face = make_section_card(scroll_ctrl, '👱  ទម្រង់មុខ & សក់ (Face & Hair)', '#A855F7')
        make_slider_row(c_face, 'face_slim', 'ស្រឡូនថ្គាម / ថ្ពាល់ (Slim Face):', min_val=0, max_val=100, default_val=0)
        make_slider_row(c_face, 'chin_y', 'ចង្កា វែង-ខ្លី (Chin Length):')
        make_slider_row(c_face, 'hair_vol', 'កម្រាស់សក់ (Hair Volume):')

        # Bottom Action Bar
        bot_ctrl = ctk.CTkFrame(left_frame, fg_color='#0B101D', corner_radius=10, border_width=1, border_color='#1E293B')
        bot_ctrl.pack(fill='x', padx=8, pady=(4, 8))

        row_act = ctk.CTkFrame(bot_ctrl, fg_color='transparent')
        row_act.pack(fill='x', padx=6, pady=6)

        def close_studio():
            try:
                sym_win.destroy()
            except Exception:
                pass
            self.force_foreground()
            self.after(50, self.force_foreground)

        def apply_studio_changes():
            is_modified = any(abs(v) > 0.1 for v in current_params.values())
            if not is_modified:
                close_studio()
                return

            self.save_state()

            if scale_p < 1.0:
                loading_apply = ctk.CTkToplevel(sym_win)
                loading_apply.title('កំពុងអនុវត្ត...')
                main_x, main_y = (sym_win.winfo_x(), sym_win.winfo_y())
                main_w, main_h = (sym_win.winfo_width(), sym_win.winfo_height())
                pos_x = main_x + main_w // 2 - 160
                pos_y = main_y + main_h // 2 - 60
                loading_apply.geometry(f'320x120+{pos_x}+{pos_y}')
                loading_apply.attributes('-topmost', True)
                loading_apply.grab_set()

                ctk.CTkLabel(loading_apply, text='🪞 កំពុងរក្សាទុកគុណភាពខ្ពស់ 100%...\nសូមរង់ចាំបន្តិច 🙏', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#00F2FE').pack(pady=(16, 6))
                prog = ctk.CTkProgressBar(loading_apply, width=240, height=8, progress_color='#00F2FE', mode='indeterminate')
                prog.pack(pady=4)
                prog.start()
                loading_apply.update()

                def do_full_res():
                    try:
                        final_bgr, maps = deform_face_symmetry(orig_bgr, full_lms, current_params)
                        if orig_alpha is not None and maps is not None:
                            map_x, map_y = maps
                            final_alpha = cv2.remap(orig_alpha, map_x, map_y, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                            final_pil = Image.fromarray(np.dstack((cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB), final_alpha)))
                        else:
                            final_pil = Image.fromarray(cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB))

                        def on_done():
                            try:
                                self.processed_image = final_pil
                                if hasattr(self, 'base_makeup_img'):
                                    self.base_makeup_img = self.processed_image.copy()
                                self.update_canvas_display()
                                self.increment_action('symmetry_studio')
                            finally:
                                try:
                                    loading_apply.grab_release()
                                    loading_apply.destroy()
                                except Exception:
                                    pass
                                close_studio()

                        self.after(0, on_done)
                    except Exception as e:
                        print('Apply full-res error:', e)
                        self.after(0, close_studio)

                threading.Thread(target=do_full_res, daemon=True).start()
            else:
                self.processed_image = display_pil[0].copy()
                if hasattr(self, 'base_makeup_img'):
                    self.base_makeup_img = self.processed_image.copy()
                self.update_canvas_display()
                self.increment_action('symmetry_studio')
                close_studio()

        sym_win.protocol("WM_DELETE_WINDOW", close_studio)
        ctk.CTkButton(row_act, text='បោះបង់ (Cancel)', font=('Khmer OS Siemreap', 12), width=120, height=38, fg_color='#334155', hover_color='#475569', command=close_studio).pack(side='left', padx=(0, 6))
        ctk.CTkButton(row_act, text='✅ យល់ព្រម (Apply)', font=('Khmer OS Siemreap', 12, 'bold'), height=38, fg_color='#059669', hover_color='#047857', command=apply_studio_changes).pack(side='left', fill='x', expand=True)

        # Center Top Bar
        top_bar = ctk.CTkFrame(center_frame, fg_color='#0B101D', height=40, corner_radius=8)
        top_bar.pack(fill='x', padx=8, pady=(8, 4))

        lbl_status_badge = ctk.CTkLabel(
            top_bar, text='✨ កែរួច (AFTER)',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            fg_color='#064E3B', text_color='#34D399', corner_radius=6, width=120, height=26
        )
        lbl_status_badge.pack(side='left', padx=(8, 4), pady=6)

        ctk.CTkLabel(
            top_bar, text=f'ទំហំ: {W_orig}×{H_orig}px',
            font=('Khmer OS Siemreap', 10), text_color='#94A3B8'
        ).pack(side='left', padx=6)

        # Before / After Hold Button
        btn_before = ctk.CTkButton(
            top_bar, text='👁️ សង្កត់មើលរូបដើម (Hold Before)',
            font=('Khmer OS Siemreap', 10, 'bold'),
            height=26, corner_radius=6,
            fg_color='#1E293B', hover_color='#334155', text_color='#E2E8F0'
        )
        btn_before.pack(side='left', padx=6)

        def on_hold_before_press(e):
            is_holding_before[0] = True
            lbl_status_badge.configure(text='⏮️ រូបដើម (BEFORE)', fg_color='#451A03', text_color='#FDE68A')
            render_canvas()

        def on_hold_before_release(e):
            is_holding_before[0] = False
            lbl_status_badge.configure(text='✨ កែរួច (AFTER)', fg_color='#064E3B', text_color='#34D399')
            render_canvas()

        btn_before.bind('<ButtonPress-1>', on_hold_before_press)
        btn_before.bind('<ButtonRelease-1>', on_hold_before_release)

        # Toggle Guide Lines
        btn_guide_toggle = ctk.CTkButton(
            top_bar, text='📏 បន្ទាត់ជំនួយ (Guides: ON)',
            font=('Khmer OS Siemreap', 10, 'bold'),
            height=26, corner_radius=6,
            fg_color='#14273E', hover_color='#1E3A5F', text_color='#38BDF8'
        )
        btn_guide_toggle.pack(side='left', padx=6)

        def toggle_guides():
            show_guides[0] = not show_guides[0]
            if show_guides[0]:
                btn_guide_toggle.configure(text='📏 បន្ទាត់ជំនួយ (Guides: ON)', fg_color='#14273E', text_color='#38BDF8')
            else:
                btn_guide_toggle.configure(text='📏 បន្ទាត់ជំនួយ (Guides: OFF)', fg_color='#1E293B', text_color='#94A3B8')
            render_canvas()

        btn_guide_toggle.configure(command=toggle_guides)

        # Zoom Controls
        frame_zoom = ctk.CTkFrame(top_bar, fg_color='transparent')
        frame_zoom.pack(side='right', padx=8, pady=4)

        lbl_zoom = ctk.CTkLabel(frame_zoom, text='100%', font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'), text_color='#00F2FE', width=52)

        def zoom_by_factor(factor, center_x=None, center_y=None):
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            if center_x is None:
                center_x = cw // 2
            if center_y is None:
                center_y = ch // 2

            new_zoom = max(0.1, min(8.0, zoom_level[0] * factor))
            if abs(new_zoom - zoom_level[0]) < 1e-4:
                return
            actual_factor = new_zoom / zoom_level[0]
            canvas_img_x[0] = int(center_x - (center_x - canvas_img_x[0]) * actual_factor)
            canvas_img_y[0] = int(center_y - (center_y - canvas_img_y[0]) * actual_factor)
            zoom_level[0] = new_zoom
            lbl_zoom.configure(text=f'{int(zoom_level[0] * 100)}%')
            render_canvas()

        def set_zoom_exact(val):
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            canvas_img_x[0] = cw // 2
            canvas_img_y[0] = ch // 2
            zoom_level[0] = val
            lbl_zoom.configure(text=f'{int(val * 100)}%')
            render_canvas()

        def fit_canvas_image():
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)
            zoom_level[0] = min(cw / pw, ch / ph) * 0.95
            canvas_img_x[0] = cw // 2
            canvas_img_y[0] = ch // 2
            lbl_zoom.configure(text=f'{int(zoom_level[0] * 100)}%')
            render_canvas()

        ctk.CTkButton(frame_zoom, text='➖', width=28, height=26, font=('Arial', 10), fg_color='#1E293B', hover_color='#334155', command=lambda: zoom_by_factor(0.85)).pack(side='left', padx=2)
        lbl_zoom.pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='➕', width=28, height=26, font=('Arial', 10), fg_color='#1E293B', hover_color='#334155', command=lambda: zoom_by_factor(1.15)).pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='100%', width=44, height=26, font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), fg_color='#1E293B', hover_color='#334155', command=lambda: set_zoom_exact(1.0)).pack(side='left', padx=2)
        ctk.CTkButton(frame_zoom, text='⛶ Fit', width=44, height=26, font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'), fg_color='#1E293B', hover_color='#334155', command=lambda: fit_canvas_image()).pack(side='left', padx=2)

        # Interactive Canvas
        canvas = tk.Canvas(center_frame, bg='#080B12', highlightthickness=0, cursor='hand2')
        canvas.pack(fill='both', expand=True, padx=6, pady=6)

        def render_canvas():
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            if cw <= 10 or ch <= 10:
                cw, ch = (750, 600)

            img_to_show = preview_base_pil if is_holding_before[0] else display_pil[0]
            img_w, img_h = img_to_show.size
            z = zoom_level[0]

            disp_w = max(1, int(img_w * z))
            disp_h = max(1, int(img_h * z))

            cx = canvas_img_x[0]
            cy = canvas_img_y[0]

            x1 = cx - disp_w // 2
            y1 = cy - disp_h // 2

            src_x1 = max(0, int((0 - x1) / z))
            src_y1 = max(0, int((0 - y1) / z))
            src_x2 = min(img_w, int((cw - x1) / z) + 1)
            src_y2 = min(img_h, int((ch - y1) / z) + 1)

            canvas.delete('all')
            if src_x2 > src_x1 and src_y2 > src_y1:
                crop_w = max(1, int((src_x2 - src_x1) * z))
                crop_h = max(1, int((src_y2 - src_y1) * z))
                part = img_to_show.crop((src_x1, src_y1, src_x2, src_y2)).resize((crop_w, crop_h), Image.Resampling.BILINEAR)
                tk_photo = ImageTk.PhotoImage(part)
                dst_x = int(x1 + src_x1 * z)
                dst_y = int(y1 + src_y1 * z)

                canvas.create_image(dst_x, dst_y, image=tk_photo, anchor='nw')
                canvas._photo_cache = tk_photo

                # Draw Guide Lines & Symmetry Landmarks if enabled
                if show_guides[0] and not is_holding_before[0]:
                    lx_scr = int(x1 + p_lms[0] * z)
                    ly_scr = int(y1 + p_lms[1] * z)
                    rx_scr = int(x1 + p_lms[2] * z)
                    ry_scr = int(y1 + p_lms[3] * z)
                    nx_scr = int(x1 + p_lms[4] * z)
                    ny_scr = int(y1 + p_lms[5] * z)
                    lmx_scr = int(x1 + p_lms[6] * z)
                    lmy_scr = int(y1 + p_lms[7] * z)
                    rmx_scr = int(x1 + p_lms[8] * z)
                    rmy_scr = int(y1 + p_lms[9] * z)

                    mid_x_scr = (lx_scr + rx_scr) // 2
                    mid_y_scr = (ly_scr + ry_scr) // 2

                    # Vertical Symmetry Axis (Cyan dashed line)
                    canvas.create_line(mid_x_scr, 0, mid_x_scr, ch, fill='#00F2FE', dash=(4, 4), width=1)

                    # Horizontal Eye Level Axis (Gold dashed line)
                    canvas.create_line(0, mid_y_scr, cw, mid_y_scr, fill='#F59E0B', dash=(4, 4), width=1)

                    # Feature Anchor Points
                    def draw_anchor(ax, ay, col='#00F2FE', r=4):
                        canvas.create_oval(ax - r, ay - r, ax + r, ay + r, outline=col, width=1.5)
                        canvas.create_oval(ax - 1, ay - 1, ax + 1, ay + 1, fill=col, outline=col)

                    draw_anchor(lx_scr, ly_scr, '#38BDF8', 5)
                    draw_anchor(rx_scr, ry_scr, '#38BDF8', 5)
                    draw_anchor(nx_scr, ny_scr, '#F59E0B', 4)
                    draw_anchor(lmx_scr, lmy_scr, '#EC4899', 4)
                    draw_anchor(rmx_scr, rmy_scr, '#EC4899', 4)

        # Mouse Pan & Zoom
        def on_mouse_wheel(e):
            factor = 1.15 if e.delta > 0 else 0.85
            zoom_by_factor(factor, e.x, e.y)

        canvas.bind('<MouseWheel>', on_mouse_wheel)
        canvas.bind('<Button-4>', lambda e: zoom_by_factor(1.15, e.x, e.y))
        canvas.bind('<Button-5>', lambda e: zoom_by_factor(0.85, e.x, e.y))

        def on_pan_press(e):
            pan_last_pos[0] = e.x
            pan_last_pos[1] = e.y
            canvas.configure(cursor='fleur')

        def on_pan_drag(e):
            dx = e.x - pan_last_pos[0]
            dy = e.y - pan_last_pos[1]
            pan_last_pos[0] = e.x
            pan_last_pos[1] = e.y
            canvas_img_x[0] += dx
            canvas_img_y[0] += dy
            render_canvas()

        def on_pan_release(e):
            canvas.configure(cursor='hand2')

        canvas.bind('<ButtonPress-1>', on_pan_press)
        canvas.bind('<B1-Motion>', on_pan_drag)
        canvas.bind('<ButtonRelease-1>', on_pan_release)
        canvas.bind('<ButtonPress-2>', on_pan_press)
        canvas.bind('<B2-Motion>', on_pan_drag)
        canvas.bind('<ButtonRelease-2>', on_pan_release)

        # Live Slider and Warp Event Handlers
        def execute_warp():
            is_modified = any(abs(v) > 0.1 for v in current_params.values())
            if not is_modified:
                display_pil[0] = preview_base_pil.copy()
                render_canvas()
                return

            warped_bgr, maps = deform_face_symmetry(preview_bgr, p_lms, current_params)
            if preview_alpha is not None and maps is not None:
                map_x, map_y = maps
                warped_alpha = cv2.remap(preview_alpha, map_x, map_y, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                display_pil[0] = Image.fromarray(np.dstack((cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2RGB), warped_alpha)))
            else:
                display_pil[0] = Image.fromarray(cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2RGB))
            render_canvas()

        def schedule_warp():
            if warp_after_id[0] is not None:
                try:
                    sym_win.after_cancel(warp_after_id[0])
                except Exception:
                    pass
            warp_after_id[0] = sym_win.after(20, execute_warp)

        def on_slider_change(key, val):
            val_int = int(round(float(val)))
            current_params[key] = float(val_int)
            if key in value_labels:
                value_labels[key].configure(text=f'{val_int:+d}' if val_int != 0 else '0')
            schedule_warp()

        def apply_auto_symmetry():
            lx, ly, rx, ry, nx, ny, lmx, lmy, rmx, rmy = p_lms
            mid_eye_y = (ly + ry) / 2.0
            eye_dist = math.hypot(rx - lx, ry - ly)
            face_mid_x = (lx + rx) / 2.0
            mouth_mid_x = (lmx + rmx) / 2.0
            mouth_tilt = lmy - rmy

            auto_eye_l = int(np.clip((mid_eye_y - ly) / (eye_dist * 0.18) * 100.0, -100, 100))
            auto_eye_r = int(np.clip((mid_eye_y - ry) / (eye_dist * 0.18) * 100.0, -100, 100))
            auto_nose = int(np.clip((face_mid_x - nx) / (eye_dist * 0.18) * 100.0, -100, 100))
            auto_mouth = int(np.clip((face_mid_x - mouth_mid_x) / (eye_dist * 0.18) * 100.0, -100, 100))
            auto_smile = int(np.clip(-abs(mouth_tilt) / (eye_dist * 0.12) * 25.0, -40, 40))

            targets = {
                'eye_l_y': auto_eye_l,
                'eye_r_y': auto_eye_r,
                'brow_l_y': auto_eye_l,
                'brow_r_y': auto_eye_r,
                'nose_x': auto_nose,
                'mouth_x': auto_mouth,
                'smile': auto_smile,
                'face_slim': 15
            }
            for k, tgt in targets.items():
                if k in slider_widgets:
                    slider_widgets[k].set(tgt)
                current_params[k] = float(tgt)
                if k in value_labels:
                    value_labels[k].configure(text=f'{tgt:+d}' if tgt != 0 else '0')

            execute_warp()

        def reset_all_sliders():
            for k in param_keys:
                if k in slider_widgets:
                    slider_widgets[k].set(0)
                current_params[k] = 0.0
                if k in value_labels:
                    value_labels[k].configure(text='0')
            execute_warp()

        center_frame.bind('<Configure>', lambda e: fit_canvas_image() if zoom_level[0] == 1.0 else render_canvas())

        sym_win.update_idletasks()
        fit_canvas_image()

    def open_template_crop(self, size_type):
        if not self.processed_image:
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        else:
            crop_win = ctk.CTkToplevel(self)
            title_str = 'Crop 3x4 (2.7x3.7cm)' if size_type == '3x4' else 'Crop 4x6 (3.5x4.5cm)'
            crop_win.title(title_str + ' - ទម្រង់ស្តង់ដារថតកាត (Fix Size)')
            crop_win.transient(self)
            crop_win.attributes('-topmost', True)
            crop_win.configure(fg_color='#0A0E17')
            w_win, h_win = (960, 810)
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            crop_win.geometry(f'{w_win}x{h_win}+{int(sw / 2 - w_win / 2)}+{int(sh / 2 - h_win / 2)}')
            crop_win.grab_set()
            w_cm = 2.7 if size_type == '3x4' else 3.5
            h_cm = 3.7 if size_type == '3x4' else 4.5
            tr = w_cm / h_cm
            ctrl_frame = ctk.CTkFrame(crop_win, fg_color='#111622', corner_radius=12, border_width=1, border_color='#1E293B')
            ctrl_frame.pack(pady=10, padx=20, fill='x')
            ctk.CTkLabel(ctrl_frame, text=f'ទំហំកាត់ស្តង់ដារ: {w_cm}cm x {h_cm}cm (ជាប់សោរ)', font=self.font_bold, text_color='#38BDF8').pack(side='left', padx=15, pady=8)
            ctk.CTkLabel(ctrl_frame, text='|  បង្វិល (Rotate):', font=self.font_text, text_color='#F59E0B').pack(side='left', padx=(10, 5), pady=8)
            sl_rotate = ctk.CTkSlider(ctrl_frame, from_=(-45), to=45, width=150, fg_color='#182234', progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#00F2FE')
            sl_rotate.set(0)
            sl_rotate.pack(side='left', padx=5, pady=8)
            canvas_frame = tk.Frame(crop_win, bg='#080B12')
            canvas_frame.pack(expand=True, fill='both', padx=20, pady=10)
            canvas = tk.Canvas(canvas_frame, bg='#080B12', cursor='crosshair', highlightthickness=0)
            canvas.pack(expand=True, fill='both')
            state = {'rects': [], 'mode': None, 'last_x': 0, 'last_y': 0, 'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0, 'disp_w': 0, 'disp_h': 0, 'scale': 1.0, 'rotated_img': None}
            def update_image(event=None):
                angle = sl_rotate.get()
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None:
                    try:
                        s_matched = self.suit_overlay_image.resize(self.processed_image.size, Image.Resampling.BILINEAR)
                        show_base = Image.alpha_composite(self.processed_image.convert('RGBA'), s_matched).convert('RGB')
                    except Exception:
                        show_base = self.processed_image.convert('RGB')
                else:
                    show_base = self.processed_image.convert('RGB')
                rotated = show_base.rotate(-angle, resample=Image.Resampling.BILINEAR, expand=True, fillcolor=(255, 255, 255))
                canvas.update_idletasks()
                cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                if cw <= 1 or ch <= 1:
                    cw, ch = (800, 600)
                w_img, h_img = rotated.size
                scale = min((cw - 100) / w_img, (ch - 40) / h_img)
                disp_w, disp_h = (int(w_img * scale), int(h_img * scale))
                state['img_tk'] = ImageTk.PhotoImage(rotated.resize((disp_w, disp_h), Image.Resampling.BILINEAR))
                state['scale'] = scale
                state['disp_w'] = disp_w
                state['disp_h'] = disp_h
                state['rotated_img'] = rotated
                canvas.delete('img')
                canvas.create_image((cw - 100) // 2, ch // 2, image=state['img_tk'], anchor='center', tags='img')
                box_h = disp_h * 0.8
                box_w = box_h * tr
                if box_w > disp_w * 0.8:
                    box_w = disp_w * 0.8
                    box_h = box_w / tr
                cx, cy = ((cw - 100) // 2, ch // 2)
                if state['x1'] == 0 and state['y1'] == 0:
                        state['x1'] = cx - box_w / 2
                        state['y1'] = cy - box_h / 2
                        state['x2'] = cx + box_w / 2
                        state['y2'] = cy + box_h / 2
                draw_guides()
            _crop_rotate_after = [None]
            def on_crop_slider(val=None):
                if _crop_rotate_after[0] is not None:
                    try:
                        crop_win.after_cancel(_crop_rotate_after[0])
                    except Exception:
                        pass
                _crop_rotate_after[0] = crop_win.after(20, update_image)
            sl_rotate.configure(command=on_crop_slider)
            crop_win.after(200, update_image)
            def draw_guides():
                for item in state['rects']:
                    canvas.delete(item)
                state['rects'].clear()
                x1, y1, x2, y2 = (state['x1'], state['y1'], state['x2'], state['y2'])
                w, h = (x2 - x1, y2 - y1)
                rect = canvas.create_rectangle(x1, y1, x2, y2, outline='black', width=4, tags='guide')
                cx = x1 + w / 2
                vl = canvas.create_line(cx, y1, cx, y2, fill='red', dash=(10, 5), width=3, tags='guide')
                top_margin_y = y1 + h * 0.08
                hl1 = canvas.create_line(x1, top_margin_y, x2, top_margin_y, fill='red', dash=(10, 5), width=3, tags='guide')
                chin_y = y1 + h * 0.55
                hl2 = canvas.create_line(x1, chin_y, x2, chin_y, fill='red', dash=(10, 5), width=3, tags='guide')
                state['rects'].extend([rect, vl, hl1, hl2])
                text_x = x2 + 15
                kh_font = ('Khmer OS Battambang', 12, 'bold')
                t1 = canvas.create_text(text_x, y1 + (top_margin_y - y1) / 2, text='គម្លាតសក់', fill='white', font=kh_font, anchor='w')
                l1 = canvas.create_line(text_x - 10, y1, text_x - 10, top_margin_y, fill='white', dash=(6, 4), width=2)
                t2 = canvas.create_text(text_x, top_margin_y + (chin_y - top_margin_y) / 2, text='ទំហំមុខ', fill='white', font=kh_font, anchor='w')
                l2 = canvas.create_line(text_x - 10, top_margin_y, text_x - 10, chin_y, fill='white', dash=(6, 4), width=2)
                t3 = canvas.create_text(text_x, chin_y + (y2 - chin_y) / 2, text='ដងខ្លួន', fill='white', font=kh_font, anchor='w')
                l3 = canvas.create_line(text_x - 10, chin_y, text_x - 10, y2, fill='white', dash=(6, 4), width=2)
                state['rects'].extend([t1, t2, t3, l1, l2, l3])
            def get_mode(x_pos, y_pos):
                tol = 20
                if abs(x_pos - state['x1']) < tol and abs(y_pos - state['y1']) < tol:
                        return 'TL'
                if abs(x_pos - state['x2']) < tol and abs(y_pos - state['y2']) < tol:
                        return 'BR'
                if abs(x_pos - state['x2']) < tol and abs(y_pos - state['y1']) < tol:
                        return 'TR'
                if abs(x_pos - state['x1']) < tol and abs(y_pos - state['y2']) < tol:
                        return 'BL'
                if state['x1'] < x_pos < state['x2'] and state['y1'] < y_pos < state['y2']:
                                return 'MOVE'
                return None
            def update_cursor(event):
                mode = get_mode(event.x, event.y)
                if mode in ['TL', 'BR']:
                    canvas.config(cursor='size_nw_se')
                else:
                    if mode in ['TR', 'BL']:
                        canvas.config(cursor='size_ne_sw')
                    else:
                        if mode == 'MOVE':
                            canvas.config(cursor='fleur')
                        else:
                            canvas.config(cursor='crosshair')
            canvas.bind('<Motion>', update_cursor)
            def on_press(event):
                state['mode'] = get_mode(event.x, event.y)
                state['last_x'], state['last_y'] = (event.x, event.y)
            def on_drag(event):
                if not state['mode']:
                    return
                else:
                    dx, dy = (event.x - state['last_x'], event.y - state['last_y'])
                    cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                    lim_x1 = (cw - 100 - state['disp_w']) / 2
                    lim_y1 = (ch - state['disp_h']) / 2
                    lim_x2 = lim_x1 + state['disp_w']
                    lim_y2 = lim_y1 + state['disp_h']
                    if state['mode'] == 'MOVE':
                        if state['x1'] + dx >= lim_x1 and state['x2'] + dx <= lim_x2 and (state['y1'] + dy >= lim_y1) and (state['y2'] + dy <= lim_y2):
                                        state['x1'] += dx
                                        state['x2'] += dx
                                        state['y1'] += dy
                                        state['y2'] += dy
                                        state['last_x'], state['last_y'] = (event.x, event.y)
                    else:
                        fx, fy = (state['x1'], state['y1'])
                        nw = state['x2'] - state['x1']
                        if state['mode'] == 'BR':
                            fx, fy, nw = (state['x1'], state['y1'], event.x - state['x1'])
                        else:
                            if state['mode'] == 'TL':
                                fx, fy, nw = (state['x2'], state['y2'], state['x2'] - event.x)
                            else:
                                if state['mode'] == 'TR':
                                    fx, fy, nw = (state['x1'], state['y2'], event.x - state['x1'])
                                else:
                                    if state['mode'] == 'BL':
                                        fx, fy, nw = (state['x2'], state['y1'], state['x2'] - event.x)
                        if nw < 100:
                            nw = 100
                        nh = nw / tr
                        if fx + nw > lim_x2 and state['mode'] in ['TR', 'BR']:
                                nw = lim_x2 - fx
                                nh = nw / tr
                        if fx - nw < lim_x1 and state['mode'] in ['TL', 'BL']:
                                nw = fx - lim_x1
                                nh = nw / tr
                        if fy + nh > lim_y2 and state['mode'] in ['BL', 'BR']:
                                nh = lim_y2 - fy
                                nw = nh * tr
                        if fy - nh < lim_y1 and state['mode'] in ['TL', 'TR']:
                                nh = fy - lim_y1
                                nw = nh * tr
                        if state['mode'] == 'BR':
                            state['x2'] = fx + nw
                            state['y2'] = fy + nh
                        else:
                            if state['mode'] == 'TL':
                                state['x1'] = fx - nw
                                state['y1'] = fy - nh
                            else:
                                if state['mode'] == 'TR':
                                    state['x2'] = fx + nw
                                    state['y1'] = fy - nh
                                else:
                                    if state['mode'] == 'BL':
                                        state['x1'] = fx - nw
                                        state['y2'] = fy + nh
                        state['last_x'], state['last_y'] = (event.x, event.y)
                    draw_guides()
            canvas.bind('<ButtonPress-1>', on_press)
            canvas.bind('<B1-Motion>', on_drag)
            def apply_crop():
                self.save_state()
                cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                img_x_start = (cw - 100 - state['disp_w']) / 2
                img_y_start = (ch - state['disp_h']) / 2
                left = (state['x1'] - img_x_start) / state['scale']
                top = (state['y1'] - img_y_start) / state['scale']
                right = (state['x2'] - img_x_start) / state['scale']
                bottom = (state['y2'] - img_y_start) / state['scale']
                crop_box = (int(min(left, right)), int(min(top, bottom)), int(max(left, right)), int(max(top, bottom)))
                self.output_dpi = (1200, 1200)
                req_w = int(w_cm / 2.54 * 1200)
                req_h = int(h_cm / 2.54 * 1200)
                angle = sl_rotate.get()
                rotated_human = self.processed_image.rotate(-angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
                self.processed_image = rotated_human.crop(crop_box).resize((req_w, req_h), Image.Resampling.LANCZOS)
                self.invalidate_bg_cache()
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None:
                    rotated_suit = self.suit_overlay_image.rotate(-angle, resample=Image.BICUBIC, expand=True)
                    self.suit_overlay_image = rotated_suit.crop(crop_box).resize((req_w, req_h), Image.Resampling.LANCZOS)
                self.increment_action('crop_3x4' if size_type == '3x4' else 'crop_4x6')
                self.fit_image()
                crop_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            def on_crop_close():
                crop_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            crop_win.protocol("WM_DELETE_WINDOW", on_crop_close)
            ctk.CTkButton(ctrl_frame, text='✅ យល់ព្រមកាត់រូប (Apply)', font=self.font_btn_bold, command=apply_crop, fg_color='#059669', hover_color='#047857', border_width=1, border_color='#34D399', height=36, corner_radius=8).pack(side='right', padx=15, pady=8)
    def open_manual_crop(self):
        if not self.processed_image:
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        else:
            crop_win = ctk.CTkToplevel(self)
            crop_win.title('Manual Crop - អូសទាញកាត់ខ្នាត')
            crop_win.transient(self)
            crop_win.attributes('-topmost', True)
            crop_win.configure(fg_color='#0A0E17')
            w, h = (960, 810)
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = int(sw / 2 - w / 2)
            y = int(sh / 2 - h / 2)
            crop_win.geometry(f'{w}x{h}+{x}+{y}')
            crop_win.grab_set()
            ctrl_frame = ctk.CTkFrame(crop_win, fg_color='#111622', corner_radius=12, border_width=1, border_color='#1E293B')
            ctrl_frame.pack(pady=10, padx=20, fill='x')
            ctk.CTkLabel(ctrl_frame, text='ទទឹង (cm):', font=self.font_text, text_color='#94A3B8').pack(side='left', padx=(15, 4), pady=8)
            ent_w = ctk.CTkEntry(ctrl_frame, width=54, height=32, corner_radius=6, fg_color='#080B12', border_color='#334155', text_color='#00F2FE', font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'))
            ent_w.insert(0, '3.5')
            ent_w.pack(side='left', padx=4, pady=8)
            ctk.CTkLabel(ctrl_frame, text='បណ្ដោ (cm):', font=self.font_text, text_color='#94A3B8').pack(side='left', padx=(10, 4), pady=8)
            ent_h = ctk.CTkEntry(ctrl_frame, width=54, height=32, corner_radius=6, fg_color='#080B12', border_color='#334155', text_color='#00F2FE', font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'))
            ent_h.insert(0, '4.5')
            ent_h.pack(side='left', padx=4, pady=8)
            ctk.CTkLabel(ctrl_frame, text='|  បង្វិល (Rotate):', font=self.font_text, text_color='#F59E0B').pack(side='left', padx=(15, 5), pady=8)
            sl_rotate = ctk.CTkSlider(ctrl_frame, from_=(-45), to=45, width=150, fg_color='#182234', progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#00F2FE')
            sl_rotate.set(0)
            sl_rotate.pack(side='left', padx=5, pady=8)
            canvas_frame = tk.Frame(crop_win, bg='#080B12')
            canvas_frame.pack(expand=True, fill='both', padx=20, pady=10)
            canvas = tk.Canvas(canvas_frame, bg='#080B12', cursor='crosshair', highlightthickness=0)
            canvas.pack(expand=True, fill='both')
            state = {'rect': None, 'mode': None, 'last_x': 0, 'last_y': 0, 'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0, 'disp_w': 0, 'disp_h': 0, 'scale': 1.0, 'rotated_img': None}
            def update_image(event=None):
                angle = sl_rotate.get()
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None:
                    try:
                        s_matched = self.suit_overlay_image.resize(self.processed_image.size, Image.Resampling.BILINEAR)
                        show_base = Image.alpha_composite(self.processed_image.convert('RGBA'), s_matched).convert('RGB')
                    except Exception:
                        show_base = self.processed_image.convert('RGB')
                else:
                    show_base = self.processed_image.convert('RGB')
                rotated = show_base.rotate(-angle, resample=Image.Resampling.BILINEAR, expand=True, fillcolor=(255, 255, 255))
                canvas.update_idletasks()
                cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                if cw <= 1 or ch <= 1:
                    cw, ch = (800, 600)
                w_img, h_img = rotated.size
                scale = min((cw - 40) / w_img, (ch - 40) / h_img)
                disp_w, disp_h = (int(w_img * scale), int(h_img * scale))
                state['img_tk'] = ImageTk.PhotoImage(rotated.resize((disp_w, disp_h), Image.Resampling.BILINEAR))
                state['scale'] = scale
                state['disp_w'] = disp_w
                state['disp_h'] = disp_h
                state['rotated_img'] = rotated
                canvas.delete('img')
                canvas.create_image(cw // 2, ch // 2, image=state['img_tk'], anchor='center', tags='img')
                try:
                    tr = float(ent_w.get()) / float(ent_h.get())
                except:
                    tr = 0.7777777777777778
                box_h = disp_h * 0.7
                box_w = box_h * tr
                if box_w > disp_w * 0.8:
                    box_w = disp_w * 0.8
                    box_h = box_w / tr
                cx, cy = (cw // 2, ch // 2)
                if not state['rect']:
                    state['x1'] = cx - box_w / 2
                    state['y1'] = cy - box_h / 2
                    state['x2'] = cx + box_w / 2
                    state['y2'] = cy + box_h / 2
                draw_rect()
            _manual_rotate_after = [None]
            def on_manual_slider(val=None):
                if _manual_rotate_after[0] is not None:
                    try:
                        crop_win.after_cancel(_manual_rotate_after[0])
                    except Exception:
                        pass
                _manual_rotate_after[0] = crop_win.after(20, update_image)
            sl_rotate.configure(command=on_manual_slider)
            crop_win.after(200, update_image)
            def draw_rect():
                if state['rect']:
                    canvas.delete(state['rect'])
                state['rect'] = canvas.create_rectangle(state['x1'], state['y1'], state['x2'], state['y2'], outline='#00FF00', width=3, dash=(4, 4))
            def get_mode(x_pos, y_pos):
                tol = 15
                if abs(x_pos - state['x1']) < tol and abs(y_pos - state['y1']) < tol:
                        return 'TL'
                if abs(x_pos - state['x2']) < tol and abs(y_pos - state['y2']) < tol:
                        return 'BR'
                if abs(x_pos - state['x2']) < tol and abs(y_pos - state['y1']) < tol:
                        return 'TR'
                if abs(x_pos - state['x1']) < tol and abs(y_pos - state['y2']) < tol:
                        return 'BL'
                if state['x1'] < x_pos < state['x2'] and state['y1'] < y_pos < state['y2']:
                                return 'MOVE'
                return None
            def update_cursor(event):
                mode = get_mode(event.x, event.y)
                if mode in ['TL', 'BR']:
                    canvas.config(cursor='size_nw_se')
                else:
                    if mode in ['TR', 'BL']:
                        canvas.config(cursor='size_ne_sw')
                    else:
                        if mode == 'MOVE':
                            canvas.config(cursor='fleur')
                        else:
                            canvas.config(cursor='crosshair')
            canvas.bind('<Motion>', update_cursor)
            def on_press(event):
                state['mode'] = get_mode(event.x, event.y)
                state['last_x'], state['last_y'] = (event.x, event.y)
            def on_drag(event):
                if not state['mode']:
                    return
                try:
                    tr = float(ent_w.get()) / float(ent_h.get())
                except:
                    tr = 0.7777777777777778
                dx, dy = (event.x - state['last_x'], event.y - state['last_y'])
                cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                lim_x1 = (cw - state['disp_w']) / 2
                lim_y1 = (ch - state['disp_h']) / 2
                lim_x2 = lim_x1 + state['disp_w']
                lim_y2 = lim_y1 + state['disp_h']
                if state['mode'] == 'MOVE':
                    if state['x1'] + dx >= lim_x1 and state['x2'] + dx <= lim_x2 and (state['y1'] + dy >= lim_y1) and (state['y2'] + dy <= lim_y2):
                                    state['x1'] += dx
                                    state['x2'] += dx
                                    state['y1'] += dy
                                    state['y2'] += dy
                                    state['last_x'], state['last_y'] = (event.x, event.y)
                else:
                    fx, fy = (state['x1'], state['y1'])
                    nw = state['x2'] - state['x1']
                    if state['mode'] == 'BR':
                        fx, fy, nw = (state['x1'], state['y1'], event.x - state['x1'])
                    else:
                        if state['mode'] == 'TL':
                            fx, fy, nw = (state['x2'], state['y2'], state['x2'] - event.x)
                        else:
                            if state['mode'] == 'TR':
                                fx, fy, nw = (state['x1'], state['y2'], event.x - state['x1'])
                            else:
                                if state['mode'] == 'BL':
                                    fx, fy, nw = (state['x2'], state['y1'], state['x2'] - event.x)
                    if nw < 50:
                        nw = 50
                    nh = nw / tr
                    if fx + nw > lim_x2 and state['mode'] in ['TR', 'BR']:
                            nw = lim_x2 - fx
                            nh = nw / tr
                    if fx - nw < lim_x1 and state['mode'] in ['TL', 'BL']:
                            nw = fx - lim_x1
                            nh = nw / tr
                    if fy + nh > lim_y2 and state['mode'] in ['BL', 'BR']:
                            nh = lim_y2 - fy
                            nw = nh * tr
                    if fy - nh < lim_y1 and state['mode'] in ['TL', 'TR']:
                            nh = fy - lim_y1
                            nw = nh * tr
                    if state['mode'] == 'BR':
                        state['x2'] = fx + nw
                        state['y2'] = fy + nh
                    else:
                        if state['mode'] == 'TL':
                            state['x1'] = fx - nw
                            state['y1'] = fy - nh
                        else:
                            if state['mode'] == 'TR':
                                state['x2'] = fx + nw
                                state['y1'] = fy - nh
                            else:
                                if state['mode'] == 'BL':
                                    state['x1'] = fx - nw
                                    state['y2'] = fy + nh
                    state['last_x'], state['last_y'] = (event.x, event.y)
                draw_rect()
            canvas.bind('<ButtonPress-1>', on_press)
            canvas.bind('<B1-Motion>', on_drag)
            def apply_crop():
                self.save_state()
                cw, ch = (canvas.winfo_width(), canvas.winfo_height())
                img_x_start = (cw - state['disp_w']) / 2
                img_y_start = (ch - state['disp_h']) / 2
                left = (state['x1'] - img_x_start) / state['scale']
                top = (state['y1'] - img_y_start) / state['scale']
                right = (state['x2'] - img_x_start) / state['scale']
                bottom = (state['y2'] - img_y_start) / state['scale']
                crop_box = (int(min(left, right)), int(min(top, bottom)), int(max(left, right)), int(max(top, bottom)))
                try:
                    w_cm, h_cm = (float(ent_w.get()), float(ent_h.get()))
                except:
                    w_cm, h_cm = (3.5, 4.5)
                self.output_dpi = (1200, 1200)
                req_w, req_h = (int(w_cm / 2.54 * 1200), int(h_cm / 2.54 * 1200))
                angle = sl_rotate.get()
                rotated_human = self.processed_image.rotate(-angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
                self.processed_image = rotated_human.crop(crop_box).resize((req_w, req_h), Image.Resampling.LANCZOS)
                self.invalidate_bg_cache()
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None:
                    rotated_suit = self.suit_overlay_image.rotate(-angle, resample=Image.BICUBIC, expand=True)
                    self.suit_overlay_image = rotated_suit.crop(crop_box).resize((req_w, req_h), Image.Resampling.LANCZOS)
                self.increment_action('manual_crop')
                self.fit_image()
                crop_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            def on_manual_crop_close():
                crop_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            crop_win.protocol("WM_DELETE_WINDOW", on_manual_crop_close)
            ctk.CTkButton(ctrl_frame, text='✅ យល់ព្រម (Apply)', font=self.font_btn, command=apply_crop, fg_color='#059669', hover_color='#047857', border_width=1, border_color='#34D399', corner_radius=8).pack(side='left', padx=15)
    def open_lut_studio(self):
        if not self.processed_image:
            return messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
        else:
            try:
                from pillow_lut import load_cube_file
            except ImportError:
                return messagebox.showerror('បញ្ហា', 'សូមដំឡើង pillow-lut សិន')
            base_img = self.processed_image.convert('RGB')
            fg_mask = None
            try:
                from rembg import remove
                import io
                img_byte = io.BytesIO()
                base_img.save(img_byte, format='PNG')
                bg_ses = self.get_bg_session()
                if bg_ses:
                    out_bytes = remove(img_byte.getvalue(), session=bg_ses)
                else:
                    out_bytes = remove(img_byte.getvalue())
                no_bg = Image.open(io.BytesIO(out_bytes)).convert('RGBA')
                fg_mask = no_bg.split()[3]
            except Exception as e:
                print('Mask Error:', e)
            lut_win = ctk.CTkToplevel(self)
            lut_win.title('🎨 Color LUTs & Lighting Studio')
            lut_win.configure(fg_color='#07090E')
            lut_win.transient(self)
            lut_win.attributes('-topmost', True)
            w, h = (1350, 780)
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = int(sw / 2 - w / 2)
            y = int(sh / 2 - h / 2)
            lut_win.geometry(f'{w}x{h}+{x}+{y}')
            lut_win.grab_set()
            display_img = base_img.copy()
            lut_win.preview_cache = None
            lut_win.image_cache = []
            selected_lut = 'Original'
            left_frame = ctk.CTkFrame(lut_win, width=320, fg_color='#0F172A', corner_radius=12, border_width=1, border_color='#1E293B')
            left_frame.pack(side='left', fill='y', padx=10, pady=10)
            left_frame.pack_propagate(False)
            right_frame = ctk.CTkFrame(lut_win, width=320, fg_color='#0F172A', corner_radius=12, border_width=1, border_color='#1E293B')
            right_frame.pack(side='right', fill='y', padx=10, pady=10)
            right_frame.pack_propagate(False)
            center_frame = ctk.CTkFrame(lut_win, fg_color='#080B12', corner_radius=12, border_width=1, border_color='#1E293B')
            center_frame.pack(side='left', fill='both', expand=True, padx=5, pady=10)
            preview_label = ctk.CTkLabel(center_frame, text='')
            preview_label.pack(fill='both', expand=True, padx=5, pady=5)
            slider_var = ctk.DoubleVar(value=0.5)
            wb_var = ctk.DoubleVar(value=1.0)
            bright_var = ctk.DoubleVar(value=1.0)
            contrast_var = ctk.DoubleVar(value=1.0)
            ui_labels = {}
            def process_image(*args):
                nonlocal display_img
                def format_lighting_val(v):
                    val = int((v - 1.0) * 200)
                    return f'+{val}' if val > 0 else str(val)
                if 'lut' in ui_labels:
                    ui_labels['lut'].configure(text=f'កម្រិតពណ៌ LUT: {int(slider_var.get() * 100)}%')
                if 'wb' in ui_labels:
                    ui_labels['wb'].configure(text=f'White Balance (កម្ដៅ): {format_lighting_val(wb_var.get())}')
                if 'bright' in ui_labels:
                    ui_labels['bright'].configure(text=f'Brightness (ពន្លឺ): {format_lighting_val(bright_var.get())}')
                if 'contrast' in ui_labels:
                    ui_labels['contrast'].configure(text=f'Highlights / Shadows: {format_lighting_val(contrast_var.get())}')
                fg_enhanced = base_img.copy()
                if selected_lut != 'Original' and selected_lut != 'None':
                        import os
                        lut_path = os.path.join('LUTs', selected_lut)
                        if os.path.exists(lut_path):
                            try:
                                from PIL import Image
                                lut = load_cube_file(lut_path)
                                lut_img = base_img.filter(lut)
                                fg_enhanced = Image.blend(base_img, lut_img, slider_var.get())
                            except Exception as e:
                                print('LUT Error:', e)
                from PIL import ImageEnhance
                if bright_var.get() != 1.0:
                    fg_enhanced = ImageEnhance.Brightness(fg_enhanced).enhance(bright_var.get())
                if contrast_var.get() != 1.0:
                    fg_enhanced = ImageEnhance.Contrast(fg_enhanced).enhance(contrast_var.get())
                if wb_var.get() != 1.0:
                    fg_enhanced = ImageEnhance.Color(fg_enhanced).enhance(wb_var.get())
                if fg_mask:
                    from PIL import Image
                    display_img = Image.composite(fg_enhanced, base_img, fg_mask)
                else:
                    display_img = fg_enhanced
                update_preview_ui()
            def select_lut(lut_name):
                nonlocal selected_lut
                selected_lut = lut_name
                process_image()
            def update_preview_ui():
                w_win, h_win = (center_frame.winfo_width(), center_frame.winfo_height())
                if w_win <= 10 or h_win <= 10:
                    w_win, h_win = (600, 600)
                img_copy = display_img.copy()
                img_copy.thumbnail((w_win, h_win))
                ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
                preview_label.configure(image=ctk_img)
                lut_win.preview_cache = ctk_img
            center_frame.bind('<Configure>', lambda e: update_preview_ui())
            def apply_to_main():
                try:
                    self.save_state()
                    self.processed_image = display_img
                    self.fit_image()
                    self.increment_action('lut')
                    lut_win.destroy()
                except Exception as e:
                    print('Error ពេល Apply:', e)
                    lut_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            def on_lut_close():
                lut_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
            lut_win.protocol("WM_DELETE_WINDOW", on_lut_close)
            ctk.CTkLabel(left_frame, text='🎨 ជ្រើសរើសប្រភេទពណ៌', font=('Khmer OS Siemreap', 15, 'bold'), text_color='#38BDF8').pack(pady=(15, 5))
            scroll_frame = ctk.CTkScrollableFrame(left_frame, width=300, height=520, fg_color='#0A0E17')
            scroll_frame.pack(fill='both', expand=True, padx=10, pady=5)
            lbl_intensity = ctk.CTkLabel(left_frame, text='កម្រិតពណ៌ LUT: 50%', font=('Khmer OS Siemreap', 13), text_color='#E2E8F0')
            lbl_intensity.pack(pady=(15, 5))
            ui_labels['lut'] = lbl_intensity
            ctk.CTkSlider(left_frame, from_=0, to=1, variable=slider_var, command=process_image, progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#7DD3FC').pack(fill='x', padx=15, pady=(5, 20))
            ctk.CTkLabel(right_frame, text='✨ កំណត់ពន្លឺបន្ថែម', font=('Khmer OS Siemreap', 15, 'bold'), text_color='#F59E0B').pack(pady=(15, 20))
            def create_adjust_slider(parent, text, var, from_val, to_val, key):
                val_num = int((var.get() - 1.0) * 200)
                sign = '+' if val_num > 0 else ''
                lbl = ctk.CTkLabel(parent, text=f'{text} {sign}{val_num}', font=('Arial', 12), text_color='#CBD5E1')
                lbl.pack(anchor='w', padx=15, pady=(5, 0))
                ui_labels[key] = lbl
                slider = ctk.CTkSlider(parent, from_=from_val, to=to_val, variable=var, command=process_image, progress_color='#00F2FE', button_color='#38BDF8', button_hover_color='#7DD3FC')
                slider.pack(fill='x', padx=15, pady=(5, 15))
                return slider
            create_adjust_slider(right_frame, 'White Balance (កម្ដៅ):', wb_var, 0.5, 1.5, 'wb')
            create_adjust_slider(right_frame, 'Brightness (ពន្លឺ):', bright_var, 0.5, 1.5, 'bright')
            create_adjust_slider(right_frame, 'Highlights / Shadows:', contrast_var, 0.5, 1.5, 'contrast')
            def reset_lighting():
                wb_var.set(1.0)
                bright_var.set(1.0)
                contrast_var.set(1.0)
                process_image()
            ctk.CTkButton(right_frame, text='🔄 ត្រឡប់ដើម (Reset Light)', font=('Khmer OS Siemreap', 13), fg_color='#1E293B', hover_color='#334155', border_width=1, border_color='#334155', corner_radius=8, command=reset_lighting).pack(pady=10, padx=15, fill='x')
            ctk.CTkButton(right_frame, text='✅ យល់ព្រម (Apply)', font=('Khmer OS Siemreap', 14, 'bold'), command=apply_to_main, fg_color='#059669', hover_color='#047857', border_width=1, border_color='#34D399', corner_radius=8).pack(side='bottom', fill='x', padx=15, pady=20)
            import os
            if not os.path.exists('LUTs'):
                os.makedirs('LUTs')
            lut_files = ['Original'] + [f for f in os.listdir('LUTs') if f.endswith(('.cube', '.CUBE'))]
            thumb_base = base_img.copy()
            thumb_base.thumbnail((120, 120))
            row_pos, col_pos = (0, 0)
            for lut_name in lut_files:
                try:
                    if lut_name == 'Original':
                        thumb_img = thumb_base.copy()
                        display_name = 'Original'
                    else:
                        lut_path = os.path.join('LUTs', lut_name)
                        lut = load_cube_file(lut_path)
                        thumb_img = thumb_base.filter(lut)
                        raw_name = lut_name.replace('.cube', '').replace('.CUBE', '')
                        display_name = raw_name[:12] + '...' if len(raw_name) > 15 else raw_name
                    thumb_ctk = ctk.CTkImage(light_image=thumb_img, dark_image=thumb_img, size=(100, 100))
                    lut_win.image_cache.append(thumb_ctk)
                    btn = ctk.CTkButton(scroll_frame, image=thumb_ctk, text=display_name, compound='top', width=110, height=130, fg_color='#111827', hover_color='#1E293B', border_width=1, border_color='#1E293B', corner_radius=8, font=('Arial', 11), command=lambda name=lut_name: select_lut(name))
                    btn.grid(row=row_pos, column=col_pos, padx=8, pady=8)
                    col_pos += 1
                    if col_pos > 1:
                        col_pos = 0
                        row_pos += 1
                except Exception:
                    continue
            lut_win.after(200, update_preview_ui)
    def save_image(self):
        if not self.ensure_license_active("រក្សាទុករូបភាព (Save Image)"):
            return
        if self.processed_image:
            save_path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG', '*.jpg')])
            if save_path:
                if hasattr(self, 'suit_overlay_image') and self.suit_overlay_image:
                    save_img = Image.alpha_composite(self.processed_image.convert('RGBA'), self.suit_overlay_image).convert('RGB')
                else:
                    save_img = self.processed_image.convert('RGB')
                save_img.save(save_path, quality=100, dpi=self.output_dpi)
                messagebox.showinfo('ជោគជ័យ', f'រក្សាទុករួចរាល់! គុណភាព 2K កម្រិត {self.output_dpi[0]} DPI។')
        else:
            messagebox.showwarning('បញ្ហា', 'គ្មានរូបភាពសម្រាប់ Save ទេ!')
    def _process_live_lighting(self):
        if not hasattr(self, 'base_lighting_img'):
            return
        else:
            from PIL import Image
            wb = self.sl_wb.get() / 2.0
            bright = self.sl_bright.get() / 1.5
            hl = self.sl_hl.get() / 1.5
            shadow = self.sl_shadow.get() / 1.5
            blacks = self.sl_black.get() / 1.5
            img_np = np.array(self.base_lighting_img.convert('RGB')).astype(np.float32)
            if wb != 0:
                img_np[:, :, 0] += wb * 1.5
                img_np[:, :, 2] -= wb * 1.5
            if bright != 0:
                img_np += bright
            if hl != 0 or shadow != 0 or blacks != 0:
                lum = cv2.cvtColor(np.clip(img_np, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
                shadow_mask = np.clip((128 - lum) / 128, 0, 1)
                hl_mask = np.clip((lum - 128) / 128, 0, 1)
                black_mask = np.clip((50 - lum) / 50, 0, 1)
                for i in range(3):
                    if shadow != 0:
                        img_np[:, :, i] += shadow_mask * shadow
                    if hl != 0:
                        img_np[:, :, i] += hl_mask * hl
                    if blacks != 0:
                        img_np[:, :, i] += black_mask * blacks
            enhanced_fg = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
            if getattr(self, 'light_fg_mask', None):
                self.preview_lighting_img = Image.composite(enhanced_fg, self.base_lighting_img, self.light_fg_mask)
            else:
                self.preview_lighting_img = enhanced_fg
            self.update_canvas_display(preview_mode=True)
    def toggle_light_panel(self):
        if not self.light_panel_open:
            if not getattr(self, 'processed_image', None):
                return messagebox.showwarning('បញ្ជាក់', 'សូមបញ្ចូលរូបថតជាមុនសិន!')
            else:
                self.light_panel_open = True
                if hasattr(self, 'btn_toggle_light'):
                    self.btn_toggle_light.configure(text='💡 បិទផ្ទាំងពន្លឺ (Close Light) ▲')
                if hasattr(self, 'container_light') and hasattr(self, 'card_pro'):
                    self.container_light.pack(pady=4, padx=12, fill='x', after=self.card_pro)
                self.light_frame.pack(fill='x', pady=4)
                self.base_lighting_img = self.processed_image.copy()
                self.preview_lighting_img = self.processed_image.copy()
                bg_cache = getattr(self, '_bg_cache', None)
                if bg_cache is not None and bg_cache.get('alpha') is not None and bg_cache.get('size') == self.base_lighting_img.size:
                    alpha_np = (bg_cache['alpha'][:, :, 0] * 255.0).astype(np.uint8)
                    self.light_fg_mask = Image.fromarray(alpha_np)
                else:
                    self.light_fg_mask = None
        else:
            self.light_panel_open = False
            if hasattr(self, 'btn_toggle_light'):
                self.btn_toggle_light.configure(text='💡 កំណត់ពន្លឺ (Studio Light) ▼')
            self.light_frame.pack_forget()
            if hasattr(self, 'container_light'):
                self.container_light.pack_forget()
            if self.processed_image and hasattr(self, 'base_lighting_img'):
                self.processed_image = self.base_lighting_img
                self.update_canvas_display()
            self.reset_sliders()
            if hasattr(self, 'light_fg_mask'):
                delattr(self, 'light_fg_mask')
    def apply_lighting(self):
        if not hasattr(self, 'preview_lighting_img'):
            return
        else:
            self.save_state()
            self.processed_image = self.preview_lighting_img.copy()
            self.base_lighting_img = self.processed_image.copy()
            self.update_canvas_display()
            self.toggle_light_panel()
            self.increment_action('lighting')
    def live_preview_lighting(self, value=None):
        if hasattr(self, '_light_after_id') and self._light_after_id:
                self.after_cancel(self._light_after_id)
        self._light_after_id = self.after(100, self._process_live_lighting)
    def live_preview_makeup(self, value=None):
        if not self.processed_image:
            return
        else:
            if hasattr(self, '_makeup_after_id') and self._makeup_after_id:
                    self.after_cancel(self._makeup_after_id)
            self._makeup_after_id = self.after(100, self._process_live_makeup)
    def _process_live_makeup(self):
        if not hasattr(self, 'base_makeup_img'):
            self.base_makeup_img = self.processed_image.copy()
        tone_val = self.sl_tone.get()
        glow_val = self.sl_glow.get()
        matte_val = self.sl_matte.get()
        lips_val = self.sl_lips.get()
        if tone_val == 0 and glow_val == 0 and (matte_val == 0) and (lips_val == 0 or getattr(self, 'lips_mask_layer', None) is None):
            self.canvas.delete('lip_trace')
            self.preview_makeup_img = self.base_makeup_img.copy()
            self.update_canvas_display(preview_mode=True, use_makeup=True)
        else:
            img_cv = np.array(self.base_makeup_img.convert('RGB'))[:, :, ::(-1)].copy()
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            result_cv = img_cv.astype(np.float32)
            skin_mask = cv2.inRange(hsv, np.array([0, 10, 20]), np.array([30, 200, 255]))
            skin_mask = cv2.GaussianBlur(skin_mask, (21, 21), 0).astype(np.float32) / 255.0
            if tone_val != 0:
                tone_factor = abs(tone_val) / 50.0
                if tone_val < 0:
                    result_cv += np.stack([skin_mask] * 3, axis=(-1)) * (20 * tone_factor)
                    result_cv[:, :, 2] += skin_mask * 10 * tone_factor
                    result_cv[:, :, 0] += skin_mask * 15 * tone_factor
                else:
                    result_cv[:, :, 2] += skin_mask * 20 * tone_factor
                    result_cv[:, :, 1] += skin_mask * 10 * tone_factor
                    result_cv[:, :, 0] -= skin_mask * 20 * tone_factor
            if glow_val > 0:
                result_cv += np.stack([skin_mask] * 3, axis=(-1)) * (glow_val * 0.4)
            if matte_val > 0:
                face_box = getattr(self, '_cached_face_box', None)
                if face_box is None:
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    cascade_path = getattr(self, '_cascade_path', None)
                    if not cascade_path or not os.path.exists(cascade_path):
                        cascade_path = 'haarcascade_frontalface_default.xml'
                        if not os.path.exists(cascade_path):
                            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                        self._cascade_path = cascade_path
                    if os.path.exists(cascade_path):
                        if getattr(self, '_face_classifier', None) is None:
                            self._face_classifier = cv2.CascadeClassifier(cascade_path)
                        faces = self._face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
                        if len(faces) > 0:
                            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                            self._cached_face_box = faces[0]
                            face_box = faces[0]
                if face_box is not None:
                    x_face, y_face, w_face, h_face = face_box
                    ey = max(0, y_face - int(h_face * 0.1))
                    eh = min(img_cv.shape[0] - ey, int(h_face * 1.2))
                    ex = max(0, x_face - int(w_face * 0.1))
                    ew = min(img_cv.shape[1] - ex, int(w_face * 1.2))
                    if eh > 0 and ew > 0:
                        roi = result_cv[ey:ey + eh, ex:ex + ew]
                        roi_hsv = cv2.cvtColor(np.clip(roi, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
                        v_channel = roi_hsv[:, :, 2].astype(np.float32)
                        s_channel = roi_hsv[:, :, 1].astype(np.float32)
                        shine_mask = np.clip((v_channel - 160) / 95.0, 0, 1)
                        sat_mask = np.clip((90 - s_channel) / 90.0, 0, 1)
                        combined_shine = shine_mask * sat_mask
                        roi_skin_mask = skin_mask[ey:ey + eh, ex:ex + ew]
                        final_shine_mask = combined_shine * roi_skin_mask
                        final_shine_mask = cv2.GaussianBlur(final_shine_mask, (15, 15), 0)
                        blurred_roi = cv2.bilateralFilter(np.clip(roi, 0, 255).astype(np.uint8), 15, 75, 75)
                        blurred_roi = cv2.GaussianBlur(blurred_roi, (35, 35), 0).astype(np.float32)
                        matte_factor = matte_val / 100.0
                        mask_3d = np.stack([final_shine_mask * matte_factor] * 3, axis=2)
                        result_cv[ey:ey + eh, ex:ex + ew] = roi * (1.0 - mask_3d) + blurred_roi * mask_3d
            if lips_val > 0 and getattr(self, 'lips_mask_layer', None) is not None:
                    lips_factor = lips_val / 100.0
                    lips_mask_3d = np.stack([self.lips_mask_layer] * 3, axis=2).astype(np.float32) / 255.0
                    result_cv[:, :, 2] += lips_mask_3d[:, :, 2] * 80 * lips_factor
                    result_cv[:, :, 1] -= lips_mask_3d[:, :, 1] * 20 * lips_factor
                    result_cv[:, :, 0] -= lips_mask_3d[:, :, 0] * 20 * lips_factor
            self.canvas.delete('lip_trace')
            result_cv = np.clip(result_cv, 0, 255).astype(np.uint8)
            self.preview_makeup_img = Image.fromarray(cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB))
            self.update_canvas_display(preview_mode=True, use_makeup=True)
    def apply_makeup_live(self):
        if not hasattr(self, 'preview_makeup_img'):
            return
        else:
            self.save_state()
            self.processed_image = self.preview_makeup_img.copy()
            if hasattr(self, 'base_makeup_img'):
                delattr(self, 'base_makeup_img')
            self.sl_tone.set(0)
            self.sl_glow.set(0)
            self.sl_matte.set(0)
            self.sl_lips.set(0)
            self.lips_mask_layer = None
            self.update_canvas_display()
            self.increment_action('live_makeup')
    def reset_all_tools(self):
        self.healing_active = False
        self.lips_brush_active = False
        self.eraser_active = False
        self.liquify_active = False
        self.btn_spot_heal.configure(fg_color='#141C2B', border_width=1, border_color='#1E2A3E')
        self.btn_lips_brush.configure(fg_color='#141C2B', border_width=1, border_color='#1E2A3E')
        self.btn_eraser.configure(fg_color='#141C2B', border_width=1, border_color='#1E2A3E')
        self.btn_liquify.configure(fg_color='#141C2B', border_width=1, border_color='#1E2A3E')
        self.canvas.config(cursor='')
        self.canvas.delete('brush_outline')

    def toggle_healing(self):
        if not self.processed_image:
            return
        else:
            is_active = not self.healing_active
            self.reset_all_tools()
            if is_active:
                self.healing_active = True
                self.btn_spot_heal.configure(fg_color='#331E05', border_width=2, border_color='#F59E0B')
                self.canvas.config(cursor='crosshair')
    def toggle_lips_brush(self):
        if not self.processed_image:
            return
        else:
            is_active = not getattr(self, 'lips_brush_active', False)
            self.reset_all_tools()
            if is_active:
                self.lips_brush_active = True
                self.btn_lips_brush.configure(fg_color='#3B0822', border_width=2, border_color='#FF2E93')
                self.canvas.config(cursor='crosshair')
                if getattr(self, 'lips_mask_layer', None) is None:
                    self.lips_mask_layer = np.zeros((self.processed_image.height, self.processed_image.width), dtype=np.float32)
    def toggle_eraser(self):
        if not self.processed_image:
            return
        else:
            is_active = not getattr(self, 'eraser_active', False)
            self.reset_all_tools()
            if is_active:
                self.eraser_active = True
                self.btn_eraser.configure(fg_color='#032735', border_width=2, border_color='#00F2FE')
                self.canvas.config(cursor='dot')
                if self.processed_image.mode != 'RGBA':
                    self.processed_image = self.processed_image.convert('RGBA')
                    self.update_canvas_display()
    def toggle_liquify(self):
        if not self.processed_image:
            return
        else:
            is_active = not getattr(self, 'liquify_active', False)
            self.reset_all_tools()
            if is_active:
                self.liquify_active = True
                self.btn_liquify.configure(fg_color='#240E3E', border_width=2, border_color='#A855F7')
                self.canvas.config(cursor='target')
    def on_brush_size_change(self, value):
        if self.healing_active or self.lips_brush_active or self.eraser_active or self.liquify_active:
            if hasattr(self, 'current_mouse_x'):
                self.draw_brush_cursor(self.current_mouse_x, self.current_mouse_y)
    def draw_brush_cursor(self, x, y):
        if not (self.healing_active or self.lips_brush_active or self.eraser_active or self.liquify_active):
            self.canvas.delete('brush_outline')
            return
        brush_rad = getattr(self, 'cached_brush_radius', None)
        if brush_rad is None:
            brush_rad = float(self.sl_brush.get())
            self.cached_brush_radius = brush_rad
        color = 'white' if not self.liquify_active else 'yellow'
        r = brush_rad * self.zoom_level
        items = self.canvas.find_withtag('brush_outline')
        if len(items) == 2:
            self.canvas.coords(items[0], x - r, y - r, x + r, y + r)
            if getattr(self, '_last_brush_cursor_color', None) != color:
                self.canvas.itemconfig(items[0], outline=color)
                self._last_brush_cursor_color = color
            self.canvas.coords(items[1], x - r - 1, y - r - 1, x + r + 1, y + r + 1)
        else:
            self.canvas.delete('brush_outline')
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2, tags='brush_outline')
            self.canvas.create_oval(x - r - 1, y - r - 1, x + r + 1, y + r + 1, outline='black', width=1, tags='brush_outline')
            self._last_brush_cursor_color = color
            self.canvas.tag_raise('brush_outline')
    def draw_heal_stroke(self, cx, cy):
        iw, ih = self.processed_image.size
        sw, sh = (iw * self.zoom_level, ih * self.zoom_level)
        img_x = int((cx - (self.canvas_img_x - sw / 2)) / self.zoom_level)
        img_y = int((cy - (self.canvas_img_y - sh / 2)) / self.zoom_level)
        brush = int(self.sl_brush.get())
        hardness = self.sl_hard.get() / 100.0 if hasattr(self, 'sl_hard') else 0.5
        brush_mask_float = self.get_soft_brush(brush, hardness)
        prev_x = getattr(self, 'prev_brush_x', img_x)
        prev_y = getattr(self, 'prev_brush_y', img_y)
        dist = math.hypot(img_x - prev_x, img_y - prev_y)
        spacing = max(1, int(brush * 0.15))
        steps = max(1, int(dist / spacing))
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            px = int(prev_x + t * (img_x - prev_x))
            py = int(prev_y + t * (img_y - prev_y))
            y1, y2 = (max(0, py - brush), min(self.heal_mask_soft.shape[0], py + brush))
            x1, x2 = (max(0, px - brush), min(self.heal_mask_soft.shape[1], px + brush))
            by1 = brush - (py - y1)
            by2 = brush + (y2 - py)
            bx1 = brush - (px - x1)
            bx2 = brush + (x2 - px)
            if y1 < y2 and x1 < x2:
                    self.heal_mask_soft[y1:y2, x1:x2] = np.maximum(self.heal_mask_soft[y1:y2, x1:x2], brush_mask_float[by1:by2, bx1:bx2])
                    cv2.circle(self.heal_mask, (px, py), brush, 255, (-1))
        self.prev_brush_x = img_x
        self.prev_brush_y = img_y
        r = brush * self.zoom_level
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline='red', width=2, fill='red', stipple='gray25', tags='heal_trace')
    def draw_lips_stroke(self, cx, cy):
        iw, ih = self.processed_image.size
        sw, sh = (iw * self.zoom_level, ih * self.zoom_level)
        img_x = int((cx - (self.canvas_img_x - sw / 2)) / self.zoom_level)
        img_y = int((cy - (self.canvas_img_y - sh / 2)) / self.zoom_level)
        brush = int(self.sl_brush.get())
        hardness = self.sl_hard.get() / 100.0 if hasattr(self, 'sl_hard') else 0.5
        brush_mask = self.get_soft_brush(brush, hardness) * 255.0
        prev_x = getattr(self, 'prev_brush_x', img_x)
        prev_y = getattr(self, 'prev_brush_y', img_y)
        dist = math.hypot(img_x - prev_x, img_y - prev_y)
        spacing = max(1, int(brush * 0.15))
        steps = max(1, int(dist / spacing))
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            px = int(prev_x + t * (img_x - prev_x))
            py = int(prev_y + t * (img_y - prev_y))
            y1, y2 = (max(0, py - brush), min(self.lips_mask_layer.shape[0], py + brush))
            x1, x2 = (max(0, px - brush), min(self.lips_mask_layer.shape[1], px + brush))
            by1 = brush - (py - y1)
            by2 = brush + (y2 - py)
            bx1 = brush - (px - x1)
            bx2 = brush + (x2 - px)
            if y1 < y2 and x1 < x2:
                    self.lips_mask_layer[y1:y2, x1:x2] = np.maximum(self.lips_mask_layer[y1:y2, x1:x2], brush_mask[by1:by2, bx1:bx2])
        self.prev_brush_x = img_x
        self.prev_brush_y = img_y
        r = brush * self.zoom_level
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline='pink', width=2, fill='pink', stipple='gray25', tags='lip_trace')
    def on_mouse_move(self, event):
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y
        if self.healing_active or self.lips_brush_active or self.eraser_active or self.liquify_active:
            self.draw_brush_cursor(event.x, event.y)
        else:
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
    def on_mouse_leave(self, event):
        self.canvas.delete('brush_outline')
    def on_mouse_press(self, event):
        try:
            self.canvas.focus_set()
        except Exception:
            pass
        if not self.processed_image:
            return
        else:
            iw, ih = self.processed_image.size
            sw, sh = (iw * self.zoom_level, ih * self.zoom_level)
            img_x = int((event.x - (self.canvas_img_x - sw / 2)) / self.zoom_level)
            img_y = int((event.y - (self.canvas_img_y - sh / 2)) / self.zoom_level)

            if self.healing_active:
                self.save_state()
                self.heal_mask = np.zeros((self.processed_image.height, self.processed_image.width), dtype=np.uint8)
                self.heal_mask_soft = np.zeros((self.processed_image.height, self.processed_image.width), dtype=np.float32)
                self.prev_brush_x = img_x
                self.prev_brush_y = img_y
                self.draw_heal_stroke(event.x, event.y)
            else:
                if self.lips_brush_active:
                    self.prev_brush_x = img_x
                    self.prev_brush_y = img_y
                    self.draw_lips_stroke(event.x, event.y)
                else:
                    if self.eraser_active:
                        self.save_state()
                        self.prev_brush_x = img_x
                        self.prev_brush_y = img_y
                        self.cached_brush_radius = float(self.sl_brush.get())
                        self.cached_brush_hardness = float(self.sl_hard.get()) / 100.0 if hasattr(self, 'sl_hard') else 0.5
                        try:
                            self.eraser_bg_color = self.processed_image.getpixel((5, 5))
                        except:
                            self.eraser_bg_color = (255, 255, 255)
                        if self.processed_image.mode != 'RGBA':
                            self.processed_image = self.processed_image.convert('RGBA')
                        self.eraser_cv = np.array(self.processed_image)
                        self.on_mouse_drag(event)
                    else:
                        if self.liquify_active:
                            self.save_state()
                            self.liq_start_x = event.x
                            self.liq_start_y = event.y
                            self.liq_has_moved = False
                        else:
                            self.last_mouse_x = event.x
                            self.last_mouse_y = event.y
    def on_mouse_drag(self, event):
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y
        if self.healing_active and getattr(self, 'heal_mask', None) is not None:
            self.draw_heal_stroke(event.x, event.y)
            self.draw_brush_cursor(event.x, event.y)
            return
        else:
            if self.lips_brush_active and getattr(self, 'lips_mask_layer', None) is not None:
                self.draw_lips_stroke(event.x, event.y)
                self.draw_brush_cursor(event.x, event.y)
                return
            else:
                if getattr(self, 'eraser_active', False):
                    if getattr(self, 'processed_image', None) is None or getattr(self, 'eraser_cv', None) is None:
                        return
                    else:
                        iw, ih = self.processed_image.size
                        sw, sh = (iw * self.zoom_level, ih * self.zoom_level)
                        img_x = int((event.x - (self.canvas_img_x - sw / 2)) / self.zoom_level)
                        img_y = int((event.y - (self.canvas_img_y - sh / 2)) / self.zoom_level)
                        try:
                            brush_radius = int(getattr(self, 'cached_brush_radius', 30.0))
                            hardness = getattr(self, 'cached_brush_hardness', 0.5)
                            brush_mask_float = self.get_soft_brush(brush_radius, hardness)
                            default_bg = getattr(self, 'eraser_bg_color', (255, 255, 255))
                            if len(default_bg) == 3:
                                default_bg = (*default_bg, 255)
                            default_bg_np = np.array(default_bg, dtype=np.float32)

                            prev_x = getattr(self, 'prev_brush_x', img_x)
                            prev_y = getattr(self, 'prev_brush_y', img_y)
                            dist = math.hypot(img_x - prev_x, img_y - prev_y)
                            spacing = max(1, int(brush_radius * 0.2))
                            steps = max(1, int(dist / spacing))
                            h_cv, w_cv = self.eraser_cv.shape[:2]

                            for i in range(steps + 1):
                                t = i / steps if steps > 0 else 0
                                cx = int(prev_x + t * (img_x - prev_x))
                                cy = int(prev_y + t * (img_y - prev_y))
                                y1, y2 = (max(0, cy - brush_radius), min(h_cv, cy + brush_radius))
                                x1, x2 = (max(0, cx - brush_radius), min(w_cv, cx + brush_radius))
                                by1 = brush_radius - (cy - y1)
                                by2 = brush_radius + (y2 - cy)
                                bx1 = brush_radius - (cx - x1)
                                bx2 = brush_radius + (x2 - cx)
                                if y1 < y2 and x1 < x2:
                                    roi = self.eraser_cv[y1:y2, x1:x2].astype(np.float32)
                                    mask = brush_mask_float[by1:by2, bx1:bx2]
                                    mask_3d = mask[:, :, None]
                                    blended = roi * (1.0 - mask_3d) + default_bg_np * mask_3d
                                    self.eraser_cv[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)

                            self._composite_cache_key = None
                            self._composite_cache_img = None
                            self.schedule_canvas_update()
                            self.draw_brush_cursor(event.x, event.y)
                            self.prev_brush_x = img_x
                            self.prev_brush_y = img_y
                        except Exception as ex:
                            print('Error ពេលលុប Background រូបដើម៖', ex)
                else:
                    if getattr(self, 'liquify_active', False):
                        if getattr(self, 'processed_image', None) is None:
                            return
                        else:
                            iw, ih = self.processed_image.size
                            sw, sh = (iw * self.zoom_level, ih * self.zoom_level)
                            img_curr_x = (event.x - (self.canvas_img_x - sw / 2)) / self.zoom_level
                            img_curr_y = (event.y - (self.canvas_img_y - sh / 2)) / self.zoom_level
                            img_prev_x = (self.liq_start_x - (self.canvas_img_x - sw / 2)) / self.zoom_level
                            img_prev_y = (self.liq_start_y - (self.canvas_img_y - sh / 2)) / self.zoom_level
                            try:
                                disp_x = img_curr_x - img_prev_x
                                disp_y = img_curr_y - img_prev_y
                                disp_len = math.hypot(disp_x, disp_y)
                                brush_radius = float(self.sl_brush.get())
                                hardness = (self.sl_hard.get() / 100.0) if hasattr(self, 'sl_hard') else 0.5
                                if disp_len >= 0.75:
                                    max_disp = brush_radius * 0.45
                                    if disp_len > max_disp:
                                        scale_factor = max_disp / disp_len
                                        disp_x *= scale_factor
                                        disp_y *= scale_factor

                                    r = max(2, int(brush_radius))
                                    r_sq = float(r * r)
                                    roi_x1 = max(0, int(img_prev_x - r))
                                    roi_y1 = max(0, int(img_prev_y - r))
                                    roi_x2 = min(iw, int(img_prev_x + r + 1))
                                    roi_y2 = min(ih, int(img_prev_y + r + 1))
                                    if roi_x2 > roi_x1 and roi_y2 > roi_y1:
                                        roi = self.processed_image.crop((roi_x1, roi_y1, roi_x2, roi_y2))
                                        roi_np = np.array(roi)
                                        h_roi, w_roi = roi_np.shape[:2]
                                        gx = np.arange(roi_x1, roi_x2, dtype=np.float32) - img_prev_x
                                        gy = np.arange(roi_y1, roi_y2, dtype=np.float32) - img_prev_y
                                        dist_sq = (gx[None, :] ** 2) + (gy[:, None] ** 2)
                                        norm_sq = np.clip(dist_sq / r_sq, 0.0, 1.0)
                                        weight = (1.0 - norm_sq) ** 3
                                        if hardness > 0.5:
                                            weight = weight ** (1.0 - (hardness - 0.5) * 0.8)
                                        push_factor = 0.55
                                        map_X = (np.arange(w_roi, dtype=np.float32)[None, :] - (disp_x * push_factor) * weight).astype(np.float32)
                                        map_Y = (np.arange(h_roi, dtype=np.float32)[:, None] - (disp_y * push_factor) * weight).astype(np.float32)
                                        warped = cv2.remap(roi_np, map_X, map_Y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                                        warped_roi = Image.fromarray(warped, self.processed_image.mode)
                                        self.processed_image.paste(warped_roi, (roi_x1, roi_y1))
                                        self._composite_cache_key = None
                                        self._composite_cache_img = None
                                        self.liq_has_moved = True
                                        self.schedule_canvas_update()
                                    self.liq_start_x = event.x
                                    self.liq_start_y = event.y
                                self.draw_brush_cursor(event.x, event.y)
                            except Exception as ex:
                                print('Error ពេល Liquify រូបដើម៖', ex)
                    else:
                        if not self.processed_image:
                            return
                        else:
                            dx = event.x - self.last_mouse_x
                            dy = event.y - self.last_mouse_y
                            self.canvas_img_x += dx
                            self.canvas_img_y += dy
                            self.last_mouse_x = event.x
                            self.last_mouse_y = event.y
                            self.canvas.move('img_item', dx, dy)
                            self.canvas.move('suit_item', dx, dy)
                            if getattr(self, '_viewport_clipped', False):
                                self._pan_accum_x = getattr(self, '_pan_accum_x', 0) + dx
                                self._pan_accum_y = getattr(self, '_pan_accum_y', 0) + dy
                                if abs(self._pan_accum_x) > 60 or abs(self._pan_accum_y) > 60:
                                    self._pan_accum_x = 0
                                    self._pan_accum_y = 0
                                    self.schedule_canvas_update()
    def on_mouse_release(self, event):
        if getattr(self, 'eraser_active', False) and getattr(self, 'eraser_cv', None) is not None:
            self.processed_image = Image.fromarray(self.eraser_cv)
            self.eraser_cv = None
            if getattr(self, '_canvas_update_scheduled', False):
                self._perform_scheduled_canvas_update()
            else:
                self.update_canvas_display()
            self.increment_action('eraser')
        elif self.healing_active and getattr(self, 'heal_mask', None) is not None:
            img_cv = np.array(self.processed_image.convert('RGB'))[:, :, ::(-1)]
            inpainted = cv2.inpaint(img_cv, self.heal_mask, 3, cv2.INPAINT_TELEA)
            soft_mask_3d = np.stack([self.heal_mask_soft] * 3, axis=2)
            result = (img_cv * (1 - soft_mask_3d) + inpainted * soft_mask_3d).astype(np.uint8)
            self.processed_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            self.heal_mask = None
            self.heal_mask_soft = None
            self.canvas.delete('heal_trace')
            self.update_canvas_display()
            self.increment_action('spot_heal')
        else:
            if self.lips_brush_active and getattr(self, 'lips_mask_layer', None) is not None:
                self.live_preview_makeup()
            else:
                if self.liquify_active:
                    if hasattr(self, 'liq_start_x'):
                        delattr(self, 'liq_start_x')
                    if hasattr(self, 'liq_start_y'):
                        delattr(self, 'liq_start_y')
                    if getattr(self, '_canvas_update_scheduled', False):
                        self._perform_scheduled_canvas_update()
                    else:
                        self.update_canvas_display()
                    if getattr(self, 'liq_has_moved', False):
                        self.liq_has_moved = False
                        self.increment_action('liquify')
        if getattr(self, '_viewport_clipped', False):
            self.schedule_canvas_update()

    def get_composite_display_image(self, img_to_show, override_suit=None):
        has_suit = (override_suit is not None) or (hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None)
        active_suit = override_suit if override_suit is not None else getattr(self, 'suit_overlay_image', None)
        cache_key = (id(img_to_show), id(active_suit) if has_suit else None)
        if getattr(self, '_composite_cache_key', None) == cache_key and getattr(self, '_composite_cache_img', None) is not None:
            return self._composite_cache_img

        if has_suit and active_suit is not None:
            try:
                if active_suit.size != img_to_show.size:
                    suit_matched = active_suit.resize(img_to_show.size, Image.Resampling.BILINEAR)
                else:
                    suit_matched = active_suit
                base_rgba = img_to_show.convert('RGBA')
                comp = Image.alpha_composite(base_rgba, suit_matched).convert('RGB')
            except Exception:
                comp = img_to_show.convert('RGB')
        else:
            comp = img_to_show.convert('RGB')

        self._composite_cache_key = cache_key
        self._composite_cache_img = comp
        return comp

    def schedule_canvas_update(self):
        if not getattr(self, '_canvas_update_scheduled', False):
            self._canvas_update_scheduled = True
            self.after(16, self._perform_scheduled_canvas_update)

    def _perform_scheduled_canvas_update(self):
        self._canvas_update_scheduled = False
        self.update_canvas_display()

    def update_canvas_display(self, preview_mode=False, use_makeup=False, use_rotate=False):
        override_suit = None
        is_eraser_active = getattr(self, 'eraser_active', False) and getattr(self, 'eraser_cv', None) is not None
        if is_eraser_active:
            img_to_show = None
            ih, iw = self.eraser_cv.shape[:2]
        elif preview_mode and use_rotate and getattr(self, '_rotate_temp_disp', None) is not None:
            img_to_show = self._rotate_temp_disp
            override_suit = getattr(self, '_rotate_temp_suit', None)
            iw, ih = img_to_show.size
        elif preview_mode and use_makeup:
            img_to_show = getattr(self, 'preview_makeup_img', self.processed_image)
            iw, ih = img_to_show.size
        elif preview_mode:
            img_to_show = getattr(self, 'preview_lighting_img', self.processed_image)
            iw, ih = img_to_show.size
        else:
            img_to_show = self.processed_image
            if img_to_show:
                iw, ih = img_to_show.size

        if not is_eraser_active and not img_to_show:
            return None

        if getattr(self, 'empty_text', None) is not None:
            try:
                self.canvas.delete(self.empty_text)
                self.canvas.delete('empty_elem')
                self.empty_text = None
            except Exception:
                pass

        new_w, new_h = (int(iw * self.zoom_level), int(ih * self.zoom_level))
        if new_w < 10 or new_h < 10:
            return None

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            cw, ch = 800, 600

        has_suit = (override_suit is not None) or (hasattr(self, 'suit_overlay_image') and self.suit_overlay_image is not None)
        active_suit = override_suit if override_suit is not None else getattr(self, 'suit_overlay_image', None)

        # Viewport optimization: if image is zoomed larger than canvas viewport, crop only visible portion
        # Prevents allocating massive multi-hundred megabyte bitmaps and eliminates lag on deep zoom and brush drag
        if new_w > cw + 150 or new_h > ch + 150:
            img_cx0 = self.canvas_img_x - new_w / 2.0
            img_cy0 = self.canvas_img_y - new_h / 2.0
            margin = 80
            vis_cx0 = max(-margin, img_cx0)
            vis_cy0 = max(-margin, img_cy0)
            vis_cx1 = min(cw + margin, img_cx0 + new_w)
            vis_cy1 = min(ch + margin, img_cy0 + new_h)

            if vis_cx1 > vis_cx0 and vis_cy1 > vis_cy0:
                src_x0 = max(0, int((vis_cx0 - img_cx0) / self.zoom_level))
                src_y0 = max(0, int((vis_cy0 - img_cy0) / self.zoom_level))
                src_x1 = min(iw, int((vis_cx1 - img_cx0) / self.zoom_level + 1))
                src_y1 = min(ih, int((vis_cy1 - img_cy0) / self.zoom_level + 1))

                if src_x1 > src_x0 and src_y1 > src_y0:
                    if is_eraser_active:
                        sub_base = Image.fromarray(self.eraser_cv[src_y0:src_y1, src_x0:src_x1], 'RGBA')
                    else:
                        sub_base = img_to_show.crop((src_x0, src_y0, src_x1, src_y1))

                    if has_suit and active_suit is not None:
                        sub_suit = active_suit.crop((src_x0, src_y0, src_x1, src_y1))
                        sub_img = Image.alpha_composite(sub_base.convert('RGBA'), sub_suit).convert('RGB')
                    else:
                        sub_img = sub_base.convert('RGB')

                    target_w = max(1, int((src_x1 - src_x0) * self.zoom_level))
                    target_h = max(1, int((src_y1 - src_y0) * self.zoom_level))
                    resized = sub_img.resize((target_w, target_h), Image.Resampling.BILINEAR)
                    self.tk_image = ImageTk.PhotoImage(resized)

                    sub_center_x = img_cx0 + (src_x0 + src_x1) * 0.5 * self.zoom_level
                    sub_center_y = img_cy0 + (src_y0 + src_y1) * 0.5 * self.zoom_level

                    if self.canvas.find_withtag('img_item'):
                        self.canvas.itemconfig('img_item', image=self.tk_image)
                        self.canvas.coords('img_item', sub_center_x, sub_center_y)
                    else:
                        self.canvas.delete('img_item')
                        self.canvas.create_image(sub_center_x, sub_center_y, image=self.tk_image, anchor='center', tags='img_item')

                    self._viewport_clipped = True
                    return

        self._viewport_clipped = False
        if is_eraser_active and not has_suit:
            resized_cv = cv2.resize(self.eraser_cv, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            self.tk_image = ImageTk.PhotoImage(Image.fromarray(resized_cv, 'RGBA'))
        else:
            if is_eraser_active:
                img_to_show = Image.fromarray(self.eraser_cv)
            composite_img = self.get_composite_display_image(img_to_show, override_suit=override_suit)

            resized = composite_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            self.tk_image = ImageTk.PhotoImage(resized)

        if self.canvas.find_withtag('img_item'):
            self.canvas.itemconfig('img_item', image=self.tk_image)
            self.canvas.coords('img_item', self.canvas_img_x, self.canvas_img_y)
        else:
            self.canvas.delete('img_item')
            self.canvas.create_image(self.canvas_img_x, self.canvas_img_y, image=self.tk_image, anchor='center', tags='img_item')

        if getattr(self, 'healing_active', False) or getattr(self, 'lips_brush_active', False) or getattr(self, 'eraser_active', False) or getattr(self, 'liquify_active', False):
            self.canvas.tag_raise('brush_outline')

    def fit_image(self):
        if not self.processed_image:
            return
        self.canvas.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = self.processed_image.size
        self.zoom_level = min(cw / iw, ch / ih) * 0.95
        self.canvas_img_x = cw // 2
        self.canvas_img_y = ch // 2
        self.update_canvas_display()

    def zoom(self, event):
        if not self.processed_image:
            return
        factor = 1.15 if event.delta > 0 else 0.85
        new_zoom = max(0.05, min(8.0, self.zoom_level * factor))
        if abs(new_zoom - self.zoom_level) < 1e-5:
            return
        actual_factor = new_zoom / self.zoom_level
        self.canvas_img_x = int(event.x - (event.x - self.canvas_img_x) * actual_factor)
        self.canvas_img_y = int(event.y - (event.y - self.canvas_img_y) * actual_factor)
        self.zoom_level = new_zoom

        import time
        now = time.time()
        last_t = getattr(self, '_last_zoom_render_time', 0.0)
        if now - last_t > 0.025:
            self._last_zoom_render_time = now
            if hasattr(self, '_zoom_after_id') and self._zoom_after_id:
                self.after_cancel(self._zoom_after_id)
                self._zoom_after_id = None
            self._do_zoom_render()
        else:
            if hasattr(self, '_zoom_after_id') and self._zoom_after_id:
                self.after_cancel(self._zoom_after_id)
            self._zoom_after_id = self.after(16, self._do_zoom_render)

    def _do_zoom_render(self):
        self._zoom_after_id = None
        self.update_canvas_display()
        if getattr(self, 'healing_active', False) or getattr(self, 'lips_brush_active', False) or getattr(self, 'eraser_active', False) or getattr(self, 'liquify_active', False):
            self.draw_brush_cursor(getattr(self, 'current_mouse_x', 0), getattr(self, 'current_mouse_y', 0))
    def open_wardrobe(self):
        suit_win = ctk.CTkToplevel(self)
        suit_win.title('ជ្រើសរើសអាវធំ (Wardrobe)')
        suit_win.transient(self)
        suit_win.attributes('-topmost', True)
        w, h = (650, 550)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int(sw / 2 - w / 2)
        y = int(sh / 2 - h / 2)
        suit_win.geometry(f'{w}x{h}+{x}+{y}')
        suit_win.grab_set()

        def on_wardrobe_close():
            try:
                suit_win.grab_release()
            except Exception:
                pass
            try:
                suit_win.attributes('-topmost', False)
            except Exception:
                pass
            suit_win.withdraw()
            suit_win.destroy()
            self.force_foreground()
            self.after(50, self.force_foreground)
            self.after(150, self.force_foreground)

        suit_win.protocol("WM_DELETE_WINDOW", on_wardrobe_close)
        khmer_font = ctk.CTkFont(family='Khmer OS Battambang', size=14)
        tabview = ctk.CTkTabview(suit_win)
        tabview.pack(fill='both', expand=True, padx=10, pady=10)
        try:
            tabview._segmented_button.configure(font=khmer_font)
        except:
            pass
        tab_men = tabview.add('បុរស (Men)')
        tab_women = tabview.add('ស្ត្រី (Women)')
        tab_upload = tabview.add('បន្ថែមអាវ (Upload)')
        def load_suits(tab_frame, folder_name):
            for widget in tab_frame.winfo_children():
                widget.destroy()
            suit_base = resource_path('Suits')
            if not os.path.exists(suit_base):
                suit_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Suits')
            suit_folder = os.path.join(suit_base, folder_name)
            os.makedirs(suit_folder, exist_ok=True)
            state = {'delete_mode': False}
            if folder_name == 'Upload':
                bottom_frame = ctk.CTkFrame(tab_frame, fg_color='transparent')
                bottom_frame.pack(side='bottom', pady=(5, 10))
                def upload_new_suit():
                    file_path = filedialog.askopenfilename(title='ជ្រើសរើសរូបអាវ (PNG)', filetypes=[('PNG Files', '*.png')])
                    if file_path:
                        filename = os.path.basename(file_path)
                        dest_path = os.path.join(suit_folder, filename)
                        try:
                            shutil.copy(file_path, dest_path)
                            load_suits(tab_frame, folder_name)
                        except Exception as e:
                            print('Error uploading:', e)
                def toggle_delete():
                    if not state['delete_mode']:
                        state['delete_mode'] = True
                        btn_delete.configure(text='ត្រឡប់វិញ (Cancel)', fg_color='#95A5A6', hover_color='#7F8C8D')
                        btn_upload.configure(state='disabled')
                    else:
                        state['delete_mode'] = False
                        btn_delete.configure(text='🗑️ លុបអាវ (Delete)', fg_color='#E74C3C', hover_color='#C0392B')
                        btn_upload.configure(state='normal')
                btn_upload = ctk.CTkButton(bottom_frame, text='+ បន្ថែមអាវ (Upload)', font=khmer_font, height=35, fg_color='#27AE60', hover_color='#1E8449', command=upload_new_suit)
                btn_upload.pack(side='left', padx=5)
                btn_delete = ctk.CTkButton(bottom_frame, text='🗑️ លុបអាវ (Delete)', font=khmer_font, height=35, fg_color='#E74C3C', hover_color='#C0392B', command=toggle_delete)
                btn_delete.pack(side='left', padx=5)
            scroll_frame = ctk.CTkScrollableFrame(tab_frame)
            scroll_frame.pack(side='top', fill='both', expand=True)
            def on_suit_click(img_path):
                if state.get('delete_mode', False):
                    confirm = messagebox.askyesno('បញ្ជាក់ការលុប', 'តើបងពិតជាចង់លុបរូបអាវនេះមែនទេ?')
                    if confirm:
                        try:
                            os.remove(img_path)
                            load_suits(tab_frame, folder_name)
                        except Exception as e:
                            print('Error deleting:', e)
                else:
                    try:
                        suit_win.grab_release()
                    except Exception:
                        pass
                    try:
                        suit_win.attributes('-topmost', False)
                    except Exception:
                        pass
                    suit_win.withdraw()
                    suit_win.destroy()
                    self.add_suit_to_canvas(img_path)
            row, col = (0, 0)
            if os.path.exists(suit_folder):
                for file in os.listdir(suit_folder):
                    if file.lower().endswith('.png'):
                        img_path = os.path.join(suit_folder, file)
                        try:
                            pil_img = Image.open(img_path)
                            suit_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                            btn = ctk.CTkButton(
                                scroll_frame,
                                image=suit_img,
                                text='',
                                width=110,
                                height=110,
                                fg_color='transparent',
                                hover_color='#334155',
                                command=lambda p=img_path: on_suit_click(p)
                            )
                            btn.grid(row=row, column=col, padx=10, pady=10)
                            col += 1
                            if col > 3:
                                col = 0
                                row += 1
                        except Exception as e:
                            print('Error loading suit:', e)
        load_suits(tab_men, 'Men')
        load_suits(tab_women, 'Women')
        load_suits(tab_upload, 'Upload')
    def remove_suit_layer(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title('បញ្ជាក់ការលុប')
        dialog.transient(self)
        dialog.attributes('-topmost', True)
        dialog.geometry('400x200')
        dialog.grab_set()
        dialog.update_idletasks()
        x = self.winfo_x() + self.winfo_width() // 2 - 200
        y = self.winfo_y() + self.winfo_height() // 2 - 100
        dialog.geometry(f'+{x}+{y}')
        lbl = ctk.CTkLabel(dialog, text='តើអ្នកពិតជាចង់ដកអាវចេញមែនទេ?', font=getattr(self, 'font_text', ('Khmer OS Battambang', 14)))
        lbl.pack(pady=(40, 20))
        user_choice = [False]
        def on_yes():
            user_choice[0] = True
            dialog.destroy()
        def on_no():
            user_choice[0] = False
            dialog.destroy()
        btn_frame = ctk.CTkFrame(dialog, fg_color='transparent')
        btn_frame.pack()
        btn_yes = ctk.CTkButton(btn_frame, text='បាទ/ចាស', font=getattr(self, 'font_btn', ('Khmer OS Battambang', 14, 'bold')), fg_color='#E74C3C', hover_color='#C0392B', width=120, command=on_yes)
        btn_yes.pack(side='left', padx=10)
        btn_no = ctk.CTkButton(btn_frame, text='ទេ', font=getattr(self, 'font_btn', ('Khmer OS Battambang', 14, 'bold')), fg_color='#7F8C8D', hover_color='#95A5A6', width=120, command=on_no)
        btn_no.pack(side='left', padx=10)
        self.wait_window(dialog)
        self.force_foreground()
        self.after(50, self.force_foreground)
        if not user_choice[0]:
            return
        else:
            try:
                self.suit_overlay_image = None
                if hasattr(self, 'image_before_suit') and self.image_before_suit is not None:
                        self.processed_image = self.image_before_suit.copy()
                if hasattr(self, 'btn_remove_suit'):
                    self.btn_remove_suit.pack_forget()
                self._composite_cache_key = None
                self._composite_cache_img = None
                self.update_canvas_display()
            except Exception as e:
                print(f'⚠️ មានបញ្ហាពេលដកអាវចេញ ៖ {e}')
    def add_suit_to_canvas(self, suit_path):
        if not self.ensure_license_active("បំពាក់អាវធំ (Suit Overlay)"):
            return
        from PIL import Image, ImageTk, ImageFilter, ImageDraw
        import cv2
        import numpy as np
        import os
        import urllib.request
        from tkinter import messagebox
        import customtkinter as ctk
        import tkinter as tk
        if getattr(self, 'processed_image', None) is None:
            messagebox.showwarning('បញ្ហា', 'សូមបញ្ចូលរូបថតអតិថិជនជាមុនសិន!')
            return
        else:
            suit_original = Image.open(suit_path).convert('RGBA')
            bbox = suit_original.getbbox()
            if bbox:
                suit_original = suit_original.crop(bbox)
            undo_stack = []
            redo_stack = []
            base_img = self.processed_image.convert('RGBA')
            img_w, img_h = base_img.size
            cascade_file = 'haarcascade_frontalface_default.xml'
            if not os.path.exists(cascade_file):
                try:
                    url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
                    urllib.request.urlretrieve(url, cascade_file)
                except:
                    pass
            init_scale = 1.0
            init_x = img_w // 2
            init_y = img_h - suit_original.height // 2
            if os.path.exists(cascade_file):
                face_cascade = cv2.CascadeClassifier(cascade_file)
                gray = cv2.cvtColor(np.array(base_img.convert('RGB'))[:, :, ::(-1)], cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(int(img_w * 0.15), int(img_h * 0.15)))
                if len(faces) > 0:
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    fx, fy, fw, fh = faces[0]
                    target_suit_w = int(fw * 2.8)
                    init_scale = target_suit_w / suit_original.width
                    init_x = fx + fw // 2
                    init_y = fy + fh + int(suit_original.height * init_scale * 0.05)
            fit_win = ctk.CTkToplevel(self)
            fit_win.title('បន្ទប់តម្រឹមអាវធំ កម្រិត PRO (Layer + Zoom + Drag + Eraser + Undo/Redo)')
            fit_win.transient(self)
            fit_win.attributes('-topmost', True)
            w, h = (1100, 800)
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x_pos = int(sw / 2 - w / 2)
            y_pos = int(sh / 2 - h / 2)
            fit_win.geometry(f'{w}x{h}+{x_pos}+{y_pos}')
            fit_win.grab_set()
            ctrl = ctk.CTkFrame(fit_win, width=350)
            ctrl.pack(side='right', fill='y', padx=10, pady=10)
            ctk.CTkLabel(ctrl, text='🔧 បញ្ជាអាវធំ (អូស និង Zoom លើរូបបាន)', font=getattr(self, 'font_bold', None)).pack(pady=20)
            lbl_scale = ctk.CTkLabel(ctrl, text='🔍 ពង្រីក / បង្រួម (Scale): 100%', font=getattr(self, 'font_text', None))
            lbl_scale.pack(pady=(10, 0))
            sl_scale = ctk.CTkSlider(ctrl, from_=0.1, to=10.0, number_of_steps=400)
            sl_scale.set(init_scale)
            sl_scale.pack(pady=5, padx=20)
            lbl_x = ctk.CTkLabel(ctrl, text='ឆ្វេង / ស្តាំ: 0', font=getattr(self, 'font_text', None))
            lbl_x.pack(pady=(10, 0))
            sl_x = ctk.CTkSlider(ctrl, from_=-img_w, to=img_w * 2, number_of_steps=400)
            sl_x.set(init_x)
            sl_x.pack(pady=5, padx=20)
            lbl_y = ctk.CTkLabel(ctrl, text='លើ / ក្រោម: 0', font=getattr(self, 'font_text', None))
            lbl_y.pack(pady=(10, 0))
            sl_y = ctk.CTkSlider(ctrl, from_=-img_h, to=img_h * 2, number_of_steps=400)
            sl_y.set(init_y)
            sl_y.pack(pady=5, padx=20)
            tools_frame = ctk.CTkFrame(ctrl, fg_color='transparent')
            tools_frame.pack(pady=(20, 0))
            ctk.CTkLabel(tools_frame, text='Tools លុប និងកែទម្រង់អាវ', font=getattr(self, 'font_bold', None)).pack(pady=(0, 10))
            icons_frame = ctk.CTkFrame(tools_frame, fg_color='transparent')
            icons_frame.pack()
            try:
                img_eraser = ctk.CTkImage(light_image=Image.open(resource_path('eraser.png')), size=(24, 24))
                img_liquify = ctk.CTkImage(light_image=Image.open(resource_path('liquify.png')), size=(24, 24))
            except:
                img_eraser = None
                img_liquify = None
            btn_eraser_tool = ctk.CTkButton(icons_frame, text='' if img_eraser else '🧹', image=img_eraser, width=40, height=40, fg_color='#34495E', hover_color='#2C3E50')
            btn_eraser_tool.pack(side='left', padx=10)
            btn_liquify_tool = ctk.CTkButton(icons_frame, text='' if img_liquify else '🌪️', image=img_liquify, width=40, height=40, fg_color='#34495E', hover_color='#2C3E50')
            btn_liquify_tool.pack(side='left', padx=10)
            ur_frame = ctk.CTkFrame(tools_frame, fg_color='transparent')
            ur_frame.pack(pady=(10, 0))
            btn_undo = ctk.CTkButton(ur_frame, text='⟲ Undo', width=60, font=getattr(self, 'font_text', None), fg_color='#7F8C8D', hover_color='#95A5A6', state='disabled')
            btn_undo.pack(side='left', padx=5)
            btn_redo = ctk.CTkButton(ur_frame, text='⟳ Redo', width=60, font=getattr(self, 'font_text', None), fg_color='#7F8C8D', hover_color='#95A5A6', state='disabled')
            btn_redo.pack(side='left', padx=5)
            sliders_frame = ctk.CTkFrame(tools_frame, fg_color='transparent')
            sliders_frame.pack(pady=(15, 0))
            brush_frame = ctk.CTkFrame(sliders_frame, fg_color='transparent')
            brush_frame.pack(side='left', padx=10)
            ctk.CTkLabel(brush_frame, text='Brush Size', font=getattr(self, 'font_text', None), text_color='#BDC3C7').pack(pady=(0, 5))
            sl_brush = ctk.CTkSlider(brush_frame, width=100, from_=1, to=100)
            sl_brush.set(30)
            sl_brush.pack()
            hard_frame = ctk.CTkFrame(sliders_frame, fg_color='transparent')
            hard_frame.pack(side='left', padx=10)
            ctk.CTkLabel(hard_frame, text='Hardness Size', font=getattr(self, 'font_text', None), text_color='#BDC3C7').pack(pady=(0, 5))
            sl_hard = ctk.CTkSlider(hard_frame, width=100, from_=0, to=100)
            sl_hard.set(50)
            sl_hard.pack()
            info_txt = 'ចំណាំ៖\n១. ប្រើ កង់រមូរ (Scroll) ដើម្បី Zoom\n២. សារ៉េទំហំអាវដោយយក ក អាវ ជាគោល\n៣. ចុច \"យល់ព្រម\" ខាងក្រោម ដើម្បីកំណត់\n៤. អាវដែលលៀនមកក្រៅ អាចលុបបានតាមក្រោយ'
            ctk.CTkLabel(ctrl, text=info_txt, font=getattr(self, 'font_text', None), text_color='#F39C12', justify='left').pack(pady=20, padx=20)
            canvas_frame = tk.Frame(fit_win, bg='#1a1a1a')
            canvas_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            fit_canvas = tk.Canvas(canvas_frame, bg='#2C3E50', highlightthickness=0)
            fit_canvas.pack(expand=True, fill='both')
            fit_win.update_idletasks()
            cw, ch = (fit_canvas.winfo_width(), fit_canvas.winfo_height())
            if cw <= 1:
                cw, ch = (700, 750)
            state = {
                'zoom': min(cw / img_w, ch / img_h) * 0.9,
                'pan_x': cw // 2,
                'pan_y': ch // 2,
                'suit_s': init_scale,
                'suit_x': init_x,
                'suit_y': init_y,
                'drag_x': 0,
                'drag_y': 0,
                'mouse_x': 0,
                'mouse_y': 0,
                'base_tk': None,
                'suit_tk': None,
                'is_dragging_pan': False,
                'active_tool': 'move',
                '_last_zoom_time': 0.0,
                'base_clipped': False,
                'suit_clipped': False,
                '_pan_acc_x': 0,
                '_pan_acc_y': 0
            }

            def update_ur_btns():
                btn_undo.configure(state='normal' if len(undo_stack) > 0 else 'disabled', fg_color='#E67E22' if len(undo_stack) > 0 else '#7F8C8D')
                btn_redo.configure(state='normal' if len(redo_stack) > 0 else 'disabled', fg_color='#2980B9' if len(redo_stack) > 0 else '#7F8C8D')

            def save_history():
                undo_stack.append(suit_original.copy())
                if len(undo_stack) > 50:
                    undo_stack.pop(0)
                redo_stack.clear()
                update_ur_btns()

            def perform_undo():
                nonlocal suit_original
                if undo_stack:
                    redo_stack.append(suit_original.copy())
                    suit_original = undo_stack.pop()
                    update_suit_tk()
                    update_ur_btns()

            def perform_redo():
                nonlocal suit_original
                if redo_stack:
                    undo_stack.append(suit_original.copy())
                    suit_original = redo_stack.pop()
                    update_suit_tk()
                    update_ur_btns()

            btn_undo.configure(command=perform_undo)
            btn_redo.configure(command=perform_redo)
            def on_fit_key(event):
                widget = getattr(event, 'widget', None)
                if widget is not None:
                    try:
                        w_class = widget.winfo_class()
                        if w_class in ('Entry', 'Text', 'TEntry') or isinstance(widget, (tk.Entry, tk.Text)):
                            return
                    except Exception:
                        pass
                is_ctrl = bool(event.state & 4) or bool(event.state & 0x20000)
                is_shift = bool(event.state & 1)
                kc = getattr(event, 'keycode', 0)
                ks = (getattr(event, 'keysym', '') or '').lower()
                if is_ctrl:
                    if kc == 90 or ks == 'z':
                        if is_shift:
                            perform_redo()
                        else:
                            perform_undo()
                        return 'break'
                    elif kc in (89, 82) or ks in ('y', 'r'):
                        perform_redo()
                        return 'break'

            for w in (fit_win, fit_canvas):
                w.bind('<KeyPress>', on_fit_key)
                for seq in ('<Control-z>', '<Control-Z>', '<Control-Key-z>', '<Control-Key-Z>'):
                    w.bind(seq, lambda e: perform_undo())
                for seq in ('<Control-y>', '<Control-Y>', '<Control-Key-y>', '<Control-Key-Y>', '<Control-r>', '<Control-R>', '<Control-Shift-Z>', '<Control-Shift-z>'):
                    w.bind(seq, lambda e: perform_redo())

            def toggle_tool(tool_name):
                if state['active_tool'] == tool_name:
                    state['active_tool'] = 'move'
                else:
                    state['active_tool'] = tool_name
                btn_eraser_tool.configure(fg_color='#E74C3C' if state['active_tool'] == 'erase' else '#34495E')
                btn_liquify_tool.configure(fg_color='#E74C3C' if state['active_tool'] == 'liquify' else '#34495E')
                if state['active_tool'] in ['erase', 'liquify']:
                    fit_canvas.configure(cursor='none')
                    fit_canvas.itemconfig('brush_cursor', state='normal')
                else:
                    fit_canvas.configure(cursor='fleur')
                    fit_canvas.itemconfig('brush_cursor', state='hidden')

            btn_eraser_tool.configure(command=lambda: toggle_tool('erase'))
            btn_liquify_tool.configure(command=lambda: toggle_tool('liquify'))

            import time

            def get_canvas_size():
                cw = fit_canvas.winfo_width()
                ch = fit_canvas.winfo_height()
                if cw <= 10 or ch <= 10:
                    cw = max(state.get('cw', 700), 700)
                    ch = max(state.get('ch', 750), 750)
                else:
                    state['cw'] = cw
                    state['ch'] = ch
                return cw, ch

            def update_base_tk():
                cw, ch = get_canvas_size()
                zoom = state['zoom']
                bw = int(img_w * zoom)
                bh = int(img_h * zoom)
                base_tl_x = state['pan_x'] - bw // 2
                base_tl_y = state['pan_y'] - bh // 2
                base_br_x = base_tl_x + bw
                base_br_y = base_tl_y + bh

                margin = 80
                # Viewport cropping when image is larger than canvas viewport
                if (bw > cw + margin or bh > ch + margin) and (base_br_x > -margin and base_tl_x < cw + margin and base_br_y > -margin and base_tl_y < ch + margin):
                    vis_x0 = max(base_tl_x, -margin)
                    vis_y0 = max(base_tl_y, -margin)
                    vis_x1 = min(base_br_x, cw + margin)
                    vis_y1 = min(base_br_y, ch + margin)

                    src_x0 = max(0, min(img_w, int(round((vis_x0 - base_tl_x) / zoom))))
                    src_y0 = max(0, min(img_h, int(round((vis_y0 - base_tl_y) / zoom))))
                    src_x1 = max(0, min(img_w, int(round((vis_x1 - base_tl_x) / zoom))))
                    src_y1 = max(0, min(img_h, int(round((vis_y1 - base_tl_y) / zoom))))

                    if src_x1 > src_x0 and src_y1 > src_y0:
                        crop_w = max(1, int((src_x1 - src_x0) * zoom))
                        crop_h = max(1, int((src_y1 - src_y0) * zoom))
                        cropped_base = base_img.crop((src_x0, src_y0, src_x1, src_y1)).resize((crop_w, crop_h), Image.Resampling.BILINEAR)
                        state['base_tk'] = ImageTk.PhotoImage(cropped_base)
                        draw_x = base_tl_x + int(src_x0 * zoom)
                        draw_y = base_tl_y + int(src_y0 * zoom)
                        fit_canvas.itemconfig('bg', image=state['base_tk'])
                        fit_canvas.coords('bg', draw_x, draw_y)
                        state['base_clipped'] = True
                        return

                if bw > 5 and bh > 5:
                    base_resized = base_img.resize((bw, bh), Image.Resampling.BILINEAR)
                    state['base_tk'] = ImageTk.PhotoImage(base_resized)
                    fit_canvas.itemconfig('bg', image=state['base_tk'])
                    fit_canvas.coords('bg', base_tl_x, base_tl_y)
                state['base_clipped'] = False

            def update_suit_tk():
                cw, ch = get_canvas_size()
                zoom = state['zoom']
                s = state['suit_s']
                sw = int(suit_original.width * s * zoom)
                sh = int(suit_original.height * s * zoom)
                bw = int(img_w * zoom)
                bh = int(img_h * zoom)
                base_tl_x = state['pan_x'] - bw // 2
                base_tl_y = state['pan_y'] - bh // 2
                suit_center_x = base_tl_x + int(state['suit_x'] * zoom)
                suit_center_y = base_tl_y + int(state['suit_y'] * zoom)
                suit_tl_x = suit_center_x - sw // 2
                suit_tl_y = suit_center_y - sh // 2
                suit_br_x = suit_tl_x + sw
                suit_br_y = suit_tl_y + sh

                margin = 80
                suit_scale_ratio = s * zoom
                if (sw > cw + margin or sh > ch + margin) and suit_scale_ratio > 0 and (suit_br_x > -margin and suit_tl_x < cw + margin and suit_br_y > -margin and suit_tl_y < ch + margin):
                    s_vis_x0 = max(suit_tl_x, -margin)
                    s_vis_y0 = max(suit_tl_y, -margin)
                    s_vis_x1 = min(suit_br_x, cw + margin)
                    s_vis_y1 = min(suit_br_y, ch + margin)

                    s_src_x0 = max(0, min(suit_original.width, int(round((s_vis_x0 - suit_tl_x) / suit_scale_ratio))))
                    s_src_y0 = max(0, min(suit_original.height, int(round((s_vis_y0 - suit_tl_y) / suit_scale_ratio))))
                    s_src_x1 = max(0, min(suit_original.width, int(round((s_vis_x1 - suit_tl_x) / suit_scale_ratio))))
                    s_src_y1 = max(0, min(suit_original.height, int(round((s_vis_y1 - suit_tl_y) / suit_scale_ratio))))

                    if s_src_x1 > s_src_x0 and s_src_y1 > s_src_y0:
                        s_crop_w = max(1, int((s_src_x1 - s_src_x0) * suit_scale_ratio))
                        s_crop_h = max(1, int((s_src_y1 - s_src_y0) * suit_scale_ratio))
                        cropped_suit = suit_original.crop((s_src_x0, s_src_y0, s_src_x1, s_src_y1)).resize((s_crop_w, s_crop_h), Image.Resampling.BILINEAR)
                        state['suit_tk'] = ImageTk.PhotoImage(cropped_suit)
                        s_draw_x = suit_tl_x + int(s_src_x0 * suit_scale_ratio)
                        s_draw_y = suit_tl_y + int(s_src_y0 * suit_scale_ratio)
                        fit_canvas.itemconfig('suit', image=state['suit_tk'])
                        fit_canvas.coords('suit', s_draw_x, s_draw_y)
                        state['suit_clipped'] = True
                        return

                if sw > 5 and sh > 5:
                    suit_resized = suit_original.resize((sw, sh), Image.Resampling.BILINEAR)
                    state['suit_tk'] = ImageTk.PhotoImage(suit_resized)
                    fit_canvas.itemconfig('suit', image=state['suit_tk'])
                    fit_canvas.coords('suit', suit_tl_x, suit_tl_y)
                state['suit_clipped'] = False

            def render_fit_canvas():
                update_base_tk()
                update_suit_tk()
                fit_canvas.tag_raise('suit', 'bg')
                fit_canvas.tag_raise('brush_cursor')

            def update_positions(raise_tags=False):
                if state.get('base_clipped', False) or state.get('suit_clipped', False):
                    render_fit_canvas()
                else:
                    bw = int(img_w * state['zoom'])
                    bh = int(img_h * state['zoom'])
                    base_tl_x = state['pan_x'] - bw // 2
                    base_tl_y = state['pan_y'] - bh // 2
                    fit_canvas.coords('bg', base_tl_x, base_tl_y)

                    s = state['suit_s']
                    sw = int(suit_original.width * s * state['zoom'])
                    sh = int(suit_original.height * s * state['zoom'])
                    suit_center_x = base_tl_x + int(state['suit_x'] * state['zoom'])
                    suit_center_y = base_tl_y + int(state['suit_y'] * state['zoom'])
                    suit_tl_x = suit_center_x - sw // 2
                    suit_tl_y = suit_center_y - sh // 2
                    fit_canvas.coords('suit', suit_tl_x, suit_tl_y)

                if raise_tags:
                    fit_canvas.tag_raise('suit', 'bg')
                    fit_canvas.tag_raise('brush_cursor')

            def update_labels():
                display_scale = int(state['suit_s'] / 10.0 * 100)
                lbl_scale.configure(text=f'🔍 ពង្រីក / បង្រួម (Scale): {display_scale}%')
                x_percent = int((state['suit_x'] - init_x) / img_w * 100)
                y_percent = int((state['suit_y'] - init_y) / img_h * 100)
                lbl_x.configure(text=f'ឆ្វេង / ស្តាំ: {x_percent}')
                lbl_y.configure(text=f'លើ / ក្រោម: {y_percent}')

            # Initial rendering setup on canvas
            fit_canvas.create_image(0, 0, anchor='nw', tags='bg')
            fit_canvas.create_image(0, 0, anchor='nw', tags='suit')
            fit_canvas.create_oval(-100, -100, -100, -100, outline='white', dash=(4, 4), tags='brush_cursor', state='hidden')
            render_fit_canvas()
            update_labels()

            def on_slider_scale(*args):
                state['suit_s'] = sl_scale.get()
                update_labels()
                update_suit_tk()

            def on_slider_x(*args):
                state['suit_x'] = sl_x.get()
                update_labels()
                update_suit_tk()

            def on_slider_y(*args):
                state['suit_y'] = sl_y.get()
                update_labels()
                update_suit_tk()

            sl_scale.configure(command=on_slider_scale)
            sl_x.configure(command=on_slider_x)
            sl_y.configure(command=on_slider_y)

            def on_brush_size_change(val):
                if state['active_tool'] in ['erase', 'liquify']:
                    r = float(val)
                    mx, my = (state['mouse_x'], state['mouse_y'])
                    fit_canvas.coords('brush_cursor', mx - r, my - r, mx + r, my + r)

            sl_brush.configure(command=on_brush_size_change)

            def _delayed_fit_zoom_render():
                state['_zoom_job'] = None
                render_fit_canvas()

            def fit_zoom_scroll(e):
                steps = max(-3.0, min(3.0, e.delta / 120.0))
                factor = 1.12 ** steps
                new_zoom = max(0.05, min(25.0, state['zoom'] * factor))
                actual_factor = new_zoom / state['zoom']
                state['zoom'] = new_zoom

                # Zoom centered directly under the mouse pointer
                state['pan_x'] = int(e.x - (e.x - state['pan_x']) * actual_factor)
                state['pan_y'] = int(e.y - (e.y - state['pan_y']) * actual_factor)

                now = time.time()
                # 40 FPS throttled real-time rendering during wheel scrolling (25ms)
                if now - state.get('_last_zoom_time', 0.0) >= 0.025:
                    state['_last_zoom_time'] = now
                    render_fit_canvas()
                else:
                    update_positions(raise_tags=False)

                if state.get('_zoom_job'):
                    try:
                        fit_win.after_cancel(state['_zoom_job'])
                    except Exception:
                        pass
                state['_zoom_job'] = fit_win.after(20, _delayed_fit_zoom_render)

            def fit_press(e):
                try:
                    fit_canvas.focus_set()
                except Exception:
                    pass
                state['drag_x'], state['drag_y'] = (e.x, e.y)
                if state['active_tool'] in ['erase', 'liquify']:
                    save_history()
                s = state['suit_s']
                sw = int(suit_original.width * s * state['zoom'])
                sh = int(suit_original.height * s * state['zoom'])
                bw = int(img_w * state['zoom'])
                bh = int(img_h * state['zoom'])
                base_tl_x = state['pan_x'] - bw // 2
                base_tl_y = state['pan_y'] - bh // 2
                suit_center_x = base_tl_x + int(state['suit_x'] * state['zoom'])
                suit_center_y = base_tl_y + int(state['suit_y'] * state['zoom'])
                left, right = (suit_center_x - sw // 2, suit_center_x + sw // 2)
                top, bottom = (suit_center_y - sh // 2, suit_center_y + sh // 2)
                if left <= e.x <= right and top <= e.y <= bottom:
                    state['is_dragging_pan'] = False
                else:
                    state['is_dragging_pan'] = True

            def fit_motion(e):
                state['mouse_x'], state['mouse_y'] = (e.x, e.y)
                if state['active_tool'] in ['erase', 'liquify']:
                    r = sl_brush.get()
                    fit_canvas.coords('brush_cursor', e.x - r, e.y - r, e.x + r, e.y + r)

            def fit_drag(e):
                dx, dy = (e.x - state['drag_x'], e.y - state['drag_y'])
                state['mouse_x'], state['mouse_y'] = (e.x, e.y)
                if state['active_tool'] in ['erase', 'liquify']:
                    r = sl_brush.get()
                    fit_canvas.coords('brush_cursor', e.x - r, e.y - r, e.x + r, e.y + r)
                s = state['suit_s']
                bw = int(img_w * state['zoom'])
                bh = int(img_h * state['zoom'])
                base_tl_x = state['pan_x'] - bw // 2
                base_tl_y = state['pan_y'] - bh // 2
                px = int(state['suit_x'] * state['zoom']) - int(suit_original.width * s * state['zoom'] // 2)
                py = int(state['suit_y'] * state['zoom']) - int(suit_original.height * s * state['zoom'] // 2)
                suit_rel_x = e.x - base_tl_x - px
                suit_rel_y = e.y - base_tl_y - py
                orig_curr_x = suit_rel_x / (s * state['zoom'])
                orig_curr_y = suit_rel_y / (s * state['zoom'])
                brush_radius = sl_brush.get() / (s * state['zoom'])
                if state['active_tool'] == 'erase':
                    try:
                        from PIL import ImageChops, ImageDraw
                        alpha = suit_original.split()[3]
                        mask = Image.new('L', alpha.size, 255)
                        draw = ImageDraw.Draw(mask)
                        erase_radius = int(sl_brush.get() / (s * state['zoom']))
                        px_erase = int(orig_curr_x)
                        py_erase = int(orig_curr_y)
                        draw.ellipse((px_erase - erase_radius, py_erase - erase_radius, px_erase + erase_radius, py_erase + erase_radius), fill=0)
                        new_alpha = ImageChops.multiply(alpha, mask)
                        suit_original.putalpha(new_alpha)
                        update_suit_tk()
                    except Exception as ex:
                        print('Error ពេលលុបអាវ ៖', ex)
                    state['drag_x'], state['drag_y'] = (e.x, e.y)
                elif state['active_tool'] == 'liquify':
                    try:
                        import cv2
                        import numpy as np
                        prev_x = state['drag_x'] - base_tl_x - px
                        prev_y = state['drag_y'] - base_tl_y - py
                        orig_prev_x = prev_x / (s * state['zoom'])
                        orig_prev_y = prev_y / (s * state['zoom'])
                        disp_x = orig_curr_x - orig_prev_x
                        disp_y = orig_curr_y - orig_prev_y
                        disp_len = math.hypot(disp_x, disp_y)
                        if disp_len >= 0.75:
                            max_disp = brush_radius * 0.45
                            if disp_len > max_disp:
                                scale_factor = max_disp / disp_len
                                disp_x *= scale_factor
                                disp_y *= scale_factor
                            r = max(2, int(brush_radius))
                            r_sq = float(r * r)
                            roi_x1 = max(0, int(orig_prev_x - r))
                            roi_y1 = max(0, int(orig_prev_y - r))
                            roi_x2 = min(suit_original.width, int(orig_prev_x + r + 1))
                            roi_y2 = min(suit_original.height, int(orig_prev_y + r + 1))
                            if roi_x2 > roi_x1 and roi_y2 > roi_y1:
                                roi = suit_original.crop((roi_x1, roi_y1, roi_x2, roi_y2))
                                roi_np = np.array(roi)
                                h_roi, w_roi = roi_np.shape[:2]
                                gx = np.arange(roi_x1, roi_x2, dtype=np.float32) - orig_prev_x
                                gy = np.arange(roi_y1, roi_y2, dtype=np.float32) - orig_prev_y
                                dist_sq = (gx[None, :] ** 2) + (gy[:, None] ** 2)
                                norm_sq = np.clip(dist_sq / r_sq, 0.0, 1.0)
                                weight = (1.0 - norm_sq) ** 3
                                hardness = sl_hard.get() / 100.0
                                if hardness > 0.5:
                                    weight = weight ** (1.0 - (hardness - 0.5) * 0.8)
                                push_factor = 0.55
                                map_X = (np.arange(w_roi, dtype=np.float32)[None, :] - (disp_x * push_factor) * weight).astype(np.float32)
                                map_Y = (np.arange(h_roi, dtype=np.float32)[:, None] - (disp_y * push_factor) * weight).astype(np.float32)
                                warped_roi_np = cv2.remap(roi_np, map_X, map_Y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
                                warped_roi = Image.fromarray(warped_roi_np, 'RGBA')
                                suit_original.paste(warped_roi, (roi_x1, roi_y1))
                                update_suit_tk()
                            state['drag_x'], state['drag_y'] = (e.x, e.y)
                    except Exception as ex:
                        print('Error ពេល Liquify ៖', ex)
                        state['drag_x'], state['drag_y'] = (e.x, e.y)
                else:
                    state['drag_x'], state['drag_y'] = (e.x, e.y)
                    if state['is_dragging_pan']:
                        state['pan_x'] += dx
                        state['pan_y'] += dy
                        fit_canvas.move('bg', dx, dy)
                        fit_canvas.move('suit', dx, dy)
                        state['_pan_acc_x'] += abs(dx)
                        state['_pan_acc_y'] += abs(dy)
                        if state['_pan_acc_x'] > 50 or state['_pan_acc_y'] > 50:
                            state['_pan_acc_x'] = 0
                            state['_pan_acc_y'] = 0
                            render_fit_canvas()
                    else:
                        state['suit_x'] += dx / state['zoom']
                        state['suit_y'] += dy / state['zoom']
                        fit_canvas.move('suit', dx, dy)
                        state['_pan_acc_x'] += abs(dx)
                        state['_pan_acc_y'] += abs(dy)
                        if state['_pan_acc_x'] > 50 or state['_pan_acc_y'] > 50:
                            state['_pan_acc_x'] = 0
                            state['_pan_acc_y'] = 0
                            update_suit_tk()

            def fit_release(e):
                state['_pan_acc_x'] = 0
                state['_pan_acc_y'] = 0
                render_fit_canvas()
                if state.get('active_tool') == 'move':
                    sl_x.set(state['suit_x'])
                    sl_y.set(state['suit_y'])
                    update_labels()

            fit_canvas.bind('<MouseWheel>', fit_zoom_scroll)
            fit_canvas.bind('<Button-4>', lambda e: fit_zoom_scroll(type('Event', (), {'x': e.x, 'y': e.y, 'delta': 120})()))
            fit_canvas.bind('<Button-5>', lambda e: fit_zoom_scroll(type('Event', (), {'x': e.x, 'y': e.y, 'delta': -120})()))
            fit_canvas.bind('<ButtonPress-1>', fit_press)
            fit_canvas.bind('<B1-Motion>', fit_drag)
            fit_canvas.bind('<ButtonRelease-1>', fit_release)
            fit_canvas.bind('<Motion>', fit_motion)

            def apply_suit():
                try:
                    if hasattr(self, 'save_state'):
                        self.save_state()
                    self.image_before_suit = self.processed_image.copy()
                    s, x, y = (state['suit_s'], state['suit_x'], state['suit_y'])
                    new_w, new_h = (int(suit_original.width * s), int(suit_original.height * s))
                    if new_w > 10 and new_h > 10:
                        s_resized = suit_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        px, py = (int(x) - new_w // 2, int(y) - new_h // 2)
                        overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
                        try:
                            blur_amount = max(1, int(new_w * 0.02))
                            drop_offset = max(1, int(new_h * 0.02))
                            shadow_img = Image.new('RGBA', s_resized.size, (0, 0, 0, 255))
                            shadow_img.putalpha(s_resized.split()[3])
                            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
                            shadow_alpha = shadow_img.split()[3].point(lambda p: int(p * 0.85))
                            shadow_img.putalpha(shadow_alpha)
                            overlay.paste(shadow_img, (px, py + drop_offset), mask=shadow_img)
                        except Exception:
                            pass
                        overlay.paste(s_resized, (px, py), mask=s_resized)
                        
                        # Store as separate layer so main workspace Eraser Tool will NOT erase the suit
                        self.suit_overlay_image = overlay
                        if hasattr(self, 'btn_remove_suit'):
                            self.btn_remove_suit.pack(fill='x', padx=8, pady=(0, 6))
                        self.update_canvas_display()
                    try:
                        fit_win.grab_release()
                    except Exception:
                        pass
                    try:
                        fit_win.attributes('-topmost', False)
                    except Exception:
                        pass
                    try:
                        fit_win.withdraw()
                    except Exception:
                        pass
                    try:
                        fit_win.destroy()
                    except Exception:
                        pass
                    self.force_foreground()
                    self.after(50, self.force_foreground)
                    self.after(150, self.force_foreground)
                except Exception as ex:
                    messagebox.showerror('បញ្ហា', f'មានបញ្ហាក្នុងការបំពាក់អាវ៖ {str(ex)}')

            def cancel_suit():
                try:
                    fit_win.grab_release()
                except Exception:
                    pass
                try:
                    fit_win.attributes('-topmost', False)
                except Exception:
                    pass
                fit_win.withdraw()
                fit_win.destroy()
                self.force_foreground()
                self.after(50, self.force_foreground)
                self.after(150, self.force_foreground)

            fit_win.protocol("WM_DELETE_WINDOW", cancel_suit)

            btn_box = ctk.CTkFrame(ctrl, fg_color='transparent')
            btn_box.pack(pady=25, fill='x', padx=15)
            ctk.CTkButton(btn_box, text='✅ យល់ព្រម (Apply)', font=getattr(self, 'font_btn', None), fg_color='#27AE60', hover_color='#1E8449', command=apply_suit, height=42).pack(fill='x', pady=5)
            ctk.CTkButton(btn_box, text='❌ បោះបង់ (Cancel)', font=getattr(self, 'font_btn', None), fg_color='#7F8C8D', hover_color='#95A5A6', command=cancel_suit, height=36).pack(fill='x', pady=5)
    def show_guideline_window(self):
        guide_win = ctk.CTkToplevel(self)
        guide_win.title('ការណែនាំ - Guidelines')
        w, h = (960, 670)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        guide_win.geometry(f'{w}x{h}+{int(sw / 2 - w / 2)}+{int(sh / 2 - h / 2)}')
        guide_win.attributes('-topmost', True)
        guide_win.grab_set()
        guide_win.configure(fg_color='#0A0E17')

        head = ctk.CTkFrame(guide_win, fg_color='#111622', corner_radius=10, border_width=1, border_color='#00F2FE')
        head.pack(fill='x', padx=20, pady=(15, 10))
        ctk.CTkLabel(head, text='📖 ការណែនាំស្តង់ដារថតរូបកាត (Studio Guidelines)', font=('Khmer OS Battambang', 14, 'bold'), text_color='#00F2FE').pack(pady=8)

        img_card = ctk.CTkFrame(guide_win, fg_color='#080B12', corner_radius=12, border_width=1, border_color='#1E293B')
        img_card.pack(fill='both', expand=True, padx=20, pady=5)
        try:
            from PIL import Image
            img_path = resource_path('guideline.jpg')
            img = Image.open(img_path)
            img_w, img_h = img.size
            ratio = min(900 / img_w, 480 / img_h)
            new_w, new_h = (int(img_w * ratio), int(img_h * ratio))
            guide_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
            lbl_img = ctk.CTkLabel(img_card, text='', image=guide_img)
            lbl_img.pack(pady=10)
        except Exception as e:
            ctk.CTkLabel(img_card, text='រកមិនឃើញរូបភាព guideline.jpg ទេ!', text_color='#FF4466').pack(pady=50)

        bottom_frame = ctk.CTkFrame(guide_win, fg_color='transparent')
        bottom_frame.pack(fill='x', padx=20, pady=(10, 15))
        btn_close = ctk.CTkButton(
            bottom_frame, text='បិទ (Close)', font=('Khmer OS Siemreap', 13),
            fg_color='#1E293B', hover_color='#334155', border_width=1, border_color='#475569',
            height=36, corner_radius=8, command=guide_win.destroy, width=120
        )
        btn_close.pack(side='right')

    def open_about_window(self):
        import sys
        import webbrowser
        about_win = ctk.CTkToplevel(self)
        about_win.title('អំពីកម្មវិធី - RN Photography v3.0')
        w, h = (680, 620)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        about_win.geometry(f'{w}x{h}+{int(sw / 2 - w / 2)}+{int(sh / 2 - h / 2)}')
        about_win.attributes('-topmost', True)
        about_win.grab_set()
        about_win.configure(fg_color='#0A0E17')
        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            about_win.iconbitmap(ico_path)
        except Exception:
            pass

        header_card = ctk.CTkFrame(about_win, fg_color='#111622', corner_radius=12, border_width=1, border_color='#00F2FE')
        header_card.pack(fill='x', padx=20, pady=(15, 8))

        ctk.CTkLabel(header_card, text='✦ RN Photography v3.0 ✦', font=('Arial', 22, 'bold'), text_color='#00F2FE').pack(pady=(10, 2))
        ctk.CTkLabel(header_card, text='Next-Gen AI Photo Retouching Suite for Cambodia', font=('Segoe UI', 11), text_color='#94A3B8').pack(pady=(0, 6))

        try:
            pc_id = self.get_hwid()
            is_val, lic_info, info = self.check_license()
            lic_status_text = f"🔐 ស្ថានភាព: {lic_info}   |   💻 PC ID: {pc_id}"
            lic_pill = ctk.CTkFrame(header_card, fg_color='#062D24' if is_val else '#331015', corner_radius=8, border_width=1, border_color='#00F5A0' if is_val else '#EF4444')
            lic_pill.pack(pady=(0, 10), padx=16, fill='x')
            ctk.CTkLabel(lic_pill, text=lic_status_text, font=('Khmer OS Siemreap', 11, 'bold'), text_color='#00FF9D' if is_val else '#F87171').pack(pady=4)
        except Exception:
            pass

        scroll_box = ctk.CTkScrollableFrame(about_win, width=600, height=330, fg_color='#111622', corner_radius=10, border_width=1, border_color='#1E293B')
        scroll_box.pack(padx=20, pady=5, fill='both', expand=True)
        about_text = '💡 គោលបំណង និងការចាប់ផ្តើម (Our Story & Purpose)\nកម្មវិធី RN Photography ត្រូវបានបង្កើតឡើងដោយផ្អើមចេញពីការសង្កេតឃើញនូវការលំបាក និងបញ្ហាប្រឈមរបស់បងប្អូនអាជីវកររោងពុម្ព ក៏ដូចជាអ្នកចាប់ផ្តើមអាជីវកម្មថតរូប ដែលពុំទាន់មានភាពស្ទាត់ជំនាញក្នុងការប្រើប្រាស់កម្មវិធី Photoshop ច្រើនតំណាក់កាល។\n\nយើងយល់ច្បាស់ថា ពេលវេលាគឺជាមាសប្រាក់! ហេតុនេះហើយ ទើប RN Photography បង្ហាញខ្លួនឡើងក្នុងគោលដៅតែមួយគត់ គឺ "កែប្រែភាពស្មុគស្មាញ ឲ្យក្លាយជាភាពងាយស្រួលបំផុត"។ កម្មវិធីនេះដើរតួនាទីជាជំនួយការដ៏ចំណាន ក្នុងការកាត់តរូបថតកាត (៣x៤ និង ៤x៦) តាមស្តង់ដារស្ទូឌីយោ ដោយគ្រាន់តែប្រើចុងម្រាមដៃ មិនទាមទារចំណេះដឹងផ្នែក កាត់តជ្រៅជ្រះឡើយ។\n\n🚀 មុខងារស្នូលដែលយើងមានមោទនភាព (Key Features)\n• ដំណើរការ Offline 100% ៖ រក្សាឯកជនភាពអតិថិជនបានខ្ពស់ ទោះគ្មានសេវាអ៊ីនធឺណិតក៏ដោយ។\n• បច្ចេកវិទ្យា "ចុចចេញៗ" (One-Click Magic) ៖ សន្សំសំចៃពេលវេលាខ្ពស់ បញ្ជាលឿន រហ័ស និងទទួលបានលទ្ធផលភ្លាមៗ មិនបាច់រង់ចាំយូរ។\n• ប្រើប្រាស់បាន ២ ទម្រង់ ៖ អាចដំណើរការជាកម្មវិធីដាច់ដោយឡែក (Standalone Application) ឬជា Plugin បញ្ចូលប្រើផ្ទាល់នៅក្នុង Photoshop តែម្តង។\n• បច្ចេកវិទ្យា AI ដ៏ឆ្លាតវៃ ៖ រួមបញ្ចូលមុខងារ AI ជួសជុលស្បែកមុខ, AI Enhance, និងធ្វើឲ្យស្បែករលោង (Smooth Skin) ដែលរក្សាទម្រង់ដើមបានល្អឥតខ្ចោះ។\n• កាត់ប្តូរផ្ទៃខាងក្រោយរហ័ស ៖ ផ្លាស់ប្តូរ Background ទៅជាពណ៌ខៀវ ពណ៌ស ឬពណ៌ស្តង់ដារផ្សេងៗដោយស្វ័យប្រវត្តិ។\n• បំពាក់អាវធំឌីជីថល ៖ មានប្រព័ន្ធសារ៉េ និងបំពាក់អាវធំ (Suit Overlay) យ៉ាងសមសួន និងមានភាពរស់រវើក។\n\n👁️‍🗨️ ចក្ខុវិស័យ (Our Vision)\nយើងមានចក្ខុវិស័យចង់ឃើញ RN Photography ក្លាយជាកម្មវិធីស្តង់ដារមួយ ដែលត្រូវបានចែកចាយ និងប្រើប្រាស់យ៉ាងទូលំទូលាយទូទាំងប្រទេសកម្ពុជា។ យើងនឹងបន្តដើរស្របគ្នាជាមួយនឹងការរីកចម្រើននៃប្រព័ន្ធបច្ចេកវិទ្យា AI ដើម្បីអភិវឌ្ឍកម្មវិធីនេះឲ្យកាន់តែមានភាពទំនើប ជួយពន្លឿនការងាររបស់ប្រជាជនខ្មែរឲ្យកាន់តែប្រសើរឡើង។\n\n👨‍💻 កម្មសិទ្ធិបញ្ញា និងអ្នកអភិវឌ្ឍន៍ (Copyright & Developer)\n• ស្ថាបនិក និងអ្នកអភិវឌ្ឍន៍ ៖ លោក ឃីន រតនា (KHIN RATANA)\n• កម្មសិទ្ធិដោយ ៖ RN Printing\n• រក្សាសិទ្ធិគ្រប់យ៉ាង © ឆ្នាំ២០២៦។'
        lbl_text = ctk.CTkLabel(scroll_box, text=about_text, font=('Khmer OS Siemreap', 13), text_color='#ECF0F1', justify='left', wraplength=560)
        lbl_text.pack(padx=12, pady=10, anchor='w')

        btn_row = ctk.CTkFrame(about_win, fg_color='transparent')
        btn_row.pack(fill='x', padx=20, pady=12)

        def open_telegram():
            webbrowser.open('https://t.me/Ratana_Printing')
        btn_telegram = ctk.CTkButton(
            btn_row, text='✈️ ទំនាក់ទំនង Telegram: @Ratana_Printing',
            font=('Khmer OS Siemreap', 13, 'bold'),
            fg_color='#0284C7', hover_color='#0369A1',
            border_width=1, border_color='#38BDF8',
            height=38, corner_radius=8, command=open_telegram
        )
        btn_telegram.pack(side='left', expand=True, fill='x', padx=(0, 8))

        ctk.CTkButton(
            btn_row, text='បិទ (Close)', font=('Khmer OS Siemreap', 13),
            command=about_win.destroy,
            fg_color='#1E293B', hover_color='#334155',
            border_width=1, border_color='#475569',
            height=38, corner_radius=8, width=110
        ).pack(side='right')

    def show_splash_screen(self):
        self.splash = ctk.CTkToplevel(self)
        self.splash.overrideredirect(True)
        w, h = (620, 420)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.splash.geometry(f'{w}x{h}+{int(sw / 2 - w / 2)}+{int(sh / 2 - h / 2)}')
        self.splash.attributes('-topmost', True)
        self.splash.attributes('-alpha', 0.0)
        self.splash.configure(fg_color='#07090E')

        splash_border = ctk.CTkFrame(self.splash, corner_radius=14, fg_color='#0F1420', border_width=2, border_color='#00F2FE')
        splash_border.pack(fill='both', expand=True, padx=2, pady=2)

        try:
            from PIL import Image
            img_path = resource_path('RNPHOTOGRAPHY_orig.png')
            if not os.path.exists(img_path):
                img_path = resource_path('RN PHOTOGRAPHY.png')
            if not os.path.exists(img_path):
                img_path = resource_path('splash_bg.jpg')
            img = Image.open(img_path)
            if img.size[0] == img.size[1] or 'orig' in img_path.lower():
                bg = Image.new('RGBA', (w - 4, h - 4), (10, 14, 23, 255))
                max_dim = 250
                logo_c = img.copy()
                logo_c.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
                pos = ((w - 4 - logo_c.width) // 2, (h - 4 - 60 - logo_c.height) // 2 + 5)
                bg.paste(logo_c, pos, logo_c if logo_c.mode == 'RGBA' else None)
                splash_img = ctk.CTkImage(light_image=bg, size=(w - 4, h - 4))
            else:
                splash_img = ctk.CTkImage(light_image=img, size=(w - 4, h - 4))
            bg_label = ctk.CTkLabel(splash_border, text='', image=splash_img)
            bg_label.pack(fill='both', expand=True)

            bot_bar = ctk.CTkFrame(bg_label, fg_color='#070A10', corner_radius=10, border_width=1, border_color='#00F2FE')
            bot_bar.place(relx=0.5, rely=0.88, anchor='center', relwidth=0.85, height=44)
            ctk.CTkLabel(bot_bar, text='⚡ កំពុងរៀបចំប្រព័ន្ធ AI Engine... សូមរង់ចាំ!', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#00F2FE', fg_color='transparent').pack(expand=True)
        except Exception as e:
            error_msg = str(e)
            ctk.CTkLabel(splash_border, text='⚡ RN Photography v3.0 ⚡', font=('Arial', 26, 'bold'), text_color='#00F2FE').pack(pady=(40, 10))
            ctk.CTkLabel(splash_border, text='Offline AI Photo Retouch Suite', font=('Segoe UI', 13), text_color='#94A3B8').pack(pady=(0, 20))
            if error_msg:
                ctk.CTkLabel(splash_border, text=f'Info: {error_msg}', font=('Arial', 10), text_color='#64748B', wraplength=550).pack(pady=5)
            ctk.CTkLabel(splash_border, text='⚡ កំពុងរៀបចំប្រព័ន្ធ AI Engine... សូមរង់ចាំ!', font=('Khmer OS Siemreap', 13, 'bold'), text_color='#00F5A0').pack(pady=20)
        def load_ai_background():
            global ops
            global remove
            global torchvision
            global torch
            global new_session
            global TF
            global rembg
            global gfpgan
            global GFPGANer
            try:
                # 1. Setup Models Dir & Numba Dispatcher
                models_dir = os.environ.get('U2NET_HOME')
                if not models_dir or not os.path.exists(models_dir):
                    models_dir = os.path.join(_app_dir, 'AI_Models')
                    if not os.path.exists(models_dir):
                        models_dir = resource_path('AI_Models')
                if models_dir and os.path.exists(models_dir):
                    os.environ['U2NET_HOME'] = models_dir
                    os.environ['REMBG_HOME'] = models_dir
                os.environ['MODEL_CHECKSUM_DISABLED'] = '1'

                try:
                    from numba.core.dispatcher import Dispatcher
                    Dispatcher.enable_caching = lambda self: None
                except Exception:
                    pass

                # 2. Preload rembg AI model FIRST
                try:
                    import rembg
                    from rembg import remove, new_session
                    for m_name in ['birefnet-general-lite', 'birefnet-portrait', 'isnet-general-use', 'u2net']:
                        try:
                            import onnxruntime as ort
                            sess_opts = ort.SessionOptions()
                            sess_opts.intra_op_num_threads = min(8, max(2, (os.cpu_count() or 4) // 2))
                            sess_opts.inter_op_num_threads = 1
                            sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                            self.bg_session = new_session(m_name, session_options=sess_opts)
                            self.loaded_bg_model = m_name
                            self.bg_model_name = m_name
                            print(f'Preloaded background AI model: {m_name}')
                            break
                        except Exception as e_s:
                            continue
                except Exception as e_r:
                    print('Warning importing rembg:', e_r)

                # 3. Preload Torch, Torchvision, and GFPGAN
                try:
                    import torch
                    import torchvision
                    from torchvision import ops
                    import torchvision.transforms.functional as TF
                    if 'torchvision.transforms.functional_tensor' not in sys.modules:
                        sys.modules['torchvision.transforms.functional_tensor'] = TF
                    import gfpgan
                    from gfpgan import GFPGANer
                    import facexlib
                except Exception as e_t:
                    print('Warning importing GFPGAN:', e_t)
            except Exception as e:
                try:
                    print('Warning loading AI in background:', str(e))
                except Exception:
                    pass
        import threading
        threading.Thread(target=load_ai_background, daemon=True).start()
        self.fade_in(0.0)
    def fade_in(self, alpha):
        if alpha < 1.0:
            alpha += 0.1
            try:
                self.splash.attributes('-alpha', min(1.0, alpha))
            except Exception:
                pass
            self.after(20, lambda: self.fade_in(alpha))
        else:
            self.after(1200, lambda: self.fade_out(1.0))
    def fade_out(self, alpha):
        if alpha > 0.0:
            alpha -= 0.1
            try:
                self.splash.attributes('-alpha', max(0.0, alpha))
            except Exception:
                pass
            self.after(20, lambda: self.fade_out(alpha))
        else:
            try:
                self.splash.destroy()
            except Exception:
                pass
            self.verify_startup()
    # ================= RN PHOTO MAKER V3 SECURITY & LICENSING SYSTEM =================
    LICENSE_MASTER_KEY = b'RN_PHOTO_MAKER_V3_MASTER_SECURITY_KEY_2026_@#9xK!_SECURE_AUTH_TOKEN'
    LICENSE_REG_KEY = r'Software\RNPhotoMaker\Security'

    @staticmethod
    def get_machine_hwid():
        guid = ""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
        except Exception:
            pass
        if not guid:
            try:
                import subprocess
                out = subprocess.check_output("wmic csproduct get uuid", shell=True).decode()
                lines = [l.strip() for l in out.splitlines() if l.strip() and "UUID" not in l]
                if lines:
                    guid = lines[0]
            except Exception:
                pass
        if not guid:
            import uuid
            guid = str(uuid.getnode())

        clean_guid = "".join(c for c in str(guid).upper() if c in "0123456789ABCDEF")
        if not clean_guid:
            clean_guid = str(guid).upper().strip()
        import hashlib
        h = hashlib.sha256(f"RN_HWID_2026_{clean_guid}".encode('utf-8')).hexdigest().upper()
        return f"RN-{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"

    @staticmethod
    def normalize_pc_id(raw_id):
        if not raw_id:
            return ""
        clean = "".join(c for c in str(raw_id).upper() if c.isalnum())
        if clean.startswith("RN") or clean.startswith("MT"):
            clean = clean[2:]
        if len(clean) >= 16:
            return f"RN-{clean[0:4]}-{clean[4:8]}-{clean[8:12]}-{clean[12:16]}"
        return str(raw_id).strip().upper()

    @classmethod
    def generate_expected_license_key(cls, pc_id, exp_date="99991231"):
        import hmac
        import hashlib
        norm_id = cls.normalize_pc_id(pc_id)
        payload = f"RN_PRO_v3|{norm_id}|{exp_date}".encode('utf-8')
        h = hmac.new(cls.LICENSE_MASTER_KEY, payload, hashlib.sha256).hexdigest().upper()
        return f"RN-{exp_date}-{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"

    @classmethod
    def get_security_timestamp(cls):
        """Read last recorded run timestamp to detect clock rollback tampering."""
        import base64
        last_ts = 0.0
        # 1. Check local app folder
        try:
            p_local = os.path.join(_app_dir, '.rn_sec.dat')
            if os.path.exists(p_local):
                with open(p_local, 'r', encoding='utf-8') as f:
                    c = f.read().strip()
                if c:
                    last_ts = float(base64.b64decode(c.encode('ascii')).decode('ascii', errors='ignore'))
        except Exception:
            pass
        # 2. Check AppData folder
        if last_ts <= 0:
            try:
                appdata = os.environ.get('APPDATA', '')
                if appdata:
                    p = os.path.join(appdata, 'RN_PhotoMaker', '.rn_sec.dat')
                    if os.path.exists(p):
                        with open(p, 'r', encoding='utf-8') as f:
                            c = f.read().strip()
                        if c:
                            last_ts = float(base64.b64decode(c.encode('ascii')).decode('ascii', errors='ignore'))
            except Exception:
                pass
        # 3. Check Windows Registry
        if last_ts <= 0:
            try:
                import winreg
                k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.LICENSE_REG_KEY, 0, winreg.KEY_READ)
                val, _ = winreg.QueryValueEx(k, "SysRef")
                winreg.CloseKey(k)
                if val:
                    last_ts = float(base64.b64decode(val.encode('ascii')).decode('ascii', errors='ignore'))
            except Exception:
                pass
        return last_ts

    @classmethod
    def record_security_timestamp(cls):
        """Securely record current timestamp to block system clock manipulation."""
        import base64
        import time
        now_ts = time.time()
        enc = base64.b64encode(str(now_ts).encode('ascii')).decode('ascii')
        # 1. Save to local app folder
        try:
            with open(os.path.join(_app_dir, '.rn_sec.dat'), 'w', encoding='utf-8') as f:
                f.write(enc)
        except Exception:
            pass
        # 2. Save to AppData folder
        try:
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                d = os.path.join(appdata, 'RN_PhotoMaker')
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, '.rn_sec.dat'), 'w', encoding='utf-8') as f:
                    f.write(enc)
        except Exception:
            pass
        # 3. Save to Windows Registry
        try:
            import winreg
            k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, cls.LICENSE_REG_KEY)
            winreg.SetValueEx(k, "SysRef", 0, winreg.REG_SZ, enc)
            winreg.CloseKey(k)
        except Exception:
            pass

    @classmethod
    def verify_license_key(cls, key, current_pc_id):
        import re
        import datetime
        import hmac
        import time
        try:
            if not key:
                return False, "សូមវាយបញ្ចូល License Key!", None
            key = key.strip().upper()
            m = re.match(r"^RN-(\d{8})-([A-F0-9]{4})-([A-F0-9]{4})-([A-F0-9]{4})-([A-F0-9]{4})$", key)
            if not m:
                return False, "ទម្រង់ License Key មិនត្រឹមត្រូវ! (ទម្រង់ត្រឹមត្រូវ: RN-YYYYMMDD-XXXX-XXXX-XXXX-XXXX)", None
            exp_str = m.group(1)
            norm_id = cls.normalize_pc_id(current_pc_id)
            expected_key = cls.generate_expected_license_key(norm_id, exp_str)

            if not hmac.compare_digest(key, expected_key):
                return False, "License Key មិនត្រឹមត្រូវសម្រាប់កុំព្យូទ័រនេះទេ!", None

            # Check Lifetime
            if exp_str == "99991231":
                cls.record_security_timestamp()
                info = {
                    "type": "lifetime",
                    "days_left": 999999,
                    "exp_date": "គ្មានថ្ងៃផុតកំណត់ (Lifetime)",
                    "text": "💎 Lifetime License (ប្រើបានរហូត)"
                }
                return True, "License Lifetime សកម្ម (គ្មានថ្ងៃផុតកំណត់)", info

            # Check Expiry Date
            try:
                exp_date = datetime.datetime.strptime(exp_str, "%Y%m%d").date()
            except Exception:
                return False, "កាលបរិច្ឆេទក្នុង Key មិនត្រឹមត្រូវ!", None

            # Anti-clock rollback verification
            last_ts = cls.get_security_timestamp()
            now_ts = time.time()
            if last_ts > 0 and now_ts < (last_ts - 86400):
                return False, "ប្រព័ន្ធបានរកឃើញការថយម៉ោងកុំព្យូទ័រ (Clock Rollback)! សូមកំណត់ម៉ោងម៉ាស៊ីនឡើងវិញ។", None

            cls.record_security_timestamp()
            today = datetime.date.today()
            days_left = (exp_date - today).days

            if days_left < 0:
                d_str = exp_date.strftime("%d/%m/%Y")
                return False, f"License Key នេះបានផុតកំណត់កាលពីថ្ងៃ {d_str} ({abs(days_left)} ថ្ងៃមុន)!", None

            info = {
                "type": "expiring",
                "days_left": days_left,
                "exp_date": exp_date.strftime("%d/%m/%Y"),
                "text": f"⏳ នៅសល់ {days_left} ថ្ងៃ (ផុតកំណត់: {exp_date.strftime('%d/%m/%Y')})"
            }
            return True, f"License សកម្ម (នៅសល់ {days_left} ថ្ងៃ - ផុតកំណត់: {exp_date.strftime('%d/%m/%Y')})", info

        except Exception as e:
            return False, f"កំហុស License: {e}", None

    def get_license_file_paths(self):
        paths = []
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            paths.append(os.path.join(base_dir, 'license.lic'))
        except Exception:
            pass
        try:
            appdata = os.environ.get('APPDATA')
            if appdata:
                rn_dir = os.path.join(appdata, 'RN_PhotoMaker')
                paths.append(os.path.join(rn_dir, 'license.lic'))
                mt_dir = os.path.join(appdata, 'MT_PhotoMaker')
                paths.append(os.path.join(mt_dir, 'license.lic'))
        except Exception:
            pass
        return paths

    def read_saved_license(self):
        for p in self.get_license_file_paths():
            try:
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        key = content.split('||')[0].strip()
                        if key.startswith('RN-'):
                            return key
            except Exception:
                pass
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\RNPhotoMaker", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(k, "LicenseKey")
            winreg.CloseKey(k)
            if val and val.strip().startswith('RN-'):
                return val.strip()
        except Exception:
            pass
        return ""

    def save_license(self, key):
        saved = False
        key = key.strip().upper()
        for p in self.get_license_file_paths():
            try:
                folder = os.path.dirname(p)
                if folder and not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(key)
                saved = True
            except Exception:
                pass
        try:
            import winreg
            k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RNPhotoMaker")
            winreg.SetValueEx(k, "LicenseKey", 0, winreg.REG_SZ, key)
            winreg.CloseKey(k)
            saved = True
        except Exception:
            pass
        return saved

    def get_hwid(self):
        return self.get_machine_hwid()

    def has_legacy_mt_license(self):
        """Check if an old MT license exists on this machine from previous versions."""
        for p in self.get_license_file_paths():
            try:
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        c = f.read().strip()
                    if c and ('MT-' in c.upper()):
                        return True
            except Exception:
                pass
        try:
            import winreg
            for subkey in [r"Software\MTPhotoMaker", r"Software\MT_PhotoMaker", r"Software\RNPhotoMaker"]:
                try:
                    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_READ)
                    val, _ = winreg.QueryValueEx(k, "LicenseKey")
                    winreg.CloseKey(k)
                    if val and ('MT-' in str(val).upper()):
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def check_license(self):
        try:
            saved_key = self.read_saved_license()
            if not saved_key:
                if self.has_legacy_mt_license():
                    return False, "កម្មវិធីត្រូវបាន Upgrade ប្រព័ន្ធសុវត្ថិភាពថ្មី (RN Pro v3)! សូមផ្ញើ PC ID ខាងក្រោមទៅកាន់ Admin ដើម្បីប្តូរយក License Key ថ្មី។", None
                return False, "មិនទាន់បានចុះឈ្មោះ License នៅឡើយទេ", None
            pc_id = self.get_hwid()
            is_valid, msg, info = self.verify_license_key(saved_key, pc_id)
            return is_valid, msg, info
        except Exception as e:
            return False, f"បញ្ហា License: {e}", None

    def ensure_license_active(self, feature_name="ដំណើរការមុខងារ"):
        is_valid, msg, info = self.check_license()
        if not is_valid:
            try:
                messagebox.showerror(
                    "ទាមទារ License (Activation Required)",
                    f"មិនអាច {feature_name} បានឡើយ!\n\nស្ថានភាព: {msg}\nសូមចុះឈ្មោះ License កម្មវិធីជាមុនសិន។"
                )
            except Exception:
                pass
            self.show_activation_window(msg)
            return False
        return True

    def update_license_ui_badge(self):
        try:
            if not hasattr(self, 'btn_license_pill') or self.btn_license_pill is None:
                return
            is_valid, msg, info = self.check_license()
            if is_valid and info:
                if info.get('type') == 'lifetime':
                    self.btn_license_pill.configure(
                        text='💎 Lifetime License (ប្រើបានរហូត)',
                        fg_color='#062D24',
                        hover_color='#0A3D31',
                        border_color='#00F5A0',
                        text_color='#00FF9D'
                    )
                else:
                    days = info.get('days_left', 0)
                    exp_date = info.get('exp_date', '')
                    if days > 15:
                        self.btn_license_pill.configure(
                            text=f'⏳ នៅសល់ {days} ថ្ងៃ (ផុត: {exp_date})',
                            fg_color='#0C2A3A',
                            hover_color='#133B52',
                            border_color='#38BDF8',
                            text_color='#38BDF8'
                        )
                    else:
                        self.btn_license_pill.configure(
                            text=f'⚠️ នៅសល់ {days} ថ្ងៃ (ផុត: {exp_date})',
                            fg_color='#332205',
                            hover_color='#4A3208',
                            border_color='#F59E0B',
                            text_color='#FBBF24'
                        )
            else:
                self.btn_license_pill.configure(
                    text='❌ License ផុតកំណត់ / មិនទាន់ចុះឈ្មោះ',
                    fg_color='#331015',
                    hover_color='#47151C',
                    border_color='#EF4444',
                    text_color='#F87171'
                )
        except Exception:
            pass

    def show_license_info_window(self):
        pc_id = self.get_hwid()
        saved_key = self.read_saved_license()
        is_valid, msg, info = self.check_license()

        lic_win = ctk.CTkToplevel(self)
        lic_win.title('🔐 ព័ត៌មាន License - RN Photography v3.0')
        w, h = (540, 520)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        lic_win.geometry(f'{w}x{h}+{int(sw / 2 - w / 2)}+{int(sh / 2 - h / 2)}')
        lic_win.attributes('-topmost', True)
        lic_win.grab_set()
        lic_win.configure(fg_color='#0B0F19')

        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            lic_win.iconbitmap(ico_path)
        except Exception:
            pass

        # Header
        head_frame = ctk.CTkFrame(lic_win, fg_color='#111726', corner_radius=12, border_width=1, border_color='#00F2FE')
        head_frame.pack(fill='x', padx=20, pady=(16, 12))
        ctk.CTkLabel(head_frame, text='💎 RN Photography v3.0 License 💎', font=('Segoe UI', 16, 'bold'), text_color='#00F2FE').pack(pady=(12, 2))
        ctk.CTkLabel(head_frame, text='ព័ត៌មានសុពលភាព និងការចុះឈ្មោះប្រើប្រាស់កម្មវិធី', font=('Khmer OS Siemreap', 10), text_color='#94A3B8').pack(pady=(0, 10))

        # Status Card
        card_status = ctk.CTkFrame(lic_win, fg_color='#161C2C', corner_radius=10, border_width=1, border_color='#253047')
        card_status.pack(fill='x', padx=20, pady=(0, 10))
        ctk.CTkLabel(card_status, text='⚡ ស្ថានភាពអាជ្ញាបណ្ណ (License Status):', font=('Khmer OS Siemreap', 11, 'bold'), text_color='#E2E8F0').pack(anchor='w', padx=14, pady=(10, 4))

        if is_valid and info:
            if info.get('type') == 'lifetime':
                status_box = ctk.CTkFrame(card_status, fg_color='#062D24', corner_radius=8, border_width=1, border_color='#00F5A0')
                status_box.pack(fill='x', padx=14, pady=(0, 10))
                ctk.CTkLabel(status_box, text='💎 ប្រើប្រាស់បានពេញមួយជីវិត (Lifetime Active)', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#00FF9D').pack(pady=(6, 2))
                ctk.CTkLabel(status_box, text='✓ គ្មានថ្ងៃផុតកំណត់  •  ✓ ប្រើប្រាស់មុខងារទាំងអស់គ្មានដែនកំណត់', font=('Khmer OS Siemreap', 10), text_color='#A7F3D0').pack(pady=(0, 6))
            else:
                days = info.get('days_left', 0)
                exp = info.get('exp_date', '')
                status_box = ctk.CTkFrame(card_status, fg_color='#0C2A3A', corner_radius=8, border_width=1, border_color='#38BDF8')
                status_box.pack(fill='x', padx=14, pady=(0, 10))
                ctk.CTkLabel(status_box, text=f'⏳ សកម្ម (នៅសល់ {days} ថ្ងៃ)', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#38BDF8').pack(pady=(6, 2))
                ctk.CTkLabel(status_box, text=f'កាលបរិច្ឆេទផុតកំណត់: {exp}', font=('Khmer OS Siemreap', 10), text_color='#BAE6FD').pack(pady=(0, 6))
        else:
            status_box = ctk.CTkFrame(card_status, fg_color='#331015', corner_radius=8, border_width=1, border_color='#EF4444')
            status_box.pack(fill='x', padx=14, pady=(0, 10))
            ctk.CTkLabel(status_box, text='❌ មិនទាន់ចុះឈ្មោះ ឬ License ផុតកំណត់', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#F87171').pack(pady=(6, 2))
            ctk.CTkLabel(status_box, text=f'{msg}', font=('Khmer OS Siemreap', 10), text_color='#FECACA').pack(pady=(0, 6))

        # Hardware ID Card
        card_hwid = ctk.CTkFrame(lic_win, fg_color='#161C2C', corner_radius=10, border_width=1, border_color='#253047')
        card_hwid.pack(fill='x', padx=20, pady=(0, 10))
        ctk.CTkLabel(card_hwid, text='💻 PC ID របស់កុំព្យូទ័រនេះ (Hardware ID):', font=('Khmer OS Siemreap', 11, 'bold'), text_color='#E2E8F0').pack(anchor='w', padx=14, pady=(8, 2))
        
        row_hwid = ctk.CTkFrame(card_hwid, fg_color='transparent')
        row_hwid.pack(fill='x', padx=14, pady=(0, 10))
        ent_hwid = ctk.CTkEntry(row_hwid, font=('Consolas', 12, 'bold'), text_color='#00FFAA', fg_color='#0B0F19', border_color='#334155')
        ent_hwid.insert(0, pc_id)
        ent_hwid.configure(state='readonly')
        ent_hwid.pack(side='left', fill='x', expand=True, padx=(0, 8))

        def copy_pcid():
            self.clipboard_clear()
            self.clipboard_append(pc_id)
            btn_copy_id.configure(text='✓ បានចម្លង')
            self.after(2000, lambda: btn_copy_id.configure(text='📋 ចម្លង ID'))
        btn_copy_id = ctk.CTkButton(row_hwid, text='📋 ចម្លង ID', width=95, font=('Khmer OS Siemreap', 11, 'bold'), fg_color='#2563EB', hover_color='#1D4ED8', command=copy_pcid)
        btn_copy_id.pack(side='right')

        # Active Key Card
        card_key = ctk.CTkFrame(lic_win, fg_color='#161C2C', corner_radius=10, border_width=1, border_color='#253047')
        card_key.pack(fill='x', padx=20, pady=(0, 12))
        ctk.CTkLabel(card_key, text='🔑 License Key បច្ចុប្បន្ន:', font=('Khmer OS Siemreap', 11, 'bold'), text_color='#E2E8F0').pack(anchor='w', padx=14, pady=(8, 2))
        
        row_key = ctk.CTkFrame(card_key, fg_color='transparent')
        row_key.pack(fill='x', padx=14, pady=(0, 10))
        ent_key = ctk.CTkEntry(row_key, font=('Consolas', 11, 'bold'), text_color='#FBBF24', fg_color='#0B0F19', border_color='#334155')
        ent_key.insert(0, saved_key if saved_key else '(ពុំទាន់មាន)')
        ent_key.configure(state='readonly')
        ent_key.pack(side='left', fill='x', expand=True, padx=(0, 8))

        def copy_key():
            if saved_key:
                self.clipboard_clear()
                self.clipboard_append(saved_key)
                btn_copy_k.configure(text='✓ បានចម្លង')
                self.after(2000, lambda: btn_copy_k.configure(text='📋 ចម្លង Key'))
        btn_copy_k = ctk.CTkButton(row_key, text='📋 ចម្លង Key', width=95, font=('Khmer OS Siemreap', 11, 'bold'), fg_color='#475569', hover_color='#334155', command=copy_key)
        btn_copy_k.pack(side='right')

        # Buttons
        btn_row = ctk.CTkFrame(lic_win, fg_color='transparent')
        btn_row.pack(fill='x', padx=20, pady=(0, 12))

        def on_change_key():
            lic_win.destroy()
            self.show_activation_window(initial_msg="សូមបញ្ចូល License Key ថ្មី")

        btn_change = ctk.CTkButton(
            btn_row, text='🔄 ប្តូរ License Key ថ្មី', font=('Khmer OS Siemreap', 12, 'bold'),
            fg_color='#10B981', hover_color='#059669', height=38, command=on_change_key
        )
        btn_change.pack(side='left', fill='x', expand=True, padx=(0, 8))

        def open_tg():
            import webbrowser
            webbrowser.open('https://t.me/Ratana_Printing')

        btn_admin = ctk.CTkButton(
            btn_row, text='✈️ Admin Telegram', font=('Khmer OS Siemreap', 12),
            fg_color='#0284C7', hover_color='#0369A1', height=38, width=130, command=open_tg
        )
        btn_admin.pack(side='left', padx=(0, 8))

        btn_close = ctk.CTkButton(
            btn_row, text='បិទ (Close)', font=('Khmer OS Siemreap', 12),
            fg_color='#1E293B', hover_color='#334155', height=38, width=90, command=lic_win.destroy
        )
        btn_close.pack(side='right')

    def verify_startup(self):
        is_valid, msg, info = self.check_license()
        self.update_license_ui_badge()
        if is_valid:
            self.deiconify()
            if getattr(self, 'ps_mode', False):
                self.attributes('-topmost', True)
            self.force_foreground()
            self.after(200, self.fit_image)
        else:
            self.show_activation_window(msg)

    def show_activation_window(self, initial_msg=""):
        pc_id = self.get_hwid()
        act_win = ctk.CTkToplevel(self)
        act_win.title('🔐 ការចុះឈ្មោះកម្មវិធី (RN Photography Activation)')
        w, h = (530, 490)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        act_win.geometry(f'{w}x{h}+{int(sw / 2 - w / 2)}+{int(sh / 2 - h / 2)}')
        act_win.attributes('-topmost', True)
        act_win.grab_set()
        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            act_win.iconbitmap(ico_path)
        except Exception:
            pass

        def on_close():
            self.destroy()
            sys.exit(0)

        act_win.protocol('WM_DELETE_WINDOW', on_close)

        # Title Header
        ctk.CTkLabel(act_win, text='💎 RN Photography v3.0 Activation 💎', font=('Segoe UI', 18, 'bold'), text_color='#00F5D4').pack(pady=(18, 4))
        ctk.CTkLabel(act_win, text='សូមចម្លង PC ID ខាងក្រោមផ្ញើទៅកាន់ Admin ដើម្បីទទួលយក License Key', font=('Khmer OS Siemreap', 11), text_color='#94A3B8').pack(pady=(0, 14))

        # Card: PC ID (Hardware ID)
        frame_hwid = ctk.CTkFrame(act_win, fg_color='#1E2433', corner_radius=10)
        frame_hwid.pack(padx=25, fill='x', pady=(0, 12))

        ctk.CTkLabel(frame_hwid, text='💻 PC ID របស់កុំព្យូទ័រនេះ (Hardware ID):', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#E2E8F0').pack(anchor='w', padx=15, pady=(10, 4))

        row_id = ctk.CTkFrame(frame_hwid, fg_color='transparent')
        row_id.pack(fill='x', padx=15, pady=(0, 10))

        hwid_entry = ctk.CTkEntry(row_id, font=('Consolas', 13, 'bold'), text_color='#00FFAA', fg_color='#0F131D', border_color='#334155')
        hwid_entry.insert(0, pc_id)
        hwid_entry.configure(state='readonly')
        hwid_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))

        lbl_copy_hint = ctk.CTkLabel(act_win, text='', font=('Khmer OS Siemreap', 11), text_color='#10B981')

        def copy_hwid():
            self.clipboard_clear()
            self.clipboard_append(pc_id)
            lbl_copy_hint.configure(text='📋 បានចម្លង PC ID ចូល Clipboard រួចរាល់! អាចផ្ញើជូន Admin បាន')
            lbl_copy_hint.pack(pady=(0, 4))

        btn_copy = ctk.CTkButton(row_id, text='📋 ចម្លង (Copy)', width=105, font=('Khmer OS Siemreap', 12, 'bold'), fg_color='#6366F1', hover_color='#4F46E5', command=copy_hwid)
        btn_copy.pack(side='right')

        # Card: License Key Entry
        frame_key = ctk.CTkFrame(act_win, fg_color='#1E2433', corner_radius=10)
        frame_key.pack(padx=25, fill='x', pady=(0, 10))

        ctk.CTkLabel(frame_key, text='🔑 បញ្ចូល License Key ដែលទទួលបានពី Admin:', font=('Khmer OS Siemreap', 12, 'bold'), text_color='#E2E8F0').pack(anchor='w', padx=15, pady=(10, 4))
        key_entry = ctk.CTkEntry(frame_key, justify='center', font=('Consolas', 14, 'bold'), placeholder_text='RN-99991231-XXXX-XXXX-XXXX-XXXX', fg_color='#0F131D', border_color='#334155', height=40)
        key_entry.pack(fill='x', padx=15, pady=(0, 12))

        # Status Label
        lbl_status = ctk.CTkLabel(act_win, text=f'⚠️ {initial_msg}' if initial_msg else '', font=('Khmer OS Siemreap', 11), text_color='#F59E0B', wraplength=480, justify='center')
        lbl_status.pack(pady=(0, 8))

        def activate():
            license_key = key_entry.get().strip().upper()
            if not license_key:
                lbl_status.configure(text='សូមវាយ ឬ Paste License Key!', text_color='#EF4444')
                messagebox.showwarning('បញ្ជាក់', 'សូមបញ្ចូល License Key មុននឹងចុច Activate!')
                return

            is_valid, msg, info = self.verify_license_key(license_key, pc_id)
            if is_valid:
                self.save_license(license_key)
                self.update_license_ui_badge()
                act_win.grab_release()
                act_win.attributes('-topmost', False)
                messagebox.showinfo('ជោគជ័យ', f'✅ ការចុះឈ្មោះជោគជ័យ!\n{msg}\nសូមស្វាគមន៍មកកាន់ RN Photography v3.0')
                act_win.destroy()
                self.deiconify()
                if getattr(self, 'ps_mode', False):
                    self.attributes('-topmost', True)
                self.force_foreground()
                self.after(200, self.fit_image)
            else:
                lbl_status.configure(text=f'❌ {msg}', text_color='#EF4444')
                act_win.grab_release()
                act_win.attributes('-topmost', False)
                messagebox.showerror('បរាជ័យ', f'❌ {msg}')
                act_win.attributes('-topmost', True)
                act_win.grab_set()

        # Action Buttons
        btn_frame = ctk.CTkFrame(act_win, fg_color='transparent')
        btn_frame.pack(fill='x', padx=25, pady=(0, 10))

        btn_activate = ctk.CTkButton(btn_frame, text='✅ ធ្វើសកម្មភាព (Activate Now)', height=42, font=('Khmer OS Siemreap', 13, 'bold'), fg_color='#10B981', hover_color='#059669', command=activate)
        btn_activate.pack(side='left', fill='x', expand=True, padx=(0, 6))

        btn_exit = ctk.CTkButton(btn_frame, text='❌ ចាកចេញ (Exit)', width=110, height=42, font=('Khmer OS Siemreap', 13), fg_color='#334155', hover_color='#1E293B', command=on_close)
        btn_exit.pack(side='right')

        def open_admin_telegram():
            import webbrowser
            webbrowser.open('https://t.me/Ratana_Printing')

        btn_tg = ctk.CTkButton(act_win, text='💬 ទំនាក់ទំនងទិញ Key Telegram: @Ratana_Printing', font=('Khmer OS Siemreap', 11, 'underline'), fg_color='transparent', text_color='#38BDF8', hover_color='#1E293B', command=open_admin_telegram)
        btn_tg.pack(pady=(0, 5))

    # ================= AUTO-UPDATE SYSTEM =================
    @staticmethod
    def parse_version_tuple(v_str):
        import re
        try:
            nums = [int(x) for x in re.findall(r'\d+', str(v_str))]
            return tuple(nums) if nums else (0,)
        except Exception:
            return (0,)

    @classmethod
    def is_version_newer(cls, remote_v, local_v):
        r = cls.parse_version_tuple(remote_v)
        l = cls.parse_version_tuple(local_v)
        length = max(len(r), len(l))
        r_pad = r + (0,) * (length - len(r))
        l_pad = l + (0,) * (length - len(l))
        return r_pad > l_pad

    def get_update_manifest_url(self):
        url = DEFAULT_UPDATE_URL
        try:
            cfg_p = os.path.join(_app_dir, 'update_url.txt')
            if os.path.exists(cfg_p):
                with open(cfg_p, 'r', encoding='utf-8') as f:
                    c = f.read().strip()
                    if c.startswith('http'):
                        return c
        except Exception:
            pass
        return url

    def fetch_update_manifest(self):
        import urllib.request
        import json
        url = self.get_update_manifest_url()
        req = urllib.request.Request(
            url,
            headers={'User-Agent': f'RN-PhotoMaker-App/{APP_VERSION}'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            return json.loads(data)

    def start_silent_update_check(self):
        def worker():
            try:
                manifest = self.fetch_update_manifest()
                if not manifest:
                    return
                latest_ver = manifest.get('latest_version') or manifest.get('version', '')
                if self.is_version_newer(latest_ver, APP_VERSION):
                    def update_ui():
                        if hasattr(self, 'btn_check_update') and self.btn_check_update:
                            self.btn_check_update.configure(
                                text=f'🚀 Update v{latest_ver}',
                                fg_color='#7C2D12',
                                hover_color='#9A3412',
                                border_color='#F97316',
                                text_color='#FDBA74'
                            )
                        if manifest.get('mandatory', False):
                            self.show_update_dialog(manifest, auto_prompt=True)
                    self.after(0, update_ui)
            except Exception:
                pass
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def check_for_updates(self, manual=True):
        if manual and hasattr(self, 'btn_check_update') and self.btn_check_update:
            self.btn_check_update.configure(text='⏳ ពិនិត្យ...')

        def worker():
            try:
                manifest = self.fetch_update_manifest()
                latest_ver = manifest.get('latest_version') or manifest.get('version', '')
                if self.is_version_newer(latest_ver, APP_VERSION):
                    def show_dlg():
                        if hasattr(self, 'btn_check_update') and self.btn_check_update:
                            self.btn_check_update.configure(
                                text=f'🚀 Update v{latest_ver}',
                                fg_color='#7C2D12',
                                hover_color='#9A3412',
                                border_color='#F97316',
                                text_color='#FDBA74'
                            )
                        self.show_update_dialog(manifest)
                    self.after(0, show_dlg)
                else:
                    def show_uptodate():
                        if hasattr(self, 'btn_check_update') and self.btn_check_update:
                            self.btn_check_update.configure(text='✓ v' + APP_VERSION)
                            self.after(3000, lambda: self.btn_check_update.configure(text='🔄 Update'))
                        if manual:
                            messagebox.showinfo(
                                'ទាន់សម័យ',
                                f'✅ កម្មវិធី RN PhotoMaker របស់អ្នកជាកំណែថ្មីបំផុតហើយ (v{APP_VERSION})!'
                            )
                    self.after(0, show_uptodate)
            except Exception as e:
                def show_err():
                    if hasattr(self, 'btn_check_update') and self.btn_check_update:
                        self.btn_check_update.configure(text='🔄 Update')
                    if manual:
                        messagebox.showwarning(
                            'មិនអាចភ្ជាប់បាន',
                            '⚠️ មិនអាចភ្ជាប់ទៅកាន់ Server ដើម្បីពិនិត្យ Update បានឡើយ!\n'
                            'សូមពិនិត្យមើលការភ្ជាប់ Internet របស់អ្នក ឬសាកល្បងម្ដងទៀតនៅពេលក្រោយ។'
                        )
                self.after(0, show_err)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def show_update_dialog(self, manifest, auto_prompt=False):
        new_ver = manifest.get('latest_version') or manifest.get('version', '3.1.0')
        rel_date = manifest.get('release_date', '')
        title_text = manifest.get('title', f'RN PhotoMaker v{new_ver} Update')
        changelog = manifest.get('changelog', '• កែលម្អដំណើរការ និងបន្ថែមមុខងារថ្មីៗ')
        patch_url = manifest.get('patch_url', '')
        setup_url = manifest.get('setup_url', '')

        dlg = ctk.CTkToplevel(self)
        dlg.title(f'🚀 កំណែ Update ថ្មី v{new_ver} - RN PhotoMaker')
        w, h = 530, 500
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dlg.geometry(f'{w}x{h}+{int(sw/2 - w/2)}+{int(sh/2 - h/2)}')
        dlg.attributes('-topmost', True)
        dlg.grab_set()
        dlg.configure(fg_color='#0B0F19')

        try:
            ico_path = resource_path('RNPHOTOGRAPHY.ico')
            if not os.path.exists(ico_path):
                ico_path = resource_path('icon.ico')
            dlg.iconbitmap(ico_path)
        except Exception:
            pass

        # Top Banner
        pnl_top = ctk.CTkFrame(dlg, fg_color='#111827', corner_radius=12, border_width=1, border_color='#F97316')
        pnl_top.pack(fill='x', padx=18, pady=(16, 10))

        ctk.CTkLabel(
            pnl_top, text=f'🚀 មានកំណែថ្មី: v{new_ver}',
            font=('Segoe UI', 17, 'bold'), text_color='#FB923C'
        ).pack(anchor='w', padx=16, pady=(12, 2))

        sub_info = f'កំណែបច្ចុប្បន្ន: v{APP_VERSION}'
        if rel_date:
            sub_info += f'  •  ថ្ងៃចេញផ្សាយ: {rel_date}'
        ctk.CTkLabel(
            pnl_top, text=sub_info,
            font=('Khmer OS Siemreap', 10), text_color='#94A3B8'
        ).pack(anchor='w', padx=16, pady=(0, 10))

        # Changelog Card
        pnl_notes = ctk.CTkFrame(dlg, fg_color='#151D2F', corner_radius=10, border_width=1, border_color='#253047')
        pnl_notes.pack(fill='both', expand=True, padx=18, pady=(0, 12))

        ctk.CTkLabel(
            pnl_notes, text='📋 ចំណុចកែប្រែ និងមុខងារថ្មីៗ (Changelog):',
            font=('Khmer OS Siemreap', 11, 'bold'), text_color='#E2E8F0'
        ).pack(anchor='w', padx=14, pady=(10, 6))

        txt_notes = ctk.CTkTextbox(
            pnl_notes, font=('Khmer OS Siemreap', 10.5),
            fg_color='#0E1322', text_color='#F1F5F9', border_color='#334155', border_width=1
        )
        txt_notes.pack(fill='both', expand=True, padx=14, pady=(0, 12))
        txt_notes.insert('1.0', changelog)
        txt_notes.configure(state='disabled')

        # Progress Section
        pnl_prog = ctk.CTkFrame(dlg, fg_color='transparent')
        pnl_prog.pack(fill='x', padx=18, pady=(0, 8))

        lbl_prog = ctk.CTkLabel(pnl_prog, text='', font=('Khmer OS Siemreap', 10), text_color='#38BDF8')
        lbl_prog.pack(anchor='w', pady=(0, 2))

        prog_bar = ctk.CTkProgressBar(pnl_prog, height=10, corner_radius=5, progress_color='#10B981')
        prog_bar.set(0)

        # Action Buttons
        pnl_btns = ctk.CTkFrame(dlg, fg_color='transparent')
        pnl_btns.pack(fill='x', padx=18, pady=(0, 16))

        def start_quick_patch():
            if not patch_url:
                if setup_url:
                    import webbrowser
                    webbrowser.open(setup_url)
                else:
                    messagebox.showwarning('បញ្ជាក់', 'មិនមាន Link Patch ឡើយ!')
                return

            btn_update_now.configure(state='disabled')
            btn_later.configure(state='disabled')
            prog_bar.pack(fill='x', pady=(2, 6))
            lbl_prog.configure(text='⏳ កំពុងចាប់ផ្តើមទាញយក File Update...')

            def download_worker():
                try:
                    import urllib.request
                    temp_file = os.path.join(_app_dir, 'photo_maker.pyc.update')
                    req = urllib.request.Request(patch_url, headers={'User-Agent': f'RN-PhotoMaker-Update/{APP_VERSION}'})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        total_size = int(resp.headers.get('content-length', 0))
                        downloaded = 0
                        chunk_size = 16384
                        with open(temp_file, 'wb') as f:
                            while True:
                                chunk = resp.read(chunk_size)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    pct = downloaded / total_size
                                    dlg.after(0, lambda p=pct, d=downloaded, t=total_size: (
                                        prog_bar.set(p),
                                        lbl_prog.configure(text=f'📥 កំពុងទាញយក: {int(p*100)}% ({int(d/1024)} KB / {int(t/1024)} KB)')
                                    ))

                    if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 50000:
                        raise Exception("File update ទំហំតូចខុសប្រក្រតី (Download មិនពេញលេញ)!")

                    dlg.after(0, lambda: lbl_prog.configure(text='✅ ទាញយករួចរាល់! កំពុង Restart កម្មវិធី...'))

                    # Create self-deleting restart batch file
                    bat_path = os.path.join(_app_dir, 'apply_update.bat')
                    bat_content = (
                        "@echo off\r\n"
                        "timeout /t 1 /nobreak >nul\r\n"
                        f"move /y \"{temp_file}\" \"{os.path.join(_app_dir, 'photo_maker.pyc')}\" >nul\r\n"
                        f"start \"\" \"{os.path.join(_app_dir, 'PhotoMaker.exe')}\"\r\n"
                        "del \"%~f0\" >nul 2>&1\r\n"
                    )
                    with open(bat_path, 'w', encoding='ascii') as f:
                        f.write(bat_content)

                    # Launch batch and exit
                    import subprocess
                    flags = 0x08000000 if os.name == 'nt' else 0
                    subprocess.Popen(['cmd.exe', '/c', bat_path], creationflags=flags)
                    self.after(300, lambda: os._exit(0))
                except Exception as err:
                    dlg.after(0, lambda: (
                        btn_update_now.configure(state='normal'),
                        btn_later.configure(state='normal'),
                        lbl_prog.configure(text=f'❌ បរាជ័យ: {err}', text_color='#EF4444'),
                        messagebox.showerror('បញ្ហាទាញយក', f'មិនអាច Update បានទេ: {err}')
                    ))

            t = threading.Thread(target=download_worker, daemon=True)
            t.start()

        def open_full_setup():
            if setup_url:
                import webbrowser
                webbrowser.open(setup_url)
            else:
                messagebox.showinfo('ដំណឹង', 'មិនមាន Setup URL ឡើយ។')

        btn_update_now = ctk.CTkButton(
            pnl_btns, text='⚡ Update ឥឡូវនេះ (Quick Patch)',
            font=('Khmer OS Siemreap', 12, 'bold'),
            height=38, fg_color='#10B981', hover_color='#059669',
            command=start_quick_patch
        )
        btn_update_now.pack(side='left', fill='x', expand=True, padx=(0, 6))

        if setup_url:
            btn_setup = ctk.CTkButton(
                pnl_btns, text='🌐 កញ្ចប់ Setup ពេញ',
                font=('Khmer OS Siemreap', 11),
                height=38, width=130, fg_color='#0284C7', hover_color='#0369A1',
                command=open_full_setup
            )
            btn_setup.pack(side='left', padx=(0, 6))

        btn_later = ctk.CTkButton(
            pnl_btns, text='ពេលក្រោយ',
            font=('Khmer OS Siemreap', 11),
            height=38, width=95, fg_color='#1E293B', hover_color='#334155',
            command=dlg.destroy
        )
        btn_later.pack(side='right')
if __name__ == '__main__':
    try:
        app = PhotoMakerApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)