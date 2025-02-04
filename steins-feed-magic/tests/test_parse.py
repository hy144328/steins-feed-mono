import steins_feed_magic.parse

def test_text_content():
    res = steins_feed_magic.parse.text_content("""Hello.
<p>
This is a test.
</p>
World!""")

    assert res == """Hello.

This is a test.

World!"""
