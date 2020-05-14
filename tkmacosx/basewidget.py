#                       Copyright 2020 Saad Mairaj
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from __future__ import annotations
from dataclasses import dataclass, field
from tkinter import ttk
import tkinter as _TK
import re
import subprocess
from math import floor, ceil
from typing import Iterable

try: 
    import colour as C
except Exception as e:
    import sys, os
    import tkinter.messagebox as ms
    Error_win = _TK.Tk()
    Error_win.withdraw()
    message = """
    Module "tkmacosx" is dependent on 
    "colour" Module. 

    Do you want to install it with pip now?
    Or install it manually later.
    
    Link to the colour github:
    https://github.com/vaab/colour"""
    if ms._show(e, message, 'warning', 'yesno')=='yes':
        Error_win.destroy()
        os.system('pip install colour')
        import colour as C
    else: 
        sys.exit(0)


def to_tuple(v) -> tuple:
    return (v,) if isinstance(v, str) else tuple(v)


def check_appearence(cmd='defaults read -g AppleInterfaceStyle'):
    """### Checks DARK/LIGHT mode of macos. Returns Boolean.
    #### Args:
    - `cmd`: Give commands. Like to check DARK/LIGHT mode the command is `'defaults read -g AppleInterfaceStyle'` .
    """
    out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, shell=True).communicate()
    if out: return True
    elif err: return False


def get_shade(color, shade: float, mode='auto'):
    """### Darken or Lghten a shade of A HEX color.
    #### Args:
    1. `color`: Give a color as either HEX or name of the color.
    2. `shade`: The amount of change required. Takes float. eg: shade=0.225.
    3. `mode`: 
        - `'-'` for darker shade.
        - `'+'` for lighter shade.
        - `'auto-110'` automatically decide lighter or darker. where 110 is the intensity.
    
    return hexcode"""
    if isinstance( color, str ):
        if color.startswith('#'):
            Hex = color.lstrip('#')
            color = tuple( int(Hex[i:i+2], 16) for i in (0, 2, 4) )
        else:  
            tmp = _TK.Frame()
            r,g,b = tmp.winfo_rgb(color)
            tmp.destroy()
            color = (r/257, g/257, b/257)
    if 'auto' in mode:
        intensity = 110.0 if len(mode)<=4 else float(mode.split('-')[1])
        mode = '-' if float(color[0]*0.299 + color[1]*0.587 \
                        + color[2]*0.114) > intensity else '+'
    if mode == '+':
        R = float(color[0]*(1-shade) + shade*255) \
                if float(color[0]*(1-shade) + shade*255) > 0 else 0.0
        G = float(color[1]*(1-shade) + shade*255) \
                if float(color[1]*(1-shade) + shade*255) > 0 else 0.0
        B = float(color[2]*(1-shade) + shade*255) \
                if float(color[2]*(1-shade) + shade*255) > 0 else 0.0
    elif mode == '-':
        R = float(color[0]*(1-shade) - shade*255) \
                if float(color[0]*(1-shade) - shade*255) > 0 else 0.0
        G = float(color[1]*(1-shade) - shade*255) \
                if float(color[1]*(1-shade) - shade*255) > 0 else 0.0
        B = float(color[2]*(1-shade) - shade*255) \
                if float(color[2]*(1-shade) - shade*255) > 0 else 0.0
    else: raise ValueError ('Invalid mode "{}"'. format(mode))
    return '#%02x%02x%02x' % (int(R),int(G),int(B))  


class _Frame(_TK.BaseWidget):
    """Don't use this Frame widget. The widget has no geometry manager.
    
    It is used in SFrame widget to support screen."""
    def __init__(self, master=None, cnf={}, **kw):
        cnf = _TK._cnfmerge((cnf, kw))
        _TK.BaseWidget.__init__(self, master, 'frame', cnf, {})


