# ui/windows.py

from gi.repository import Gtk, Adw, Gio, Gdk

from core.database import DataManager
from core.ai_service import HAS_AI
from core.config import APP_ID, CSS_FILE

from .pages import DeckPage, StudyPage
from .dialogs import SmartInputDialog, AIGeneratorDialog

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="BrainVault")
        self.set_default_size(1100, 700)
        self.manager = DataManager()
        
        # ... (Код побудови UI MainWindow без змін, лише імпорти замінені) ...
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_sidebar_width_fraction(0.25); self.split_view.set_min_sidebar_width(250)
        self.sidebar_list = Gtk.ListBox(); self.sidebar_list.add_css_class("navigation-sidebar")
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.sidebar_list)
        sb_toolbar = Adw.ToolbarView(); sb_toolbar.set_content(scroll)
        sb_header = Adw.HeaderBar(); sb_header.set_show_end_title_buttons(False)
        sb_header.set_title_widget(Gtk.Label(label="Бібліотека", css_classes=["title-2"])); sb_toolbar.add_top_bar(sb_header)
        btm = Gtk.HeaderBar(); btm.set_show_title_buttons(False)
        btn_ai = Gtk.Button(icon_name="system-search-symbolic", tooltip_text="AI Генератор"); btn_ai.add_css_class("suggested-action")
        if not HAS_AI: btn_ai.set_sensitive(False)
        btn_ai.connect("clicked", self.on_ai_click); btm.pack_start(btn_ai)
        b1 = Gtk.Button(label="Папка", icon_name="folder-new-symbolic"); b1.connect("clicked", self.on_new_folder)
        b2 = Gtk.Button(label="Колода", icon_name="list-add-symbolic"); b2.connect("clicked", self.on_new_deck)
        btm.pack_start(b1); btm.pack_end(b2); sb_toolbar.add_bottom_bar(btm); self.split_view.set_sidebar(sb_toolbar)
        self.nav_view = Adw.NavigationView()
        status = Adw.StatusPage(title="BrainVault", description="Оберіть колоду", icon_name="folder-documents-symbolic")
        home_toolbar = Adw.ToolbarView(); home_header = Adw.HeaderBar(); btn_menu = Gtk.Button(icon_name="view-sidebar-symbolic")
        btn_menu.connect("clicked", lambda x: self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar()))
        home_header.pack_start(btn_menu); home_toolbar.add_top_bar(home_header); home_toolbar.set_content(status)
        home_page = Adw.NavigationPage(title="Home", tag="home"); home_page.set_child(home_toolbar); self.nav_view.add(home_page); self.split_view.set_content(self.nav_view)
        self.toast_overlay = Adw.ToastOverlay(); self.toast_overlay.set_child(self.split_view); self.set_content(self.toast_overlay); self.refresh_sidebar()

    # ... (Усі методи MainWindow – без змін) ...
    def refresh_sidebar(self):
        self.sidebar_list.remove_all(); folders = self.manager.get_folders()
        for f in folders:
            row = Adw.ExpanderRow(title=f['name'], subtitle=f"{len(f['decks'])} тем"); row.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))
            btn_del = Gtk.Button(icon_name="user-trash-symbolic"); btn_del.add_css_class("flat"); btn_del.add_css_class("destructive-action")
            btn_del.connect("clicked", self.on_delete_folder_click, f); row.add_suffix(btn_del)
            for d in f['decks']:
                dr = Adw.ActionRow(title=d['name']); dr.add_prefix(Gtk.Image.new_from_icon_name("format-justify-fill-symbolic"))
                btn = Gtk.Button(icon_name="go-next-symbolic"); btn.add_css_class("flat")
                btn.connect("clicked", lambda b, fi=f['id'], de=d: self.open_deck(fi, de)); dr.add_suffix(btn); row.add_row(dr)
            lb = Gtk.ListBoxRow(); lb.set_child(row); lb.set_selectable(False); self.sidebar_list.append(lb)
    def on_delete_folder_click(self, btn, folder):
        dialog = Adw.MessageDialog(heading="Видалити папку?", body=f"'{folder['name']}' буде видалено.", transient_for=self)
        dialog.add_response("cancel", "Ні"); dialog.add_response("delete", "Так"); dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        def _r(d, r):
            if r == "delete": self.manager.delete_folder(folder['id']); self.refresh_sidebar(); self.show_toast("Папку видалено")
        dialog.connect("response", _r); dialog.present()
    def open_deck(self, fid, d): self.nav_view.push(DeckPage(fid, d, self.manager, self.nav_view, self.split_view, on_update_callback=self.refresh_sidebar))
    def on_new_folder(self, btn):
        def _c(n): self.manager.create_folder(n); self.refresh_sidebar()
        SmartInputDialog(self, "Нова папка", _c).present()
    def on_new_deck(self, btn):
        fs = self.manager.get_folders()
        if not fs: self.show_toast("Немає папок!"); return
        def _c(n, f=None):
            tid = f['id'] if f else fs[0]['id']; self.manager.create_deck(tid, n); self.refresh_sidebar()
        SmartInputDialog(self, "Нова колода", _c, True, fs).present()
    def on_ai_click(self, btn): AIGeneratorDialog(self, self.manager, self.refresh_sidebar).present()
    def show_toast(self, msg): self.toast_overlay.add_toast(Adw.Toast.new(msg))


class App(Adw.Application):
    def __init__(self): 
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_startup(self):
        Adw.Application.do_startup(self)
        
        # Завантаження CSS з окремого файлу
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path(CSS_FILE)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            raise "Помилка завантаження CSS: {e}"

    def do_activate(self):
        win = self.props.active_window
        if not win: 
            win = MainWindow(self)
        win.present()