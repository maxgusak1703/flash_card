# ui/dialogs.py

import threading
import json
from gi.repository import Gtk, Adw, GLib

from core.config import ConfigManager
from core.database import DataManager
from core.ai_service import HAS_AI, generate_flashcards

class AIGeneratorDialog(Adw.Window):
    def __init__(self, parent, manager, on_success_callback):
        super().__init__(modal=True, default_width=500, default_height=650)
        self.set_transient_for(parent)
        self.manager = manager
        self.config = ConfigManager()
        self.on_success = on_success_callback

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar(); header.set_show_end_title_buttons(False)
        btn_close = Gtk.Button(icon_name="window-close-symbolic")
        btn_close.connect("clicked", lambda x: self.close())
        header.pack_end(btn_close); content.append(header)
        scroll = Gtk.ScrolledWindow(); scroll.set_vexpand(True); scroll.set_hexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20); box.set_margin_bottom(20); box.set_margin_start(20); box.set_margin_end(20)
        title_box = Gtk.Box(spacing=10, halign=Gtk.Align.CENTER)
        icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic"); icon.set_pixel_size(32)
        lbl = Gtk.Label(label="AI Конструктор", css_classes=["title-2"]); title_box.append(icon); title_box.append(lbl)
        box.append(title_box)
        self.pref_group = Adw.PreferencesGroup(title="Налаштування")
        self.entry_key = Adw.PasswordEntryRow(title="Gemini API Key"); self.entry_key.set_text(self.config.get_key()); self.pref_group.add(self.entry_key)
        self.entry_topic = Adw.EntryRow(title="Тема"); self.pref_group.add(self.entry_topic)
        self.combo_folder = Adw.ComboRow(title="Папка"); self.folders = self.manager.get_folders()
        model = Gtk.StringList()
        for f in self.folders: model.append(f['name'])
        self.combo_folder.set_model(model); self.pref_group.add(self.combo_folder)
        self.langs = ["Українська", "English", "Deutsch", "Polski", "Français", "Español", "Italiano", "Auto"]
        self.combo_lang_q = Adw.ComboRow(title="Мова питання (Q)"); model_q = Gtk.StringList()
        for l in self.langs: model_q.append(l); self.combo_lang_q.set_model(model_q); self.combo_lang_q.set_selected(1); self.pref_group.add(self.combo_lang_q)
        self.combo_lang_a = Adw.ComboRow(title="Мова відповіді (A)"); model_a = Gtk.StringList()
        for l in self.langs: model_a.append(l); self.combo_lang_a.set_model(model_a); self.combo_lang_a.set_selected(0); self.pref_group.add(self.combo_lang_a)
        self.spin_count = Adw.SpinRow(title="Кількість карток", subtitle="Від 3 до 50"); adjustment = Gtk.Adjustment(value=10, lower=3, upper=50, step_increment=1)
        self.spin_count.set_adjustment(adjustment); self.pref_group.add(self.spin_count)
        self.entry_context = Adw.EntryRow(title="Додаткові умови"); self.pref_group.add(self.entry_context)
        box.append(self.pref_group)
        hint = Gtk.Label(label="Наприклад: 'для дітей', 'рівень B2', 'тільки дієслова'", css_classes=["dim-label"]); hint.set_wrap(True); box.append(hint)
        self.btn_gen = Gtk.Button(label="Створити"); self.btn_gen.add_css_class("suggested-action"); self.btn_gen.add_css_class("pill"); self.btn_gen.set_size_request(200, 50); self.btn_gen.set_halign(Gtk.Align.CENTER)
        self.btn_gen.connect("clicked", self.on_generate_click); box.append(self.btn_gen)
        self.spinner = Gtk.Spinner(); self.spinner.set_size_request(32, 32); box.append(self.spinner)
        self.status_lbl = Gtk.Label(label=""); self.status_lbl.set_wrap(True); box.append(self.status_lbl)
        scroll.set_child(box); content.append(scroll); self.set_content(content)


    def on_generate_click(self, btn):
        api_key = self.entry_key.get_text().strip()
        topic = self.entry_topic.get_text().strip()
        
        if not api_key: self.status_lbl.set_text("Потрібен API Key!"); return
        if not topic: self.status_lbl.set_text("Введіть тему!"); return
            
        count = int(self.spin_count.get_value())
        idx_q = self.combo_lang_q.get_selected(); lang_q = self.langs[idx_q]
        idx_a = self.combo_lang_a.get_selected(); lang_a = self.langs[idx_a]
        context = self.entry_context.get_text().strip()
        
        self.config.set_key(api_key)
        self.btn_gen.set_sensitive(False)
        self.spinner.start()
        self.status_lbl.set_text(f"Генерую {count} карток ({lang_q} -> {lang_a})...")
        
        thread = threading.Thread(target=self.run_ai_thread, args=(api_key, topic, count, lang_q, lang_a, context))
        thread.start()

    def run_ai_thread(self, api_key, topic, count, lang_q, lang_a, context):
        try:
            cards = generate_flashcards(api_key, topic, count, lang_q, lang_a, context)
            GLib.idle_add(self.finish_success, topic, cards)
        except Exception as e:
            GLib.idle_add(self.finish_error, f"Помилка AI: {str(e)}")


    def finish_success(self, topic, cards):
        self.spinner.stop()
        self.btn_gen.set_sensitive(True)
        
        if not self.folders: self.status_lbl.set_text("Помилка: Немає папок!"); return

        f_idx = self.combo_folder.get_selected()
        target_folder = self.folders[0] if f_idx < 0 or f_idx >= len(self.folders) else self.folders[f_idx]
        
        deck = self.manager.create_deck(target_folder['id'], topic)
        for c in cards:
            self.manager.add_card(target_folder['id'], deck['id'], str(c.get('q')), str(c.get('a')))
            
        self.on_success()
        self.close()


    def finish_error(self, msg):
        self.spinner.stop()
        self.btn_gen.set_sensitive(True)
        self.status_lbl.set_text(msg)