class _Canvas(_TK.Widget):
    """Internal Class especially for Button widget"""
    def __init__(self, master=None, cnf={}, **kw):
        super(_Canvas, self).__init__(master, 'canvas', cnf, kw)
    
    def find(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'find') + args)) or ()
    
    def bbox(self, *args):
        """Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
        which encloses all items with tags specified as arguments."""
        return self._getints(
            self.tk.call((self._w, 'bbox') + args)) or None
    
    def coords(self, *args):
        """Return a list of coordinates for the item given in ARGS."""
        return [
            self.tk.getdouble(x) \
                for x in self.tk.splitlist(self.tk.call((self._w, 'coords') + args))
        ]
    
    def _create(self, itemType, args, kw): # Args: (val, val, ..., cnf={})
        """Internal function."""
        args = _TK._flatten(args)
        cnf = args[-1]
        if isinstance(cnf, (dict, tuple)):
            args = args[:-1]
        else:
            cnf = {}
        return self.tk.getint(self.tk.call(
            self._w, 'create', itemType,
            *(args + self._options(cnf, kw))))
    
    def _arc(self, *args, **kw):
        """Create arc shaped region with coordinates x1,y1,x2,y2."""
        return self._create('arc', args, kw)
    
    def _bitmap(self, *args, **kw):
        """Create bitmap with coordinates x1,y1."""
        return self._create('bitmap', args, kw)
    
    def _image(self, *args, **kw):
        """Create image item with coordinates x1,y1."""
        return self._create('image', args, kw)
    
    def _line(self, *args, **kw):
        """Create line with coordinates x1,y1,...,xn,yn."""
        return self._create('line', args, kw)
    
    def _text(self, *args, **kw):
        """Create text with coordinates x1,y1."""
        return self._create('text', args, kw)
    
    def _rectangle(self, *args, **kw):
        """Create rectangle with coordinates x1,y1,x2,y2."""
        return self._create('rectangle', args, kw)
    
    def _polygon(self, *args, **kw):
        """Create polygon with coordinates x1,y1,x2,y2,..."""
        return self._create('polygon', args, kw)
    
    def delete(self, *args):
        """Delete items identified by all tag or ids contained in ARGS."""
        self.tk.call((self._w, 'delete') + args)
    
    def itemcget(self, tagOrId, option):
        """Return the resource value for an OPTION for item TAGORID."""
        return self.tk.call(
            (self._w, 'itemcget') + (tagOrId, '-'+option))
    
    def itemconfigure(self, tagOrId, cnf=None, **kw):
        """Configure resources of an item TAGORID.

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method without arguments.
        """
        return self._configure(('itemconfigure', tagOrId), cnf, kw)
    itemconfig = itemconfigure

    def tag_lower(self, *args):
        """Lower an item TAGORID given in ARGS
        (optional below another item)."""
        self.tk.call((self._w, 'lower') + args)
    lower = tag_lower

    def tag_raise(self, *args):
        """Raise an item TAGORID given in ARGS
        (optional above another item)."""
        self.tk.call((self._w, 'raise') + args)
    lift = tkraise = tag_raise

    def rounded_rect(self, x, y, w, h, c, tag1=None, tag2=None, **kw) -> _TK.Widget:
        hc = c * 1 / 3
        bdw = kw.get('width', 0)
        hbdw = bdw / 2
        x0 = floor(x + hbdw)
        y0 = floor(y + hbdw)
        x1 = floor(x + w - (hbdw + 1))
        y1 = floor(y + h - (hbdw + 1))
        bdpoints = [
            floor(x0 + hc), floor(y0 + hc),
            x0 + c, y0,
            x1 - c, y0,
            floor(x1 - hc), ceil(y0 + hc),
            x1, y0 + c,
            x1, floor(y1 - c),
            floor(x1 - hc), floor(y1 - hc),
            x1 - c, y1,
            x0 + c, y1,
            floor(x0 + hc), floor(y1 - hc),
            x0, y1 - c,
            x0, y0 + c,
            floor(x0 + hc), floor(y0 + hc),
        ]
        features = {
            'outline': '', 
            'fill': 'white',
            'tag': tag1,
            #'joinstyle': _TK.ROUND,
            'width': 2
        }
        features.update(kw)
        return self._polygon(*bdpoints, **features)

    def rounded_rect_original(self, x, y, w, h, c, tag1=None, tag2=None, **kw):
        'Internal function.'
        # Need fix to just have one tag to change the background color
        kw['extent'] = 90
        kw['style'] = 'arc'
        kw['outline'] = kw.pop('fill', 'black')
        if tag1: kw['tag'] = tag1
        self._arc(x,       y,        x+2*c,   y+2*c,   start= 90, **kw) # NW
        self._arc(x+w-2*c-6, y+h-2*c-6,  x+w,     y+h, start=270, **kw) # SE
        self._arc(x+w-2*c, y,        x+w,     y+2*c,   start=  0, **kw) # NE
        self._arc(x,       y+h-2*c,  x+2*c+4,   y+h,     start=180, **kw) # SW
        kw.pop('extent', None)
        kw.pop('style', None)
        kw['fill'] = kw.pop('outline', None)
        if tag2: kw['tag'] = tag2
        self._line(x+c, y,   x+w-c, y    , **kw) # N
        self._line(x+c+2, y+h, x+w-c-1, y+h  , **kw) # S
        self._line(x,   y+c, x,     y+h-c, **kw) # W
        self._line(x+w, y+c, x+w,   y+h-c-1, **kw) # E

    def _rounded(self, x1, y1, x2, y2, r, **kw):
        self._arc(x1,  y1,  x1+r,   y1+r, start= 90, extent=90, style='pieslice', outline='', **kw)
        self._arc(x2-r-1, y1, x2-1, y1+r, start=  0, extent=90, style='pieslice', outline='', **kw)
        self._arc(x1, y2-r-1, x1+r, y2-1, start=180, extent=90, style='pieslice', outline='', **kw)
        self._arc(x2-r, y2-r, x2-1, y2-1, start=270, extent=90, style='pieslice', outline='', **kw)
        self._rectangle(x1+r/2, y1, x2-r/2, y2, width=0, **kw)
        self._rectangle(x1, y1+r/2, x2, y2-r/2, width=0, **kw)


