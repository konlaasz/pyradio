# -*- coding: utf-8 -*-
import curses
import curses.ascii
import logging
from sys import version_info, platform, version
try:
    from .cjkwrap import PY3, is_wide, cjklen
except:
    from cjkwrap import PY3, is_wide, cjklen
import locale
locale.setlocale(locale.LC_ALL, '')    # set your locale

logger = logging.getLogger(__name__)

class DisabledWidget(object):
    '''A dummy class that only returns enabled = False

    To be used in complex dialogs
    '''
    _enabled = False
    focus = False
    checked = False

    def __init__(self):
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        pass

    def show(self):
        pass

class SimpleCursesWidget(object):
    '''An abstract widget class '''
    _win = _parent = _callback_function = None
    _focused = _showed = False
    _enabled = True
    _Y = _X = _width = _color_focused = _color = 0
    _height = 1
    _caption = _display_caption = ''

    @property
    def window(self):
        return self._win

    @window.setter
    def window(self, value):
        raise ValueError('parameter is read only')

    @property
    def Y(self):
        return self._Y

    @Y.setter
    def Y(self, value):
        self._Y = value

    @property
    def X(self):
        return self._X

    @X.setter
    def X(self, value):
        self._X = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        raise ValueError('parameter is read only')

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        raise ValueError('parameter is read only')

    @property
    def caption(self):
        '''The text of the widget'''
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value
        if self._showed:
            self.resize_and_show()

    @property
    def enabled(self):
        '''Returns if the widget is enabled'''
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._showed:
            self.refresh()

    @property
    def focused(self):
        '''Returns if the widget has focus'''
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        if self._showed:
            self.refresh()

    @property
    def color_focused(self):
        '''The color to use when the widget has the focus'''
        return self._color_focused

    @color_focused.setter
    def color_focused(self, value):
        self._color = value
        if self._showed:
            self.refresh()

    @property
    def color(self):
        '''The normal color of the widget (no focus)'''
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        if self._showed:
            self.refresh()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def callback_function(self):
        '''The function to call when the widget is "clicked"'''
        return self._callback_function

    @callback_function.setter
    def callback_function(self, value):
        self._callback_function = value

    def getmaxyx(self):
        return self._win.getmaxyx() if self._win else (0, 0)

    def mvwin(self, Y, X, show=True, erase=False):
        '''Move the widget

            Parameters
            ==========
            Y, X
                New T and X coodrinates
            show
                If True, display the widget at its new location.
                Otherwise, just calculate the new location.
            erase
                If True, erase the window before moving it
                if False (the default), do not erase the
                  window; the parent will erase itself
        '''

        if self._win:
            if erase:
                self._win.erase()
                self._win.touchwin()
                self._win.refresh()
            try:
                self._win.mvwin(Y, X)
            except:
                pass
            self._Y = Y
            self._X = X
            if show:
                self._win.touchwin()
                self.refresh()

    def set_focus(self, focus):
        if focus:
            self._focused = True
        else:
            self._focused = False
        if self._showed:
            self.refresh()

    def toggle_focus(self):
        self._focused = not self._focused
        if self._showed:
            self.refresh()

    def resize(self):
        '''Resize the widget.
        The window (_win) gets created here'''

        pass

    def resize_and_show(self):
        '''Resize and show the widget'''
        self.resize()
        self.show()

    def show(self):
        '''Display the widget'''
        self._showed = True

    def refresh(self):
        '''Refresh the widget'''
        pass

    def keypress(char):
        '''Handle keyboard input

            Returns
            =======
                True
                    The character was not handled by the widget.
                    The calling function can go on and handle it.
                False
                    The character was handled by the widget.
                    The calling function does not need to handle it.
        '''
        return False


class SimpleCursesString(SimpleCursesWidget):
    ''' A class to provide a String value

        Parameters
        ==========
        Y, X, window
            Coordinates and parent window
        caption
            preffix string
        string
            the string to display (variable)
        color
            text color
        color_focused
            counter color when enabled and focused
        color_not_focused
            counter color when enabled but not focused
        color_disabled
            counter color when disabled
        full_slection
            if not None, it should be a tuple:
                (go left from self._X, numbder of chars to print)
            draw selection cursor as a full line
    '''


    _max_string = 0

    def __init__(
        self,
        Y, X, parent,
        caption,
        string,
        color, color_focused,
        color_not_focused,
        color_disabled,
        right_arrow_selects=True,
        callback_function_on_activation=None,
        full_selection=None
    ):
        self._Y = Y
        self._X = X
        self._win = self._parent = parent
        self._string = string
        if cjklen(self._string) > self._max_string:
            self._max_string = cjklen(self._string)
        self._caption = caption
        self._color = color
        self._color_focused = color_focused
        self._color_not_focused = color_not_focused
        self._color_disabled = color_disabled
        self._right_arrow_selects = right_arrow_selects
        self._callback_function_on_activation = callback_function_on_activation
        self._full_selection = full_selection

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, value):
        self._string = value
        if cjklen(self._string) > self._max_string:
            self._max_string = cjklen(self._string)

    @property
    def string_len(self):
        return len(self._string)

    @property
    def caption_len(self):
        return len(self._caption)

    @property
    def string_Y(self):
        return self._Y

    @property
    def string_X(self):
        return self._X + len(self._string)

    def keypress(self, char):
        ''' SimpleCursesString key press
            Returns:
                -1 continue
                 0 action (select)
        '''
        ret = -1
        if self._right_arrow_selects and char in (
            ord('l'), ord(' '), ord('\n'), ord('\r'),
            curses.KEY_RIGHT, curses.KEY_ENTER
        ):
            ret = 0
        elif not self._right_arrow_selects and char in (
            ord(' '), ord('\n'), ord('\r'),
            curses.KEY_ENTER
        ):
            ret = 0
        if ret == 0 and self._callback_function_on_activation:
            self._callback_function_on_activation()
        return ret

    def _print_full_line(self, col):
        tmp = self._full_selection[0] * ' ' + self.caption + self._string
        self._win.addstr(
            self._Y,
            self._X - self._full_selection[0],
            tmp.ljust(self._full_selection[1]),
            col
        )
    def show(self, parent=None):
        if parent:
            self._win = self_parent = parent
        if self._full_selection and self._enabled and self._focused:
            self._print_full_line(self._color_focused)
        else:
            if self._full_selection:
                self._win.addstr(
                    self._Y,
                    self._X - self._full_selection[0],
                    (self._full_selection[1] ) * ' ',
                    self._color
                )
            if self._enabled:
                self._win.addstr(self._Y, self._X, self._caption, self._color)
                if self._focused:
                    self._win.addstr(self._string.ljust(self._max_string), self._color_focused)
                else:
                    self._win.addstr(self._string.ljust(self._max_string), self._color_not_focused)
            else:
                self._win.addstr(self._Y, self._X, self._caption, self._color_disabled)
                self._win.addstr(self._string.ljust(self._max_string), self._color_disabled)

class SimpleCursesCounter(SimpleCursesWidget):
    ''' A class to provide a counter

        Parameters
        ==========
        Y, X, window
            Coordinates and parent window
        value, minumum, maximum, step, big_step
            counter parameters
            step : small changer (h, l)
            big_step : big change (PgUp, PgDn)
        number_length
            minimum length of number when displayed
            the number is right alligned, i.e. a value of 11
            with a number_length of 4, will display '  11'
        color
            text color
        color_focused
            counter color when enabled and focused
        color_not_focused
            counter color when enabled but not focused
        color_disabled
            counter color when disabled
        full_slection
            if not None, it should be a tuple:
                (go left from self._X, numbder of chars to print)
            draw selection cursor as a full line
    '''
    def __init__(
        self, Y, X, window,
        color, color_focused,
        color_not_focused,
        color_disabled,
        minimum=0, maximum=100,
        step=1, big_step=5, value=1,
        number_length=3, string='{0}',
        full_selection=None
    ):
        self._Y = Y
        self._X = X
        self._win = self._parent = window
        self._min = minimum
        self._max = maximum
        self._step = step
        self._big_step = big_step
        self._value = int(value)
        if self._value < self._min:
            self._value = self.min
        if self._value > self._max:
            self._value = self._max
        self._len = number_length
        max_len = len(str(self._max))
        if self._len < max_len:
            self._len = max_len
        self.string = string
        self._color = color
        self._color_focused = color_focused
        self._color_not_focused = color_not_focused
        self._color_disabled = color_disabled
        self._full_selection = full_selection

    def refresh(self):
        self.show(self._win)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = int(val)
        logger.error('Count: {}'.format(self._value))

    @property
    def minimum(self):
        return self._min

    @minimum.setter
    def minimum(self, val):
        self._min = val

    @property
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, val):
        self._max = val
        max_len = len(srt(self._max))
        if self._len < max_len:
            self._len = max_len

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, val):
        self._step = val

    @property
    def big_step(self):
        return self._big_step

    @big_step.setter
    def big_step(self, val):
        self._big_step = val

    @property
    def number_length(self):
        return self._len

    @number_length.setter
    def number_length(self, val):
        self._len = val
        max_len = len(srt(self._max))
        if self._len < max_len:
            self._len = max_len

    @property
    def string(self):
        return self._prefix + self._number + self._suffix

    @string.setter
    def string(self, value):
        self._number = '{0}'
        if value:
            sp = value.split('{0}')
            self._prefix = sp[0]
            if len(sp) > 1:
                self._suffix = sp[1]
        else:
            self._prefix = ''
            self._suffix = ''

    def move(self, newY=-1, newX=-1, parent=None):
        if newY > 0:
            self._Y = newY
        if newX > 0:
            self._X = newX
        if parent:
            self._win = self._parent = parent

    def _print_full_line(self, col):
        tmp = self._full_selection[0] * ' ' + self._prefix + str(self._value).rjust(self._len) + self._suffix
        self._win.addstr(
            self._Y,
            self._X - self._full_selection[0],
            tmp.ljust(self._full_selection[1]),
            col
        )

    def show(self, window, opening=False):
        if window:
            self._win = self._parent = window
        if self._enabled:
            if self._focused:
                col = self._color_focused
            else:
                col = self._color_not_focused
        else:
            col = self._color_disabled
        if self._full_selection and self._enabled and self._focused:
            self._print_full_line(col)
        else:
            if self._full_selection:
                self._win.addstr(
                    self._Y,
                    self._X - self._full_selection[0],
                    (self._full_selection[1] ) * ' ',
                    self._color
                )
            self._win.move(self._Y, self._X)
            if self._prefix:
                self._win.addstr(self._prefix, self._color)
            self._win.addstr(self._number.format(str(self._value).rjust(self._len)), col)
            if self._suffix:
                self._win.addstr(self._suffix, self._color)
            ''' overwrite last self._len characters '''
            self._win.addstr(' ' * self._len, self._color)
        self._showed = True

    def keypress(self, char):
        ''' SimpleCursesCounter keypress

            Returns
            -------
               -1 - Cancel
                0   Counter changed
                1 - Continue
                2 - Display help
        '''
        if (not self._focused) or (not self._enabled):
            return 1

        if char in (
            curses.KEY_EXIT, ord('q'), 27,
        ):
            return -1

        elif char == ord('?'):
            return 2

        elif char in (curses.KEY_NPAGE, ):
            self._value -= self._big_step
            if self._value < self._min:
                self._value = self._min
            self.show(self._win)
            return 0

        elif char in (curses.KEY_PPAGE, ):
            self._value += self._big_step
            if self._value > self._max:
                self._value = self._max
            self.show(self._win)
            return 0

        elif char in (ord('h'), curses.KEY_LEFT):
            self._value -= self._step
            if self._value < self._min:
                self._value = self._min
            self.show(self._win)
            return 0

        elif char in (ord('l'), curses.KEY_RIGHT):
            self._value += self._step
            if self._value > self._max:
                self._value = self._max
            self.show(self._win)
            return 0

        return 1


