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


class YoutubeVideoTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.app_context().push()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_download_video_normal(self):
        """Tests the downloading of a video with normal captioning."""
        DOWNLOADS = "%s/files" % os.path.abspath(os.path.dirname(__file__))
        video = Youtube_Video(videoid="VX65Xdy8cKA")
        video.download_sub()
        with open("%s/video_caption.txt" % (DOWNLOADS)) as file:
            caption = file.read()
        self.assertEqual(video.caption, caption)

    def test_download_video_none(self):
        """Tests downloading the caption of a video with no caption track."""
        no_caption_video = Youtube_Video(videoid="BTa2P8Z-O0w")
        no_caption_video.download_sub()
        self.assertEqual(no_caption_video.caption, "")

    def test_added_to_db(self):
        """Tests Youtube_Video.add_to_db ability to add to the database
            at all"""
        video = Youtube_Video(videoid="BTa2P8Z-O0w",
                              title="test",
                              caption="",
                              score=0)
        video.add_to_db()
        videodb = YoutubeVideoDB.query.filter_by(videoid="BTa2P8Z-O0w").first()
        self.assertFalse(videodb is None)

    def test_info_added_to_db(self):
        video = Youtube_Video(videoid="000",
                              title="test2",
                              caption="caption",
                              score=1)
        video.add_to_db()
        videodb = YoutubeVideoDB.query.filter_by(videoid="000").first()
        self.assertEqual(videodb.videoid, video.videoid)
        self.assertEqual(videodb.title, video.title)
        self.assertEqual(videodb.score, video.score)
        self.assertEqual(videodb.caption, video.caption)

    def test_illegal_add_to_db(self):
        """Tests that videos with no titles or videoids are not
            added to the db"""
        video1 = Youtube_Video(videoid="001")
        video1.add_to_db()
        videodb1 = YoutubeVideoDB.query.filter_by(videoid="001").first()
        self.assertEqual(videodb1, None)
        video2 = Youtube_Video(title="test3")
        video2.add_to_db()
        videodb2 = YoutubeVideoDB.query.filter_by(title="test3").first()
        self.assertEqual(videodb2, None)

    def test_find_db_entry(self):
        """Tests the find_db_entry method on an entry that exists"""
        video = Youtube_Video(title="entry1", videoid="videoid1")
        entry = YoutubeVideoDB(title='entry1', videoid='videoid1')
        db.session.add(entry)
        db.session.commit()
        self.assertEqual(entry, video.find_db_entry())

    def test_find_bad_db_entry(self):
        """Tests the find_db_entry method on an entry that doesn't exist"""
        video = Youtube_Video(title="no_video", videoid="no_video")
        self.assertEqual(video.find_db_entry(), None)

    def test_from_db_entry(self):
        """Tests the from_db_entry method"""
        video1 = Youtube_Video()
        video2 = Youtube_Video(title="test4",
                               videoid="test4",
                               score=0.5,
                               caption="4")
        entry = YoutubeVideoDB(title="test4",
                               videoid="test4",
                               score=0.5,
                               caption="4")
        video1.from_db_entry(entry)
        self.assertEqual(video1.title, video2.title)
        self.assertEqual(video1.videoid, video2.videoid)
        self.assertEqual(video1.score, video2.score)
        self.assertEqual(video1.caption, video2.caption)

    def test_serialize(self):
        """Tests the serialize method"""
        video = Youtube_Video(title="test5",
                              videoid="v5",
                              score=-0.3,
                              caption="5")
        dict = {
            'videoid': "v5",
            'title': "test5",
            'score': -0.3,
        }
        self.assertEqual(video.serialize(), dict)


if __name__ == '__main__':
    unittest.main(verbosity=1)