@dataclass(frozen=True)
class WidgetState:
    value:str
    description:str = field(default=None, repr=False, compare=False)
    implies:tuple = field(default_factory=tuple, repr=False, compare=False)
    negates:tuple = field(default_factory=tuple, repr=False, compare=False)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.value)

    @classmethod
    def by_value(cls, value, all_states, allow_missing=True) -> WidgetState:
        result = None
        if isinstance(value, WidgetState):
            if value in all_states:
                result = value
        elif isinstance(value, str):
            for st in all_states:
                if st.value == value:
                    result = st
                    break
        elif isinstance(value, Iterable):
            result = tuple([ 
                cls.by_value(x, all_states, allow_missing=allow_missing) \
                for x in value 
            ])
        if not result and allow_missing:
            raise ValueError("Element not found: {}".format(value))
        else:
            return result

    @classmethod
    def expanded_states(cls, state, all_states) -> tuple:
        '''
        Expands given state to all of its implied states,
        retrieving those from given all_states set.
        '''
        if not isinstance(state, WidgetState):
            state = cls.by_value(state, all_states)
        result = [ state ]
        for implied_state_value in state.implies:
            result.append(cls.by_value(implied_state_value, all_states))
        return result

    def matches(self, required_states, valid_states) -> bool:
        '''
        Tells whether current state matches, either by identity or by implication,
        *all* of the required state(s).
        '''
        required_states = WidgetState.by_value(to_tuple(required_states), valid_states)
        current_states = WidgetState.expanded_states(self, valid_states)
        for reqst in required_states:
            if required_states not in current_states:
                return False
        return True

    @classmethod
    def value_of(cls, states):
        '''
        Returns the string value, or tuple of values for the specified state(s).
        If states is a string, the same string is returned.
        If states is a WidgetState object, its value property is returned.
        If states is an iterable object, a tuple with the corresponding values is returned.
        In any other case, ValueError is raised
        '''
        if isinstance(states, str):
            return states
        elif isinstance(states, WidgetState):
            return states.value
        elif isinstance(states, Iterable):
            return to_tuple([ cls.value_of(x) for x in states ])
        else:
            raise ValueError("Wrong type, must be one of {}"\
                .format((WidgetState, str, Iterable)))