class SimpleCursesWidgetColumns(SimpleCursesWidget):
    ''' A widget to display selectable items
        in columns on a foreign window.
    '''

    ''' items alignment '''
    LEFT = 0        # default
    RIGHT = 1
    CENTER = 2      # not implemented

    ''' items placement '''
    VERICAL = True
    HORIZONTAL = False

    _columns = _rows = 0

    def __init__(self,
                 Y, X,
                 window,
                 items,
                 max_width,
                 color,
                 color_active,
                 color_cursor_selection,
                 color_cursor_active,
                 placement=True,
                 selection=0,
                 active=-1,
                 margin=0,
                 align=0,
                 right_arrow_selects = False,
                 on_activate_callback_function=None,
                 on_up_callback_function=None,
                 on_down_callback_function=None,
                 on_left_callback_function=None,
                 on_right_callback_function=None
                 ):
        ''' Initialize the widget.

            Parameters
            ----------
            Y, X
                Y, X position of widget in its parent (int)
            window
                The window to print items into. It must already exist
                (this widget will not create a window)
            items
                A list or tuple containing the menu items
            max_width
                The maximum width the widget can occupy.
                The number of columns is determined by this value
            color
                The normal color of the non-selected items
            color_active
                The color of the active item (no cursor on it)
            color_cursor_selection
                The cursor color
            color_cursor_active
                The cursor color when cursor is on the active item
            placement
                The items placement when displayed,
                either vertical (default) or horizontal
            selection
                The id of the currently selected item
            active
                The id of the active item
            margin
                Number of spaces to add before and after each item caption
            align
                Items alignment (left, right, center)
            right_arrow_selects
                If True, pressing right arrow will activate the selected item
            on_activate_callback_function
                A function to execute when new active item selected
            on_up_callback_function
                A function to execute when cursor is at row 0 and up is pressed
                The cursor will not move
            on_down_callback_function
                A function to execute when cursor is at the bottom row and down
                is pressed. The cursor will not move
            on_left_callback_function
                A function to execute when cursor is at the first column and left
                is pressed. The cursor will not move
            on_right_callback_function
                A function to execute when cursor is at the last column and right
                is pressed. The cursor will not move
        '''
        self._Y = Y
        self._X = X
        self._win = window
        self.items = items
        self._max_width = max_width
        self._color = color
        self._color_active = color_active
        self._color_cursor_active = color_cursor_active
        self._color_cursor_selection = color_cursor_selection
        self._margin = margin
        self._align = align
        self._right_arrow_selects = right_arrow_selects
        self._placement = placement
        self._on_activate_callback_function = on_activate_callback_function
        self._on_up_callback_function = on_up_callback_function
        self._on_down_callback_function = on_down_callback_function
        self._on_left_callback_function = on_left_callback_function
        self._on_right_callback_function = on_right_callback_function
        self.selection = selection
        self.active = active
        self._focused = True
        self._enabled = True
        self._showed = False
        self._coords = []

        self.set_items()

    @property
    def margin(self):
        '''Returns the widget's Y position '''
        return self._margin

    @property
    def columns(self):
        '''Returns the widget's number of columns '''
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value

    @property
    def rows(self):
        '''Returns the widget's number of rows '''
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value

    @property
    def height(self):
        '''Returns the widget's Y position '''
        return self._maxY

    @height.setter
    def height(self, value):
        self._maxY = value

    @property
    def width(self):
        '''Returns the widget's X position '''
        return self._maxX

    @width.setter
    def width(self, value):
        self._maxX = value

    @property
    def Y(self):
        '''Returns the widget's Y position '''
        return self._Y

    @Y.setter
    def Y(self, value):
        self._Y = value

    @property
    def X(self):
        '''Returns the widget's X position '''
        return self._X

    @X.setter
    def X(self, value):
        self._X = value

    @property
    def window(self):
        '''Returns if the widget is enabled'''
        return self._win

    @window.setter
    def window(self, value):
        self._win = value
        if self._showed:
            self.show()

    @property
    def enabled(self):
        '''Returns if the widget is enabled'''
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._showed:
            self.show()

    @property
    def focused(self):
        '''Returns if the widget has focus'''
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        if self._showed:
            self.show()

    @property
    def max_width(self):
        '''Returns if the widget has focus'''
        return self._max_width

    @max_width.setter
    def max_width(self, value):
        self._max_width = value
        self.set_items()

    def recalculate_columns(self):
        self.set_items()

    def _last_in_row(self, pY, pX):
        # logger.error('DE pY = {0}, pX = {1}'.format(pY, pX))
        test = [x for x in self._coords if x[0] == pY]
        # logger.error('DE test = {}'.format(test))
        return True if test[-1] == (pY, pX) else False

    def set_items(self, items=None):
        if items:
            self.items = tuple(items[:])
        self._item_width = len(max(self.items, key=len)) + 2 * self._margin
        self._columns = int((self._max_width / self._item_width))
        if self._columns == 1:
            self._columns = 2
        self._maxX = self._columns * self._item_width
        self._maxY = int(len(self.items) / self._columns)
        if len(self.items) % self._columns != 0:
            self._maxY += 1
        self._coords = []

    def show(self):
        # logger.error('DE columns = {}, rows ={}'.format(self._columns, self._maxY))
        for i, n in enumerate(self.items):
            ''' create string to display '''
            if self._align == self.LEFT:
                disp_item = ' ' * self._margin + n.ljust(self._item_width - 2 * self._margin) + ' ' * self._margin
            elif self._align == self.RIGHT:
                disp_item = ' ' * self._margin + n.rjust(self._item_width - 2 * self._margin) + ' ' * self._margin
            else:
                disp_item = n.center(self._item_width)

            ''' find color to use '''
            # logger.error('DE self._focused = {}'.format(self._focused))
            if self._focused and self._enabled:
                # logger.error('DE focused and enabled')
                col = self._color
                # logger.error('{0}, sel={1}, ac={2}'.format(i, self.selection, self.active))
                if i == self.selection and i == self.active:
                    col = self._color_cursor_active
                    # logger.error('active color')
                elif i == self.selection:
                    col =self._color_cursor_selection
                    # logger.error('color_cursor_selection')
                elif i == self.active:
                    col = self._color_active
                    # logger.error('color_cursor_active')
            elif self._enabled:
                # logger.error('DE enabled')
                col = self._color
                if i == self.active:
                    col = self._color_active
            else:
                # logger.error('DE not focused')
                col = self._color

            ''' fill coords list, if not filled yet '''
            if len(self._coords) != len(self.items):
                if i == 0:
                    column = row = 0
                else:
                    if self._placement == self.VERICAL:
                        row = int(i / self._maxY)
                        column = int(i % self._maxY)
                    else:
                        column = int(i / self._columns)
                        row = int(i % self._columns)
                # logger.error('DE i = {}, column = {}, row = {}'.format(i, column, row))

                self._coords.append((column, row))

            ''' display string '''
            try:
                self._win.addstr(
                    self._Y + self._coords[i][0],
                    self._X + self._coords[i][1] * self._item_width,
                    disp_item,
                    col
                )
            except:
                logger.error('error displaying item {}'.format(i))

        # for i, n in enumerate(self._coords):
        #     logger.error('Item {}: X = {}, Y = {}'.format(i, *n))

        self._rows = max([x[0] for x in self._coords]) + 1
        # logger.error('DE coords = {}'.format(self._coords))
        # logger.error('DE columns = {0}, rows = {1}'.format(self._columns, self._rows))

        self._showed = True

    def keypress(self, char):
        ''' SimpleCursesWidgetColumns keypress

            Returns
            -------
               -1 - Cancel
                0 - Item selected
                1 - Continue
                2 - Cursor moved
                3 - Display help
        '''
        if (not self._focused) or (not self._enabled):
            return 1

        if char in (
            curses.KEY_EXIT, ord('q'), 27,
        ):
            return -1

        elif char == ord('?'):
            return 3

        elif self._right_arrow_selects and char in (
            ord('l'), ord(' '), ord('\n'), ord('\r'),
            curses.KEY_RIGHT, curses.KEY_ENTER
        ):
            self.active = self.selection
            logger.error('DE active = {}'.format(self.active))
            ''' Do not refresh the widget, it will
                probably be hidden next
            '''
            if self._on_activate_callback_function:
                self._on_activate_callback_function()
            return 0

        elif not self._right_arrow_selects and char in (
            ord(' '), ord('\n'), ord('\r'),
            curses.KEY_ENTER
        ):
            self.active = self.selection
            logger.error('DE active = {}'.format(self.active))
            self.show()
            return 0

        elif char in (ord('g'), curses.KEY_HOME):
            self.selection = 0
            self.show()
            return 2

        elif char in (ord('G'), curses.KEY_END):
            self.selection = len(self.items) - 1
            self.show()
            return 2

        elif char in (curses.KEY_PPAGE, ):
            if self.selection == 0:
                self.selection = len(self.items) - 1
            else:
                self.selection -= 5
                if self.selection < 0:
                    self.selection = 0
            self.show()
            return 2

        elif char in (curses.KEY_NPAGE, ):
            if self.selection == len(self.items) - 1:
                self.selection = 0
            else:
                self.selection += 5
                if self.selection >= len(self.items):
                    self.selection = len(self.items) - 1
            self.show()
            return 2

        elif char in (ord('k'), curses.KEY_UP):
            pY, pX = self._coords[self.selection]
            if self._on_up_callback_function and pY == 0:
                self._on_up_callback_function()
            else:
                self.selection -= 1
                if self.selection < 0:
                    self.selection = len(self.items) - 1
                self.show()
            return 2

        elif char in (ord('j'), curses.KEY_DOWN):
            pY, pX = self._coords[self.selection]
            # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
            # logger.error('DE rows = {}'.format(self._rows))
            if self._on_down_callback_function and \
                    (pY == self._rows - 1 or self.selection == len(self.items) - 1):
                self._on_down_callback_function()
            else:
                self.selection += 1
                if self.selection == len(self.items):
                    self.selection = 0
                self.show()
            return 2

        elif char in (ord('l'), curses.KEY_RIGHT):
            pY, pX = self._coords[self.selection]
            if self._on_right_callback_function and \
                    (pX == self._columns - 1 or self._last_in_row(pY, pX)):
                self._on_right_callback_function()
            else:
                # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
                pX += 1
                if pX >= self._columns:
                    pX = 0
                    pY += 1
                # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
                # logger.error('DE {}'.format(self._coords))
                try:
                    it = self._coords.index((pY, pX))
                except ValueError:
                    pX = 0
                    pY += 1
                    # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
                    try:
                        it = self._coords.index((pY, pX))
                    except:
                        it = self._coords.index((0, 0))
                # logger.error('DE it = {}'.format(it))
                self.selection = it
                self.show()
            return 2

        elif char in (ord('h'), curses.KEY_LEFT):
            pY, pX = self._coords[self.selection]
            if self._on_left_callback_function and pX == 0:
                self._on_left_callback_function()
            else:
                # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
                pX -= 1
                if pX < 0:
                    pX = self._columns - 1
                    pY -= 1
                    if pY < 0:
                        self.selection = self._coords.index(max(self._coords))
                    else:
                        # logger.error('DE pY ={0}, pX ={1}'.format(pY, pX))
                        # logger.error('DE {}'.format(self._coords))
                        try:
                            it = self._coords.index((pY, pX))
                        except ValueError:
                            pX -= 1
                            while True:
                                try:
                                    it = self._coords.index((pY, pX))
                                    break
                                except ValueError:
                                    pX -= 1
                        # logger.error('DE it = {}'.format(it))
                        self.selection = it
                else:
                    self.selection = self._coords.index((pY, pX))

                self.show()
            return 2

        return 1


