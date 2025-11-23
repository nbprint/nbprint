from IPython.display import HTML
from pydantic import Field

from nbprint import Content

__all__ = (
    "ExampleFinanceAuthor",
    "ExampleFinanceBulletPoints",
    "ExampleFinanceDisclosures",
    "ExampleFinanceFinancialTable",
    "ExampleFinanceFirstPageDisclosures",
    "ExampleFinanceKeyMetricsTable",
    "ExampleFinanceSectionHeading",
    "ExampleFinanceSectionText",
    "ExampleFinanceStockBody",
    "ExampleFinanceStockEarningsTable",
    "ExampleFinanceStockHeadline",
    "ExampleFinanceStockPTUpdate",
    "ExampleFinanceStockQuickStats",
    "ExampleFinanceStockSubHeadline",
    "ExampleFinanceStockWhatsChanged",
    "ExampleFinanceTitle",
    "ExampleFinanceValuationTable",
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


class ExampleFinanceSectionHeading(Content):
    title: str = ""
    color: str = "#5db39c"

    css: str = """
:scope {
  margin-top: 25px;
  margin-bottom: 15px;
  page-break-after: avoid;
}

h2 {
  font-size: 18px;
  font-weight: bold;
  margin: 0px !important;
  padding: 8px 0px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div style="border-left: 4px solid {self.color}; padding-left: 10px;">
            <h2>{self.title}</h2>
        </div>
        """)


class ExampleFinanceSectionText(Content):
    text: str = ""

    css: str = """
:scope p {
  font-size: 11px;
  line-height: 1.5;
  margin-bottom: 10px;
  text-align: justify;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"<p>{self.text}</p>")


class ExampleFinanceFinancialTable(Content):
    css: str = """
