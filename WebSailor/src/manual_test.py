"""Manual test for sahibinden.com search.

Bu betik, `tool_search.Search` aracını kullanarak sahibinden.com'da
"2018 model kırmızı Fiat Egea" araması yapar ve ilk 5 sonucu yazdırır.
"""

from tool_search import Search


if __name__ == "__main__":
    tool = Search()
    params = {"query": "2018 model kırmızı Fiat Egea"}
    result = tool.call(params)
    print(result)