class SimpleCursesMenuEntries(SimpleCursesWidget):
    ''' A menu entries widget
        (a list of items vertically stacked)
        with selection and active item.
    '''

    ''' items alignment '''
    LEFT = 0        # default
    RIGHT = 1
    CENTER = 2      # not implemented

    def __init__(self,
                 Y, X,
                 window,
                 items,
                 color,
                 color_active,
                 color_cursor_selection,
                 color_cursor_active,
                 selection=0,
                 active=-1,
                 margin=0,
                 align=0,
                 right_arrow_selects=True,
                 on_activate_callback_function=None,
                 on_up_callback_function=None,
                 on_down_callback_function=None,
                 on_left_callback_function=None,
                 on_right_callback_function=None,
                 ):
        ''' Initialize the widget.

            Parameters
            ----------
            Y, X
                Y, X position of widget in its parent (int)
            window
                The window to print items into. It must already exist
                (this widget will not create a window)
            items
                A list or tuple containing the menu items
            color
                The normal color of the non-selected items
            color_active
                The color of the active item (no cursor on it)
            color_cursor_selection
                The cursor color
            color_cursor_active
                The cursor color when cursor is on the active item
            selection
                The id of the currently selected item
            active
                The id of the active item
            margin
                Number of spaces to add before and after each item caption
            align
                Items alignment (left, right, center)
            right_arrow_selects
                If True (default) right arrow and "l" selects the new
                active item (for example a menu). Set it to False if
                the widget is part of a composite widget.
            on_activate_callback_function
                A function to execute when new active item selected
        '''
        self._Y = Y
        self._X = X
        self._win = window
        self.items = items
        self._color = color
        self._color_active = color_active
        self._color_cursor_active = color_cursor_active
        self._color_cursor_selection = color_cursor_selection
        self._margin = margin
        self._align = align
        self._right_arrow_selects = right_arrow_selects
        self._on_activate_callback_function = on_activate_callback_function
        self._on_up_callback_function = on_up_callback_function
        self._on_down_callback_function = on_down_callback_function
        self._on_left_callback_function = on_left_callback_function
        self._on_right_callback_function = on_right_callback_function
        self.selection = selection
        self.active = active
        self._focused = True
        self._enabled = True
        self._showed = False

        self.set_items()

    @property
    def height(self):
        '''Returns the widget's height '''
        return self._maxY

    @height.setter
    def height(self, value):
        self._maxY = val

    @property
    def width(self):
        '''Returns the widget's width '''
        return self._maxX

    @width.setter
    def width(self, value):
        self._maxX = val

    @property
    def Y(self):
        '''Returns the widget's Y position '''
        return self._Y

    @Y.setter
    def Y(self, value):
        self._Y = val

    @property
    def X(self):
        '''Returns the widget's X position '''
        return self._X

    @X.setter
    def X(self, value):
        self._X = val

    @property
    def parent(self):
        '''Returns the widget's window '''
        return self._parent

    @parent.setter
    def parent(self, value):
        if self._showed:
            self.show(parent=value)

    @property
    def window(self):
        '''Returns the widget's window '''
        return self._win

    @window.setter
    def window(self, value):
        self._win = value
        if self._showed:
            self.show()

    @property
    def enabled(self):
        '''Returns if the widget is enabled'''
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._showed:
            self.show()

    @property
    def focused(self):
        '''Returns if the widget has focus'''
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        if self._showed:
            self.show()

    def set_items(self, items=None):
        if items:
            self.items = tuple(items[:])
        self._item_width = len(max(self.items, key=len))
        self._maxX = self._item_width + 2 * self._margin
        self._maxY = len(self.items)

    def show(self, parent=None):
        if parent:
            self._parent = parent
            self._win = None
        for i, n in enumerate(self.items):
            if self._align == self.LEFT:
                disp_item = ' ' * self._margin + n.ljust(self._item_width) + ' ' * self._margin
            elif self._align == self.RIGHT:
                disp_item = ' ' * self._margin + n.rjust(self._item_width) + ' ' * self._margin
            if self._focused and self._enabled:
                col = self._color
                if i == self.selection == self.active:
                    col = self._color_active
                elif i == self.selection:
                    col =self._color_cursor_selection
                elif i == self.active:
                    col = self._color_cursor_active
            elif self._enabled:
                col = self._color
                if i == self.active:
                    col = self._color_active
            else:
                col = self._color
            self._win.addstr(i + self._Y, self._X, disp_item, col)
        self._showed = True

    def keypress(self, char):
        ''' SimpleCursesMenuEntries keypress

            Returns
            -------
               -1 - Cancel
                0 - Item selected
                1 - Continue
                2 - Display help
        '''
        if (not self._focused) or (not self._enabled):
            return 1

        if char in (
            curses.KEY_EXIT, ord('q'), 27,
            ord('h'), curses.KEY_LEFT
        ):
            return -1

        elif char == ord('?'):
            return 2

        elif self._right_arrow_selects and char in (
            ord('l'), ord(' '), ord('\n'), ord('\r'),
            curses.KEY_RIGHT, curses.KEY_ENTER
        ):
            self.active = self.selection
            ''' Do not refresh the widget, it will
                probably be hidden next
            '''
            if self._on_activate_callback_function:
                self._on_activate_callback_function()
            return 0

        elif not self._right_arrow_selects and char in (
            ord(' '), ord('\n'), ord('\r'),
            curses.KEY_ENTER
        ):
            self.active = self.selection
            self.show()
            return 0

        elif char in (ord('g'), curses.KEY_HOME):
            self.selection = 0
            self.show()

        elif char in (ord('G'), curses.KEY_END):
            self.selection = len(self.items) - 1
            self.show()

        elif char in (curses.KEY_PPAGE, ):
            if self.selection == 0:
                self.selection = len(self.items) - 1
            else:
                self.selection -= 5
                if self.selection < 0:
                    self.selection = 0
            self.show()

        elif char in (curses.KEY_NPAGE, ):
            if self.selection == len(self.items) - 1:
                self.selection = 0
            else:
                self.selection += 5
                if self.selection >= len(self.items):
                    self.selection = len(self.items) - 1
            self.show()

        elif char in (ord('k'), curses.KEY_UP):
            self.selection -= 1
            if self.selection < 0:
                self.selection = len(self.items) - 1
            self.show()

        elif char in (ord('j'), curses.KEY_DOWN):
            self.selection += 1
            if self.selection == len(self.items):
                self.selection = 0
            self.show()

        return 1


