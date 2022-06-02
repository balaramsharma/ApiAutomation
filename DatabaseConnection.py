from enum import Enum
import pyotp
from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, String,
    Boolean, Enum, ForeignKey, func,
    Float, TEXT, UniqueConstraint, create_engine
)
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from sshtunnel import SSHTunnelForwarder
import pymysql
import paramiko
from paramiko import SSHClient
# from dal.model import Base

# class BUY_ACC_STATUS(Enum):
#     Deleted = 0
#     Active = 1
#     Disabled = 99
#
#
# class PAYMENT_METHOD(Enum):
#     GIFT_CARD = 1
#     CREDIT_CARD = 2
#
#
# class PAYMENT_SOURCE(Enum):
#     Privacy = 1
#     Visa = 2
#     MasterCard = 3
#     Emburse = 4
#     Divvy = 5
#     Bento = 6
#
#
# class SITES(Enum):
#     Amazon = 1
#     Ebay = 2
#     Ebay_UK = 3
#     Amazon_UK = 4
#     Amazon_DE = 5
#     Amazon_FR = 6
#     Amazon_ES = 7
#     Amazon_IT = 8
#     Ebay_DE = 9
#     Ebay_FR = 10
#     Ebay_CA = 11
#     Ebay_IT = 12
#     Ebay_ES = 13
#     Walmart = 14
#     Banggood = 15
#     Aliexpress = 16
#     Ebay_Motors = 17
#     AutoBooster = 18
#     HomeDepot = 19
#     Aliexpress_UK = 20
#     Aliexpress_DE = 21
#     Aliexpress_FR = 22
#     Aliexpress_IT = 23
#     WayFair_US = 24
#     WayFair_UK = 25
#     Costco_US = 26
#     Overstock = 27
#     Costway = 28
#     Costway_UK = 29
#     Costway_DE = 30
#     Costway_FR = 31
#     Costway_IT = 32
#     ChinaBrands_US = 33
#     ChinaBrands_UK = 34
#     ChinaBrands_DE = 35
#     ChinaBrands_FR = 36
#     ChinaBrands_IT = 37
#     Etsy = 38
#     Lowes = 39
#     Target = 40
#     CjDropshipping = 41
#     Vidaxl = 42
#     GearBest = 43
#     Samsclub = 44
#     Miniinthebox = 45
#     Lightinthebox = 46
#     Alibaba = 47
#     Pureformulas = 48
#     Redbubble = 49
#     Wish = 50
#     Amazon_AU = 51
#     Amazon_CA = 52
#     Costco_UK = 53
#     WayFair_CA = 54
#     Costway_CA = 55
#     Ebay_AU = 56
#
#
# class BuyAccount(Base):
#     __tablename__ = 'buy_account'
#     id = Column(Integer, primary_key=True)
#     email = Column(String(100))
#
#     buy_site_id = Column(Enum(SITES))
#     supplier = Column(Integer, nullable=True)
#     region = Column(Integer, nullable=True)
#
#     created_date = Column(DateTime, server_default=func.now(), nullable=False)
#     updated_date = Column(DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)
#     last_date_used = Column(DateTime)
#     status = Column(Enum(BUY_ACC_STATUS), default=BUY_ACC_STATUS.Active, nullable=False)
#     phone_number = Column(String(25))
#     zip_code = Column(String(15))
#     full_name = Column(String(25))
#
#     proxy_id = Column(Integer, ForeignKey('proxy.id'), nullable=True)
#     proxy = relationship("Proxy", foreign_keys=[proxy_id])
#     # newly added
#     last_lock_date = Column(DateTime, nullable=True)
#     last_tracking_number_check = Column(DateTime, nullable=True)
#     selenium_last_tracking_number_check = Column(DateTime, nullable=True)
#     last_payment_revise_time = Column(DateTime, nullable=True)
#     # Daily limit and account lock
#     account_error_reason = Column(String(1000), default=None)
#     last_account_error = Column(DateTime(), nullable=True)
#     locked = Column(Boolean(), default=False)
#     login_lock_count = Column(Integer, nullable=False, default=0)
#     daily_limit_amount = Column(Float(), nullable=True)
#     remaining_daily_limit = Column(Float(), default=9999)
#     gift_card_balance = Column(Float(), nullable=True, default=None)
#     last_gift_balance_check = Column(DateTime(), default=None, nullable=True)
#     verefication_code = Column(String(100), default=None, nullable=True)
#     pending_orders_limit = Column(Integer, default=None, nullable=True)
#     remaining_orders_to_send = Column(Integer, default=None, nullable=True)
#     is_managed = Column(Boolean(), default=False, nullable=False)
#     validate_prime = Column(Boolean(), default=False, nullable=False)
#     use_for_ao = Column(Boolean(), default=True, nullable=False)
#     use_for_tracking = Column(Boolean(), default=True, nullable=False)
#     multilogin_profile_id = Column(String(1000), default=None)
#     orders_scan = Column(Boolean(), default=False, nullable=False)
#     last_scan_order_id = Column(String(50), nullable=True)
#     user_agent = Column(String(255), nullable=True)
#     order_min_price = Column(Float(), nullable=True, default=None)
#     order_max_price = Column(Float(), nullable=True, default=None)
#     parent_account_id = Column(Integer, ForeignKey('buy_account.id'), nullable=True)
#     parent_account = relationship(lambda: BuyAccount, remote_side=id, backref='child_account')
#
#
# class BuyAccountGroups(Base):
#     __tablename__ = 'buyer_accounts_types'
#     id = Column(Integer, primary_key=True)
#     account_id = Column(Integer, nullable=True, unique=True)
#     type = Column(String(300), nullable=True)
#

class DatabaseConnection:
    def get_database_connection(self, sql_query):
        # ssh config
        ssh_key_file = 'credential/ssh/id_rsa'
        mypkey = paramiko.RSAKey.from_private_key_file(ssh_key_file)
        ssh_host = 'bastion-k8s-autods-com-0a664d-949684120.us-west-2.elb.amazonaws.com'
        ssh_user = 'admin'
        ssh_port = 22

        # mysql config
        sql_hostname = 'autods-stage-marketplace.cw5vcetrjbet.us-west-2.rds.amazonaws.com'
        sql_username = 'admin'
        sql_password = 'H^bsx%6YhgesXBg-'
        sql_main_database = 'autoorder'
        sql_port = 3306
        host = '127.0.0.1'

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = ssh_host, username = ssh_user, key_filename = ssh_key_file)

        stdin, stdout, stderr = ssh.exec_command("ls")
        lines = stdout.readlines()
        print(lines)


        print("entering to ssh tunnel")
        with SSHTunnelForwarder(
                ssh_address_or_host = ssh_host,
                ssh_username=ssh_user,
                ssh_pkey=mypkey,
                remote_bind_address=(host, sql_port)
                ) as tunnel:
            print("within a tunnel")
            engine = create_engine('mysql+pymysql://' + sql_username + ':' + sql_password + '@' + host + ':' + str(
                tunnel.local_bind_port) + '/' + sql_main_database)

            connection = engine.connect()
            print('engine creating...')

            output = connection.execute(sql_query)
            print(output)
            connection.close()

if __name__ == "__main__":
    mydb = DatabaseConnection()
    mydb.get_database_connection("select * from buyer_accounts_types limit 1;")

