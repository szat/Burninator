# This Python script is provided under the MIT License. Please refer to the LICENSE file
# or visit https://opensource.org/licenses/MIT for the full text of the license.

# Author: Adrian Szatmari
# Date: October 2023


import unittest
from helpers import *


# Example usage
class TestHelpersFunctions(unittest.TestCase):
    def setUp(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        video_filename = "SiliconValleyBigHeadFiredFromHooli.mp4"  # Replace with the actual filename
        video_filename_burned = "SiliconValleyBigHeadFiredFromHooli_burned.mp4"
        video_path = os.path.join(script_dir, video_filename)
        video_path_burned = os.path.join(script_dir, video_filename_burned)

        self.original_vid_path = video_path
        self.burned_vid_path = video_path_burned
        self.directory, filename_with_extension = os.path.split(self.original_vid_path)
        self.stats_original = get_video_stats(self.original_vid_path, options='ffmpeg')
        self.stats_burned = get_video_stats(self.burned_vid_path, options='ffmpeg')

    def test_get_frame_info_ocr(self):
        delta = self.stats_burned['time_between_frames']
        for i in range(100):
            frame = extract_frame(self.burned_vid_path, i)
            nb, seconds = get_frame_info_ocr(frame)
            np.testing.assert_allclose(seconds, delta * i, atol=0.0001)
            assert nb == i
            print(i)

    def test_extract_frame(self):
        frame_start = extract_frame(self.burned_vid_path, 0)
        nb, seconds = get_frame_info_ocr(frame_start)
        np.testing.assert_allclose(seconds, 0, atol=0.0001)
        assert nb == 0

        frame_end = extract_frame(self.burned_vid_path, self.stats_burned['frames'] - 1)
        nb, seconds = get_frame_info_ocr(frame_end)
        np.testing.assert_allclose(seconds,
                                   self.stats_burned['duration_seconds'] - self.stats_burned['time_between_frames'],
                                   atol=0.0001)
        assert nb == self.stats_burned['frames'] - 1

        frame_none = extract_frame(self.burned_vid_path, self.stats_burned['frames'])
        assert frame_none is None

    def test_burn_frame_info(self):
        assert self.stats_original['length'] == self.stats_burned['length']
        assert self.stats_original['frames'] == self.stats_burned['frames']
        np.testing.assert_allclose(self.stats_original['duration_seconds'], self.stats_burned['duration_seconds'],
                                   atol=0.0001)
        np.testing.assert_allclose(self.stats_original['fps'], self.stats_burned['fps'], atol=0.001)
        np.testing.assert_allclose(self.stats_original['time_between_frames'], self.stats_burned['time_between_frames'],
                                   atol=0.0001)
        assert self.stats_original['codec'] == 'h264'
        assert self.stats_burned['codec'] == 'mpeg4'

        f = extract_frame(self.burned_vid_path, 0)
        nb, seconds = get_frame_info_ocr(f)
        assert nb == 0
        assert seconds == 0.0

        f = extract_frame(self.burned_vid_path, self.stats_burned['frames'] - 1)
        nb, seconds = get_frame_info_ocr(f)
        assert nb == self.stats_burned['frames'] - 1
        np.testing.assert_allclose(seconds,
                                   self.stats_burned['duration_seconds'] - self.stats_burned['time_between_frames'],
                                   atol=0.0001)


if __name__ == '__main__':
    unittest.main()
