import http.server
import socketserver
from urllib.parse import urlparse
import clustering

def result_clustering(method):
    if method == 'kmeans':
        result = clustering.result_kmeans(bag)
    if method == 'mbk':
        result = clustering.result_mbk(bag)
    if method == 'agglo':
        result = clustering.result_agglomerat(bag)
    if method == 'all_methods':
        result = clustering.all_methods(bag)
    return result


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(200) # статус http-запроса (200 - OK)

            # Setting the header
            self.send_header("Content-type", "text/html; charset=utf-8")

            # Whenever using 'send_header', you also have to call 'end_headers'
            self.end_headers()

            # Extract query param
            query = urlparse(self.path).query # получение выбранного значения из элемента <select>
            #print(query)
            m = ""
            if query != '':
                query_components = dict(qc.split("=") for qc in query.split("&")) # формирование словаря {'method': 'kmeans'}
                m = query_components["method"]

            result = result_clustering(m)

            f = open('index.html', 'r', encoding="utf-8") # чтение html-файла
            html = f.read().format(name=result) # интерполяция конструкции {name:} в HTML-файле. создание новой строки с новыми данными
            f.close()

            # Writing the HTML contents with UTF-8
            self.wfile.write(bytes(html, "utf8"))

            return




bag = clustering.main()

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8001
my_server = socketserver.TCPServer(("", PORT), handler_object)
print("serving at port", PORT)
my_server.serve_forever()
