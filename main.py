# -*- coding: utf-8 -*-

import os
import json
import requests
import webbrowser
from configparser import ConfigParser
from wox import Wox, WoxAPI
from google_translate_api import GoogleTranslateAPI


def build_result(title, subTitle="", icoPath="translate.png", jsonRPCAction=None):
    d = dict(
        Title=title,
        SubTitle=subTitle,
        IcoPath=icoPath,
        JsonRPCAction=jsonRPCAction
    )
    return {k: v for k, v in d.items() if v is not None}


class Translator(Wox):
    def _load_config(self) -> dict:
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
            return json.loads(f.read())
        return dict()

    def _dump_config(self, config):
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as f:
            f.write(json.dumps(config))

    def _get_api(self):
        config = self._load_config()
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxy_url = "http://{}:{}".format(
                self.proxy.get("server"), self.proxy.get("port"))
        else:
            proxy_url = config.get("proxy", None)

        return GoogleTranslateAPI(config.get("key"), dict(http=proxy_url, https=proxy_url) if proxy_url is not None else None)

    def _get_supported_language(self):
        try:
            f = open("supported_languages", "r")
            data = f.read()
            return json.loads(data)
        except:
            target = self._load_config().get("lang")
            return self._update_supportted_languages_cache(target)

    def _update_supportted_languages_cache(self, lang):
        api = self._get_api()
        r = api.get_supported_language(lang)
        if r.status_code == 403:
            return dict(
                Title="Key Invalid",
                SubTitle="",
                IcoPath="translate.png",
            )
        with open("supported_languages", "w") as f:
            f.write(json.dumps(r.json()))
        return r.json()

    def openUrl(self, url):
        webbrowser.open(url)

    def set_default_lang(self, lang):
        config = self._load_config()
        config["lang"] = lang
        self._dump_config(config)
        self._update_supportted_languages_cache(lang)

    def translate(self, q, target, source=None):
        api = self._get_api()
        r = api.translate(q, target, source=source)
        if r.status_code == 403:
            return dict(
                Title="Key Invalid",
                SubTitle="",
                IcoPath="translate.png",
            )
        data = r.json()
        results = []
        if "data" in data and "translations" in data["data"]:
            for item in data["data"]["translations"]:
                results.append(
                    build_result(item["translatedText"], subTitle="Translate from {}".format(
                        item["detectedSourceLanguage"]))
                )
        else:
            results.append(build_result("Err"))
        return results

    def get_supported_language(self):
        data = self._get_supported_language()
        results = []
        if "data" in data and "languages" in data["data"]:
            for item in data["data"]["languages"]:
                results.append(
                    build_result(
                        item["name"] if "name" in item else item["language"],
                        subTitle=item["language"] if "name" in item else "",
                        jsonRPCAction=dict(method="set_default_lang", parameters=[
                                           item["language"]])
                    )
                )

        else:
            results.append(build_result("Err"))
        return results

    def query(self, query):
        results = []
        config = self._load_config()
        target = config.get("lang")
        if query is None or query is "":
            results.append(build_result(
                "Current dest language: {}".format(target)))
            return results

        results += \
            self.translate(query, target)
        return results

    def context_menu(self, data):
        results = []
        results.append(build_result("Select default destination language"))
        results += \
            self.get_supported_language()
        return results


if __name__ == "__main__":
    Translator()
