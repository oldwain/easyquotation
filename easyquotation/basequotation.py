import asyncio
# import json

import aiohttp
import datetime
import time
import stockcodes


class BaseQuotation:
    """行情获取基类"""
    max_num = 800  # 每次请求的最大股票数
    stock_api = ''  # 股票 api

    def __init__(self, rawformat = True):
        stock_codes = self.load_stock_codes()
        self.stock_list = self.gen_stock_list(stock_codes)
        self.rawformat = rawformat
    def gen_stock_list(self, stock_codes):
        stock_with_exchange_list = list(
                map(lambda stock_code: ('%s' if stock_code.startswith('s')
                                        else('sh%s' if stock_code.startswith(('5', '6', '9'))
                                        else 'sz%s')) % stock_code, stock_codes))

        stock_list = []
        request_num = len(stock_codes) // self.max_num + 1
        for range_start in range(request_num):
            num_start = self.max_num * range_start
            num_end = self.max_num * (range_start + 1)
            request_list = ','.join(stock_with_exchange_list[num_start:num_end])
            stock_list.append(request_list)
        return stock_list

    @staticmethod
    def load_stock_codes():
        return stockcodes.get_stock_codes()

    @property
    def all(self):
        return self.get_stock_data(self.stock_list)

    def stocks(self, stock_codes):
        if type(stock_codes) is not list:
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list)

    async def get_stocks_by_range(self, params):
        print(u"{}: api:{} get_stocks_by_range({})".format(datetime.datetime.now(), self.stock_api,params))
        for _ in range(10):
            try:
                with aiohttp.ClientSession() as session:
                    async with session.get(self.stock_api + params) as r:
                        response_text = await r.text()
                        return response_text
            except aiohttp.errors.ClientOSError as err:
                print(u"{} {}".format(datetime.datetime.now(), err))
                time.sleep(10)

    def get_stock_data(self, stock_list):
        coroutines = []
        for params in stock_list:
            coroutine = self.get_stocks_by_range(params)
            coroutines.append(coroutine)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        res = loop.run_until_complete(asyncio.gather(*coroutines))

        return self.format_response_data(res)

    def format_response_data(self, rep_data):
        pass
