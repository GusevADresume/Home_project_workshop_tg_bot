import sqlalchemy
import datetime
from ast import literal_eval as le


class Handler:
    def __init__(self):
        self.database = database = 'postgresql://bot:password@localhost:5432/bot_base'
        self.engine = sqlalchemy.create_engine(database)
        self.connection = self.engine.connect()

    def _request_part(self, part_num):

        return self.connection.execute(f'Select *from parts where part_number = {part_num}').fetchall()

    def create_order(self, part_list, client_id):
        resul_dict = {}
        for item in part_list:
            if self._request_part(item) == []:
                resul_dict[item] = "Whe don't have it"
            elif self._request_part(item)[0][4] == 0:
                resul_dict[item] = "not available"
            else:
                resul_dict[item] = self._request_part(item)[0][3]
        resul = self.order_sum(resul_dict)
        resul['client_id'] = client_id
        self.safe_order(resul)
        return resul

    def order_sum(self, dict):
        order_sum = [i for i in dict.values() if isinstance(i, int)]
        dict['order_sum'] = sum(order_sum)
        return dict

    def safe_order(self, order):
        part_numbers = [i for i in order.keys() if i != 'order_sum' and i != 'client_id']
        part_id = self._get_id_parts(part_numbers)
        self.connection.execute(
            f"INSERT into Orders(client_id,part_id,sum,status) values ({order['client_id']},'{part_id}',{order['order_sum']},'new')")

    def _get_id_parts(self, part_numbers):
        part_id = []
        for i in part_numbers:
            if self._request_part(i) != []:
                part_id.append(self._request_part(i)[0][0])
        return str(" ".join(map(str, part_id)))

    def safe_contact(self, contact):
        contact = le(str(contact).replace('+', ''))
        if self.connection.execute(
                f"Select user_id from clients where user_id = '{contact['user_id']}'").fetchall() == []:
            self.connection.execute(
                f"INSERT into Clients(phone_number, first_name, last_name, user_id) values ({contact['phone_number']}, '{contact['first_name']}', '{contact['last_name']}','{contact['user_id']}')")

    def safe_question(self, question, user_id):
        self.connection.execute(f"INSERT INTO questions (client_id, question) values ({user_id},'{question}')")

    def last_date(self):
        if  self.connection.execute('Select * from workshop order by id desc limit 1').fetchone() is None:
            date_list = [datetime.datetime.date(datetime.datetime.now())]
        else:
            last_date = self.connection.execute('Select * from workshop order by id desc limit 1').fetchone()
            date_list = [last_date[2] + datetime.timedelta(i) for i in range(3)]
        return date_list

    def sing_up_repair(self, id, date):
        self.connection.execute(f"insert into workshop (client_id,visit_date) values({id},'{date}')")