class SimpleCursesCheckBox(SimpleCursesWidget):
    '''A very simple checkbox curses widget '''
    _checked = False
    _highlight_all = False

    def __init__(self,
                 Y, X, caption,
                 color_focused, color, bracket_color,
                 char='✔', checked=False, focused=False,
                 highlight_all=False, callback_function=None):
        ''' Initialize the widget.

            Parameters
            ----------
            Y, X
                Y, X position of widget in its parent (int)
            caption
                The caption of the widget (string).
            color_focused
                Active checkbox color (curses.color_pair)
            color
                Inactive checkbox color (curses.color_pair)
            bracket_color
                The color of the brackets (curses.color_pair)
                Also the color to use when widget is disabled
            char
                The character to indicate a checked checkbox (string)
            checked
                Index of checked checkbox (int)
            focused
                True if widget has focus (boolean)
            highlight_all
                Focused behaviour (boolean).
                If True, the whole window uses the active color.
                If False, only char uses the active color.
        '''

        self._Y = Y
        self._X = X
        self._caption = caption
        self._char = char
        if platform.lower().startswith('win') and \
                self._char == '✔':
            self._char = 'X'
        self._checked = checked
        self._focused = focused
        self._highlight_all = highlight_all
        self._color_focused = color_focused
        self._color = color
        self._bracket_color = bracket_color

        ''' initialize the window '''
        self.resize()

    @property
    def char(self):
        '''Character to indicate a checked checkbox
           Default: ✔
        '''
        return self._char

    @char.setter
    def char(self, value):
        self._char = value
        self.refresh()

    @property
    def checked(self):
        '''Returns if the checkbox is ckecked'''
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self.refresh()

    @property
    def highlight_all(self):
        '''Returns if the whole window will use the
        focused color when focused'''
        return self._highlight_all

    @highlight_all.setter
    def highlight_all(self, value):
        self._highlight_all = value
        self.refresh()

    def resize(self):
        '''Resize the widget
           For changes to be displayed,
           use show afterwards'''

        ''' use cjklen for cjk support '''
        if self._win:
            del self._win
        self._width = None
        self._width = len(self._caption) + 4
        self._win = curses.newwin(1, self._width, self._Y, self._X)

    def move(self, new_Y=None, new_X=None):
        if new_Y:
            self._Y = new_Y
        if new_X:
            self._X = new_X
        if self._win:
            self._win.mvwin(self._Y, self._X)

    def show(self):
        '''Put the widget on the screen'''
        if self._win:
            self._win.bkgdset(' ', self._color)
            self._win.erase()
            self._win.touchwin()
            self._win.refresh()
            self.refresh()
            self._showed = True

    def refresh(self):
        '''Refresh the widget's content'''
        if self._win:
            char = self._char if self._checked else ' '
            if not self._enabled:
                try:
                    self._win.addstr(0, 0, '[ ] ', self._bracket_color)
                    self._win.addstr(self._caption, self._bracket_color)
                except curses.error:
                    pass
            elif self._focused:
                if self._highlight_all:
                    try:
                        self._win.addstr(0, 0,
                                         '[' + char + '] ' + self._caption,
                                         self._color_focused)
                    except curses.error:
                        pass
                else:
                    try:
                        self._win.addstr(0, 0, '[', self._bracket_color)
                        self._win.addstr(char, self._color_focused)
                        self._win.addstr('] ', self._bracket_color)
                        self._win.addstr(self._caption, self._color)
                    except curses.error:
                        pass
            else:
                try:
                    self._win.addstr(0, 0, '[', self._bracket_color)
                    self._win.addstr(char, self._color)
                    self._win.addstr('] ', self._bracket_color)
                    self._win.addstr(self._caption, self._color)
                except curses.error:
                    pass
            self._win.touchwin()
            self._win.refresh()

    def toggle_checked(self):
        self._checked = not self._checked
        self.refresh()

    def _get_metrics(self):
        ''' Calculate width and height based on caption '''
        self._height = 1
        self._width = len(self._title) + 4

    def keypress(self, char):
        if self._focused and \
                self.enabled and \
                char in (ord(' '), curses.KEY_ENTER):
            self.checked = not self._checked
            if self._checked and \
                    self._callback_function is not None:
                self._callback_function()
            return False
        return True


class SimpleCursesPushButton(SimpleCursesWidget):

    def __init__(self,
                 Y, X, caption,
                 color_focused,
                 color,
                 bracket_color,
                 constant_width=0,
                 parent=None,
                 callback_function=None):
        '''Initialize the wizard.

        Parameters
        ----------
        Y, X
            Y, X position of wizard in its parent (int)
        caption
            The caption of the wizard (string).
        color_focused
            Focused button caption color (curses.color_pair)
        color
            Normal button caption color (curses.color_pair)
        bracket_color
            The color to use for the surrounding brackets
        focused
            True if wizard has focus (boolean)
        constant_width
            if > 0 make the widget this wide (int)
            May have to adjust the caption
        parent
            The widget's parent window
        callback_function
            The function to call when the button
            is "clicked". Default is None
        '''

        self._Y = Y
        self._X = X
        self._caption = caption
        self._color_focused = color_focused
        self._color = color
        self._constant_width = constant_width
        self._bracket_color = bracket_color
        if 0 < self._constant_width < 6:
            raise ValueError('constant_width must be at least 6')
        self._callback_function = callback_function
        self.resize()

    @property
    def constant_width(self):
        return self.__constant_width

    @constant_width.setter
    def constant_width(self, value):
        raise ValueError('parameter is read only')

    def resize(self):
        old_width = self._width
        self._display_caption = self._caption
        if self._constant_width == 0:
            self._width = len(self._caption) + 4
        else:
            self._width = self._constant_width
            if len(self._caption) + 4 > self._width:
                self._display_caption = self._caption[:self._width - 4]

        if self._width != old_width:
            if self._win:
                del self._win
            self._win = None
            self._win = curses.newwin(1, self._width, self._Y, self._X)

    def show(self):
        '''Put the widget on the screen'''
        if self._win:
            self._win.bkgdset(' ', self._color)
            self._win.erase()
            self._win.touchwin()
            self._win.refresh()
            self.refresh()
            self._showed = True

    def refresh(self):
        '''Refresh the widget's content'''
        if self._win:
            if self._enabled:
                self._win.addstr(0, 0, '[', self._bracket_color)
                if self._focused:
                    col = self._color_focused
                else:
                    col = self._color
                self._win.addstr(' ' + self._display_caption + ' ', col)
                try:
                    self._win.addstr(']', self._bracket_color)
                except:
                    pass
            else:
                self._win.addstr(0, 0, '[', self._color)
                self._win.addstr(' ' + self._display_caption + ' ', self._bracket_color)
                try:
                    self._win.addstr(']', self._color)
                except:
                    pass

            self._win.touchwin()
            self._win.refresh()

    def keypress(self, char):
        if char in (ord(' '), ord('\n'),
                    ord('\r'), curses.KEY_ENTER) and \
                self._focused:
            if self._callback_function:
                self._callback_function(self._parent)
                return True
        return False


class SimpleCursesHorizontalPushButtons(object):
    '''A helper class to create horizontally
    spaced curses push buttons.

    After its creation, use show() to display them.
    Access to individual button is through <class>.buttons
    '''
    _X = _width = 0
    _parent = None
    _left_or_right_margin = 2

    def __init__(self, Y, captions,
                 color_focused, color,
                 bracket_color, constant_width=0,
                 parent = None,
                 focused=0,
                 left_or_right_margin = 2):
        '''Initialize the wizard.

        Parameters
        ----------
        Y
            Y position of wizard in its parent (int)
        captions
            The caption of the buttons contained within
            the widget (list or tuple).
        color_focused
            Focused button caption color (curses.color_pair)
        color
            Normal button caption color (curses.color_pair)
        bracket_color
            The color to use for the surrounding brackets
        focused
            True if wizard has focus (boolean)
        constant_width
            if > 0 make the widget this wide (int)
            May have to adjust the caption
        parent
            The widget's parent window (curses window)
        focused
            The id of the button which will have the focus
            the first time the widget is displayed. Default
            value is 0 (i.e. the first button). Set it to -1
            to disable it, i part of other widget. (int)
        '''

        self._buttons = []
        for n in captions:
            self._buttons.append(SimpleCursesPushButton(
                Y=Y, X=0,
                caption=n,
                color_focused=color_focused, color=color,
                bracket_color=bracket_color,
                constant_width=constant_width,
                parent=parent))
            self._width += self.buttons[-1].width + 2
        self._width -= 2
        for n in self._buttons:
            n.window.bkgdset(' ', n.color)
            n.window.erase()
            n.window.touchwin()
        self._Y = Y
        self._left_or_right_margin = left_or_right_margin
        if -1 < focused < len(self._buttons):
            ''' use _focused so that we don't refresh '''
            self._buttons[focused]._focused = True
        self._parent = parent

    def move(self, newY, newX=0):
        self._Y = newY
        for n in self._buttons:
            n.Y = newY

    def show(self, parent=None, orientation='center', show=True):
        '''Display the widget

        Parameters
        ==========
        parent
            The widget's parent
        orientation
            Can be 'center' (default), 'left' or 'right'.
            <class>.parent must be already set (either
            during creation or through property assignment.
        show
            If True, the widget is displayed at its new position.
            Never explicitly set it to False;
            use calculate_buttons_position() instead.
        '''
        if parent:
            self._parent = parent
        if self._parent:
            Y, X = self._parent.getmaxyx()
            offY, offX = self._parent.getbegyx()
            if orientation == 'left':
                self._X = offX + self._left_or_right_margin
            elif orientation == 'right':
                self._X = X - self._left_or_right_margin - self._width
            else:
                self._X = offX + int((X - self._width) / 2)
            ''' place widgets '''
            X = self._X
            Y = self._Y + offY
            for n in self._buttons:
                n.mvwin(Y, X, show)
                X += n.width + 2

    def calculate_buttons_position(self, parent=None, orientation='center'):
        '''Calculate buttons position but do not display them.
        It will call show() with show=False'''
        self.show(parent, orientation, show=False)

    @property
    def buttons(self):
        '''The list of buttons within the widget.
        This is the way to get access to an individual
        button and use its functionality.
        '''
        return self._buttons

    @buttons.setter
    def buttons(self, value):
        raise ValueError('parameter is read only')

    @property
    def parent(self):
        '''The parent window of the widget.
        This is a window, not another widget.
        If not set (or invalid), the buttons will not be
        visible even if show() is called.
        '''
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        if self._buttons:
            for n in self._buttons:
                n.parent = value


