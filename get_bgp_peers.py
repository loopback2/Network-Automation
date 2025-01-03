from junos_lib import JunosDevice, JunosInventoryManager

def select_option(prompt, options):
    """
    Display options and allow the user to select one.
    """
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    choice = input("Enter your choice (or 'q' to quit): ").strip()
    if choice.lower() == 'q':
        return None
    try:
        return options[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Please try again.")
        return select_option(prompt, options)

# Load Inventory
inventory_manager = JunosInventoryManager('device_inventory.yml')
inventory = inventory_manager.load_inventory()

# Interactive Site Selection
if inventory:
    sites = list(inventory.keys())
    selected_site = select_option("Select a site:", sites)
    if not selected_site:
        print("No site selected. Exiting.")
        exit()

    # Interactive Category Selection
    categories = list(inventory[selected_site].keys())
    selected_category = select_option("Select a category:", categories)
    if not selected_category:
        print("No category selected. Exiting.")
        exit()

    # Interactive Host Selection
    devices = inventory[selected_site][selected_category]
    device_hosts = [device["host"] for device in devices]
    device_hosts.append("All Hosts")  # Add an option for all hosts
    selected_host = select_option("Select a host (or 'All Hosts'):", device_hosts)
    if not selected_host:
        print("No host selected. Exiting.")
        exit()

    # Determine target devices
    if selected_host == "All Hosts":
        target_devices = devices
    else:
        target_devices = [device for device in devices if device["host"] == selected_host]

    # Initialize output file
    output_file = "bgp_peers.txt"
    with open(output_file, "w") as f:
        f.write("")  # Clear the file before appending new data

    # Process target devices
    for device in target_devices:
        try:
            # Create an instance of the JunosDevice class
            junos_device = JunosDevice(
                host=device["host"],
                user=device["user"],
                password=device["password"],
                port=device.get("port", 830)
            )
            junos_device.connect()

            print("=" * 60)
            print(f"Processing Device: {junos_device.host}")
            print("=" * 60)

            # Retrieve and write BGP peers to the output file
            result = junos_device.get_bgp_peers(output_file=output_file)
            print(result)

            # Close connection
            junos_device.close()

        except Exception as e:
            print(f"Error processing device {device['host']}: {e}")
else:
    print("No inventory found. Please check your device_inventory.yml file.")
    exit()

# Display summary
print("\n=== Summary ===")
try:
    with open(output_file, "r") as f:
        peers = f.readlines()
        print(f"Total BGP Peers retrieved: {len(peers)}")
        print(f"Peers saved to: {output_file}")
except FileNotFoundError:
    print("Output file not found.")