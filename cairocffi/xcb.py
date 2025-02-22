"""
    cairocffi.xcb
    ~~~~~~~~~~~~~

    Bindings for XCB surface objects using xcffib.

    :copyright: Copyright 2014-2019 by Simon Sapin
    :license: BSD, see LICENSE for details.
"""

from xcffib import visualtype_to_c_struct

from . import dlopen
from . import cairo, constants
from .surfaces import SURFACE_TYPE_TO_CLASS, Surface

# Attempt api mode, then precompiled abi mode, then import time abi
cffi_mode = "(unknown)"
try:
    # Note in ABI mode lib is already available, no dlopen() needed
    from ._cairocffi_xcb import ffi, lib as cairo_xcb
    cffi_mode = "api"
except ImportError:
    try:
        # Note in ABI mode lib will be missing
        from ._cairocffi_xcb import ffi
        cffi_mode = "abi_precompiled"
    except ImportError:
        # Fall back to importing and parsing cffi defs
        from .ffi_build import xcb_ffi_for_mode
        ffi = xcb_ffi_for_mode("abi")
        cffi_mode = "abi"


if cffi_mode != "api":
    cairo_xcb = dlopen(
        ffi, ('xcb'),
        ('libxcb.so', 'libxcb.dylib',
         'libxcb.dll'))


class XCBSurface(Surface):
    """The XCB surface is used to render cairo graphics to X Window System
    windows and pixmaps using the XCB library.

    Creates a cairo surface that targets the given drawable (pixmap or window).

    .. note::

        This class works using objects and libraries in ``xcffib``.

    :param conn: The ``xcffib.Connection`` for an open XCB connection
    :param drawable:
        An XID corresponding to an XCB drawable (a pixmap or a window)
    :param visual: An ``xcffib.xproto.VISUALTYPE`` object.
    :param width: integer
    :param height: integer
    """
    def __init__(self, conn, drawable, visual, width, height):
        c_visual = visualtype_to_c_struct(visual)

        p = cairo_xcb.cairo_xcb_surface_create(
            conn._conn, drawable, c_visual, width, height)
        Surface.__init__(self, p)

    def set_size(self, width, height):
        """
        Informs cairo of the new size of the X Drawable underlying the surface.
        For a surface created for a Window (rather than a Pixmap), this
        function must be called each time the size of the window changes (for
        a subwindow, you are normally resizing the window yourself, but for a
        toplevel window, it is necessary to listen for
        :class:`xcffib.xproto.ConfigureNotifyEvent`'s).

        A Pixmap can never change size, so it is never necessary to call this
        function on a surface created for a Pixmap.

        :param width: integer
        :param height: integer
        """
        cairo_xcb.cairo_xcb_surface_set_size(self._pointer, width, height)
        self._check_status()


SURFACE_TYPE_TO_CLASS[constants.SURFACE_TYPE_XCB] = XCBSurface
