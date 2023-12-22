import socket
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
subd_address = ('37.193.53.6', 31543)

token = "7HbN3P#m9e6@kT2d123dNEar"
token_admin = "R#f7GhT9@Lp2$y5BqZx!0*D"

class Get_data:
    def __init__(self, city):
        self.city = city
    def get_data_Pharmacy(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(subd_address)
                s.sendall(f"{token} --file Pharmacies_{self.city}.json --query 'GSON get'".encode())
                print("Message sent successfully.")
                datas_subd = s.recv(61440)
                data_sub = datas_subd.decode()
                print(data_sub)
                return data_sub
            except ConnectionRefusedError:
                print("Connection to the server failed.")


    def get_data_Medicine(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(subd_address)
                s.sendall(f"{token} --file Medicine_{self.city}.json --query 'GSON get'".encode())
                print("Message sent successfully.")
                datas_subd = s.recv(61440)
                data_sub = datas_subd.decode()
                print(data_sub)
                return data_sub
            except ConnectionRefusedError:
                print("Connection to the server failed.")

    def send_updated_drug_data(self, data):


        print("Data for send to SUBD: ", data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(subd_address)
                s.sendall(f"{token_admin} --file Medicine_{self.city}.json --query 'GSON save {data}'".encode())
                print("Message sent successfully.")
                datas_subd = s.recv(61440)
                data_sub = datas_subd.decode()
                print(data_sub)
            except ConnectionRefusedError:
                print("Connection to the server failed.")

    def send_updated_pharmacy_data(self, data):
        print("Data for send to SUBD: ", data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(subd_address)
                s.sendall(f"{token_admin} --file Pharmacies_{self.city}.json --query 'GSON save {data}'".encode())
                print("Message sent successfully.")
                datas_subd = s.recv(61440)
                data_sub = datas_subd.decode()
                print(data_sub)
            except ConnectionRefusedError:
                print("Connection to the server failed.")

    def get_password(self, login):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(subd_address)
                s.sendall(f"{token} --file passwords.data --query 'HGET Apteka_passwords {login}'".encode())
                print("Message sent successfully.")
                datas_subd = s.recv(61440)
                data_sub = datas_subd.decode()
                print(data_sub)
                return data_sub
            except ConnectionRefusedError:
                print("Connection to the server failed.")





