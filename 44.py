import csv
import os

class BaseEntity:
    def __init__(self):
        pass

class TaxiOrder(BaseEntity):
    """Класс одной поездки"""
    def __init__(self, orderid, date, phone, distance, price):
        # Инициализация свойств
        self.orderid = orderid
        self.date = date
        self.phone = phone
        self.distance = distance
        self.price = price

    def __setattr__(self, name, value):
        if name in ['distance', 'price']:
            try:
                value = float(str(value).replace(',', '.'))
            except (ValueError, TypeError):
                value = 0.0
        super().__setattr__(name, value)

    def __repr__(self):
        return f"Order(id={self.orderid})"

    def __str__(self):
        return f"{self.orderid:<3} | {self.date:<10} | {self.phone:<12} | {self.distance:<5.1f} | {self.price:.2f}р"


class TaxiManager:
    """Класс-менеджер для работы с коллекцией"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.orders = []
        self.currentindex = 0
        self.load()

    def load(self):
        """Чтение данных из CSV"""
        if os.path.exists(self.filepath):
            with open(self.filepath, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, skipinitialspace=True)
                for row in reader:
                    if not row.get('id'):
                        continue
                    order = TaxiOrder(
                        orderid=row.get('id'),
                        date=row.get('starttimed', ''),
                        phone=row.get('phone', ''),
                        distance=row.get('distance', 0),
                        price=row.get('price', 0)
                    )
                    self.orders.append(order)

    def __iter__(self):
        self.currentindex = 0
        return self

    def __next__(self):
        if self.currentindex < len(self.orders):
            item = self.orders[self.currentindex]
            self.currentindex += 1
            return item
        raise StopIteration

    def __getitem__(self, index):
        return self.orders[index]

    # стат метод
    @staticmethod
    def printheader():
        print(f"\n{'ID':<3} | {'Дата':<10} | {'Телефон':<12} | {'Км':<5} | {'Цена'}")
        print("-" * 55)

    # Генератор
    def filterprice(self, limit):
        """Генератор, который выдает заказы дороже лимита"""
        for o in self.orders:
            if o.price > limit:
                yield o

    def save(self):
        """Запись в файл"""
        fields = ['id', 'starttimed', 'phone', 'distance', 'price']
        with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for o in self.orders:
                writer.writerow({
                    'id': o.orderid,
                    'starttimed': o.date,
                    'phone': o.phone,
                    'distance': o.distance,
                    'price': o.price
                })

    def add(self, data):
        neworder = TaxiOrder(**data)
        self.orders.append(neworder)
        self.save()


path = r"C:\Users\Lople\OneDrive\Desktop\pt\44pt"
if not os.path.exists(path):
    os.makedirs(path, exist_ok=True)

file = os.path.join(path, "data1.csv")
manager = TaxiManager(file)

#Добавление записи
choice = input("Добавить запись? (1 - да, Enter - нет): ")
if choice == '1':
    try:
        data = {
            'orderid': len(manager.orders) + 1,
            'date': input("Дата (ГГГГ-ММ-ДД): "),
            'phone': input("Телефон: "),
            'distance': input("Км: "),
            'price': input("Цена: ")
        }
        manager.add(data)
        print("Запись успешно сохранена!")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")

#Сортировка и вывод
if manager.orders:
    sortfield = input("\nСортировать по (date/price/distance) или Enter чтобы пропустить: ")
    if sortfield in ['date', 'price', 'distance']:
        if sortfield == 'date':
            manager.orders.sort(key=lambda x: str(x.date))
        else:
            manager.orders.sort(key=lambda x: getattr(x, sortfield))

    # Печать таблицы через статический метод и итератор
    TaxiManager.printheader()
    for order in manager:
        print(order)

    #Работа с генератором
    print("\nФильтрация через генератор")
    limit_input = input("Показать заказы дороже какой суммы? (число или Enter чтобы пропустить): ")
    
    if limit_input.strip():
        try:
            limit = float(limit_input.replace(',', '.'))
            print(f"\nРезультаты фильтрации (> {limit}р):")
            
            found = False

            for expensive in manager.filterprice(limit):
                print(f"ID {expensive.orderid}: {expensive.price:.2f}р")
                found = True
            
            if not found:
                print("Ничего не найдено.")
        except ValueError:
            print("Ошибка: введите корректное число.")
else:
    print("\nСписок заказов пуст.")
