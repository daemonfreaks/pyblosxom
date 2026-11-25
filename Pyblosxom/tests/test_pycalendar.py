#######################################################################
# This file is part of Pyblosxom.
#
# Copyright (C) 2010-2011 by the Pyblosxom team.  See AUTHORS.
#
# Pyblosxom is distributed under the MIT license.  See the file
# LICENSE for distribution details.
#######################################################################

from Pyblosxom.plugins import pycalendar

import os
import unittest
import tempfile
import shutil

class PyCalendarTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        if hasattr(self, 'tmpdir'):
            shutil.rmtree(self.tmpdir)

    def get_datadir(self):
        return os.path.join(self.tmpdir, "datadir")

    entry1 = {"timetuple": (2010, 1, 17, 15, 48, 20, 6, 17, 0)}

    def test_generate_calendar(self):
        entry1 = dict(PyCalendarTest.entry1)

        from Pyblosxom.pyblosxom import Request
        req = Request({"datadir": self.get_datadir()},
                      {},
                      {"entry_list": [entry1],
                       "extensions": {}})
        pycalendar.cb_prepare({"request": req})

        data = req.get_data()
        cal = data["calendar"]

        cal.generate_calendar()

    def test_links_do_not_depend_on_locale(self):
        """Calendar links must use month numbers so that they resolve
        whatever the locale is (e.g. "%b" is " 9月" under ja_JP)."""
        import locale
        import re
        import time

        old_locale = locale.setlocale(locale.LC_TIME)
        try:
            try:
                locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
            except locale.Error:
                self.skipTest("ja_JP.UTF-8 locale is not available")

            datadir = self.get_datadir()
            os.makedirs(datadir)
            for name, date in (("sep.txt", (2026, 9, 26, 15, 0, 0, 0, 0, -1)),
                               ("oct.txt", (2026, 10, 12, 16, 40, 0, 0, 0, -1)),
                               ("nov.txt", (2026, 11, 3, 12, 0, 0, 0, 0, -1))):
                path = os.path.join(datadir, name)
                with open(path, "w") as fp:
                    fp.write("title\nbody\n")
                mtime = time.mktime(date)
                os.utime(path, (mtime, mtime))

            from Pyblosxom.pyblosxom import Request
            entry = {"timetuple": (2026, 10, 12, 16, 40, 0, 0, 285, 0)}
            req = Request({"datadir": datadir,
                           "base_url": "http://example.com/blog"},
                          {},
                          {"entry_list": [entry],
                           "extensions": {"txt": None}})
            pycalendar.cb_prepare({"request": req})

            cal = req.get_data()["calendar"]
            cal.generate_calendar()

            hrefs = re.findall(r'href="([^"]*)"', cal._cal)
            self.assertEqual(sorted(hrefs),
                             ["http://example.com/blog/2026/09",
                              "http://example.com/blog/2026/10/12",
                              "http://example.com/blog/2026/11"])
        finally:
            locale.setlocale(locale.LC_TIME, old_locale)
