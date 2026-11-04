import pytest


@pytest.fixture
def product_factory():
    def make(
        code="IIU",
        version="1.2.3",
        build="123.456.789",
        channel="release",
        platforms=("mac",),
        url="https://download.jetbrains.com/idea/example.dmg",
    ):
        return {
            "code": code,
            "name": f"Example {code}",
            "categories": ["IDE"],
            "releases": [
                {
                    "version": version,
                    "build": build,
                    "type": channel,
                    "date": "2026-11-03",
                    "downloads": {
                        platform: {"link": url, "checksumLink": url + ".sha256", "size": 20}
                        for platform in platforms
                    },
                }
            ],
        }

    return make
