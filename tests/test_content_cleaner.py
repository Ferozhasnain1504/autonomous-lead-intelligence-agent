from src.content_cleaner import ContentCleaner


def test_removes_irrelevant_html_elements():
    html = """
    <html>
        <body>

            <nav>
                Home About Pricing
            </nav>

            <main>
                <h1>Example Company</h1>

                <p>
                    We build software for developers.
                </p>

                <script>
                    console.log("this should disappear");
                </script>

                <style>
                    body {
                        color: red;
                    }
                </style>

                <svg>
                    <circle />
                </svg>

            </main>

            <footer>
                Copyright 2026
            </footer>

        </body>
    </html>
    """

    cleaner = ContentCleaner()

    result = cleaner.clean(html)

    assert "Example Company" in result
    assert "We build software for developers." in result

    assert "console.log" not in result
    assert "color: red" not in result
    assert "Copyright 2026" not in result
    assert "Home About Pricing" not in result


def test_normalizes_whitespace():
    html = """
    <main>
        <h1>Example Company</h1>

        <p>
            We    build    software
            for developers.
        </p>
    </main>
    """

    cleaner = ContentCleaner()

    result = cleaner.clean(html)

    assert result == (
        "Example Company\n"
        "We build software for developers."
    )


def test_empty_html_returns_empty_string():
    cleaner = ContentCleaner()

    assert cleaner.clean("") == ""