# ui/pages.py

import random
from gi.repository import Gtk, Adw
from core.database import DataManager 
from .dialogs import CardInputDialog


class StudyPage(Adw.NavigationPage):
    def __init__(self, folder_id, deck, manager, nav_view):
        tag = f"study-{deck['id']}-{random.randint(1000, 9999)}"
        super().__init__(title=deck['name'], tag=tag); self.folder_id = folder_id; self.deck = deck; self.manager = manager; self.nav_view = nav_view
        
        self.queue = deck['cards'].copy()
        random.shuffle(self.queue) 
        
        self.current_card = None; self.build_ui(); self.next_card()
    def build_ui(self):
        toolbar_view = Adw.ToolbarView(); header = Adw.HeaderBar(); toolbar_view.add_top_bar(header)
        clamp = Adw.Clamp(maximum_size=700); box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        box.set_valign(Gtk.Align.CENTER); box.set_margin_top(20); box.set_margin_bottom(20)
        self.progress_bar = Gtk.ProgressBar(); box.append(self.progress_bar)
        self.card_surface = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20); self.card_surface.add_css_class("card-display")
        self.lbl_q = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER, css_classes=["title-text"])
        self.lbl_a = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER, css_classes=["answer-text"]); self.lbl_a.set_visible(False)
        self.card_surface.append(self.lbl_q); self.card_surface.append(Gtk.Separator()); self.card_surface.append(self.lbl_a); box.append(self.card_surface)
        self.btn_show = Gtk.Button(label="Показати відповідь"); self.btn_show.add_css_class("pill"); self.btn_show.add_css_class("suggested-action")
        self.btn_show.set_size_request(200, 60); self.btn_show.set_halign(Gtk.Align.CENTER); self.btn_show.connect("clicked", self.on_show); box.append(self.btn_show)
        self.rating_box = Gtk.Box(spacing=20, halign=Gtk.Align.CENTER); self.rating_box.set_visible(False)
        btn_f = Gtk.Button(label="Не знаю"); btn_f.add_css_class("pill"); btn_f.add_css_class("destructive-action"); btn_f.set_size_request(160, 60); btn_f.connect("clicked", self.on_rate, 0)
        btn_p = Gtk.Button(label="Знаю"); btn_p.add_css_class("pill"); btn_p.add_css_class("success"); btn_p.set_size_request(160, 60); btn_p.connect("clicked", self.on_rate, 5)
        self.rating_box.append(btn_f); self.rating_box.append(btn_p); box.append(self.rating_box); clamp.set_child(box)
        self.finish_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20); self.finish_box.set_valign(Gtk.Align.CENTER)
        status = Adw.StatusPage(title="Сесію завершено!", description="Чудова робота.", icon_name="emblem-ok-symbolic")
        btn_exit = Gtk.Button(label="Завершити"); btn_exit.set_halign(Gtk.Align.CENTER); btn_exit.add_css_class("pill"); btn_exit.connect("clicked", lambda x: self.nav_view.pop())
        self.finish_box.append(status); self.finish_box.append(btn_exit)
        self.stack = Gtk.Stack(); self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.add_named(clamp, "card"); self.stack.add_named(self.finish_box, "finish")
        toolbar_view.set_content(self.stack); self.set_child(toolbar_view)
    def next_card(self):
        if not self.queue: self.stack.set_visible_child_name("finish"); return
        self.current_card = self.queue.pop(0); self.lbl_q.set_text(self.current_card['q']); self.lbl_a.set_text(self.current_card['a'])
        self.lbl_a.set_visible(False); self.btn_show.set_visible(True); self.rating_box.set_visible(False)
        total = len(self.deck['cards']); done = max(0, total - len(self.queue) - 1); self.progress_bar.set_fraction(done / total if total else 0)
    def on_show(self, btn): self.lbl_a.set_visible(True); self.btn_show.set_visible(False); self.rating_box.set_visible(True)
    def on_rate(self, btn, quality):
        self.manager.update_stats(self.folder_id, self.deck['id'], self.current_card['id'], quality)
        if quality == 0: self.queue.append(self.current_card)
        self.next_card()