class SimpleCursesLineEdit(object):
    ''' Class to insert one line of text
    Python 3 supports all chars
    Python 2 supports ascii only

    '''
    string = ''
    _string = ''
    _displayed_string = ''

    ''' windows '''
    _parent_win = None
    _caption_win = None             # contains box and caption
    _edit_win = None                # contains the "input box"
    _use_paste_mode = False         # paste mode is off by default
    _paste_mode = False             # enables direct insersion of ? and \
    _disable_paste_mode = False     # if True, disable paste mode
    _paste_mode_always_on = False   # set paste mode and never disable it

    ''' Default value for string length '''
    _max_chars_to_display = 0

    ''' Cursor position within _max_chars_to_display '''
    _curs_pos = 0
    _disp_curs_pos = 0
    ''' First char of sting to display '''
    _first = 0
    _last = 0

    ''' init values '''
    y = x = 0
    _caption = 'Insert string'
    _disp_caption = ' Insert string: '
    title = ''
    _disp_title = ''
    _boxed = False
    bracket = False
    box_color = 0
    caption_color = 0
    title_color = 0
    edit_color = 0
    unfocused_color = -1
    cursor_color = curses.A_REVERSE
    _has_history = False
    _input_history = None
    _key_up_function_handler = None
    _key_down_function_handler = None
    _key_pgup_function_handler = None
    _key_pgdown_function_handler = None
    _key_tab_function_handler = None
    _key_stab_function_handler = None
    _string_changed_handler = None
    _ungetch_unbound_keys = False

    _focused = True
    _enabled = True
    _showed = False

    ''' if width < 1, auto_width gets this value,
        so that width gets parent.width - auto_width '''
    _auto_width = 1

    ''' string to redisplay after exiting help '''
    _restore_data = []

    log = None
    _log_file = ''

    _reset_position = False

    _add_to_end = True
    _cjk = False

    _word_delim = (' ', '-', '_', '+', '=',
                   '~', '~', '!', '@', '#',
                   '$', '%', '^', '&', '*', '(', ')',
                   '[', ']', '{', '}', '|', '\\', '/',
                   )

    ''' Set to True to restringt accepted characters to ASCII only '''
    _pure_ascii = False

    ''' True if backlash has been pressed '''
    _backslash_pressed = False

    ''' Behaviour of ? key regarding \
        If True, display ? (\? to display help)
        If False, display help '''
    _show_help_with_backslash_pressed = False

    _mode_changed = None

    _global_functions = {}

    def __init__(self, parent, width, begin_y, begin_x, **kwargs):

        self._parent_win = parent
        self.width = width
        self._height = 3
        self.y = begin_y
        self.x = begin_x

        if kwargs:
            for key, value in kwargs.items():
                if key == 'boxed':
                    self._boxed = value
                    if not self._boxed:
                        self.height = 1
                elif key == 'bracket':
                    self.bracket = True
                elif key == 'string':
                    self._string = value
                elif key == 'caption':
                    ''' string on editing line '''
                    self._caption = value
                elif key == 'title':
                    ''' string on box '''
                    self.title = value
                elif key == 'box_color':
                    self.box_color = value
                elif key == 'caption_color':
                    self.caption_color = value
                elif key == 'title_color':
                    self.title_color = value
                elif key == 'edit_color':
                    self.edit_color = value
                elif key == 'cursor_color':
                    self.cursor_color = value
                elif key == 'unfocused_color':
                    self.unfocused_color = value
                elif key == 'has_history':
                    self._has_history = value
                elif key == 'ungetch_unbound_keys':
                    self._ungetch_unbound_keys = value
                elif key == 'log_file':
                    self._log_file = value
                    self.log = self._log
                elif key == 'key_up_function_handler':
                    ''' callback function for KEY_UP '''
                    self._key_up_function_handler = value
                elif key == 'key_down_function_handler':
                    ''' callback function for KEY_DOWN '''
                    self._key_down_function_handler = value
                elif key == 'key_pgup_function_handler':
                    ''' callback function for KEY_PPAGE '''
                    self._key_pgup_function_handler = value
                elif key == 'key_pgdown_function_handler':
                    ''' callback function for KEY_NPAGE '''
                    self._key_pgdown_function_handler = value
                elif key == 'key_tab_function_handler':
                    ''' callback function for TAB '''
                    self._key_tab_function_handler = value
                elif key == 'key_stab_function_handler':
                    ''' callback function for KEY_STAB '''
                    self._key_stab_function_handler = value
                elif key == 'string_changed_handler':
                    ''' callback function for KEY_STAB '''
                    self._string_changed_handler = value
                elif key == 'paste_mode_always_on':
                    ''' set paste mode and never disable it '''
                    self._paste_mode_always_on = True
                    self._paste_mode = True

        if self._has_history:
            self._input_history = SimpleCursesLineEditHistory()
        self._calculate_window_metrics()

    @property
    def focused(self):
        '''Returns if the widget has focus'''
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        if self._showed:
            self.refresh()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, val):
        self._enabled = val
        if self._showed:
            self.refresh()

    @property
    def backslash_pressed(self):
        return self._backslash_pressed

    @backslash_pressed.setter
    def backslash_pressed(self, val):
        self._backslash_pressed = val

    @property
    def paste_mode(self):
        return self._paste_mode

    @paste_mode.setter
    def paste_mode(self, val):
        self._paste_mode = val

    @property
    def use_paste_mode(self):
        return self._use_paste_mode

    @use_paste_mode.setter
    def use_paste_mode(self, val):
        self._use_paste_mode = val

    @property
    def width(self):
        if self._auto_width < 1:
            h, self._width = self._parent_win.getmaxyx()
            self._width += self._auto_width
            self._width -= self.x
        return self._width

    @width.setter
    def width(self, val):
        if val < 1:
            h, self._width = self._parent_win.getmaxyx()
            self._width -= val
            self._auto_width = val
        else:
            self._width = val
            self._auto_width = val

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, val):
        self._string = val
        self._is_cjk()
        self._go_to_end()

    @property
    def show_help_with_backslash_pressed(self):
        return self._show_help_with_backslash_pressed

    @show_help_with_backslash_pressed.setter
    def show_help_with_backslash_pressed(self, val):
        self._show_help_with_backslash_pressed = val

    @property
    def pure_ascii(self):
        return self.pure_ascii

    @pure_ascii.setter
    def pure_ascii(self, val):
        self._pure_ascii = val

    def _is_cjk(self):
        ''' Check if string contains CJK characters.
            If string is empty reset history index '''
        old_cjk = self._cjk
        if len(self.string) == cjklen(self.string):
            self._cjk = False
        else:
            self._cjk = True
        if self.string == '' and self._has_history:
            self._input_history.reset_index()
        if logger.isEnabledFor(logging.DEBUG) and self._cjk != old_cjk:
                logger.debug('=== CJK editing is {} ==='.format('ON' if self._cjk else 'OFF'))

    def keep_restore_data(self):
        ''' Keep a copy of current editor state
            so that it can be restored later. '''
        self._restore_data = [
            self.string,
            self._displayed_string,
            self._curs_pos,
            self._disp_curs_pos,
            self._first
        ]

    def getmaxyx(self):
        return self._caption_win.getmaxyx()

    def set_global_functions(self, global_functions):
        self._global_functions = {}
        if global_functions is not None:
            self._global_functions = dict(global_functions)
            if ord('t') in self._global_functions.keys():
                del self._global_functions[ord('t')]
            # if 'T' in self._global_functions.keys():
            #     del self._global_functions['T']

    def _calculate_window_metrics(self):
        if self._caption:
            if self._boxed:
                self.bracket = False
                self._disp_caption = ' ' + self._caption + ': '
                if self.title:
                    self._disp_title = ' ' + self._disp_title + ' '
                else:
                    self._disp_title = ''
            else:
                if self.bracket:
                    self._disp_caption = self._caption + ': ['
                else:
                    self._disp_caption = self._caption + ': '
                if self.title:
                    self._disp_title = self._disp_title
                else:
                    self._disp_title = ''
        else:
            if self.bracket:
                self._disp_caption = '['
            else:
                self._disp_caption = ''
        # width = len(self._disp_caption) + self._max_chars_to_display + 4
        # logger.error('DE 0 width = {0}, max_chars_to_display = {1}'.format(width, self._max_chars_to_display))
        self._max_chars_to_display = self.width - len(self._disp_caption) - 4
        # logger.error('DE 1 width = {0}, max_chars_to_display = {1}'.format(width, self._max_chars_to_display))
        if self._boxed:
            self._height = 3
        else:
            self._height = 1
            self._max_chars_to_display += 2
            if not self.bracket:
                self._max_chars_to_display += 1
        if self.log is not None:
            self.log('string_len = {}\n'.format(self._max_chars_to_display))
        # logger.error('DE 2 width = {0}, max_chars_to_display = {1}'.format(width, self._max_chars_to_display))
        return

    def _prepare_to_show(self):
        self._calculate_window_metrics()
        self._caption_win = curses.newwin(
            self._height, self.width,
            self.y, self.x
        )
        maxY, maxX = self._caption_win.getmaxyx()
        if self._boxed:
            self._edit_win = curses.newwin(
                1, maxX - len(self._disp_caption) - 2,
                self.y + 1, self.x + len(self._disp_caption) + 1
            )
            self._caption_win.addstr(
                1, 1, self._disp_caption, self.caption_color
            )
        else:
            self._caption_win.addstr(
                0, 0, self._disp_caption, self.caption_color
            )
            if self.bracket:
                self._edit_win = curses.newwin(
                    1, maxX - len(self._disp_caption) - 1,
                    self.y, self.x + len(self._disp_caption)
                )
                try:
                    ''' printing at the end of the window, do not break... '''
                    self._caption_win.addstr(0, maxX - 1, ']', self.caption_color)
                except:
                    pass
            else:
                self._edit_win = curses.newwin(
                    1, maxX - len(self._disp_caption),
                    self.y, self.x + len(self._disp_caption)
                )

        maxY, maxX = self._edit_win.getmaxyx()

    def refreshEditWindow(self, opening=False):
        if self._focused:
            active_edit_color = self.edit_color
        else:
            if self.unfocused_color >= 0:
                active_edit_color = self.unfocused_color
            else:
                active_edit_color = self.caption_color
        self._edit_win.erase()

        ''' opening '''
        if opening:
            if self._restore_data:
                self._string = self._restore_data[0]
                self._displayed_string = self._restore_data[1]
                self._curs_pos = self._restore_data[2]
                self._disp_curs_pos = self._restore_data[3]
                self._first = self._restore_data[4]
                self._restore_data = []
            else:
                self.string = self._displayed_string = ''
                self._curs_pos = self._disp_curs_pos = self._first = 0
        if self._enabled:
            self._edit_win.addstr(0, 0, self._displayed_string, active_edit_color)

        ''' reset position '''
        if self._reset_position:
            self._reset_position = False
            self._go_to_end()

        if self.log is not None:
            self.log('first={0}, curs={1}, dcurs={2}\n'.format(
                self._first, self._curs_pos, self._disp_curs_pos))
            self.log('     full string: "{}"\n'.format(self.string))
            self.log('displayed string: "{}"\n'.format(self._displayed_string))

        if self.focused:
            ''' enable this to get info on function '''
            #if logger.isEnabledFor(logging.DEBUG):
            #    logger.debug('refreshEditWindow:\n  first={0}, curs={1}, dcurs={2}, max={3}\n  len={4}, cjklen={5}\n  string="{6}"\n  len={7}, cjklen={8}\n  disstr="{9}"'.format(self._first, self._curs_pos, self._disp_curs_pos, self._max_chars_to_display, len(self.string), cjklen(self.string), self.string, len(self._displayed_string), cjklen(self._displayed_string), self._displayed_string))
            self._edit_win.chgat(0, self._disp_curs_pos, 1, self.cursor_color)

        self._edit_win.refresh()
        self._showed = True

    def move(self, parent, newY, newX, opening=False, update=True):
        if update:
            kwargs={'new_y': newY, 'new_x': newX, 'opening': opening}
            self.show(parent, **kwargs)
        else:
            self._parent_win = parent
            self.y = newY
            self.x = newX

    def refresh(self):
        self.show(self._parent_win, opening=False)

    def show(self, parent_win, **kwargs):
        opening = True
        self._caption_win = None
        self._edit_win = None
        if parent_win is not None:
            self._parent_win = parent_win
        if kwargs:
            for key, value in kwargs.items():
                if key == 'new_y':
                    self.y = value
                    if self.log is not None:
                        self.log('self.y = {}\n'.format(self.y))
                elif key == 'new_x':
                    self.x = value
                    if self.log is not None:
                        self.log('self.x = {}\n'.format(self.x))
                elif key == 'opening':
                    opening = value
        self._prepare_to_show()
        if self._focused:
            self._caption_win.bkgdset(' ', self.box_color)
            self._edit_win.bkgdset(' ', self.box_color)
        else:
            if self.unfocused_color >= 0:
                self._caption_win.bkgdset(' ', self.unfocused_color)
                self._edit_win.bkgdset(' ', self.unfocused_color)
            else:
                self._caption_win.bkgdset(' ', self.box_color)
                self._edit_win.bkgdset(' ', self.box_color)
        if self._boxed:
            self._caption_win.box()
            if self._disp_title:
                self._title_win.addstr(
                    0, 1, self._disp_title, self.title_color
                )
        self._caption_win.refresh()
        self.refreshEditWindow(opening)
        self._showed = True

    def _go_to_start(self):
        self._first = self._curs_pos = self._disp_curs_pos = 0
        self._displayed_string = self.string[:self._max_chars_to_display]
        if self._cjk:
            end = len(self._displayed_string)
            while cjklen(self._displayed_string) > self._max_chars_to_display:
                end -= 1
                self._displayed_string = self.string[:end]

    def _go_to_end(self):
        self._first = len(self.string[:-self._max_chars_to_display])
        self._displayed_string = self.string[self._first:]
        if self._cjk:
            while cjklen(self._displayed_string) > self._max_chars_to_display:
                self._first += 1
                self._displayed_string = self.string[self._first:]
            self._curs_pos = len(self._displayed_string)
            self._disp_curs_pos = cjklen(self._displayed_string)
        else:
            self._curs_pos = self._disp_curs_pos = len(self._displayed_string)

    def _at_end_of_sting(self):
        if self._at_end_of_displayed_sting():
            if self.string.endswith(self._displayed_string):
                return True
            return False
        else:
            return False

    def _at_end_of_displayed_sting(self):
        if self._disp_curs_pos >= cjklen(self._displayed_string):
            return True
        return False

    def _at_last_char_of_string(self):
        if self._at_last_char_of_displayed_string():
            if self.string.endswith(self._displayed_string):
                return True
            return False
        else:
            return False

    def _at_last_char_of_displayed_string(self):
        if self._disp_curs_pos == cjklen(self._displayed_string):
            return True
        return False

    def _delete_char(self):
        if self.string and not self._at_end_of_sting():
            self._string = self._string[:self._first + self._curs_pos] + self._string[self._first + self._curs_pos+1:]
            if self._first + self._max_chars_to_display > cjklen(self.string):
                if self._first > 0:
                    self._first -= 1
                    if self._curs_pos < self._max_chars_to_display:
                        self._curs_pos += 1
            if self._cjk:
                self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
            else:
                self._disp_curs_pos = self._curs_pos
            self._displayed_string = self.string[self._first:self._first+self._max_chars_to_display]
            while cjklen(self._displayed_string) > self._max_chars_to_display:
                self._displayed_string = self._displayed_string[:-1]
            self._is_cjk()

    def _backspace_char(self):
        if self.string:
            if self._first + self._curs_pos > 0:
                if self._curs_pos == 0:
                    ''' remove non visible char from the left of the string '''
                    self.string = self.string[:self._first-1] + self.string[self._first:]
                    self._first -= 1
                    self._curs_pos = 0
                    self._is_cjk()
                    return

                str_len = cjklen(self.string)
                if self._cjk:
                    if self._at_end_of_sting():
                        if len(self.string) == 1:
                            self.string = ''
                            self._displayed_string = ''
                            self._first = 0
                            self._curs_pos = 0
                            if self._cjk:
                                self._cjk = False
                                if logger.isEnabledFor(logging.DEBUG):
                                    logger.debug('CJK is {}'.format(self._cjk))
                        else:
                            self.string = self.string[:-1]
                            if len(self.string) <= self._max_chars_to_display:
                                self._displayed_string = self.string
                            else:
                                self._displayed_string = self._string[len(self.string) - self._max_chars_to_display:]
                            while cjklen(self._displayed_string) > self._max_chars_to_display:
                                self._displayed_string = self._displayed_string[1:]
                            self._curs_pos = len(self._displayed_string)
                            self._disp_curs_pos = cjklen(self._displayed_string)
                            self._first = len(self.string) - len(self._displayed_string)
                            if self._first < 0: self._first = 0
                    else:
                        self._curs_pos -= 1
                        curs = self._curs_pos
                        self.string = self.string[:self._first+self._curs_pos] + self.string[self._first+self._curs_pos+1:]
                        self._curs_pos = curs
                        self._displayed_string = self.string[self._first: self._first+self._max_chars_to_display]
                        while cjklen(self._displayed_string) > self._max_chars_to_display:
                            self._displayed_string = self._displayed_string[:-1]
                        self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
                else:
                    self._string = self._string[:self._first + self._curs_pos-1] + self._string[self._first + self._curs_pos:]
                    if str_len <= self._max_chars_to_display:
                        self._first = 0
                        if self._curs_pos > 0:
                            self._curs_pos -= 1
                    elif self._first + self._max_chars_to_display >= str_len:
                        if self._first > 0:
                            self._first -= 1
                    else:
                        if self._curs_pos > 0:
                            self._curs_pos -= 1
                    self._disp_curs_pos = self._curs_pos
                    self._displayed_string=self.string[self._first:self._first+self._max_chars_to_display]
                    self._is_cjk()

    def _previous_word(self):
        if self._first + self._curs_pos > 0:
            pos = 0
            str_len = cjklen(self.string)
            for n in range(self._first + self._curs_pos - 1, 0, -1):
                if self._string[n] in self._word_delim:
                    if n < self._first + self._curs_pos - 1:
                        pos = n
                        break
            if pos == 0:
                ''' word_delimiter not found: '''
                self._go_to_start()
                return
            else:
                ''' word delimiter found '''
                if str_len < self._max_chars_to_display or \
                        pos >= self._first:
                    ''' pos is on screen '''
                    self._curs_pos = pos - self._first + 1
                else:
                    self._first = n + 1
                    self._curs_pos = 0
                    self._displayed_string = self.string[self._first:self._first+self._max_chars_to_display]
                self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
                while cjklen(self._displayed_string) > self._max_chars_to_display:
                    self._displayed_string = self._displayed_string[:-1]

    def _next_word(self):
        if self._at_end_of_sting():
            return
        if self._first + self._curs_pos + 1 >= len(self.string):
            self._go_to_end()
            return
        pos = 0
        for n in range(self._first + self._curs_pos + 1, len(self.string)):
            if self._string[n] in self._word_delim:
                pos = n
                break
        if pos >= len(self.string):
            pos = 0
        if pos > 0:
            if pos < len(self._displayed_string):
                ''' pos is on screen '''
                self._curs_pos = pos + 1 - self._first
                self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
            else:
                if pos < self._first + len(self._displayed_string):
                    ''' pos is on middle and on screen '''
                    self._curs_pos = pos - self._first + 1
                    self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
                else:
                    ''' pos is off screen '''
                    self._first = 0
                    self._curs_pos = pos + 2
                    self._displayed_string = tmp = self.string[:self._curs_pos]
                    while cjklen(tmp) > self._max_chars_to_display:
                        self._first += 1
                        tmp = self._displayed_string[self._first:]
                    self._displayed_string = tmp
                    self._curs_pos = len(self._displayed_string) - 1
                    self._disp_curs_pos = cjklen(self._displayed_string[:-1])

        else:
            ''' word delimiter not found '''
            self._go_to_end()

    def _go_right(self):
        if self.string and not self._at_end_of_sting():
            if self._cjk:
                if cjklen(self.string) < self._max_chars_to_display:
                    ''' just go to next char '''
                    if self._curs_pos <= len(self.string):
                        self._curs_pos += 1
                    self._disp_curs_pos = cjklen(self.string[:self._curs_pos])
                    self._displayed_string = self.string

                else:
                    at_end_of_disp = self._at_last_char_of_displayed_string()
                    self._curs_pos += 1
                    if self._curs_pos <= len(self._displayed_string):
                        ''' just go to next char '''
                        self._disp_curs_pos = cjklen(self.string[self._first:self._first+self._curs_pos])
                    else:
                        ''' scroll one char right '''
                        self._displayed_string = self.string[self._first:self._first+len(self._displayed_string)+1]
                        while cjklen(self._displayed_string) >= self._max_chars_to_display + 1:
                            self._first += 1
                            self._displayed_string = self._displayed_string[1:]
                        self._disp_curs_pos = cjklen(self._displayed_string) - cjklen(self._displayed_string[-1])
                        if at_end_of_disp:
                            self._disp_curs_pos += cjklen(self._displayed_string[-1])
            else:
                self.__to_right_simple()
            if self._curs_pos > len(self._displayed_string):
                self._curs_pos = len(self._displayed_string)

    def __to_right_simple(self):
        if len(self.string) < self._max_chars_to_display:
            self._curs_pos += 1
            if self._curs_pos > len(self.string):
                    self._curs_pos = len(self.string)
            else:
                if len(self._string) < self._first + self._curs_pos:
                    self._curs_pos = len(self._string) - self._max_chars_to_display
        else:
            if self._curs_pos == self._max_chars_to_display:
                if len(self._string) > self._first + self._curs_pos:
                    self._first += 1
            else:
                self._curs_pos += 1
        self._disp_curs_pos = self._curs_pos
        disp_string = self.string[self._first:self._first + self._max_chars_to_display]
        self._displayed_string = disp_string[:self._max_chars_to_display]

    def _go_left(self):
        if self._first + self._curs_pos > 0:
            if self._cjk:
                if self._curs_pos > 0:
                    ''' just go to previous char '''
                    self._curs_pos -= 1
                    self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
                else:
                    self._first -= 1
                    self._displayed_string = self.string[self._first: self._first+self._max_chars_to_display]
                    while cjklen(self._displayed_string) > self._max_chars_to_display:
                        self._displayed_string = self._displayed_string[:-1]
            else:
                # logger.error('simple')
                self._go_left_simple()

    def _go_left_simple(self):
        if len(self.string) < self._max_chars_to_display:
            self._curs_pos -= 1
            if self._curs_pos < 0:
                self._curs_pos = 0
        else:
            if self._curs_pos == 0:
                self._first -= 1
                if self._first < 0:
                    self._first = 0
            else:
                self._curs_pos -= 1
        self._disp_curs_pos = self._curs_pos
        disp_string = self.string[self._first:self._first + self._max_chars_to_display]
        self._displayed_string = disp_string[:self._max_chars_to_display]

    def _clear_to_start_of_line(self):
        if self.string:
            self.string = self._string[self._first + self._curs_pos:]
            self._go_to_start()
            self._is_cjk()

    def _clear_to_end_of_line(self):
        if self.string:
            self.string = self._string[:self._first + self._curs_pos]
            self._go_to_end()
            self._is_cjk()

    def _can_show_help(self):
        ''' return not xor of two values
                self._backslash_pressed,
                self._show_help_with_backslash_pressed'''
        if self._paste_mode:
            return False
        return not (
            (self._backslash_pressed and
             not self._show_help_with_backslash_pressed)
            or (not self._backslash_pressed
                and self._show_help_with_backslash_pressed))

    def keypress(self, win, char):
        '''
         returns:
            2: display help
            1: get next char
            0: exit edit mode, string is valid
           -1: cancel
        '''
        #self._log_file='/home/spiros/edit.log'
        #self._log_file='C:\\Users\\spiros\\edit.log'
        #self.log = self._log
        if not self._focused:
            return 1
        if self.log is not None:
            self.log('char = {}\n'.format(char))

        if char in self._global_functions.keys() and \
                self._backslash_pressed:
            ''' toggle paste mode '''
            self._backslash_pressed = False
            if not self._paste_mode_always_on:
                self._paste_mode = False
                if self._mode_changed:
                    self._mode_changed()
            self._global_functions[char]()
            return 1

        if platform.startswith('win'):
            if char == 420:
                ''' A-D, clear to end of line '''
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: clear-to-end')
                self._clear_to_end_of_line()
                self.refreshEditWindow()
                if self._string_changed_handler:
                    self._string_changed_handler()
                if self._use_paste_mode and self._paste_mode:
                    self._paste_mode = self._disable_paste_mode = False
                    if self._mode_changed:
                        self._mode_changed()
                return 1
            elif char == 422:
                ''' A-F, move to next word '''
                if self.string:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug('action: next-word')
                    self._next_word()
                    self.refreshEditWindow()

                    if not self._paste_mode_always_on:
                        if self._use_paste_mode and self._paste_mode:
                            self._paste_mode = self._disable_paste_mode = False
                            if self._mode_changed:
                                self._mode_changed()
                return 1
            elif char == 418:
                ''' A-B, move to previous word '''
                if self.string:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug('action: previous-word')
                    self._previous_word()
                    if not self._paste_mode_always_on:
                        if self._use_paste_mode and self._paste_mode:
                            self._paste_mode = self._disable_paste_mode = False
                            if self._mode_changed:
                                self._mode_changed()
                return 1

        if char == 92 and not self._backslash_pressed and not self._paste_mode:
            self._backslash_pressed = True
            if self._mode_changed:
                self._mode_changed()
            return 1

        elif char in (ord('?'), ) and self._can_show_help():
            ''' display help '''
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('action: help')
            self.keep_restore_data()
            self._backslash_pressed = False
            if self._mode_changed:
                self._mode_changed()
            if not self._paste_mode_always_on:
                if self._use_paste_mode and self._paste_mode:
                    self._paste_mode = self._disable_paste_mode = False
                    if self._mode_changed:
                        self._mode_changed()
            return 2

        elif char in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            ''' ENTER '''
            self._backslash_pressed = False
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('action: enter')
            if self._has_history:
                self._input_history.add_to_history(self._string)
            if not self._paste_mode_always_on:
                if self._use_paste_mode and self._paste_mode:
                    self._paste_mode = self._disable_paste_mode = False
                    if self._mode_changed:
                        self._mode_changed()
            return 0

        elif char in (curses.KEY_EXIT, 27):
            self._backslash_pressed = False
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('action: ESCAPE')
            self._edit_win.nodelay(True)
            char = self._edit_win.getch()
            if self.log is not None:
                self.log('   *** char = {}\n'.format(char))
            self._edit_win.nodelay(False)
            if not self._paste_mode_always_on:
                if self._use_paste_mode and self._paste_mode:
                    self._disable_paste_mode = True
            if char == -1:
                ''' ESCAPE '''
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: Cancel')
                self._string = ''
                self._curs_pos = 0
                if self._input_history:
                    self._input_history.reset_index()
                if not self._paste_mode_always_on:
                    if self._use_paste_mode and self._paste_mode:
                        self._paste_mode = self._disable_paste_mode = False
                        if self._mode_changed:
                            self._mode_changed()
                return -1
            else:
                if self.log is not None:
                    self.log('   *** char = {}\n'.format(char))
                if char in (ord('d'), ):
                    ''' A-D, clear to end of line '''
                    if self.string:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug('action: clear-to-end')
                        self._clear_to_end_of_line()
                        if self._string_changed_handler:
                            self._string_changed_handler()
                elif char in (ord('f'), ):
                    ''' A-F, move to next word '''
                    if self.string:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug('action: next-word')
                        self._next_word()
                elif char in (ord('b'), ):
                    ''' A-B, move to previous word '''
                    if self.string:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug('action: previous-word')
                        self._previous_word()
                else:
                    if not self._paste_mode_always_on:
                        if self._use_paste_mode and self._paste_mode:
                            self._paste_mode = self._disable_paste_mode = False
                            if self._mode_changed:
                                self._mode_changed()
                    return 1

        elif char in (curses.KEY_RIGHT, ):
            ''' KEY_RIGHT '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: RIGHT')
            self._go_right()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_LEFT, ):
            ''' KEY_LEFT '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: LEFT')
                self._go_left()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_HOME, curses.ascii.SOH):
            ''' KEY_HOME, ^A '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: HOME')
                self._go_to_start()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_END, curses.ascii.ENQ):
            ''' KEY_END, ^E '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: END')
                self._go_to_end()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.ascii.ETB, ):
            ''' ^W, clear to start of line '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: clear-to-end')
                self._clear_to_start_of_line()
                if self._string_changed_handler:
                    self._string_changed_handler()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.ascii.VT, ):
            ''' Ctrl-K - clear to end of line '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: clear-to-end')
                self._clear_to_end_of_line()
                if self._string_changed_handler:
                    self._string_changed_handler()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.ascii.NAK, ):
            ''' ^U, clear line '''
            self._backslash_pressed = False
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('action: clear')
            self.string = self._displayed_string = ''
            self._first = self._curs_pos = self._disp_curs_pos = 0
            self._is_cjk()
            if self._string_changed_handler:
                self._string_changed_handler()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_DC, curses.ascii.EOT):
            ''' DEL key, ^D '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: delete')
                self._delete_char()
                if self._string_changed_handler:
                    self._string_changed_handler()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_BACKSPACE, curses.ascii.BS, 127):
            ''' KEY_BACKSPACE '''
            self._backslash_pressed = False
            if self.string:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('action: backspace')
                self._backspace_char()
                if self._string_changed_handler:
                    self._string_changed_handler()
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_UP, curses.ascii.DLE):
            ''' KEY_UP, ^N '''
            self._backslash_pressed = False
            if self._key_up_function_handler is not None:
                try:
                    self._key_up_function_handler()
                except:
                    pass
            else:
                if self._ungetch_unbound_keys:
                    curses.ungetch(char)
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_DOWN, curses.ascii.SO):
            ''' KEY_DOWN, ^P '''
            self._backslash_pressed = False
            if self._key_down_function_handler is not None:
                try:
                    self._key_down_function_handler()
                except:
                    pass
            else:
                if self._ungetch_unbound_keys:
                    curses.ungetch(char)
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_NPAGE, ):
            ''' PgDn '''
            self._backslash_pressed = False
            if self._key_pgdown_function_handler is not None:
                try:
                    self._key_pgdown_function_handler()
                except:
                    pass
            else:
                if self._ungetch_unbound_keys:
                    curses.ungetch(char)
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_PPAGE, ):
            ''' PgUp '''
            self._backslash_pressed = False
            if self._key_pgup_function_handler is not None:
                try:
                    self._key_pgup_function_handler()
                except:
                    pass
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (9, ):
            ''' TAB '''
            self._backslash_pressed = False
            if self._key_tab_function_handler is not None:
                try:
                    self._key_tab_function_handler()
                except:
                    pass
            else:
                if self._ungetch_unbound_keys:
                    curses.ungetch(char)
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif char in (curses.KEY_BTAB, ):
            ''' Shift-TAB '''
            self._backslash_pressed = False
            if self._key_stab_function_handler is not None:
                try:
                    self._key_stab_function_handler()
                except:
                    pass
            else:
                if self._ungetch_unbound_keys:
                    curses.ungetch(char)
            if self._use_paste_mode and self._paste_mode:
                self._disable_paste_mode = True

        elif 0 <= char <= 31:
            ''' do not accept any other control characters '''
            self._backslash_pressed = False

        elif char == ord('p') and self._backslash_pressed \
                and self._use_paste_mode:
            ''' toggle paste mode '''
            self._backslash_pressed = False
            self._paste_mode = True
            self._disable_paste_mode = False
            if self._mode_changed:
                self._mode_changed()

        else:
            self._backslash_pressed = False
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('action: add-character')
            if self.log is not None:
                self.log('====================\n')
            if version_info < (3, 0) or (self._pure_ascii and not platform.startswith('win')):
                if 32 <= char < 127:
                    ''' accept only ascii characters '''
                    if len(self._string) == self._first + self._curs_pos:
                        self._string += chr(char)
                        self._add_to_end = True
                        self._curs_pos += 1
                        self._displayed_string = self._string[self._first:self._first+self._curs_pos]
                    else:
                        self._string = self._string[:self._first + self._curs_pos] + chr(char) + self._string[self._first + self._curs_pos:]
                        self._add_to_end = False
                        self._curs_pos += 1
                        self._disp_curs_pos = self._curs_pos
                        self._displayed_string = self.string[self._first:self._first+self._max_chars_to_display]
            else:
                if platform.startswith('win'):
                    char = chr(char)
                else:
                    char = self._get_char(win, char)
                if char is None:
                    return 1
                if self._pure_ascii:
                    if ord(char) > 127:
                        return 1
                #if len(self._string) == self._first + self._curs_pos:
                if self._at_end_of_sting():
                    self._string += char
                    self._add_to_end = True
                    self._curs_pos += 1
                    self._displayed_string = self._string[self._first:self._first+self._curs_pos]
                else:
                    self._string = self._string[:self._first + self._curs_pos] + char + self._string[self._first + self._curs_pos:]
                    self._curs_pos += 1
                    self._add_to_end = False
                    self._displayed_string = self.string[self._first:self._first+self._max_chars_to_display]
            if self._add_to_end:
                ''' adding to end of string '''
                while cjklen(self._displayed_string) > self._max_chars_to_display:
                    self._displayed_string = self._displayed_string[1:]
                    self._first += 1
                    self._curs_pos -= 1
                if self._cjk:
                    self._disp_curs_pos = cjklen(self._displayed_string)
                else:
                    self._disp_curs_pos = self._curs_pos
            else:
                ''' adding to middle of string '''
                while cjklen(self._displayed_string) > self._max_chars_to_display:
                    self._displayed_string = self._displayed_string[:-1]
                if self._cjk:
                    self._disp_curs_pos = cjklen(self._displayed_string[:self._curs_pos])
                else:
                    self._disp_curs_pos = self._curs_pos
            if self._string_changed_handler:
                self._string_changed_handler()
        self.refreshEditWindow()
        # logger.error('self._disable_paste_mode = {}'.format(self._disable_paste_mode))
        if not self._paste_mode_always_on:
            if self._disable_paste_mode:
                self._paste_mode = self._disable_paste_mode = False
            if self._mode_changed:
                self._mode_changed()
        return 1

    def _get_char(self, win, char):
        def get_check_next_byte():
            char = win.getch()
            if 128 <= char <= 191:
                return char
            else:
                raise UnicodeError

        bytes = []
        if char <= 127:
            ''' 1 byte '''
            bytes.append(char)
        #elif 194 <= char <= 223:
        elif 192 <= char <= 223:
            ''' 2 bytes '''
            bytes.append(char)
            bytes.append(get_check_next_byte())
        elif 224 <= char <= 239:
            ''' 3 bytes '''
            bytes.append(char)
            bytes.append(get_check_next_byte())
            bytes.append(get_check_next_byte())
        elif 240 <= char <= 244:
            ''' 4 bytes '''
            bytes.append(char)
            bytes.append(get_check_next_byte())
            bytes.append(get_check_next_byte())
            bytes.append(get_check_next_byte())
        ''' no zero byte allowed '''
        while 0 in bytes:
            bytes.remove(0)
        if version_info < (3, 0):
            out = ''.join([chr(b) for b in bytes])
        else:
            buf = bytearray(bytes)
            out = self._decode_string(buf)
            if out:
                if PY3:
                    if is_wide(out) and not self._cjk:
                        self._cjk = True
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug('=== CJK editing is ON ===')
            else:
                out = None
        return out

    def _encode_string(self, data):
        encodings = ['utf-8', locale.getpreferredencoding(False), 'latin1']
        for enc in encodings:
            try:
                data = data.encode(enc)
            except:
                continue
            break

        assert type(data) != bytes  # Latin1 should have worked.
        return data

    def _decode_string(self, data):
        encodings = ['utf-8', locale.getpreferredencoding(False), 'latin1']
        for enc in encodings:
            try:
                data = data.decode(enc)
            except:
                continue
            break

        assert type(data) != bytes  # Latin1 should have worked.
        return data

    def _log(self, msg):
        with open(self._log_file, 'a') as log_file:
            log_file.write(msg)

    def run(self):
        self._edit_win.nodelay(False)
        self._edit_win.keypad(True)
        ''' make sure we don't get into an infinite loop '''
        self._ungetch_unbound_keys = False
        try:
            curses.curs_set(0)
        except:
            pass

        while True:
            char = self._edit_win.getch()
            ret = self.keypress(char)
            if ret != 1:
                return ret


