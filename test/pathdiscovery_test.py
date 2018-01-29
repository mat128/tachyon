# Tachyon - Fast Multi-Threaded Web Discovery Tool
# Copyright (c) 2011 Gabriel Tremblay - initnull hat gmail.com
#
# GNU General Public Licence (GPL)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA

from unittest import TestCase
from unittest.mock import MagicMock
from hammertime.core import HammerTime
from hammertime.ruleset import RejectRequest
from urllib.parse import urlparse

from core.database import valid_paths
from core.directoryfetcher import DirectoryFetcher
from fixtures import async


class TestPathDiscovery(TestCase):

    def setUp(self):
        valid_paths.clear()

    @async()
    async def test_fetch_paths_add_valid_path_to_database(self, loop):
        valid = ["/a", "b", "/c", "/1", "/2", "/3"]
        invalid = ["/d", "/e", "/4", "/5"]
        paths = valid + invalid
        hammertime = HammerTime(loop=loop, request_engine=FakeHammertimeEngine())
        hammertime.heuristics.add(RejectInvalidPaths(invalid))
        directory_fetcher = DirectoryFetcher("http://example.com", hammertime)

        await directory_fetcher.fetch_paths(paths)

        self.assertEqual(len(valid), len(valid_paths))
        for path in valid_paths:
            self.assertIn(path, valid)
            self.assertNotIn(path, invalid)


class FakeHammertimeEngine:

    async def perform(self, entry, heuristics):
        await heuristics.before_request(entry)
        await heuristics.after_headers(entry)
        await heuristics.after_response(entry)
        return entry


class RejectInvalidPaths:

    def __init__(self, invalid_paths):
        self.invalid_paths = invalid_paths

    async def before_request(self, entry):
        path = urlparse(entry.request.url).path
        if path in self.invalid_paths:
            raise RejectRequest("Invalid path")
