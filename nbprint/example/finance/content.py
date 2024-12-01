from IPython.display import HTML

from nbprint import Content

__all__ = (
    "ExampleFinanceAuthor",
    "ExampleFinanceDisclosures",
    "ExampleFinanceFirstPageDisclosures",
    "ExampleFinanceStockBody",
    "ExampleFinanceStockEarningsTable",
    "ExampleFinanceStockHeadline",
    "ExampleFinanceStockPTUpdate",
    "ExampleFinanceStockQuickStats",
    "ExampleFinanceStockSubHeadline",
    "ExampleFinanceStockWhatsChanged",
    "ExampleFinanceTitle",
)


class ExampleFinanceTitle(Content):
    title: str = ""
    subtitle: str = ""
    date: str = ""
    css: str = """

h1 {
  font-family: sans-serif;
  font-size: 25px !important;
  padding-right: 15px;
  border-right: 2px solid black;
}

h2 {
  font-family: sans-serif;
  text-transform: uppercase;
  font-weight: bold !important;
  font-size: 12px !important;
  padding-left: 15px;
}

span {
  color: grey;
  font-size: 15px !important;
  font-style: italic;
  padding-top: 10px;
  padding-bottom: 10px;
}
    """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="row">
            <h1>{self.title}</h1>
            <h2>{self.subtitle}</h2>
        </div>
        <div class="row">
            <span>{self.date}</span>
        </div>
        """)


class ExampleFinanceStockHeadline(Content):
    company_name: str = ""
    region: str = ""
    byline: str = ""
    color: str = ""
    css: str = """
div.row {
  padding-bottom: 10px;
  margin-top: 12px !important;
  margin-bottom: 12px !important;
}

h2:nth-child(1) {
  padding-right: 15px;

}

h2:nth-child(2) {
  padding-left: 15px;
}

h1 {
  font-weight: lighter !important;
  margin-bottom: 12px !important;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="row">
            <h2 style="color: {self.color}; border-right: 2px solid {self.color}">{self.company_name}</h2>
            <h2 style="color: {self.color};">{self.region}</h2>
        </div>
        <h1>{self.byline}</h1>
        """)


class ExampleFinanceAuthor(Content):
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    css: str = """

div.column > span:nth-child(1) {
  font-size: 12px;
  font-weight: bold;
}

div.column > span:nth-child(2) {
  font-size: 10px;
  text-transform: uppercase;
}

div.row {
  justify-content: space-between;
}

div.row > span:nth-child(1) {
  font-size: 10px;
}

div.row > span:nth-child(2) {
  font-family: monospace;
  font-size: 10px;
}

    """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="column">
                <span>{self.name}</span>
                <span>{self.title}</span>
                <div class="row">
                    <span>{self.email}</span>
                    <span>{self.phone}</span>
                </div>
            </div>
        """)


class ExampleFinanceStockQuickStats(Content):
    ticker: str = ""
    company_name: str = ""
    color: str = ""

    sector: str = ""
    country: str = ""
    region: str = ""

    rating: str
    view: str
    price_target: float

    share_price: float
    market_cap: str
    range_min: float
    range_max: float

    css: str = """
div.row {
  justify-content: space-between;
  font-size: 10px;
}

div.column > div.column > div.row:nth-child(1),
div.column > div.column > div.row:nth-child(2),
div.column > div.column > div.row:nth-child(3) {
  font-weight: bold;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="column pt20">
                <div style="padding-left: 5px; background-color: {self.color}; color: white;">
                    <span>{self.company_name} ( {self.ticker} )</span>
                </div>
                <div class="row" style="font-size: 9px; justify-content: unset;">
                    <span>{self.sector}</span>
                    <span>&nbsp;/&nbsp;</span>
                    <span style="font-weight: bold;">{self.country}</span>
                </div>
                <div class="column">
                    <div class="row">
                        <span>Stock Rating</span>
                        <span>{self.rating}</span>
                    </div>
                    <div class="row">
                        <span>Industry View</span>
                        <span>{self.view}</span>
                    </div>
                    <div class="row">
                        <span>Price target</span>
                        <span>${self.price_target:.2f}</span>
                    </div>
                    <div class="row">
                        <span>Share Price</span>
                        <span>${self.share_price:.0f}</span>
                    </div>
                    <div class="row">
                        <span>Market Cap (mm)</span>
                        <span>${self.market_cap}</span>
                    </div>
                    <div class="row">
                        <span>52-Week Range</span>
                        <span>${self.range_min:.2f} - {self.range_max:.2f}</span>
                    </div>
                </div>
            </div>
        """)


