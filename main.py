import flet as ft
import ipaddress
import math


def calculate_vlsm(base_ip_str, hosts_list):
    try:
        # Сортируем хосты по убыванию для правильного VLSM
        hosts_list.sort(reverse=True)

        # Создаем объект сети из начального IP
        # Если ввели 192.168.1.0/24, берем адрес
        current_addr = ipaddress.IPv4Address(base_ip_str.split('/')[0])

        results = []
        for required_hosts in hosts_list:
            # Находим нужный размер префикса
            # Нужное кол-во адресов = хосты + 2 (сеть и бродкаст)
            needed_size = required_hosts + 2
            bits = math.ceil(math.log2(needed_size))
            prefix = 32 - bits

            # Создаем подсеть
            subnet = ipaddress.IPv4Network(f"{current_addr}/{prefix}", strict=False)

            results.append({
                "label": f"{required_hosts} хостов",
                "network": str(subnet.network_address),
                "broadcast": str(subnet.broadcast_address),
                "pool": f"{subnet.network_address + 1} - {subnet.broadcast_address - 1}",
                "mask": f"{subnet.netmask} /{prefix}"
            })

            # Сдвигаем адрес для следующей подсети
            current_addr = subnet.broadcast_address + 1

        return results, None
    except Exception as e:
        return None, str(e)


def main(page: ft.Page):
    page.title = "IP Subnet Calc"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"

    ip_input = ft.TextField(label="IP и префикс (192.168.1.0/24)", value="192.168.1.0/24")
    hosts_input = ft.TextField(label="Хосты (через запятую: 42, 26, 10, 2)", value="42, 26, 10, 2")
    results_column = ft.Column(spacing=10)

    def on_calculate(e):
        results_column.controls.clear()
        try:
            hosts = [int(x.strip()) for x in hosts_input.value.split(",")]
            data, error = calculate_vlsm(ip_input.value, hosts)

            if error:
                results_column.controls.append(ft.Text(f"Ошибка: {error}", color="red"))
            else:
                for res in data:
                    results_column.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Для {res['label']}", weight="bold", size=18, color=ft.colors.BLUE_600),
                                    ft.Text(f"1. Адрес сети: {res['network']}"),
                                    ft.Text(f"2. Broadacst: {res['broadcast']}"),
                                    ft.Text(f"3. Пул: {res['pool']}"),
                                    ft.Text(f"4. Маска: {res['mask']}"),
                                ]),
                                padding=15
                            )
                        )
                    )
        except:
            results_column.controls.append(ft.Text("Проверьте формат ввода хостов!", color="red"))

        page.update()

    calc_btn = ft.ElevatedButton("Рассчитать подсети", on_click=on_calculate, fill=True)

    page.add(
        ft.Text("VLSM Калькулятор", size=25, weight="bold"),
        ip_input,
        hosts_input,
        calc_btn,
        ft.Divider(),
        results_column
    )


ft.app(target=main)