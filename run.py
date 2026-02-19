from city import City

def run_simulation():
    city = City()
    city.generate_random_city(30, 50)
    city.save_city("random_city.txt")
    print("Random city generated and saved to random_city.txt")
    city.visualize_city()

if __name__ == "__main__":
    run_simulation()