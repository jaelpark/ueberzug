import sys
import struct
import fcntl
import termios
import math


class TerminalInfo:
    @staticmethod
    def get_size(fd_pty=None):
        """Determines the columns, rows, width (px), height (px) of the terminal.

        Returns:
            tuple of int: cols, rows, width, height
        """
        fd_pty = fd_pty or sys.stdout.fileno()
        farg = struct.pack("HHHH", 0, 0, 0, 0)
        fretint = fcntl.ioctl(fd_pty, termios.TIOCGWINSZ, farg)
        rows, cols, xpixels, ypixels = struct.unpack("HHHH", fretint)
        return cols, rows, xpixels, ypixels

    @staticmethod
    def __get_font_size_padding(chars, pixels):
        # (this won't work all the time but
        # it's still better than disrespecting padding all the time)
        # let's assume the padding is the same on both sides:
        # let font_width = floor(xpixels / cols)
        # (xpixels - padding)/cols = font_size
        # <=> (xpixels - padding) = font_width * cols
        # <=> - padding = font_width * cols - xpixels
        # <=> padding = - font_width * cols + xpixels
        font_size = math.floor(pixels / chars)
        padding = (- font_size * chars + pixels) / 2
        return font_size, padding

    def __init__(self, pty=None):
        self.font_width = None
        self.font_height = None
        self.padding = None

        if isinstance(pty, (int, type(None))):
            self.__calculate_sizes(pty)
        else:
            with open(pty) as fd_pty:
                self.__calculate_sizes(fd_pty)

    def __calculate_sizes(self, fd_pty):
        """Calculates the values for font_{width,height} and
        padding_{horizontal,vertical}.
        """
        cols, rows, xpixels, ypixels = TerminalInfo.get_size(fd_pty)
        self.font_width, padding_horizontal = \
            TerminalInfo.__get_font_size_padding(cols, xpixels)
        self.font_height, padding_vertical = \
            TerminalInfo.__get_font_size_padding(rows, ypixels)
        self.padding = max(padding_horizontal, padding_vertical)
