import os
import os.path
import time

import pandas as pd
from IPython.display import HTML

from . import nbconvert_context
from .image import image

try:
    from tempfile import TemporaryDirectory
except BaseException:
    from backports.tempfile import TemporaryDirectory


with open(os.path.join(os.path.dirname(__file__), "resources", "jupyter_style.css"), "r") as fp:
    _JUPYTERLAB_STYLE = "<style>{}</style>".format(fp.read())


def _setup_screenshot(driver, path):
    """Grab screenshot of browser rendered HTML.
    Ensure the browser is sized to display all the HTML content."""
    # Ref: https://stackoverflow.com/a/52572919/
    driver.set_window_size(3000, 800)
    # required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    # required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    # driver.set_window_size(required_width, required_height)
    driver.save_screenshot(path)  # has scrollbar
    driver.find_element_by_tag_name("table").screenshot(path)  # avoids scrollbar
    # driver.find_element_by_tag_name('table').screenshot(path)  # avoids scrollbar
    # driver.set_window_size(original_size['width'], original_size['height'])


def _getTableImage(url, filename="dummy_table", path=".", delay=3, height=420, width=800):
    """Render HTML file in browser and grab a screenshot."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--hide-scrollbars")

    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    # Give the html some time to load
    time.sleep(delay)
    imgpath = "{}/{}.png".format(path, filename)
    _setup_screenshot(browser, imgpath)
    browser.quit()
    os.remove(imgpath.replace(".png", ".html"))
    return imgpath


def table_to_png(df_or_series_or_styler, **kwargs):
    if isinstance(df_or_series_or_styler, pd.DataFrame):
        tablehtml = df_or_series_or_styler.to_html()
    elif isinstance(df_or_series_or_styler, pd.Series):
        tablehtml = df_or_series_or_styler.to_html()
    else:
        tablehtml = df_or_series_or_styler.render()

    if nbconvert_context() == "pdf":
        with TemporaryDirectory() as dir:
            file_full_path = "{}/{}.html".format(dir, "temp")
            tmpurl = "file://{}".format(file_full_path)

            doc = '<html><head>{}</head><body><div class="jp-RenderedHTMLCommon">{}</div>'.format(
                _JUPYTERLAB_STYLE, tablehtml
            )
            with open(file_full_path, "w") as out:
                out.write(doc)
            with open(_getTableImage(tmpurl, "temp", dir), "rb") as fp:
                return image(fp.read())
    else:
        # defer to native rendering
        return HTML(tablehtml)