class Widget(_Canvas):
    """Internal class used for tkinter macos Buttton"""

    _instances = []  # list of all buttons
    _features = [  
        'activebackground',
        'activebitmap', 
        'pressedbordercolor', 
        'activeborderwidth',
        'activeforeground', 
        'activeimage', 
        'anchor', 
        'background', 'bg', 
        'bitmap', 
        'bordercolor', 
        'borderwidth', 'bd', 
        'command', 
        'compound', 
        'cornerrounding', 
        'disabledbackground', 
        'disabledbitmap', 
        'disabledbordercolor', 
        'disabledborderwidth', 
        'disabledforeground', 
        'innerbackground', 'innerbg',
        'foreground', 'fg',
        'font', 
        'height', 
        'image', 
        'overrelief', 
        'padx', 
        'pady', 
        'pressedbackground', 
        'pressedbitmap', 
        'pressedbordercolor', 
        'pressedborderwidth', 
        'pressedforeground', 
        'repeatdelay', 
        'repeatinterval', 
        'text', 
        'textvariable', 
        'underline', 
        'width' 
    ]

    valid_states = (
        WidgetState(
            value='disabled', 
            description="Widget will ignore user interaction", 
            negates='*'),
        WidgetState(
            value='normal', 
            description="Widget will accept user interaction", 
            negates=('disabled',)),
        WidgetState(
            value='active', 
            description="Mouse entered the widget (hovers directly over it)", 
            implies=('normal',),
            negates=('disabled',)),
        WidgetState(
            value='focus', 
            description="Widget is ready to accept user input", 
            implies=('normal',),
            negates=('disabled',)),
        WidgetState(
            value='pressed', 
            description="Widget is being pressed (tipically mouse button or action key pressed)", 
            implies=('normal', 'focus',),
            negates=('disabled',)),
    )

    repaint_fps = 50

    def __init__(self, master=None, cnf={}, **kw):
        kw = _TK._cnfmerge( (cnf, kw) )
        kw = { k:v for k,v in kw.items() if v is not None }
        self.stopped = None
        self.cnf = {}
        for i in kw.copy().keys():
            if i in self._features: self.cnf[i] = kw.pop(i, None)

        self.cnf['bg'] = self.cnf.get('bg', None) or self.cnf.get('background', '#dddddd')
        self.cnf['fg'] = self.cnf.get('fg', None) or self.cnf.get('foreground', 'black')
        self.cnf['bd'] = self.cnf.get('bd', None) or self.cnf.get('borderwidth', 4)
        self.cnf['innerbg'] = self.cnf.get('innerbg', None) or self.cnf.get('innerbackground', '#eeeeee')
        self.cnf['cornerrounding'] = int(self.cnf.get('cornerrounding', 0))
        self.cnf['borderwidth'] = int(self.cnf.get('borderwidth', 0))
        self.cnf['borderless'] = self.cnf['borderwidth'] == 0
        self.cnf['disabledforeground'] = self.cnf.get('disabledforeground', 'grey')
        if self.cnf.get('textvariable') is not None: self.cnf['text'] = self.cnf['textvariable'].get()
        self.cnf['anchor'] = self.cnf.get('anchor', 'center')

        kw['takefocus'] = kw.get('takefocus', 1)
        kw['highlightthickness'] = kw.get('highlightthickness', 0)
        kw['width'] = kw.get('width', 87)
        kw['height'] = kw.get('height', 24)

        super(Widget, self).__init__(master=master, **kw)
        self._instances.append(self)
        self.__state:WidgetState = None
        self._has_focus = False
        self._mouse_in = False
        self._pressed = False
        self._invalidated = False
        self._innerbg_id = ''
        self._compute_state()
        self._size = (self.winfo_width(), self.winfo_height())
        if self.cnf.get('text'): self._text(0,0,text=None, tag='_txt')
        if self.cnf.get('image'): self._image(0,0,image=None, tag='_img')
        elif self.cnf.get('bitmap'): self._bitmap(0,0,image=None, tag='_bit')
        self.bind_class('mouse_enter', '<Enter>', self.on_mouse_enter, '+')
        self.bind_class('mouse_leave', '<Leave>', self.on_mouse_leave, '+')
        self.bind_class('button_release', '<ButtonRelease-1>', self.on_release, '+')
        self.bind_class('button_press', '<Button-1>', self.on_press, '+' )
        self.bind_class('set_size', '<Configure>', self._set_size, '+')
        self.original_bg = self['bg']

        #  Focus in and out effect 
        main_win =  self.winfo_toplevel()
        def _chngIn(evt):
            #print("chngIn", evt.widget, evt)
            if self.focus_get() is None:
                color = get_shade(self['bg'], 0.04, 'auto-120')
                self.itemconfig('_border1', outline=color)
                self.itemconfig('_border2', fill=color)
            if self.focus_get() and get_shade(self['bg'], 0.04, 'auto-120') == self.itemcget('_border2','fill'):
                color = get_shade(self['bg'], 0.1, 'auto-120')
                self.itemconfig('_border1', outline=color)
                self.itemconfig('_border2', fill=color)
        main_win.bind_class(main_win,'<FocusIn>', _chngIn, '+')
        main_win.bind_class(main_win,'<FocusOut>', _chngIn, '+')
        self._reconfigure(self.cnf)

    @property
    def richstate(self) -> WidgetState:
        return self.__state

    @richstate.setter
    def richstate(self, value):
        '''
        Updates widget's current (rich) state as defined by the corresponding WidgetState.
        Note that states are not necessarily mutually exclusive, and may even imply others.
        '''
        norm_value = WidgetState.by_value(value, self.valid_states)
        if not norm_value:
            raise ValueError("Invalid state, must be one of " + str(self.valid_states.keys()))
        self.__state = value
        self.invalidate_ui()

    def _init_widget(self):
        cr = self.cnf['cornerrounding']
        innerbgcolor = self.cnf.get('innerbackgroundg')
        bdw = int(self.cnf.get('borderwidth', 1))
        bdcolor = self.cnf.get('bordercolor', get_shade(self['bg'], 0.04, 'auto-120'))
        width, height = self._size
        if self._innerbg_id:
            #TODO: destroy previous widget
            pass
        tag_id = '_innerbgXXXXXX'
        #self._innerbg_id = self.rounded_rect(0, 0, width, height, cr, tag1=tag_id)
        self._innerbg_id = self.rounded_rect(0, 0, width, height, cr, 
            width=bdw, fill=innerbgcolor, outline=bdcolor,
            tag1=tag_id)
        self.invalidate_ui()

    def _compute_state(self, force_invalidate:bool=False):
        ws = self['state']
        rs = self.richstate
        new_rs = None
        if ws == 'disabled':
            new_rs = 'disabled'
        else:
            new_rs = 'normal'
            if self._pressed:
                new_rs = 'pressed'
            else:
                if self._has_focus:
                    new_rs = 'focus'
                if self._mouse_in:
                    new_rs = 'active'
        new_rs = WidgetState.by_value(new_rs, self.valid_states, allow_missing=False)
        print("Widget {} state = {}".format(self, new_rs))
        if force_invalidate or new_rs != rs:
            self.richstate = new_rs

    def invalidate_ui(self):
        '''
        Marks this widget as having pending UI updates and schedules
        a repaint at a later time.
        '''
        self._invalidated = True
        self.after(1000 // self.repaint_fps, self.repaint_if_necessary)

    def _set_size(self, *ags):
        print("Setting size ", str(ags))
        """Internal function. This will resize everything that is in the button"""
        if ags[0].width == self._size[0] and ags[0].height == self._size[1]: return
        width = ags[0].width
        height = ags[0].height
        self._size = (width, height)
        self._init_widget()
        self.delete('_innerbg')
        self.delete('_activebg')
        self.delete('_bd_color1')
        self.delete('_bd_color2')
        self.delete('_border1')
        self.delete('_border2')
        self.delete('_tf')
        # Need fix (laggy on resizing) ----> workaround: cancel if still resizing 
        if self.stopped: 
            self.after_cancel(self.stopped)

        self.stopped = self.after(50, lambda: self.on_press_color(tag='_innerbg', 
            width=width, height=height, color=self.cnf.get('activebackground')))
        #if bdw > 0:
        #    self.rounded_rect(0, 0, width-4, height-4, bdw,
        #        width=bdw + 2, fill=bdcolor, tag1='_border1', tag2='_border2')
        # Focus halo for Mac
        #self.rounded_rect(4, 4, width-4, height-3, 4, width=2, fill='green', tag='_tf', state='hidden')
        self.coords('_txt', width/2, height/2)
        self.coords('_img', width/2, height/2)
        self.coords('_bit', width/2, height/2)
        self._compound(self.cnf.get('compound'), width=width, height=height)
        self.tag_raise('_txt')
        self.tag_raise('_img')
        self.tag_raise('_bit')
        self.tag_raise('_tf')
        self.after(50, self._reconfigure)
        # self.master.focus()
        ## NEED TESTS:- 
        ## if this is really needed, then change master with root 
        ## window as this set focus to entry widget if the master is in an entry widget.

    def on_mouse_enter(self, *a):
        print("Entering widget", str(a))
        self._mouse_in = True
        self._compute_state()

    def on_mouse_leave(self, *a):
        print("Leaving widget", str(a))
        self._mouse_in = False
        self._compute_state()

    def on_press(self, *ags):
        ''' Internal function. When button is pressed <Button-1>'''
        if self.richstate.matches('disabled', self.valid_states):
            return
        self._pressed = True
        self._compute_state()

        self._rpin = None
        self._rpinloop = True

        def cmd(*a):
            print("Executing command", str(a))
            self.cnf['command']() if self.cnf.get('command') else None
            self.unbind_class('button_command', '<ButtonRelease-1>')
            if self._rpinloop and self.cnf.get('repeatdelay', 0) and self.cnf.get('repeatinterval', 0):
                self._rpin = self.after(self.cnf.get('repeatinterval', 0), cmd)

        def on_enter(*a):
            print("Entering widget", str(a))
            self._mouse_in = True
            self._compute_state()
            self.itemconfig('_activebg', state='normal')
            self.itemconfig('_border1', state='hidden')
            self.itemconfig('_border2', state='hidden')
            if self.cnf.get('repeatdelay', 0) and self.cnf.get('repeatinterval', 0):
                self._rpinloop = True
                cmd()
            self.bind_class('button_command', '<ButtonRelease-1>', 
                lambda *a: self.after(0, cmd), '+')

        def on_leave(*a):
            self._mouse_in = False
            self._compute_state()
            print("Leaving widget", str(a))
            self.itemconfig('_activebg', state='hidden')
            self.itemconfig('_border1', state='normal')
            self.itemconfig('_border2', state='normal')
            if self.cnf.get('repeatdelay',0) and self.cnf.get('repeatinterval', 1):
                self._rpinloop = False
                self.after_cancel(self._rpin)
            self.unbind_class('button_command', '<ButtonRelease-1>')

        if self['state'] == 'normal':
            self.focus_set()
            self.itemconfig('_activebg', state='normal')
            self.itemconfig('_border1', state='hidden')
            self.itemconfig('_border2', state='hidden')
            self.bind_class('on_press_enter', '<Enter>', on_enter, '+')
            self.bind_class('on_press_leave', '<Leave>', on_leave, '+')
            if self.cnf.get('repeatdelay',0) and self.cnf.get('repeatinterval', 1):
                self._rpin = self.after(self.cnf.get('repeatdelay',0), cmd)
            self.bind_class('button_command', '<ButtonRelease-1>', cmd, '+')
            
    def on_release(self, *ags):
        self._pressed = False
        self._compute_state()
        return
        '''Internal function. When button is released <ButtonRelease-1>'''
        if self['state'] == 'normal':
            self.itemconfig('_activebg', state='hidden')
            self.itemconfig('_border1', state='normal')
            self.itemconfig('_border2', state='normal')
            self.unbind_class('on_press_enter', '<Enter>')
            self.unbind_class('on_press_leave', '<Leave>')
            self.unbind_class('button_command', '<ButtonRelease-1>')
            self._rpinloop = False
            if self._rpin: self.after_cancel(self._rpin)

    def repaint(self):
        self._invalidated = False
        if not self._innerbg_id: return
        
        state = self['state']
        richstate = self.richstate
        print("Repainting {} state={}, richstate={}".format(self, state, self.richstate))
        bg_updates = self._generate_updates_from_state(richstate, {
            'fill': ('background', 'inner'),
            'outline': ('bordercolor',),
            'width': ('borderwidth',),
        })
        print("Updates to button base: ", str(bg_updates))
        self.itemconfig(self._innerbg_id, **bg_updates)
        txt_updates = self._generate_updates_from_state(richstate, {
            'color': ('foreground',),
        })
        #print("Updates to label: ", str(txt_updates))
        #self.itemconfig('_txt', **txt_updates)

    def repaint_if_necessary(self):
        if self._invalidated:
            self.repaint()

    def _generate_updates_from_state(self, richstate, mappings):
        cfg = self.cnf.get
        updates = {}
        for prop, mapping in mappings.items():
            normal_prefix = mapping[1] if len(mapping) > 1 else ''
            prefix = normal_prefix if richstate.value == 'normal' else richstate.value
            mapped_prop = prefix + mapping[0]
            v = cfg(mapped_prop, None)
            if v is None and richstate.value != 'normal':
                v = cfg(mapped_prop, None)
            if v:
                updates[prop] = v
        return updates

    def _configure(self, cmd, cnf=None, kw=None):
        'Internal function to configure the inherited class'
        return super()._configure(cmd, cnf, kw)

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget.

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.

        Returns tuple of 2 configuration settings info, if any
        """
        kw = _TK._cnfmerge( (cnf, kw) )
        cnf = {}
        for i in list(kw):
            if i in self._features: 
                cnf[i] = kw.pop(i,None)
        r1 = super().configure(**kw)
        if kw.get('bg') or kw.get('background'):
            self.original_bg = self['bg']
        self.after(10, self._reconfigure, cnf)
        if r1 is not None:
            r1.update(self.cnf)
        return r1
    config = configure

    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key in self._features: return self.cnf[key]
        else: return super().cget(key)
    __getitem__ = cget

    def _reconfigure(self, cnf={}, **kw):
        """Internal Function.
        This function configure all the resouces of the Widget and save it to the class dict."""
        kw = _TK._cnfmerge( (cnf, kw) )
        kw = { k:v for k,v in kw.items() if v is not None }        
        self.cnf.update(kw)
        self.cnf = { k:v for k, v in self.cnf.items() if v is not None }
        self.cnf['fg'] = self.cnf.get('fg') if self.cnf.get('fg', None) else self.cnf.get('foreground','black')
        self.cnf['bd'] = self.cnf.get('bd') if self.cnf.get('bd', None) else self.cnf.get('borderwidth',6)
        if self.cnf.get('textvariable') is not None: self.cnf['text'] = self.cnf['textvariable'].get()

        if self['state'] == 'disabled':
            super().configure(bg=self.cnf.get('disabledbackground'))
        elif self['state'] == 'normal':
            super().configure(bg=self.original_bg)

        self._rel = self['relief']
        if self.cnf.get('overrelief') is not None:
            self._rel = self['relief']
            self.bind_class("overrelief", "<Enter>", lambda _: self.config(relief=kw['overrelief']), '+')
            self.bind_class("overrelief", "<Leave>", lambda _: self.config(relief=self._rel), '+')
        else:
            self.unbind_class('overrelief', '<Enter>')
            self.unbind_class('overrelief', '<Leave>')
            self._configure('configure', { 'relief': self._rel }, kw=None)
        
        if kw.get('activebackground') is not None:
            self.on_press_color(tag='_innerbg', width=self.winfo_reqwidth(), 
                height=self.winfo_reqheight(), color=self.cnf.get('activebackground'))
            self.tag_lower('_activebg')
        elif kw.get('activebackground') is '': 
            self.cnf.pop('activebackground', None)
            self.on_press_color(tag='_innerbg', width=self.winfo_reqwidth(), 
                height=self.winfo_reqheight(), color=None)
        
        if kw.get('activeforeground') is not None:
            self.bind_class('active_fg','<Enter>', lambda _:self.itemconfig('_txt',fill=kw['activeforeground'] ))
            self.bind_class('active_fg','<Leave>', lambda _:self.itemconfig('_txt',fill=self.cnf.get('fg','black')) )
        elif kw.get('activeforeground') is '':
            self.unbind_class('active_fg','<Enter>')
            self.unbind_class('active_fg','<Leave>')
            self.itemconfig('_txt',fill=self.cnf.get('fg','black'))
        
        for set_size_if in ('text', 'font', 'textvariable', 'image', 'bitmap', 
                            'compound', 'padx', 'pady', 'width', 'height'):
            if kw.get(set_size_if) is not None:
                W, H = self._info_button(
                        text = self.cnf.get('text'), 
                        font = self.cnf.get('font'), 
                        image = self.cnf.get('image'),
                        bitmap = self.cnf.get('bitmap'),
                        padding = ( self.cnf.get('padx',0), self.cnf.get('pady',0) ), 
                        compound = self.cnf.get('compound'),
                        textvariable = self.cnf.get('textvariable') )
                W = kw.get('width', W)
                H = kw.get('height', H)
                self._configure('configure', { 'width': W, 'height': H })
                break

        if self.cnf.get('image'):
            if kw.get('activeimage') is not None:
                self.bind_class('active_img','<Enter>', lambda _:self.itemconfig('_img',image=kw['activeimage'])   )
                self.bind_class('active_img','<Leave>', lambda _:self.itemconfig('_img',image=self.cnf.get('image'))   )
            elif kw.get('activeimage') is '':
                self.unbind_class('active_img','<Enter>')
                self.unbind_class('active_img','<Leave>')
                self.itemconfig('_img',image=self.cnf.get('image'))
            # For Image config
            config_cnf_img = {}
            for i in ('anchor', 'image'):
                config_cnf_img.update( {i : kw.get(i, self.cnf.get(i))} )
            self.itemconfig('_img', config_cnf_img, state=self['state'])
        elif self.cnf.get('bitmap'):
            if kw.get('activebitmap') is not None:
                self.bind_class('active_bit','<Enter>', lambda _:self.itemconfig('_bit',image=kw['activebitmap'])   )
                self.bind_class('active_bit','<Leave>', lambda _:self.itemconfig('_bit',image=self.cnf.get('bitmap'))   )
            elif kw.get('activebitmap') is '':
                self.unbind_class('active_bit','<Enter>')
                self.unbind_class('active_bit','<Leave>')
                self.itemconfig('_bit',image=self.cnf.get('bitmap'))
            # For bitmap config
            config_cnf_bit = {}
            for i in ('anchor', 'bitmap'):
                config_cnf_bit.update( {i : kw.get(i, self.cnf.get(i))} )
            self.itemconfig('_bit', config_cnf_bit, state=self['state'])

        if kw.get('compound'):
            self._compound(kw.get('compound'), self.winfo_reqheight(), self.winfo_reqwidth())
        
        if self.cnf.get('textvariable') is not None:
            self.cnf['text'] = self.cnf['textvariable'].get()
            self.cnf['textvariable'].trace_add( 'write', lambda *ag: 
                    self.itemconfig('_txt', text = self.cnf['textvariable'].get() ))

        # For Text config
        config_cnf_txt = {}
        for i in ('text','anchor','font','justify'):
            config_cnf_txt.update( {    i : kw.get(i, self.cnf.get(i))  } )
        self.itemconfig( '_txt', config_cnf_txt, state=self['state'], 
                        fill=kw.get('fg', self.cnf.get('fg')), 
                        disabledfill=kw.get('disabledforeground', 
                        self.cnf.get('disabledforeground')))  
        # if commented and state='disabled then doesnt disable completely. (NEED FIX)
        self.after(10, lambda: self.itemconfig( '_txt', state=self['state']))   
             
        if int(self['takefocus']) and self['state'] == 'normal':
            self.bind_class('takefocus', '<FocusIn>' , lambda _: self.itemconfig('_tf', state='normal'))
            self.bind_class('takefocus', '<FocusOut>', lambda _: self.itemconfig('_tf', state='hidden'))
        elif not int(self['takefocus']) or self['state'] == 'disabled':
            self.unbind_class('takefocus', '<FocusIn>' )
            self.unbind_class('takefocus', '<FocusOut>')
            self.itemconfig('_tf', state='hidden')
    
        Edge_color = get_shade(self['bg'], 0.1, 'auto-120')    # This will darken the border around the button
        self.itemconfig('_border1', outline=Edge_color)
        self.itemconfig('_border2', fill=Edge_color)

        if kw.get('bd'):
            self.itemconfig('_bd_color1', width=kw.get('bd', 6))
            self.itemconfig('_bd_color2', width=kw.get('bd', 6))

        defaultbdcolor = self.cnf.get('innerbg', self.master['bg'])
        if bool(kw.get('borderless')): 
            # Modify configurations of master widget to support `borderless=1`.
            def configure(cnf=None, **kw):
                """Configure resources of a widget.

                The values for resources are specified as keyword
                arguments. To get an overview about
                the allowed keyword arguments call the method keys.
                """
                #  Need a better fix ..
                kw = _TK._cnfmerge((cnf, kw))
                r = self.master._configure('configure', None, kw)
                if kw.get('bg') or kw.get('background'):
                    for i in self._instances:
                        if i['borderless']:
                            i.cnf.update( {'bordercolor': i.master['innerbg']} )
                            i.itemconfig('_bd_color1', outline=i.master['bg'])
                            i.itemconfig('_bd_color2', fill=i.master['bg'])
                return r

            self.master.configure = configure
            self.master.config = configure
            self.cnf.update({'bordercolor': defaultbdcolor})
            self.itemconfig('_bd_color1', outline=defaultbdcolor)
            self.itemconfig('_bd_color2', fill=defaultbdcolor)
        elif not bool(kw.get('borderless', True)) or not self.cnf.get('borderless'):
            if self.cnf.get('bordercolor') == defaultbdcolor:
                self.cnf.pop('bordercolor', None)
            bd_color = self.cnf.get('bordercolor', get_shade(self['innerbg'], 0.04, 'auto-120'))
            self.cnf.update({'bordercolor': bd_color})
            self.itemconfig('_bd_color1', outline=kw.get('bordercolor', bd_color))
            self.itemconfig('_bd_color2', fill=kw.get('bordercolor', bd_color))
    
    def bind_class(self, className, sequence=None, func=None, add='+'):
        className = className+str(self)
        bindtags = list( self.bindtags() )
        if className in bindtags: bindtags.remove(className)
        bindtags.insert(bindtags.index('Canvas'), className)
        self.bindtags(bindtags)
        return super().bind_class(className, sequence=sequence, func=func, add=add)
    
    def unbind_class(self, className, sequence):
        className = className+str(self)
        bindtags = list(self.bindtags())
        if className in bindtags: bindtags.remove(className)
        self.bindtags(bindtags)
        return super().unbind_class(className, sequence)

    def on_press_color(self, **kw):
        '''### Give gradient color effect
        Internal funtion. return tag
        #### Arguments:
        1. `color`: ("#4b91fe", "#055be5")
        2. `tag`
        3. `height`
        4. `width`'''
        print("on_press_color", kw.get('tag', None))
        self.cnf['activebackground'] = self.cnf.get('activebackground', ("#4b91fe", "#055be5"))
        width = self.coords('_activebg')
        if len(width) > 3:
            width = width[2]
        if self.winfo_height() == len(self.find('withtag', '_activebg')) \
                and self.winfo_width() == width and not kw.get('color'): 
            return
        self.delete('_activebg')
        tag = kw.get('tag', 'press')
        if kw.get('color') is None: 
            kw.pop('color', None)
        cr = kw.get( 'color', ("#4b91fe", "#055be5") )  # This is the default color for mac 
        if isinstance(cr, tuple):
            if None in cr: 
                cr = list(cr)
                cr.remove(None)
                cr = cr[0]
        w, h = self.winfo_width(), self.winfo_height()
        if not isinstance(cr, tuple): cr = ( C.Color(cr),C.Color(cr) )
        else: cr = ( C.Color(cr[0]),C.Color(cr[1]) )
        for i, j in enumerate(list( cr[0].range_to( cr[1],  kw.get('heigh', h)) )):
            self._line(0, i, kw.get('width',w), i, fill=j, tag=tag, state='hidden')
        self.tag_lower(tag)     # keep the tag last 
        return tag 

    def _info_button(self, **kw):
        """Internal Funtion.\n
        This function takes essentials parameters to give
        the approximate width and height accordingly. \n
        It creates a ttk button and use all the resouces given 
        and returns width and height of the ttk button, after taking 
        width and height the button gets destroyed also the custom style."""
        _style_tmp = ttk.Style()
        _style_tmp.configure('%s.TButton'%self, font=kw.get('font') ) 
        _style_tmp.configure('%s.TButton'%self, padding=kw.get('padding') )
        tmp = ttk.Button(self, text=kw.get('text'), image=kw.get('image'), 
            bitmap=kw.get('bitmap'), textvariable=kw.get('textvariable'),
            compound=kw.get('compound'), style='%s.TButton'%self )
        geo = tmp.winfo_reqwidth(), tmp.winfo_reqheight()
        del _style_tmp   # Need fix --- doesn't really delete the custom style
        tmp.destroy()
        return geo

    def _compound(self, flag, height, width):
        "Internal function. Use `compound = 'left'/'right'/'top'/'bottom'` to configure."
        _PiTag = '_img' if self.cnf.get('image') else '_bit'
        _im_size = self.bbox(_PiTag)
        _txt_size = self.bbox('_txt')
        if _im_size and _txt_size:
            W_im = _im_size[2] - _im_size[0]
            H_im = _im_size[3] - _im_size[1]
            W_txt = _txt_size[2] - _txt_size[0]
            H_txt = _txt_size[3] - _txt_size[1]
            if flag is 'bottom':
                width = (width/2, width/2)
                height = (height/2-H_im/2, height/2+H_txt/2)
            elif flag is 'top' :
                width = (width/2, width/2)
                height = (height/2+H_im/2, height/2-H_txt/2)
            elif flag is 'right' :
                width = (width/2-W_im/2, width/2+W_txt/2)
                height = (height/2, height/2)
            elif flag is'left':
                width = (width/2+W_im/2, width/2-W_txt/2)
                height = (height/2, height/2)
            elif flag is not None:
                raise _TK.TclError('bad compound "{}": must be \
                    none, text, image, center, top, bottom, left, or right'.format(flag))
            if isinstance(height, tuple):
                self.coords('_txt', width[0], height[0])
                self.coords(_PiTag, width[1], height[1])
                return { 'width':width, 'height':height }
        return None
    
    def keys(self):
        """Return a list of all resource names of this widget."""
        K_all = [
            'background', 'bg', 'innerbackground', 'innerbg',
            'bd', 'borderwidth', 'cursor', 'height', 
            'highlightbackground', 'highlightcolor', 'highlightthickness',
            'relief', 'state', 'takefocus', 'width', 'activebackground', 'activeforeground', 
            'activeimage', 'activebitmap', 'anchor', 'bitmap', 'command', 'compound', 'disabledforeground', 'fg', 
            'font', 'foreground', 'image', 'overrelief', 'padx', 'pady', 'repeatdelay', 'repeatinterval', 'text', 
            'textvariable', 'underline', 'bordercolor', 'cornerrounding', 'borderless', 'disabledbackground']
        K_all.sort()
        return K_all