class SimpleCursesLineEditHistory(object):

    def __init__(self):
        self._history = ['']
        self._active_history_index = 0

    def add_to_history(self, a_string):
        if a_string:
            if self._history:
                if len(self._history) > 1:
                    for i, a_history_item in enumerate(self._history):
                        if a_history_item.lower() == a_string.lower():
                            self._history.pop(i)
                            break
                if self._history[-1].lower() != a_string.lower():
                    self._history.append(a_string)
            else:
                self._history.append(a_string)
            self._active_history_index = len(self._history)

    def return_history(self, direction, current_string):
        if self._history:
            self._active_history_index += direction
            if self._active_history_index <= -1:
                self._active_history_index = len(self._history) - 1
            elif self._active_history_index >= len(self._history):
                self._active_history_index = 0
            ret = self._history[self._active_history_index]
            if ret.lower() == current_string.lower():
                return self.return_history(direction, current_string)
            return ret
        return ''

    def reset_index(self):
        self._active_history_index = 0


class SimpleCursesBoolean(SimpleCursesCounter):
    ''' A class to provide a Boolean value

        Parameters
        ==========
        Y, X, window
            Coordinates and parent window
        value
            the value, either Tru of False (default)
        color
            text color
        color_focused
            counter color when enabled and focused
        color_not_focused
            counter color when enabled but not focused
        color_disabled
            counter color when disabled
        full_slection
            if not None, it should be a tuple:
                (go left from self._X, numbder of chars to print)
            draw selection cursor as a full line
    '''

    def __init__(
        self, Y, X, window,
        color, color_focused,
        color_not_focused,
        color_disabled,
        string='{0}', value=False,
        full_selection=None
    ):
        self._Y = Y
        self._X = X
        self._win = self._parent = window
        self._value = value
        self.string = string
        self._color = color
        self._color_focused = color_focused
        self._color_not_focused = color_not_focused
        self._color_disabled = color_disabled
        self._full_selection = full_selection

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        logger.error('Bool: {}'.format(self._value))

    def _print_full_line(self, col):
        tmp = self._full_selection[0] * ' ' + self._prefix + str(self._value) + self._suffix
        self._win.addstr(
            self._Y,
            self._X - self._full_selection[0],
            tmp.ljust(self._full_selection[1]),
            col
        )

    def show(self, window=None):
        if window:
            self._win = self._parent = window
        if self._enabled:
            if self._focused:
                col = self._color_focused
            else:
                col = self._color_not_focused
        else:
            col = self._color_disabled
        if self._full_selection and self._enabled and self._focused:
            self._print_full_line(col)
        else:
            if self._full_selection:
                self._win.addstr(
                    self._Y,
                    self._X - self._full_selection[0],
                    (self._full_selection[1] ) * ' ',
                    self._color
                )
            self._win.move(self._Y, self._X)
            if self._prefix:
                self._win.addstr( self._prefix, self._color)
            self._win.addstr(str(self._value).ljust(5), col)
            if self._suffix:
                self._win.addstr(self._suffix, self._color)
            ''' overwrite last self._len characters '''
            self._win.addstr(' ' * 2, self._color)
        self._showed = True

    def keypress(self, char):
        ''' SimpleCursesBoolean keypress

            Returns
            -------
               -1 - Cancel
                0   Value changed
                1 - Continue
                2 - Display help
        '''
        if (not self._focused) or (not self._enabled):
            return 1

        if char in (
            curses.KEY_EXIT, ord('q'), 27,
        ):
            return -1

        elif char == ord('?'):
            return 2

        elif char in (ord(' '),
                      ord('\n'), ord('\r'),
                      curses.KEY_ENTER,
                      ord('h'),
                      curses.KEY_LEFT,
                      ord('l'),
                      curses.KEY_RIGHT):
            self.toggle()
            self.show(self._win)
            return 0

        return 1

    def toggle(self):
        ''' toggles SimpleCursesBoolean value '''
        self._value = not self._value


