# -*- coding: utf-8 -*-
#
#  onnu.py - A plugin for gedit
#
#  Copyright (C) 2015 - Nithin K R
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110-1301, USA.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Peas', '1.0')
gi.require_version('Gedit', '3.0')
from gi.repository import GObject, Gtk, Gdk, Gedit

common_brackets = {
    '(' : ')',
    '[' : ']',
    '{' : '}',
    '"' : '"',
    "'" : "'",
}

close_brackets = {
    ')' : '(',
    ']' : '[',
    '}' : '{',
}

language_brackets = {
    'changelog': { '<' : '>' },
    'html': { '<' : '>' },
    'xml': { '<' : '>' },
    'php': { '<' : '>' },
}


class Onnu(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "Onnu"

    view = GObject.Property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._doc = self.view.get_buffer()
        self._last_iter = None
        self._stack = []
        self._relocate_marks = True
        self.update_language()

        # Add the markers to the buffer
        insert = self._doc.get_iter_at_mark(self._doc.get_insert())
        self._mark_begin = self._doc.create_mark(None, insert, True)
        self._mark_end = self._doc.create_mark(None, insert, False)

        self._handlers = [
            None,
            None,
            self.view.connect('notify::editable', self.on_notify_editable),
            self._doc.connect('notify::language', self.on_notify_language),
            None,
        ]
        self.update_active()

    def do_deactivate(self):
        if self._handlers[0]:
            self.view.disconnect(self._handlers[0])
            self.view.disconnect(self._handlers[1])
            self._doc.disconnect(self._handlers[4])
        self.view.disconnect(self._handlers[2])
        self._doc.disconnect(self._handlers[3])
        self._doc.delete_mark(self._mark_begin)
        self._doc.delete_mark(self._mark_end)

    def update_active(self):
        # Don't activate the feature if the buffer isn't editable or if
        # there are no brackets for the language
        active = self.view.get_editable() and \
                 self._brackets is not None

        if active and self._handlers[0] is None:
            self._handlers[0] = self.view.connect('event-after',
                                                   self.on_event_after)
            self._handlers[1] = self.view.connect('key-press-event',
                                                   self.on_key_press_event)
            self._handlers[4] = self._doc.connect('delete-range',
                                                  self.on_delete_range)
        elif not active and self._handlers[0] is not None:
            self.view.disconnect(self._handlers[0])
            self._handlers[0] = None
            self.view.disconnect(self._handlers[1])
            self._handlers[1] = None
            self._doc.disconnect(self._handlers[4])
            self._handlers[4] = None

    def update_language(self):
        lang = self._doc.get_language()
        if lang is None:
            self._brackets = None
            return

        lang_id = lang.get_id()
        if lang_id in language_brackets:
            self._brackets = language_brackets[lang_id]
            # we populate the language-specific brackets with common ones lazily
            self._brackets.update(common_brackets)
        else:
            self._brackets = common_brackets

        # get the corresponding keyvals
        self._bracket_keyvals = set()
        for b in self._brackets:
            kv = Gdk.unicode_to_keyval(ord(b[-1]))
            if (kv):
                self._bracket_keyvals.add(kv)
        for b in close_brackets:
            kv = Gdk.unicode_to_keyval(ord(b[-1]))
            if (kv):
                self._bracket_keyvals.add(kv)

    def get_current_token(self):
        end = self._doc.get_iter_at_mark(self._doc.get_insert())
        start = end.copy()
        word = None

        if end.ends_word() or (end.inside_word() and not end.starts_word()):
            start.backward_word_start()
            word = self._doc.get_text(start, end)

        if not word and start.backward_char():
            word = start.get_char()
            if word.isspace():
                word = None

        if word:
            return word, start, end
        else:
            return None, None, None

    def get_next_token(self):
        start = self._doc.get_iter_at_mark(self._doc.get_insert())
        end = start.copy()
        word = None

        if start.ends_word() or (start.inside_word() and not start.starts_word()):
            end.forward_word_end()
            word = self._doc.get_text(start, end)

        if not word:
            word = start.get_char()
            if word.isspace():
                word = None

        if word:
            return word, start, end
        else:
            return None, None, None

    def compute_indentation(self, cur):
      pass

    def on_notify_language(self, view, pspec):
      pass

    def on_notify_editable(self, view, pspec):
      pass

    def on_key_press_event(self, view, event):
      pass

    def on_event_after(self, view, event):
      pass

    def on_delete_range(self, doc, start, end):
      pass