class DeckPage(Adw.NavigationPage):
    def __init__(self, folder_id, deck, manager, nav_view, split_view, on_update_callback=None):
        tag = f"deck-{deck['id']}-{random.randint(1000, 9999)}"; super().__init__(title=deck['name'], tag=tag)
        self.folder_id = folder_id; self.deck = deck; self.manager = manager; self.nav_view = nav_view; self.split_view = split_view; self.on_update_callback = on_update_callback; self.build_ui()
    def build_ui(self):
        toolbar = Adw.ToolbarView(); header = Adw.HeaderBar(); btn_toggle = Gtk.Button(icon_name="view-sidebar-symbolic")
        btn_toggle.connect("clicked", lambda x: self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar())); header.pack_start(btn_toggle); toolbar.add_top_bar(header)
        scroll = Gtk.ScrolledWindow(); box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(20); box.set_margin_bottom(20); box.set_margin_start(20); box.set_margin_end(20)
        hero = Adw.PreferencesGroup(); hero_row = Adw.ActionRow(title=self.deck['name'], subtitle=f"Всього карток: {len(self.deck['cards'])}")
        hero_row.add_prefix(Gtk.Image.new_from_icon_name("folder-documents-symbolic")); hero.add(hero_row); box.append(hero)
        actions = Gtk.Box(spacing=10, halign=Gtk.Align.CENTER)
        btn_study = Gtk.Button(label=" Вчити зараз ", icon_name="media-playback-start-symbolic"); btn_study.add_css_class("pill"); btn_study.add_css_class("suggested-action"); btn_study.set_size_request(150, 50); btn_study.connect("clicked", self.on_study)
        btn_add = Gtk.Button(label=" Додати ", icon_name="list-add-symbolic"); btn_add.add_css_class("pill"); btn_add.connect("clicked", self.on_add_card)
        actions.append(btn_study); actions.append(btn_add); box.append(actions)
        self.cards_group = Adw.PreferencesGroup(title="Картки"); self.refresh_list(); box.append(self.cards_group)
        btn_del = Gtk.Button(label="Видалити колоду"); btn_del.add_css_class("destructive-action"); btn_del.connect("clicked", self.on_delete_deck); box.append(btn_del)
        clamp = Adw.Clamp(maximum_size=800); clamp.set_child(box); scroll.set_child(clamp); toolbar.set_content(scroll); self.set_child(toolbar)
    def refresh_list(self):
        if not self.deck['cards']: self.cards_group.add(Adw.ActionRow(title="Пусто", subtitle="Додайте картки")); return
        for card in self.deck['cards']:
            row = Adw.ExpanderRow(title=card['q'], subtitle=card['a']); btn = Gtk.Button(label="Видалити"); btn.add_css_class("destructive-action")
            btn.set_margin_top(10); btn.set_margin_bottom(10); btn.set_margin_start(10); btn.connect("clicked", self.on_delete_card, card['id']); row.add_row(btn); self.cards_group.add(row)
    def on_study(self, btn):
        if not self.deck['cards']: return
        self.nav_view.push(StudyPage(self.folder_id, self.deck, self.manager, self.nav_view))
    def on_add_card(self, btn):
        def _save(q, a):
            if self.manager.add_card(self.folder_id, self.deck['id'], q, a):
                self.nav_view.pop(); self.nav_view.push(DeckPage(self.folder_id, self.deck, self.manager, self.nav_view, self.split_view, self.on_update_callback))
        CardInputDialog(self.get_native(), _save).present()
    def on_delete_card(self, btn, cid):
        self.manager.delete_card(self.folder_id, self.deck['id'], cid); self.nav_view.pop(); self.nav_view.push(DeckPage(self.folder_id, self.deck, self.manager, self.nav_view, self.split_view, self.on_update_callback))
    def on_delete_deck(self, btn):
        dialog = Adw.MessageDialog(heading="Видалити?", body="Незворотно.", transient_for=self.get_native())
        dialog.add_response("cancel", "Ні"); dialog.add_response("delete", "Так"); dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        def _r(d, r):
            if r == "delete":
                self.manager.delete_deck(self.folder_id, self.deck['id']);
                if self.on_update_callback: self.on_update_callback()
                self.nav_view.pop()
        dialog.connect("response", _r); dialog.present()