class ExampleFinanceStockEarningsTable(Content):
    ticker: str = ""
    company_name: str = ""

    css: str = """
:scope {
  margin: 0px !important;
  padding: 0px !important;
  break-before: avoid;
}

table {
  font-size: 10px !important;
}
table thead tr {
  font-weight: bold;
}
table tbody tr td:nth-child(1){
  font-weight: bold;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
            <table>
                <thead>
                    <tr>
                        <td>Fiscal Year Ending</td>
                        <td>3/24</td>
                        <td>3/25e</td>
                        <td>3/26e</td>
                        <td>3/27e</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>EPS ($)</td>
                        <td>(0.32)</td>
                        <td>(0.14)</td>
                        <td>0.11</td>
                        <td>0.31</td>
                    </tr>
                    <tr>
                        <td>Prior EPS ($)</td>
                        <td>(0.23)</td>
                        <td>(0.15)</td>
                        <td>0.03</td>
                        <td>0.13</td>
                    </tr>
                    <tr>
                        <td>P/E</td>
                        <td>NM</td>
                        <td>NM</td>
                        <td>NM</td>
                        <td>NM</td>
                    </tr>
                </tbody>
            </table>
        """)


class ExampleFinanceStockPTUpdate(Content):
    ticker: str = ""
    rating: str
    view: str
    price_target: float

    css: str = """
:scope div.row {
  margin-top: 15px;
  margin-bottom: 15px;
  justify-content: space-between;
}

div.row > div:nth-child(2),
div.row > div:nth-child(3) {
  padding-left: 20px;
  border-left: 1px solid black;
}

div.row > div > span:nth-child(1) {
  font-size: 10px;
}

div.row > div > span:nth-child(2) {
  font-weight: lighter !important;
  font-size: 17px;
  padding-left: 5px;
}

div.row div:nth-child(1) span:nth-child(1)::before {
  font-family: "Font Awesome 6 Free";
  font-weight: 900;
  content: '\\f201';
  display: none;
  width: 20px;
}

div.row div:nth-child(2) span:nth-child(1)::before {
  font-family: "Font Awesome 6 Free";
  content: '\\f06e';
  display: none;
}

div.row div:nth-child(3) span:nth-child(1)::before {
  font-family: "Font Awesome 6 Free";
  content: '\\f192';
  display: none;
}

svg {
  width: 15px;
  margin-right: 3px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="row">
            <div class="column">
                <span class="stock-rating">Stock Rating</span>
                <span>{self.rating}</span>
            </div>
            <div class="column">
                <span>Industry View</span>
                <span>{self.view}</span>
            </div>
            <div class="column">
                <span>Price Target</span>
                <span>${self.price_target:.2f}</span>
            </div>
        </div>
        """)


class ExampleFinanceStockSubHeadline(Content):
    text: str = ""

    css: str = """
:scope span {
  font-size: 20px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <span>{self.text}</span>
        """)


class ExampleFinanceStockWhatsChanged(Content):
    ticker: str = ""
    company_name: str = ""
    color: str = ""
    price_target: float
    price_target_old: float

    css: str = """
:scope {
  margin-top: 10px;
  margin-bottom: 10px;
}

:scope span {
  font-size: 15px;
}

div.row {
  justify-content: space-between;
}

table {
  flex: 1;
  margin-left: 7px !important;
}

thead {
  border-bottom: 1px solid black;
  font-weight: bold;
}

td {
  text-align: left !important;
  padding: 0px !important;
}

div.whatschangedbox {
  text-transform: uppercase;
  font-weight: 100;
  padding: 2px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
          <div class="row">
            <div class="column whatschangedbox" style="padding: 5px; background-color: {self.color}; color: white;">
              <span>What's</span>
              <span>Changed</span>
            </div>
            <table>
              <thead>
                <tr>
                  <td>{self.company_name}</td>
                  <td>From</td>
                  <td>To</td>
                </tr>
                <tr>
                  <td>({self.ticker})</td>
                  <td></td>
                  <td></td>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Price Target</td>
                  <td>{self.price_target_old:.2f}</td>
                  <td style="font-weight: bold;">{self.price_target:.2f}</td>
                </tr>
              </tbody>
            </table>
          </div>
        """)


class ExampleFinanceStockBody(Content):
    our_take: str = ""
    review: str = ""
    outlook: str = ""

    css: str = """
p {
  margin: auto !important;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="column">
          <span><b>Our take</b>: {self.our_take}</span>
          <span><b>Quarter in review</b>: {self.review}</span>
          <span><b>Outlook</b>: {self.outlook}</span>
        </div>
        """)


class ExampleFinanceFirstPageDisclosures(Content):
    css: str = """

:scope {
  /* margin-top: 350px; */
  line-height: 1 !important;
}

span {
  font-size: 8px;
}

span:nth-child(2) {
  font-weight: bold;
}

"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
  <div class="column">
    <span>Jefferies Morgan does and seeks to do business with companies covered in Jefferies Morgan Research. As a result, investors should be aware that the firm may have a conflict of interest that could affect the objectivity of Jefferies Morgan Research. Investors should consider Jefferies Morgan Research as only a single factor in making their investment decision.</span>
    <span>For analyst certification and other important disclosures, refer to the Disclosure Section, located at the end of this report.</span>
  </div>
        """)


class ExampleFinanceDisclosures(Content):
    css: str = """
:scope h1 {
  font-size: 12px;
}

:scope p {
  font-size: 8px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
                <h1>Important Disclosures</hw1>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</p>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</p>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</p>
        """)
