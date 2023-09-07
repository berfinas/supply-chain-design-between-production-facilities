import json

import pandas as pd
import sys
import time as t


class Locations:
    num_locations = 7

    def __init__(self, vehicle_capacities):
        self.roads = self._create_roads()
        self.vehicle_capacities = vehicle_capacities

    def _create_roads(self):
        roads = {}
        for i in range(1, self.num_locations + 1):
            for j in range(i + 1, self.num_locations + 1):
                roads[f"{i}-{j}"] = 0
                roads[f"{j}-{i}"] = 0
        return roads

    def set_load(self, road, load_value):
        if road in self.roads:
            self.roads[road] = load_value
        else:
            raise ValueError(f"Invalid road: {road}")

    def get_load(self, road):
        if road in self.roads:
            return self.roads[road]
        else:
            raise ValueError(f"Invalid road: {road}")

    def get_vehicle_type(self, f1, f2):
        if (f1 % 2 == 1 and f2 % 2 == 0) or (f1 % 2 == 0 and f2 % 2 == 1):
            vehicle_type = 1
        elif (f1 % 2 == 1 and f2 % 2 == 1):
            vehicle_type = 2
        else:
            vehicle_type = 3
        return vehicle_type

    def calculate_num_vehicles(self, vehicle_type):
        total_vehicles = 0

        for road in self.roads:
            f1, f2 = map(int, road.split('-'))
            if self.get_vehicle_type(f1, f2) == vehicle_type:
                load = self.roads[road]
                capacity = self.vehicle_capacities[vehicle_type]
                num_vehicles = -(-load // capacity)  # Ceiling division
                total_vehicles += num_vehicles

        return total_vehicles

    def num_vehicle_in_a_road(self, f1, f2):
        capacity = self.vehicle_capacities[self.get_vehicle_type(f1, f2)]
        load = self.get_load(f"{f1}-{f2}")
        num_vehicles = load // capacity + (load % capacity > 0)
        return num_vehicles


def start_button(demand_file_name, product_file_name, distance_file_name, machine_file_name1, machine_file_name2, vehicle_file_name,
                 output_file):
    with open(output_file, "w") as f:
        f.write(f"Sonuçlar: \n")

    original_stdout = sys.stdout
    t1 = t.time()
    sys.setrecursionlimit(100000)
    results_list = []

    demand_file = pd.read_excel(demand_file_name)
    product_file = pd.read_excel(product_file_name)
    distance = pd.read_excel(distance_file_name)
    machine_file1 = pd.read_excel(machine_file_name1)
    machine_file2 = pd.read_excel(machine_file_name2)
    vehicle_file = pd.read_excel(vehicle_file_name)
    machine_file3 = [machine_file1, machine_file2]
    machine_file = pd.concat(machine_file3)

    # heuristic approach h(n) = h'(n, w1) + distance(w1, w2) + h'(w2, goal)
    vehicle_capacities = {row[0]: row[1] for _, row in vehicle_file.iterrows()}
    tesis_dict = {1: 2001, 2: 2101, 3: 2201, 4: 2202, 5: 3001, 6: 3003, 7: 3501}
    tesis_dict2 = {2001: 1, 2101: 2, 2201: 3, 2202: 4, 3001: 5, 3003: 6, 3501: 7}
    unique_values = machine_file['Makine Adı'].unique()
    value_to_number = {value: index + 1 for index, value in enumerate(unique_values)}
    number_to_value = {v: k for k, v in value_to_number.items()}

    count = 0
    uretilmeyenler = list()

    distance_matrix = []
    for ind, line in distance.iterrows():
        a = line[:];
        a = [j for j in a]
        distance_matrix.append(a)

    def get_distance(point1, point2, distance_matrix=distance_matrix):
        # Subtract 1 from the input points to match the 0-indexed matrix
        point1 -= 1
        point2 -= 1
        return distance_matrix[point1][point2]

    product_seq = {}
    product_mass = {}
    for ind, line in product_file.iterrows():
        product_seq[line["Ürün Adı"]] = line["Proses"].split(",")
    for ind, line in demand_file.iterrows():
        product_mass[line["Ürün Adı"]] = float(line["Talep"])

    pro_machines = {}
    machines_seq = {}
    f_machines = {}
    machine_process = {}
    machine_capacity = {}
    total_distances = []
    product_facilities = {}

    for ind, line in machine_file.iterrows():
        facility_num = line["Fabrika"]

        try:
            facility = tesis_dict2[facility_num]
        except:
            print(facility_num)

        product = line["Bitmiş Kodu"]
        m = value_to_number[line["Makine Adı"]]

        process = line["Process"]
        cevrim = line["Çevrim Süresi"]
        key = f"{facility}.{m}"
        key_1 = f"{key}.{product}.{process}"
        key_2 = f"{product}.{process}"
        machine_process[key_1] = cevrim
        machine_capacity[key] = 43200

        if key in machines_seq.keys():
            liste_2 = machines_seq[key][:]
            liste_2.append(key_2)
            machines_seq[key] = liste_2
        else:
            machines_seq[key] = [key_2]

        if key_2 in pro_machines.keys():
            liste_1 = pro_machines[key_2][:]
            liste_1.append(key)
            pro_machines[key_2] = liste_1
        else:
            pro_machines[key_2] = [key]

        if facility in f_machines.keys():
            liste = f_machines[facility][:]
            if key in liste:
                pass
            else:
                liste.append(key)
                f_machines[facility] = liste
        else:
            f_machines[facility] = [key]

    def find(k, p, pro_list, k_list):
        sequence = product_seq[k];
        next_p = sequence[p]
        kg = product_mass[k]
        d = pro_list[f"{k}.{next_p}"]
        results = []
        for keyy in k_list:

            try:
                c_time = machine_process[f"{keyy}.{k}.{next_p}"] * kg / 100000
            except:
                continue
            m_time = machine_capacity[keyy]

            if (keyy in d) and (m_time > c_time):
                results.append(keyy)
        return results

    def greedy_distance(cur, liste, dist_m=distance_matrix):
        cur -= 1
        liste_1 = [[int(j.split(".")[0]), int(j.split(".")[1])] for j in liste]
        dist_d = {f"{i[0]}.{i[1]}": dist_m[cur][i[0] - 1] for i in liste_1}
        min_val = min(dist_d.values())
        result = []
        for k in dist_d.keys():
            if dist_d[k] == min_val:
                result.append([k, min_val])
        return result

    def update_product_facilities(product_key, facility_from, facility_to, product_facilities):
        if product_key not in product_facilities:
            product_facilities[product_key] = []
        product_facilities[product_key].append((facility_from, facility_to))

    def calculate_product_distance(product_key, product_facilities, distance_matrix):
        distance = 0
        facility_pairs = product_facilities.get(product_key, [])
        if not facility_pairs:
            return 0
        for facility_pair in facility_pairs:
            distance += distance_matrix[facility_pair[0] - 1][facility_pair[1] - 1]
        return distance

    my_locations = Locations(vehicle_capacities)
    countq = 1

    def next_greed_finder(k, p, f, m, total_distance=0, total_transport=[0, 0, 0], vehicle_loads={1: 0, 2: 0, 3: 0},
                          initial=True, location=my_locations, count=countq):
        count += 1
        sekans = product_seq[k]
        next_process = sekans[p]
        if f"{f}.{m}" not in machines_seq.keys():
            f, m = list(map(int, pro_machines[f"{k}.{next_process}"][0].split(".")))
        c_cap = machines_seq[f"{f}.{m}"]
        mass = product_mass[k]
        c_fac = f_machines[f]
        mac_time = machine_capacity[f"{f}.{m}"]

        if initial:
            with open(output_file, "a") as output:
                print(
                    f"Ürün {k} için {tesis_dict[f]}. tesiste, {number_to_value[m].strip()} numaralı makinede, ilk işlem olarak işlem {next_process} başladı",
                    file=output)
            results_list.append({"info_product": "Ürün", "Product": k, "info_facility": "Tesis ",
                                 "Facility": tesis_dict[f], "info_machine": "Makine ", "Machine": number_to_value[m].strip(),
                                 "info_process": "ilk işlem olarak başlayan işlem ", "Process": next_process})
            initial = False

        while (len(sekans[p:]) > 0) and (f"{k}.{next_process}" in c_cap) and (mac_time > 0) and (
                f"{f}.{m}.{k}.{next_process}" in machine_process.keys()):
            c_time = machine_process[f"{f}.{m}.{k}.{next_process}"]
            mac_time = machine_capacity[f"{f}.{m}"]
            mac_time -= c_time * mass / 100000;
            machine_capacity[f"{f}.{m}"] = mac_time
            p += 1
            try:
                next_process = sekans[p]

            except:
                next_process = -1
                product_distance = calculate_product_distance(k, product_facilities, distance_matrix)

                with open(output_file, "a") as output:
                    print(
                        f"İşlem sırası {tesis_dict[f]}. tesiste, {number_to_value[m].strip()} numaralı makinede {product_distance} km katedilen mesafe ile tamamlandı. \n{mass} kg Ürün {k} üretildi\n\n",
                        file=output)
                    # print(
                    #     f"Tır Sefer Sayısı: {total_transport[0]}\nKamyon Sefer Sayısı: {total_transport[1]}\nRömork Sefer Sayısı: {total_transport[2]}\n",
                    #     file=output)
                results_list.append({
                    "Results": f"İşlem sırası {tesis_dict[f]}. tesiste, {number_to_value[m].strip()} numaralı makinede {product_distance} km katedilen mesafe ile tamamlandı."})
                results_list.append({"Results": f"{mass} kg Ürün {k} üretildi"})
                # results_list.append({"Results": f"Tır Sefer Sayısı: {total_transport[0]}"})
                # results_list.append({"Results": f"Kamyon Sefer Sayısı: {total_transport[1]}"})
                # results_list.append({"Results": f"Römork Sefer Sayısı: {total_transport[2]}"})
                return total_distance

        else:
            lists = find(k, p, pro_machines, c_fac)
            if len(lists) > 0:
                f, m = list(map(int, lists[0].split(".")))
                with open(output_file, "a") as output:
                    print(f"Ürün {k} {tesis_dict[f]}. tesis, {number_to_value[m].strip()} numaralı makineye taşınmalı, halihazırdaki işlem {next_process}",
                          file=output)

                results_list.append(
                    {"info_product": "Ürün", "Product": k, "info_facility": "Tesis", "Facility": tesis_dict[f],
                     "info_machine": "Makineye taşınmalı ", "Machine": number_to_value[m].strip(), "info_process": "Halihazırdaki işlem",
                     "Process": next_process})
                return next_greed_finder(k, p, f, m, total_distance, total_transport, initial=False, location = location, count = count)
            else:

                lists = find(k,p,pro_machines,pro_machines[f"{k}.{next_process}"])
                if len(lists) == 0:
                    with open(output_file, "a") as output:
                        print("Ürün {k} için talep çok fazla. Makineler arası paylaştırma yapıldı.", file=output)

                    results_list.append(
                        {"Results": f"Ürün {k} için talep çok fazla. Makineler arası paylaştırma yapıldı."})
                    p_m = product_mass[k] / 2
                    product_mass[k] = p_m
                    return next_greed_finder(k, p, f, m, total_distance, total_transport, initial=False,
                                             location=location, count=count) + next_greed_finder(k, p, 0, 0,
                                                                                                 total_distance,
                                                                                                 total_transport,
                                                                                                 initial=False,
                                                                                                 location=location,
                                                                                                 count=count)

                available = greedy_distance(f, lists)
                f_1, m_1 = list(map(int, available[0][0].split(".")))
                with open(output_file, "a") as output:
                    print(
                        f"Ürün {k} {tesis_dict[f_1]}. tesis, {number_to_value[m_1].strip()} numaralı makineye taşınmalı, halihazırdaki işlem {next_process}",
                        file=output)

                results_list.append(
                    {"info_product": "Ürün", "Product": k, "info_facility": "Tesis", "Facility": tesis_dict[f_1],
                     "info_machine": "Taşınılmalsı gereken makine ", "Machine": number_to_value[m_1].strip(),
                     "info_process": "halihazırdaki işlem", "Process": next_process})
                vehicle_type, num_vehicles, new_veh = transport_vehicle(f, f_1, mass, vehicle_loads, product_mass,
                                                                        my_locations)
                temp = total_transport[vehicle_type - 1]
                temp = location.calculate_num_vehicles(vehicle_type)
                total_transport[vehicle_type - 1] = temp

                total_distance += get_distance(f, f_1, distance_matrix) * new_veh
                update_product_facilities(k, f, f_1, product_facilities)

                return next_greed_finder(k, p, f_1, m_1, total_distance, total_transport, initial=False,
                                         location=location, count=count)

    def transport_vehicle(f1, f2, mass, vehicle_loads, product_mass, my_location):
        if (f1 % 2 == 1 and f2 % 2 == 0) or (f1 % 2 == 0 and f2 % 2 == 1):
            vehicle_type = 1
        elif (f1 % 2 == 1 and f2 % 2 == 1):
            vehicle_type = 2
        else:
            vehicle_type = 3

        capacity = vehicle_capacities[vehicle_type]
        num_old = my_location.get_load(f"{f1}-{f2}") // capacity + (my_location.get_load(f"{f1}-{f2}") % capacity > 0)
        my_location.set_load(f"{f1}-{f2}", my_location.get_load(f"{f1}-{f2}") + mass)
        num_vehicles = my_location.get_load(f"{f1}-{f2}") // capacity + (
                    my_location.get_load(f"{f1}-{f2}") % capacity > 0)
        new_veh = num_vehicles - num_old
        return vehicle_type, num_vehicles, new_veh

    def check_remaining_products_between_facilities(f1, f2, product_mass):
        total_remaining_mass = 0
        for product_key in product_mass.keys():
            remaining_mass = product_mass[product_key]
            if remaining_mass != 0:
                product_sequences = product_seq[product_key]
                for process_index in range(len(product_sequences) - 1):
                    current_process = product_sequences[process_index]
                    next_process = product_sequences[process_index + 1]
                    current_machines = pro_machines[f"{product_key}.{current_process}"]
                    next_machines = pro_machines[f"{product_key}.{next_process}"]
                    for current_machine in current_machines:
                        current_facility = int(current_machine.split('.')[0])
                        if current_facility == f1:
                            for next_machine in next_machines:
                                next_facility = int(next_machine.split('.')[0])
                                if next_facility == f2:
                                    total_remaining_mass += remaining_mass
                                    break
        return total_remaining_mass

    t2 = t.time()
    with open(output_file, "a") as output:
        print(f"Veri programa {t2 - t1} saniyede yüklendi.", file=output)

    results_list.append({"Results": f"Veri programa {t2 - t1} saniyede yüklendi."})

    vehicle_loads = {1: 0, 2: 0, 3: 0}
    total_transports = [0, 0, 0]

    for dem_key in product_mass.keys():
        val_dem = product_mass[dem_key]
        if val_dem != 0:
            try:
                example = next_greed_finder(dem_key, 0, 0, 0, total_transport=total_transports)
                total_distances.append(example)
            except:
                pass
                count += 1
                uretilmeyenler.append(dem_key)
                with open(output_file, "a") as output:
                    print(f"Talep edilen {val_dem} kg ürün {dem_key} üretilemedi zira onun işlemi bulunduğu tesiste tamamlanamıyor", file=output)
    t3 = t.time()

    total_distance = sum(total_distances) if total_distances else 0
    total_distance = round(total_distance, 2)

    with open(output_file, "r") as file:
        file_data = file.read()

    new_data = f"Tır Sefer Sayısı: {total_transports[0]}\nKamyon Sefer Sayısı: {total_transports[1]}\nRömork Sefer Sayısı: {total_transports[2]}\n"
    new_data += f"Toplam Katedilen Mesafe: {total_distance} km.\n"

    vehicles = a = {1: "Tır", 2: "Kamyon", 3: "Römork"}
    for loci1 in range(7):
        for loci2 in range(7):
            loc1 = loci1 + 1
            loc2 = loci2 + 1
            if loc1 != loc2:
                number_of_vehicles = int(my_locations.num_vehicle_in_a_road(loc1, loc2))
                if number_of_vehicles > 0:
                    new_data += f"Tesis {tesis_dict[loc1]} ile Tesis {tesis_dict[loc2]} arası {vehicles[my_locations.get_vehicle_type(loc1, loc2)]} sefer sayısı: {number_of_vehicles}\n"

    return_data = []
    for loci1 in range(7):
        for loci2 in range(loci1 + 1, 7):
            the_load = my_locations.get_load(f"{loci1 + 1}-{loci2 + 1}")
            return_data.append([loci1+1, loci2+1, the_load])
            new_data += f"{loci1 + 1} ve {loci2 + 1} arasinda tasinan urun miktari : {the_load} \n"

    new_data = new_data + file_data

    with open(output_file, "w") as file:
        file.write(new_data)

    results_list.insert(0, {
        "Results": f"Tüm programın çalışma süresi: {t3 - t1} saniye.\nModelin Çalışma Süresi: {t3 - t2} saniye."})
    results_list.insert(0, {"Results": f"Toplam Katedilen Mesafe: {total_distance} km."})
    results_list.insert(0, {"Results": f"Römork Sefer Sayısı: {total_transports[2]}"})
    results_list.insert(0, {"Results": f"Kamyon Sefer Sayısı: {total_transports[1]}"})
    results_list.insert(0, {"Results": f"Tır Sefer Sayısı: {total_transports[0]}"})


    sys.stdout = original_stdout
    results_df = pd.DataFrame(results_list, columns=["Results", "info_product", "Product", "info_facility", "Facility",
                                                     "info_machine", "Machine", "info_process", "Process"])
    results_df.to_excel("output.xlsx", index=False)
    print("Program is completed")
    with open('graph_data.json', 'w') as outfile:
        json.dump(return_data, outfile)

if __name__ == "__main__":
    example = start_button()
