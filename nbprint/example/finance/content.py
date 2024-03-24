from IPython.display import HTML

from nbprint import Content


class ExampleFinanceTitleContent(Content):
    title: str = ""
    subtitle: str = ""
    date: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="nbprint-example-finance-title">
        <div class="row">
            <h1 class="nbprint-example-finance-title-title">{self.title}</h1>
            <span class="nbprint-example-finance-title-subtitle">{self.subtitle}</span>
        </div>
        <div class="row">
            <span class="nbprint-example-finance-title-date">{self.date}</span>
        </div>
        </div>
        """)


class ExampleFinanceStockHeadlineContent(Content):
    company_name: str = ""
    region: str = ""
    byline: str = ""
    color: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="nbprint-example-finance-heading">
            <div class="row">
                <h2 class="nbprint-example-finance-heading-companyname" style="color: {self.color}; border-right: 2px solid {self.color}">{self.company_name}</h2>
                <h2 class="nbprint-example-finance-heading-region" style="color: {self.color};">{self.region}</h2>
            </div>
            <h1 class="nbprint-example-finance-heading-byline">{self.byline}</h1>
        </div>
        """)


class ExampleFinanceReportAuthor(Content):
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="nbprint-example-finance-author column">
                <span class="nbprint-example-finance-author-name">{self.name}</span>
                <span class="nbprint-example-finance-author-title">{self.title}</span>
                <div class="nbprint-example-finance-author-contact row">
                    <span class="nbprint-example-finance-author-email">{self.email}</span>
                    <span class="nbprint-example-finance-author-phone">{self.phone}</span>
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

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="nbprint-example-finance-stock-quickstats column pt20">
                <div class="nbprint-example-finance-stock-quickstats-titlebar" style="background-color: {self.color}; color: white;">
                    <span>{self.company_name} ( {self.ticker} )</span>
                </div>
                <div class="row">
                    <span>{self.sector}</span>
                    <span>&nbsp;/&nbsp;</span>
                    <span style="font-weight: bold;">{self.country}</span>
                </div>
                <div class="nbprint-example-finance-stock-quickstats-stats column">
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

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("""
            <div class="nbprint-example-finance-stock-earnings pt10">
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
            </div>
        """)


class ExampleFinanceStockPTUpdate(Content):
    ticker: str = ""
    rating: str
    view: str
    price_target: float

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="row nbprint-example-finance-stock-ptupdate">
                <div class="column">
                    <span class="nbprint-example-finance-stock-ptupdate-stockrating">Stock Rating</span>
                    <span>{self.rating}</span>
                </div>
                <div class="column">
                    <span class="nbprint-example-finance-stock-ptupdate-industryview">Industry View</span>
                    <span>{self.view}</span>
                </div>
                <div class="column">
                    <span class="nbprint-example-finance-stock-ptupdate-pricetarget">Price Target</span>
                    <span>${self.price_target:.2f}</span>
                </div>
            </div>
        """)


class ExampleFinanceStockHeadline(Content):
    text: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <div class="nbprint-example-finance-stock-headline">
                <span>{self.text}
            </div>
        """)
