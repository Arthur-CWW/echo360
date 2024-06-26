from functools import cached_property
import json
import re
import sys
from typing import Optional

import requests
import selenium
import logging

from .videos import EchoVideos, EchoCloudVideos
import selenium.common.exceptions
import selenium.webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

_LOGGER = logging.getLogger(__name__)


class EchoCourse:
    driver:WebDriver
    def __init__(self, uuid, hostname=None, alternative_feeds=False):
        self._course_id:Optional[str] = None
        self._course_name:Optional[str] = None
        self.uuid:str = uuid
        self._videos:Optional[EchoVideos] = None
        self._alternative_feeds = alternative_feeds
        if hostname is None:
            self.hostname = "https://view.streaming.sydney.edu.au:8443"
        else:
            self.hostname = hostname

    @cached_property
    def videos(self):
        # if self.driver is None:
        assert self.driver is not None, "webdriver not set yet!!!"
        if not self._videos:
            try:
                course_data_json = self._get_course_data()
                videos_json = course_data_json["section"]["presentations"][
                    "pageContents"
                ]
                self._videos = EchoVideos(videos_json, self.driver)
            except KeyError as e:
                self._blow_up(
                    "Unable to parse course videos from JSON (course_data)", e
                )
            except selenium.common.exceptions.NoSuchElementException as e:
                self._blow_up("selenium cannot find given elements", e)
        assert self._videos is not None, "videos is not set"
        return self._videos


    @property
    def url(self):
        return f"{self.hostname}/ess/portal/section/{self.uuid}"

    @property
    def video_url(self):
        return f"{self.hostname}/ess/client/api/sections/{self.uuid}/section-data.json?pageSize=100"


    @property
    def course_id(self):
        if self._course_id is None:
            try:
                self.driver.get(
                    self.url
                )  # Initialize to establish the 'anon' cookie that Echo360 sends.
                self.driver.get(self.video_url)
                course_data_json = self._get_course_data()

                self._course_id = course_data_json["section"]["course"]["identifier"]
                self._course_name = course_data_json["section"]["course"]["name"]
            except KeyError as e:
                self._blow_up(
                    "Unable to parse course id (e.g. CS473) from JSON (course_data)", e
                )

        assert self._course_id is not None, "course_id could not be set"
        return self._course_id

    @property
    def course_name(self):
        if self._course_name is None:
            self.course_id
        return self._course_name

    @property
    def nice_name(self):
        return f"{self.course_id} - {self.course_name}"

    def _get_course_data(self):
        try:
            self.driver.get(self.video_url)
            _LOGGER.debug(
                "Dumping course page at %s: %s",
                self.video_url,
                self.driver.page_source,
            )
            json_str = self.driver.find_element(By.TAG_NAME, "pre").text
        except ValueError as e:
            raise Exception("Unable to retrieve JSON (course_data) from url", e)
        self.course_data = json.loads(json_str)
        return self.course_data

    def set_driver(self, driver):
        self.driver = driver

    def _blow_up(self, msg, e):
        print(msg)
        print(f"Exception: {str(e)}")
        sys.exit(1)


class EchoCloudCourse(EchoCourse):
    def __init__(self, *args, **kwargs):
        super(EchoCloudCourse, self).__init__(*args, **kwargs)

    @cached_property
    def videos(self):
        if self.driver is None:
            raise Exception("webdriver not set yet!!!", "")
        if not self._videos:
            try:
                course_data_json = self._get_course_data()
                videos_json = course_data_json["data"]
                self._videos = EchoCloudVideos(
                    videos_json, self.driver, self.hostname, self._alternative_feeds
                )
            except KeyError as e:
                assert False, "Unable to parse course videos from JSON (course_data)"
            except selenium.common.exceptions.NoSuchElementException as e:
                print("selenium cannot find given elements")
                raise e

        return self._videos

    @property
    def video_url(self):
        return f"{self.hostname}/section/{self.uuid}/syllabus"

    @property
    def course_id(self):
        if self._course_id is None:
            # self.course_data['data'][0]['lesson']['lesson']['displayName']
            # should be in the format of XXXXX (ABCD1001 - 2020 - Semester 1) ???
            # canidate = self.course_data['data'][0]['lesson']['video']['published']['courseName']
            # print(self._course_name)
            # self._course_name = canidate
            # Too much variant, it's too hard to have a unique way to extract course id.
            # we will simply use course name and ignore any course id.
            self._course_id = ""
            # result = re.search('^[^(]+', canidate)
            # if result is not None:
            #     self._course_name = result.group()
            #     result = re.search('[(].+[)]', canidate)
            #     self._course_id = result.group()[1:-1]
        return self._course_id

    @property
    def course_name(self):
        if self._course_name is None:
            # try each available video as some video might be special has contains
            # no information about the course.
            for v in self.course_data["data"]:
                try:
                    self._course_name = v["lesson"]["video"]["published"]["courseName"]
                    break
                except KeyError:
                    pass
            if self._course_name is None:
                # no available course name found...?
                self._course_name = "[[UNTITLED]]"
        return self._course_name

    @property
    def nice_name(self):
        return self.course_name

    def _get_course_data(self):
        try:
            self.driver.get(self.video_url)
            _LOGGER.debug(
                "Dumping course page at %s: %s",
                self.video_url,
                self.driver.page_source,
            )
            # use requests to retrieve data
            session = requests.Session()
            # load cookies
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie["name"], cookie["value"])

            r = session.get(self.video_url)
            if not r.ok:
                raise Exception("Error: Failed to get m3u8 info for EchoCourse!")

            json_str = r.text
        except ValueError as e:
            raise Exception("Unable to retrieve JSON (course_data) from url", e)
        self.course_data = json.loads(json_str)
        return self.course_data