class SmartInputDialog(Adw.Window):
    def __init__(self, parent, title, callback, needs_folder_select=False, folders=None):
        super().__init__(modal=True, default_width=400, default_height=250); self.set_transient_for(parent); self.callback = callback
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar(); header.set_show_end_title_buttons(False); btn_c = Gtk.Button(label="Скасувати"); btn_c.connect("clicked", lambda x: self.close()); header.pack_start(btn_c)
        self.btn_s = Gtk.Button(label="Створити"); self.btn_s.add_css_class("suggested-action"); self.btn_s.set_sensitive(False); self.btn_s.connect("clicked", self.on_confirm); header.pack_end(self.btn_s); content.append(header)
        group = Adw.PreferencesGroup(); group.set_margin_top(20); group.set_margin_start(20); group.set_margin_end(20); group.set_title(title)
        self.entry = Adw.EntryRow(title="Назва"); self.entry.connect("notify::text", self.on_text_changed); group.add(self.entry)
        self.combo_row = None; self.folders_map = []
        if needs_folder_select and folders:
            self.combo_row = Adw.ComboRow(title="Оберіть папку"); model = Gtk.StringList()
            for f in folders: model.append(f['name']); self.folders_map.append(f)
            self.combo_row.set_model(model); group.add(self.combo_row)
        content.append(group); self.set_content(content)
    def on_text_changed(self, e, p): self.btn_s.set_sensitive(len(e.get_text().strip()) > 0)
    def on_confirm(self, b):
        t = self.entry.get_text().strip()
        if not t: return
        if self.combo_row: self.callback(t, self.folders_map[self.combo_row.get_selected()])
        else: self.callback(t)
        self.close()

class CardInputDialog(Adw.Window):
    def __init__(self, parent, callback):
        super().__init__(modal=True, default_width=450, default_height=300); self.set_transient_for(parent); self.callback = callback
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL); header = Adw.HeaderBar(); header.set_show_end_title_buttons(False)
        btn_c = Gtk.Button(label="Відміна"); btn_c.connect("clicked", lambda x: self.close()); header.pack_start(btn_c)
        btn_a = Gtk.Button(label="Додати"); btn_a.add_css_class("suggested-action"); btn_a.connect("clicked", self.on_add); header.pack_end(btn_a)
        content.append(header); group = Adw.PreferencesGroup(); group.set_margin_top(20); group.set_margin_start(20); group.set_margin_end(20); group.set_title("Нова картка")
        self.entry_q = Adw.EntryRow(title="Питання"); self.entry_a = Adw.EntryRow(title="Відповідь"); group.add(self.entry_q); group.add(self.entry_a); content.append(group); self.set_content(content)
    def on_add(self, b):
        q = self.entry_q.get_text().strip(); a = self.entry_a.get_text().strip()
        if q and a: self.callback(q, a); self.close()
