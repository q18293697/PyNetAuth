import time
import sys
import socket

from PySide2.QtWidgets import QWidget
from threading import Thread

from ui.wnd_client_main import Ui_WndClientMain
import mf


class WndClientMain(QWidget, Ui_WndClientMain):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_status_bar()
        self.init_net_auth()

    def init_status_bar(self):
        # info标签
        self.lbe_info = QLabel(self)
        self.statusbar.addWidget(self.lbe_info)

    def show_info(self, info):
        self.lbe_info.setText(f"<提示> : {info}")
        mf.log_info(info)

    def init_net_auth(self):
        self.error_count = 0
        Thread(target=self.thd_heart_beat, daemon=True).start()
        ...

    def thd_heart_beat(self):
        while True:
            time.sleep(600)  # 等待600秒(10分钟)
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            err_no = tcp_socket.connect_ex((mf.server_ip, mf.server_port))
            if err_no == 0:
                client_info_dict = {
                    "消息类型": "心跳",
                    "账号": mf.client_account,
                    "错误次数": error_count,
                }
                mf.send_to_server(tcp_socket, client_info_dict)
                self.recv_from_server(tcp_socket)
                tcp_socket.close()  # 发送接收完立刻断开
            else:
                self.error_count += 1
            if self.error_count > 5:
                self.show_info("网络连接已断开")
                sys.exit(-1)

    # 接收来自服务端的数据
    def recv_from_server(self, tcp_socket: socket.socket):
        try:  # 若等待服务端发出消息时, 客户端套接字关闭会异常
            recv_bytes = tcp_socket.recv(1024)
        except:
            recv_bytes = ""
        if not recv_bytes:  # 若客户端退出,会收到一个空str
            return
        json_str = recv_bytes.decode()
        # json字符串 转 py字典
        json_str = recv_bytes.decode()
        server_info_dict = json.loads(json_str)
        mf.log_info(f"收到服务端的消息: {server_info_dict}")
        msg_type = server_info_dict["消息类型"]
        if msg_type != "心跳":
            return
        detail = server_info_dict["详情"]
        if detail == "正常":
            self.error_count = 0
        elif detail == "下线":
            self.error_count = 10
        else:  # 其它异常情况
            self.error_count += 1


from PySide2.QtWidgets import QApplication, QStyleFactory
from PySide2.QtCore import Qt
import sys

if __name__ == '__main__':
    # 界面随DPI自动缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    app = QApplication()
    app.setStyle(QStyleFactory.create("fusion"))
    app.setStyleSheet(mf.qss_style)

    wnd_client_main = WndClientMain()
    wnd_client_main.show()

    sys.exit(app.exec_())