:scope {
  margin: 15px 0px;
  break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

table thead {
  background-color: #f5f5f5;
  font-weight: bold;
}

table thead tr th {
  padding: 8px 5px;
  text-align: right;
  border-bottom: 2px solid #333;
}

table thead tr th:first-child {
  text-align: left;
}

table tbody tr td {
  padding: 6px 5px;
  text-align: right;
  border-bottom: 1px solid #ddd;
}

table tbody tr td:first-child {
  text-align: left;
  font-weight: 500;
}

table tbody tr.total td {
  font-weight: bold;
  border-top: 2px solid #333;
  border-bottom: 2px solid #333;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
            <table>
                <thead>
                    <tr>
                        <th>Income Statement ($mm)</th>
                        <th>FY2023A</th>
                        <th>FY2024E</th>
                        <th>FY2025E</th>
                        <th>FY2026E</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Revenue</td>
                        <td>12,450</td>
                        <td>14,120</td>
                        <td>16,340</td>
                        <td>18,720</td>
                    </tr>
                    <tr>
                        <td>Cost of Revenue</td>
                        <td>(7,890)</td>
                        <td>(8,950)</td>
                        <td>(10,250)</td>
                        <td>(11,680)</td>
                    </tr>
                    <tr>
                        <td>Gross Profit</td>
                        <td>4,560</td>
                        <td>5,170</td>
                        <td>6,090</td>
                        <td>7,040</td>
                    </tr>
                    <tr>
                        <td>Operating Expenses</td>
                        <td>(3,240)</td>
                        <td>(3,650)</td>
                        <td>(4,180)</td>
                        <td>(4,730)</td>
                    </tr>
                    <tr>
                        <td>EBITDA</td>
                        <td>1,820</td>
                        <td>2,120</td>
                        <td>2,560</td>
                        <td>3,010</td>
                    </tr>
                    <tr>
                        <td>Depreciation & Amortization</td>
                        <td>(500)</td>
                        <td>(580)</td>
                        <td>(670)</td>
                        <td>(760)</td>
                    </tr>
                    <tr>
                        <td>EBIT</td>
                        <td>1,320</td>
                        <td>1,540</td>
                        <td>1,890</td>
                        <td>2,250</td>
                    </tr>
                    <tr>
                        <td>Interest Expense</td>
                        <td>(180)</td>
                        <td>(210)</td>
                        <td>(230)</td>
                        <td>(250)</td>
                    </tr>
                    <tr>
                        <td>Pre-Tax Income</td>
                        <td>1,140</td>
                        <td>1,330</td>
                        <td>1,660</td>
                        <td>2,000</td>
                    </tr>
                    <tr>
                        <td>Taxes</td>
                        <td>(285)</td>
                        <td>(333)</td>
                        <td>(415)</td>
                        <td>(500)</td>
                    </tr>
                    <tr class="total">
                        <td>Net Income</td>
                        <td>855</td>
                        <td>997</td>
                        <td>1,245</td>
                        <td>1,500</td>
                    </tr>
                </tbody>
            </table>
        """)


class ExampleFinanceValuationTable(Content):
    color: str = "#5db39c"

    css: str = """
:scope {
  margin: 15px 0px;
  break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

table thead {
  font-weight: bold;
}

table thead tr th {
  padding: 8px 5px;
  text-align: right;
  border-bottom: 2px solid #333;
}

table thead tr th:first-child {
  text-align: left;
}

table tbody tr td {
  padding: 6px 5px;
  text-align: right;
  border-bottom: 1px solid #ddd;
}

table tbody tr td:first-child {
  text-align: left;
}

table tbody tr.highlight td {
  font-weight: bold;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <table>
                <thead>
                    <tr>
                        <th>Valuation Methodology</th>
                        <th>Multiple</th>
                        <th>Value per Share</th>
                        <th>Weight</th>
                        <th>Weighted Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>P/E Multiple (FY25E)</td>
                        <td>12.5x</td>
                        <td>$11.25</td>
                        <td>40%</td>
                        <td>$4.50</td>
                    </tr>
                    <tr>
                        <td>EV/EBITDA Multiple (FY25E)</td>
                        <td>8.5x</td>
                        <td>$10.50</td>
                        <td>30%</td>
                        <td>$3.15</td>
                    </tr>
                    <tr>
                        <td>DCF Valuation</td>
                        <td>-</td>
                        <td>$9.00</td>
                        <td>30%</td>
                        <td>$2.70</td>
                    </tr>
                    <tr class="highlight" style="background-color: {self.color}15;">
                        <td><strong>Blended Target Price</strong></td>
                        <td>-</td>
                        <td>-</td>
                        <td>100%</td>
                        <td><strong>$10.35</strong></td>
                    </tr>
                </tbody>
            </table>
        """)


class ExampleFinanceKeyMetricsTable(Content):
    css: str = """
:scope {
  margin: 15px 0px;
  break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

table thead {
  background-color: #f5f5f5;
  font-weight: bold;
}

table thead tr th {
  padding: 8px 5px;
  text-align: right;
  border-bottom: 2px solid #333;
}

table thead tr th:first-child {
  text-align: left;
}

table tbody tr td {
  padding: 6px 5px;
  text-align: right;
  border-bottom: 1px solid #ddd;
}

table tbody tr td:first-child {
  text-align: left;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
            <table>
                <thead>
                    <tr>
                        <th>Key Operating Metrics</th>
                        <th>FY2023A</th>
                        <th>FY2024E</th>
                        <th>FY2025E</th>
                        <th>FY2026E</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Revenue Growth (YoY)</td>
                        <td>18.5%</td>
                        <td>13.4%</td>
                        <td>15.7%</td>
                        <td>14.6%</td>
                    </tr>
                    <tr>
                        <td>Gross Margin</td>
                        <td>36.6%</td>
                        <td>36.6%</td>
                        <td>37.3%</td>
                        <td>37.6%</td>
                    </tr>
                    <tr>
                        <td>EBITDA Margin</td>
                        <td>14.6%</td>
                        <td>15.0%</td>
                        <td>15.7%</td>
                        <td>16.1%</td>
                    </tr>
                    <tr>
                        <td>Operating Margin</td>
                        <td>10.6%</td>
                        <td>10.9%</td>
                        <td>11.6%</td>
                        <td>12.0%</td>
                    </tr>
                    <tr>
                        <td>Net Margin</td>
                        <td>6.9%</td>
                        <td>7.1%</td>
                        <td>7.6%</td>
                        <td>8.0%</td>
                    </tr>
                    <tr>
                        <td>ROE</td>
                        <td>15.2%</td>
                        <td>16.8%</td>
                        <td>18.9%</td>
                        <td>20.5%</td>
                    </tr>
                    <tr>
                        <td>ROIC</td>
                        <td>12.8%</td>
                        <td>14.1%</td>
                        <td>15.6%</td>
                        <td>17.0%</td>
                    </tr>
                </tbody>
            </table>
        """)


class ExampleFinanceBulletPoints(Content):
    items: list[str] = Field(default_factory=list)

    css: str = """
:scope ul {
  font-size: 11px;
  line-height: 1.6;
  margin: 10px 0px;
  padding-left: 20px;
}

:scope ul li {
  margin-bottom: 8px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        items_html = "".join([f"<li>{item}</li>" for item in self.items])
        return HTML(f"<ul>{items_html}</ul>")