#
#   Testing part
#

import logging
logger = logging.getLogger('pyradio')
logger.setLevel(logging.DEBUG)

def main(stdscr):
    __configureLogger()
    # curses.start_color()
    # curses.use_default_colors()
    #stdscr.addstr('Number of colors: {0}, number of pairs: {1}\n'.format(curses.COLORS, curses.COLOR_PAIRS), curses.color_pair(0))
    #stdscr.getch()

    #pr(stdscr)
    #stdscr.getch()

    curses.init_pair(4,curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5,curses.COLOR_WHITE,curses.COLOR_BLACK)
    curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_RED)
    curses.init_pair(9,curses.COLOR_BLACK,curses.COLOR_WHITE)
    #curses.init_pair(1,237,248)
    #for n in range(3,13):
    #    stdscr.addstr(n,1,str(n),curses.color_pair(1))

    stdscr.bkgdset(' ', curses.color_pair(3))
    stdscr.erase()
    stdscr.refresh()
    search_by_items = (
        'Votes',
        'Clicks',
        'Recent click',
        'Recently changed',
        'Item 1',
        'Item 2',
        'Item 3',
        'Item 4',
        'Item 5',
        'Item 6',
    )

    a_widget = SimpleCursesWidgetColumns(
        Y=2, X=3, window=stdscr,
        selection=0,
        active=0,
        items=search_by_items,
        color=curses.color_pair(5),
        color_active=curses.color_pair(4),
        color_cursor_selection=curses.color_pair(6),
        color_cursor_active=curses.color_pair(9),
        margin=1,
        max_width=65,
        on_up_callback_function=up,
        on_down_callback_function=down,
        on_left_callback_function=left,
        on_right_callback_function=right
    )
    # a_widget.show()

    a_widget = SimpleCursesBoolean(
        Y=2, X=3, window=stdscr,
        color=curses.color_pair(5),
        color_focused=curses.color_pair(9),
        color_not_focused=curses.color_pair(4),
        color_disabled=curses.color_pair(5),
        string='The valued is: {0}'
    )
    a_widget.focused = True
    a_widget.show(window=stdscr)

    while True:
        try:
            c = stdscr.getch()
            # logger.error('DE pressed "{0} - {1}"'.format(c, chr(c)))
            ret = a_widget.keypress(c)
            if (ret == -1):
                return
        except KeyboardInterrupt:
            break

def up():
    logger.error('up')

def down():
    logger.error('down')

def left():
    logger.error('left')

def right():
    logger.error('right')

def __configureLogger():
    logger = logging.getLogger('pyradio')
    logger.setLevel(logging.DEBUG)

    # Handler
    fh = logging.FileHandler('/home/spiros/pyradio.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    PATTERN = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(PATTERN)

    # add formatter to ch
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(fh)

if __name__ == "__main__":
    curses.wrapper(main)

