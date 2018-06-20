import unittest
import os
import sys
sys.path.append('..')
from unittest.mock import patch
from flask import current_app
from app import create_app, db
from app.models import YoutubeVideoDB
from app.main.youtube.youtube_video import Youtube_Video
from app.main.youtube.sort_videos import sort_videos
from rq import Queue, Connection, get_current_job, get_failed_queue
from fakeredis import FakeStrictRedis


class SortVideosTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.app_context().push()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @staticmethod
    def search_replacement1(*args):
        video1 = Youtube_Video(videoid="VX65Xdy8cKA")
        video2 = Youtube_Video(videoid="BTa2P8Z-O0w")
        return [video1, video2]

    @patch('app.main.youtube.search.youtube_search')
    def test_current_and_total_attributes(self, search_replacement):
        queue = Queue(async=False, connection=FakeStrictRedis())
        job = queue.enqueue(sort_videos("test"))
        while(job.complete is False):
            continue
        self.assertEqual(job.meta['current'], job.meta['total'], 2)


if __name__ == "__main__":
    unittest.main(verbosity=0)
