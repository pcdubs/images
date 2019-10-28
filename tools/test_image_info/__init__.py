import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request


TEST_DIR = os.path.dirname(__file__)


def json_files(path):
    """Reads .json files in path and yields (name, blob) for each of them."""
    for entry in os.scandir(path):
        name, ext = os.path.splitext(entry.name)
        if ext == ".json":
            with open(entry.path) as f:
                data = json.load(f)
            yield name, data


class TestImageInfo(unittest.TestCase):
    """Tests for image-info

    All tests share the same osbuild store to make running them more efficient.
    That's ok, because we're not testing osbuild itself.
    """

    @classmethod
    def setUpClass(cls):
        cls.store = tempfile.mkdtemp(dir="/var/tmp", prefix="osbuild-composer-test-")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.store)

    def run_osbuild(self, pipeline, input=None):
            osbuild_cmd = ["python3", "-m", "osbuild", "--json", "--libdir", ".", "--store", self.store, pipeline]

            build_pipeline = os.getenv("OSBUILD_TEST_BUILD_PIPELINE", None)
            if build_pipeline:
                osbuild_cmd.append("--build-pipeline")
                osbuild_cmd.append(os.path.abspath(build_pipeline))

            try:
                result = json.loads(subprocess.check_output(osbuild_cmd, cwd="./osbuild", encoding="utf-8", input=input))
            except subprocess.CalledProcessError as err:
                print(err.output, file=sys.stderr)

            return result["tree_id"], result["output_id"]

    def run_image_info(self, image):
        return json.loads(subprocess.check_output(["tools/image-info", image]))

    @unittest.skip("run too long")
    def test_pipelines(self):
        """Run image-info against an image generated by an osbuild pipepline

        The test case should have these keys:
            "pipeline": the pipeline to run, which should have an assembler
                        with a "filename" option
            "expected": the expected output from image-info
        """
        for name, case in json_files(f"{TEST_DIR}/pipelines"):
            if "expected" not in case:
                continue
            with self.subTest(name):
                _, output_id = self.run_osbuild("-", input=json.dumps(case["pipeline"]))
                filename = os.path.join(self.store, "refs", output_id, case["pipeline"]["assembler"]["options"]["filename"])
                info = self.run_image_info(filename)
                self.assertEqual(info, case["expected"])

    def test_images(self):
        """Run image-info against an image from the web

        The test case should have these keys:
                 "url": the url at which to find the image
            "expected": the expected output from image-info
        """
        for name, case in json_files(f"{TEST_DIR}/images"):
            with self.subTest(name):
                try:
                    filename, _ = urllib.request.urlretrieve(case["url"])
                    info = self.run_image_info(filename)
                    self.assertEqual(info, case["expected"])
                finally:
                    urllib.request.urlcleanup()
