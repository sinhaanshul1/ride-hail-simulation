from city import City

def run_simulation():
    city = City()
    city.load_city_from_address("1449 Primrose Way, Cupertino, CA", radius=1000)
    # city.print_nodes()
    # city.print_edges()
    city.get_route("1449 Primrose Way, Cupertino, CA", "7588 Lockford Court, Cupertino, CA")
    city.visualize_city()

if __name__ == "__main__":
    run_simulation()