from gi.repository import Gtk, Gdk
from GTG.gtk.browser.tag_context_menu import TagContextMenu


# NOTE: This is heavily WIP and broken code. 
# And super disorganized. It will eventually get better :)


class Sidebar():
    
    def __init__(self, app, builder):
        super().__init__()

        self.app = app
        self.builder = builder

        # Performance test
        # app.ds.fill_with_samples(400)

        listbox = builder.get_object('sidebar_list')

        box = Gtk.Box() 
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_left(12)
        box.set_margin_right(12)

        # TODO:
        # Deduplicate all this stuff
        # Figure out how to update info here (receive callbacks and stuff)
        # Adapt tagpopup and tageditor to the new DS

        # EMIT signals for:
        # - Tag clicked
        # - Tag RIGHT clicked
        
        # Receive callback for:
        # - Tag data changed
        # - Tag removed
        # - Task count update 
        # - Pane change
        # - Reparenting

        self.tagpopup = TagContextMenu(app.req, app)

        icon = Gtk.Image.new_from_icon_name(
            'emblem-documents-symbolic', 
            Gtk.IconSize.MENU
        )
        
        icon.set_margin_right(6)
        box.add(icon)

        name = Gtk.Label()
        name.set_halign(Gtk.Align.START)
        name.set_text('All Tasks')
        box.add(name)

        count = Gtk.Label()
        count.set_halign(Gtk.Align.START)
        count.set_text(str(app.ds.tasks.count()))
        count.get_style_context().add_class('dim-label')
        box.pack_end(count, False, False, 0)
        listbox.add(box)


        box = Gtk.Box() 
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_left(12)
        box.set_margin_right(12)

        icon = Gtk.Image.new_from_icon_name(
            'task-past-due-symbolic', 
            Gtk.IconSize.MENU
        )
        
        icon.set_margin_right(6)
        box.add(icon)

        name = Gtk.Label()
        name.set_halign(Gtk.Align.START)
        name.set_text('Tasks with no tags')
        box.add(name)

        listbox.add(box)

        box = Gtk.Box() 
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_left(12)
        box.set_margin_right(12)

        icon = Gtk.Image.new_from_icon_name(
            'system-search-symbolic', 
            Gtk.IconSize.MENU
        )
        
        icon.set_margin_right(6)
        box.add(icon)

        name = Gtk.Label()
        name.set_halign(Gtk.Align.START)
        name.set_text('Saved Searches')
        box.add(name)

        listbox.add(box)

        separator = Gtk.Separator()
        separator.set_sensitive(False)

        row = Gtk.ListBoxRow() 
        row.set_selectable(False)
        row.set_activatable(False)
        row.add(separator)
        listbox.add(row)

        self.rows = []

        for tag in app.ds.tags.data:
            tag_row = TagSidebarRow(tag, self)
            listbox.add(tag_row)
            self.rows.append(tag_row)

            for child in tag.children:
                tag_child = TagSidebarRow(child, self)
                listbox.add(tag_child)
                self.rows.append(tag_child)

        listbox.show_all()

        # Hide initial children
        for row in self.rows:
            if row.tag.parent:
                row.hide()



    def add_separator(self) -> None:
        ...


    def add_row(self) -> None:
        ...


    def show_children(self, tags: list) -> None:
        """show or hide children tags"""

        for row in self.rows:
            if row.tag in tags:
                if row.props.visible:
                    row.hide()
                else:
                    row.show()



class TagSidebarRow(Gtk.ListBoxRow):
    
    __gtype_name__ = 'gtg_TagSidebarRow'

    def on_expander_clicked(self, expander) -> None:
        
        if expander.get_active():
            expander.get_child().set_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU)
        else:
            expander.get_child().set_from_icon_name('pan-end-symbolic', Gtk.IconSize.MENU)

        self.bar.show_children(self.tag.children)


    def on_clicked(self, widget, event) -> None:

        if event.button == 3:
            my_tag = self.bar.app.req.get_tag(self.tag.name)
            self.bar.tagpopup.set_tag(my_tag)
            self.bar.tagpopup.popup(None, None, None, None, event.button, event.time)



    def __init__(self, tag, bar):
        super().__init__()

        self.tag = tag
        self.event_box = Gtk.EventBox()
        self.box = Gtk.Box()
        self.box.set_margin_top(8)
        self.box.set_margin_bottom(8)
        self.box.set_margin_left(12)
        self.box.set_margin_right(12)
        self.bar = bar

        # TODO:
        # Figure out how to add task counts in core branch! Probably in taskstore
        # Figure out DND

        if tag.parent:
            self.box.set_margin_left(36)


        if tag.children:
            expander = Gtk.ToggleButton()
            expander.get_style_context().add_class('flat')
            expander.set_margin_right(6)

            icon = Gtk.Image.new_from_icon_name(
                'pan-end-symbolic', 
                Gtk.IconSize.MENU
            )

            expander.add(icon)
            expander.get_style_context().add_class('flat')
            background = str.encode('* { padding: 0; min-height: 16px; min-width: 16px; background: none; border: none;}')

            cssProvider = Gtk.CssProvider()
            cssProvider.load_from_data(background)
            expander.get_style_context().add_provider(cssProvider, 
                                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)


            expander.connect('clicked', self.on_expander_clicked) 
            self.box.add(expander)


        if tag.icon:
            icon = Gtk.Label()
            icon.set_justify(Gtk.Justification.LEFT)
            icon.set_text(tag.icon)
            icon.set_margin_right(6)
            self.box.add(icon)
        elif tag.color:
            color = Gdk.RGBA()
            color.parse(f'#{tag.color}')
            hex = color.to_string()
            color_btn = Gtk.Button()
            color_btn.get_style_context().add_class('flat')
            background = str.encode('* { background: ' + hex + ' ; padding: 0; min-height: 16px; min-width: 16px;}')

            cssProvider = Gtk.CssProvider()
            cssProvider.load_from_data(background)


            color_btn.set_sensitive(False)
            color_btn.set_margin_right(6)
            color_btn.set_valign(Gtk.Align.CENTER)
            color_btn.set_halign(Gtk.Align.CENTER)
            color_btn.set_vexpand(False)
            color_btn.get_style_context().add_provider(cssProvider, 
                                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

            self.box.pack_start(color_btn, False, False, 0)
        else:
            color = Gdk.RGBA()
            color.parse(f'#{tag.color}')
            hex = color.to_string()
            color_btn = Gtk.Button()
            color_btn.get_style_context().add_class('flat')
            background = str.encode('* { border: 1px solid rgba(0,0,0,0.15); padding: 0; min-height: 16px; min-width: 16px;}')

            cssProvider = Gtk.CssProvider()
            cssProvider.load_from_data(background)

            color_btn.set_sensitive(False)
            color_btn.set_margin_right(6)
            color_btn.set_valign(Gtk.Align.CENTER)
            color_btn.set_halign(Gtk.Align.CENTER)
            color_btn.set_vexpand(False)
            color_btn.get_style_context().add_provider(cssProvider, 
                                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

            self.box.pack_start(color_btn, False, False, 0)

        name = Gtk.Label()
        name.set_halign(Gtk.Align.START)
        name.set_text(tag.name)
        self.box.add(name)

        self.event_box.add(self.box)
        self.add(self.event_box)
        self.event_box.connect('button-release-event', self.on_clicked)


